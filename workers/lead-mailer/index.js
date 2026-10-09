// Tech Tamer lead mailer.
// Private Worker: no routes and no workers.dev URL. Only the Pages Function
// (functions/api/lead.js) can reach it, through a service binding.
// The send_email binding is locked to one destination (Josh's Gmail) and one
// sender (leads@joshthetechtamer.com), so it cannot be used to email anyone else.
const TO = 'joshthetechtamer@gmail.com';
const FROM = { email: 'leads@joshthetechtamer.com', name: 'Tech Tamer Leads' };

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 });
    let msg;
    try { msg = await request.json(); } catch { return Response.json({ ok: false, error: 'bad_json' }, { status: 400 }); }
    const { subject, text, html, replyTo } = msg || {};
    if (!subject || !text) return Response.json({ ok: false, error: 'missing_fields' }, { status: 400 });
    try {
      const res = await env.EMAIL.send({
        to: TO,
        from: FROM,
        subject: String(subject).slice(0, 200),
        text: String(text),
        html: html ? String(html) : undefined,
        replyTo: replyTo || undefined,
      });
      return Response.json({ ok: true, id: res && res.messageId });
    } catch (e) {
      console.error('send failed', e && e.code, e && e.message);
      return Response.json({ ok: false, error: (e && e.code) || 'send_failed' }, { status: 502 });
    }
  },
};
