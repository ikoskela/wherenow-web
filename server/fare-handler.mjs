// Provider-neutral, dependency-free reference handler. NOT DEPLOYED.
// Pass a trusted request object and injected authorization/quota/provider adapters.
const iata = /^[A-Z]{3}$/;
const iso = /^\d{4}-\d{2}-\d{2}$/;
export function validateFareRequest(input, today = new Date().toISOString().slice(0,10)) {
  if (!input || typeof input !== 'object') throw new Error('invalid_request');
  const {origin,destination,departureDate,returnDate,adults=1,currency='USD'}=input;
  if (![origin,destination].every(v=>typeof v==='string'&&iata.test(v)) || origin===destination) throw new Error('invalid_airports');
  if (![departureDate,returnDate].every(v=>typeof v==='string'&&iso.test(v)&&new Date(v+'T00:00:00Z').toISOString().slice(0,10)===v)) throw new Error('invalid_dates');
  if (departureDate<today || returnDate<departureDate || (Date.parse(returnDate)-Date.parse(departureDate))>365*86400000) throw new Error('invalid_date_range');
  if (!Number.isInteger(adults)||adults<1||adults>6||currency!=='USD') throw new Error('invalid_passengers_or_currency');
  return {origin,destination,departureDate,returnDate,adults,currency};
}
export async function fareSearch(input,{authorized,quota,provider,today}={}) {
  let request;
  try { request=validateFareRequest(input,today); } catch(e) {return {httpStatus:400,body:{status:e.message,offers:[]}};}
  if (!authorized || !provider || !quota) return {httpStatus:503,body:{status:'provider_unavailable',offers:[]}};
  const allowed=await quota.reserve(request); // Must be atomic, global and fail closed.
  if (!allowed) return {httpStatus:429,body:{status:'budget_exceeded',offers:[]}};
  try {
    const raw=await provider.search(request);
    if (!Array.isArray(raw)) throw new Error('invalid_provider_response');
    const offers=raw.filter(o=>Number.isFinite(o.totalUsd)&&o.totalUsd>0&&o.currency==='USD').map(o=>({
      totalUsd:o.totalUsd,provider:String(o.provider||'authorized-provider'),observedAt:o.observedAt||new Date().toISOString(),
      stops:Number.isInteger(o.stops)?o.stops:null,durationMinutes:Number.isInteger(o.durationMinutes)?o.durationMinutes:null,
      baggageIncluded:typeof o.baggageIncluded==='boolean'?o.baggageIncluded:null,
      bookingUrl:typeof o.bookingUrl==='string'&&/^https:\/\//.test(o.bookingUrl)?o.bookingUrl:null
    }));
    return {httpStatus:200,body:{status:offers.length?'ok':'no_offers',offers}};
  } catch {return {httpStatus:502,body:{status:'provider_error',offers:[]}};}
}
