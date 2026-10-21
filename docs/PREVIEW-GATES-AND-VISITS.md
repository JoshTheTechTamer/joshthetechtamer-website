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

## Short addresses (Oct 20, 2026)
- Each demo-* Worker also answers on `https://<slug>.joshthetechtamer.com/` (Workers custom domain). workers.dev links still work.
- `/p/<slug>` on this site 302s to that subdomain; `/p/royalgrooming` and `/p/backinline` go to `/demos/<slug>/`.
- Worker session cookies are host-only and the token is signed for the demo's slug, so one demo's cookie never unlocks another.
- `/me` sets `tt_owner` with `Domain=joshthetechtamer.com` (covers every subdomain) and still hops through the workers.dev hosts.

## Oct 20, 2026 update: tags, site tracking, export

- **Columns added:** `colo`, `asn` (already), `rule` (which tag rule fired), `site` (`preview` or `tt`), `referrer` (host only), `utm` (utm_source).
- **Tags:** `josh` (real owner cookie), `qa` (box test clients: `X-TT-QA` header or `tt_qa` cookie matching the `QA_KEY` secret, or the fake test owner cookie), `bot`, and `prospect` (previews) / `visitor` (main site).
- **Bot rules, in order:** probe path or a path that is not a real page; empty UA; bot/tool UA; box egress (AS13335 + IAD + a box address: 104.28.192.0/20, 2a09:bac0::/29 or a BOX_IPS entry; or the legacy Fort Worth geo). Since Oct 21, 2026 the box exit geolocates to Muscatine/Davenport, IA, so Iowa geography is never a box signal by itself; Chrome/119 Windows on AS13335; scanner ASNs (46261, 963, 47007, 18779; 3356 when non-US); cloud ASNs; no Accept-Language. Ordinary WARP / iCloud Private Relay users elsewhere stay real.
- **Main site:** `functions/_middleware.js` logs HTML page views (not assets, previews, /me, /p) with site="tt", via waitUntil.
- **Report:** `/me/visits` has "My website" and "Previews" sections. A preview prospect counts only after the password (login_ok or a page view). Plain gate views are listed as "opened the link".
- **Export:** `/me/visits.json?since=ISO&until=ISO&token=...` (or `Authorization: Bearer`). The token is the `VISITS_TOKEN` Pages secret. No raw IPs, only the salted hash `iph`.
- **QA setup on the box** lives under the agent-data tt-qa folder; it is not in the repo.
