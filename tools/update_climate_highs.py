#!/usr/bin/env python3
"""Enrich WhereNow with NASA POWER 1991–2020 monthly mean daily highs.
NASA T2M_MAX_AVG is the mean of daily maxima; T2M_MAX is the extreme maximum.
No personal records, credentials, or paid APIs. Failed lookups stay unknown.
"""
import json,urllib.request,urllib.parse,time,datetime,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
BASE='https://power.larc.nasa.gov/api/temporal/climatology/point' # NASA POWER source
MONTHS=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
def get_highs(lat,lon):
 params={'parameters':'T2M_MAX_AVG','community':'RE','longitude':str(lon),'latitude':str(lat),'format':'JSON','start':'1991','end':'2020'}
 url=BASE+'?'+urllib.parse.urlencode(params)
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'WhereNow-climate-audit/1.0'}),timeout=35) as r: raw=json.load(r)
   vals=raw['properties']['parameter']['T2M_MAX_AVG']
   result=[vals.get(m) for m in MONTHS]
   if len(result)!=12 or not all(isinstance(v,(int,float)) and -75<v<65 for v in result):raise ValueError('missing or implausible climate data')
   return [round(v,1) for v in result],url
  except Exception as exc:
   if attempt==2:raise
   time.sleep(2**attempt)
def main():
 p=Path('data.json');raw=json.loads(p.read_text());cities=raw if isinstance(raw,list) else raw['locations']
 assert len(cities)==208,'Unexpected destination count; review before publishing'
 successes=0;errors=[]
 def lookup(item):
  i,c=item
  if not isinstance(c.get('lat'),(int,float)) or not isinstance(c.get('lon'),(int,float)):
   return i,None,'missing coordinates'
  try:
   highs,url=get_highs(c['lat'],c['lon'])
   return i,(highs,url),None
  except Exception as e:return i,None,str(e)[:180]
 with ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(lookup,item) for item in enumerate(cities) if not (len(item[1].get('months',[]))==12 and all(isinstance(m.get('highC'),(int,float)) and -75<m['highC']<65 for m in item[1]['months']))]
  for n,f in enumerate(as_completed(futures),1):
   i,result,error=f.result();c=cities[i]
   if result:
    highs,url=result
    for m,v in zip(c.get('months',[]),highs):m['highC']=v
    c['highTempSource']=url
    c['highTempNote']='NASA POWER MERRA-2 1991–2020 climatology: T2M_MAX_AVG, mean daily maximum temperature (°C); gridded model estimate, not station observations or forecast.'
    successes+=1
   else:errors.append(c.get('id','unknown')+': '+error)
   if n%25==0:print('processed',n,'of',len(cities),'success',successes,flush=True)
 # Preserve all existing verified highs; never replace failures with estimates.
 if successes==0 and futures:
  raise RuntimeError('No successful NASA POWER requests; no file changed. First errors: '+repr(errors[:4]))
 p.write_text(json.dumps(raw,ensure_ascii=False,separators=(',',':'))+'\\n')
 print(json.dumps({'locations':len(cities),'updated':successes,'complete':sum(len(c.get('months',[]))==12 and all(isinstance(m.get('highC'),(int,float)) for m in c['months']) for c in cities),'unavailable':len(errors),'errors':errors}))

if __name__=='__main__':main()
