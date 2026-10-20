import { handleClientPreviewsGate } from '../_lib/client-previews-gate.js';

/**
 * /demos-gallery/ was retired on 2026-10-20 (Josh's call): every gallery URL
 * now 301s to the homepage. The old page lives in
 * previews/demos-gallery-retired-2026-10-20/ (not deployed) and in git history.
 *
 * /demos-gallery/auth and /demos-gallery/logout stay on the shared gate handler:
 * the login form for the private previews (/demos/royalgrooming/, /demos/backinline/)
 * posts to /demos-gallery/auth. /assets/demos-gallery/gallery.css stays because
 * that login page uses it.
 */
export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname;
  if (
    path === '/demos-gallery/auth' || path === '/demos-gallery/auth/' ||
    path === '/demos-gallery/logout' || path === '/demos-gallery/logout/'
  ) {
    return handleClientPreviewsGate(context);
  }
  return new Response(null, {
    status: 301,
    headers: {
      Location: url.origin + '/',
      'Cache-Control': 'public, max-age=3600',
      'X-Robots-Tag': 'noindex, nofollow, noarchive',
    },
  });
}
