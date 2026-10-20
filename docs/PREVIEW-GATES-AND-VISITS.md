# Preview gates and visit log (Oct 20, 2026)

## Gates
- 14 demo-* Workers (`demo-<slug>.joshthetechtamer.workers.dev`) and `/demos/royalgrooming/`, `/demos/backinline/` on this site.
- Same restrained login page everywhere (`functions/_lib/gate-page.js`; inlined into the Workers by `/workspace/tpl/gate/build_gate.py`), showing the business name. Password unchanged (Pages/Worker secrets). noindex kept.
- Site demos: one cookie per demo, `tt_demo_<slug>`, Path=`/demos/<slug>`, token signed for that slug. Logging into one never unlocks the other. The form still posts to `/demos-gallery/auth`.

## Visit log
- D1 database `tt-preview-visits`, table `visits` (binding `VISITS` on the Pages project and every demo-* Worker).
- Kinds: `login_view`, `login_ok`, `login_fail`, `view` (HTML pages after login). Fields: ts (UTC), slug, path, city/region/country, device, tag, asn, short UA, `iph` (12-char salted HMAC of the IP; no IPs stored).
- Tags: `bot` (box IPs in `BOX_IPS`, link scanners/crawlers/scripts/headless by user agent, cloud and mail-security networks by ASN), `josh` (device carries the `tt_owner` cookie), else `prospect`.
- Secrets: `OWNER_KEY`, `IP_SALT`, `BOX_IPS` (Pages production + each demo-* Worker; entries are exact IPs or `prefix*@COLO`). Never commit their values.

## Josh's devices
- Open the private `/me?k=…` link once per browser. It sets `tt_owner` on joshthetechtamer.com, then hops through each demo Worker's `/__preview/me` (sets the same cookie on that origin) and ends at `/me/done`.
- If a demo is added, add its slug to `DEMO_SLUGS` in `functions/_lib/visit-log.js` and rebuild the Workers.

## Report
- `/me/visits` on a marked device (or `/me/visits?k=…`). `?tag=prospect|josh|bot|all`, `?days=N`, `?format=json`.
