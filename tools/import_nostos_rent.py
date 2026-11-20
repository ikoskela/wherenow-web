#!/usr/bin/env python3
"""Build a provenance-aware rent overlay from a separately downloaded Nostos JSON.
No network calls, no credentials, no personal records. Review field-level licenses
before publishing output. Usage:
 python tools/import_nostos_rent.py data.json nomad-cities-2026.json > rent-overlay.review.json
"""
import json,sys,unicodedata
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or ''))
 return ''.join(c for c in s if not unicodedata.combining(c)).casefold().strip()
def unwrap(x):
 return x.get('value') if isinstance(x,dict) else x
def run(ours,external):
 locs=ours.get('locations',ours) if isinstance(ours,dict) else ours
 cities=external.get('cities',[]) if isinstance(external,dict) else external
 index={}
 for c in cities:
  key=(norm(c.get('name')),norm(c.get('country')))
  index.setdefault(key,[]).append(c)
 out=[]; matched=0
 for l in locs:
  key=(norm(l['city']),norm(l['country']))
  candidates=index.get(key,[])
  row={'id':l['id'],'city':l['city'],'country':l['country'],'status':'unmatched','rent':None}
  if len(candidates)==1:
   c=candidates[0];cost=c.get('metrics',{}).get('cost',{})
   fields={}
   for k in ('rent1brUsd','rentOutskirts1brUsd','rentTypical1brUsd'):
    obj=cost.get(k);v=unwrap(obj)
    if isinstance(v,(int,float)) and not isinstance(v,bool) and 0<v<30000:
     fields[k]={'usd':round(v,2),'sourceId':obj.get('sourceId') if isinstance(obj,dict) else None,'asOf':obj.get('asOf') if isinstance(obj,dict) else None,'level':obj.get('level') if isinstance(obj,dict) else None,'type':'market_baseline_not_furnished_quote'}
   if fields:
    row['status']='matched_review_license';row['rent']=fields;matched+=1
   else:row['status']='matched_no_rent'
  elif len(candidates)>1:row['status']='ambiguous_match'
  out.append(row)
 return {'source':'Nostos (Navoy) 2026.11.19','sourceUrl':'https://nostos.navoy.io/data/nomad-cities-2026.json','publicationStatus':'REVIEW_REQUIRED_NOT_PUBLIC','matched':matched,'total':len(locs),'records':out}
if __name__=='__main__':
 with open(sys.argv[1],encoding='utf8') as f:ours=json.load(f)
 with open(sys.argv[2],encoding='utf8') as f:external=json.load(f)
 print(json.dumps(run(ours,external),ensure_ascii=False,indent=2))
