"""Build the header-animation layers from ONE source image (assets/hero-logo.png), so every
frame uses the same colours as the still logo.  Run with a Python that has numpy, scipy, Pillow.

Layers (all the same canvas size/offset as the still logo, transparent PNG -> WebP):
  still.webp  the untouched logo (frame 0 and the final frame)
  bg.webp     the blue medallion + ring, with the mascot area rebuilt (plain blue fill + ring)
  body.webp   mascot (hat, phone, arms, tether rope, white sticker halo) - logo pixels only,
              plus hidden trouser fabric below the waist from the GPT mascot cut-out
  coil.webp   the lasso coil hanging from his right hand (swapped for the animated SVG rope)
  word.webp   'THE TECH TAMER' wordmark plate (stationary foreground)
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
L=np.array(Image.open(ROOT/'assets/hero-logo.png').convert('RGBA'))
H,W=L.shape[:2]
# GPT mascot cut-out, aligned to the logo (affine found with OpenCV ECC; actor px -> logo px)
WARP=np.array([[2.21323561668396,0.025878403335809708,43.2644157409668],[-0.008582452312111855,2.178365468978882,7.855079650878906]])
A=Image.open(ROOT/'source-art/header/mascot-actor-source.png').convert('RGBA')
inv=np.linalg.inv(np.vstack([WARP,[0,0,1]]))
Aw=np.array(A.transform((W,H),Image.AFFINE,tuple(inv[:2].ravel()),resample=Image.BICUBIC))
yy,xx=np.mgrid[0:H,0:W]
CX,CY,R=685,635,386
d=np.hypot(xx-CX,yy-CY);ang=np.arctan2(yy-CY,xx-CX)
inDisc=d<R+18
op=L[...,3]>8
r,g,b=[L[...,i].astype(int) for i in range(3)]
blue=(b>200)&(r<90)&(g>130)&(g<190)
dark=(r<70)&(g<70)&(b<90)
white=(np.minimum(np.minimum(r,g),b)>185)
gold=(r>165)&(g>110)&(b<140)&(r-b>60)
disk=lambda n:np.hypot(*np.mgrid[-n:n+1,-n:n+1])<=n
actor=ndi.binary_dilation(Aw[...,3]>100,disk(2))
coil=op&~inDisc&(xx>1000)&(yy>775)&(yy<1018)
word=op&~coil&(((yy>=912)&inDisc)|(yy>=1018))
rope=ndi.binary_dilation(gold&inDisc&~actor,disk(7))&~blue&op&inDisc
halo=ndi.binary_dilation(actor|rope,disk(22))&white&inDisc
body=op&~word&~coil&(~inDisc|actor|rope|halo)
body=ndi.binary_closing(body,disk(2))&op&~word&~coil
# --- background medallion: logo pixels where visible, rebuilt blue fill + ring where covered ---
known=op&inDisc&~body
ringpx=known&dark&(d>330)&~word
bins=np.linspace(-np.pi,np.pi,181)
rin=np.full(180,np.nan);rout=np.full(180,np.nan)
idx=np.digitize(ang,bins)-1
for i in range(180):
  m=ringpx&(idx==i)
  if m.sum()>40:rin[i]=np.percentile(d[m],3);rout[i]=np.percentile(d[m],97)
def fill(v):
  ok=~np.isnan(v);xs=np.arange(180);return np.interp(xs,xs[ok],v[ok],period=180)
rin,rout=fill(rin),fill(rout)
RI=rin[np.clip(idx,0,179)];RO=rout[np.clip(idx,0,179)]
BLUE=np.median(L[known&blue][:,:3],axis=0);INK=np.median(L[ringpx][:,:3],axis=0)
syn=np.zeros((H,W,4),np.float32)
t=np.clip(d-RI+0.5,0,1)[...,None]   # 0 = blue, 1 = ink
syn[...,:3]=BLUE*(1-t)+INK*t
syn[...,3]=np.clip(RO-d+0.5,0,1)*255
kn=known&((np.abs(L[...,:3].astype(int)-BLUE).max(-1)<18)|(d>RI-2))
kn=ndi.binary_erosion(kn,disk(2))
bg=np.where(kn[...,None],L.astype(np.float32),syn)
bg[...,3]=np.where(kn,L[...,3],np.where(d<RO+1,syn[...,3],0))
bg[~inDisc]=0
# --- everything below is done at the delivered size (300 x 258) ---
# The still is downscaled ONCE.  Every layer pixel that is visible at rest is a copy of the
# still's own pixel (a hard partition, no overlaps), so the layers stacked at rest are
# pixel-identical to the still.  Hidden pixels (under the mascot / plate) get rebuilt fill.
SIZE=(300,258)
def down(a):
  f=a.astype(np.float32)/255;f[...,:3]*=f[...,3:4]
  im=[Image.fromarray(f[...,i]).resize(SIZE,Image.BOX) for i in range(4)]
  o=np.clip(np.stack([np.array(x) for x in im],-1),0,1)
  al=o[...,3:4];rgb=np.where(al>1e-4,o[...,:3]/np.maximum(al,1e-4),0)
  return (np.concatenate([np.clip(rgb,0,1),al],-1)*255+.5).astype(np.uint8)
cov=lambda m:np.array(Image.fromarray(m.astype(np.float32)).resize(SIZE,Image.BOX))
still=down(L)
a=still[...,3];a[a>=248]=255;a[a<=6]=0;still[a==0]=0   # snap near-opaque/near-empty alpha
vis=still[...,3]>0
bgk=op&inDisc&~body&~word&~coil
C=np.stack([cov(bgk),cov(body),cov(coil),cov(word)],-1)
names=np.array(['bg','body','coil','word'],dtype=object)
owner=names[np.argmax(C+np.array([0,1e-3,0,2e-3]),-1)]
outside=cov(inDisc)<0.5
# the mascot also takes the faint white sticker-halo edge pixels that touch it, so nothing
# whitish is left behind on the blue medallion when he moves
BL=np.array(BLUE)
for _ in range(2):
  nb=ndi.binary_dilation(owner=='body',np.ones((3,3),bool))
  far=np.abs(still[...,:3].astype(int)-BL).max(-1)>14
  owner[nb&(owner=='bg')&far]='body'
owner[~vis]='none'
lay={n:np.zeros_like(still) for n in ['bg','body','coil','word']}
for n in lay:
  m=owner==n;lay[n][m]=still[m]
synd=down(bg)                     # rebuilt medallion, only shows where the mascot moves away
m=(owner!='bg')&(synd[...,3]>0)&~outside&(still[...,3]==255);lay['bg'][m]=synd[m]
extd=down(np.where(((yy>=880)&(Aw[...,3]>100)&inDisc)[...,None],Aw,0).astype(np.uint8))
m=(owner=='word')&(extd[...,3]>0)&(lay['body'][...,3]==0)&(still[...,3]==255);lay['body'][m]=extd[m]   # trousers hidden under the plate
lay['still']=still
out=ROOT/'assets/header';out.mkdir(exist_ok=True)
# ONE shared 256-colour palette built from the still; identical pixels -> identical palette index
from scipy.spatial import cKDTree
def prem(x):x=x.astype(np.float32);return np.c_[x[:,:3]*x[:,3:4]/255,x[:,3]]
pool=np.concatenate([lay[n].reshape(-1,4) for n in lay]);pool=pool[pool[:,3]>0]
rng=np.random.default_rng(1)
seed=Image.fromarray(still).convert('RGB').quantize(200,method=Image.Quantize.FASTOCTREE)
c0=np.c_[np.array(seed.getpalette()[:200*3]).reshape(-1,3),np.full(200,255)]
edge=pool[pool[:,3]<255];c0=np.vstack([c0,edge[rng.choice(len(edge),55,replace=False)]])
cent=prem(c0);X=prem(pool)
for _ in range(15):
  _,ix=cKDTree(cent).query(X)
  sums=np.zeros_like(cent);np.add.at(sums,ix,X);cnt=np.bincount(ix,minlength=len(cent))
  cent=np.where(cnt[:,None]>0,sums/np.maximum(cnt,1)[:,None],cent)
cent=np.vstack([cent,[0,0,0,0]]);tree=cKDTree(cent)
P=np.c_[np.where(cent[:,3:4]>0,cent[:,:3]*255/np.maximum(cent[:,3:4],1e-3),0),cent[:,3]]
P=np.clip(P+.5,0,255).astype(np.uint8)
P[P[:,3]>=246,3]=255   # opaque stays opaque
for name,a in lay.items():
  flat=a.reshape(-1,4);_,ix=tree.query(prem(flat));ix[flat[:,3]==0]=255
  im=Image.fromarray(ix.reshape(a.shape[:2]).astype(np.uint8),'P');im.putpalette(P[:,:3].ravel().tolist())
  im.save(out/f'{name}.png',optimize=True,transparency=bytes(P[:,3].tolist()))
  Image.fromarray(a).save(f'/workspace/previews/header-anim/work/{name}-300.png')
print({n:(out/f'{n}.png').stat().st_size for n in lay})
