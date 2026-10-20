import { isOwner } from '../_lib/visit-log.js';
const NO = { 'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Cache-Control': 'no-store', 'Content-Type': 'text/html; charset=utf-8' };
export async function onRequestGet({ request, env }) {
  const ok = await isOwner(env, request);
  const msg = ok
    ? '<h1>This device is marked as yours.</h1><p>Preview visits from this browser are now tagged “josh”, so they won’t count as prospect visits. Do this once on each phone, computer and browser you use.</p><p><a href="/me/visits">See preview visits</a></p>'
    : '<h1>Not marked</h1><p>This browser didn’t keep the cookie. Open your private /me link again in this browser.</p>';
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Device marked | The Tech Tamer</title><style>body{font:17px/1.6 Arial,Helvetica,sans-serif;color:#202d4b;background:#f3f5f9;margin:0;padding:40px 18px}main{max-width:520px;margin:auto;background:#fff;border:1px solid #dce2ed;border-radius:8px;padding:28px}h1{font-size:1.4rem;color:#23335c;margin:0 0 10px}a{color:#0a84c9;font-weight:700}</style></head><body><main>${msg}</main></body></html>`, { status: ok ? 200 : 403, headers: NO });
}
