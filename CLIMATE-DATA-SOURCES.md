# Climate data sources

WhereNow shows historical normals, not forecasts. Its map points are approximate city centers. Where available, existing station observations or nearby station proxies are retained; source and measurement choices can differ by metric. Gridded values are comparable historical model estimates, not local measurements. Mountain, urban, coastal and island microclimates can differ substantially from the grid cell.

## ClimaNote (CC BY 4.0)

For exact location matches, selected missing monthly mean temperature, daily high and/or precipitation values were copied from: ClimaNote (2026), *Monthly climate normals 1991–2020 for 7,426 places*, release of 2026-10-27, <https://climanote.app/data/>. Dataset license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Normalized city and country names were matched within 15 km, and only fields absent in the previous WhereNow release were filled. Field selection and formatting are WhereNow changes.

Contains modified Copernicus Climate Change Service information (ERA5 and ERA5-Land, 1991–2020). Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.

- Copernicus Climate Change Service (2018): *ERA5 hourly data on single levels from 1940 to present*. Climate Data Store. [DOI 10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47).
- Copernicus Climate Change Service (2019): *ERA5-Land hourly data from 1950 to present*. Climate Data Store. [DOI 10.24381/cds.e2161bac](https://doi.org/10.24381/cds.e2161bac).
- Hourly data read by ClimaNote from the Open-Meteo open-data archive (CC BY 4.0), place metadata from GeoNames (CC BY 4.0).

## NASA POWER MERRA-2

The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division. Source: [NASA POWER Climatology API](https://power.larc.nasa.gov/docs/services/api/temporal/climatology/), version recorded per city, accessed 2026-11-20. [POWER data reference and attribution guidance](https://power.larc.nasa.gov/docs/referencing/).

WhereNow uses the 1991–2020 model climatology on its coarse 0.5° latitude × 0.625° longitude MERRA-2 grid only where an existing value is missing. The API location is the grid center, not the town's precise site. Mean temperature uses T2M. Typical daytime highs are calculated by averaging the 30 same-calendar-month T2M_MAX_AVG values from the Monthly endpoint. The climatology endpoint is not used for daily highs: at the Bariloche test location, the Climatology value for January was 26.9 °C while the 30-year Monthly endpoint calculation was 19.78 °C. Check the per-destination source because WhereNow also uses ClimaNote estimates when matched. Approximate precipitation totals in mm/month are PRECTOTCORR in mm/day multiplied by the mean calendar month length over 1991–2020. Do not interpret these model estimates as city weather forecasts, health data, or station observations.

## Direct and nearby weather stations

[Japan Meteorological Agency Tokyo Climate Center](https://ds.data.jma.go.jp/tcc/tcc/products/climate/normal/normal.html) and [Dirección Meteorológica de Chile](https://climatologia.meteochile.gob.cl/) station-period details are listed in the destination data. Where a nearby station is substituted for a town without its own data, that provenance is marked separately.
