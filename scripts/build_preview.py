from pathlib import Path
import base64,json,mimetypes,re
root=Path(__file__).resolve().parents[1]
out=root.parent/'review';out.mkdir(exist_ok=True)
pages={f.name:f.read_text() for f in root.glob('*.html') if f.name != 'preview.html'}
assets={}
for p in [root/'assets/logo.png',root/'assets/josh.jpg',root/'assets/favicon.svg',*root.glob('images/*cover.png')]:
 assets[str(p.relative_to(root))]='data:'+mimetypes.guess_type(p.name)[0]+';base64,'+base64.b64encode(p.read_bytes()).decode()
css=(root/'assets/site.css').read_text();js=(root/'assets/site.js').read_text()
# Preview navigation is handled within this offline file, not by a server.
js=js[:js.index("if(location.pathname")]
for key,html in pages.items():
 html=html.replace('<link rel="stylesheet" href="assets/site.css">','<style>'+css+'</style>')
 html=html.replace('<script src="assets/site.js" defer></script>','')
 html=html.replace('</body>','<script>'+js+'</script></body>')
 html=html.replace('<head>','<head><meta name="robots" content="noindex,nofollow">')
 pages[key]=html
shell='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Tech Tamer — Design Preview</title><style>*{box-sizing:border-box}body{margin:0;background:#e5e9f1;font-family:Arial,sans-serif}.reviewbar{height:52px;background:#172440;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 20px;gap:12px;font-size:13px}.reviewbar b{font-size:14px}.reviewbar span{color:#c5d0e6;margin-left:12px}.controls{display:flex;gap:8px;align-items:center}.controls button{border:1px solid #7385a8;background:transparent;color:white;padding:7px 12px;border-radius:4px;cursor:pointer}.controls button.active{background:white;color:#23335c}iframe{display:block;border:0;width:100%;height:calc(100dvh - 52px);background:#fff;margin:auto;transition:width .15s}iframe.phone{width:390px;max-width:100%}.reviewbar small{font-size:12px;color:#c5d0e6}@media(max-width:620px){.reviewbar{height:56px;padding:0 12px}.reviewbar span,.reviewbar small,.controls{display:none}.reviewbar b:after{content:' · Unpublished';font-weight:400;color:#c5d0e6;font-size:12px}iframe{height:calc(100dvh - 56px)}}</style></head><body><div class="reviewbar"><div><b>The Tech Tamer</b><span>Design preview · Not published</span></div><div class="controls"><small>Use the site navigation to explore all 7 pages</small><button class="active" id="desktop" type="button">Desktop</button><button id="phone" type="button">Phone</button></div></div><iframe id="site" title="Interactive Tech Tamer website preview"></iframe><script>const pages=__PAGES__;const assets=__ASSETS__;const frame=document.getElementById('site');function show(){let key=location.hash.slice(1)||'index.html';if(!pages[key])key='index.html';let html=pages[key];for(const [path,data]of Object.entries(assets)){html=html.split('"'+path+'"').join('"'+data+'"')}frame.srcdoc=html;}frame.addEventListener('load',()=>{const d=frame.contentDocument;d.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href');if(pages[href]){e.preventDefault();if(location.hash.slice(1)===href)show();else location.hash=href}})});window.addEventListener('hashchange',show);for(const mode of ['desktop','phone'])document.getElementById(mode).addEventListener('click',()=>{frame.classList.toggle('phone',mode==='phone');document.querySelectorAll('.controls button').forEach(b=>b.classList.toggle('active',b.id===mode))});show();</script></body></html>'''
shell=shell.replace('__PAGES__',json.dumps(pages).replace('</','<\\/')).replace('__ASSETS__',json.dumps(assets))
(out/'tech-tamer-preview.html').write_text(shell)
print('Offline preview written:',(out/'tech-tamer-preview.html').stat().st_size,'bytes')
