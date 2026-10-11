from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import json,re,sys
from html import unescape,escape
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
  path=unquote(u.path.lstrip('/'))
  # Internal page links must use the final extensionless URL ("/" for home, "/rates" not "/rates.html").
  if t=='a' or (t=='link' and a.get('rel')=='canonical'):assert not path.endswith('.html'),('.html link (redirect hop)',f.name,a[key])
  target=(ROOT/'index.html' if path=='' else ROOT/(path+'.html') if (ROOT/(path+'.html')).is_file() else ROOT/path) if u.path else f
  assert target.is_file(),(f.name,a[key])
  if u.fragment and target.suffix=='.html':assert u.fragment in [x.get('id') for t,x in Page(target.read_text()).tags],(f.name,a[key])
  if t=='img':assert all(k in a for k in ['alt','width','height'])
  if t=='a' and a.get('href','').strip() in ('','#'):raise AssertionError(('empty link',f.name))
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
assert re.sub(r'<svg.*?</svg>|<[^>]+>','',h1,flags=re.S).split()==['See','your','website','built','before','you','spend','a','dime.'],h1
assert '<span class="wp-gold">built<svg class="wp-swoosh"' in h1 and 'aria-hidden="true"' in h1 and '<em class="wp-italic">dime</em>.' in h1,h1
pkg_head=pkg[:pkg.index('</head>')]
assert 'free demo' not in (h1+pkg_head).lower(),'no free demo in headline/title/meta'
assert 'wp-demo-note' not in pkg and 'Not unlimited redesigns' not in pkg and 'not unlimited redesigns' in pkg,'demo note removed; step 2 keeps it'
for page in ['rates.html','business.html']:assert 'href="/website-package"' in (ROOT/page).read_text(),page
rates=(ROOT/'rates.html').read_text();assert 'one-hour minimum' in rates and 'No subscription required.' not in rates
# Every page shares the homepage header (only aria-current and For Business's contact ?service= may differ).
hdr=lambda n:re.sub(r' aria-current="page"|\?service=[^"]*','',re.search(r'<header.*?</header>',(ROOT/n).read_text(),re.S).group())
for f in ROOT.glob('*.html'):assert hdr(f.name)==hdr('index.html'),('header differs',f.name)
# Main menu order (desktop nav and mobile slide-out share this markup); current page marked on Website Package.
nav=re.search(r'<nav class="navlinks".*?</nav>',(ROOT/'index.html').read_text(),re.S).group()
assert re.findall(r'>([^<>]+)</a>',nav)==['Tech Help','For Business','Get a Website','Digital Kits','Rates & FAQ','About Josh','Request a visit ↗'],nav
assert '<a href="/website-package" aria-current="page">Get a Website</a>' in (ROOT/'website-package.html').read_text()

# ---- Local SEO (Oct 2026 audit): final URLs, sitemap, robots, structured data, no address, no ratings ----
BASE='https://joshthetechtamer.com'
pages=sorted(f.name for f in ROOT.glob('*.html') if f.name!='404.html')
final=lambda n:BASE+'/'+('' if n=='index.html' else n[:-5])
for n in pages:
 s=(ROOT/n).read_text();head=s[:s.index('</head>')]
 assert re.findall(r'<link rel="canonical" href="([^"]+)">',head)==[final(n)],('canonical',n)
 assert re.findall(r'<meta property="og:url" content="([^"]+)">',head)==[final(n)],('og:url',n)
 assert '.html' not in ''.join(re.findall(r'(?:href|content)="(https://joshthetechtamer\.com[^"]*)"',s)),('absolute .html URL',n)
 title=re.search(r'<title>(.*?)</title>',head).group(1);desc=re.search(r'<meta name="description" content="([^"]*)">',head).group(1)
 assert len(unescape(desc))<=160,('meta description too long',n,len(unescape(desc)))
 blocks=[json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s)];assert len(blocks)==1,n
 graph=blocks[0]['@graph'];biz=graph[0]
 assert blocks[0]['@context']=='https://schema.org' and biz['@type']==['ProfessionalService','LocalBusiness'] and biz['@id']==BASE+'/#business',n
 assert biz['telephone']=='+1-563-261-0200' and 'streetAddress' not in biz['address'],n
 dump=json.dumps(blocks[0])
 assert 'aggregateRating' not in dump and 'reviewRating' not in dump and '"Review"' not in dump,('no review/rating markup',n)
 for node in graph:
  assert node['@type'] in (['ProfessionalService','LocalBusiness'],'BreadcrumbList','Service','FAQPage'),node['@type']
  if node['@type']=='BreadcrumbList':
   assert all(i['item'].startswith(BASE) and not i['item'].endswith('.html') for i in node['itemListElement']),n
   assert node['itemListElement'][-1]['item']==final(n),n
  if node['@type']=='FAQPage':
   # FAQ markup only where the same questions are visible on the page.
   vis=unescape(re.sub(r'<[^>]+>','',s))
   for q in node['mainEntity']:assert q['name'] in vis and q['acceptedAnswer']['text'] in vis,('FAQ markup must match visible text',n,q['name'])
 assert (n=='index.html')==(not any(x['@type']=='BreadcrumbList' for x in graph)),n
cfg=json.loads((ROOT/'data/site-config.json').read_text())
for k in ['google_business_profile_url','google_review_url']:
 v=cfg.get(k,'')
 for n in pages:
  if v:assert v in (ROOT/n).read_text(),(k,n)
