# Dataset provenance and schema

**Every numerical CSV here is a synthetic demonstration.** Rates, volumes,
rankings, dates, availability and modeled differences are fictional. Carrier
names and geographic labels are real public names used for explanation. They
do not imply the carrier offers the illustrated price or service. No number
represents historical operations or realized savings.

Every row has `dataset_kind=synthetic_demo` plus a narrative provenance label.
`demo_lanes.json` holds only geography; `demo_schema.json` defines CSV contracts.
Generic commercial fields replace publisher-specific prefixes. Provenance is an
additive field. The retained `teus_2026` and date fields demonstrate a schema,
not real activity. Two TEUs per 40-foot container is a demo equipment assumption;
a mixed 20/40-foot fleet needs a separate conversion.

## Views

- `master_current.csv`: latest scenario carrier comparison.
- `rates_history.csv`: two fictional observations per carrier/lane, with component sums and rail isolation.
- `market_benchmarks.csv`: commercial demo quotes kept out of SSL averages.
- `demo_top10_refresh.csv`: volume-selected scenario with indicative equivalents.
- `demo_top12_destination.csv`: demo rankings and modeled differences.
- `demo_destination_worklist.csv`: additional example lanes.
- `demo_destination_routing_breakdown.csv`: two route bases and a weighted rollup.
- `snapshots/demo_*.csv`: scenario snapshots, not historical market observations.

Rebuild offline using only the Python standard library:

```sh
python scripts/build_demo.py
python -m unittest discover -s tests -v
```

## Future public observations

Keep approved public carrier data separately labeled with source URL, publication
and retrieval dates, equipment, routing basis, currency and publication permission
where needed. A public carrier name does not establish quote provenance. Keep
real customer/shipment IDs, operational volumes, private locators and recipient
configuration outside this public repository. Do not mix real/demo provenance.
