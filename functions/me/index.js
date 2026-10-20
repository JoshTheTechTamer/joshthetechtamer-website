/**
 * Josh's device-marking link: /me?k=<OWNER_KEY>. Sets the long-lived tt_owner cookie on
 * joshthetechtamer.com (Domain=joshthetechtamer.com, so <slug>.joshthetechtamer.com previews see it), then hops through each demo-* Worker's /__preview/me so the same
 * cookie lands on every workers.dev preview origin, ending at /me/done.
 * Visits carrying tt_owner are tagged "josh" in the visit log.
 */
import { ownerKeyOk, ownerValue, ownerCookie, ownerCookieSiteWide, DEMO_SLUGS } from '../_lib/visit-log.js';

const NO = { 'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer' };

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const k = url.searchParams.get('k') || '';
  if (!ownerKeyOk(env, k)) return new Response('Not found', { status: 404, headers: { 'Content-Type': 'text/plain', ...NO } });
  const [first, ...rest] = DEMO_SLUGS;
  const loc = `https://demo-${first}.joshthetechtamer.workers.dev/__preview/me?k=${encodeURIComponent(k)}&chain=${rest.join(',')}`;
  const headers = new Headers({ Location: loc, ...NO });
  const v = await ownerValue(env);
  // Clear the old host-only copy, then set it for joshthetechtamer.com and every <slug>.joshthetechtamer.com.
  headers.append('Set-Cookie', 'tt_owner=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax');
  headers.append('Set-Cookie', ownerCookieSiteWide(v));
  return new Response(null, { status: 302, headers });
}
