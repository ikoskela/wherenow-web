#!/usr/bin/env python3
"""Sequential NASA POWER climatology enrichment with per-city diagnostics.
Processes up to BATCH_SIZE missing destinations per run, one request at a time.
Only writes sourced values; persists failure diagnostics for follow-up runs.
"""
import datetime,json,os,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
BASE='https://power.larc.nasa.gov/api/temporal/climatology/point'
MONTHS=('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC')
BATCH_SIZE=max(1,min(20,int(os.environ.get('CLIMATE_BATCH_SIZE','5'))))
def valid(city):
 m=city.get('months',[])
 return len(m)==12 and all(isinstance(v.get('highC'),(int,float)) and -75<v['highC']<65 for v in m)
def fetch(city):
 params={'parameters':'T2M_MAX_AVG','community':'RE','longitude':city['lon'],'latitude':city['lat'],'format':'JSON','start':'1991','end':'2020'}
 url=BASE+'?'+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={'User-Agent':'WhereNowClimate/1.1 (public-source-enrichment)','Accept':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=45) as response:
   status=response.status
   raw=json.load(response)
  series=raw['properties']['parameter']['T2M_MAX_AVG']
  values=[series.get(k) for k in MONTHS]
  if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and -75<v<65 for v in values):
   return None,{'status':status,'reason':'missing_or_invalid_months','keys':list(series)[:20]}
  return ([round(v,1) for v in values],url),None
 except urllib.error.HTTPError as e:
  return None,{'status':e.code,'reason':'http_error','response':e.read(500).decode('utf-8','replace')}
 except Exception as e:
  return None,{'status':None,'reason':type(e).__name__,'detail':str(e)[:300]}
def main():
 path=Path('data.json');cities=json.loads(path.read_text(encoding='utf-8'))
 assert isinstance(cities,list) and len(cities)==208,'Unexpected destination dataset'
 logpath=Path('climate-import-status.json')
 log=json.loads(logpath.read_text()) if logpath.exists() else {'failures':{},'lastAttempt':None}
 failures=log.setdefault('failures',{})
 missing=[c for c in cities if not valid(c)]
 # Prefer untried cities; retry known failures only after other cities have been attempted.
 missing.sort(key=lambda c:(failures.get(c['id'],{}).get('attempts',0),c['id']))
 success=0
 for city in missing[:BATCH_SIZE]:
  now=datetime.datetime.now(datetime.timezone.utc).isoformat()
  if not isinstance(city.get('lat'),(int,float)) or not isinstance(city.get('lon'),(int,float)):
   result=None;error={'reason':'missing_coordinates'}
  else:result,error=fetch(city)
  if result:
   values,url=result
   for month,value in zip(city['months'],values):month['highC']=value
   city['highTempSource']=url
   city['highTempNote']='NASA POWER 1991–2020 T2M_MAX_AVG gridded climatology; monthly average of daily maxima, not a forecast.'
   failures.pop(city['id'],None);success+=1
   print('SUCCESS',city['id'],values,flush=True)
  else:
   prev=failures.get(city['id'],{})
   failures[city['id']]={'attempts':prev.get('attempts',0)+1,'lastAttempt':now,'error':error}
   print('FAILED',city['id'],json.dumps(error),flush=True)
  time.sleep(1)
 log['lastAttempt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 log['complete']=sum(valid(c) for c in cities)
 log['total']=len(cities)
 log['lastBatch']={'requested':min(BATCH_SIZE,len(missing)),'success':success}
 # Valid JSON and atomic replacement, even when some cities fail.
 tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(cities,ensure_ascii=False,separators=(',',':'))+chr(10));tmp.replace(path)
 tmp=logpath.with_suffix('.json.tmp');tmp.write_text(json.dumps(log,ensure_ascii=False,indent=2)+chr(10));tmp.replace(logpath)
 print('SUMMARY',json.dumps({'complete':log['complete'],'remaining':len(cities)-log['complete'],'batch':log['lastBatch']}),flush=True)
if __name__=='__main__':main()
