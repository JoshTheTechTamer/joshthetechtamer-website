/**
 * Shared password gate for Client website previews.
 * Covers /demos-gallery/* and /demos/royalgrooming/* + /demos/backinline/*.
 *
 * Env: DEMOS_GALLERY_PASSWORD, DEMOS_GALLERY_COOKIE_SECRET (Pages secrets)
 * Cookie: tt_demos_auth — Path=/ so one login unlocks gallery + gated demos.
 * Never put the password value in HTML, titles, errors, or client-facing comments.
 */

export const COOKIE = 'tt_demos_auth';
const TTL_SEC = 60 * 60 * 24 * 30;
const enc = new TextEncoder();

export const NOINDEX = {
  'X-Robots-Tag': 'noindex, nofollow, noarchive',
  'Cache-Control': 'no-store',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};

export function isGatedDemoPath(pathname) {
  const p = pathname || '';
  return (
    p === '/demos/royalgrooming' ||
    p.startsWith('/demos/royalgrooming/') ||
    p === '/demos/backinline' ||
    p.startsWith('/demos/backinline/')
  );
}

export function isGatedPath(pathname) {
  const p = pathname || '';
  return (
    p === '/demos-gallery' ||
    p.startsWith('/demos-gallery/') ||
    isGatedDemoPath(p)
  );
}

function b64url(buf) {
  let s = btoa(String.fromCharCode(...new Uint8Array(buf)));
  return s.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  return crypto.subtle.sign('HMAC', key, enc.encode(msg));
}

async function makeToken(secret, now = Math.floor(Date.now() / 1000)) {
  const exp = String(now + TTL_SEC);
  const sig = b64url(await hmac(secret, exp));
  return `${exp}.${sig}`;
}

async function tokenOk(secret, token) {
  if (!token || !secret) return false;
  const [exp, sig] = String(token).split('.');
  if (!exp || !sig || !/^\d+$/.test(exp)) return false;
  if (Number(exp) < Math.floor(Date.now() / 1000)) return false;
  const expect = b64url(await hmac(secret, exp));
  if (expect.length !== sig.length) return false;
  let diff = 0;
  for (let i = 0; i < expect.length; i++) diff |= expect.charCodeAt(i) ^ sig.charCodeAt(i);
  return diff === 0;
}

function readCookie(req, name) {
  const raw = req.headers.get('Cookie') || '';
  for (const part of raw.split(';')) {
    const [k, ...rest] = part.trim().split('=');
    if (k === name) return decodeURIComponent(rest.join('='));
  }
  return null;
}

function setAuthCookie(token) {
  // Path=/ covers /demos-gallery and /demos/...
  return `${COOKIE}=${encodeURIComponent(token)}; Path=/; Max-Age=${TTL_SEC}; HttpOnly; Secure; SameSite=Lax`;
}

function clearAuthCookieRoot() {
  return `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
}

function clearAuthCookieLegacy() {
  // Drop earlier Path=/demos-gallery cookies from the first gallery ship
  return `${COOKIE}=; Path=/demos-gallery; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
}

