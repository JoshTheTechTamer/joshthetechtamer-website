# Website style samples gallery (public, link-invite only)

URL: `https://joshthetechtamer.com/demos-gallery/` (shared by direct link only)

- No password since 2026-10-19 (approved by Josh). It lists 12 fictional style-sample templates on `tpl-*.joshthetechtamer.workers.dev`. Branded client originals are never listed.
- **Not linked anywhere.** Keep it out of every nav, footer, page body, `sitemap.xml` and JSON-LD. `scripts/build_demos_gallery.py` strips any gallery link from the borrowed about.html chrome, and fails if one is left or if any relative link remains.
- **noindex:** `<meta name="robots" content="noindex, nofollow, noarchive">` plus `X-Robots-Tag` (set by `functions/demos-gallery/_middleware.js`). `robots.txt` deliberately does **not** block it, so crawlers can read the noindex.

## Still password-gated (unchanged)

`/demos/royalgrooming/` and `/demos/backinline/` use:
- `functions/demos/_middleware.js` and `functions/_lib/client-previews-gate.js`
- secrets `DEMOS_GALLERY_PASSWORD` and `DEMOS_GALLERY_COOKIE_SECRET`
- the cookie `tt_demos_auth`

The login form posts to `/demos-gallery/auth`, which the gallery middleware still routes to the gate handler (with `/demos-gallery/logout`). Never put the password in HTML, titles, errors, git or docs.

`scripts/serve_demos_gallery.mjs` is the old local gate preview and still gates the gallery locally. It is a dev tool only.

## Edit cards

Edit `data/demos-gallery.json`, then run `python3 scripts/build_demos_gallery.py` and `python3 scripts/validate_site.py`.
