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
NAV_SCAM='<a class="nav-scam" href="scam-help.html"><svg class="nav-scam__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3.2 2.3 20h19.4z" fill="#f2a516" stroke="#b45309" stroke-width="1.4" stroke-linejoin="round"/><path d="M12 9.5v5" stroke="#3b1d06" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17.4" r="1.25" fill="#3b1d06"/></svg>Scam Help</a>'
def footer(s):
 s=s.replace(SIGNOFF,FOOTER_AREAS,1)
 # Digital Kits leaves the main menu (desktop + mobile share the nav markup); the page stays, linked from the footer.
 hdr=re.search(r'<header\b.*?</header>',s,re.S)
 if hdr:
  h2=re.sub(r'<a href="digital-kits\.html"(?: aria-current="page")?>Digital Kits</a>','',hdr.group(),count=1);assert h2!=hdr.group(),'nav kits link'
  s=s[:hdr.start()]+h2+s[hdr.end():]
 s=s.replace('<a href="digital-kits.html">Digital kits</a><a href="rates.html">','<a href="rates.html">',1)
 s=s.replace('<a href="about.html">Meet Josh</a></div>','<a href="about.html">Meet Josh</a><a href="tech-help-muscatine.html">Tech help in Muscatine</a><a href="scam-help.html">Scam &amp; hacked accounts</a><a href="service-area.html">Areas I serve</a><a href="digital-kits.html">Digital kits</a></div>',1)
 # Scam Help in the main menu (desktop + mobile), first item, as a soft-red pill.
 hdr=re.search(r'<header\b.*?</header>',s,re.S)
 if hdr:
  h2=re.sub(r'(<a href="services\.html"(?: aria-current="page")?>Tech Help</a>)',lambda m:NAV_SCAM+m.group(1),hdr.group(),count=1);assert h2!=hdr.group(),'nav scam link'
  s=s[:hdr.start()]+h2+s[hdr.end():]
 # "Built by" badge on joshthetechtamer.com itself points to the Website Package.
 s=s.replace('<a class="ttb" href="contact.html?service=Website%20%26%20business%20tech">','<a class="ttb" href="website-package.html">',1)
 assert '<a class="ttb" href="website-package.html">' in s,'built-by badge link'
 g=(f'<a href="{escape(gbp)}" target="_blank" rel="noopener noreferrer">Find us on Google ↗</a>' if gbp else '')+(f'<a href="{escape(review_url)}" target="_blank" rel="noopener noreferrer">Leave a Google review ↗</a>' if review_url else '')
 s=s.replace('LinkedIn ↗</a></div>','LinkedIn ↗</a>'+g+'</div>',1)
 assert FOOTER_AREAS in s and 'tech-help-muscatine.html">Tech help in Muscatine' in s and 'service-area.html">Areas I serve</a><a href="digital-kits.html">Digital kits</a>' in s,'footer markup changed'
 return s

# ---- Round 2 of the redesign (Josh's feedback, Oct 11) ----
S=[None]
def rep1(s,a,b):
 assert a in s,('expected markup',a[:90]);S[0]=s.replace(a,b,1)
