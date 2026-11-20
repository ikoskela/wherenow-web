# Source-backed location enrichment plan

## Separate data and opinion
Each observation: location_id, metric, value, unit, currency='USD' where applicable, observation_date, valid_from, valid_to, source_url, source_type, geographic_scope (city/neighborhood/address), method, confidence, review_due, license, notes. Do not overwrite historical observations. Unknown stays null.

### Cost
Furnished 30/60/90-day rents must distinguish monthly lease from tourist nightly quote; include utilities, fees, deposits, taxes, cancellation, workspace, and seasonal availability. Separate food, transport, and total cost. Currency conversion must store rate, date and source; display USD only.

### Social
Separate nightlife, electronic music, restaurants, coworking, international community and walkable social venues. Source using official venue calendars, verified business listings, dated event schedules and locally sourced community discussions. Score confidence independently from personal fit; never infer a person's social preferences from demographics.

### First 25 research targets (not validated)
Concepción, Penco, Hualpén, Talcahuano, Tomé, Valdivia, Osorno, Puerto Montt, La Serena, Coquimbo, Valparaíso, Viña del Mar, San Antonio (Chile), Constitución, Arequipa, Cusco, Huancayo, Cajamarca, Sucre, Tarija, Cochabamba, Esquel, Bariloche, Quetzaltenango, Antigua Guatemala.

### Acceptance
For each target: 2 independently dated rent observations, at least 1 authoritative transport/cost source, 2 social sources, clear source timestamp and licensing, no extrapolated 'verified' airfare, and a confidence score. Missing evidence must not produce green.
