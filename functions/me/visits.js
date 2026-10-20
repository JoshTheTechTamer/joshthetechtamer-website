/**
 * Visit report (Josh only): /me/visits on a device marked via /me, or /me/visits?k=<OWNER_KEY>.
 * Two sections: "My website" (site=tt) and "Previews" (site=preview).
 * A preview "prospect" counts only on a correct password or a page viewed after login; plain login-page views are "opened the link".
 * ?days=30 (default), ?tag=real|josh|qa|bot|all (default real = prospect/visitor).
 */
import { isOwner, ownerKeyOk } from '../_lib/visit-log.js';
const NO = { 'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer' };
const NAMES = { bamamama: 'Bama Mama Concierge Services', coffeebelt: 'The Coffee Belt', decades: 'Decades Barbershop', elolmito: 'El Olmito', hawknest: 'Hawk Nest Concierge', lemon: 'Lemon Landscaping', megsvintage: 'Meg’s Vintage Collective', osaka: 'Osaka Japanese Steakhouse & Sushi Bar', packnship: 'Pack-N-Ship', riotsrebelles: 'Riots & Rebelles Salon', sellsauto: 'Sell’s Auto Repair', shafferauto: 'Shaffer Automotive', sunsetview: 'Sunset View Pet Hospital', tresses: 'Tresses N’ Tones Hair Studio', royalgrooming: 'Royal Grooming Barber Lounge', backinline: 'Back In Line Chiropractic & Massage' };
const h = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const ctDay = (iso) => new Date(iso).toLocaleDateString('en-CA', { timeZone: 'America/Chicago' });
const ctTime = (iso) => new Date(iso).toLocaleString('en-US', { timeZone: 'America/Chicago', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) + ' CT';
const table = (head, rows, empty) => `<div class="wrap"><table><tr>${head.map((x) => `<th>${x}</th>`).join('')}</tr>${rows.length ? rows.join('') : `<tr><td colspan="${head.length}">${empty}</td></tr>`}</table></div>`;
const td = (...c) => `<tr>${c.map((x) => `<td>${h(x)}</td>`).join('')}</tr>`;

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  if (!(ownerKeyOk(env, url.searchParams.get('k')) || (await isOwner(env, request)))) {
    return new Response('Not found', { status: 404, headers: { 'Content-Type': 'text/plain', ...NO } });
  }
  if (!env.VISITS) return new Response('Visit log not connected', { status: 503, headers: NO });
  const days = Math.min(365, Math.max(1, parseInt(url.searchParams.get('days') || '30', 10) || 30));
  const tagSel = ['real', 'josh', 'qa', 'bot', 'all'].includes(url.searchParams.get('tag')) ? url.searchParams.get('tag') : 'real';
  const since = new Date(Date.now() - days * 864e5).toISOString();
  const { results } = await env.VISITS.prepare('SELECT ts,site,slug,kind,path,city,region,device,tag,iph,referrer,utm FROM visits WHERE ts >= ?1 ORDER BY ts DESC LIMIT 5000').bind(since).all();
  const keep = (r) => tagSel === 'all' || (tagSel === 'real' ? r.tag === 'prospect' || r.tag === 'visitor' : r.tag === tagSel);
  const rows = results.filter(keep);
  const site = rows.filter((r) => r.site === 'tt');
  const prev = rows.filter((r) => (r.site || 'preview') === 'preview');

  // My website: views by page and day; top referrers.
  const pd = new Map();
  for (const r of site) { const k = `${ctDay(r.ts)}|${r.path}`; const g = pd.get(k) || { day: ctDay(r.ts), path: r.path, n: 0, ppl: new Set() }; g.n++; if (r.iph) g.ppl.add(r.iph); pd.set(k, g); }
  const pageRows = [...pd.values()].sort((a, b) => (a.day < b.day ? 1 : a.day > b.day ? -1 : b.n - a.n)).map((g) => td(g.day, g.path, g.n, g.ppl.size));
  const rf = new Map();
  for (const r of site) { const k = r.utm ? `utm: ${r.utm}` : r.referrer && !/joshthetechtamer\.com$/.test(r.referrer) ? r.referrer : null; if (k) rf.set(k, (rf.get(k) || 0) + 1); }
  const refRows = [...rf.entries()].sort((a, b) => b[1] - a[1]).slice(0, 20).map(([k, n]) => td(k, n));

  // Previews: opened the link vs entered the password, by business and day.
  const bd = new Map();
  for (const r of prev) { const k = `${ctDay(r.ts)}|${r.slug}`; const g = bd.get(k) || { day: ctDay(r.ts), slug: r.slug, opened: 0, ok: 0, fail: 0, views: 0, where: new Set(), dev: new Set() };
    if (r.kind === 'login_view') g.opened++; else if (r.kind === 'login_ok') g.ok++; else if (r.kind === 'login_fail') g.fail++; else if (r.kind === 'view') g.views++;
    if (r.city || r.region) g.where.add([r.city, r.region].filter(Boolean).join(', ')); if (r.device) g.dev.add(r.device); bd.set(k, g); }
  const all = [...bd.values()].sort((a, b) => (a.day < b.day ? 1 : a.day > b.day ? -1 : a.slug.localeCompare(b.slug)));
  const inRows = all.filter((g) => g.ok || g.views).map((g) => td(g.day, NAMES[g.slug] || g.slug, g.ok, g.views, g.fail, [...g.where].join('; '), [...g.dev].join(', ')));
  const openRows = all.filter((g) => !(g.ok || g.views) && (g.opened || g.fail)).map((g) => td(g.day, NAMES[g.slug] || g.slug, g.opened, g.fail, [...g.where].join('; '), [...g.dev].join(', ')));
  const tabs = [['real', 'Real people'], ['josh', 'Josh'], ['qa', 'QA tests'], ['bot', 'Bots'], ['all', 'All']].map(([t, l]) => `<a${t === tagSel ? ' class="on"' : ''} href="?tag=${t}&days=${days}">${l}</a>`).join(' ');
  const body = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Visits | The Tech Tamer</title><style>body{font:15px/1.5 Arial,Helvetica,sans-serif;color:#202d4b;background:#f3f5f9;margin:0;padding:24px 14px}main{max-width:1100px;margin:auto}h1{color:#23335c;font-size:1.5rem;margin:0 0 6px}h2{color:#23335c;font-size:1.25rem;margin:30px 0 4px;border-bottom:2px solid #23335c;padding-bottom:4px}h3{color:#23335c;font-size:1.02rem;margin:18px 0 6px}table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #dce2ed}th,td{padding:7px 9px;border-bottom:1px solid #e6ebf3;text-align:left;vertical-align:top}th{background:#23335c;color:#fff}.tabs a{display:inline-block;padding:4px 10px;margin:0 4px 4px 0;border:1px solid #c8d1e0;border-radius:4px;color:#23335c;text-decoration:none;background:#fff}.tabs a.on{background:#23335c;color:#fff}.wrap{overflow-x:auto}p{color:#56617a;margin:4px 0 10px}</style></head><body><main><h1>Visits</h1><p>Last ${days} day${days === 1 ? '' : 's'}, Central Time. Bots, link scanners and our own tests are filtered out unless you pick them. No IP addresses are stored.</p><p class="tabs">${tabs}</p>
<h2>My website</h2><h3>Views by page and day</h3>${table(['Day', 'Page', 'Views', 'People'], pageRows, 'No views yet.')}<h3>Top referrers</h3>${table(['From', 'Views'], refRows, 'No outside referrers yet.')}
<h2>Previews</h2><h3>Entered the password</h3><p>Someone typed the correct password (or viewed pages after logging in). These are the real prospects.</p>${table(['Day', 'Business', 'Logged in', 'Pages viewed', 'Wrong password', 'Where', 'Device'], inRows, 'Nobody has logged in yet.')}<h3>Opened the link only</h3><p>Saw the password page but didn’t get in. Can include link checkers that slipped past the filters.</p>${table(['Day', 'Business', 'Opened', 'Wrong password', 'Where', 'Device'], openRows, 'None.')}
</main></body></html>`;
  return new Response(body, { headers: { 'Content-Type': 'text/html; charset=utf-8', ...NO } });
}
