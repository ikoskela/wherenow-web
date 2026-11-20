import json,urllib.request,unicodedata,datetime
from pathlib import Path
URL='https://nostos.navoy.io/data/nomad-cities-2026.json'
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or '')).casefold()
 return ' '.join(''.join(c for c in s if not unicodedata.combining(c)).split())
def main():
 data=json.loads(Path('data.json').read_text());locs=data if isinstance(data,list) else data['locations']
 with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'WhereNow-rent-import/1.0'}),timeout=90) as response: source=json.load(response)
 idx={}
 for c in source['cities']:idx.setdefault((norm(c.get('name')),norm(c.get('country'))),[]).append(c)
 prior=json.loads(Path('rent-overlay.json').read_text())
 existing={r['id']:r for r in prior['records']}
 out=[];stats={'new':0,'preserved':0,'missing':0,'ambiguous':0,'no_eligible_rent':0}
 for l in locs:
  matches=idx.get((norm(l['city']),norm(l['country'])),[])
  if len(matches)!=1:
   if l['id'] in existing:out.append(existing[l['id']]);stats['preserved']+=1
   else:stats['ambiguous' if len(matches)>1 else 'missing']+=1
   continue
  cost=((matches[0].get('metrics') or {}).get('cost') or {});fields={}
  for k in ('rentTypical1brUsd','rent1brUsd','rentOutskirts1brUsd'):
   obj=cost.get(k)
   if not isinstance(obj,dict):continue
   v=obj.get('value')
   if obj.get('level')!='city' or not isinstance(v,(int,float)) or isinstance(v,bool) or not 0<v<30000:continue
   fields[k]={'usd':round(v,2),'asOf':obj.get('asOf'),'sourceId':obj.get('sourceId'),'sourceUrl':'https://nostos.navoy.io/data','kind':'market_rent_not_furnished_quote','level':'city'}
  old=existing.get(l['id'])
  if fields:
   out.append({'id':l['id'],'status':'matched','rent':{**fields,**((old or {}).get('rent') or {})}})
   stats['new']+=int(not old);stats['preserved']+=int(bool(old))
  elif old:out.append(old);stats['preserved']+=1
  else:stats['no_eligible_rent']+=1
 assert len(set(r['id'] for r in out))==len(out)
 assert all(all(v['usd']>0 for v in r['rent'].values()) for r in out)
 result={'schemaVersion':1,'publicationAllowed':True,'attribution':'Nostos (Navoy) CC BY 4.0 compilation; field source IDs included; earlier observations preserved','sourceUrl':URL,'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coverage':{'destinations':len(locs),'withRent':len(out),'missing':len(locs)-len(out),'stats':stats},'records':out}
 Path('rent-overlay.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['coverage']))
if __name__=='__main__':main()
