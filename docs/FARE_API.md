# On-demand airfare lookup — implementation contract

Status: design and mock only. **No provider authorized, credentials registered, paid service activated, or endpoint deployed.**

## POST /api/fares/search

Request: `{origin:"ASU",destination:"SCL",departureDate:"2027-01-15",returnDate:"2027-03-15",adults:1,currency:"USD"}`. Require IATA codes, ISO dates, departure in future, return after departure, adults 1–6, max journey 365 days. Never accept arbitrary provider URL.

Response: `{status:"ok",offers:[{totalUsd:123.45,provider:"...",observedAt:"ISO timestamp",stops:1,durationMinutes:420,baggageIncluded:null,bookingUrl:null}],quoteExpiresAt:"ISO timestamp"}`. `totalUsd` must be actual quoted amount; no zero placeholders. For unavailable provider: HTTP 503 `{status:"provider_unavailable",offers:[]}`. For exhausted budget: HTTP 429 `{status:"budget_exceeded",offers:[]}`.

## Security and spending controls

- Authenticated server-to-provider credentials in secret manager only; never in Pages JavaScript, source, query strings or logs.
- Authorized production fare provider with explicit rights to query, display and link offers. Validate commercial pricing and caching rules first.
- Fixed upstream provider hostname, 6-second timeout, maximum 3 retries only on safe failures, no retry after spend threshold reached.
- Global daily request cap, monthly hard spend cap, per-IP rate limits, request-size limits, strict CORS to approved origin, bot protection; fail closed if shared quota store is unavailable.
- Provider adapter translates offers into normalized USD price, stop count, baggage status, quote timestamp and permitted booking URL. Distinguish missing baggage from included baggage.
- Cache only identical query results for a provider-permitted 5–15-minute TTL. No historical fare database.
- Do not expose raw provider errors, user IPs or itinerary PII in logs. No payment or booking action.
- Keep the existing dated external search links as fallback.
- Tests: malformed IATA/date; past dates; cross-origin; quota exhausted; provider timeout; no offers; currency mismatch; unknown baggage; missing token; provider URL allowlist; fake offer rejected.

## Approval gate

Require explicit authorization of provider, credentials, monthly USD spend ceiling, and deployment target before enabling a real lookup. Until then the frontend should show 'Live fare lookup unavailable' and retain outbound search links.
