"""Build static pages from preserved design templates and shared data. No network writes."""
from pathlib import Path
from html import escape,unescape
from urllib.parse import quote
import re,json
ROOT=Path(__file__).resolve().parents[1];BASE='https://joshthetechtamer.com'
manifest=json.loads((ROOT/'data/image-manifest.json').read_text());reviews=json.loads((ROOT/'data/reviews.json').read_text());config=json.loads((ROOT/'data/site-config.json').read_text())
meta={
'index.html':('Computer & Tech Help in Muscatine, IA | The Tech Tamer','House-call computer repair and tech help in Muscatine, IA. Wi-Fi, printers, phones, scams. Evenings & weekends. $50/hr. Call or text 563-261-0200.','home'),
'services.html':('Computer Repair & Tech Support in Muscatine, IA | Tech Tamer','In-home computer repair, Wi-Fi, printer, phone and TV help in Muscatine, Wilton, West Liberty & the Quad Cities. I come to you. Text 563-261-0200.','services'),
'business.html':('Small-Business Tech, Branding & Ads in Muscatine | Tech Tamer','Logo and brand work, advertising setup, websites and practical startup help for Eastern Iowa businesses. Free consultation; estimates for larger projects.','business'),
'digital-kits.html':('DIY Tech Guides: Wi-Fi, Computers & Scam Safety | The Tech Tamer','Practical downloadable guides for home networks, new computers, scam safety and small-business technology. Explore six kits and learn at your own pace.','kits'),
'rates.html':('Tech Help Rates in Muscatine: $50/hr, Free Consult | Tech Tamer','Simple pricing for in-home tech help in Muscatine and Eastern Iowa: $50/hour, free consultation, estimates for bigger projects.','rates'),
'about.html':('Josh Sargent: Your Local Muscatine Tech Guy | The Tech Tamer','Meet Josh Sargent, your local Tech Tamer in Muscatine, IA. Patient, personal home and office tech help, with electronics and network engineering training.','about'),
'contact.html':('Book Tech Help in Muscatine, IA | Call/Text 563-261-0200','Request an in-home tech help visit in Muscatine & nearby towns. Text or call 563-261-0200, evenings and weekends available.','contact'),
'website-package.html':('Small-Business Websites in Muscatine, IA: $800 | Tech Tamer','A simple, phone-friendly website for your Muscatine or Quad Cities business: free preview first, then $800 to build and launch. Optional $25/month Care Plan.','website'),
# Local SEO pages (Oct 2026 audit, section B4).
'tech-help-muscatine.html':('Tech Help in Muscatine, IA: I Come to You | The Tech Tamer','Computer, printer, Wi-Fi and phone help at your home in Muscatine, IA. Evenings & weekends, $50/hr, free consultation. Call or text 563-261-0200.','muscatine'),
'service-area.html':('Service Area: Tech Help Near Muscatine, IA | The Tech Tamer','House-call tech help about 30 miles around Muscatine: Fruitland, Wilton, West Liberty, Durant, Columbus Junction, Letts, Nichols & the Quad Cities.','areas'),
'scam-help.html':('Scam & Hacked Account Help in Muscatine | The Tech Tamer','Pop-up scams, hacked email and Facebook, locked-out accounts and 2-step verification. Calm in-home help in Muscatine, IA. Call or text 563-261-0200.','scam'),
'tech-help-quad-cities.html':('In-Home Tech Help in Davenport & the Quad Cities | Tech Tamer','In-home computer, printer, Wi-Fi and scam help in Davenport, Bettendorf, Moline, Rock Island, East Moline & nearby. $50/hr. Text 563-261-0200.','qc')}
# Pages without their own share image or a one-word breadcrumb name.
share_key={'website':'business','muscatine':'about','areas':'home','scam':'about','qc':'about'}  # new pages: Josh-only share photo
crumb={'website':'Website Package','muscatine':'Tech Help in Muscatine','areas':'Areas I Serve','scam':'Scam & Hacked Account Help','qc':'Quad Cities','kits':'Digital Kits','services':'Tech Help'}
# Final, extensionless public URL for each page (Cloudflare Pages serves /about from about.html and 308s about.html -> /about).
def url(name):return BASE+'/'+('' if name=='index.html' else name[:-5])
parent={'tech-help-quad-cities.html':'service-area.html'}
# Example sites appear only once the client has OK'd it (flags in data/site-config.json, off by default).
examples={'mvp563':('show_mvp563_example','<article class="wp-example"><div class="wp-example-body"><h3>MVP 563</h3><p>A local business site built and hosted the same way.</p><a class="btn wp-btn-blue" href="https://mvp563.com/">Visit mvp563.com<span aria-hidden="true">↗</span></a></div></article>')}
# The header uses the readable full lockup; the favicon stays the mascot crop.
def apply_header_logo(s):
 if 'class="brand brand-lockup header-animation"' in s:return s
 m=re.search(r'<header\b.*?<a href="[^"]+" class="brand(?: brand-lockup)?" aria-label="The Tech Tamer home">.*?</a>',s,re.S)
 if not m:return s
 header=m.group()
 header=re.sub(r'<a href=("[^"]+") class="brand(?: brand-lockup)?" aria-label="The Tech Tamer home">.*?</a>',r'<a href=\1 class="brand brand-lockup" aria-label="The Tech Tamer home"><img src="assets/hero-logo.png" alt="The Tech Tamer full logo" width="128" height="110"></a>',header,count=1,flags=re.S)
 return s[:m.start()]+header+s[m.end():]
