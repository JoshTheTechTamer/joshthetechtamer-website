"""Draw the service-area map (inline SVG) from real lat/long. No street address: Muscatine is the city centroid.
Projection: equirectangular, x scaled by cos(latitude) so distances are true at this latitude (fine at ~60 miles)."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[1]
# City centers (OpenStreetMap Nominatim / Wikipedia coordinates, Oct 2026).
T={'Muscatine':(-91.0432,41.4245),'Fruitland':(-91.1294,41.3559),'Wilton':(-91.0168,41.5889),'West Liberty':(-91.2638,41.5700),
 'Durant':(-90.9107,41.5997),'Nichols':(-91.3076,41.4812),'Letts':(-91.2369,41.3283),'Columbus Junction':(-91.3614,41.2792),
 'Davenport':(-90.5776,41.5236),'Bettendorf':(-90.4846,41.5525),'Moline':(-90.5150,41.5066),'Rock Island':(-90.5776,41.4920),
 'East Moline':(-90.4409,41.5160),'Iowa City':(-91.5299,41.6613),'Coralville':(-91.5807,41.6760)}
W,H=1000,600;LON0,LON1,LAT0,LAT1=-91.70,-90.22,41.22,41.75
k=W/((LON1-LON0)*math.cos(math.radians(41.5)));H=round((LAT1-LAT0)*k)
P=lambda lon,lat:((lon-LON0)*math.cos(math.radians(41.5))*k,(LAT1-lat)*k)
mi=k/69.17  # SVG units per mile
pts={n:P(*c) for n,c in T.items()}
# label placement: (dx,dy,anchor,leader)
L={'Muscatine':(0,58,'middle',0),'Fruitland':(-16,10,'end',0),'Wilton':(0,-22,'middle',0),'West Liberty':(0,-22,'middle',0),
 'Durant':(0,-22,'middle',0),'Nichols':(-16,8,'end',0),'Letts':(16,24,'start',0),'Columbus Junction':(0,34,'middle',0),
 'Davenport':(-70,-50,'end',1),'Bettendorf':(0,-40,'middle',1),'East Moline':(16,-4,'start',0),'Moline':(40,52,'start',1),
 'Rock Island':(-40,62,'middle',1),'Iowa City':(26,30,'start',1),'Coralville':(20,-34,'start',1)}
def hull(ps):
 ps=sorted(ps);lo=[];up=[]
 cr=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 for p in ps:
  while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(ps):
  while len(up)>=2 and cr(up[-2],up[-1],p)<=0:up.pop()
  up.append(p)
 return lo[:-1]+up[:-1]
h=hull(list(pts.values()))
f=lambda v:f'{v:.1f}'
area=' '.join(f(x)+','+f(y) for x,y in h)
river=json.loads((ROOT/'data/map-mississippi.json').read_text())['mississippi']
rpath=' '.join('M'+' L'.join(f(P(*p)[0])+','+f(P(*p)[1]) for p in seg) for seg in river)
mx,my=pts['Muscatine']
o=[f'<svg class="area-svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="area-map-title area-map-desc" xmlns="http://www.w3.org/2000/svg">',
 '<title id="area-map-title">Map of The Tech Tamer’s service area around Muscatine, Iowa</title>',
 '<desc id="area-map-desc">House calls centered on Muscatine, covering Fruitland, Letts, Nichols, Columbus Junction, West Liberty, Wilton, Durant, Iowa City and Coralville, and the Quad Cities on both sides of the Mississippi River: Davenport and Bettendorf in Iowa, and Moline, Rock Island and East Moline in Illinois. No street address is shown.</desc>',
 '<style>.area-svg{font-family:inherit}.am-t{font-size:23px;font-weight:700;fill:#23335c;paint-order:stroke;stroke:#f4f7fc;stroke-width:6px;stroke-linejoin:round}.am-big{font-size:34px;font-weight:800}.am-sub{font-size:17px;font-weight:700;letter-spacing:.14em;fill:#0074aa}.am-state{font-size:22px;font-weight:800;letter-spacing:.4em;fill:#9aa9c6}.am-note{font-size:17px;fill:#52617f}.am-mob{display:none}@media(max-width:620px){.am-t{font-size:33px;stroke-width:9px}.am-big{font-size:44px}.am-sub{font-size:24px}.am-state{font-size:28px}.am-note{font-size:26px}.am-spokes,.am-desk{display:none}.am-mob{display:inline}}</style>',
 f'<rect width="{W}" height="{H}" fill="#f4f7fc"/>',
 '<g stroke="#e3e9f4" stroke-width="1">'+''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(50,W,50))+''.join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(50,H,50))+'</g>',
 f'<polygon points="{area}" fill="#cdeaf8" stroke="#cdeaf8" stroke-width="{f(11*mi)}" stroke-linejoin="round"/>',
 f'<path d="{rpath}" fill="none" stroke="#7cc6ea" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>',
 f'<path d="{rpath}" fill="none" stroke="#bfe6f7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
 '<g class="am-spokes" stroke="#23335c" stroke-opacity=".22" stroke-width="2" stroke-dasharray="6 7">'+''.join(f'<line x1="{f(mx)}" y1="{f(my)}" x2="{f(x)}" y2="{f(y)}"/>' for n,(x,y) in pts.items() if n!='Muscatine')+'</g>']
for n,(x,y) in pts.items():
 if n=='Muscatine':continue
 dx,dy,anc,lead=L[n]
 if lead:o.append(f'<line class="am-desk" x1="{f(x)}" y1="{f(y)}" x2="{f(x+dx*.8)}" y2="{f(y+dy*.75)}" stroke="#23335c" stroke-opacity=".5" stroke-width="1.5"/>')
 o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="8" fill="#23335c" stroke="#fff" stroke-width="3"/>')
 o.append(f'<text class="am-t am-desk" x="{f(x+dx)}" y="{f(y+dy)}" text-anchor="{anc}">{n}</text>')
o.append(f'<circle cx="{f(mx)}" cy="{f(my)}" r="30" fill="#00a3e0" fill-opacity=".25"/><circle cx="{f(mx)}" cy="{f(my)}" r="16" fill="#23335c" stroke="#00a3e0" stroke-width="5"/>')
o.append(f'<g class="am-desk"><text class="am-t am-big" x="{f(mx+30)}" y="{f(my+36)}" text-anchor="start">Muscatine</text><text class="am-sub" x="{f(mx+32)}" y="{f(my+62)}" text-anchor="start">HOME BASE</text></g>')
# Phone layout: bigger type, the Quad Cities and Iowa City/Coralville clusters get one label each (the full list is in the caption).
M=[('Muscatine',478,306,'start','am-big'),('HOME BASE',480,338,'start','am-sub'),('Fruitland',370,362,'end',''),('Letts',298,398,'end',''),
 ('Columbus Junction',245,458,'start',''),('Nichols',250,252,'end',''),('West Liberty',295,140,'middle',''),('Wilton',462,120,'middle',''),
 ('Durant',552,146,'start',''),('Iowa City &amp; Coralville',135,52,'start',''),('Quad Cities',805,160,'middle','')]
o.append('<g class="am-mob">'+''.join(f'<text class="am-t {c}" x="{x}" y="{y}" text-anchor="{a}">{t}</text>' for t,x,y,a,c in M)+'</g>')
o.append(f'<text class="am-state" x="{f(P(-91.66,41.40)[0])}" y="{f(P(-91.66,41.40)[1])}">IOWA</text><text class="am-state" x="790" y="405" text-anchor="middle">ILLINOIS</text>')
o.append(f'<text class="am-t am-sub am-desk" x="800" y="62" text-anchor="middle">QUAD CITIES · IA &amp; IL</text>')
# scale bar (10 miles) and north arrow
sx,sy=W-40-10*mi,H-30
o.append(f'<g><line x1="{f(sx)}" y1="{sy}" x2="{f(W-40)}" y2="{sy}" stroke="#23335c" stroke-width="4"/><line x1="{f(sx)}" y1="{sy-8}" x2="{f(sx)}" y2="{sy+8}" stroke="#23335c" stroke-width="3"/><line x1="{W-40}" y1="{sy-8}" x2="{W-40}" y2="{sy+8}" stroke="#23335c" stroke-width="3"/><text class="am-note" x="{f(sx+5*mi)}" y="{sy-14}" text-anchor="middle">10 miles</text></g>')
o.append(f'<g transform="translate(40 {H-60})"><path d="M0 -26 L10 4 L0 -2 L-10 4 Z" fill="#23335c"/><text class="am-note" x="0" y="26" text-anchor="middle" font-weight="800">N</text></g>')
o.append(f'<text class="am-note am-key" x="600" y="{H-14}" text-anchor="middle">Shaded: where I make house calls</text>')
o.append('</svg>')
(ROOT/'data/service-area-map.svg').write_text(''.join(o))
print(W,H,round(mi,2),'units/mile')
