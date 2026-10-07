# Methodology and maintenance rules

All numerical examples are [synthetic scenarios](../data/README.md). They
preserve analytical mechanics, not actual quotes, demand or business results.

## Routing and field mapping

A generic input may map `Destino Nome` to the ocean gateway, `Destino Delivery
Nome` to delivery and populated `Destino Final Nome` to the inland ramp. A
quote's first POD is not necessarily its final ramp. Keep distinct ramp options
separate. If the ramp or equivalent Rail-only quote is unknown, mark the local
truck amount pending instead of inventing it.

## Direct truck and combined rail quotes

Sum applicable haulage/on-carriage/landfreight, fuel, emergency fuel, inland fuel
and chassis on a consistent equipment/service basis.

`Isolated Truck Drayage = Combined Rail+Door Total - Rail Ramp Only Total`

Both totals need comparable components. Chassis charged on both sides cancels;
a missing/differently scoped component needs review. Preserve component detail
in dated records, including source evidence for any approved public observations.

## Commercial package normalization

Keep the commercial quote and service basis separate from its indicative
two-day-chassis equivalent. Bundled price differences need not equal standalone
accessorial arithmetic. An analytical estimate is not a supplier quote.

The demo standard All-in package means two chassis days, prepull and one storage
day, with a hypothetical USD 120-200 adjustment. The enhanced package adds one
chassis day and one storage day; fictional reference assumptions of USD 45 and
USD 50 produce a USD 215-295 adjustment. These are teaching assumptions, not
price guidance or a lane's actual policy.

`Equivalent range = package quote - maximum adjustment through package quote - minimum adjustment`

CSV point equivalents use the range midpoint; the report shows both bounds.
Direct two-day demo quotes require no adjustment. Real packages require
independently supported inputs rather than this hypothetical adjustment.

## Averages, winners and modeled differences

`SSL average = sum(valid comparable numeric prices) / count(valid comparable numeric prices)`

Exclude No Service, No Pricing, Pending and routing-incomparable prices. No
valid price means an undefined average; one valid price is its own average.
The SSL winner is the lowest comparable available SSL, not the entire market.

`Modeled difference = (SSL average - commercial comparator) * demo container volume`

`Destination average = sum(route average * route volume) / sum(route volume)`

Negative differences mean a more expensive commercial scenario. Positive
modeled differences are not realized savings or evidence of competitiveness.
Aggregate unrounded values, then round USD to cents; sums of rounded rows may
differ by a cent. Demo volume rankings are not actual demand. Normalize package
ranges before like-for-like comparisons.

## Status and historical structure

- Available: numeric scenario price.
- No Service: scenario service unavailable.
- No Pricing: no usable scenario price.
- Pending: routing/quote evidence needed.
- Excluded - different routing: cannot enter a same-basis average.

Retain prior observations and snapshots when adding a dated scenario. The two
generator dates are fictional. For approved actual public series, record exact
publication/quote dates, validity, provenance and comparable components. Refresh
when validity or fuel/surcharge changes require it; demos are never usable quotes.