def carousel():
 cards=[]
 for i,r in enumerate(reviews):
  badge='<span class="review-stars" aria-label="5 out of 5 stars">★★★★★</span>' if r['rating']==5 else '<span class="review-kind">'+escape(r['source'])+'</span>'
  cards.append(f'<article class="review-card" role="group" aria-roledescription="slide" aria-label="{i+1} of {len(reviews)}">{badge}<blockquote><p>“{escape(r["quote"])}”</p></blockquote><p class="review-credit"><strong>{escape(r["name"])}</strong><span>{escape(r["source"])}</span></p></article>')
 return '<section class="section reviews-section" aria-labelledby="reviews-heading"><div class="wrap"><div class="section-head"><div><div class="eyebrow">A little reassurance</div><h2 id="reviews-heading">Good help. In their words.</h2></div><p>Feedback shared by customers on Google and Facebook.</p></div><div class="review-carousel" role="region" aria-roledescription="carousel" aria-label="Customer feedback"><div class="review-track">'+''.join(cards)+'</div><div class="review-controls" hidden><button type="button" class="btn secondary" data-review="prev" aria-label="Previous review">← Previous</button><span class="review-count" aria-live="polite" aria-atomic="true">1 / '+str(len(reviews))+'</span><button type="button" class="btn secondary" data-review="next" aria-label="Next review">Next →</button><button type="button" class="review-pause" data-review="pause">Pause rotation</button></div></div><p class="small review-note">Names are shortened for privacy. Stars appear only where a five-star Google rating was provided. Facebook feedback is shown as originally shared.</p></div></section>'
def image_tag(m):
 tag=m.group();src=re.search(r'src="([^"]+)"',tag).group(1)
 if src not in manifest:return tag
 if src=='assets/logo.png' and 'width="58"' in tag:return tag.replace(src,'/assets/logo.png')
 variants=manifest[src];large=variants[-1];tag=tag.replace('src="'+src+'"','src="/'+large['src']+'"')
 tag=re.sub(r'\s(?:width|height)="[^"]*"','',tag)
 attrs=f' width="{large["width"]}" height="{large["height"]}" decoding="async"'
 if len(variants)>1:attrs+=' srcset="'+', '.join('/'+v['src']+' '+str(v['width'])+'w' for v in variants)+'" sizes="(max-width: 620px) calc(100vw - 44px), 580px"'
 return tag[:-1]+attrs+'>'
form='''<form id="request-form" action="/api/lead" method="post"><div class="form-row"><div><label for="name">Your name *</label><input id="name" name="name" required autocomplete="name" maxlength="100"></div><div><label for="reply">Reply by *</label><select id="reply" name="reply"><option value="text">Text message</option><option value="phone">Phone call</option><option value="email">Email</option></select></div></div><label for="contact">Phone number *</label><input id="contact" name="contact" type="tel" required maxlength="150" autocomplete="tel"><label for="service">What can I help with?</label><select id="service" name="service"><option>Tech help at home</option><option>Computers & printers</option><option>Phones & tablets</option><option>Wi-Fi & home networks</option><option>TVs & streaming</option><option>Smart home & home cameras</option><option>Accounts & scam help</option><option>Logo & brand work</option><option>Advertising setup</option><option>Startup consulting</option><option>Website & business tech</option><option>Something else</option></select><label for="location">City or service location</label><input id="location" name="location" autocomplete="address-level2" maxlength="150" placeholder="For example, Muscatine"><label for="time">Good times to reach you</label><input id="time" name="preferred_time" maxlength="150" placeholder="For example, weekday afternoons"><label for="issue">A little about your request *</label><textarea id="issue" name="issue" required maxlength="4000" placeholder="What’s happening, or what would you like help creating?"></textarea><div class="form-trap" aria-hidden="true"><label for="website">Leave this field empty</label><input id="website" name="_gotcha" tabindex="-1" autocomplete="off"></div><p class="small">Your details are used to respond to this request. Please leave out passwords, payment details, and other sensitive information.</p><div id="request-turnstile" class="cf-turnstile-box" data-sitekey="0x4AAAAAAFR89kkQkacO3Tdf" style="margin:0 0 18px;min-height:65px"></div><button class="btn" type="submit">Send request</button><p class="status" id="form-status" role="status" aria-live="polite">Your request goes straight to Josh, and he’ll get back to you the way you picked. A visit is confirmed after you agree on a time.</p><noscript><p>Please call, text, or email Josh using the links on this page.</p></noscript></form>'''
visit='''<section class="section tint" id="your-visit"><div class="wrap"><div class="section-head"><div><div class="eyebrow">Help where you need it</div><h2>What happens during a visit?</h2></div><p>At your home or office, with a plan you can understand.</p></div><div class="grid3"><article class="step"><div class="number">01</div><h3>Show me what’s happening.</h3><p>We’ll look at the device and its setup together. You don’t need to know the technical name for the problem.</p></article><article class="step"><div class="number">02</div><h3>Talk through the next step.</h3><p>We’ll discuss the work and any equipment or software needed. Hands-on help is $50/hour; larger projects start with an estimate.</p></article><article class="step"><div class="number">03</div><h3>Try it together.</h3><p>We’ll check the result and walk through how to use it. There’s room for questions along the way.</p></article></div><a class="textlink" href="/contact.html?service=Tech%20help%20at%20home">Request a visit</a></div></section>'''

