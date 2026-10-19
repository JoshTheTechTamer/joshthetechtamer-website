# Client website previews (password-protected)

URL (live): `https://joshthetechtamer.com/demos-gallery/`

Visible label: **Client website previews**. Path: `/demos-gallery/`.

## Gate

- Pages Function: `functions/demos-gallery/_middleware.js`
- Secrets (Pages → Settings → Environment variables): `DEMOS_GALLERY_PASSWORD`, `DEMOS_GALLERY_COOKIE_SECRET`
- Changing the password needs no rebuild
- Never put the password in HTML, titles, errors, placeholders, git, or docs

## Enable a demo

Edit `data/demos-gallery.json` → `"enabled": true` after Josh OKs, then:

```bash
python3 scripts/build_demos_gallery.py
```

## Local preview server

```bash
DEMOS_GALLERY_PASSWORD='…' node scripts/serve_demos_gallery.mjs
```

Password only in the start-command env (not in served pages).

## noindex

Meta + `X-Robots-Tag`, `robots.txt` Disallow `/demos-gallery/`, not in sitemap, never IndexNow.
