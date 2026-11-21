# Worldwide coverage audit

Run `node tools/audit_coverage.mjs 1 30 any` for January and a 30 km passenger-airport radius. Use `off` to inspect every city. Run `node tools/audit_coverage.test.mjs` for regression checks. No installs, API calls, writes, or workflow runs are needed.

The report reads the same public city inputs and additive overlays as the site. It measures data availability, not whether a city fits a budget or a climate threshold. "Complete" means the typical default filters have inputs for that month without local overrides. Context-only rent is not a rent match. No listed airport within a radius is separate from an airport with unverified service.

Baseline at a2ccf17 (Jan, 30 km, domestic or international passenger flights): 216 destinations, 83 with confirmed service, 42 of those complete and 39 missing only a comparable rent. Of those 39, 27 already have non-scoring rent context. Across all 216, 66 have a comparable rent reference and none have a comparable total monthly cost. Airport service is unverified for 53 places; 80 have no listed airport in range. These are source-coverage numbers, not fit counts.

## Gap-filling order

1. Start with the report's firstRentPass queue. Group cities by country/source, prefer reusable city-wide one-bedroom evidence, and keep ordinary asking rent, furnished monthly pricing, and benchmarks as separate data types. Capture dates, sample size, geographic scope, currency and conversion date, attribution, and reuse basis. Leave a field unknown when there is no comparable evidence.
2. Complete the small monthly climate gaps, preferring documented station normals and labeling gridded estimates. Do not substitute monthly means or extreme maxima for mean daily highs. Verify passenger service separately from airport existence; do not infer no service from absent data.
3. Expand region by region from documented city IDs, with baseline time zones, normals and airport records supplied in bulk where possible. Add comparable total-cost inputs and optional criteria separately; don't use rent as a stand-in for total cost or disease incidence as a stand-in for biting nuisance.
4. Each pass runs the audit against the latest data, picks one batch, saves evidence and skipped reasons, reruns checks, and reports before/after counts. Distinguish candidates, committed records, and verified live data.

This change is an offline audit and regression test. It does not change the live app, dataset, or deployment schedule.
