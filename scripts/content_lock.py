"""Content lock for the sitewide redesign: everything a visitor reads or a search engine indexes.
`python3 scripts/content_lock.py --write` snapshots it to data/content-lock.json (run once on main before a restyle);
validate_site.py then fails if any page's words, links, images, forms, header, footer, JSON-LD or head metadata change."""
from pathlib import Path
from html import unescape
import re,json,sys
ROOT=Path(__file__).resolve().parents[1]
def text(h):
 h=re.sub(r'<(script|style)\b.*?</\1>','',h,flags=re.S)
 h=re.sub(r'<svg class="ds-swoosh".*?</svg>','',h,flags=re.S)  # decorative accent, aria-hidden, no text
 h=re.sub(r'</?(?:span|em|strong|b|i|small|a)\b[^>]*>','',h)  # inline tags don't split words
 return ' '.join(unescape(re.sub(r'<[^>]+>',' ',h)).split())
def lock(s):
 head=s[:s.index('</head>')];body=s[s.index('</head>'):]
 main=body[body.index('<main'):body.index('</main>')]
 return {'title':re.findall(r'<title>.*?</title>',head),
  'meta':sorted(re.findall(r'<meta [^>]*>',head)),
  'canonical':re.findall(r'<link rel="canonical"[^>]*>',head),
  'jsonld':re.findall(r'<script type="application/ld\+json">.*?</script>',s,re.S),
  'header':re.search(r'<header\b.*?</header>',s,re.S).group(),
  'footer':re.search(r'<footer\b.*?</footer>',s,re.S).group(),
  'forms':re.findall(r'<form\b.*?</form>',s,re.S),
  'main_text':text(main),
  'h1_text':text(re.search(r'<h1\b.*?</h1>',s,re.S).group()),
  'links':re.findall(r'<a [^>]*href="([^"]*)"',main),
  'images':[[re.search(r'src="([^"]*)"',t).group(1),(re.search(r'alt="([^"]*)"',t) or [None,None])[1]] for t in re.findall(r'<img [^>]*>',s)],
  'review_cards':re.findall(r'<article class="review-card".*?</article>',s,re.S)}
def snapshot(root=ROOT):return {f.name:lock(f.read_text()) for f in sorted(Path(root).glob('*.html'))}
if __name__=='__main__' and '--write' in sys.argv:
 # optional: --from <dir> snapshots a checkout of main (e.g. git worktree of the backup tag)
 src=sys.argv[sys.argv.index('--from')+1] if '--from' in sys.argv else ROOT
 (ROOT/'data/content-lock.json').write_text(json.dumps(snapshot(src),ensure_ascii=False,indent=0));print('wrote data/content-lock.json from',src)