WARN_ICON='<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3.2 2.3 20h19.4z" fill="#f2a516" stroke="#b45309" stroke-width="1.4" stroke-linejoin="round"/><path d="M12 9.5v5" stroke="#3b1d06" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17.4" r="1.25" fill="#3b1d06"/></svg>'
SCAM_BADGE='<a class="scam-badge" href="scam-help.html"><span class="scam-badge__icon">'+WARN_ICON+'</span><span class="scam-badge__text">Scam &amp; hacked-account help</span></a>'
SCAM_BADGE_HOME='<a class="scam-badge scam-badge--wide" href="scam-help.html"><span class="scam-badge__icon">'+WARN_ICON+'</span><span class="scam-badge__text"><strong>Worried about a scam or a hacked account?</strong> Take a breath. Here’s what to do right now.</span><span class="scam-badge__go" aria-hidden="true">→</span></a>'
PHONE_ICON='<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path pathLength="1" d="M5 3.5h3.2l1.6 4.2-2.1 1.4a11 11 0 0 0 7.2 7.2l1.4-2.1 4.2 1.6V19a1.6 1.6 0 0 1-1.7 1.6A16.5 16.5 0 0 1 3.4 5.2 1.6 1.6 0 0 1 5 3.5z"/></svg>'
HELP_NOW='<div class="help-now"><span class="help-now__icon">'+PHONE_ICON+'</span><div class="help-now__body"><p class="help-now__title">Need help right now? Call or text Josh at <a href="tel:+15632610200">563-261-0200</a>.</p><p class="help-now__sub">Evenings &amp; weekends: Sun–Tue &amp; Thu–Sat, 8 AM–8 PM. Wednesday: appointment setting only.</p></div><div class="actions"><a class="btn" href="sms:+15632610200">Text Josh<span aria-hidden="true">↗</span></a><a class="btn secondary" href="tel:+15632610200">Call Josh<span aria-hidden="true">↗</span></a></div></div>'
_steps=[('Stop. Don’t pay or send anything more.','If someone is rushing you to pay, buy gift cards or move money, stop there. A real company will wait while you check.'),
 ('Hang up or close the pop-up. Don’t call the number.','Close the browser. If a warning won’t go away, hold the power button to turn the computer off. Real companies don’t put phone numbers in warning pop-ups.'),
 ('Don’t give out codes or remote access.','Never read back a code sent to your phone, and don’t let anyone connect to your computer, no matter who they say they are.'),
 ('From a safe device, change your passwords. Start with email.','Use a phone or computer you trust. Your email comes first, because it can reset almost everything else.'),
 ('Turn on 2-step verification.','Add it to your email, bank and social accounts, so a stolen password alone isn’t enough to get in.'),
 ('Call your bank if money or a card was involved.','Use the number on the back of your card, not a number from a message or a caller.'),
 ('Save screenshots and details.','Write down names, phone numbers, times and amounts, and take screenshots. They help your bank, and they help when you report it.'),
 ('Check for remote-access software.','If you let someone connect to your computer, keep it off the internet until it’s checked for programs they may have left behind. I can check it with you.')]
SCAM_STEPS=('<section class="section scam-steps-section" aria-labelledby="scam-steps-heading"><div class="wrap"><div class="section-head"><div><div class="eyebrow">Right now, before anything else</div><h2 id="scam-steps-heading">Think you’ve been scammed or hacked? Take a breath. Here’s what to do.</h2></div><p>These steps are safe to do on your own while you wait to hear back from me.</p></div>'
 +'<ol class="calm-steps">'+''.join(f'<li><span class="calm-steps__n" aria-hidden="true">{i+1}</span><div><h3>{escape(t,quote=False)}</h3><p>{escape(d,quote=False)}</p></div></li>' for i,(t,d) in enumerate(_steps))+'</ol></div></section>')
SCAM_HERO_ART=('<svg class="scam-shield" viewBox="0 0 320 320" focusable="false"><defs>'
 '<radialGradient id="shGlow" cx="50%" cy="48%" r="50%"><stop offset="0" stop-color="#12aef5" stop-opacity=".34"/><stop offset=".62" stop-color="#12aef5" stop-opacity=".08"/><stop offset="1" stop-color="#12aef5" stop-opacity="0"/></radialGradient>'
 '<linearGradient id="shFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4f8c"/><stop offset="1" stop-color="#23335c"/></linearGradient></defs>'
 '<circle class="scam-shield__glow" cx="160" cy="160" r="156" fill="url(#shGlow)"/>'
 '<circle cx="160" cy="160" r="128" fill="none" stroke="#7fd3fb" stroke-opacity=".35" stroke-width="2" stroke-dasharray="3 10" stroke-linecap="round"/>'
 '<path d="M160 50 246 85v74c0 56-38 95-86 113-48-18-86-57-86-113V85z" fill="url(#shFill)"/>'
 '<path class="scam-shield__draw" pathLength="1" d="M160 50 246 85v74c0 56-38 95-86 113-48-18-86-57-86-113V85z" fill="none" stroke="#f5b731" stroke-width="7" stroke-linejoin="round"/>'
 '<path class="scam-shield__draw scam-shield__inner" pathLength="1" d="M160 72 226 99v60c0 43-29 74-66 89-37-15-66-46-66-89V99z" fill="none" stroke="#7fd3fb" stroke-opacity=".7" stroke-width="2.5" stroke-linejoin="round"/>'
 '<path class="scam-shield__draw scam-shield__check" pathLength="1" d="M119 160l29 29 55-60" fill="none" stroke="#f5b731" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>'
 '<g class="scam-shield__spark" fill="#f5b731"><path d="M262 64l4 10 10 4-10 4-4 10-4-10-10-4 10-4z"/><path d="M52 214l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" opacity=".8"/><circle cx="276" cy="232" r="4" fill="#7fd3fb"/><circle cx="58" cy="96" r="3.5" fill="#7fd3fb"/></g></svg>')
