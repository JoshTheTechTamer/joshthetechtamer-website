/**
 * Local preview for the password-gated demos gallery.
 * Mimics functions/demos-gallery/_middleware.js against the site root.
 *
 * Env:
 *   DEMOS_GALLERY_PASSWORD (required for local; set in the start command — never served to browsers)
 *   DEMOS_GALLERY_COOKIE_SECRET (default: local-dev-secret-change-me)
 *   PORT (default: 4177)
 *
 * Does NOT touch production. Preview only.
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.PORT || 4177);
const PASSWORD = process.env.DEMOS_GALLERY_PASSWORD;
if (!PASSWORD) {
  console.error('Set DEMOS_GALLERY_PASSWORD in the start command (never bake it into HTML).');
  process.exit(1);
}
const SECRET = process.env.DEMOS_GALLERY_COOKIE_SECRET || 'local-dev-secret-change-me';
const COOKIE = 'tt_demos_auth';
const TTL = 60 * 60 * 24 * 30;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.mjs': 'text/javascript',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.woff2': 'font/woff2',
  '.ico': 'image/x-icon',
  '.json': 'application/json',
  '.webmanifest': 'application/manifest+json',
};

function b64url(buf) {
  return Buffer.from(buf).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function makeToken() {
  const exp = String(Math.floor(Date.now() / 1000) + TTL);
  const sig = b64url(crypto.createHmac('sha256', SECRET).update(exp).digest());
  return `${exp}.${sig}`;
}
function tokenOk(token) {
  if (!token) return false;
  const [exp, sig] = String(token).split('.');
  if (!exp || !sig || !/^\d+$/.test(exp)) return false;
  if (Number(exp) < Math.floor(Date.now() / 1000)) return false;
  const expect = b64url(crypto.createHmac('sha256', SECRET).update(exp).digest());
  return crypto.timingSafeEqual(Buffer.from(expect), Buffer.from(sig.padEnd(expect.length).slice(0, expect.length))) && expect === sig;
}
function readCookie(req, name) {
  const raw = req.headers.cookie || '';
  for (const part of raw.split(';')) {
    const [k, ...rest] = part.trim().split('=');
    if (k === name) return decodeURIComponent(rest.join('='));
  }
  return null;
}

function loginHtml(error = '', next = '/demos-gallery/') {
  const err = error ? `<p class="dg-gate-error" role="alert">${error}</p>` : '';
  return `<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>Client website previews | The Tech Tamer</title>
<link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/design.css">
<link rel="stylesheet" href="/assets/demos-gallery/gallery.css"></head>
<body class="dg-gate-body"><main id="gate" class="dg-gate"><div class="dg-gate-card">
<p class="eyebrow">Private</p>
<h1>Client website previews</h1>
<p class="dg-gate-lead">These are private website previews shared with specific businesses. Enter the password from your message or email to view.</p>
${err}
<form class="dg-gate-form" method="post" action="/demos-gallery/auth">
<input type="hidden" name="next" value="${String(next).replace(/"/g, '&quot;')}">
<label for="pw">Password</label>
<input id="pw" name="password" type="password" autocomplete="current-password" required autofocus>
<button class="btn" type="submit">Open gallery</button>
</form>
<p class="dg-gate-note">Need help? Text or call Josh at <a href="tel:+15632610200">563-261-0200</a>.</p>
<p class="dg-gate-home"><a href="/">← Back to The Tech Tamer</a></p>
</div></main></body></html>`;
}

function send(res, status, body, headers = {}) {
  const h = {
    'Cache-Control': 'no-store',
    'X-Robots-Tag': 'noindex, nofollow, noarchive',
    ...headers,
  };
  res.writeHead(status, h);
  res.end(body);
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => {
      const raw = Buffer.concat(chunks).toString();
      const params = new URLSearchParams(raw);
      resolve(params);
    });
    req.on('error', reject);
  });
}

function safePath(urlPath) {
  let name;
  try {
    name = decodeURIComponent(urlPath);
  } catch {
    return null;
  }
  if (name === '/') name = '/index.html';
  if (name.endsWith('/')) name += 'index.html';
  const full = path.resolve(ROOT, '.' + name);
  if (!full.startsWith(ROOT + path.sep)) return null;
  if (name.includes('/.') || name.startsWith('/scripts/') || name.startsWith('/backups/') || name.startsWith('/functions/')) return null;
  return full;
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || '/', `http://127.0.0.1:${PORT}`);
  const p = url.pathname;

  // Auth
  if (p === '/demos-gallery/auth' || p === '/demos-gallery/auth/') {
    if (req.method !== 'POST') return send(res, 405, loginHtml('Please use the form below.'), { 'Content-Type': 'text/html; charset=utf-8' });
    const form = await parseBody(req);
    const next = String(form.get('next') || '/demos-gallery/');
    const nextSafe = next.startsWith('/demos-gallery') ? next : '/demos-gallery/';
    if (form.get('password') !== PASSWORD) {
      return send(res, 401, loginHtml('That didn’t work. Try again, or text Josh.', nextSafe), { 'Content-Type': 'text/html; charset=utf-8' });
    }
    const token = makeToken();
    res.writeHead(303, {
      Location: nextSafe,
      'Set-Cookie': `${COOKIE}=${encodeURIComponent(token)}; Path=/demos-gallery; Max-Age=${TTL}; HttpOnly; SameSite=Lax`,
      'X-Robots-Tag': 'noindex, nofollow, noarchive',
      'Cache-Control': 'no-store',
    });
    return res.end();
  }
  if (p === '/demos-gallery/logout' || p === '/demos-gallery/logout/') {
    res.writeHead(303, {
      Location: '/demos-gallery/',
      'Set-Cookie': `${COOKIE}=; Path=/demos-gallery; Max-Age=0; HttpOnly; SameSite=Lax`,
      'X-Robots-Tag': 'noindex, nofollow, noarchive',
    });
    return res.end();
  }

  // Gate /demos-gallery/*
  if (p === '/demos-gallery' || p.startsWith('/demos-gallery/')) {
    const token = readCookie(req, COOKIE);
    if (!tokenOk(token)) {
      return send(res, 401, loginHtml('', p + url.search), { 'Content-Type': 'text/html; charset=utf-8' });
    }
  }

  const full = safePath(p);
  if (!full) return send(res, 403, 'Forbidden');
  fs.readFile(full, (err, data) => {
    if (err) return send(res, 404, 'Not found');
    const headers = {
      'Content-Type': TYPES[path.extname(full)] || 'application/octet-stream',
      'Cache-Control': 'no-store',
    };
    if (p.startsWith('/demos-gallery')) headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive';
    res.writeHead(200, headers);
    res.end(data);
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Demos gallery preview: http://127.0.0.1:${PORT}/demos-gallery/`);
  console.log('Password: (from DEMOS_GALLERY_PASSWORD env — not printed)');
  console.log(`Root: ${ROOT}`);
});
