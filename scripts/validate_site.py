from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,s):super().__init__();self.tags=[];self.stack=[];self.feed(s);assert not self.stack,self.stack
 def handle_starttag(self,t,a):
  self.tags.append((t,dict(a)))
  if t not in ['meta','link','img','br','hr','input','source','wbr','area','base','col','embed','param','track']:self.stack.append(t)
 def handle_endtag(self,t):assert self.stack.pop()==t,t
for f in ROOT.glob('*.html'):
 s=f.read_text();p=Page(s);ids=[a['id'] for t,a in p.tags if 'id' in a];assert len(ids)==len(set(ids));assert sum(t=='h1' for t,a in p.tags)==1
 for t,a in p.tags:
  key='src' if t in ['img','script'] else 'href' if t in ['a','link'] else None
  if not key or key not in a:continue
  u=urlparse(a[key]);
  if u.scheme or u.netloc:continue
  target=ROOT/unquote(u.path.lstrip('/')) if u.path else f
  assert target.is_file(),(f.name,a[key])
  if u.fragment and target.suffix=='.html':assert u.fragment in [x.get('id') for t,x in Page(target.read_text()).tags],(f.name,a[key])
  if t=='img':assert all(k in a for k in ['alt','width','height'])
 for schema in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s):json.loads(schema)
kit=(ROOT/'digital-kits.html').read_text();base=(ROOT/'templates/digital-kits.html').read_text()
assert kit.count('class="product"')==6
assert re.findall(r'https://joshthetechtamer.gumroad.com/l/[^" ]+',kit)==re.findall(r'https://joshthetechtamer.gumroad.com/l/[^" ]+',base)
assert 'class="review-carousel"' in (ROOT/'index.html').read_text()
assert [r['rating'] for r in json.loads((ROOT/'data/reviews.json').read_text())].count(5)==2
assert 'backups' in (ROOT/'_config.yml').read_text()
# Website Package page: linked from Rates and For Business; unapproved example sites stay hidden.
pkg=(ROOT/'website-package.html').read_text();cfg=json.loads((ROOT/'data/site-config.json').read_text())
for needed in ['$800','$400 deposit','$25','First month free, cancel anytime','billed monthly to your card through Stripe','$120/year','sms:+15632610200','tel:+15632610200','Built by']:assert needed in pkg,needed
assert ('mvp563.com' in pkg)==bool(cfg.get('show_mvp563_example')),'mvp563 example flag'
assert '<!--EXAMPLE:' not in pkg
h1=re.search(r'<h1[^>]*>(.*?)</h1>',pkg,re.S).group(1)
assert '<span class="wp-h1-a">See your website built</span>' in h1 and '<span class="wp-h1-b">before you spend a dime.</span>' in h1,h1
pkg_head=pkg[:pkg.index('</head>')]
assert 'free demo' not in (h1+pkg_head).lower(),'no free demo in headline/title/meta'
assert 'wp-demo-note' not in pkg and 'Not unlimited redesigns' not in pkg and 'not unlimited redesigns' in pkg,'demo note removed; step 2 keeps it'
for page in ['rates.html','business.html']:assert '/website-package.html' in (ROOT/page).read_text(),page
rates=(ROOT/'rates.html').read_text();assert 'one-hour minimum' in rates and 'No subscription required.' not in rates
assert '/website-package.html' in (ROOT/'sitemap.xml').read_text()
# Every page shares the homepage header (only aria-current and For Business's contact ?service= may differ).
hdr=lambda n:re.sub(r' aria-current="page"|\?service=[^"]*','',re.search(r'<header.*?</header>',(ROOT/n).read_text(),re.S).group())
for f in ROOT.glob('*.html'):assert hdr(f.name)==hdr('index.html'),('header differs',f.name)
# Main menu order (desktop nav and mobile slide-out share this markup); current page marked on Website Package.
nav=re.search(r'<nav class="navlinks".*?</nav>',(ROOT/'index.html').read_text(),re.S).group()
assert re.findall(r'>([^<>]+)</a>',nav)==['Tech Help','For Business','Get a Website','Digital Kits','Rates & FAQ','About Josh','Request a visit ↗'],nav
assert '<a href="/website-package.html" aria-current="page">Get a Website</a>' in (ROOT/'website-package.html').read_text()
if '--production' in sys.argv:
 assert json.loads((ROOT/'data/site-config.json').read_text())['form_mode']=='cloudflare'
 contact=(ROOT/'contact.html').read_text();script=(ROOT/'assets/site.js').read_text()
 assert 'action="/api/lead" method="post"' in contact and 'mailto:joshthetechtamer@gmail.com" method' not in contact
 assert 'challenges.cloudflare.com/turnstile/v0/api.js' in contact and 'id="request-turnstile"' in contact
 assert 'Send request' in contact and "action:'lead'" in script and 'encodeURIComponent(body)' not in script
 assert (ROOT/'functions/api/lead.js').is_file()

print('PASS: HTML nesting, internal links/anchors, headings, images, structured data, all six kit links, review ratings and deployment exclusions.')