REACH_OUT=('<div class="reach-out"><div class="reach-out__copy"><h3>Still worried, or need a hand with this? Reach out to me.</h3>'
 '<p>Text or call 563-261-0200. Tell me what happened in your own words. No judgment, and no rushing.</p></div>'
 '<div class="actions"><a class="btn" href="sms:+15632610200">Text Josh<span aria-hidden="true">↗</span></a><a class="btn secondary" href="tel:+15632610200">Call 563-261-0200<span aria-hidden="true">↗</span></a></div></div>')
TOC=[('what-to-do','What to do right now'),('spot-scams','Spot common scams'),('hacked-signs','Signs an account was hacked'),('lock-down','Lock your accounts down'),('family','Protect older family members'),('report','Where to report it'),('faq','Quick answers')]
def _sec(id_,cls,icon,eyebrow,h2,intro,body):
 return (f'<section class="section{cls} guide-sec" id="{id_}" aria-labelledby="{id_}-h"><div class="wrap"><div class="guide-head">'+icon_tile(icon)+
  f'<div><div class="eyebrow">{eyebrow}</div><h2 id="{id_}-h">{h2}</h2><p>{intro}</p></div></div>'+body+'</div></section>')
def _cards(items,cls='grid3'):
 return f'<div class="{cls} guide-cards">'+''.join('<article class="service-card guide-card">'+icon_tile(i)+f'<h3>{h}</h3>'+b+'</article>' for i,h,b in items)+'</div>'
