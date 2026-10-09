"""Build static pages from preserved design templates and shared data. No network writes."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import re,json
ROOT=Path(__file__).resolve().parents[1];BASE='https://joshthetechtamer.com'
manifest=json.loads((ROOT/'data/image-manifest.json').read_text());reviews=json.loads((ROOT/'data/reviews.json').read_text());config=json.loads((ROOT/'data/site-config.json').read_text())
meta={
'index.html':('In-Home Tech Help in Muscatine, IA | The Tech Tamer','Computer, printer, Wi-Fi and device help at your home or office in Muscatine and Eastern Iowa. $50/hour. Start with a free consultation.','home'),
'services.html':('Computer, Printer & Wi-Fi Help in Muscatine | The Tech Tamer','Patient help with computers, printers, Wi-Fi, phones and TVs. Josh comes to your home or office in Muscatine, Iowa City and the Quad Cities.','services'),
'business.html':('Small-Business Branding & Tech Help in Muscatine | The Tech Tamer','Logo and brand work, advertising setup, websites and practical startup help for Eastern Iowa businesses. Free consultation; estimates for larger projects.','business'),
'digital-kits.html':('DIY Tech Guides: Wi-Fi, Computers & Scam Safety | The Tech Tamer','Practical downloadable guides for home networks, new computers, scam safety and small-business technology. Explore six kits and learn at your own pace.','kits'),
'rates.html':('Tech Help Rates & FAQ | Muscatine | The Tech Tamer','Tech help and business support at $50/hour. Free initial consultation and estimates for larger projects. Learn how visits, scheduling and project costs work.','rates'),
'about.html':('Meet Josh Sargent | Muscatine Tech Help | The Tech Tamer','Meet Josh Sargent, your local Tech Tamer. Patient, personal home and office tech help, with electronics and network engineering training.','about'),
'contact.html':('Request a Tech Help Visit in Muscatine | The Tech Tamer','Request home or office tech help in Muscatine and Eastern Iowa. Call or text 563-261-0200, or send an inquiry. Free initial consultation.','contact')}
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
 return '<section class="section reviews-section" aria-labelledby="reviews-heading"><div class="wrap"><div class="section-head"><div><div class="eyebrow">A little reassurance</div><h2 id="reviews-heading">Good help. In their words.</h2></div><p>Feedback shared by customers on Google and Facebook.</p></div><div class="review-carousel" role="region" aria-roledescription="carousel" aria-label="Customer feedback"><div class="review-track">'+''.join(cards)+'</div><div class="review-controls" hidden><button type="button" class="btn secondary" data-review="prev" aria-label="Previous review">← Previous</button><span class="review-count" aria-live="polite" aria-atomic="true">1 / 8</span><button type="button" class="btn secondary" data-review="next" aria-label="Next review">Next →</button><button type="button" class="review-pause" data-review="pause">Pause rotation</button></div></div><p class="small review-note">Names are shortened for privacy. Stars appear only where a five-star Google rating was provided. Facebook feedback is shown as originally shared.</p></div></section>'
def image_tag(m):
 tag=m.group();src=re.search(r'src="([^"]+)"',tag).group(1)
 if src not in manifest:return tag
 if src=='assets/logo.png' and 'width="58"' in tag:return tag.replace(src,'/assets/logo.png')
 variants=manifest[src];large=variants[-1];tag=tag.replace('src="'+src+'"','src="/'+large['src']+'"')
 tag=re.sub(r'\s(?:width|height)="[^"]*"','',tag)
 attrs=f' width="{large["width"]}" height="{large["height"]}" decoding="async"'
 if len(variants)>1:attrs+=' srcset="'+', '.join('/'+v['src']+' '+str(v['width'])+'w' for v in variants)+'" sizes="(max-width: 620px) calc(100vw - 44px), 580px"'
 return tag[:-1]+attrs+'>'
form='''<form id="request-form" action="/api/lead" method="post"><div class="form-row"><div><label for="name">Your name *</label><input id="name" name="name" required autocomplete="name" maxlength="100"></div><div><label for="reply">Reply by *</label><select id="reply" name="reply"><option value="text">Text message</option><option value="phone">Phone call</option><option value="email">Email</option></select></div></div><label for="contact">Phone number *</label><input id="contact" name="contact" type="tel" required maxlength="150" autocomplete="tel"><label for="service">What can I help with?</label><select id="service" name="service"><option>Tech help at home</option><option>Computers & printers</option><option>Phones & tablets</option><option>Wi-Fi & home networks</option><option>TVs & streaming</option><option>Smart devices & cameras</option><option>Accounts & scam help</option><option>Logo & brand work</option><option>Advertising setup</option><option>Startup consulting</option><option>Website & business tech</option><option>Something else</option></select><label for="location">City or service location</label><input id="location" name="location" autocomplete="address-level2" maxlength="150" placeholder="For example, Muscatine"><label for="time">Good times to reach you</label><input id="time" name="preferred_time" maxlength="150" placeholder="For example, weekday afternoons"><label for="issue">A little about your request *</label><textarea id="issue" name="issue" required maxlength="4000" placeholder="What’s happening, or what would you like help creating?"></textarea><div class="form-trap" aria-hidden="true"><label for="website">Leave this field empty</label><input id="website" name="_gotcha" tabindex="-1" autocomplete="off"></div><p class="small">Your details are used to respond to this request. Please leave out passwords, payment details, and other sensitive information.</p><div id="request-turnstile" class="cf-turnstile-box" data-sitekey="0x4AAAAAAFR89kkQkacO3Tdf" style="margin:0 0 18px;min-height:65px"></div><button class="btn" type="submit">Send request</button><p class="status" id="form-status" role="status" aria-live="polite">Your request goes straight to Josh, and he’ll get back to you the way you picked. A visit is confirmed after you agree on a time.</p><noscript><p>Please call, text, or email Josh using the links on this page.</p></noscript></form>'''
visit='''<section class="section tint" id="your-visit"><div class="wrap"><div class="section-head"><div><div class="eyebrow">Help where you need it</div><h2>What happens during a visit?</h2></div><p>At your home or office, with a plan you can understand.</p></div><div class="grid3"><article class="step"><div class="number">01</div><h3>Show me what’s happening.</h3><p>We’ll look at the device and its setup together. You don’t need to know the technical name for the problem.</p></article><article class="step"><div class="number">02</div><h3>Talk through the next step.</h3><p>We’ll discuss the work and any equipment or software needed. Hands-on help is $50/hour; larger projects start with an estimate.</p></article><article class="step"><div class="number">03</div><h3>Try it together.</h3><p>We’ll check the result and walk through how to use it. There’s room for questions along the way.</p></article></div><a class="textlink" href="/contact.html?service=Tech%20help%20at%20home">Request a visit</a></div></section>'''
for file in (ROOT/'templates').glob('*.html'):
 s=apply_header_logo(file.read_text());name=file.name
 if name=='index.html':
  s=s.replace('From the Wi-Fi that won’t cooperate to the business you’re ready to launch. I’m Josh, and I’ll help you get it working.','Wi-Fi, printers, computers, and everyday tech—without the runaround. I’m Josh, and I come to your home or office in Muscatine and Eastern Iowa to help get it working.')
  s=s.replace('<section class="cta cta-photo">',carousel()+'<section class="cta cta-photo">',1)
 if name=='services.html':
  s=s.replace('Patient, practical help for your home and everyday technology.','Patient, practical help at your home or office in Muscatine and Eastern Iowa.')
  s=s.replace('<section class="cta cta-photo">',visit+'<section class="cta cta-photo">',1)
  def context(m):
   card=m.group();h=re.search(r'<h2>(.*?)</h2>',card).group(1)
   return card.replace('href="contact.html"','href="/contact.html?service='+quote(h)+'"')
  s=re.sub(r'<article class="service-card".*?</article>',context,s)
 if name=='business.html':s=s.replace('href="contact.html"','href="/contact.html?service=Startup%20consulting"')
 if name=='contact.html':
  s=s.replace('I’ll tame promptly on your schedule','Let’s find a time to tame your tech.')
  s=s.replace('This prepares a message in your email app. Review it and press Send there to get in touch.','Tell me what you need and how you’d like me to get back to you. We’ll arrange the next step together.')
  s=re.sub(r'<form id="request-form".*?</form>',form,s)
  s=s.replace('<script src="/assets/site.js" defer></script>','<script src="/assets/site.js" defer></script><script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=onTechTamerTurnstile" async defer></script>',1)
 if name=='rates.html':
  s=s.replace('or prepare an email request on the Contact page','or send an inquiry on the Contact page')
  extra='<details><summary>What should I have ready for a visit?</summary><p>Keep the device and its usual cables available. If signing in is needed, you can enter your password yourself. Share your location and a brief description when arranging the visit.</p></details><details><summary>How are travel and payment details handled?</summary><p>Share your location when you request help. Ask Josh to confirm any travel charges, minimum billing, and payment arrangements before your visit.</p></details>'
  s=s.replace('<details><summary>Do you offer a monthly subscription?',extra+'<details><summary>Do you offer a monthly subscription?')
 if name in meta:
  title,desc,key=meta[name];s=re.sub(r'<title>.*?</title>','<title>'+escape(title)+'</title>',s)
  for prop,value in [('name="description"',desc),('property="og:title"',title),('property="og:description"',desc),('property="og:image"',BASE+'/assets/optimized/share-'+key+'.jpg')]:
   s=re.sub(r'<meta '+prop+r' content="[^"]*">','<meta '+prop+' content="'+escape(value,quote=True)+'">',s)
  s=s.replace('</head>','<meta name="twitter:card" content="summary_large_image"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"></head>')
  data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s).group(1))
  data.update({'@id':BASE+'/#business','logo':BASE+'/assets/logo.png','sameAs':data['sameAs']+['https://www.linkedin.com/in/josh-sargent-adsales'],'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Sunday','Monday','Tuesday','Thursday','Friday','Saturday'],'opens':'08:00','closes':'20:00'}]})
  graph=[data]
  if name!='index.html':graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':key.title(),'item':BASE+'/'+name}]})
  s=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph})+'</script>',s)
 else:s=s.replace('</head>','<meta name="robots" content="noindex,follow"></head>')
 s=re.sub(r'<img\b[^>]*>',image_tag,s)
 s=re.sub(r'<link rel="icon"[^>]*>','<link rel="icon" href="/assets/logo.png?v=20261002" type="image/png">',s)
 s=re.sub(r'<link rel="apple-touch-icon"[^>]*>','<link rel="apple-touch-icon" href="/assets/logo.png?v=20261002">',s)
 # Root-relative paths also make custom 404 pages work at nested URLs.
 s=re.sub(r'(href|src)="((?:assets/|images/)[^"]*|[a-z0-9-]+\.html(?:\?[^"]*)?)"',lambda m:m[1]+'="/'+m[2]+'"',s)
 (ROOT/name).write_text(s)
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+'/'+('' if n=='index.html' else n)+'</loc></url>' for n in meta)+'</urlset>')
print('Built seven pages and 404; no publishing performed.')
