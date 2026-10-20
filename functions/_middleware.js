/**
 * Site-wide page-view log for joshthetechtamer.com (Oct 20, 2026).
 * Logs HTML page views only (no assets) into the same D1 visits table with site="tt",
 * after the response is ready (waitUntil), so pages are not slowed down.
 * Previews (/demos/*), /me*, /p/*, /demos-gallery*, /api/* are logged elsewhere or not at all.
 */
import { logVisit, isDocRequest } from './_lib/visit-log.js';

const SKIP = /^\/(demos\/|demos-gallery|me(\/|$)|p\/|api\/|cdn-cgi\/)/;

export async function onRequest(context) {
  const res = await context.next();
  try {
    const { request, env } = context;
    const path = new URL(request.url).pathname;
    if (env.VISITS && !SKIP.test(path) && isDocRequest(request, path)) {
      const ct = res.headers.get('Content-Type') || '';
      if (res.status >= 400 || ct.includes('text/html')) {
        logVisit(env, context, request, 'tt', 'page', path, { site: 'tt', realPath: res.status < 400 });
      }
    }
  } catch (e) { /* never break the page for logging */ }
  return res;
}
