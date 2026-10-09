// POST /api/lead — contact form handler for joshthetechtamer.com.
// 1. Checks the Cloudflare Turnstile token (spam protection) with Siteverify.
// 2. Emails the request to Josh's Gmail through the private lead-mailer Worker
//    (service binding MAILER), sent from leads@joshthetechtamer.com with
//    Reply-To set to the visitor's email when they gave one.
// Env: TURNSTILE_SECRET (secret), TURNSTILE_HOSTNAMES (comma list, "*.host" allowed), MAILER (service binding).

const ACTION = 'lead';
const MAX = { name: 100, reply: 10, contact: 150, service: 100, location: 150, preferred_time: 150, issue: 4000 };
const REPLY_LABEL = { text: 'Text message', phone: 'Phone call', email: 'Email' };

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const clean = (s) => String(s || '').replace(/\r\n?/g, '\n').trim();
const oneLine = (s) => clean(s).replace(/\s+/g, ' ');

function hostAllowed(hostname, list) {
  if (!hostname) return false;
  return list.some((h) => (h.startsWith('*.') ? hostname.endsWith(h.slice(1)) : hostname === h));
}

export async function onRequestPost({ request, env }) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return json({ ok: false, error: 'bad_request' }, 400);
  }
  const f = {};
  for (const k of Object.keys(MAX)) f[k] = clean(form.get(k)).slice(0, MAX[k]);

  // Honeypot: real people never fill this hidden field.
  if (clean(form.get('_gotcha'))) return json({ ok: true });

  if (!f.name || !f.issue || !f.contact) return json({ ok: false, error: 'missing_fields' }, 400);
  const reply = REPLY_LABEL[f.reply] ? f.reply : 'text';
  const isEmail = /^[^\s@<>"]+@[^\s@<>"]+\.[^\s@<>"]+$/.test(f.contact);
  if (reply === 'email' && !isEmail) return json({ ok: false, error: 'bad_email' }, 400);
  if (reply !== 'email' && f.contact.replace(/\D/g, '').length < 10) return json({ ok: false, error: 'bad_phone' }, 400);

  // Turnstile Siteverify (tokens are single-use).
  const hostnames = String(env.TURNSTILE_HOSTNAMES || '').split(',').map((h) => h.trim()).filter(Boolean);
  const token = form.get('cf-turnstile-response');
  if (!env.TURNSTILE_SECRET || hostnames.length === 0) return json({ ok: false, error: 'not_configured' }, 500);
  if (!token) return json({ ok: false, error: 'turnstile_missing' }, 403);
  let verdict;
  try {
    const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        secret: env.TURNSTILE_SECRET,
        response: String(token),
        remoteip: request.headers.get('CF-Connecting-IP') || '',
      }),
    });
    verdict = r.ok ? await r.json() : null;
  } catch {
    verdict = null;
  }
  if (!verdict || verdict.success !== true || verdict.action !== ACTION || !hostAllowed(verdict.hostname, hostnames)) {
    return json({ ok: false, error: 'turnstile_failed', codes: verdict && verdict['error-codes'] }, 403);
  }

  const rows = [
    ['Name', f.name],
    ['Service', f.service || 'Not specified'],
    ['Reply by', REPLY_LABEL[reply]],
    ['Contact', f.contact],
    ['City / service location', f.location || 'Not specified'],
    ['Good times to reach me', f.preferred_time || 'Not specified'],
  ];
  const text = rows.map(([k, v]) => `${k}: ${v}`).join('\n') + `\n\nRequest:\n${f.issue}\n\n— Sent from the contact form on ${verdict.hostname}`;
  const html =
    '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#14213d;line-height:1.5">' +
    '<h2 style="margin:0 0 12px;color:#14213d">New Tech Tamer request</h2>' +
    '<table cellpadding="6" style="border-collapse:collapse">' +
    rows.map(([k, v]) => `<tr><td style="font-weight:bold;vertical-align:top;white-space:nowrap">${esc(k)}</td><td>${esc(v)}</td></tr>`).join('') +
    '</table>' +
    `<p style="font-weight:bold;margin:16px 0 4px">Request</p><p style="white-space:pre-wrap;margin:0">${esc(f.issue)}</p>` +
    `<p style="color:#667;font-size:12px;margin-top:20px">Sent from the contact form on ${esc(verdict.hostname)}</p></div>`;

  const payload = {
    subject: `Tech Tamer request: ${oneLine(f.service || 'General')} — ${oneLine(f.name)}`,
    text,
    html,
    replyTo: isEmail ? { email: f.contact, name: oneLine(f.name) } : undefined,
  };

  try {
    const res = await env.MAILER.fetch('https://mailer.internal/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const out = await res.json().catch(() => ({}));
    if (!res.ok || out.ok !== true) return json({ ok: false, error: out.error || 'send_failed' }, 502);
  } catch {
    return json({ ok: false, error: 'send_failed' }, 502);
  }
  return json({ ok: true });
}

export const onRequest = () => json({ ok: false, error: 'method_not_allowed' }, 405);
