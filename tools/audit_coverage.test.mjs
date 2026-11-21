import assert from 'node:assert/strict';
import {audit} from './audit_coverage.mjs';
const months=Array.from({length:12},()=>({tempC:15,highC:20,rainMm:0,humidityPct:50}));
const first={id:'first',tz:'America/Panama',months};
const second={id:'second',tz:'Asia/Tokyo',months};
const third={id:'third',tz:'Europe/Madrid',months};
const inline={id:'inline',tz:'Asia/Bangkok',months};
const html='<script id="atlas-data">[]</script>\nconst destinationAdditions='+JSON.stringify([first,inline])+';';
const input={html,base:[first,second,third],
 humidity:{schemaVersion:1,parameter:'RH2M',records:{first:{months:[null,...Array(11).fill(40)]}}},
 airport:{schemaVersion:1,airports:{a:{international:true},b:{}},records:{first:[['a',30]],second:[['b',10]],third:[],inline:[['a',5]]}},
 rent:{schemaVersion:1,publicationAllowed:true,records:[
  {id:'first',status:'matched',rent:{rentTypical1brUsd:{usd:500}}},
  {id:'second',status:'matched',rent:{rentApartmentMedianUsd:{usd:450}}},
  {id:'inline',status:'matched',rent:{rentDistrict1brAskingUsd:{usd:400}}}
 ]}};
const a=audit(input);
assert.equal(a.destinations,4);
assert.deepEqual(a.baseline,{eligible:2,complete:1});
assert.deepEqual(a.airportCounts,{confirmed:2,unverified:1,'no-listed-airport':1,off:0});
assert.deepEqual(a.rent,{comparable:1,benchmarkOnly:2,absent:1});
assert.equal(a.rows[0].months[0].humidity,true);
assert.equal(a.rows[0].months[0].precipitation,true);
assert.equal(a.firstRentPass[0].id,'inline');
assert.equal(audit(input,{month:12,mode:'off'}).baseline.eligible,4);
assert.equal(audit(input,{radius:29,mode:'any'}).airportCounts.confirmed,1);
assert.equal(audit(input,{mode:'both'}).airportCounts.confirmed,0);
assert.throws(()=>audit(input,{month:13}));
assert.throws(()=>audit({...input,html:'loader changed'}));
assert.throws(()=>audit({...input,rent:{...input.rent,publicationAllowed:false}}));
console.log('Coverage audit regression tests passed');
