# "Built by The Tech Tamer" footer credit

A small maker's-mark badge for the footer of every site Josh builds. It matches the
badge on joshthetechtamer.com exactly (same shape, spacing, type and hover), all on one
line: a small **BUILT BY** label, the full ringmaster lockup (mascot circle with phone
and lasso plus the THE TECH TAMER glitch wordmark, transparent, nothing cropped) at
40px tall, and **Want a site like this? →**. The whole badge links to the contact page
with "Website & business tech" preselected, in a new tab.

On dark footers (`ttb--dark`) there is no white plate. The badge swaps in
`built-by-lockup-dark.webp` (142×120, embedded), where the black "TECH TAMER" letters
are recolored light (#f4f6fa) and the cyan/magenta glitch accents are kept, plus a
faint light glow so the hat and suit edges stay visible on black.

This folder lives in `templates/`, which `scripts/cf_build.sh` and `_config.yml` both
keep out of the published site. `scripts/build_pages.py` only reads `templates/*.html`,
so this subfolder never gets built as a page.

## Files

| File | What it is |
| --- | --- |
| `snippet.html` | **The drop-in block for client and demo sites (v3).** It includes its own `<style>` and both lockups as embedded transparent WebPs (light 94×80 about 6 KB, dark 142×120 about 12 KB), so nothing has to be uploaded. CSS shows the one that matches the variant; you can delete the unused `<img>`. |
| `built-by-lockup-dark.webp` | Source file for the dark-footer lockup (light wordmark). |
| `demo.html` | A preview of the snippet on light and dark footers. Open it in a browser. |
| `README.md` | This file. |

## Add it to a client or demo site (about 2 minutes)

1. Open the client site's footer, usually the bottom of `index.html` and each page, or the shared footer include.
2. Paste the whole `snippet.html` block just inside the end of the footer, after the copyright line.
3. Change `utm_source=CLIENT-SLUG` to a short client name, for example `utm_source=mvp563` or `utm_source=royalgrooming`.
4. Pick the variant that matches the footer background:
   - Light or white footer: keep `ttb ttb--light`.
   - Dark footer (navy, black, photo): change it to `ttb ttb--dark`.
5. Preview it on desktop and phone before publishing.

The link opens in a new tab with `rel="noopener"` and looks like this:

```
https://joshthetechtamer.com/contact?service=Website%20%26%20business%20tech&ref=client-footer&utm_source=CLIENT-SLUG&utm_medium=referral&utm_campaign=built-by
```

`ref=client-footer` plus the UTM tags show which client site sent each visitor once
analytics (for example Cloudflare Web Analytics or GA4) is turned on.

### Options

- **Center vs. left-align:** the `.ttb-row` wrapper centers the badge. To left-align it, remove the wrapper `<div>` and keep just the `<a>`.
- **Already has a footer row:** drop only the `<a class="ttb ...">…</a>` into the existing row. Keep the `<style>` block.
- **Search engines:** the link uses a plain brand name, not keywords, so it's fine as a normal link. If a client ever wants it hidden from search engines, change `rel="noopener"` to `rel="noopener nofollow"`.
- **Hosted image instead of embedded:** after this branch is merged, `https://joshthetechtamer.com/assets/built-by-lockup.webp` (142×120, transparent) can replace the `data:` image source.
- **Ask first:** only add the badge with the client's OK. Shawn (mvp563.com) is first.

## On joshthetechtamer.com itself

Every page's `.footer-bottom` has a self-referencing version: **BUILT BY [lockup] · Want a site like this? →**. It links to
`/contact.html?service=Website%20%26%20business%20tech`, which preselects
"Website & business tech" on the contact form. The same `.ttb` styles are in
`assets/site.css`, along with footer overrides so the theme's `.footer a` and mobile
`.footer-bottom span` rules don't restyle it. The lockup crop is the full transparent `assets/hero-logo.png` with 14px of padding around everything, so the phone, the rope loop and the wordmark underline are all fully visible.

The badge is in both `templates/*.html` (the build source) and the root `*.html` pages,
so rerunning `scripts/build_pages.py` keeps it.
