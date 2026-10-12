"""October 12 audit improvements shared by every generated page."""
import re

def apply(s, name):
    # One locally hosted font, shared by the header and showcase.
    s=re.sub(r'<link\b[^>]*href="https://fonts\.(?:googleapis|gstatic)\.com[^>]*>', '', s)
    s=s.replace('Muscatine · Iowa City · Quad Cities','Muscatine · Nearby towns · Quad Cities')
    s=s.replace('https://joshthetechtamer.com/assets/logo.png','https://joshthetechtamer.com/assets/optimized/hero-logo-800.png')
    s=s.replace('</header>','<div class="wrap header-motion" hidden><button type="button" class="motion-toggle" aria-pressed="false">Pause animation</button></div></header>',1)
    s=s.replace('</footer>','<div class="wrap policy-links"><a href="/privacy">Privacy</a><a href="/accessibility">Accessibility help</a><button type="button" class="privacy-settings">Cookie settings</button></div></footer>',1)
    s=s.replace('Please leave out passwords, payment details, and other sensitive information.</p>','Please leave out passwords, payment details, and other sensitive information. <a href="/privacy">How your information is handled</a>.</p>')
    s=re.sub(r'(/assets/site\.(?:css|js))(?:\?v=[^"]*)?',r'\1?v=20261012-audit1',s)
    s=s.replace('/assets/header-animation.js?v=20261012-ha11','/assets/header-animation.js?v=20261012-audit1')
    s=s.replace('</head>','<link rel="stylesheet" href="/assets/audit.css?v=20261012-audit1"><script src="/assets/privacy.js?v=20261012-audit1" defer></script></head>',1)
    return s
