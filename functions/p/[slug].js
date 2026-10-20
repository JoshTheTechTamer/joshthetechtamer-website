/**
 * Short preview links (Oct 20, 2026):
 *   /p/royalgrooming, /p/backinline -> the gated pages on this site
 *   /p/<slug> -> https://<slug>.joshthetechtamer.com/ (each demo-* Worker's own custom domain and gate)
 * 302 so targets can change later. Unknown slugs fall through to the normal 404.
 */
import { DEMO_SLUGS } from '../_lib/visit-log.js';
const SITE = { royalgrooming: '/demos/royalgrooming/', backinline: '/demos/backinline/' };
export async function onRequestGet({ params, next }) {
  const slug = String(params.slug || '').toLowerCase();
  const to = SITE[slug] ? 'https://joshthetechtamer.com' + SITE[slug] : DEMO_SLUGS.includes(slug) ? `https://${slug}.joshthetechtamer.com/` : null;
  if (!to) return next();
  return new Response(null, { status: 302, headers: { Location: to, 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow, noarchive' } });
}
