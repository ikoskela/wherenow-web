#!/usr/bin/env python3
"""Offline, review-gated rent ingestion. No private Atlas data or network calls.
python tools/rent_pipeline.py data.json nomad-cities-2026.json --output rent-review.json
python tools/rent_pipeline.py data.json nomad-cities-2026.json --output rent-overlay.json --approved
"""
import argparse,json,unicodedata,datetime
from pathlib import Path
def key(x):
 x=unicodedata.normalize("NFKD",str(x or "")).casefold()
 return " ".join("".join(c for c in x if not unicodedata.combining(c)).split())
def value(o):
 return o.get("value") if isinstance(o,dict) else o
def get_locations(data):
 return data if isinstance(data,list) else data.get("locations",[])
def build(ours,external,approved=False):
 locations=get_locations(ours)
 cities=external if isinstance(external,list) else external.get("cities",[])
 index={}
 for c in cities:
  index.setdefault((key(c.get("name")),key(c.get("country"))),[]).append(c)
 output=[];stats={"matched":0,"missing":0,"ambiguous":0,"no_rent":0}
 for loc in locations:
  match=index.get((key(loc["city"]),key(loc["country"])),[])
  entry={"id":loc["id"],"city":loc["city"],"country":loc["country"],"status":"missing","rent":None}
  if len(match)>1:entry["status"]="ambiguous";stats["ambiguous"]+=1
  elif len(match)==1:
   cost=(match[0].get("metrics") or {}).get("cost") or {}
   fields={}
   for name in ("rent1brUsd","rentOutskirts1brUsd","rentTypical1brUsd"):
    obj=cost.get(name);v=value(obj)
    if isinstance(v,(float,int)) and not isinstance(v,bool) and 0<v<30000:
     fields[name]={"usd":round(v,2),"asOf":obj.get("asOf") if isinstance(obj,dict) else None,
       "sourceId":obj.get("sourceId") if isinstance(obj,dict) else None,
       "level":obj.get("level") if isinstance(obj,dict) else None,
       "kind":"market_rent_not_furnished_quote"}
   if fields:
    entry["rent"]=fields;entry["status"]="matched";stats["matched"]+=1
   else:entry["status"]="no_rent";stats["no_rent"]+=1
  else:stats["missing"]+=1
  output.append(entry)
 return {"schemaVersion":1,"source":"Nostos (Navoy) nomad-cities-2026",
   "sourceUrl":"https://nostos.navoy.io/data/nomad-cities-2026.json",
   "licenseReview":"approved_by_operator" if approved else "pending",
   "publicationAllowed":bool(approved),"total":len(locations),"stats":stats,"records":output}
def main():
 p=argparse.ArgumentParser();p.add_argument("atlas");p.add_argument("source");p.add_argument("--output",required=True);p.add_argument("--approved",action="store_true");a=p.parse_args()
 ours=json.loads(Path(a.atlas).read_text());external=json.loads(Path(a.source).read_text())
 result=build(ours,external,a.approved)
 Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False))
 print(json.dumps({"total":result["total"],"stats":result["stats"],"publicationAllowed":result["publicationAllowed"]}))
if __name__=="__main__":main()
