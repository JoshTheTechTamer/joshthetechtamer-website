/* Tech Tamer header, round 2: a seamless loop.  The markup already IS the loop's first frame (still
   logo, angry printer on the right, no slogan).  After the page has loaded, the layered rig (cut from
   the logo's own pixels) is fetched and the scene loops; it pauses off-screen / in hidden tabs.
   Reduced motion never starts it (CSS shows the final state with the slogan). */
(()=>{
const ha=document.querySelector('.header-animation .ha');if(!ha)return;
const RM=matchMedia('(prefers-reduced-motion: reduce)');if(RM.matches)return;
const SMALL=matchMedia('(max-width:620px)'),slogan=ha.querySelector('.ha-slogan'),printer=ha.querySelector('.ha-printer'),
 pr=printer.querySelector('.ha-pr'),page=printer.querySelector('.ha-page'),thumb=printer.querySelector('.ha-thumb'),led=printer.querySelector('.ha-led'),swoosh=[...slogan.querySelectorAll('.ha-swoosh path')],gold=slogan.querySelector('.ha-gold'),stars=[...slogan.querySelectorAll('.ha-twinkle svg')];
const V='?v=20261011-ha10',NS='http://www.w3.org/2000/svg',PI=Math.PI;
const clamp=x=>x<0?0:x>1?1:x,ease=x=>(x=clamp(x),x*x*(3-2*x)),mix=(a,b,t)=>a+(b-a)*t,seg=(t,a,b)=>ease((t-a)/(b-a));
const back=x=>{x=clamp(x);const s=1.9;return 1+(s+1)*Math.pow(x-1,3)+s*Math.pow(x-1,2)};   // ease-out with overshoot
const trk=(k,t)=>{if(t<=k[0][0])return k[0][1];for(let i=1;i<k.length;i++)if(t<=k[i][0])return mix(k[i-1][1],k[i][1],ease((t-k[i-1][0])/(k[i][0]-k[i-1][0])));return k[k.length-1][1]};
// ---- the cycle (seconds) ----
const FE=36,LIVE0=.6,LIVE1=8.7,END=13.5,BROKE0=.25,FIXED=6.05,ESC0=12,ESC1=12.9;
// banner units: desktop 700 x 200, phone 540 x 200; logo box at (8,24), 166 units wide
const LAY={d:{W:700,PR:230,PE:612,PY:117.9,S:.85,TX:288,FL:160},m:{W:540,PR:212,PE:470,PY:110.9,S:.72,TX:258,FL:150}};
 // printer hops in the opening: [start, land, from, to, height] (distances left of its parking spot)
const HOPS=[[.4,.72,0,45,14],[.95,1.22,45,90,10],[1.62,1.88,90,62,6],[2.05,2.33,62,102,12],[2.6,2.95,102,36,16],[3.0,3.28,36,0,9]];
// broken bits: [spawn time = a landing, rest position left of parking spot, rotation]
// exactly one chunk per hop landing, dropped behind the printer: [landing time, landing offset, side behind (+1 = right), spin]
const SH=HOPS.map((h,i)=>[h[1],h[3],h[3]>h[2]?1:-1,[20,-35,60,-15,30,10][i]]);
const PAPER=['M-4-1l2-3 3 0 2 2 0 3-2 2-3 1-2-2zM-2-2l2 2 2-1M0 0l-1 2','M-3-3l3-1 3 2 1 3-2 3-3 0-3-2zM-2-1l3 1 1-2M1 0l0 3'],SHAPE=['M-4-3l5-1 3 4-6 2z','M-3-2l6-2-1 5-4 0z','M-4 0l3-3 4 1-2 3z'];
const U=166/1353,P0=[8+690*U,24+910*U],THUMB=[1176,690],PINKY=[1150,752],COIL=[1182,881],CR=[14.4,11.8],NP=6,BLOB=["M7.8 -0.9A6.1 6.1 0 0 1 4.6 7.6A5.2 5.2 0 0 1 -3.7 6.8A5.5 5.5 0 0 1 -8.3 -0.4A4.9 4.9 0 0 1 -4.4 -8.1A4.6 4.6 0 0 1 2.7 -7.6A5.7 5.7 0 0 1 7.8 -0.9z", "M8.9 -0.2A5.0 5.0 0 0 1 5.5 6.6A5.3 5.3 0 0 1 -4.0 7.8A3.8 3.8 0 0 1 -7.2 3.2A4.6 4.6 0 0 1 -7.6 -3.3A4.7 4.7 0 0 1 -1.4 -7.1A4.0 4.0 0 0 1 4.7 -7.5A4.8 4.8 0 0 1 8.9 -0.2z", "M10.0 0.8A6.5 6.5 0 0 1 1.4 7.5A5.1 5.1 0 0 1 -6.6 4.2A4.9 4.9 0 0 1 -6.7 -4.5A5.6 5.6 0 0 1 2.2 -7.3A6.7 6.7 0 0 1 10.0 0.8z"];
const lp=q=>[8+q[0]*U,24+q[1]*U];
let deb,smog,puffs=[],shards=[],frozen=false,moveEls=[],coil,ropeB,ropeF,rig,top,ready=false,run=false,raf=0,clock=0,last=0,vis=true,L,k,state='';
const el=(t,c,a)=>{const e=document.createElement(t);e.className=c;if(a)for(const n in a)e.setAttribute(n,a[n]);return e};
function ropeSvg(c){const s=document.createElementNS(NS,'svg');s.setAttribute('class','ha-rope '+c);s.setAttribute('aria-hidden','true');s.setAttribute('focusable','false');s.style.display='none';
 s._p=['k','g','t','h'].map(n=>{const p=document.createElementNS(NS,'path');p.setAttribute('class',n);s.appendChild(p);return p});return s}
function build(){
 const img=n=>el('img','ha-'+n,{src:'/assets/header/'+n+'.png'+V,alt:'',width:300,height:258,decoding:'async'});
 rig=el('span','ha-rig',{'aria-hidden':'true'});rig.hidden=true;top=el('span','ha-top',{'aria-hidden':'true'});top.hidden=true;
 const mb=el('span','ha-move'),mt=el('span','ha-move');moveEls=[mb,mt];
 const im={};for(const n of ['circle','body','ringf','coil','fist','word'])im[n]=img(n);coil=im.coil;
 mb.append(im.body,im.coil);rig.append(im.circle,mb,im.ringf);mt.append(im.fist);top.append(mt,im.word);
 ropeB=ropeSvg('ha-rope--back');ropeF=ropeSvg('ha-rope--front');
 deb=document.createElementNS(NS,'svg');deb.setAttribute('class','ha-debris');deb.setAttribute('aria-hidden','true');deb.style.display='none';
 shards=SH.map((s,i)=>{const p=document.createElementNS(NS,'path'),pa=[0,1,1,0,1,0][i];p.setAttribute('d',pa?PAPER[i*7%2]:SHAPE[i*5%3]);p.setAttribute('fill',pa?'#fbf8ef':i%3?'#dce8f4':'#b9c8da');deb.appendChild(p);return p});
 smog=document.createElementNS(NS,'svg');smog.setAttribute('class','ha-smog');smog.setAttribute('aria-hidden','true');smog.style.display='none';
 // a few irregular puffs in the printer's own smoke style (light fill, navy outline), just bigger
 puffs=Array.from({length:NP},(_,i)=>{const g=document.createElementNS(NS,'path');g.setAttribute('d',BLOB[i%3]);g.setAttribute('fill','#f2f5f9');g.setAttribute('stroke','#23335c');g.setAttribute('stroke-linejoin','round');smog.appendChild(g);g.style.display='none';return g});
 ha.insertBefore(rig,slogan);slogan.after(smog);ha.insertBefore(deb,printer);ha.insertBefore(ropeB,printer);ha.append(ropeF,top);
 return Promise.all(Object.values(im).map(i=>i.decode()))
}
function layout(){L=SMALL.matches?LAY.m:LAY.d;k=ha.clientWidth/L.W;for(const s of [ropeB,ropeF,deb,smog])s.setAttribute('viewBox','0 0 '+L.W+' 200')}
const f1=n=>Math.round(n*10)/10,P=(q)=>f1(q[0])+' '+f1(q[1]);
const setD=(s,d)=>{if(s._d!==d){s._d=d;for(const p of s._p)p.setAttribute('d',d)}};
const CC=new WeakMap(),css=(e,p,v)=>{let c=CC.get(e);if(!c)CC.set(e,c={});if(c[p]!==v){c[p]=v;e.style[p]=v}};
function reset(){ // back to the markup's own state = the loop's first frame
 deb.style.display=smog.style.display='none';for(const e of [...moveEls,printer,pr,page,thumb,led,slogan,coil,gold,...stars,...swoosh]){e.removeAttribute('style');CC.delete(e)}
 slogan.style.removeProperty('--rv');printer.className='ha-printer is-grumpy';ropeB.style.display=ropeF.style.display='none';
 ha.classList.remove('is-live');rig.hidden=top.hidden=true;state='rest'}
// ---- mascot pose (one rigid cut-out; small moves so the medallion never shows a seam) ----
const sm=x=>x*x*x*(x*(6*x-15)+10);   // smoothstep: the whirl winds up and settles with weight
function pose(t){
 const spin=-4*PI*sm(clamp((t-1.05)/1.4));
 let th=trk([[LIVE0,0],[1,-2],[1.05,-1],[2.45,-1],[2.75,-4.5],[3.2,4.5],[3.8,2],[4.15,-3.6],[6,-3],[6.4,-1],[7.4,0],[7.6,-1.6],[8.4,-1.2],[8.65,0]],t);
 if(t>1.05&&t<2.45)th+=1.4*Math.sin(spin-.5);
 if(t>4.2&&t<6)th+=.6*Math.sin((t-4.2)*15)*(1-seg(t,5.6,6));
 if(t>7.5&&t<8.3)th+=.5*Math.sin((t-7.5)*20);
 const dx=trk([[LIVE0,0],[2.45,0],[2.75,-3],[3.2,3.5],[3.8,1.5],[4.15,-2],[6,-1.6],[6.6,0]],t),dy=trk([[LIVE0,0],[1,-2],[1.1,-3.5],[2.45,-3.5],[2.75,-4.5],[3.3,-1.5],[6,-1],[8.4,-1],[8.65,0]],t);
 const r=th*PI/180,co=Math.cos(r),si=Math.sin(r);
 return{th,dx,dy,spin,mv:q=>{q=lp(q);const x=q[0]-P0[0],y=q[1]-P0[1];return[P0[0]+x*co-y*si+dx,P0[1]+x*si+y*co+dy]}}}
// ---- printer ----
function prn(t){
 let px=L.PE,py=0,pa=0,sx=1,sy=1;
 if(t<4.25){
  if(t<3.3){ // capers and stomps around, angry: hops with squash & stretch, little shakes between
   let h=null;for(const q of HOPS)if(t>=q[0]-.08&&t<q[1]+.16){h=q;break}
   let v=0;for(const q of HOPS)if(t>=q[1])v=q[3];px=L.PE-v;
   if(h){const[a0,a1,f,to,ht]=h;
    if(t<a0){const q=(t-(a0-.08))/.08;sx=1+.1*q;sy=1-.12*q}
    else if(t<a1){const q=(t-a0)/(a1-a0);px=L.PE-mix(f,to,ease(q));py=-ht*4*q*(1-q);const st=Math.sin(q*PI);sx=1-.1*st;sy=1+.12*st;pa=(to>f?-1:1)*7*Math.sin(q*PI*2)}
    else{const q=(t-a1)/.16,b=Math.sin(q*PI)*(1-q*.5);sx=1+.16*b;sy=1-.2*b;pa=Math.sin(q*PI*3)*2*(1-q)}}
   else{pa=Math.sin(t*38)*2.2;px+=Math.sin(t*45)*.8}}
  else if(t<3.8){pa=Math.sin(t*21)*2.4;py=-Math.abs(Math.sin(t*9))*1.8}else{const q=seg(t,3.8,4.25);sx=1-.08*Math.sin(q*PI);sy=1+.05*Math.sin(q*PI)}}
 else if(t<6){const q=seg(t,4.25,6);px=mix(L.PE,L.PR,q);pa=-4*Math.sin(q*PI)+Math.sin(t*22)*1.2*(1-q);py=-Math.abs(Math.sin(q*PI*5))*1.5}
 else if(t<ESC0){px=L.PR;const q=clamp((t-6)/.45);pa=Math.sin(q*PI*2)*2.5*(1-q);py=-Math.sin(q*PI)*3}
 else{const q=seg(t,ESC0+.1,ESC1-.05);px=mix(L.PR,L.PE,q);py=-Math.abs(Math.sin(q*PI*3))*7*(1-q*.4);pa=Math.sin(q*PI*6)*5*(1-q)}
 return{px,py,pa,sx,sy}}
const revEdge=(t,px)=>{const OPEN=L.TX-2*FE,ed=px+49*L.S+FE*.7;return t<4.25?1e4:t<6?ed:t<ESC0?mix(ed,OPEN,seg(t,6,6.5)):mix(OPEN,ed,seg(t,ESC0,ESC0+.2))};
// ---- the lasso loop: centre, radii, tilt, the knot angle; slack (0 taut .. 1 slack) drives the rope's droop ----
const T0=()=>[lp(THUMB)[0]-10,25];
function twirl(t,spin){const T=T0(),w=Math.sin(t*4.2),w2=Math.sin(t*5.6+1),lg=spin+.75;
 return{c:[T[0]+9*Math.cos(lg),T[1]+3.5*Math.sin(lg)],rx:43*(1+.1*w),ry:10+4*Math.sin(lg)+1.8*w2,rot:6*Math.sin(lg)+2.5*w2,a:PI/2+spin-.35,sl:.35}}
const WIND=()=>{const T=T0();return{c:[T[0]-38,6],rx:46,ry:8,rot:-16}};
function loop(t,P,pp){
 const coilC=P.mv(COIL),hw=49*L.S;let g;
 if(t<1.05){const q=seg(t,.75,1.05),e=twirl(1.05,0);g={c:[mix(coilC[0],e.c[0],q),mix(coilC[1],e.c[1],q)-10*Math.sin(q*PI)],rx:mix(CR[0],e.rx,q),ry:mix(CR[1],e.ry,q),rot:mix(0,e.rot,q),a:mix(-PI/2,PI/2,q),sl:.7}}
 else if(t<2.45)g=twirl(t,P.spin);
 else if(t<2.75){ // wind-up: the loop whips back up over his hat for a beat
  const q=seg(t,2.45,2.66),e=twirl(2.45,-4*PI),W=WIND(),h=t>2.66?Math.sin((t-2.66)*30)*(1-(t-2.66)/.09):0;
  g={c:[mix(e.c[0],W.c[0],q),mix(e.c[1],W.c[1],q)],rx:mix(e.rx,W.rx,q)*(1+.05*h),ry:mix(e.ry,W.ry,q)*(1-.15*h),rot:mix(e.rot,W.rot,q),a:mix(PI/2-.35,PI*.85,q),sl:mix(.2,.3,q)}}
 else if(t<3.4){ // high arc; the loop squashes, stretches and wobbles, lagging a beat behind his arm
  const q=seg(t,2.75,3.4),e=WIND(),A=e.c,B=[L.PE+10,L.PY-60],C=[(A[0]+B[0])/2,-12],u=1-q;
  const c=[u*u*A[0]+2*u*q*C[0]+q*q*B[0],u*u*A[1]+2*u*q*C[1]+q*q*B[1]],w=Math.sin((t-2.75)*17)*(1-q*.5);
  g={c,rx:mix(e.rx,66,q)*(1+.16*w),ry:mix(e.ry,11,q)*(1-.3*w),rot:mix(e.rot,-6,q)+6*Math.sin((t-2.75)*11),a:mix(PI*.85,PI,q),sl:mix(.6,.35,q)}}
 else if(t<3.8){const q=(t-3.4)/.4;g={c:[mix(L.PE+10,L.PE,ease(q)),mix(L.PY-60,L.PY+6,back(q))],rx:mix(66,60,ease(q)),ry:mix(11,22,ease(q)),rot:mix(-6,0,ease(q)),a:PI,sl:.55,wrap:q>.45}}
 else if(t<6.3){const q=clamp((t-3.8)/.45),b=back(q);g={c:[pp.px,L.PY+6+pp.py],rx:mix(60,hw+1.5,b),ry:mix(22,11,b),rot:0,a:PI,sl:mix(.5,.08,seg(t,3.8,4.2)),wrap:true}}
 else if(t<6.85){const q=seg(t,6.3,6.85),f=q*q;g={c:[pp.px,mix(L.PY+6,L.FL,f)],rx:mix(hw+1.5,hw+12,ease(q*1.6)),ry:mix(11,3.4,f),rot:0,a:PI,sl:mix(.08,.9,q),wrap:q<.55,floor:q>.6}}
 else if(t<7.45)g={c:[L.PR,L.FL],rx:hw+12+Math.sin((t-6.85)*9)*(1-seg(t,6.85,7.3))*1.5,ry:3.4,rot:0,a:PI,sl:1,floor:true};
 else{const q=seg(t,7.45,8.05),q2=seg(t,7.95,8.4);g={c:[mix(L.PR,coilC[0],q),mix(L.FL,coilC[1],q2)],rx:mix(mix(hw+12,CR[0]+6,q),CR[0],q2),ry:mix(3.4,CR[1],q2),rot:0,a:mix(PI,1.5*PI,q2),sl:.6,floor:q2<.5}}
 if(g.c[1]<3+g.ry+g.rx*Math.abs(Math.sin(g.rot*PI/180)))g.c[1]=3+g.ry+g.rx*Math.abs(Math.sin(g.rot*PI/180));   // never leaves the banner
 return g}
// elliptical loop, rotated by `rot` degrees; returns point at angle a
const ept=(c,rx,ry,rot,a)=>{const r=rot*PI/180,x=rx*Math.cos(a),y=ry*Math.sin(a);return[c[0]+x*Math.cos(r)-y*Math.sin(r),c[1]+x*Math.sin(r)+y*Math.cos(r)]};
function render(t){
 if(t<BROKE0||t>=ESC1){if(state!=='rest')reset();return}
 state='run';
 const live=t>=LIVE0&&t<LIVE1;
 if(live!==!rig.hidden){rig.hidden=top.hidden=!live;ha.classList.toggle('is-live',live)}
 const Pz=pose(t),{th,dx,dy}=Pz;
 const tr=live?'translate('+(dx*k).toFixed(2)+'px,'+(dy*k).toFixed(2)+'px) rotate('+th.toFixed(3)+'deg)':'';
 for(const e of moveEls)css(e,'transform',tr);
 const pp=prn(t),{px,py}=pp;
 css(printer,'transform','translate('+((px-L.PR)*k).toFixed(2)+'px,'+(py*k).toFixed(2)+'px) rotate('+pp.pa.toFixed(2)+'deg)');
 css(pr,'transform',pp.sx===1?'':'scale('+pp.sx.toFixed(3)+','+pp.sy.toFixed(3)+')');
 const grumpy=t<FIXED||t>=ESC0,broken=t>=BROKE0&&t<FIXED;
 const cls='ha-printer'+(grumpy?' is-grumpy':'')+(broken?' is-broken':'');if(printer.className!==cls)printer.className=cls;
 if(grumpy){css(led,'fill',Math.floor(t*5)%2?'#fff3a6':'#f5c400');css(led,'transform','')}else{const q=clamp((t-FIXED)/.3);css(led,'fill','#00a3ed');css(led,'transform',q<1?'scale('+(1+.6*Math.sin(q*PI)).toFixed(3)+')':'')}
 const pg=t<FIXED?0:t<ESC0?seg(t,FIXED+.05,FIXED+.45):1-seg(t,ESC0,ESC0+.15);css(page,'transform','scaleY('+pg.toFixed(3)+')');
 if(t>=FIXED&&t<8.3){const q=Math.min(1,(t-FIXED)/1.05),s=q<.2?back(q/.2):1;css(thumb,'display','inline');css(thumb,'transform','translate(0px,'+(-10*ease(q)).toFixed(2)+'px) scale('+s.toFixed(3)+')');css(thumb,'opacity',(1-seg(t,7.3,8.3)).toFixed(3))}
 else css(thumb,'display','');
 // broken plastic bits: knocked loose on each stomp, swept up as he drags the printer back over them
 const FLP=72+89*L.S+1.5;let anyD=false;
 SH.forEach((s,i)=>{const[ts,vv,sd,rot]=s,e=shards[i];let v='',sc=1,x=L.PE-vv+sd*(49*L.S+5),y=FLP;
  const tl=ts+.3,RL=sd*9,xf=x+RL,sx0=L.PE-vv;let sp=0;
  if(t>=ts&&t<6.2){const gone=px<=xf+6&&t>4.25?1:0;
   // falls off as he lands, then 2 small bounces and a short roll; spin follows the roll
   if(t<tl){const q=(t-ts)/.3;x=mix(sx0,x,q);y=FLP-14*4*q*(1-q)-4*(1-q)}
   else{const r=clamp((t-tl)/.45),rq=1-(1-r)*(1-r);x+=RL*rq;y=FLP-(r<.45?4*Math.sin(r/.45*PI):r<.75?1.4*Math.sin((r-.45)/.3*PI):0)}
   sp=(x-sx0)/(3*L.S)*57.3;
   if(gone){let lo=4.25,hi=6;for(let n=0;n<14;n++){const m=(lo+hi)/2;prn(m).px<=xf+6?hi=m:lo=m}const q=(t-hi)/.22;sc=1+.8*q;if(q>=1)v='hidden';e.style.opacity=(1-clamp(q)).toFixed(2)}else e.style.opacity='';
   anyD=anyD||v!=='hidden';
   e.setAttribute('transform','translate('+f1(x)+' '+f1(y)+') rotate('+(rot+sp).toFixed(0)+') scale('+(sc*2*L.S/.85).toFixed(2)+')')}else v='hidden';
  if(e._v!==v){e._v=v;e.style.visibility=v}});
 css(deb,'display',anyD?'':'none');
 // the smokescreen: cartoon clouds billow off the printer's leading edge and the words fade in through them
 const DT=.2,LIFE=1.1,S0d=4.3,S1d=6,Y0=40,Y1=L.W>600?118:146;let anyS=false;
 puffs.forEach((g,s)=>{let best=null;const n=Math.floor((t-S0d)/DT);
  for(let i=n;i>n-NP&&i>=0;i--){const ts=S0d+i*DT;if(i%NP===s&&ts<=S1d&&t-ts<LIFE){best=[ts,i];break}}
  if(!best){css(g,'display','none');return}
  const[ts,i]=best,q=(t-ts)/LIFE,h=((i*.618034)%1),h2=((i*.414214)%1),e0=revEdge(ts,prn(ts).px)-FE*.3;
  const x=e0+10*q,y=mix(Y0,Y1,h)-10*q,sc=(.9+1.1*h2)*(.7+1.1*q)*L.S/.85,op=q<.15?.95*q/.15:.95*(1-seg(q,.35,1)),rt=(i*67)%360+40*q;
  anyS=true;css(g,'display','');g.setAttribute('transform','translate('+f1(x)+' '+f1(y)+') rotate('+rt.toFixed(0)+') scale('+sc.toFixed(3)+')');g.setAttribute('stroke-width',(2/sc*L.S).toFixed(2));css(g,'opacity',op.toFixed(3))});
 css(smog,'display',anyS?'':'none');
 // 'tamed.': underline draws in, the word swells, and a little gold twinkle pops off its corner as it lands
 const dr=t<LIVE1?1:1-seg(t,LIVE1,LIVE1+.7);for(const p of swoosh){css(p,'strokeDashoffset',dr.toFixed(3));css(p,'visibility',dr>.995?'hidden':'')}
 const S0=LIVE1+.7,sw=t>=S0&&t<S0+.65?trk([[0,1],[.22,1.08],[.38,.97],[.52,1.02],[.65,1]],t-S0):1;
 css(gold,'transform',sw===1?'':'scale('+sw.toFixed(3)+')');
 stars.forEach((e,i)=>{const q=(t-S0-.42-.07*i)/.6;if(q<=0||q>=1){css(e,'transform','');return}
  const D=[[.9,-.8,1],[1.5,.2,.75],[.15,-1.3,.65]][i],s=Math.sin(q*PI)*D[2]*(q<.3?back(q/.3):1);
  css(e,'transform','translate('+(D[0]*(L.W>600?1:-.5)*q*100).toFixed(0)+'%,'+(D[1]*q*100).toFixed(0)+'%) rotate('+(q*70).toFixed(0)+'deg) scale('+s.toFixed(3)+')')});
 slogan.style.setProperty('--rv',((revEdge(t,px)-L.TX)*k).toFixed(1)+'px');
 // ---- the lasso: ONE rope from the side of his fist (fist art drawn over it) to the loop ----
 const rope=t>=.75&&t<8.4;css(coil,'visibility',live&&rope?'hidden':'');
 ropeB.style.display=ropeF.style.display=rope?'':'none';if(!rope)return;
 const g=loop(t,Pz,pp),{c,rx,ry,rot,a}=g,j=ept(c,rx,ry,rot,a),o=ept(c,rx,ry,rot,a+PI);
 // a beat of lag: where the knot was 0.14 s ago pulls the rope's far control point (heavy follow-through)
 const tl=Math.max(.75,t-.14),gl=loop(tl,pose(tl),prn(tl)),jl=ept(gl.c,gl.rx,gl.ry,gl.rot,gl.a);
 // exits the thumb side (top of the fist) when the loop is overhead, the pinky side (bottom) otherwise
 const up=clamp((Pz.mv(PINKY)[1]-j[1]-12)/26),A=Pz.mv(THUMB),Bp=Pz.mv(PINKY),S=[mix(Bp[0],A[0],up),mix(Bp[1],A[1],up)];
 const ex=[mix(.35,.25,up),mix(1,-1,up)],D=Math.hypot(j[0]-S[0],j[1]-S[1]),sag=3+g.sl*.32*D;
 let lead;
 if(g.floor){const fx=Math.min(j[0],S[0]+18);lead='M'+P(S)+'C'+P([S[0]+3,S[1]+16])+' '+P([fx-8,L.FL+.5])+' '+P(j)}
 else{const L1=Math.min(14,D*.3),c1=[S[0]+ex[0]*L1,S[1]+ex[1]*L1+sag*.35],c2=[mix(j[0],jl[0],.9)-(j[0]-S[0])*.22,mix(j[1],jl[1],.9)-(j[1]-S[1])*.22+sag];
  lead='M'+P(S)+'C'+P(c1)+' '+P(c2)+' '+P(j)}
 const arc=(sw,to)=>'A'+f1(rx)+' '+f1(Math.max(ry,.5))+' '+f1(rot)+' 0 '+sw+' '+P(to);
 if(g.wrap){setD(ropeF,lead+arc(0,o));setD(ropeB,'M'+P(j)+arc(1,o))}
 else{setD(ropeF,lead+arc(0,o)+arc(0,j));setD(ropeB,'')}
}
function frame(now){raf=0;if(!run)return;clock+=Math.min(now-last,100);last=now;let t=clock/1000;if(t>=END){clock-=END*1000;t-=END}render(t);raf=requestAnimationFrame(frame)}
function go(){if(frozen||run||!ready||document.hidden||!vis)return;run=true;layout();last=performance.now();raf=requestAnimationFrame(frame)}
function stop(){run=false;if(raf)cancelAnimationFrame(raf);raf=0}
document.addEventListener('visibilitychange',()=>document.hidden?stop():go());
addEventListener('resize',()=>{if(run)layout()});
RM.addEventListener&&RM.addEventListener('change',()=>{if(RM.matches){stop();reset()}else go()});
function start(){build().then(()=>{reset();ready=true;
 if('IntersectionObserver'in window)new IntersectionObserver(e=>{vis=e[0].isIntersecting;vis?go():stop()}).observe(ha);
 setTimeout(go,400)}).catch(()=>{})}
const idle=()=>(window.requestIdleCallback||(f=>setTimeout(f,200)))(start,{timeout:2500});
document.readyState==='complete'?idle():addEventListener('load',idle,{once:true});
// test hook for the preview recorder: freeze at time t (seconds into the cycle)
window.__ha={END,get ready(){return ready},get running(){return run},get t(){return clock/1000},stop,go,seek(t){if(!ready)return;frozen=true;stop();layout();t=((t%END)+END)%END;clock=t*1000;render(t)},resume(){frozen=false;go()}};
})();
