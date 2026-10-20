/**
 * Password gate for the client previews served on joshthetechtamer.com:
 * /demos/royalgrooming/* and /demos/backinline/*.
 *
 * Env: DEMOS_GALLERY_PASSWORD, DEMOS_GALLERY_COOKIE_SECRET (Pages secrets).
 * Each demo has its OWN cookie (tt_demo_<slug>, Path=/demos/<slug>) and the token is
 * signed for that slug, so logging into one preview never unlocks another (Oct 20, 2026).
 * The login form still posts to /demos-gallery/auth (routed here by functions/demos-gallery/_middleware.js).
 * Visits are logged via ./visit-log.js. Never put the password value in HTML, errors, or comments.
 */
import { gatePage } from './gate-page.js';
import { logVisit, isDocRequest } from './visit-log.js';

export const DEMOS = {
  royalgrooming: 'Royal Grooming Barber Lounge',
  backinline: 'Back In Line Chiropractic & Massage',
};
const LEGACY_COOKIE = 'tt_demos_auth';
const TTL_SEC = 60 * 60 * 24 * 30;
const enc = new TextEncoder();
const ERR = 'That password didn\u2019t match. Please check Josh\u2019s email and try again.';

export const NOINDEX = {
  'X-Robots-Tag': 'noindex, nofollow, noarchive',
  'Cache-Control': 'no-store',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};

export function slugOf(pathname) {
  const m = /^\/demos\/([a-z0-9-]+)(\/|$)/.exec(pathname || '');
  return m && Object.prototype.hasOwnProperty.call(DEMOS, m[1]) ? m[1] : null;
}
export function isGatedDemoPath(pathname) { return !!slugOf(pathname); }
const cookieName = (slug) => `tt_demo_${slug}`;

function b64url(buf) {
  return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return crypto.subtle.sign('HMAC', key, enc.encode(msg));
}
async function makeToken(secret, slug) {
  const exp = String(Math.floor(Date.now() / 1000) + TTL_SEC);
  return `${exp}.${b64url(await hmac(secret, `${exp}|${slug}`))}`;
}
function same(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
async function tokenOk(secret, slug, token) {
  if (!token || !secret) return false;
  const [exp, sig] = String(token).split('.');
  if (!exp || !sig || !/^\d+$/.test(exp) || Number(exp) < Math.floor(Date.now() / 1000)) return false;
  return same(b64url(await hmac(secret, `${exp}|${slug}`)), sig);
}
function readCookie(req, name) {
  for (const part of (req.headers.get('Cookie') || '').split(';')) {
    const [k, ...rest] = part.trim().split('=');
    if (k === name) return decodeURIComponent(rest.join('='));
  }
  return null;
}
const setCookie = (slug, token) => `${cookieName(slug)}=${encodeURIComponent(token)}; Path=/demos/${slug}; Max-Age=${TTL_SEC}; HttpOnly; Secure; SameSite=Lax`;
const clearCookie = (slug) => `${cookieName(slug)}=; Path=/demos/${slug}; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
const clearLegacy = () => [
  `${LEGACY_COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`,
  `${LEGACY_COOKIE}=; Path=/demos-gallery; Max-Age=0; HttpOnly; Secure; SameSite=Lax`,
];

/** Relative same-site demo paths only (no open redirects). */
export function safeNext(raw) {
  const n = String(raw == null ? '' : raw).trim();
  if (!n.startsWith('/') || n.startsWith('//') || n.includes('\\') || n.includes('..')) return null;
  return slugOf(n.split('?')[0].split('#')[0]) ? n : null;
}

function gate(slug, next, error, status) {
  return new Response(gatePage({ name: DEMOS[slug], action: '/demos-gallery/auth', next, error }), {
    status,
    headers: { 'Content-Type': 'text/html; charset=utf-8', ...NOINDEX },
  });
}
function withNoindex(res) {
  const headers = new Headers(res.headers);
  for (const [k, v] of Object.entries(NOINDEX)) headers.set(k, v);
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
}

export async function handleClientPreviewsGate(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;
  const password = env.DEMOS_GALLERY_PASSWORD || '';
  const secret = env.DEMOS_GALLERY_COOKIE_SECRET || '';

  if (path === '/demos-gallery/auth' || path === '/demos-gallery/auth/') {
    if (request.method !== 'POST') return Response.redirect(url.origin + '/', 303);
    let form;
    try { form = await request.formData(); } catch { form = new FormData(); }
    const nextPath = safeNext(form.get('next'));
    if (!nextPath) return Response.redirect(url.origin + '/', 303);
    const slug = slugOf(nextPath);
    if (!password || !secret) return gate(slug, nextPath, 'This preview isn\u2019t available right now. Please call or text Josh at 563-261-0200.', 503);
    const submitted = String(form.get('password') || '');
    const len = Math.max(password.length, submitted.length);
    let diff = submitted.length === password.length ? 0 : 1;
    for (let i = 0; i < len; i++) diff |= (submitted.charCodeAt(i) || 0) ^ (password.charCodeAt(i) || 0);
    if (diff !== 0) {
      logVisit(env, context, request, slug, 'login_fail', nextPath);
      return gate(slug, nextPath, ERR, 401);
    }
    logVisit(env, context, request, slug, 'login_ok', nextPath);
    const headers = new Headers({ Location: nextPath, ...NOINDEX });
    headers.append('Set-Cookie', setCookie(slug, await makeToken(secret, slug)));
    for (const c of clearLegacy()) headers.append('Set-Cookie', c);
    return new Response(null, { status: 303, headers });
  }

  if (path === '/demos-gallery/logout' || path === '/demos-gallery/logout/') {
    const headers = new Headers({ Location: '/', ...NOINDEX });
    for (const s of Object.keys(DEMOS)) headers.append('Set-Cookie', clearCookie(s));
    for (const c of clearLegacy()) headers.append('Set-Cookie', c);
    return new Response(null, { status: 303, headers });
  }

  const slug = slugOf(path);
  if (!slug) return next();
  if (!password || !secret) return gate(slug, path + url.search, 'This preview isn\u2019t available right now. Please call or text Josh at 563-261-0200.', 503);
  if (!(await tokenOk(secret, slug, readCookie(request, cookieName(slug))))) {
    if (request.method === 'GET') logVisit(env, context, request, slug, 'login_view', path);
    return gate(slug, path + url.search, '', 401);
  }
  if (isDocRequest(request, path)) logVisit(env, context, request, slug, 'view', path);
  return withNoindex(await next());
}
