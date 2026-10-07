"""Rebuild fictional pricing examples. No live/private services or dependencies."""
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARRIERS = ('Maersk', 'MSC', 'Hapag-Lloyd')
LABEL = 'SYNTHETIC DEMO - not quotes, shipments, actual volumes or realized savings'


def money(value):
    return str(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def average(values):
    valid = [Decimal(str(v)) for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def normalize(quote, basis):
    """Indicative range, not a supplier quote. Return (low, high, midpoint)."""
    quote = Decimal(str(quote))
    low_adjust, high_adjust = {'2-day demo': (0, 0), 'All-in demo': (120, 200),
                               'Enhanced All-in demo': (215, 295)}[basis]
    return quote - high_adjust, quote - low_adjust, quote - Decimal(low_adjust + high_adjust) / 2


def models():
    lanes = json.loads((ROOT / 'data/demo_lanes.json').read_text())
    result = []
    for i, lane in enumerate(lanes):
        base = Decimal(610 + i * 53)
        rates = [base + 37, base + 89 if i % 4 else None,
                 base + 131 if i % 5 else None]
        basis = ('2-day demo', 'All-in demo', 'Enhanced All-in demo')[i % 3]
        quote = base + (Decimal(180) if i % 2 else Decimal(-35))
        low, high, equivalent = normalize(quote, basis)
        avg = average(rates)
        volume = 7 + ((i * 13 + 5) % 41)
        result.append(dict(**lane, rates=rates, basis=basis, quote=quote,
                           low=low, high=high, equivalent=equivalent,
                           avg=avg, volume=volume))
    return result


def view(lane, rank):
    """Canonical generic fields shared by all sample CSV views."""
    rates = lane['rates']
    saving = lane['avg'] - lane['equivalent']
    v = dict(lane_id=lane['lane_id'], origin=lane['origin'], destination=lane['destination'],
             rank=rank, port_origin=lane['origin'], rail_ramp=lane['origin'],
             origin_or_ramp=lane['origin'], delivery=lane['destination'],
             lane_or_drayage_basis=lane['origin'] + ' to ' + lane['destination'],
             volume_40ft=lane['volume'], containers_40ft=lane['volume'],
             equivalent_40ft_containers=lane['volume'], teus_2026=2 * lane['volume'],
             maersk_usd=money(rates[0]), msc_usd=money(rates[1]) if rates[1] else '',
             hapag_lloyd_usd=money(rates[2]) if rates[2] else '', maersk_status='Available',
             msc_status='Available' if rates[1] else 'No Service',
             hapag_status='Available' if rates[2] else 'Pending',
             ssl_average_usd=money(lane['avg']), average_ssl_usd=money(lane['avg']),
             current_ssl_winner=CARRIERS[min((j for j, p in enumerate(rates) if p is not None), key=lambda j: rates[j])],
             commercial_best_usd=money(lane['quote']), commercial_rate_usd=money(lane['quote']),
             commercial_2day_equivalent_usd=money(lane['equivalent']),
             commercial_normalized_2day_chassis_usd=money(lane['equivalent']),
             commercial_quote_basis=lane['basis'], commercial_normalization_status='Demo analytical range',
             saving_per_container_usd=money(saving), saving_ytd_usd=money(saving * lane['volume']),
             estimated_ytd_saving_usd=money(saving * lane['volume']),
             benchmark_type='Demo commercial rate', provider_or_source='Synthetic example provider',
             rate_usd=money(lane['quote']), quoted_on='2026-01-12', valid_until='2026-03-31',
             quote_date='2026-01-12', quote_reference='Fictional scenario date: 2026-01-12',
             validity_period='DEMO scenario only', status='Demo comparable', refresh_status='Demo refreshed',
             notes=LABEL + '; ' + lane['basis'] + '; analytical equivalent range USD ' + money(lane['low']) + ' to ' + money(lane['high']),
             commercial_notes=LABEL + '; ' + lane['basis'], dataset_kind='synthetic_demo')
    return v


def write_csv(path, headers, rows):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        for row in rows:
            missing = set(headers) - set(row)
            if missing:
                raise ValueError(f'Missing generic fields: {sorted(missing)}')
            writer.writerow(row)


def build():
    lanes = models()
    ranked = sorted(lanes, key=lambda x: (-x['volume'], x['lane_id']))
    specs = json.loads((ROOT / 'data/demo_schema.json').read_text())
    for spec in specs:
        name = spec['path']
        if name.endswith('rates_history.csv'):
            rows = []
            for date, change in [('2026-01-05', Decimal(-60)), ('2026-01-12', Decimal(0))]:
                for lane in lanes:
                    for j, carrier in enumerate(CARRIERS):
                        rate = lane['rates'][j]
                        rate = rate + change if rate is not None else None
                        method = 'isolated_rail_door' if j == 2 else 'component_sum'
                        components = (f'{money(rate + 800)} combined Rail+Door - 800.00 rail-only'
                                      if j == 2 else f'{money(rate - 210)} haulage + 120.00 fuel + 90.00 chassis') if rate else ''
                        rows.append(dict(lane_id=lane['lane_id'], origin=lane['origin'], destination=lane['destination'],
                                         carrier=carrier, rate_usd=money(rate) if rate else '',
                                         status='Available' if rate else ('No Service' if j == 1 else 'Pending'),
                                         quote_date=date, quote_period_start=date, quote_period_end=date,
                                         validity_period='DEMO scenario only', method=method if rate else 'none',
                                         components=components, source_note=LABEL,
                                         is_current='true' if not change else 'false', dataset_kind='synthetic_demo'))
        else:
            selected = ranked[:10] if 'top10' in name else ranked[:12] if 'top12' in name else ranked[-2:] if 'worklist' in name else lanes
            if 'routing_breakdown' in name:
                selected = [x for x in lanes if x['destination'] == 'Fort Mill SC']
            rows = [view(x, i + 1) for i, x in enumerate(selected)]
            if 'routing_breakdown' in name:
                # Destination-level weighting, not an unweighted average of routes.
                total = sum(x['volume'] for x in selected)
                summary = view(selected[0], '')
                summary.update(origin_or_ramp='DESTINATION CONSOLIDATED', containers_40ft=total, teus_2026=2 * total,
                               maersk_usd='', msc_usd='', hapag_lloyd_usd='', hapag_status='')
                for key, field in [('ssl_average_usd', 'avg'), ('commercial_rate_usd', 'quote'), ('commercial_2day_equivalent_usd', 'equivalent')]:
                    summary[key] = money(sum(x[field] * x['volume'] for x in selected) / total)
                saving = sum((x['avg'] - x['equivalent']) * x['volume'] for x in selected)
                summary.update(saving_per_container_usd=money(saving / total), saving_ytd_usd=money(saving), notes=LABEL + '; volume-weighted across demo routes')
                rows.append(summary)
        write_csv(name, spec['headers'], rows)
    snapshot_headers = ['snapshot_date', 'lane', 'carrier', 'rate_usd', 'status', 'method', 'components', 'notes', 'dataset_kind']
    for ident in ['NY-HAT', 'JAX-LAKE', 'PEV-LAKE', 'CHI-NEW', 'LAX-ONT']:
        lane = next(x for x in lanes if x['lane_id'] == ident)
        rows = []
        for j, carrier in enumerate(CARRIERS):
            rate = lane['rates'][j]
            rows.append(dict(snapshot_date='2026-01-12', lane=lane['origin'] + ' to ' + lane['destination'],
                             carrier=carrier, rate_usd=money(rate) if rate else '', status='Available' if rate else ('No Service' if j == 1 else 'Pending'),
                             method='component_sum' if rate else 'none', components=f'{money(rate - 210)} + 120.00 + 90.00' if rate else '', notes=LABEL, dataset_kind='synthetic_demo'))
        for carrier, rate, method in [('SSL Average', lane['avg'], 'average'), ('Commercial demo', lane['quote'], 'demo_package'), ('Commercial demo 2-day equivalent', lane['equivalent'], 'normalized_estimate')]:
            rows.append(dict(snapshot_date='2026-01-12', lane=lane['origin'] + ' to ' + lane['destination'], carrier=carrier, rate_usd=money(rate), status='Calculated', method=method, components='', notes=LABEL, dataset_kind='synthetic_demo'))
        write_csv('data/snapshots/demo_' + ident.lower() + '.csv', snapshot_headers, rows)
    sample = ranked[:10]
    benchmark = sum(x['avg'] * x['volume'] for x in sample)
    cost = sum(x['quote'] * x['volume'] for x in sample)
    text = '# Demo commercial versus SSL pricing\n\n**Entire report is synthetic.** Carrier labels and lane geography are illustrative; no number is a historical quote, shipment count, business result or realized saving. Scenario dates are fictional.\n\n'
    text += '| Lane | Demo 40-ft volume | SSL average | Commercial demo | Indicative 2-day range |\n|---|---:|---:|---:|---:|\n'
    for x in sample:
        text += f"| {x['origin']} to {x['destination']} | {x['volume']} | {money(x['avg'])} | {money(x['quote'])} | {money(x['low'])} to {money(x['high'])} |\n"
    text += f'\nDemo portfolio volume: {sum(x["volume"] for x in sample)}. Modeled SSL cost: USD {money(benchmark)}. Demo commercial cost: USD {money(cost)}. Modeled difference: USD {money(benchmark - cost)} ({money((benchmark - cost) / benchmark * 100)}%). Negative differences mean the commercial scenario is more expensive. These are educational calculations, not performance claims.\n\n'
    text += 'Only comparable available numeric rates enter the SSL average. Missing service is not zero. Normalized package equivalents are analytical ranges, not supplier quotes. Separate route bases before comparing them; destination rollups use volume weighting. See [methodology](../docs/methodology.md) and [dataset provenance](../data/README.md).\n'
    (ROOT / 'reports/demo_commercial_vs_ssl.md').write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    build()
