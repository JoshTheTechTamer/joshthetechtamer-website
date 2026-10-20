/**
 * Token-protected export of every visit row (no IPs are stored): /me/visits.json?since=ISO&until=ISO&token=<VISITS_TOKEN>
 * Used by the daily Drive log script (/workspace/fin/visits_to_drive.py). Max 10,000 rows per call; page with since=.
 */
const NO = { 'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer' };
function same(a, b) { a = String(a); b = String(b); let d = a.length ^ b.length; for (let i = 0; i < Math.max(a.length, b.length); i++) d |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0); return d === 0; }
export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const tok = url.searchParams.get('token') || (request.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
  if (!env.VISITS_TOKEN || !tok || !same(tok, env.VISITS_TOKEN)) return new Response('Not found', { status: 404, headers: { 'Content-Type': 'text/plain', ...NO } });
  if (!env.VISITS) return new Response('Visit log not connected', { status: 503, headers: NO });
  const since = url.searchParams.get('since') || '1970-01-01T00:00:00Z';
  const until = url.searchParams.get('until') || '9999-12-31T00:00:00Z';
  const { results } = await env.VISITS.prepare('SELECT id,ts,site,slug,kind,path,city,region,country,device,tag,rule,referrer,utm,colo,asn,iph FROM visits WHERE ts >= ?1 AND ts < ?2 ORDER BY id LIMIT 10000').bind(since, until).all();
  return Response.json({ since, until, count: results.length, rows: results }, { headers: NO });
}
