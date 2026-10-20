# Website style samples gallery: RETIRED 2026-10-20

Josh retired the public gallery on 2026-10-20 (it made the offer look off-the-rack).

- `https://joshthetechtamer.com/demos-gallery/` and `/demos-gallery` now **301 to `/`** (`functions/demos-gallery/_middleware.js`).
- The old page and its thumbnails are archived in `previews/demos-gallery-retired-2026-10-20/` (not deployed; `cf_build.sh` skips `previews/`). Full history is in git (last live commit `fe9e33e`).
- The 12 `tpl-*.joshthetechtamer.workers.dev` template Workers still exist but their workers.dev URL is **turned off** (Cloudflare: Workers > tpl-* > Settings > Domains & Routes > workers.dev). Turn it back on to restore.
- Never link the gallery anywhere.

## To restore
1. `git mv previews/demos-gallery-retired-2026-10-20/demos-gallery demos-gallery` and the thumbs back to `assets/demos-gallery/thumbs`.
2. Restore the old middleware from commit `fe9e33e`.
3. Re-enable workers.dev on the tpl-* Workers.

## Still password-gated (unchanged)

`/demos/royalgrooming/` and `/demos/backinline/` use:
- `functions/demos/_middleware.js` and `functions/_lib/client-previews-gate.js`
- secrets `DEMOS_GALLERY_PASSWORD` and `DEMOS_GALLERY_COOKIE_SECRET`
- the cookie `tt_demos_auth`

The login form posts to `/demos-gallery/auth`, which the gallery middleware still routes to the gate handler (with `/demos-gallery/logout`). `/assets/demos-gallery/gallery.css` stays because the login page uses it. Never put the password in HTML, titles, errors, git or docs.
