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
assert [r['rating'] for r in json.loads((ROOT/'data/reviews.json').read_text())].count(5)==3
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
assert re.findall(r'>([^<>]+)</a>',nav)==['Tech Help','For Business','Get a Website','Scam Help','Rates & FAQ','About Josh','Request a visit ↗'],nav
assert '<a href="/website-package" aria-current="page">Get a Website</a>' in (ROOT/'website-package.html').read_text()

# ---- Website Package showcase (Oct 2026): copy, timeline, slider, features, extras card, motion + weight ----
css=(ROOT/'assets/website-package.css').read_text();wpjs=(ROOT/'assets/website-package.js').read_text()
wcopy=json.loads((ROOT/'data/website-package-copy.json').read_text())
assert wcopy['hero_price_build']=='Only $800 to build & launch.' and wcopy['hero_kicker_lead']=='Like it?'
kick=re.search(r'<p class="wp-kicker">(.*?)</p>',pkg,re.S).group(1)
assert re.sub(r'<[^>]+>','',kick).split()==['Like','it?','Only','$800','to','build','&amp;','launch.','$25/month','hosting','&amp;','care,','first','month','free.'],kick
tl=re.search(r'<ol class="wp-tl" data-wp-timeline>(.*?)</ol>',pkg,re.S).group(1)
assert tl.count('<li class="wp-tl-step')==5 and tl.count('class="wp-step-num"')==5
assert re.findall(r'<h3>(.*?)</h3>',tl)==['A short call.','Build a free preview.','A fit check.','$800 to launch.','Go-live.'],'timeline headings'
assert 'A $400 deposit gets us started. The other $400 is due when your site goes live.' in tl and 'not unlimited redesigns' in tl
# one slate blue for every step number: a single background rule, no per-step colour overrides
num_bg=[r for r in re.findall(r'([^{}]*\.wp-step-num[^{}]*)\{([^{}]*)\}',css) if 'background' in r[1]]
assert len(num_bg)==1 and 'background:var(--slate)' in num_bg[0][1],num_bg
assert not re.search(r'wp-tl-step--(free|live)[^{]*\.wp-step-num',css) and '.wp-step--free' not in css
# before/after: accessible native range, generic mock (no real Facebook branding), lazy images
ba=re.search(r'<div class="wp-ba".*?</div></div><p class="wp-ba-note">',pkg,re.S).group()
assert 'type="range"' in ba and 'aria-label="Compare:' in ba and ba.count('loading="lazy"')==2
mock=(ROOT/'assets/website-package/social-page-mock.svg').read_text()
assert 'facebook' not in mock.lower() and '<image' not in mock and 'not a real business' in mock
assert 'generic mock-up, not a real business' in pkg
# What you get: only agreement-backed claims
feat=re.findall(r'<li class="wp-feat"[^>]*>.*?<h3>(.*?)</h3>',pkg,re.S)
assert feat==['Looks great on phones and computers','One-tap call &amp; booking buttons','Google Maps &amp; reviews','Your own web address','Hosting for the first year','One round of revisions'],feat
assert not re.search(r'guarantee|fast[- ]loading|\d+% |#1 ',re.sub(r'<[^>]+>',' ',pkg.split('</head>')[1]),re.I),'no guarantees or invented stats'
# polished "What costs extra" (wording kept) vs. plain "Without the Care Plan"
ex=re.search(r'<article class="wp-mini wp-mini--extra".*?</article>',pkg,re.S).group()
for t in ['Requested changes: $50/hour, with or without the Care Plan. This means new content, new pages, design changes, new services or prices, and new photos.','Website audits: $50/hour','Hosting and domain after year one without the Care Plan: $120/year (included with the Care Plan)']:assert t in ex,t
assert ex.count('<svg')==4 and 'border-box' in css
plain=re.search(r'<article class="wp-mini wp-mini--plain".*?</article>',pkg,re.S).group();assert '<svg' not in plain and 'Without the Care Plan' in plain
# motion: content is never hidden without JS; reduced motion shows everything still; tilt is mouse-only
for sel,body in re.findall(r'([^{}]*)\{([^{}]*opacity:0[^{}]*)\}',css):
 if 'data-rv' in sel or 'wp-tl-card' in sel:assert sel.strip().startswith(('.wp-anim','.wp-tl-anim')),sel
