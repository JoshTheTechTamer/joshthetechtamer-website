"""Build the header-animation layers from ONE source image (assets/hero-logo.png), so every frame
uses the same colours as the still logo.  Run with a Python that has numpy, scipy and Pillow.

Round 2 (Oct 11): the mascot is cut out with his full outline and the medallion is its own complete
layer, so nothing gets clipped when he moves.  The two white "fill" patches inside the rope loops are
removed (they are invisible on the white banner but used to cover the ring when he leaned).

Layers, all 300 x 258 like the still, one shared 256-colour palette:
  still   the logo (fills removed) - the instant frame and the loop seam
  circle  the complete medallion: blue disc + dark ring, rebuilt where the mascot covered it
  body    the mascot: hat, phone, arms, tether rope, white sticker outline (no fist, no coil)
  ringf   the lower arc of the ring, drawn in front of his legs (he sits inside the medallion)
  coil    the resting lasso coil under his right hand (hands over to the SVG rope)
  fist    his right fist, drawn above the SVG rope so the rope is always held
  word    the 'THE TECH TAMER' plate
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
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
d=np.hypot(xx-CX,yy-CY);ang=np.degrees(np.arctan2(yy-CY,xx-CX))
inDisc=d<R+18
r,g,b=[L[...,i].astype(int) for i in range(3)]
disk=lambda n:np.hypot(*np.mgrid[-n:n+1,-n:n+1])<=n
# 1) drop the opaque white fills inside the tether loop and the coil (big white areas outside the disc)
wh=(L[...,3]>200)&(np.minimum(np.minimum(r,g),b)>232)
lab,n=ndi.label(wh);sz=ndi.sum(np.ones_like(lab),lab,range(1,n+1))
for i in np.nonzero(sz>10000)[0]:
  m=lab==i+1
  if (d[m]>R+18).mean()>.95:L[m]=0
op=L[...,3]>8
blue=(b>200)&(r<90)&(g>130)&(g<190)
dark=(r<70)&(g<70)&(b<90)
white=np.minimum(np.minimum(r,g),b)>185
gold=(r>165)&(g>110)&(b<140)&(r-b>60)
skin=(r>215)&(g>135)&(g<205)&(b>70)&(b<160)
actor0=Aw[...,3]>100
actor=ndi.binary_dilation(actor0,disk(2))
# 2) ring geometry from the visible ring
ringvis=op&dark&(d>330)&(d<R+18)&~actor
bins=np.arange(-180,181,2);idx=np.clip(np.digitize(ang,bins)-1,0,179)
rin=np.full(180,np.nan);rout=np.full(180,np.nan)
for i in range(180):
  m=ringvis&(idx==i)
  if m.sum()>40:rin[i]=np.percentile(d[m],3);rout[i]=np.percentile(d[m],97)
def fill(v):ok=~np.isnan(v);xs=np.arange(180);return np.interp(xs,xs[ok],v[ok],period=180)
RI=fill(rin)[idx];RO=fill(rout)[idx]
ring=op&(d>RI-2)&(d<RO+2)
# 3) ownership at full resolution
word=op&(((yy>=912)&inDisc)|(yy>=1018))
box=(xx>1055)&(xx<1300)&(yy>630)&(yy<805)
fist=ndi.binary_dilation(skin&box,disk(7))&op&box&~word
coil=op&~inDisc&(xx>1000)&(yy>775)&(yy<1018)&~fist&~word
ringf=ring&(ang>22)&(ang<158)&~word&~fist&~coil
rope=ndi.binary_dilation(gold&inDisc&~actor,disk(7))&~blue&op&inDisc
halo=ndi.binary_dilation(actor|rope,disk(22))&white&inDisc&~ring
body=op&~word&~coil&~fist&~ringf&((~inDisc)|((actor|rope|halo)&~(ring&~actor0)))
circle=op&inDisc&~word&~coil&~fist&~ringf&~body
# 4) the rebuilt medallion (only shows where the mascot moves away)
known=circle&(blue|(ring&dark))
known=ndi.binary_erosion(known,disk(2))
BLUE=np.median(L[known&blue][:,:3],axis=0);INK=np.median(L[known&ring&dark][:,:3],axis=0)
t=np.clip(d-RI+0.5,0,1)[...,None]
syn=np.zeros((H,W,4),np.float32);syn[...,:3]=BLUE*(1-t)+INK*t;syn[...,3]=np.clip(RO-d+0.5,0,1)*255
circ=np.where(known[...,None],L.astype(np.float32),syn);circ[...,3]=np.where(known,L[...,3],syn[...,3]);circ[d>R+30]=0
# ---- delivered size ----
SIZE=(300,258)
def down(a):
  f=a.astype(np.float32)/255;f[...,:3]*=f[...,3:4]
  im=[Image.fromarray(f[...,i]).resize(SIZE,Image.BOX) for i in range(4)]
  o=np.clip(np.stack([np.array(x) for x in im],-1),0,1)
  al=o[...,3:4];rgb=np.where(al>1e-4,o[...,:3]/np.maximum(al,1e-4),0)
  return (np.concatenate([np.clip(rgb,0,1),al],-1)*255+.5).astype(np.uint8)
cov=lambda m:np.array(Image.fromarray(m.astype(np.float32)).resize(SIZE,Image.BOX))
still=down(L);a=still[...,3];a[a>=248]=255;a[a<=6]=0;still[a==0]=0
NAMES=['circle','body','ringf','coil','fist','word']
C=np.stack([cov(m) for m in [circle,body,ringf,coil,fist,word]],-1)
pri=np.array([0,1,2,3,4,5])*1e-3                 # ties go to the upper layer
owner=np.array(NAMES,dtype=object)[np.argmax(C+pri,-1)]
outside=cov(inDisc)<0.5
owner[outside&(owner=='circle')]='body'
BL=np.array(BLUE)
for _ in range(2):   # faint whitish sticker-outline pixels touching him go with him
  nb=ndi.binary_dilation(owner=='body',np.ones((3,3),bool))
  far=np.abs(still[...,:3].astype(int)-BL).max(-1)>14
  owner[nb&(owner=='circle')&far&~(cov(ring)>.5)]='body'
owner[still[...,3]==0]='none'
lay={n:np.zeros_like(still) for n in NAMES}
for n in NAMES:m=owner==n;lay[n][m]=still[m]
sc=down(circ);m=(owner!='circle')&(sc[...,3]>0)&~outside&(still[...,3]==255);lay['circle'][m]=sc[m]
ext=down(np.where(((yy>=860)&actor0&inDisc)[...,None],Aw,0).astype(np.uint8))
m=np.isin(owner,['word','ringf'])&(ext[...,3]>0)&(still[...,3]==255);lay['body'][m]=ext[m]   # trousers hidden under plate/ring
lay['still']=still
out=ROOT/'assets/header';out.mkdir(exist_ok=True)
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
P=np.clip(P+.5,0,255).astype(np.uint8);P[P[:,3]>=246,3]=255
for f in out.glob('*.png'):f.unlink()
for name,a in lay.items():
  flat=a.reshape(-1,4);_,ix=tree.query(prem(flat));ix[flat[:,3]==0]=255
  im=Image.fromarray(ix.reshape(a.shape[:2]).astype(np.uint8),'P');im.putpalette(P[:,:3].ravel().tolist())
  im.save(out/f'{name}.png',optimize=True,transparency=bytes(P[:,3].tolist()))
print({n:(out/f'{n}.png').stat().st_size for n in lay})
