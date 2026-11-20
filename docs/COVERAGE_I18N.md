# Coverage and localization plan

## 500-location expansion
Wave 1: validate the existing 164-location seed, canonical IDs, coordinates, country, timezone, and duplicate aliases. Wave 2: add ~150 cities in the Americas and Atlantic islands where seasonal suitability is promising. Wave 3: add ~186 cities across Europe, Africa, Oceania, and selected Asia; no automatic permanent bans. Prefer representative regional cities over clusters of nearby tourist towns. Add sources and confidence before a city can receive a fully green recommendation.

## English / Spanish
The live index.html already contains an English/Español toggle and bilingual dictionary. Do not replace it with a new app. Audit all visible strings including generated destination cards, map tooltips, legends, error states, search labels, empty results, flight link labels, and screen-reader text. Use one stable key per message; preserve place names; translate dynamic fragments using parameters. Browser language is a default, user choice overrides it and is persisted locally. Keep USD currency in both languages and localize date formats. Tests: both languages, mobile, keyboard, persisted toggle, missing key fallback and no mixed-language errors.

## Privacy
No private profile, personal tax, residency, finances, source SQLite or private preferences in public JSON or GitHub Pages. No automatic deployment from this development branch.
