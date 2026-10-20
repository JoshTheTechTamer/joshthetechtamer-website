#!/usr/bin/env python3
"""Build /demos-gallery/index.html from data/demos-gallery.json + site chrome.

Usage:
  python3 scripts/build_demos_gallery.py              # live rules: only enabled:true
  python3 scripts/build_demos_gallery.py --preview    # show all demos (for local review)
  python3 scripts/build_demos_gallery.py --out DIR    # write into DIR/demos-gallery/
"""
from __future__ import annotations
import argparse, html, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "demos-gallery.json"
CHROME = ROOT / "about.html"  # stable page with full header/footer

# Link-invite only (Josh, 2026-10-19): the gallery is public but not linked from any
# page, nav, footer, sitemap or schema, and stays noindex. Shared by direct link only.
GALLERY_LINK = re.compile(r'<a href="/?demos-gallery/?[^"]*"[^>]*>[^<]*</a>')

_ABS_OK = re.compile(r'^(?:/|#|[a-z][a-z0-9+.-]*:)', re.I)


def absolutize(fragment: str) -> str:
    """Make every relative href/src in borrowed chrome root-absolute.

    about.html lives at the site root, so its relative links (e.g. href="demos-gallery/")
    break when reused at /demos-gallery/ (they resolve to /demos-gallery/demos-gallery/).
    """
    def fix(m):
        attr, q, val = m.group(1), m.group(2), m.group(3)
        if not val or _ABS_OK.match(val):
            return m.group(0)
        val = val[2:] if val.startswith("./") else val
        return f'{attr}={q}/{val}{q}'
    return re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix, fragment)


def strip_gallery_links(fragment: str) -> str:
    return GALLERY_LINK.sub("", fragment)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def extract_chrome(src: str) -> tuple[str, str, str]:
    """Return (head_open_through_body_start_with_header, footer_through_end, unused)."""
    # Head: reuse about.html head but we'll rewrite title/meta
    m_head = re.search(r"(<head>)([\s\S]*?)(</head>)", src)
    m_top = re.search(r"(<body>[\s\S]*?</header>)", src)
    m_foot = re.search(r"(<footer class=\"footer\">[\s\S]*</html>)", src)
    if not (m_head and m_top and m_foot):
        raise SystemExit("Could not parse chrome from about.html")
    return m_head.group(2), m_top.group(1), m_foot.group(1)


def card(d: dict, label: str, preview_flag: bool) -> str:
    cls = "dg-card" + (" dg-dev-flag" if preview_flag and not d.get("enabled") else "")
    thumb = esc(d.get("thumb") or "")
    name = esc(d["name"])
    loc = esc(d.get("location") or "")
    blurb = esc(d.get("blurb") or "")
    url = esc(d["url"])
    return f'''<article class="{cls}">
  <a class="dg-card__shot" href="{url}" target="_blank" rel="noopener noreferrer">
    <img src="{thumb}" alt="Screenshot of the {name} website style sample" width="640" height="400" loading="lazy" decoding="async">
  </a>
  <div class="dg-card__body">
    <p class="dg-card__label">{esc(label)}</p>
    <h2>{name}</h2>
    <p class="dg-card__loc">{loc}</p>
    <p class="dg-card__blurb">{blurb}</p>
    <p class="dg-card__note">Every client site is custom-built.</p>
    <a class="btn" href="{url}" target="_blank" rel="noopener noreferrer">Open style sample<span aria-hidden="true">↗</span></a>
  </div>
</article>'''


