"""Bundle every reviewed page into an offline desktop/phone preview. No network writes."""
from pathlib import Path
from html import escape
import re,json,base64,mimetypes
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'review';OUT.mkdir(exist_ok=True)
assets={}
def asset(url):
 path=url.split('?')[0];file=ROOT/path.lstrip('/')
 if not file.is_file():raise ValueError(path)
 if path not in assets:assets[path]='data:'+(mimetypes.guess_type(path)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(file.read_bytes()).decode()
 return path
def css_inline(text):
 def replace(m):
  p=asset(m[1]);return 'url('+assets[p]+')'
 return re.sub(r'url\([\"\']?(/assets/[^)\"\']+)[\"\']?\)',replace,text)
for part in ['circle','body','ringf','coil','fist','word']:asset('/assets/header/'+part+'.png')
pages={}
for f in ROOT.glob('*.html'):
 s=f.read_text();scripts=[]
 def script(m):
  src=m[1]
  if src.startswith('/assets/'):
   js=(ROOT/src.split('?')[0].lstrip('/')).read_text()
   if src.startswith('/assets/header-animation.js'):
    js,n=re.subn(r'src:"/assets/header/"\+(\w+)\+"\.png\?v=[^"]+"',r'src:window.TT_ASSETS["/assets/header/"+\1+".png"]',js);assert n==1
   scripts.append(js)
  return ''
 s=re.sub(r'<script\b[^>]*src="([^"]+)"[^>]*></script>',script,s)
 def css(m):return '<style>'+css_inline((ROOT/m[1].split('?')[0].lstrip('/')).read_text())+'</style>'
 s=re.sub(r'<link rel="stylesheet" href="(/assets/[^"]+)"[^>]*>',css,s)
 s=re.sub(r'<link rel="(?:preload|preconnect|icon|apple-touch-icon|manifest)"[^>]*>','',s)
 s=re.sub(r'\s(?:srcset|sizes)="[^"]*"','',s)
 s=re.sub(r'((?:src|data-tall-300|data-tall-450)=")(/assets/[^"]+)(")',lambda m:m[1]+asset(m[2])+m[3],s)
 s=s.replace('<head>','<head><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="connect-src \'none\'; form-action \'none\'">')
 s=s.replace('<button class="btn" type="submit">Send request</button>','<button class="btn" type="submit" disabled>Preview — sending disabled</button>')
 s=re.sub(r'<div id="request-turnstile"[^>]*></div>','<p>Security check and sending are disabled in this offline preview.</p>',s)
 setup='window.TECH_TAMER_PREVIEW=true;window.TECH_TAMER_QUERY=__QUERY__;window.TT_ASSETS=parent.TT_ASSETS;document.addEventListener("submit",e=>{e.preventDefault();e.stopImmediatePropagation()},true);'
 s=s.replace('</body>','<script>'+setup+'\n'+'\n'.join(scripts).replace('</script','<\\/script')+'</script></body>')
 pages[f.name]=s
options=''.join('<option value="'+n+'">'+escape(n.replace('.html','').replace('-',' ').title())+'</option>' for n in ['index.html','website-package.html','scam-help.html','privacy.html','terms.html','refunds.html','cookies.html','accessibility.html','contact.html','service-area.html','services.html','business.html','rates.html','about.html','digital-kits.html','tech-help-muscatine.html','tech-help-quad-cities.html','404.html'])
shell='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tech Tamer — Audit Preview</title><style>*{box-sizing:border-box}body{margin:0;background:#dce3ef;font-family:Arial,sans-serif}.bar{padding:12px 18px;background:#172443;color:white;display:flex;gap:12px;align-items:center;flex-wrap:wrap}.bar strong{margin-right:auto}.bar select,.bar button{font:inherit;padding:9px;border:1px solid #bac8df;border-radius:5px;background:white;color:#23335c}.bar button[aria-pressed=true]{background:#f5b731}.notice{padding:10px 18px;background:#fff4d5;color:#40311a;font-size:13px;line-height:1.5}.frame-wrap{overflow:auto}iframe{display:block;width:100%;height:78vh;border:0;margin:auto;background:white}iframe.phone{width:390px;max-width:100%}iframe.narrow{width:320px;max-width:100%}</style></head><body><div class="bar"><strong>Tech Tamer · Unpublished preview</strong><label>Page <select id="page">__OPTIONS__</select></label><button data-mode="desktop" aria-pressed="true">Desktop</button><button data-mode="phone" aria-pressed="false">Phone · 390</button><button data-mode="narrow" aria-pressed="false">Small · 320</button></div><div class="notice">Live site unchanged. New Terms and Refunds are proposed business policies for Josh’s approval. Review Cookies, Privacy and Accessibility too. Review authenticity, image permissions, account retention settings and legal applicability still require confirmation. Forms and analytics cannot send from this preview. Phone views simulate width, not a physical device.</div><div class="frame-wrap"><iframe id="site" title="Website audit preview"></iframe></div><script>
const pages=__PAGES__;window.TT_ASSETS=__ASSETS__;const frame=document.getElementById('site'),picker=document.getElementById('page');
function route(href){const u=new URL(href,'https://joshthetechtamer.com');if(u.origin!=='https://joshthetechtamer.com')return null;let n=u.pathname==='/'?'index.html':u.pathname.slice(1);if(!n.endsWith('.html'))n+='.html';return pages[n]?{n,q:u.search,h:u.hash}:null}
function show(n='index.html',q='',h=''){picker.value=n;let html=pages[n].replace('__QUERY__',JSON.stringify(q));for(const [path,data]of Object.entries(window.TT_ASSETS))html=html.split('"'+path+'"').join('"'+data+'"');frame.dataset.anchor=h;frame.srcdoc=html}
frame.addEventListener('load',()=>{const doc=frame.contentDocument;doc.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href')||'';if(href.startsWith('#')){e.preventDefault();doc.getElementById(href.slice(1))?.scrollIntoView();return}const r=route(href);if(r){e.preventDefault();show(r.n,r.q,r.h)}});if(frame.dataset.anchor)doc.getElementById(frame.dataset.anchor.slice(1))?.scrollIntoView()});
picker.addEventListener('change',()=>show(picker.value));document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>{frame.className=b.dataset.mode;document.querySelectorAll('[data-mode]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}));show();
</script></body></html>'''
shell=shell.replace('__OPTIONS__',options).replace('__PAGES__',json.dumps(pages,ensure_ascii=False).replace('</','<\\/')).replace('__ASSETS__',json.dumps(assets).replace('</','<\\/'))
p=OUT/'Tech_Tamer_Audit_Preview.html';p.write_text(shell);print(p, p.stat().st_size)