def scam_guide():
 toc=('<nav class="scam-toc" aria-label="On this page"><p class="scam-toc__title">The free guide: jump to a section</p><ul>'+
  ''.join(f'<li><a href="#{a}">{t}</a></li>' for a,t in TOC)+'</ul></nav>')
 steps=SCAM_STEPS.replace('<section class="section scam-steps-section" aria-labelledby="scam-steps-heading">','<section class="section scam-steps-section" id="what-to-do" aria-labelledby="scam-steps-heading">',1)
 steps=steps.replace('<p>These steps are safe to do on your own while you wait to hear back from me.</p>',
  '<p>First, it’s not your fault. Scammers are professionals, and they work hard to make things feel urgent. You don’t have to fix everything this minute. Go through these steps in order, at your own pace. They’re safe to do on your own while you wait to hear back from me.</p>',1)
 steps=steps.replace('</ol></div></section>','</ol>'+REACH_OUT+toc+'</div></section>',1)
 spot=_sec('spot-scams',' tint','search','How to spot them','Common scams, and what they look like.',
  'Most scams follow the same few scripts. Once you know them, they get a lot easier to recognize.',
  _cards([('warning','Fake “virus” pop-ups','<p>A full-screen warning, sometimes with an alarm sound, says your computer is infected and gives a phone number to call. Microsoft, Apple and Google don’t put phone numbers in warnings like that. Close the browser, or hold the power button if it won’t close.</p>'),
   ('phone','Tech-support calls','<p>Someone calls saying they’re from Microsoft, Apple, Amazon or your internet company, and that your computer has a problem. Real companies don’t call you out of the blue about a virus. Hang up. If you’re unsure, call the company yourself at a number you look up.</p>'),
   ('chat','Bank, Amazon and delivery texts','<p>“Unusual charge on your account.” “Your package can’t be delivered.” “Your account is locked.” Don’t tap the link. Open the company’s own app, or call the number on the back of your card, and check from there.</p>'),
   ('gift','Gift cards and odd payments','<p>No real business, utility or government office asks you to pay with gift cards, a wire transfer, cryptocurrency or a payment app to a stranger. If anyone asks you to read off the numbers on the back of a gift card, it’s a scam.</p>'),
   ('users','Grandparent and family emergencies','<p>“Grandma, it’s me. I’m in trouble. Please don’t tell Mom.” Sometimes a “lawyer” or “officer” gets on the line. Voices can be faked now. Hang up and call your family member at the number you already have for them.</p>'),
   ('heart','Romance and too-good-to-be-true','<p>A new online friend who can never meet in person and soon has a money problem. A prize you have to pay to collect. An investment that “can’t lose.” Sending money to someone you’ve never met, or paying to win, is your cue to stop.</p>')])+
  '<div class="notice red-flags"><strong>The four big red flags.</strong> <b>Pressure</b> (act right now), <b>secrecy</b> (don’t tell anyone, stay on the line), <b>strange payment</b> (gift cards, wire, crypto) and <b>access</b> (codes, passwords, remote control of your computer). Any one of them is reason enough to stop and check with someone you trust.</div>')
 hacked=_sec('hacked-signs','','key','Is it hacked?','Signs an account was hacked.',
  'Not sure if someone got into your account? These are the usual clues.',
  '<div class="guide-split"><ul class="checklist guide-list">'+''.join(f'<li>{x}</li>' for x in [
   'Friends say they got strange messages or friend requests from you.','Your password suddenly stops working.',
   'You get emails or texts about sign-ins, password changes or new devices that weren’t you.','There are sent emails, posts or purchases you didn’t make.',
   'Your recovery phone number or backup email has been changed.','Sign-in codes arrive that you didn’t ask for.'])+'</ul>'
  '<div class="guide-aside"><h3>Seeing one of these?</h3><p>Start with your email, from a phone or computer you trust. Change the password, then turn on 2-step verification. The <a href="#what-to-do">checklist at the top</a> walks through the order. If a sign-in code shows up that you didn’t ask for, don’t share it with anyone. It usually means someone has your password, so change it.</p></div></div>')
 lock=_sec('lock-down',' tint','lock','Lock it down','Lock your accounts down.',
  'A few settings make the next scam a lot harder to pull off. Start with your email, then your bank, then everything else.',
  _cards([('key','Password manager basics','<p>Use a different password for every account, so one leak doesn’t open the rest. A password manager remembers them for you. One is built into iPhones, Android phones and the Chrome browser. A notebook kept safe at home is better than reusing the same password everywhere.</p>'),
   ('shield','2-step verification','<p>This adds a second check, like a code sent to your phone or a tap on an approval prompt, when someone signs in. A stolen password alone isn’t enough anymore. Turn it on for email first. Never read that code to anyone who calls or texts you.</p>'),
   ('mail','Recovery info','<p>Make sure each important account has a current recovery phone number and backup email. That’s how you get back in if you’re ever locked out. Check them once a year, and any time you change phone numbers.</p>')]))
 fam=_sec('family','','users','For the person everyone calls','Protect older family members.',
  'Scammers often target older adults. A little planning together goes a long way, and it works best without a lecture.',
  '<ul class="guide-tips">'+''.join(f'<li>{icon_tile(i)}<div><h3>{h}</h3><p>{b}</p></div></li>' for i,h,b in [
   ('chat','Talk about it, kindly','Share the common scripts above, like the fake pop-up and the “grandchild in trouble” call, so they’re easy to spot. Make it a conversation, not a test.'),
   ('phone','Make a “call me first” rule','Agree that before anyone sends money, buys gift cards or lets someone onto the computer, they call you (or me) first. A real request can wait five minutes.'),
   ('lock','Pick a family code word','A word only your family knows. If a caller claims to be a grandchild in trouble and can’t give it, hang up and call that grandchild directly.'),
   ('smartphone','Save the numbers that matter','Put the bank, family members and a trusted helper in their phone contacts, so they don’t have to search for numbers under pressure.'),
   ('shield','Turn on call and spam filters','Most phones and carriers can silence unknown callers or flag likely spam. With their permission, help set up 2-step verification and recovery info too.'),
   ('heart','No shame if it happens','If they get fooled, thank them for telling you. People who feel embarrassed stop asking for help, and that’s exactly what scammers want.')])+'</ul>')
 report=_sec('report',' tint','flag','Report it','Where to report a scam.',
  'Reporting helps warn others and creates a record. It doesn’t always get money back, so if money or a card was involved, call your bank first.',
  _cards([('phone','Your bank or card company','<p>Call the number on the back of your card, not a number from a text, email or caller. Tell them what happened and ask what they can do.</p>'),
   ('flag','ReportFraud.ftc.gov','<p>The Federal Trade Commission collects reports on scams and fraud. <a href="https://reportfraud.ftc.gov/" target="_blank" rel="noopener noreferrer">ReportFraud.ftc.gov ↗</a></p>'),
   ('shield','IdentityTheft.gov','<p>If someone used your name, Social Security number or opened accounts as you, this FTC site gives you a step-by-step plan. <a href="https://www.identitytheft.gov/" target="_blank" rel="noopener noreferrer">IdentityTheft.gov ↗</a></p>'),
   ('laptop','FBI Internet Crime Complaint Center','<p>For scams that happened online, especially if money was lost. <a href="https://www.ic3.gov/" target="_blank" rel="noopener noreferrer">ic3.gov ↗</a></p>')],'grid2 report-grid'))
 return steps+spot+hacked+lock+fam+report
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
DESIGN_V='20261012-steps2'
GOLD_WORD={'index.html':'you','services.html':'Working','business.html':'work','digital-kits.html':'confidence','rates.html':'pricing',
 'about.html':'local','contact.html':'tame','tech-help-muscatine.html':'Muscatine','service-area.html':'Muscatine','scam-help.html':'Help',
 'tech-help-quad-cities.html':'In-Home','404.html':'wandered'}