rm=re.search(r'@media\(prefers-reduced-motion:reduce\)\{(.*?)\n\}',css,re.S).group(1)
for need in ['.wp-phone-tall','[data-rv],.wp-tl-card{opacity:1!important;transform:none!important}','.wp-tl{--fill:1!important}','.wp-price{transform:none!important}','animation:none!important']:assert need in rm,need
assert "matchMedia('(prefers-reduced-motion: reduce)')" in wpjs and "'(hover: hover) and (pointer: fine)'" in wpjs and "pointerType!=='mouse'" in wpjs
assert 'src="/assets/website-package.js?v=' in pkg
assert re.search(r'\.wp-phone-screen \.wp-phone-tall\{[^}]*aspect-ratio:auto',css) and 'translateY(calc(-100% + 100cqh))' in css and 'container-type:size' in css,'phone auto-scroll uses the real image height'
# weight: below-the-fold images lazy; eager bytes (images + page CSS/JS) stay small; phone scroll image loads after the page
main_html=pkg[pkg.index('<main'):]
after_hero=main_html[main_html.index('</section>'):]
assert all('loading="lazy"' in t for t in re.findall(r'<img [^>]*>',after_hero)),'below-the-fold images lazy'
eager=[re.search(r'src="([^"]+)"',t).group(1) for t in re.findall(r'<img [^>]*>',pkg) if 'loading="lazy"' not in t]
size=lambda u:(ROOT/u.lstrip('/').split('?')[0]).stat().st_size
eager_bytes=sum(size(u) for u in eager)+len(css)+len(wpjs)
assert eager_bytes<300_000,('website-package eager weight',eager_bytes)
assert 'jtt-home-mobile-tall' not in re.sub(r'data-tall-\d+="[^"]+"','',pkg) and max(size('assets/website-package/jtt-home-mobile-tall-%d.webp'%n) for n in (300,450))<160_000
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
# (Sitewide redesign: the band and the gold accent on "savvy" are restyling only; the words, buttons and photo stay.)
hero=re.search(r'<section class="hero ds-hero">.*?</section>',idx,re.S).group()
plain=re.sub(r'<span class="ds-deco".*?</span></span></span>|<svg class="ds-swoosh".*?</svg>','',hero,flags=re.S).replace('<span class="ds-gold">you</span>','you')
assert '<div class="eyebrow">Your local tech guy · Muscatine, Iowa</div><h1>Not very tech savvy?<br><span>I’ll come to you.</span></h1>' in plain and 'eyebrow-h1' not in hero and 'hero-local' not in hero,'home hero changed'
assert '<a class="btn " href="sms:+15632610200">Text Josh<span aria-hidden="true">↗</span></a><a class="btn secondary" href="/services">Explore services<span aria-hidden="true">↗</span></a>' in hero and 'hero-logo-800.webp' in hero and '<a class="art-label" href="tel:+15632610200">563-261-0200</a>' in hero,'home hero buttons/photo'
assert 'In-home computer &amp; tech help in Muscatine, IA' in idx and 'House calls all over' in idx
# Josh's final list (small towns first, then the Quad Cities on both sides of the river), no Iowa City/Coralville.
served=[a['name'] for a in json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',idx).group(1))['@graph'][0]['areaServed']]
for n in ['services.html','digital-kits.html']:
 t=(ROOT/n).read_text();assert 'helping a woman' not in t and 'alt="Josh Sargent showing Madonna something on a laptop at a kitchen table"' in t,('josh-helping alt',n)
FINAL=['Muscatine, IA','Fruitland, IA','Wilton, IA','West Liberty, IA','Durant, IA','Columbus Junction, IA','Letts, IA','Nichols, IA','Atalissa, IA','Buffalo, IA','Blue Grass, IA','Davenport, IA','Bettendorf, IA','Moline, IL','Rock Island, IL','East Moline, IL','Silvis, IL','Milan, IL','Illinois City, IL','Muscatine County, IA']
assert served==FINAL,('areaServed must be exactly Josh’s list, in his order',served)
for n in pages+['404.html']:
 t=(ROOT/n).read_text().replace('Muscatine · Iowa City · Quad Cities','')  # Josh's sign-off is the only allowed mention
 assert 'Iowa City' not in t and 'Coralville' not in t,('Iowa City/Coralville dropped',n)
 assert (ROOT/n).read_text().count('Muscatine · Iowa City · Quad Cities')==1,('sign-off unchanged',n)
sa=(ROOT/'service-area.html').read_text()
order=[sa.index('<h3>'+t+'</h3>') for t in ['Muscatine','Fruitland','Wilton','West Liberty','Durant','Columbus Junction','Letts','Nichols','Atalissa','Buffalo','Blue Grass','The Quad Cities','Illinois City','Muscatine County']]
assert order==sorted(order),'service-area town cards in Josh’s order'
for t in ['Letts','Nichols']:assert f'>{t}</text>' in sa,('map label',t)
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
assert idx.count('class="review-card"')==len(revs) and idx.count('class="review-stars"')==3 and f'1 / {len(revs)}' in idx
assert len(revs)==14 and '1 / 14' in idx,'14 carousel cards (Barb Google review added Oct 11)'
assert revs[2]=={'name':'Barb','source':'Google review','quote':'Josh is very knowledgeable and friendly. He helped me 2 times in home and a few times on line. Rates are very reasonable. If you need help contact him.','rating':5},'Barb Google card is card 3'
assert [x['name'] for x in revs].count('Barbara M.')==3,'her Facebook cards stay Barbara M.'
assert {'name':'Barbara M.','source':'Facebook comment','quote':'JOSH is very helpful explains things so you understand.','rating':None} in revs
for r in revs:
 assert escape(r['quote'],quote=True) in idx,('review not verbatim',r['name'])
 assert (r['rating'] is None)==r['source'].startswith('Facebook'),r
# Never publish the street address (service-area business).
for n in pages+['404.html']:assert 'Cedar' not in (ROOT/n).read_text() and 'streetAddress' not in (ROOT/n).read_text(),n

# ---- Sitewide redesign (Oct 2026): shared design layer on every page except the Website Package showcase ----
sys.path.insert(0,str(ROOT/'scripts'));import content_lock
# Content lock: words, links, images (src + alt), forms, header, footer, review cards, JSON-LD, title/metas/canonical
# are exactly what was on main before the restyle (data/content-lock.json).
locked=json.loads((ROOT/'data/content-lock.json').read_text());now=content_lock.snapshot()
assert set(locked)==set(now),set(locked)^set(now)
for n in locked:
 for k in locked[n]:
  a,b=locked[n][k],now[n][k]
  if k=='images':a,b=[list(x) for x in a],[list(x) for x in b]
  assert a==b,('content changed by the redesign',n,k)
dcss=(ROOT/'assets/design.css').read_text();djs=(ROOT/'assets/design.js').read_text()
GOLD={'index.html':'you','services.html':'Working','business.html':'work','digital-kits.html':'confidence','rates.html':'pricing','about.html':'local','contact.html':'tame','tech-help-muscatine.html':'Muscatine','service-area.html':'Muscatine','scam-help.html':'Help','tech-help-quad-cities.html':'In-Home','404.html':'wandered'}
for f in ROOT.glob('*.html'):
 t=f.read_text();head=t[:t.index('</head>')]
 if f.name=='website-package.html':assert 'design.css' not in t and 'ds-hero' not in t,'showcase keeps its own layer';continue
 assert re.search(r'<link rel="stylesheet" href="/assets/design\.css\?v=[^"]+">',head) and re.search(r'<script src="/assets/design\.js\?v=[^"]+" defer></script>',head),('design layer',f.name)
 assert head.index('site.css')<head.index('design.css'),f.name
 assert 'family=Montserrat' in head,f.name
 # one dark hero band (first section), with decorative dots + stripe hidden from assistive tech
 first=re.search(r'<main[^>]*>\s*<section class="([^"]*)">(<span class="ds-deco" aria-hidden="true">)?',t)
 assert first and 'ds-hero' in first.group(1).split() and first.group(2),('hero band',f.name)
 assert t.count('ds-hero')==1 and t.count('class="ds-deco"')==1,f.name
 # exactly one gold word, inside the H1, aria-hidden swoosh, word itself unchanged
 h1=re.search(r'<h1\b[^>]*>(.*?)</h1>',t,re.S).group(1)
 assert t.count('class="ds-gold"')==1 and h1.count('<span class="ds-gold">'+GOLD[f.name]+'<svg class="ds-swoosh"')==1,('gold word',f.name)
 assert all('aria-hidden="true"' in sv for sv in re.findall(r'<svg class="ds-swoosh"[^>]*>',t))
 # card icons stay decorative; every shape can draw in
 for ic in re.findall(r'<div class="icon[ "][^>]*><svg\b.*?</svg>',t,re.S):
  assert 'aria-hidden="true"' in ic and not re.search(r'<(path|rect|circle|line|polyline|polygon|ellipse)\b(?![^>]*pathLength="1")',ic),(f.name,ic[:80])
# timelines wherever there are steps
for n in ['index.html','services.html','tech-help-muscatine.html','tech-help-quad-cities.html']:
 t=(ROOT/n).read_text();assert t.count('data-ds-steps')==1 and not re.search(r'<div class="grid3">(?=<(?:article|div) class="step">)',t),n
# motion: hidden states only behind .ds-anim (JS on, no reduced motion); reduced motion = everything still and visible; tilt mouse-only
for sel,body in re.findall(r'([^{}]*)\{([^{}]*opacity:0[^{}]*)\}',dcss):
 if 'ds-rv' in sel:assert sel.strip().startswith('.ds-anim'),sel
assert '.ds-anim .icon:not(.is-drawn) svg *{stroke-dashoffset:1}' in dcss
rmd=re.search(r'@media\(prefers-reduced-motion:reduce\)\{(.*?)\n\}',dcss,re.S).group(1)
for need in ['.ds-rv{opacity:1!important;transform:none!important}','.ds-swoosh path{animation:none!important}','.icon svg *{stroke-dashoffset:0!important}','.ds-tilt{transform:none!important}','.ds-rope{clip-path:none!important;transition:none!important}']:assert need in rmd,need
assert "matchMedia('(prefers-reduced-motion: reduce)')" in djs.replace('mm(','matchMedia(') and "(hover: hover) and (pointer: fine)" in djs and "pointerType!=='mouse'" in djs
assert 'review-carousel' in djs and "closest('form')" in djs,'no reveal/tilt inside the carousel or forms'
# weight: the shared layer stays small
assert len(dcss)<26_000 and len(djs)<9_000,(len(dcss),len(djs))
# ---- Round 2 (Josh's feedback) ----
pages={f.name:f.read_text() for f in ROOT.glob('*.html')}
for n,t in pages.items():
 # Built-by badge -> Website Package; Digital Kits only in the footer (next to the scam + area links)
 assert re.search(r'<a class="ttb" href="/website-package">',t) and 'service=Website%20%26%20business%20tech"' not in re.search(r'<footer\b.*?</footer>',t,re.S).group(),n
 hdr=re.search(r'<header\b.*?</header>',t,re.S).group();ft=re.search(r'<footer\b.*?</footer>',t,re.S).group()
 if n=='scam-help.html':assert 'digital-kits' not in t and '<a href="/service-area">Areas I serve</a></div>' in ft,'no kit links on the scam page, footer included'
 else:assert 'digital-kits' not in hdr and '<a href="/service-area">Areas I serve</a><a href="/digital-kits">Digital kits</a></div>' in ft and ft.count('/digital-kits"')==1,n
 # Scam Help pill in the menu (after Get a Website), current on its own page
 assert re.search(r'Get a Website</a><a class="nav-scam" href="/scam-help"'+(' aria-current="page"' if n=='scam-help.html' else '')+r'><svg class="nav-scam__icon"[^>]*aria-hidden="true"',hdr),n
 assert '<a href="/scam-help">Scam &amp; hacked accounts</a>' in ft,n
for sn in ['snippet.html','demo.html','README.md']:
 st=(ROOT/'templates/built-by-footer'/sn).read_text()
 assert 'joshthetechtamer.com/contact?service=' not in st and 'https://joshthetechtamer.com/website-package?ref=client-footer' in st,sn
home=pages['index.html']
assert '<a class="hero-speech hero-speech-link" href="/website-package">If you like my website,<br><strong>I can build you one!</strong></a>' in home
assert 'a.hero-speech-link:focus-visible' in dcss and 'a.hero-speech-link:hover' in dcss
# recliner photo in the "A little help goes a long way." frame; alt describes Josh; no client photo left on the homepage
fr=re.search(r'<div class="home-paths-frame">(<img\b[^>]*>)</div>',home).group(1)
assert 'about-cta-laptop-' in fr and 'alt="Josh Sargent, The Tech Tamer, smiling in a recliner with a laptop on his lap"' in fr and 'loading="lazy"' in fr and 'client' not in fr and 'home-client-visit' not in home
# scam badges: own spot on Services (not stacked with the card button), and on the homepage under the help cards
WARN='<span class="scam-badge__icon"><svg viewBox="0 0 24 24" aria-hidden="true"'
svc=pages['services.html']
assert svc.count('class="scam-badge"')==1 and re.search(r'</ul><a class="scam-badge" href="/scam-help">'+re.escape(WARN),svc) and '<a class="textlink" href="/scam-help">' not in svc
assert re.search(r'Browse digital kits</a></article></div><a class="scam-badge scam-badge--wide" href="/scam-help">',home)
assert '.scam-badge:focus-visible' in dcss and 'background:#fff1ec' in dcss and 'color:#8f2a17' in dcss
# scam page: calm heading, 8-step numbered checklist, help-now block near top and bottom; FAQ JSON-LD matches the visible FAQ (checked above)
sc=pages['scam-help.html']
assert '<h2 id="scam-steps-heading">Think you’ve been scammed or hacked? Take a breath. Here’s what to do.</h2>' in sc
ol=re.search(r'<ol class="calm-steps">(.*?)</ol>',sc,re.S).group(1);assert ol.count('<li>')==8
hn=[m.start() for m in re.finditer(r'<div class="help-now[ "]',sc)];assert len(hn)==1 and hn[0]>sc.index('id="faq"'),hn
assert sc.count('Need help right now? Call or text Josh at <a href="tel:+15632610200">563-261-0200</a>.')==1
# r3: standalone free guide
assert re.search(r'</ol><div class="reach-out"><div class="reach-out__copy"><h3>Still worried, or need a hand with this\? Reach out to me\.</h3>.*?href="sms:\+15632610200".*?href="tel:\+15632610200"',sc,re.S),'CTA right under the checklist'
for gid in ['what-to-do','spot-scams','hacked-signs','lock-down','family','report','faq']:assert f'id="{gid}"' in sc and f'href="#{gid}"' in sc,gid
for topic in ['Fake “virus” pop-ups','Tech-support calls','Bank, Amazon and delivery texts','Gift cards and odd payments','Grandparent and family emergencies','Romance and too-good-to-be-true','Password manager basics','2-step verification','Recovery info']:assert f'<h3>{topic}</h3>' in sc,topic
ext=set(re.findall(r'href="(https?://[^"]+)"',sc[sc.index('<main'):sc.index('</main>')]))
assert ext=={'https://reportfraud.ftc.gov/','https://www.identitytheft.gov/','https://www.ic3.gov/'},ext
assert not re.search(r'(?i)\b(kits?|download\w*|gumroad)\b',sc),'no kit/download mentions on the scam page'
assert 'If there’s a way back in, we’ll find it together.' in sc
assert '<div class="scam-hero-art" aria-hidden="true"><svg class="scam-shield"' in sc and '<img' not in re.search(r'<section class="[^"]*ds-hero.*?</section>',sc,re.S).group()
assert '.scam-shield *{animation:none!important;stroke-dashoffset:0!important}' in dcss
for bad in ['guarantee','recover your money','get your money back','money back','100%']:assert bad not in sc.lower().replace('doesn’t always get money back',''),bad
# timelines: twisted rope above the headings (JS-built, decorative), drawn in on view
assert "rope.className='ds-rope'" in djs and "setAttribute('aria-hidden','true')" in djs and "url(/assets/design/rope-h.svg)" in dcss and "url(/assets/design/rope-v.svg)" in dcss
assert (ROOT/'assets/design/rope-h.svg').is_file() and (ROOT/'assets/design/rope-v.svg').is_file()
assert '.ds-anim .ds-steps.is-drawn .ds-rope{clip-path:inset(0 0 0 0' in dcss and 'url(/assets/design/rope-v.svg)' in (ROOT/'assets/website-package.css').read_text()
# shared gold icon set: contact methods + rate cards get icons
icons=json.loads((ROOT/'data/icons.json').read_text());assert {'devices','phone','map-star','globe','cloud-check','pencil'}<=set(icons)
assert pages['contact.html'].count('<div class="contact-option has-icon"><div class="icon" aria-hidden="true">')==4
assert pages['rates.html'].count('<div class="icon')==2
# subtle dot-matrix accents are CSS backgrounds only (nothing announced)
assert dcss.count('var(--ds-dots')>=6
if '--production' in sys.argv:
 assert json.loads((ROOT/'data/site-config.json').read_text())['form_mode']=='cloudflare'
 contact=(ROOT/'contact.html').read_text();script=(ROOT/'assets/site.js').read_text()
 assert 'action="/api/lead" method="post"' in contact and 'mailto:joshthetechtamer@gmail.com" method' not in contact
 assert 'challenges.cloudflare.com/turnstile/v0/api.js' in contact and 'id="request-turnstile"' in contact
 assert 'Send request' in contact and "action:'lead'" in script and 'encodeURIComponent(body)' not in script
 assert (ROOT/'functions/api/lead.js').is_file()

print('PASS: HTML nesting, internal links/anchors, headings, images, structured data, all six kit links, review ratings and deployment exclusions.')
