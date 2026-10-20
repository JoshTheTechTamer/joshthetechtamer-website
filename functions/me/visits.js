/**
 * Preview visit report (Josh only): /me/visits on a device marked via /me, or /me/visits?k=<OWNER_KEY>.
 * ?days=30 (default 30), ?tag=prospect|josh|bot|all (default prospect).
 */
import { isOwner, ownerKeyOk } from '../_lib/visit-log.js';
const NO = { 'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer' };
const NAMES = { bamamama: 'Bama Mama Concierge Services', coffeebelt: 'The Coffee Belt', decades: 'Decades Barbershop', elolmito: 'El Olmito', hawknest: 'Hawk Nest Concierge', lemon: 'Lemon Landscaping', megsvintage: 'Meg’s Vintage Collective', osaka: 'Osaka Japanese Steakhouse & Sushi Bar', packnship: 'Pack-N-Ship', riotsrebelles: 'Riots & Rebelles Salon', sellsauto: 'Sell’s Auto Repair', shafferauto: 'Shaffer Automotive', sunsetview: 'Sunset View Pet Hospital', tresses: 'Tresses N’ Tones Hair Studio', royalgrooming: 'Royal Grooming Barber Lounge', backinline: 'Back In Line Chiropractic & Massage' };
const h = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
// Day buckets in Josh's time zone (America/Chicago).
const ctDay = (iso) => new Date(iso).toLocaleDateString('en-CA', { timeZone: 'America/Chicago' });
const ctTime = (iso) => new Date(iso).toLocaleString('en-US', { timeZone: 'America/Chicago', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) + ' CT';

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  if (!(ownerKeyOk(env, url.searchParams.get('k')) || (await isOwner(env, request)))) {
    return new Response('Not found', { status: 404, headers: { 'Content-Type': 'text/plain', ...NO } });
  }
  if (!env.VISITS) return new Response('Visit log not connected', { status: 503, headers: NO });
  const days = Math.min(365, Math.max(1, parseInt(url.searchParams.get('days') || '30', 10) || 30));
  const tag = ['prospect', 'josh', 'bot', 'all'].includes(url.searchParams.get('tag')) ? url.searchParams.get('tag') : 'prospect';
  const since = new Date(Date.now() - days * 864e5).toISOString();
  const where = tag === 'all' ? 'ts >= ?1' : 'ts >= ?1 AND tag = ?2';
  const { results } = await env.VISITS.prepare(`SELECT ts,slug,kind,path,city,region,country,device,tag,iph FROM visits WHERE ${where} ORDER BY ts DESC LIMIT 2000`).bind(...(tag === 'all' ? [since] : [since, tag])).all();
  if (url.searchParams.get('format') === 'json') return Response.json({ days, tag, visits: results }, { headers: NO });
  const groups = new Map();
  for (const r of results) {
    const key = `${r.slug}|${ctDay(r.ts)}`;
    const g = groups.get(key) || { slug: r.slug, day: ctDay(r.ts), login_view: 0, login_ok: 0, login_fail: 0, view: 0, people: new Set(), where: new Set(), devices: new Set(), last: r.ts };
    g[r.kind] = (g[r.kind] || 0) + 1; if (r.iph) g.people.add(r.iph);
    if (r.city || r.region) g.where.add([r.city, r.region].filter(Boolean).join(', '));
    if (r.device) g.devices.add(r.device);
    groups.set(key, g);
  }
  const rows = [...groups.values()].sort((a, b) => (a.day < b.day ? 1 : a.day > b.day ? -1 : a.slug.localeCompare(b.slug)))
    .map((g) => `<tr><td>${h(g.day)}</td><td>${h(NAMES[g.slug] || g.slug)}</td><td>${g.login_view}</td><td>${g.login_ok}</td><td>${g.login_fail}</td><td>${g.view}</td><td>${g.people.size}</td><td>${h([...g.where].join('; '))}</td><td>${h([...g.devices].join(', '))}</td><td>${h(ctTime(g.last))}</td></tr>`).join('');
  const recent = results.slice(0, 50).map((r) => `<tr><td>${h(ctTime(r.ts))}</td><td>${h(NAMES[r.slug] || r.slug)}</td><td>${h(r.kind)}</td><td>${h(r.path)}</td><td>${h([r.city, r.region].filter(Boolean).join(', '))}</td><td>${h(r.device)}</td><td>${h(r.tag)}</td></tr>`).join('');
  const tabs = ['prospect', 'josh', 'bot', 'all'].map((t) => `<a${t === tag ? ' class="on"' : ''} href="?tag=${t}&days=${days}">${t}</a>`).join(' ');
  const body = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Preview visits | The Tech Tamer</title><style>body{font:15px/1.5 Arial,Helvetica,sans-serif;color:#202d4b;background:#f3f5f9;margin:0;padding:24px 14px}main{max-width:1100px;margin:auto}h1{color:#23335c;font-size:1.5rem;margin:0 0 6px}h2{color:#23335c;font-size:1.1rem;margin:26px 0 8px}table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #dce2ed}th,td{padding:7px 9px;border-bottom:1px solid #e6ebf3;text-align:left;vertical-align:top}th{background:#23335c;color:#fff;font-weight:700}.tabs a{display:inline-block;padding:4px 10px;margin-right:4px;border:1px solid #c8d1e0;border-radius:4px;color:#23335c;text-decoration:none;background:#fff}.tabs a.on{background:#23335c;color:#fff}.wrap{overflow-x:auto}p{color:#56617a}</style></head><body><main><h1>Preview visits</h1><p>Last ${days} days, Central Time. “Login page” = someone opened the link; “Got in” = correct password; “Pages” = pages viewed after logging in; “People” = distinct devices/networks (hashed, no IPs stored).</p><p class="tabs">${tabs}</p><h2>By business and day</h2><div class="wrap"><table><tr><th>Day</th><th>Business</th><th>Login page</th><th>Got in</th><th>Wrong pw</th><th>Pages</th><th>People</th><th>Where</th><th>Device</th><th>Last visit</th></tr>${rows || '<tr><td colspan="10">No visits yet.</td></tr>'}</table></div><h2>Latest 50</h2><div class="wrap"><table><tr><th>When</th><th>Business</th><th>What</th><th>Path</th><th>Where</th><th>Device</th><th>Tag</th></tr>${recent || '<tr><td colspan="7">None.</td></tr>'}</table></div></main></body></html>`;
  return new Response(body, { headers: { 'Content-Type': 'text/html; charset=utf-8', ...NO } });
}
