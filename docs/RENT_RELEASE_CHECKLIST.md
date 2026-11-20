# WhereNow rental coverage — release gate

## Verified baseline (2026-11-20)
Public data.json has 208 destinations. Existing public location records have no populated top-level rent fields. The existing app offers separate rent and total living cost filters, but a filter is not evidence of data coverage.

## Source
Nostos/ Navoy version 2026.11.19 (https://nostos.navoy.io/data), 2,001 city dataset; license for compilation CC BY 4.0, individual fields retain their own rights. Market rent is not furnished short-stay rent. Confirm rights before --approved. Do not copy private Atlas profile, SQLite or personal overrides to public data.

## Pipeline
1. Download Nostos JSON independently from its publisher and record checksum, version and retrieved date. Do not commit the 20MB upstream raw file.
2. Run `python -m unittest discover -s tools -p 'test_*.py'`.
3. Run `python tools/rent_pipeline.py data.json nomad-cities-2026.json --output rent-review.json`.
4. Manually inspect unmatched and ambiguous locations, city/country aliases and source licenses. Do not substitute country averages for city values without explicit label.
5. After explicit review, generate approved overlay with --approved. Never present market rent as a furnished quote.
6. Integrate approved overlay with existing index.html by location ID, showing 1BR center, 1BR outskirts, typical rent, observation date and provenance. Keep unknown as null; do not turn missing rent into gray/red failed criteria.
7. Collect furnished 30/60/90-day quotes separately (minimum two dated independent listings per city; distinguish utilities, deposits, platform fees, availability and neighborhoods). Never infer from Nostos market rent.
8. Record independent totals: `totalUsd = furnishedRentUsd + nonRentLivingUsd` only when both values exist; don't double-count rent from a published all-in monthly figure.
9. Refresh market observations monthly and furnished quotes no less than quarterly for priority cities, on demand before travel. No automated paid scrapers.
10. Release only after cross-browser mobile tests, attribution and source-link audit, review of all 208 destination statuses, and approval to merge.

## Coverage gates
Track separately: total destinations; exact city matched; ambiguous; no rent; unmatched; city vs country data; source age; furnished quotes with valid stay dates. 'All rent data' means all 208 statuses resolved or visibly marked unavailable, not 208 invented prices.