def build(preview: bool, out_dir: Path) -> Path:
    catalog = json.loads(DATA.read_text())
    demos = catalog["demos"]
    label = catalog.get("free_preview_label") or "Free preview — not the business's live site"
    if preview:
        shown = demos
    else:
        shown = [d for d in demos if d.get("enabled")]

    head_inner, body_top, foot = extract_chrome(CHROME.read_text())
    body_top, foot = strip_gallery_links(absolutize(body_top)), strip_gallery_links(absolutize(foot))
    # Rewrite head meta
    head_inner = re.sub(r"<title>[\s\S]*?</title>", f"<title>{esc(catalog['page_title'])}</title>", head_inner, count=1)
    head_inner = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{esc(catalog["page_blurb"])}">',
        head_inner,
        count=1,
    )
    # Force noindex
    if 'name="robots"' in head_inner:
        head_inner = re.sub(
            r'<meta name="robots" content="[^"]*">',
            '<meta name="robots" content="noindex, nofollow, noarchive">',
            head_inner,
            count=1,
        )
    else:
        head_inner = '<meta name="robots" content="noindex, nofollow, noarchive">\n' + head_inner
    # Drop canonical / schema / og that would look like a public page
    head_inner = re.sub(r'<link rel="canonical"[^>]*>', "", head_inner)
    head_inner = re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>', "", head_inner)
    head_inner = re.sub(r'<meta property="og:[^"]*" content="[^"]*">', "", head_inner)
    head_inner = re.sub(r'<meta name="twitter:[^"]*" content="[^"]*">', "", head_inner)
    if "demos-gallery/gallery.css" not in head_inner:
        head_inner += '\n<link rel="stylesheet" href="/assets/demos-gallery/gallery.css">'

    body_top = re.sub(r'\saria-current="page"', '', body_top)

    cards = "\n".join(card(d, label, preview) for d in shown) or (
        '<p class="dg-empty">No previews are listed yet. If Josh shared a link with you, '
        "use that link — or text him at 563-261-0200 and he’ll send yours again.</p>"
    )

    banner = ""
    if preview:
        n_all = len(demos)
        n_on = sum(1 for d in demos if d.get("enabled"))
        banner = (
            f'<div class="dg-banner" role="status"><span><strong>Local preview build.</strong> '
            f"Showing all {n_all} cards ({n_on} enabled for live). "
            f"Dashed outline = not enabled yet.</span>"
            "</div>"
        )
    else:
        banner = (
            '<div class="dg-banner"><span><strong>Style sample · fictional business · sample content.</strong> '
            "These businesses are made up. Every client site is custom-built.</span></div>"
        )

    main = f'''<main id="main">
<section class="page-hero ds-hero">
  <span class="ds-deco" aria-hidden="true"><span class="ds-dots ds-dots--tr"></span><span class="ds-stripe"></span></span>
  <div class="wrap">
    <p class="breadcrumb"><a href="/">Home</a> <span>/</span> Website style samples</p>
    <div class="eyebrow">Style samples</div>
    <h1>Website style <span class="ds-gold">samples<svg class="ds-swoosh" viewBox="0 0 200 18" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path pathLength="1" d="M3 12.5C40 6.5 92 4.2 140 5.6c20 .6 38 2 55 4.4" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/><path pathLength="1" d="M18 15.5c38-4.6 86-6 150-3.4" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".55"/></svg></span></h1>
    <p class="lead">{esc(catalog["page_blurb"])}</p>
  </div>
</section>
<section class="section dg-page">
  <div class="wrap">
    {banner}
    <div class="dg-grid">
      {cards}
    </div>
  </div>
</section>
</main>'''

    page = (
        "<!doctype html><html lang=\"en\"><head>"
        + head_inner
        + "</head>"
        + body_top
        + main
        + foot
    )
    bad = re.findall(r'(?:href|src)="(?![/#]|[a-zA-Z][a-zA-Z0-9+.-]*:)[^"]*"', page)
    if bad:
        raise SystemExit(f"Relative links left in page: {bad[:5]}")
    if GALLERY_LINK.search(body_top + foot) or "/demos-gallery/logout" in page:
        raise SystemExit("Gallery nav/footer link or logout link left in page chrome")

    dest = out_dir / "demos-gallery"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(page)
    return dest / "index.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="Show all demos, even enabled:false")
    ap.add_argument("--out", type=Path, default=ROOT, help="Site root to write into")
    args = ap.parse_args()
    path = build(args.preview, args.out)
    print(f"Wrote {path} (preview={args.preview})")


if __name__ == "__main__":
    main()
