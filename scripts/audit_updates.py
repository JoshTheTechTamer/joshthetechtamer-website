"""October 12 audit improvements shared by every generated page."""
import re

def apply(s, name):
    # One locally hosted font, shared by the header and showcase.
    s=re.sub(r'<link\b[^>]*href="https://fonts\.(?:googleapis|gstatic)\.com[^>]*>', '', s)
    s=s.replace('Muscatine · Iowa City · Quad Cities','Muscatine · Nearby towns · Quad Cities')
    s=s.replace('https://joshthetechtamer.com/assets/logo.png','https://joshthetechtamer.com/assets/optimized/hero-logo-800.png')
    s=s.replace('</header>','<div class="wrap header-motion" hidden><button type="button" class="motion-toggle" aria-pressed="false">Pause animation</button></div></header>',1)
    s=s.replace('</footer>','<div class="wrap policy-links"><a href="/privacy">Privacy</a><a href="/cookies">Cookies</a><a href="/terms">Terms</a><a href="/refunds">Cancellations &amp; refunds</a><a href="/accessibility">Accessibility help</a><button type="button" class="privacy-settings">Cookie settings</button></div></footer>',1)
    s=s.replace('Please leave out passwords, payment details, and other sensitive information.</p>','Please leave out passwords, payment details, and other sensitive information. <a href="/privacy">How your information is handled</a>. By pressing Send request, you ask Josh to contact you about this request using your chosen method. This does not sign you up for marketing. Message and data rates may apply to texts.</p>')
    s=re.sub(r'(/assets/site\.(?:css|js))(?:\?v=[^"]*)?',r'\1?v=20261012-audit2',s)
    s=s.replace('/assets/header-animation.js?v=20261012-ha11','/assets/header-animation.js?v=20261012-audit2')
    s=s.replace('</head>','<link rel="stylesheet" href="/assets/audit.css?v=20261012-audit2"><script src="/assets/privacy.js?v=20261012-audit2" defer></script></head>',1)
    s=re.sub(r'(alt="[^"—]+)—[^"<]*(")', r'\1\2', s)
    return s