assert cfg.get('google_business_profile_url','')=='' or cfg['google_business_profile_url'] in json.dumps(json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',(ROOT/'index.html').read_text()).group(1)))
nf=(ROOT/'404.html').read_text();assert 'rel="canonical"' not in nf and 'noindex' in nf
sm=(ROOT/'sitemap.xml').read_text();locs=re.findall(r'<url><loc>([^<]+)</loc><lastmod>(\d{4}-\d{2}-\d{2})</lastmod></url>',sm)
assert sorted(l for l,_ in locs)==sorted(final(n) for n in pages) and sm.count('<url>')==len(pages),'sitemap: every page, final URLs, with lastmod'
assert (ROOT/'robots.txt').read_text()=='User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n'
for n in ['tech-help-muscatine.html','service-area.html','scam-help.html','tech-help-quad-cities.html']:assert n in pages and 'Built by' in (ROOT/n).read_text(),n
idx=(ROOT/'index.html').read_text()
assert 'hero-logo.png' not in ''.join((ROOT/n).read_text() for n in pages+['404.html']),'1.48 MB hero-logo.png must not be referenced'
assert 'image/webp' in idx and 'hero-logo-800.webp' in idx
for n in ['index.html','services.html']:assert 'href="/tech-help-muscatine"' in (ROOT/n).read_text(),n
# Homepage hero stays exactly as Josh approved it (only the image is the optimized <picture>, and links are extensionless).
hero=re.search(r'<section class="hero">.*?</section>',idx,re.S).group()
assert '<div class="eyebrow">Your local tech guy · Muscatine, Iowa</div><h1>Not very tech savvy?<br><span>I’ll come to you.</span></h1>' in hero and 'eyebrow-h1' not in hero and 'hero-local' not in hero,'home hero changed'
assert 'In-home computer &amp; tech help in Muscatine, IA' in idx and 'House calls all over' in idx
# Quad Cities on both sides of the river, plus Iowa City and Coralville, in the business areaServed.
served=[a['name'] for a in json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',idx).group(1))['@graph'][0]['areaServed']]
FINAL=['Muscatine, IA','Fruitland, IA','Wilton, IA','West Liberty, IA','Durant, IA','Columbus Junction, IA','Atalissa, IA','Buffalo, IA','Blue Grass, IA','Davenport, IA','Bettendorf, IA','Moline, IL','Rock Island, IL','East Moline, IL','Silvis, IL','Milan, IL','Illinois City, IL','Iowa City, IA','Coralville, IA','Letts, IA','Nichols, IA','Muscatine County, IA']
assert sorted(served)==sorted(FINAL),('areaServed must match Josh’s Google profile list',set(served)^set(FINAL))
site=''.join((ROOT/n).read_text() for n in pages)
assert 'New Boston' not in site and 'trucker' not in site and 'Xbox accounts all at once' not in site
assert '30-mile radius' in (ROOT/'service-area.html').read_text() and 'gas charge' in (ROOT/'service-area.html').read_text()
assert not re.search(r'about (?!30 )\d+ miles',(ROOT/'service-area.html').read_text(),re.I),'no per-town distances'
assert 'Illinois-side customers can ask' not in (ROOT/'tech-help-quad-cities.html').read_text() and 'a couple times a week' in (ROOT/'tech-help-quad-cities.html').read_text()
# Security cameras/systems are residential (in-home) only: never offered for businesses (not licensed for commercial security in Iowa).
for n in ['services.html','business.html']:assert 'residential' in (ROOT/n).read_text() and 'commercial or business security' in (ROOT/n).read_text(),n
assert '<svg class="area-svg"' in (ROOT/'service-area.html').read_text() and 'See me on Google Maps' in (ROOT/'service-area.html').read_text()
# Review carousel: every entry in data/reviews.json renders verbatim; stars only for the two Google 5-star reviews; Facebook items carry no rating.
revs=json.loads((ROOT/'data/reviews.json').read_text())
assert idx.count('class="review-card"')==len(revs) and idx.count('class="review-stars"')==2 and f'1 / {len(revs)}' in idx
for r in revs:
 assert escape(r['quote'],quote=True) in idx,('review not verbatim',r['name'])
 assert (r['rating'] is None)==r['source'].startswith('Facebook'),r
# Never publish the street address (service-area business).
for n in pages+['404.html']:assert 'Cedar' not in (ROOT/n).read_text() and 'streetAddress' not in (ROOT/n).read_text(),n
if '--production' in sys.argv:
 assert json.loads((ROOT/'data/site-config.json').read_text())['form_mode']=='cloudflare'
 contact=(ROOT/'contact.html').read_text();script=(ROOT/'assets/site.js').read_text()
 assert 'action="/api/lead" method="post"' in contact and 'mailto:joshthetechtamer@gmail.com" method' not in contact
 assert 'challenges.cloudflare.com/turnstile/v0/api.js' in contact and 'id="request-turnstile"' in contact
 assert 'Send request' in contact and "action:'lead'" in script and 'encodeURIComponent(body)' not in script
 assert (ROOT/'functions/api/lead.js').is_file()

print('PASS: HTML nesting, internal links/anchors, headings, images, structured data, all six kit links, review ratings and deployment exclusions.')
