import { handleClientPreviewsGate, NOINDEX } from '../_lib/client-previews-gate.js';

/**
 * /demos-gallery/ is public (no password) but link-invite only and noindex.
 * /demos-gallery/auth and /demos-gallery/logout stay on the shared gate handler:
 * the login form for the private previews (/demos/royalgrooming/, /demos/backinline/)
 * posts to /demos-gallery/auth, and those paths stay gated by functions/demos/_middleware.js.
 */
export async function onRequest(context) {
  const path = new URL(context.request.url).pathname;
  if (
    path === '/demos-gallery/auth' || path === '/demos-gallery/auth/' ||
    path === '/demos-gallery/logout' || path === '/demos-gallery/logout/'
  ) {
    return handleClientPreviewsGate(context);
  }
  const res = await context.next();
  const headers = new Headers(res.headers);
  for (const [k, v] of Object.entries(NOINDEX)) headers.set(k, v);
  headers.set('Cache-Control', 'public, max-age=300');
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
}
