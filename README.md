# SSL Inland Pricing Analysis

Generic inland/drayage comparison methods for 40-foot high-cube equipment
across U.S. lanes, using Maersk, MSC and Hapag-Lloyd carrier labels.

**All numerical datasets are synthetic demos, not live or historical quotes.**
Carrier names and lane geography are preserved; availability, prices, demand
and business-performance results are fictional.

## Methods preserved

- Direct haulage, fuel and chassis component sums.
- Local drayage isolation: `Combined Rail+Door - comparable Rail-only total`.
- Average only available, routing-comparable numeric SSL prices; missing service is not zero.
- Keep commercial benchmarks separate from SSL averages.
- Distinguish package quotes from indicative two-day-chassis equivalents.
- Keep alternative ramps separate until the routing basis is comparable.
- Weight destination/portfolio rollups by demo volume and label modeled results.
- Retain dated scenario observations and snapshots.

## Files and offline validation

- [Dataset provenance and schemas](data/README.md)
- [Methodology](docs/methodology.md)
- [Demo comparison report](reports/demo_commercial_vs_ssl.md)

```sh
python scripts/build_demo.py
python -m unittest discover -s tests -v
```

The deterministic generator needs no credentials, network or private services.
Read the provenance policy before adding any real public-source observations.
