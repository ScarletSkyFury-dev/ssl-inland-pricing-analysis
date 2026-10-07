import csv
import unittest
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_demo import average, normalize

def read(name):
    with (ROOT / name).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))

class DemoContractTests(unittest.TestCase):
    def test_missing_service_is_not_zero(self):
        self.assertEqual(average([100, None, 200]), Decimal(150))
        self.assertEqual(average([0, 100]), Decimal(50))
        self.assertIsNone(average([None, None]))

    def test_package_ranges_and_direct_rate(self):
        self.assertEqual(normalize(1000, 'All-in demo'), (800, 880, 840))
        self.assertEqual(normalize(1000, 'Enhanced All-in demo'), (705, 785, 745))
        self.assertEqual(normalize(1000, '2-day demo'), (1000, 1000, 1000))

    def test_current_view_matches_latest_history(self):
        latest = {(r['lane_id'], r['carrier']): r for r in read('data/rates_history.csv') if r['is_current'] == 'true'}
        for row in read('data/master_current.csv'):
            for field, carrier in [('maersk_usd', 'Maersk'), ('msc_usd', 'MSC'), ('hapag_lloyd_usd', 'Hapag-Lloyd')]:
                self.assertEqual(row[field], latest[row['lane_id'], carrier]['rate_usd'])
            values = [Decimal(row[f]) for f in ['maersk_usd', 'msc_usd', 'hapag_lloyd_usd'] if row[f]]
            self.assertLess(abs(Decimal(row['average_ssl_usd']) - sum(values) / len(values)), Decimal('.006'))

    def test_component_isolation_reconciles(self):
        for row in read('data/rates_history.csv'):
            if not row['rate_usd']: continue
            if row['method'] == 'isolated_rail_door':
                combined, rail = row['components'].split(' combined Rail+Door - ')
                value = Decimal(combined) - Decimal(rail.split()[0])
            else:
                value = sum(Decimal(term.split()[0]) for term in row['components'].split(' + '))
            self.assertEqual(value, Decimal(row['rate_usd']))

    def test_route_rollup_is_volume_weighted(self):
        rows = read('data/demo_destination_routing_breakdown.csv')
        detail, total = rows[:-1], rows[-1]
        count = sum(int(r['containers_40ft']) for r in detail)
        self.assertEqual(int(total['containers_40ft']), count)
        self.assertEqual(int(total['teus_2026']), 2 * count)
        for field in ['ssl_average_usd', 'commercial_rate_usd', 'commercial_2day_equivalent_usd']:
            expected = sum(Decimal(r[field]) * int(r['containers_40ft']) for r in detail) / count
            self.assertLess(abs(Decimal(total[field]) - expected), Decimal('.01'))

    def test_all_datasets_explicitly_labeled(self):
        paths = list((ROOT / 'data').rglob('*.csv'))
        self.assertEqual(len(paths), 12)
        for path in paths:
            rows = read(path.relative_to(ROOT))
            self.assertTrue(rows, path)
            for row in rows:
                self.assertNotIn(None, row, str(path))
                self.assertNotIn(None, row.values(), str(path))
                self.assertEqual(row['dataset_kind'], 'synthetic_demo')
                self.assertIn('SYNTHETIC DEMO', row.get('notes', row.get('source_note', '')))

if __name__ == '__main__': unittest.main()
