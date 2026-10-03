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
if '--production' in sys.argv:
 assert json.loads((ROOT/'data/site-config.json').read_text())['form_mode']=='mailto'
 contact=(ROOT/'contact.html').read_text();script=(ROOT/'assets/site.js').read_text()
 assert 'action="mailto:joshthetechtamer@gmail.com"' in contact
 assert 'Create email draft' in contact and 'encodeURIComponent(subject)' in script and 'encodeURIComponent(body)' in script
 assert 'fetch(endpoint' not in script and "track('generate_lead'" not in script

print('PASS: HTML nesting, internal links/anchors, headings, images, structured data, all six kit links, review ratings and deployment exclusions.')
