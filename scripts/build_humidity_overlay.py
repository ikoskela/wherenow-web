#!/usr/bin/env python3
"""Build a sourced, independent NASA POWER RH2M monthly humidity sidecar.
Only humidity-overlay.json is written. Existing temperatures, precipitation,
highs and destination observations are never changed.
"""
import concurrent.futures
import datetime as dt
import json
import math
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
API = "https://power.larc.nasa.gov/api/temporal/climatology/point"

def retrieve(city):
    if not isinstance(city.get("lat"), (int, float)) or not isinstance(city.get("lon"), (int, float)):
        return city["id"], None, "missing valid coordinates"
    qs = urllib.parse.urlencode(dict(parameters="RH2M", community="AG",
                                     longitude=city["lon"], latitude=city["lat"], format="JSON"))
    url = API + "?" + qs
    last = ""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "WhereNow-Atlas/1.0 climate research"})
            with urllib.request.urlopen(req, timeout=55) as response:
                obj = json.load(response)
            values = obj.get("properties", {}).get("parameter", {}).get("RH2M", {})
            result = []
            for month in MONTHS:
                v = values.get(month)
                if not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 100:
                    raise ValueError(f"missing/invalid {month}={v!r}")
                result.append(round(v, 1))
            period = obj.get("header", {}).get("title", "")
            return city["id"], {
                "months": result,
                "source": url,
                "sourceDataset": "NASA POWER MERRA-2 RH2M at 2 m; gridded monthly climatology",
                "period": period or "NASA POWER published climatology",
                "confidence": "modeled-grid; not station-verified",
            }, ""
        except (TimeoutError, ValueError, urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
            last = str(exc)
            time.sleep(2 * (attempt + 1))
    return city["id"], None, last

def main():
    with (ROOT / "data.json").open(encoding="utf-8") as f:
        cities = json.load(f)
    if isinstance(cities, dict):
        cities = cities["locations"]
    ids = [x["id"] for x in cities]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate city ids")
    path = ROOT / "humidity-overlay.json"
    previous = json.loads(path.read_text()) if path.exists() else {}
    old_records = previous.get("records", {})
    records = {}
    failures = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(retrieve, cities)
        for city_id, record, error in results:
            if record:
                records[city_id] = record
            else:
                old = old_records.get(city_id)
                if old and len(old.get("months", [])) == 12 and all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in old["months"]):
                    records[city_id] = old
                failures[city_id] = error
    payload = {
        "schemaVersion": 1,
        "parameter": "RH2M",
        "units": "percent monthly mean relative humidity",
        "source": "NASA POWER climatology / MERRA-2 gridded 2-meter relative humidity",
        "retrievedUTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "cityCount": len(cities),
        "completeCityCount": len(records),
        "missingCityCount": len(cities) - len(records),
        "note": "Climatological average, not forecast; coarse grid may not capture microclimates or elevation. Failures remain unknown.",
        "records": records,
        "failures": failures,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"humidity: {len(records)}/{len(cities)} complete; {len(failures)} retrieval failures; {len(cities)-len(records)} missing")
    if len(records) != len(cities):
        print("Partial coverage is explicitly documented; never fill missing observations with guesses.")

if __name__ == "__main__":
    main()