# Shared gold line-icon set (data/icons.json): the Website Package "essentials" icons plus matching ones for every icon spot.
ICONS=json.loads((ROOT/'data/icons.json').read_text())
ICON_FOR=[(r'locked-out','key'),(r'pop-up','warning'),(r'lock it down','lock'),(r'scam|hacked|accounts?\b','shield'),(r'computer|laptop','laptop'),(r'printer','printer'),
 (r'phone|tablet','smartphone'),(r'wi-fi|network','wifi'),(r'\btvs?\b|streaming','tv'),(r'camera|smart home','camera'),(r'logo|brand','pencil'),(r'advertis','megaphone'),
 (r'startup','lightbulb'),(r'\bweb','devices'),(r'tech help at home','home'),(r'business','briefcase'),(r'yourself','book')]
def icon_tile(name,extra=''):return '<div class="icon'+extra+'" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false">'+ICONS[name]+'</svg></div>'
CONTACT_ICONS={'Text or call':'phone','Email':'mail','Service area':'map-pin','Availability':'calendar'}
DS_SWOOSH='<svg class="ds-swoosh" viewBox="0 0 200 18" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path pathLength="1" d="M3 12.5C40 6.5 92 4.2 140 5.6c20 .6 38 2 55 4.4" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/><path pathLength="1" d="M18 15.5c38-4.6 86-6 150-3.4" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".55"/></svg>'
DS_DECO='<span class="ds-deco" aria-hidden="true"><span class="ds-dots ds-dots--tr"></span><span class="ds-dots ds-dots--bl"></span><span class="ds-stripe"></span></span>'
def redesign(s,name):
 if name=='website-package.html':return s  # the showcase keeps its own page CSS/JS
 s=s.replace('</head>','<link rel="preload" href="/assets/fonts/montserrat-900-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/design.css?v='+DESIGN_V+'"><script src="/assets/design.js?v='+DESIGN_V+'" defer></script></head>',1)
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
  if m:
   rest=part[m.end():]
   if word=='you' and rest.startswith('.'):rest='<span class="ds-gold-dot">.</span>'+rest[1:]   # home hero: gold period, no underline
   parts[i]=part[:m.start()]+'<span class="ds-gold">'+word+DS_SWOOSH+'</span>'+rest;break
 else:raise AssertionError(('gold word not in h1',name,word))
 s=s[:h.start(1)]+''.join(parts)+s[h.end(1):]
 # 2b) Shared icon set: card icons by topic, plus icons for contact methods and rate cards.
 def swap(m):
  head=unescape(re.sub(r'<[^>]+>','',m.group(1)))
  for pat,ic in ICON_FOR:
   if re.search(pat,head,re.I):return icon_tile(ic)+m.group(1)
  return m.group(0)
 s=re.sub(r'<div class="icon" aria-hidden="true"><svg\b(?:(?!</svg>).)*</svg></div>(<h[23]>(?:(?!</h[23]>).)*</h[23]>)',swap,s,flags=re.S)
 for h,ic in CONTACT_ICONS.items():
  s=s.replace('<div class="contact-option"><h2>'+h+'</h2>','<div class="contact-option has-icon">'+icon_tile(ic)+'<h2>'+h+'</h2>',1)
 s=s.replace('<article class="price-card featured"><div class="eyebrow">','<article class="price-card featured">'+icon_tile('dollar',' icon--light')+'<div class="eyebrow">',1)
 s=s.replace('<article class="price-card"><h2>Something a little bigger?</h2>','<article class="price-card">'+icon_tile('clipboard')+'<h2>Something a little bigger?</h2>',1)
 # 3) Card icons draw themselves in (gold stroke): pathLength="1" lets CSS animate any shape the same way.
 def icon(m):return re.sub(r'<(path|rect|circle|line|polyline|polygon|ellipse)\b(?![^>]*pathLength)',r'<\1 pathLength="1"',m.group())
 s=re.sub(r'<div class="icon(?: icon--light)?" aria-hidden="true"><svg\b.*?</svg>|<span class="help-now__icon"><svg\b.*?</svg>',icon,s,flags=re.S)
 # 4) Three-step rows become a gold-filling timeline.
 s=re.sub(r'<div class="grid3">(?=<(?:article|div) class="step">)','<div class="grid3 ds-steps" data-ds-steps>',s)
 return s
