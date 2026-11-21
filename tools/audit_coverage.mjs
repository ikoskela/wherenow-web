#!/usr/bin/env node
// Read-only audit of public WhereNow inputs. Does not fetch, score, or publish data.
import {readFileSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export function audit({html,base,humidity,airport,rent}, {month=1,radius=30,mode='any'}={}) {
  if (!Number.isInteger(month)||month<1||month>12) throw Error('Month must be 1–12');
  if (!Number.isFinite(radius)||radius<1||radius>500) throw Error('Airport radius must be 1–500 km');
  if (!['off','any','domestic','international','both'].includes(mode)) throw Error('Invalid airport mode');
  const inline=html.match(/id="atlas-data"[^>]*>([\s\S]*?)<\/script>/);
  const added=html.match(/const destinationAdditions\s*=\s*(\[[^\n]*\]);/);
  if (!inline||!added) throw Error('City input format changed; reconcile audit with app loader');
  const unpack=x=>Array.isArray(x)?x:x.locations;
  const embedded=unpack(JSON.parse(inline[1]));
  const published=embedded?.length?embedded:unpack(base);
  if (!Array.isArray(published)||!published.length) throw Error('No base destinations');
  if (humidity?.schemaVersion!==1||humidity.parameter!=='RH2M'||!humidity.records||
      airport?.schemaVersion!==1||!airport.records||!airport.airports||
      rent?.schemaVersion!==1||rent.publicationAllowed!==true||!Array.isArray(rent.records)) {
    throw Error('Overlay schema or publication status changed; reconcile audit with app loader');
  }
  const num=v=>v===null||v===undefined||String(v).trim()===''?null:Number.isFinite(Number(v))?Number(v):null;
  const present=(v,min=-Infinity,max=Infinity)=>num(v)!==null&&num(v)>=min&&num(v)<=max;
  const records=new Map(rent.records.map(v=>[v.id,v]));
  const fields=['timeZone','meanTemperature','daytimeHigh','precipitation','humidity'];
  const cities=new Map();
  for (const x of published) {
    if (!x.id||cities.has(x.id)) throw Error('Missing or duplicate base city ID: '+x.id);
    cities.set(x.id,x);
  }
  for (const x of JSON.parse(added[1])) {
    if (!x.id) throw Error('Inline city is missing its ID');
    if (!cities.has(x.id)) cities.set(x.id,x);
  }
  const rows=[...cities.values()].map(x=>{
    let timezone=false;
    if(x.tz) try {new Intl.DateTimeFormat('en',{timeZone:x.tz});timezone=true;} catch {}
    const hr=humidity.records[x.id]?.months;
    const months=Array.from({length:12},(_,i)=>{
      const m=x.months?.[i]||{};
      const modeled=hr?.length===12&&typeof hr[i]==='number'&&present(hr[i],0,100)&&x.months?.[i];
      const rh=modeled?hr[i]:m.humidityPct??m.humidity_pct??m.relativeHumidityPct??m.relative_humidity_pct;
      return {timeZone:timezone,meanTemperature:present(m.tempC??m.temp),
        daytimeHigh:present(m.highC),precipitation:present(m.rainMm??m.rain,0),
        humidity:present(rh,0,100)};
    });
    const rr=records.get(x.id);
    const hasRent=present(x.rentUsd,Number.MIN_VALUE) || (rr?.status==='matched'&&
      ['rentTypical1brUsd','rent1brUsd','rentOutskirts1brUsd'].some(k=>{
        const v=rr.rent?.[k]?.usd;return typeof v==='number'&&present(v,Number.MIN_VALUE);
      }));
    const total=present(x.costUsd??x.cost,0)||(hasRent&&present(x.nonRentUsd,0));
    const inRadius=(airport.records[x.id]||[]).filter(([,km])=>present(km,0,radius));
    const verified=inRadius.some(([id])=>{
      const a=airport.airports[id]||{};
      return mode==='any'?a.domestic===true||a.international===true:
        mode==='both'?a.domestic===true&&a.international===true:a[mode]===true;
    });
    const airportAccess=mode==='off'?'off':verified?'confirmed':inRadius.length||!Object.hasOwn(airport.records,x.id)?'unverified':'no-listed-airport';
    // New-user baseline checks presence only: no scoring, overrides, or cap assumptions.
    // Minimum mean temperature and total cost are not default filters.
    const missing=['timeZone','daytimeHigh','precipitation','humidity'].filter(k=>!months[month-1][k]);
    if(!hasRent) missing.push('rent');
    if(airportAccess==='unverified') missing.push('airportService');
    return {id:x.id,city:x.city,country:x.country,months,rent:!!hasRent,
      rentBenchmarkOnly:!hasRent&&!!rr,totalCost:!!total,airportAccess,missingDefaultInputs:missing};
  });
  const counts=Object.fromEntries(fields.map(k=>[k,{
    selectedMonth:rows.filter(x=>x.months[month-1][k]).length,
    allMonths:rows.filter(x=>x.months.every(m=>m[k])).length
  }]));
  const airportCounts=Object.fromEntries(['confirmed','unverified','no-listed-airport','off'].map(k=>[k,rows.filter(x=>x.airportAccess===k).length]));
  const defaultAirportEligible=rows.filter(x=>x.airportAccess==='confirmed'||x.airportAccess==='off');
  return {month,radius,airportMode:mode,destinations:rows.length,counts,
    rent:{comparable:rows.filter(x=>x.rent).length,benchmarkOnly:rows.filter(x=>x.rentBenchmarkOnly).length,
          absent:rows.filter(x=>!x.rent&&!x.rentBenchmarkOnly).length},
    totalCost:rows.filter(x=>x.totalCost).length,airportCounts,
    firstRentPass:rows.filter(x=>defaultAirportEligible.includes(x)&&x.missingDefaultInputs.length===1&&x.missingDefaultInputs[0]==='rent')
      .sort((a,b)=>Number(b.rentBenchmarkOnly)-Number(a.rentBenchmarkOnly)||a.id.localeCompare(b.id))
      .map(x=>({id:x.id,city:x.city,country:x.country,hasExistingRentContext:x.rentBenchmarkOnly})),
    baseline:{eligible:defaultAirportEligible.length,complete:defaultAirportEligible.filter(x=>!x.missingDefaultInputs.length).length},
    rows};
}

// Usage from the repository: node tools/audit_coverage.mjs [month=1] [radius=30] [airport=any]
// Use 'off' to see coverage without the airport eligibility filter. No network or dependencies.
// benchmarkOnly includes non-scoring context such as individual listing examples.
if (process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
  const read=p=>readFileSync(resolve(root,p),'utf8');
  const j=p=>JSON.parse(read(p));
  const [month='1',radius='30',mode='any']=process.argv.slice(2);
  const result=audit({html:read('index.html'),base:j('data.json'),humidity:j('humidity-overlay.json'),
    airport:j('airport-access.json'),rent:j('rent-overlay.json')},{month:Number(month),radius:Number(radius),mode});
  console.log(JSON.stringify(result,null,2));
}