# ---- Local SEO (Oct 2026 audit) ----
gbp=config.get('google_business_profile_url','').strip();review_url=config.get('google_review_url','').strip()
local_faqs=json.loads((ROOT/'data/local-faqs.json').read_text())
lastmod=json.loads((ROOT/'data/sitemap-lastmod.json').read_text())
AREAS=['Muscatine, IA','Fruitland, IA','Wilton, IA','West Liberty, IA','Durant, IA','Columbus Junction, IA','Letts, IA','Nichols, IA','Atalissa, IA','Buffalo, IA','Blue Grass, IA','Davenport, IA','Bettendorf, IA','Moline, IL','Rock Island, IL','East Moline, IL','Silvis, IL','Milan, IL','Illinois City, IL']  # Josh's order: small towns first
QC=['Davenport, IA','Bettendorf, IA','Moline, IL','Rock Island, IL','East Moline, IL','Silvis, IL','Milan, IL']
local_service={'tech-help-muscatine.html':('Computer repair and tech help',['Muscatine, IA','Fruitland, IA']),
 'service-area.html':('In-home computer and tech help',AREAS),
 'scam-help.html':('Scam and hacked account recovery',['Muscatine, IA']+AREAS[1:]),
 'tech-help-quad-cities.html':('In-home computer and tech help',QC)}
def business():
 """The audit's checked LocalBusiness block (B5). Service-area business: no street address, no ratings."""
 b={'@type':['ProfessionalService','LocalBusiness'],'@id':BASE+'/#business','name':'The Tech Tamer','legalName':'The Tech Tamer LLC','url':BASE+'/','telephone':'+1-563-261-0200','email':'joshthetechtamer@gmail.com','image':BASE+'/assets/optimized/share-home.jpg','logo':BASE+'/assets/logo.png',
  'description':'House-call computer repair and tech help in Muscatine, Iowa and nearby towns: computers, printers, Wi-Fi, phones, TVs, scam and hacked-account help, and small-business websites.',
  'priceRange':'$50/hour','founder':{'@type':'Person','name':'Josh Sargent'},
  'address':{'@type':'PostalAddress','addressLocality':'Muscatine','addressRegion':'IA','postalCode':'52761','addressCountry':'US'},
  'areaServed':[{'@type':'City','name':a} for a in AREAS]+[{'@type':'AdministrativeArea','name':'Muscatine County, IA'}],
  'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Sunday','Monday','Tuesday','Thursday','Friday','Saturday'],'opens':'08:00','closes':'20:00'}],
  'knowsAbout':['Computer repair','Printer setup','Wi-Fi and home networks','Smartphone and tablet help','Scam and hacked account recovery','Small-business websites'],
  'hasOfferCatalog':{'@type':'OfferCatalog','name':'Tech help services','itemListElement':[{'@type':'Offer','itemOffered':{'@type':'Service','name':n}} for n in ['In-home computer repair & tune-up','Printer setup & troubleshooting','Wi-Fi & home network setup','Phone, tablet & TV/streaming help','Scam & hacked account recovery']]+[{'@type':'Offer','itemOffered':{'@type':'Service','name':'Small-business website package','url':BASE+'/website-package'},'price':'800','priceCurrency':'USD'}]},
  'sameAs':['https://www.facebook.com/profile.php?id=61575951953109','https://www.linkedin.com/in/josh-sargent-adsales']}
 if gbp:b['sameAs'].append(gbp);b['hasMap']=gbp
 return b
