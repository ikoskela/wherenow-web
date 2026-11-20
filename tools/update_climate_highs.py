#!/usr/bin/env python3
"""Enrich WhereNow with NASA POWER 1991–2020 monthly mean daily highs.
NASA T2M_MAX_AVG is the mean of daily maxima; T2M_MAX is the extreme maximum.
No personal records, credentials, or paid APIs. Failed lookups stay unknown.
"""
import json,urllib.request,urllib.parse,time,datetime,sys
from pathlib import Path
BASE='https://power.larc.nasa.gov/api/temporal/climatology/point'
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
 successes=0;errors=[]
 for i,c in enumerate(cities):
  if not isinstance(c.get('lat'),(int,float)) or not isinstance(c.get('lon'),(int,float)):
   errors.append(c.get('id','unknown')+': missing coordinates');continue
  try:
   highs,url=get_highs(c['lat'],c['lon'])
   for m,v in zip(c.get('months',[]),highs):m['highC']=v
   c['highTempSource']=url
   c['highTempNote']='NASA POWER MERRA-2 1991–2020 climatology: T2M_MAX_AVG, mean daily maximum temperature (°C); gridded model estimate, not station observations or forecast.'
   successes+=1
  except Exception as e:errors.append(c['id']+': '+str(e)[:120])
  if (i+1)%25==0:print('processed',i+1,'of',len(cities),'success',successes,flush=True)
  time.sleep(.15)
 assert len(cities)==208,'Unexpected destination count; review before publishing'
 assert successes>=180,'Too many failures: '+str(successes)
 p.write_text(json.dumps(raw,ensure_ascii=False,separators=(',',':'))+'\n')
 print(json.dumps({'locations':len(cities),'updated':successes,'unavailable':len(errors),'errors':errors}))
if __name__=='__main__':main()
