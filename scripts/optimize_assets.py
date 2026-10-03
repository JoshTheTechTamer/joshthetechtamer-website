from pathlib import Path
from PIL import Image,ImageOps
import json,re
ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/'assets/optimized';assets.mkdir(exist_ok=True)
paths=set()
for p in (ROOT/'templates').glob('*.html'):
 paths.update(re.findall(r'<img[^>]+src="([^"]+)"',p.read_text()))
manifest={};before=after=0
for src in sorted(paths):
 p=ROOT/src
 if not p.exists():continue
 im=ImageOps.exif_transpose(Image.open(p));im.load()
 name=p.stem
 variants=[]
 for width in sorted(set([min(640,im.width),min(1280,im.width)])):
  out=im.copy();out.thumbnail((width,10000),Image.Resampling.LANCZOS)
  rel=f'assets/optimized/{name}-{width}.webp';out.save(ROOT/rel,'WEBP',quality=88,method=6)
  variants.append({'src':rel,'width':out.width,'height':out.height})
 manifest[src]=variants;before+=p.stat().st_size;after+=(ROOT/variants[-1]['src']).stat().st_size
logo=Image.open(ROOT/'assets/logo.png')
for size,name in [(116,'logo-nav'),(32,'favicon-32'),(180,'apple-touch-icon')]:
 out=logo.copy();out.thumbnail((size,size),Image.Resampling.LANCZOS);out.save(assets/(name+'.png'),optimize=True)
# Existing approved artwork provides page-specific social images; no new artwork.
for page,src in {'home':'assets/home-cta-housecall.png','services':'assets/josh-helping.jpg','business':'assets/josh-business.jpg','kits':'assets/kits-hero.webp','rates':'assets/rates-hero.png','about':'assets/josh.jpg','contact':'assets/contact-hero.png'}.items():
 im=ImageOps.exif_transpose(Image.open(ROOT/src)).convert('RGB');im.thumbnail((1200,630),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(1200,630),'#f2f4f9');canvas.paste(im,((1200-im.width)//2,(630-im.height)//2));canvas.save(assets/('share-'+page+'.jpg'),quality=87,optimize=True)
(ROOT/'data/image-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'original_unique_image_bytes':before,'optimized_largest_variant_bytes':after,'reduction_percent':round(100*(1-after/before))}))