function loginHtml({ error = '', next = '/' } = {}) {
  const err = error ? `<p class="dg-gate-error" role="alert">${error}</p>` : '';
  const nextAttr = String(next).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>Client website previews | The Tech Tamer</title>
<link rel="icon" href="/favicon.ico">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/design.css">
<link rel="stylesheet" href="/assets/demos-gallery/gallery.css">
</head>
<body class="dg-gate-body">
<a class="skip" href="#gate">Skip to content</a>
<main id="gate" class="dg-gate">
  <div class="dg-gate-card">
    <p class="eyebrow">Private</p>
    <h1>Client website previews</h1>
    <p class="dg-gate-lead">These are private website previews shared with specific businesses. Enter the password from your message or email to view.</p>
    ${err}
    <form class="dg-gate-form" method="post" action="/demos-gallery/auth">
      <input type="hidden" name="next" value="${nextAttr}">
      <label for="pw">Password</label>
      <input id="pw" name="password" type="password" autocomplete="current-password" required autofocus>
      <button class="btn" type="submit">Open preview</button>
    </form>
    <p class="dg-gate-note">Need help? Text or call Josh at <a href="tel:+15632610200">563-261-0200</a>.</p>
    <p class="dg-gate-home"><a href="/">← Back to The Tech Tamer</a></p>
  </div>
</main>
</body>
</html>`;
}

function html(body, status = 200, extra = {}) {
  return new Response(body, {
    status,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      ...NOINDEX,
      ...extra,
    },
  });
}

/** Relative same-site paths only — no open redirects. */
export function safeNext(raw) {
  const fallback = '/';
  let n = String(raw == null ? '' : raw).trim();
  if (!n) return fallback;
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(n) || n.startsWith('//') || n.includes('\\')) return fallback;
  if (!n.startsWith('/')) return fallback;
  if (n.includes('..')) return fallback;
  const pathOnly = n.split('?')[0].split('#')[0];
  const ok =
    pathOnly === '/demos-gallery' ||
    pathOnly.startsWith('/demos-gallery/') ||
    pathOnly === '/demos/royalgrooming' ||
    pathOnly.startsWith('/demos/royalgrooming/') ||
    pathOnly === '/demos/backinline' ||
    pathOnly.startsWith('/demos/backinline/');
  return ok ? n : fallback;
}

function withNoindex(res) {
  const headers = new Headers(res.headers);
  for (const [k, v] of Object.entries(NOINDEX)) headers.set(k, v);
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
}

/**
 * Full gate handler (auth + logout + cookie check + noindex).
 * Call only for gated paths (or always from demos-gallery middleware).
 */
export async function handleClientPreviewsGate(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;
  const password = env.DEMOS_GALLERY_PASSWORD || '';
  const secret = env.DEMOS_GALLERY_COOKIE_SECRET || '';

  if (path === '/demos-gallery/auth' || path === '/demos-gallery/auth/') {
    if (request.method !== 'POST') {
      return html(loginHtml({ error: 'Please use the form below.' }), 405);
    }
    if (!password || !secret) {
      return html(
        loginHtml({ error: 'These previews are not available right now. Text Josh at 563-261-0200.' }),
        503
      );
    }
    let form;
    try {
      form = await request.formData();
    } catch {
      return html(loginHtml({ error: 'Something went wrong. Try again.' }), 400);
    }
    const submitted = String(form.get('password') || '');
    const nextPath = safeNext(form.get('next'));
    const a = enc.encode(submitted.padEnd(password.length, '\0').slice(0, Math.max(password.length, submitted.length)));
    const b = enc.encode(password.padEnd(Math.max(password.length, submitted.length), '\0'));
    let diff = submitted.length === password.length ? 0 : 1;
    for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
    if (diff !== 0) {
      return html(loginHtml({ error: 'That didn’t work. Try again, or text Josh.', next: nextPath }), 401);
    }
    const token = await makeToken(secret);
    const headers = new Headers({ Location: nextPath, ...NOINDEX });
    headers.append('Set-Cookie', setAuthCookie(token));
    headers.append('Set-Cookie', clearAuthCookieLegacy());
    return new Response(null, { status: 303, headers });
  }

  if (path === '/demos-gallery/logout' || path === '/demos-gallery/logout/') {
    const headers = new Headers({ Location: '/', ...NOINDEX });
    headers.append('Set-Cookie', clearAuthCookieRoot());
    headers.append('Set-Cookie', clearAuthCookieLegacy());
    return new Response(null, { status: 303, headers });
  }

  if (!password || !secret) {
    return html(
      loginHtml({ error: 'These previews are not available right now. Text Josh at 563-261-0200.' }),
      503
    );
  }

  const token = readCookie(request, COOKIE);
  if (!(await tokenOk(secret, token))) {
    return html(loginHtml({ next: path + url.search }), 401);
  }

  const res = await next();
  return withNoindex(res);
}