HEADER_STAGE=(ROOT/'source-art/header/stage.html').read_text().strip()
HEADER_V='20261012-ha11'
for file in (ROOT/'templates').glob('*.html'):
 s=apply_header_logo(file.read_text());name=file.name
 s=footer(s)
 # Header (Oct 11 rebuild): the still logo, HTML slogan and vector printer render at once; the
 # animated layers (assets/header/*.png) are fetched by header-animation.js only after page load.
 a='<canvas width="1400" height="400" aria-hidden="true"><img src="/assets/hero-logo.png" alt="The Tech Tamer" width="128" height="110"></canvas>'
 assert a in s,('header canvas markup',file.name);s=s.replace(a,HEADER_STAGE,1)
 s=re.sub(r'/assets/header-animation\.js\?v=[^"]+','/assets/header-animation.js?v='+HEADER_V,s)
 s=re.sub(r'assets/site\.css\?v=[^"]+','assets/site.css?v=20261011-headeranim6',s)
 if name=='index.html':
  # H1 keyword line (audit B2): visible headline unchanged, eyebrow promoted into the H1.
  s=s.replace('<img src="assets/hero-logo.png" alt="The Tech Tamer: Josh’s top-hatted technology tamer mascot and wordmark" width="1353" height="1162">',HERO_PICTURE,1)
  # Hero stays exactly as on main (Josh's call); the local keyword line sits in the "Getting help should be easy" section instead.
  a='<div class="eyebrow">No jargon. No runaround.</div><h2>Getting help should be easy.</h2></div>'
  assert a in s;s=s.replace(a,a+'<p class="home-local"><strong>In-home computer &amp; tech help in Muscatine, IA.</strong> House calls all over <a href="tech-help-muscatine.html">Muscatine</a> and <a href="service-area.html">nearby towns</a>, evenings &amp; weekends.</p>',1)
  s=s.replace('<a class="textlink" href="services.html">Find your tech fix</a>','<a class="textlink" href="tech-help-muscatine.html">Tech help in Muscatine</a>',1)
  # Speech bubble = link to the Website Package (same words).
  rep1(s,'<p class="hero-speech">If you like my website,<br><strong>I can build you one!</strong></p>','<a class="hero-speech hero-speech-link" href="website-package.html">If you like my website,<br><strong>I can build you one!</strong></a>')
  s=S[0]
  # "A little help goes a long way." photo: Josh in his recliner (same photo as the About page's closing section).
  rep1(s,'<img src="/assets/home-client-visit.webp" alt="Josh, The Tech Tamer, with a client during a home visit" width="1084" height="1049" loading="lazy" decoding="async">','<img src="assets/about-cta-laptop.png" alt="Josh Sargent, The Tech Tamer, smiling in a recliner with a laptop on his lap" width="1534" height="1536" loading="lazy">')
  s=S[0]
  # Scam warning badge right under the three help cards.
  rep1(s,'<a class="textlink" href="digital-kits.html">Browse digital kits</a></article></div></div></section>','<a class="textlink" href="digital-kits.html">Browse digital kits</a></article></div>'+SCAM_BADGE_HOME+'</div></section>')
  s=S[0]
 if name=='services.html':
  # Security cameras/systems: residential (in-home) only. Never commercial or business security.
  for a,b in [('<h2>Smart devices & cameras</h2><p>Bring your connected devices together with less guesswork.</p><ul class="checklist"><li>Smart-home device setup</li><li>Compatible camera app setup</li><li>Notifications and remote viewing</li><li>Device selection and planning</li></ul>','<h2>Smart home & home cameras</h2><p>Bring your home’s connected devices together with less guesswork.</p><ul class="checklist"><li>Smart-home device setup</li><li>In-home security camera app setup</li><li>Notifications and remote viewing for your home cameras</li><li>Device selection and planning</li></ul><p class="small residential-note">Residential only: security cameras and systems for your home. I don’t do commercial or business security work.</p>'),
   ('Camera and smart-device projects start with a conversation about the equipment and setup needed.','Home camera and smart-device projects start with a conversation about the equipment and setup needed. Security cameras and systems are residential (in-home) only. I don’t do commercial or business security work.')]:
   assert a in s,a[:60];s=s.replace(a,b)
  s=s.replace('<div class="eyebrow">Tech help</div><h1>Your technology.<br>Working for you.</h1>','<h1><span class="eyebrow eyebrow-h1">Computer repair &amp; tech support at your home in Muscatine</span>Your technology.<br>Working for you.</h1>',1)
  # Scam help gets its own spot in the Accounts card: a calm warning badge above the card's button.
  rep1(s,'<li>Unwanted pop-up troubleshooting</li></ul><a class="textlink" href="contact.html">Ask Josh about this</a></article></div><div class="notice">','<li>Unwanted pop-up troubleshooting</li></ul>'+SCAM_BADGE+'<a class="textlink" href="contact.html">Ask Josh about this</a></article></div><div class="notice">')
  s=S[0]
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
 if name=='scam-help.html':
  # Standalone free guide: calm checklist, a reach-out CTA right under it, then short educational sections.
  s=s.replace('<!--SCAM_HERO_ART-->',SCAM_HERO_ART,1).replace('<!--SCAM_GUIDE-->',scam_guide(),1).replace('<!--HELP_NOW_BOTTOM-->',HELP_NOW.replace('help-now"','help-now help-now--bottom"'),1)
  # No kit / download links anywhere on this page (scared people shouldn't be sent to a download); footer included.
  s=s.replace('<a href="digital-kits.html">Digital kits</a>','',1)
  s=s.replace('<a class="nav-scam" href="scam-help.html">','<a class="nav-scam" href="scam-help.html" aria-current="page">',1)
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