def google_links(cls=''):
 """'Read our Google reviews' / 'Leave a review' buttons. Empty config values render nothing (no broken links)."""
 out=[]
 if gbp:out.append(f'<a class="btn secondary" href="{escape(gbp)}" target="_blank" rel="noopener noreferrer">Read our Google reviews<span aria-hidden="true">↗</span></a>')
 if review_url:out.append(f'<a class="btn" href="{escape(review_url)}" target="_blank" rel="noopener noreferrer">Leave a Google review<span aria-hidden="true">↗</span></a>')
 return f'<div class="actions review-links{cls}">'+''.join(out)+'</div>' if out else ''
def local_reviews():
 picks=[next(r for r in reviews if r['name']==n) for n in ('Peggy S.','Bob','Arlene S.')]  # first card per name
 cards=''.join(f'<article class="review-card">'+('<span class="review-stars" aria-label="5 out of 5 stars">★★★★★</span>' if r['rating']==5 else '<span class="review-kind">'+escape(r['source'])+'</span>')+f'<blockquote><p>“{escape(r["quote"])}”</p></blockquote><p class="review-credit"><strong>{escape(r["name"])}</strong><span>{escape(r["source"])}</span></p></article>' for r in picks)
 return '<section class="section reviews-section" aria-labelledby="local-reviews-heading"><div class="wrap"><div class="section-head"><div><div class="eyebrow">A little reassurance</div><h2 id="local-reviews-heading">What folks are saying.</h2></div><p>Feedback shared by customers on Google and Facebook.</p></div><div class="grid3 local-review-grid">'+cards+'</div>'+google_links()+'<p class="small review-note">Names are shortened for privacy. Stars appear only where a five-star Google rating was provided.</p></div></section>'
SIGNOFF='<p>Muscatine · Iowa City · Quad Cities</p>'  # Josh's sign-off: left exactly as on main (question pending with Josh)
FOOTER_AREAS=SIGNOFF+'<p>Muscatine · Fruitland · Wilton · West Liberty · Durant · Quad Cities (IA &amp; IL)<br><a class="footer-areas" href="service-area.html">Areas I serve</a></p>'
def footer(s):
 s=s.replace(SIGNOFF,FOOTER_AREAS,1)
 s=s.replace('<a href="about.html">Meet Josh</a></div>','<a href="about.html">Meet Josh</a><a href="tech-help-muscatine.html">Tech help in Muscatine</a><a href="scam-help.html">Scam &amp; hacked accounts</a><a href="service-area.html">Areas I serve</a></div>',1)
 g=(f'<a href="{escape(gbp)}" target="_blank" rel="noopener noreferrer">Find us on Google ↗</a>' if gbp else '')+(f'<a href="{escape(review_url)}" target="_blank" rel="noopener noreferrer">Leave a Google review ↗</a>' if review_url else '')
 s=s.replace('LinkedIn ↗</a></div>','LinkedIn ↗</a>'+g+'</div>',1)
 assert FOOTER_AREAS in s and 'tech-help-muscatine.html">Tech help in Muscatine' in s,'footer markup changed'
 return s
HERO_PICTURE='<picture style="display:contents"><source type="image/webp" srcset="/assets/optimized/hero-logo-400.webp 400w, /assets/optimized/hero-logo-800.webp 800w, /assets/optimized/hero-logo-1200.webp 1200w" sizes="(max-width: 620px) 290px, (max-width: 1100px) 380px, 490px"><img src="/assets/optimized/hero-logo-800.png" alt="The Tech Tamer: Josh’s top-hatted technology tamer mascot and wordmark" width="800" height="687" fetchpriority="high" decoding="async"></picture>'
def normalize_urls(s,name):
 """Canonical, og:url and every internal link use the final extensionless URL (no redirect hops)."""
 s=s.replace('"areaServed": ["Muscatine", "Iowa City", "Quad Cities"]','"areaServed": '+json.dumps([a.split(",")[0] for a in AREAS]+["Muscatine County"]))  # 404 keeps its own small JSON-LD
 s=re.sub(r'<link rel="canonical" href="[^"]*">','' if name=='404.html' else '<link rel="canonical" href="'+url(name)+'">',s)
 s=re.sub(r'<meta property="og:url" content="[^"]*">','' if name=='404.html' else '<meta property="og:url" content="'+url(name)+'">',s)
 def fix(m):
  attr,host,page,rest=m.group(1),m.group(2) or '',m.group(3),m.group(4) or ''
  path='/' if page=='index' else '/'+page
  return f'{attr}="{host}{path}{rest}"'
 return re.sub(r'(href)="(https://joshthetechtamer\.com)?/?([a-z0-9-]+)\.html([?#][^"]*)?"',fix,s)

