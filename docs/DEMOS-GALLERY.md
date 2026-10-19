# Client website previews (password-protected)

URL: `https://joshthetechtamer.com/demos-gallery/`

Also gated (same login): `/demos/royalgrooming/`, `/demos/backinline/`

## Gate

- Shared logic: `functions/_lib/client-previews-gate.js`
- Middleware: `functions/demos-gallery/_middleware.js`, `functions/demos/_middleware.js`
- Secrets: `DEMOS_GALLERY_PASSWORD`, `DEMOS_GALLERY_COOKIE_SECRET`
- Cookie `tt_demos_auth` with **Path=/** (one login unlocks gallery + gated demos)
- Auth POST: `/demos-gallery/auth` — `next` must be a safe same-site path under the gated prefixes
- Never put the password in HTML, titles, errors, git, or docs

## Enable a demo card

Edit `data/demos-gallery.json` → `"enabled": true`, then `python3 scripts/build_demos_gallery.py`

## noindex

Meta + `X-Robots-Tag` on gated responses; `robots.txt` Disallow `/demos-gallery/`; not in sitemap.
