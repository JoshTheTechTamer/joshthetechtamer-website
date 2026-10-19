/**
 * Password gate for /demos-gallery/*
 *
 * Env (Cloudflare Pages → Settings → Environment variables):
 *   DEMOS_GALLERY_PASSWORD       — shared password Josh gives prospects (change anytime, no rebuild)
 *   DEMOS_GALLERY_COOKIE_SECRET  — random string used to HMAC-sign the auth cookie (change rarely)
 *
 * Cookie: tt_demos_auth = <expiryUnix>.<base64url-hmac>
 * Valid for 30 days. HttpOnly, Secure, SameSite=Lax, Path=/demos-gallery
 *
 * Always sends X-Robots-Tag: noindex, nofollow, noarchive
 *
 * Never include the password value (or any hint of it) in HTML, errors, titles, or comments
 * that reach the browser.
 */
const COOKIE = 'tt_demos_auth';
const TTL_SEC = 60 * 60 * 24 * 30;
const enc = new TextEncoder();

const NOINDEX = {
  'X-Robots-Tag': 'noindex, nofollow, noarchive',
  'Cache-Control': 'no-store',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};

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
  return `${COOKIE}=${encodeURIComponent(token)}; Path=/demos-gallery; Max-Age=${TTL_SEC}; HttpOnly; Secure; SameSite=Lax`;
}

function clearAuthCookie() {
  return `${COOKIE}=; Path=/demos-gallery; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
}

function loginHtml({ error = '', next = '/demos-gallery/' } = {}) {
  const err = error
    ? `<p class="dg-gate-error" role="alert">${error}</p>`
    : '';
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
      <input type="hidden" name="next" value="${next.replace(/"/g, '&quot;')}">
      <label for="pw">Password</label>
      <input id="pw" name="password" type="password" autocomplete="current-password" required autofocus>
      <button class="btn" type="submit">Open gallery</button>
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

function safeNext(raw) {
  const n = String(raw || '/demos-gallery/');
  if (n.startsWith('/demos-gallery')) return n;
  return '/demos-gallery/';
}

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;
  const password = env.DEMOS_GALLERY_PASSWORD || '';
  const secret = env.DEMOS_GALLERY_COOKIE_SECRET || '';

  const withNoindex = async (res) => {
    const headers = new Headers(res.headers);
    for (const [k, v] of Object.entries(NOINDEX)) headers.set(k, v);
    return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
  };

  if (path === '/demos-gallery/auth' || path === '/demos-gallery/auth/') {
    if (request.method !== 'POST') {
      return html(loginHtml({ error: 'Please use the form below.' }), 405);
    }
    if (!password || !secret) {
      return html(
        loginHtml({ error: 'This gallery is not available right now. Text Josh at 563-261-0200.' }),
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
    return new Response(null, {
      status: 303,
      headers: {
        Location: nextPath,
        'Set-Cookie': setAuthCookie(token),
        ...NOINDEX,
      },
    });
  }

  if (path === '/demos-gallery/logout' || path === '/demos-gallery/logout/') {
    return new Response(null, {
      status: 303,
      headers: {
        Location: '/demos-gallery/',
        'Set-Cookie': clearAuthCookie(),
        ...NOINDEX,
      },
    });
  }

  if (!password || !secret) {
    return html(
      loginHtml({ error: 'This gallery is not available right now. Text Josh at 563-261-0200.' }),
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