# ---- Sitewide redesign (Oct 2026): the Website Package showcase's design language on every other page ----
# Shared layer: assets/design.css + assets/design.js. Markup changes are decorative only (aria-hidden), so every
# page's words, links, images, forms, header, footer, JSON-LD and metadata stay exactly as they were
# (scripts/content_lock.py + data/content-lock.json, checked by validate_site.py).
DESIGN_V='20261011-sitewide'
GOLD_WORD={'index.html':'savvy','services.html':'Working','business.html':'work','digital-kits.html':'confidence','rates.html':'pricing',
 'about.html':'local','contact.html':'tame','tech-help-muscatine.html':'Muscatine','service-area.html':'Muscatine','scam-help.html':'Help',
 'tech-help-quad-cities.html':'In-Home','404.html':'wandered'}
DS_SWOOSH='<svg class="ds-swoosh" viewBox="0 0 200 18" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path pathLength="1" d="M3 12.5C40 6.5 92 4.2 140 5.6c20 .6 38 2 55 4.4" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/><path pathLength="1" d="M18 15.5c38-4.6 86-6 150-3.4" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".55"/></svg>'
DS_DECO='<span class="ds-deco" aria-hidden="true"><span class="ds-dots ds-dots--tr"></span><span class="ds-dots ds-dots--bl"></span><span class="ds-stripe"></span></span>'
def redesign(s,name):
 if name=='website-package.html':return s  # the showcase keeps its own page CSS/JS
 s=s.replace('</head>','<link rel="stylesheet" href="/assets/design.css?v='+DESIGN_V+'"><script src="/assets/design.js?v='+DESIGN_V+'" defer></script></head>',1)
 if 'family=Montserrat' not in s.split('</head>')[0]:  # hero headlines use the showcase's Montserrat Black
  s=s.replace('</head>','<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&display=swap" rel="stylesheet"></head>',1)
 # 1) Dark navy hero band with dot grids and the diagonal blue stripe.
 n=0
 def hero(m):
  nonlocal n;n+=1
  cls=m.group(1)
  return '<section class="'+cls+' ds-hero">'+DS_DECO
 s=re.sub(r'<section class="((?:hero|page-hero[^"]*|notfound))">',hero,s,count=1)
 assert n==1,('hero band',name)
 # 2) Gold text-art accent (gold + hand-drawn swoosh) on one key word of the headline; the text itself is unchanged.
 h=re.search(r'<h1\b[^>]*>(.*?)</h1>',s,re.S);inner=h.group(1);word=GOLD_WORD[name]
 parts=re.split(r'(<span class="eyebrow[^"]*">.*?</span>|<[^>]+>)',inner)
 for i,part in enumerate(parts):
  if part.startswith('<'):continue
  m=re.search(r'(?<![\w-])'+re.escape(word)+r'(?![\w-])',part)
  if m:parts[i]=part[:m.start()]+'<span class="ds-gold">'+word+DS_SWOOSH+'</span>'+part[m.end():];break
 else:raise AssertionError(('gold word not in h1',name,word))
 s=s[:h.start(1)]+''.join(parts)+s[h.end(1):]
 # 3) Card icons draw themselves in (gold stroke): pathLength="1" lets CSS animate any shape the same way.
 def icon(m):return re.sub(r'<(path|rect|circle|line|polyline|polygon|ellipse)\b(?![^>]*pathLength)',r'<\1 pathLength="1"',m.group())
 s=re.sub(r'<div class="icon" aria-hidden="true"><svg\b.*?</svg>',icon,s,flags=re.S)
 # 4) Three-step rows become a gold-filling timeline.
 s=re.sub(r'<div class="grid3">(?=<(?:article|div) class="step">)','<div class="grid3 ds-steps" data-ds-steps>',s)
 return s
for file in (ROOT/'templates').glob('*.html'):
 s=apply_header_logo(file.read_text());name=file.name
 s=footer(s)
 # Header canvas fallback: small optimized logo instead of the 1.48 MB original.
 s=s.replace('<img src="/assets/hero-logo.png" alt="The Tech Tamer" width="128" height="110">','<img src="/assets/optimized/hero-logo-256.png" alt="The Tech Tamer" width="128" height="110">')
 s=re.sub(r'assets/site\.css\?v=[^"]+','assets/site.css?v=20261011-localseo',s)
 if name=='index.html':
  # H1 keyword line (audit B2): visible headline unchanged, eyebrow promoted into the H1.
  s=s.replace('<img src="assets/hero-logo.png" alt="The Tech Tamer: Josh’s top-hatted technology tamer mascot and wordmark" width="1353" height="1162">',HERO_PICTURE,1)
  # Hero stays exactly as on main (Josh's call); the local keyword line sits in the "Getting help should be easy" section instead.
  a='<div class="eyebrow">No jargon. No runaround.</div><h2>Getting help should be easy.</h2></div>'
  assert a in s;s=s.replace(a,a+'<p class="home-local"><strong>In-home computer &amp; tech help in Muscatine, IA.</strong> House calls all over <a href="tech-help-muscatine.html">Muscatine</a> and <a href="service-area.html">nearby towns</a>, evenings &amp; weekends.</p>',1)
  s=s.replace('<a class="textlink" href="services.html">Find your tech fix</a>','<a class="textlink" href="tech-help-muscatine.html">Tech help in Muscatine</a>',1)
 if name=='services.html':
  # Security cameras/systems: residential (in-home) only. Never commercial or business security.
  for a,b in [('<h2>Smart devices & cameras</h2><p>Bring your connected devices together with less guesswork.</p><ul class="checklist"><li>Smart-home device setup</li><li>Compatible camera app setup</li><li>Notifications and remote viewing</li><li>Device selection and planning</li></ul>','<h2>Smart home & home cameras</h2><p>Bring your home’s connected devices together with less guesswork.</p><ul class="checklist"><li>Smart-home device setup</li><li>In-home security camera app setup</li><li>Notifications and remote viewing for your home cameras</li><li>Device selection and planning</li></ul><p class="small residential-note">Residential only: security cameras and systems for your home. I don’t do commercial or business security work.</p>'),
   ('Camera and smart-device projects start with a conversation about the equipment and setup needed.','Home camera and smart-device projects start with a conversation about the equipment and setup needed. Security cameras and systems are residential (in-home) only. I don’t do commercial or business security work.')]:
   assert a in s,a[:60];s=s.replace(a,b)
  s=s.replace('<div class="eyebrow">Tech help</div><h1>Your technology.<br>Working for you.</h1>','<h1><span class="eyebrow eyebrow-h1">Computer repair &amp; tech support at your home in Muscatine</span>Your technology.<br>Working for you.</h1>',1)
  s=s.replace('<a class="textlink" href="contact.html">Ask Josh about this</a></article></div><div class="notice">','<a class="textlink" href="contact.html">Ask Josh about this</a><a class="textlink" href="scam-help.html">Scam &amp; hacked-account help</a></article></div><div class="notice">',1)
  s=s.replace('Serving Muscatine, Iowa City & the Quad Cities','Serving Muscatine, Wilton, West Liberty, Durant & the Quad Cities',1)
 if name=='contact.html':
  s=s.replace('<p>Based in Muscatine, Iowa.<br>Serving Iowa City and the Quad Cities.</p>','<p>Based in Muscatine, Iowa. House calls about 30 miles around Muscatine: Fruitland, Wilton, West Liberty, Durant, Columbus Junction, Letts, Nichols, Atalissa, Buffalo and Blue Grass, plus the whole Quad Cities (Davenport, Bettendorf, Moline, Rock Island, East Moline, Silvis and Milan), where I’m a couple times a week, Illinois City and the rest of Muscatine County. Trips farther out may have a small added gas charge.<br><a class="textlink" href="service-area.html">Areas I serve</a></p>',1)
 if name=='rates.html':
  s=s.replace('Josh is based in Muscatine and serves the Iowa City and Quad Cities areas.','Josh is based in Muscatine and makes house calls about 30 miles around town: Fruitland, Wilton, West Liberty, Durant, Columbus Junction and the other small towns nearby, plus the whole Quad Cities on both sides of the river (he’s there a couple times a week). Trips farther out may have a small added gas charge on your invoice. See <a href="service-area.html">areas I serve</a>.',1)
 if name=='about.html':
  s=s.replace('Based in Muscatine · Serving Iowa City and the Quad Cities','Based in Muscatine · Serving nearby towns and the Quad Cities',1)
 if name=='service-area.html':
  s=s.replace('<!--GBP_BUTTON-->',f'<a class="btn secondary" href="{escape(gbp)}" target="_blank" rel="noopener noreferrer">See me on Google Maps<span aria-hidden="true">↗</span></a>' if gbp else '')
  # Branded service-area map drawn from real lat/long by scripts/make_service_map.py (no street address).
  s=s.replace('<!--SERVICE_MAP-->',(ROOT/'data/service-area-map.svg').read_text())
 if name=='tech-help-muscatine.html':s=s.replace('<!--LOCAL_REVIEWS-->',local_reviews())
 assert '<!--' not in s.split('</head>')[1].replace('<!--EXAMPLE:','') or name=='website-package.html',('unfilled slot',name)
 if name=='index.html':
  s=s.replace('From the Wi-Fi that won’t cooperate to the business you’re ready to launch. I’m Josh, and I’ll help you get it working.','Wi-Fi, printers, computers, and everyday tech—without the runaround. I’m Josh, and I come to your home or office in Muscatine and Eastern Iowa to help get it working.')
  s=s.replace('<section class="cta cta-photo">',carousel().replace('<p class="small review-note">',google_links()+'<p class="small review-note">',1)+'<section class="cta cta-photo">',1)
 if name=='services.html':
  s=s.replace('Patient, practical help for your home and everyday technology.','Patient, practical help at your home or office in Muscatine and Eastern Iowa.')
  s=s.replace('<section class="cta cta-photo">',visit+'<section class="cta cta-photo">',1)
  def context(m):
   card=m.group();h=re.search(r'<h2>(.*?)</h2>',card).group(1)
   return card.replace('href="contact.html"','href="/contact.html?service='+quote(h)+'"')
  s=re.sub(r'<article class="service-card".*?</article>',context,s)
 if name=='business.html':
  s=s.replace('href="contact.html"','href="/contact.html?service=Startup%20consulting"')
  s=s.replace('<li>Computer, printer, and network support</li></ul></article>','<li>Computer, printer, and network support</li></ul><a class="textlink" href="website-package.html">See the Website Package</a></article>',1)
  # Security cameras/alarm systems: residential (in-home) only. No commercial or business security work (not licensed for it in Iowa).
  for a,b in [('<li>Business email and connected devices</li>','<li>Business email and everyday devices</li>'),
   ('<li>Computer, printer, and network support</li></ul><a class="textlink" href="website-package.html">','<li>Computer, printer, and network support</li></ul><p class="small residential-note">Security cameras and alarm systems are residential (in-home) only. I don’t install or service commercial or business security systems.</p><a class="textlink" href="website-package.html">')]:
   assert a in s,a;s=s.replace(a,b,1)
 if name=='website-package.html':
  # Hero wording lives in data/website-package-copy.json so it is easy to edit.
  copy=json.loads((ROOT/'data/website-package-copy.json').read_text())
  # Headline accents: one gold word with a hand-drawn swoosh (line 1) and one italic word (line 2); still real text.
  def accent(text,word,wrap):
   t=escape(text,quote=False)
   if not word:return t
   m=re.search(r'\b'+re.escape(escape(word,quote=False))+r'\b',t);assert m,('accent word not in headline',word)
   return t[:m.start()]+wrap(m.group())+t[m.end():]
  swoosh='<svg class="wp-swoosh" viewBox="0 0 200 18" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M3 12.5C40 6.5 92 4.2 140 5.6c20 .6 38 2 55 4.4" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/><path d="M18 15.5c38-4.6 86-6 150-3.4" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".55"/></svg>'
  s=s.replace('{{hero_line1}}',accent(copy['hero_line1'],copy.get('hero_gold_word'),lambda w:'<span class="wp-gold">'+w+swoosh+'</span>'))
  s=s.replace('{{hero_line2}}',accent(copy['hero_line2'],copy.get('hero_italic_word'),lambda w:'<em class="wp-italic">'+w+'</em>'))
  for k,v in copy.items():s=s.replace('{{'+k+'}}',escape(v,quote=False))
  assert '{{' not in s,'missing website-package copy key'
  for slot,(flag,card) in examples.items():s=s.replace('<!--EXAMPLE:'+slot+'-->',card if config.get(flag) else '')
 if name=='contact.html':
  s=s.replace('I’ll tame promptly on your schedule','Let’s find a time to tame your tech.')
  s=s.replace('This prepares a message in your email app. Review it and press Send there to get in touch.','Tell me what you need and how you’d like me to get back to you. We’ll arrange the next step together.')
  s=re.sub(r'<form id="request-form".*?</form>',form,s)
  s=s.replace('<script src="assets/site.js?v=20261009-leadsuccess" defer></script>','<script src="assets/site.js?v=20261009-leadsuccess" defer></script><script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=onTechTamerTurnstile" async defer></script>',1)
 if name=='rates.html':
  s=s.replace('or prepare an email request on the Contact page','or send an inquiry on the Contact page')
  extra='<details><summary>What should I have ready for a visit?</summary><p>Keep the device and its usual cables available. If signing in is needed, you can enter your password yourself. Share your location and a brief description when arranging the visit.</p></details><details><summary>How are travel and payment details handled?</summary><p>Share your location when you request help. Ask Josh to confirm any travel charges, minimum billing, and payment arrangements before your visit.</p></details>'
  s=s.replace('<details><summary>Do you offer a monthly subscription?',extra+'<details><summary>Do you offer a monthly subscription?')
  # Website Package: "no subscription" is tech help only; state the on-site minimum; point to the package.
  s=s.replace('<p>Personal help with your technology or business project. No subscription required.</p><ul class="checklist"><li>Free initial consultation</li>','<p>Personal help with your technology or business project. Tech help never needs a subscription.</p><ul class="checklist"><li>Free initial consultation</li><li>On-site visits have a one-hour minimum ($50)</li>')
  s=s.replace('Ask Josh to confirm any travel charges, minimum billing, and payment arrangements before your visit.','On-site visits have a one-hour minimum at $50/hour. Ask Josh to confirm any travel charges and payment arrangements before your visit.')
  s=s.replace('<summary>Do you offer a monthly subscription?</summary><p>No subscription is needed. Book the help you need at $50/hour, or ask for an estimate for a larger project.</p>','<summary>Do you offer a monthly subscription?</summary><p>Not for tech help. Book the help you need at $50/hour, or ask for an estimate for a larger project. The only monthly plan is the optional $25/month Care Plan for websites I build. See the <a href="/website-package.html#care-plan">Website Package</a>.</p>')
  s=s.replace('</article></div></div></section><section class="section tint">','</article></div><div class="notice"><strong>Need a website for your business?</strong> Tech help is billed by the hour with no subscription. Websites are a separate package: a free preview first, then $800 to build and launch, with an optional $25/month Care Plan.<br><a class="textlink" href="website-package.html" style="margin-top:14px">See the Website Package</a></div></div></section><section class="section tint">',1)
 if name in meta:
  title,desc,key=meta[name];s=re.sub(r'<title>.*?</title>','<title>'+escape(title)+'</title>',s)
  for prop,value in [('name="description"',desc),('property="og:title"',title),('property="og:description"',desc),('property="og:image"',BASE+'/assets/optimized/share-'+share_key.get(key,key)+'.jpg')]:
   s=re.sub(r'<meta '+prop+r' content="[^"]*">','<meta '+prop+' content="'+escape(value,quote=True)+'">',s)
  s=s.replace('</head>','<meta name="twitter:card" content="summary_large_image"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"></head>')
  graph=[business()]
  trail=[('Home',BASE+'/')]+([(crumb[meta[parent[name]][2]],url(parent[name]))] if name in parent else [])+[(crumb.get(key,key.title()),url(name))]
  if name!='index.html':graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':u} for i,(n,u) in enumerate(trail)]})
  if name in local_service:
   stype,areas=local_service[name]
   graph.append({'@type':'Service','@id':url(name)+'#service','name':stype,'serviceType':stype,'url':url(name),'provider':{'@id':BASE+'/#business'},'areaServed':[{'@type':'City','name':a} for a in areas]})
  if name in local_faqs:
   graph.append({'@type':'FAQPage','@id':url(name)+'#faq','mainEntity':[{'@type':'Question','name':unescape(re.sub(r'<[^>]+>','',f['q'])),'acceptedAnswer':{'@type':'Answer','text':unescape(re.sub(r'<[^>]+>','',f['a']))}} for f in local_faqs[name]]})
  s=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False)+'</script>',s)
 else:s=s.replace('</head>','<meta name="robots" content="noindex,follow"></head>')
 s=re.sub(r'<img\b[^>]*>',image_tag,s)
 # Favicons: transparent mascot icons (no white fills), navy apple-touch icon, web manifest.
 s=re.sub(r'(?:<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>\s*)+','<link rel="icon" href="/favicon.ico?v=20261010" sizes="any"><link rel="icon" href="/assets/favicon-32.png?v=20261010" type="image/png" sizes="32x32"><link rel="icon" href="/assets/favicon-16.png?v=20261010" type="image/png" sizes="16x16"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png?v=20261010" sizes="180x180"><link rel="manifest" href="/site.webmanifest?v=20261010">',s,count=1)
 # Root-relative paths also make custom 404 pages work at nested URLs.
 s=re.sub(r'(href|src)="((?:assets/|images/)[^"]*|[a-z0-9-]+\.html(?:\?[^"]*)?)"',lambda m:m[1]+'="/'+m[2]+'"',s)
 s=normalize_urls(s,name)
 s=redesign(s,name)
 (ROOT/name).write_text(s)
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
assert set(lastmod)==set(meta),('data/sitemap-lastmod.json must list every indexed page',set(meta)^set(lastmod))
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+url(n)+'</loc><lastmod>'+lastmod[n]+'</lastmod></url>\n' for n in meta)+'</urlset>\n')
print(f'Built {len(meta)} pages and 404; no publishing performed.')
