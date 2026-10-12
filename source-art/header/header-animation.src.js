/* Tech Tamer header, round 2: a seamless loop.  The markup already IS the loop's first frame (still
   logo, angry printer on the right, no slogan).  After the page has loaded, the layered rig (cut from
   the logo's own pixels) is fetched and the scene loops; it pauses off-screen / in hidden tabs.
   Reduced motion never starts it (CSS shows the final state with the slogan). */
(()=>{
const ha=document.querySelector('.header-animation .ha');if(!ha)return;
const RM=matchMedia('(prefers-reduced-motion: reduce)');if(RM.matches)return;
const SMALL=matchMedia('(max-width:620px)'),slogan=ha.querySelector('.ha-slogan'),printer=ha.querySelector('.ha-printer'),
 pr=printer.querySelector('.ha-pr'),page=printer.querySelector('.ha-page'),thumb=printer.querySelector('.ha-thumb'),swoosh=[...slogan.querySelectorAll('.ha-swoosh path')];
const V='?v=20261011-ha4',NS='http://www.w3.org/2000/svg',PI=Math.PI;
const clamp=x=>x<0?0:x>1?1:x,ease=x=>(x=clamp(x),x*x*(3-2*x)),mix=(a,b,t)=>a+(b-a)*t,seg=(t,a,b)=>ease((t-a)/(b-a));
const back=x=>{x=clamp(x);const s=1.9;return 1+(s+1)*Math.pow(x-1,3)+s*Math.pow(x-1,2)};   // ease-out with overshoot
const trk=(k,t)=>{if(t<=k[0][0])return k[0][1];for(let i=1;i<k.length;i++)if(t<=k[i][0])return mix(k[i-1][1],k[i][1],ease((t-k[i-1][0])/(k[i][0]-k[i-1][0])));return k[k.length-1][1]};
// ---- the cycle (seconds) ----
const LIVE0=.6,LIVE1=8.7,END=13.5,BROKE0=.25,FIXED=6.05,ESC0=12,ESC1=12.9;
// banner units: desktop 700 x 200, phone 540 x 200; logo box at (8,24), 166 units wide
const LAY={d:{W:700,PR:230,PE:612,PY:117.9,S:.85,TX:288,FL:160},m:{W:540,PR:212,PE:470,PY:110.9,S:.72,TX:258,FL:150}};
const U=166/1353,P0=[8+690*U,24+910*U],FIST=[1166,738],COIL=[1182,881],CR=[14.4,11.8];
const lp=q=>[8+q[0]*U,24+q[1]*U];
let frozen=false,moveEls=[],coil,ropeB,ropeF,rig,top,ready=false,run=false,raf=0,clock=0,last=0,vis=true,L,k,state='';
const el=(t,c,a)=>{const e=document.createElement(t);e.className=c;if(a)for(const n in a)e.setAttribute(n,a[n]);return e};
function ropeSvg(c){const s=document.createElementNS(NS,'svg');s.setAttribute('class','ha-rope '+c);s.setAttribute('aria-hidden','true');s.setAttribute('focusable','false');s.style.display='none';
 s._p=['k','g','t'].map(n=>{const p=document.createElementNS(NS,'path');p.setAttribute('class',n);s.appendChild(p);return p});return s}
function build(){
 const img=n=>el('img','ha-'+n,{src:'/assets/header/'+n+'.png'+V,alt:'',width:300,height:258,decoding:'async'});
 rig=el('span','ha-rig',{'aria-hidden':'true'});rig.hidden=true;top=el('span','ha-top',{'aria-hidden':'true'});top.hidden=true;
 const mb=el('span','ha-move'),mt=el('span','ha-move');moveEls=[mb,mt];
 const im={};for(const n of ['circle','body','ringf','coil','fist','word'])im[n]=img(n);coil=im.coil;
 mb.append(im.body,im.coil);rig.append(im.circle,mb,im.ringf);mt.append(im.fist);top.append(mt,im.word);
 ropeB=ropeSvg('ha-rope--back');ropeF=ropeSvg('ha-rope--front');
 ha.insertBefore(rig,slogan);ha.insertBefore(ropeB,printer);ha.append(ropeF,top);
 return Promise.all(Object.values(im).map(i=>i.decode()))
}
function layout(){L=SMALL.matches?LAY.m:LAY.d;k=ha.clientWidth/L.W;for(const s of [ropeB,ropeF])s.setAttribute('viewBox','0 0 '+L.W+' 200')}
const f1=n=>Math.round(n*10)/10,P=(q)=>f1(q[0])+' '+f1(q[1]);
const setD=(s,d)=>{if(s._d!==d){s._d=d;for(const p of s._p)p.setAttribute('d',d)}};
const CC=new WeakMap(),css=(e,p,v)=>{let c=CC.get(e);if(!c)CC.set(e,c={});if(c[p]!==v){c[p]=v;e.style[p]=v}};
function reset(){ // back to the markup's own state = the loop's first frame
 for(const e of [...moveEls,printer,pr,page,thumb,slogan,coil,...swoosh]){e.removeAttribute('style');CC.delete(e)}
 slogan.style.removeProperty('--rv');printer.className='ha-printer is-grumpy';ropeB.style.display=ropeF.style.display='none';
 ha.classList.remove('is-live');rig.hidden=top.hidden=true;state='rest'}
// elliptical loop, rotated by `rot` degrees; returns point at angle a
const ept=(c,rx,ry,rot,a)=>{const r=rot*PI/180,x=rx*Math.cos(a),y=ry*Math.sin(a);return[c[0]+x*Math.cos(r)-y*Math.sin(r),c[1]+x*Math.sin(r)+y*Math.cos(r)]};
function render(t){
 if(t<BROKE0||t>=ESC1){if(state!=='rest')reset();return}
 state='run';
 const live=t>=LIVE0&&t<LIVE1;
 if(live!==!rig.hidden){rig.hidden=top.hidden=!live;ha.classList.toggle('is-live',live)}
 // ---- mascot (one rigid cut-out; small moves) ----
 const spin=4*PI*seg(t,1.05,2.65);                       // exactly two revolutions
 let th=trk([[LIVE0,0],[1,-2],[1.05,-1],[2.65,-1],[3.2,5],[3.8,2],[4.15,-5.5],[6,-4],[6.4,-1],[7.4,0],[7.6,-2],[8.4,-1.5],[8.65,0]],t);
 if(t>1.05&&t<2.65)th+=1.6*Math.sin(spin);
 if(t>4.2&&t<6)th+=.7*Math.sin((t-4.2)*15)*(1-seg(t,5.6,6));
 if(t>7.5&&t<8.3)th+=.6*Math.sin((t-7.5)*20);
 const dx=trk([[LIVE0,0],[2.65,0],[3.2,3.5],[3.8,1.5],[4.15,-2.5],[6,-2],[6.6,0]],t),dy=trk([[LIVE0,0],[1,-2],[1.1,-3.5],[2.65,-3.5],[3.3,-1.5],[6,-1],[8.4,-1],[8.65,0]],t);
 const tr=live?'translate('+(dx*k).toFixed(2)+'px,'+(dy*k).toFixed(2)+'px) rotate('+th.toFixed(3)+'deg)':'';
 for(const e of moveEls)css(e,'transform',tr);
 const r=th*PI/180,co=Math.cos(r),si=Math.sin(r),mv=q=>{q=lp(q);const x=q[0]-P0[0],y=q[1]-P0[1];return[P0[0]+x*co-y*si+dx,P0[1]+x*si+y*co+dy]};
 const fist=mv(FIST),coilC=mv(COIL);
 // ---- printer ----
 let px=L.PE,py=0,pa=0,sx=1,sy=1;const hw=49*L.S;
 if(t<4.25){if(t<3.8){pa=Math.sin(t*21)*2.4;py=-Math.abs(Math.sin(t*9))*1.8}else{const q=seg(t,3.8,4.25);sx=1-.08*Math.sin(q*PI);sy=1+.05*Math.sin(q*PI)}}
 else if(t<6){const q=seg(t,4.25,6);px=mix(L.PE,L.PR,q);pa=-4*Math.sin(q*PI)+Math.sin(t*22)*1.2*(1-q);py=-Math.abs(Math.sin(q*PI*5))*1.5}
 else if(t<ESC0){px=L.PR;const q=clamp((t-6)/.45);pa=Math.sin(q*PI*2)*2.5*(1-q);py=-Math.sin(q*PI)*3}
 else{const q=seg(t,ESC0+.1,ESC1-.05);px=mix(L.PR,L.PE,q);py=-Math.abs(Math.sin(q*PI*3))*7*(1-q*.4);pa=Math.sin(q*PI*6)*5*(1-q)}
 css(printer,'transform','translate('+((px-L.PR)*k).toFixed(2)+'px,'+(py*k).toFixed(2)+'px) rotate('+pa.toFixed(2)+'deg)');
 css(pr,'transform',sx===1?'':'scale('+sx.toFixed(3)+','+sy.toFixed(3)+')');
 const grumpy=t<FIXED||t>=ESC0,broken=t>=BROKE0&&t<FIXED;
 const cls='ha-printer'+(grumpy?' is-grumpy':'')+(broken?' is-broken':'');if(printer.className!==cls)printer.className=cls;
 const pg=t<FIXED?0:t<ESC0?seg(t,FIXED+.05,FIXED+.45):1-seg(t,ESC0,ESC0+.15);css(page,'transform','scaleY('+pg.toFixed(3)+')');
 // thumbs-up pops, floats and fades once he has fixed it
 if(t>=FIXED&&t<7.1){const q=(t-FIXED)/1.05,s=q<.2?back(q/.2)*1:1;css(thumb,'display','inline');css(thumb,'transform','translate(0px,'+(-10*ease(q)).toFixed(2)+'px) scale('+s.toFixed(3)+')');css(thumb,'opacity',(1-seg(t,6.65,7.1)).toFixed(3))}
 else css(thumb,'display','');
 // slogan: shows only where the printer has cleared, with a soft feathered edge
 const edge=px+hw+4;slogan.style.setProperty('--rv',((edge-L.TX)*k).toFixed(1)+'px');
 const dr=t<LIVE1?1:1-seg(t,LIVE1,LIVE1+.7);for(const p of swoosh){css(p,'strokeDashoffset',dr.toFixed(3));css(p,'visibility',dr>.995?'hidden':'')}
 // ---- the lasso: one rope from the fist, drawn under his fingers ----
 const rope=t>=.75&&t<8.4;css(coil,'visibility',live&&rope?'hidden':'');
 ropeB.style.display=ropeF.style.display=rope?'':'none';if(!rope)return;
 const T0=[fist[0]+8,lp([0,180])[1]];                     // spin spot: beside his hat
 let c,rx,ry,a,rot=0,lead=null,wrap=false,floor=false;
 if(t<1.05){const q=seg(t,.75,1.05);c=[mix(coilC[0],T0[0]+4,q),mix(coilC[1],T0[1],q)];rx=mix(CR[0],30,q);ry=mix(CR[1],7,q);a=mix(-PI/2,PI/2,q)}
 else if(t<2.65){c=[T0[0]+4*Math.cos(spin),T0[1]+2.5*Math.sin(spin)];rx=30;ry=7+4*Math.sin(spin);a=PI/2+spin;rot=6*Math.sin(spin)}
 else if(t<3.4){ // high arc with squash & stretch and a whipping rope
  const q=seg(t,2.65,3.4),A=[T0[0]+4,T0[1]],B=[L.PE+10,L.PY-60],C=[(A[0]+B[0])/2,-12],u=1-q;
  c=[u*u*A[0]+2*u*q*C[0]+q*q*B[0],u*u*A[1]+2*u*q*C[1]+q*q*B[1]];
  const w=Math.sin((t-2.65)*20)*(1-q*.5);rx=mix(30,66,q)*(1+.16*w);ry=mix(7,11,q)*(1-.3*w);rot=mix(0,-8,q)+9*Math.sin((t-2.65)*13);a=mix(PI/2,PI,q);
  const j=ept(c,rx,ry,rot,a),vx=(B[0]-A[0]),sag=24*Math.sin(q*PI);
  lead='M'+P(fist)+'C'+P([fist[0]+(j[0]-fist[0])*.3,fist[1]-30*q-10])+' '+P([j[0]-vx*.18*(1-q)-20,j[1]+sag])+' '+P(j)}
 else if(t<3.8){ // drops down over the printer, overshooting a little
  const q=(t-3.4)/.4,b=back(q);c=[mix(L.PE+10,L.PE,ease(q)),mix(L.PY-60,L.PY+6,b)];rx=mix(66,60,ease(q));ry=mix(11,22,ease(q));rot=mix(-8,0,ease(q));a=PI;wrap=q>.45}
 else if(t<6.3){ // tightens (with a squeeze), then rides along with the printer
  const q=clamp((t-3.8)/.45),b=back(q);c=[px,L.PY+6+py];rx=mix(60,hw+1.5,b);ry=mix(22,11,b);a=PI;wrap=true}
 else if(t<6.85){ // loosens and falls to the floor
  const q=seg(t,6.3,6.85),fall=q*q;c=[px,mix(L.PY+6,L.FL,fall)];rx=mix(hw+1.5,hw+12,ease(q*1.6));ry=mix(11,3.4,fall);a=PI;wrap=q<.55;floor=q>.6}
 else if(t<7.45){c=[L.PR,L.FL];rx=hw+12+Math.sin((t-6.85)*9)*(1-seg(t,6.85,7.3))*1.5;ry=3.4;a=PI;floor=true}
 else{ // reels back: slides along the floor, then up into the resting coil
  const q=seg(t,7.45,8.05),q2=seg(t,7.95,8.4);c=[mix(L.PR,coilC[0],q),mix(L.FL,coilC[1],q2)];rx=mix(mix(hw+12,CR[0]+6,q),CR[0],q2);ry=mix(3.4,CR[1],q2);a=mix(PI,1.5*PI,q2);floor=q2<.5}
 const j=ept(c,rx,ry,rot,a),o=ept(c,rx,ry,rot,a+PI);
 if(!lead){
  if(floor){const fx=Math.min(j[0],fist[0]+18);lead='M'+P(fist)+'C'+P([fist[0]+4,fist[1]+20])+' '+P([fx-6,L.FL+.5])+' '+P(j)}
  else{const v=[j[0]-fist[0],j[1]-fist[1]],sag=t<1.05?0:t<3.8?6:t<4.2?mix(6,0,seg(t,3.8,4.15)):t<6.3?0:4;
   lead='M'+P(fist)+'C'+P([fist[0]+v[0]/3,fist[1]+v[1]/3+sag])+' '+P([fist[0]+v[0]*2/3,fist[1]+v[1]*2/3+sag])+' '+P(j)}}
 const arc=(sw,to)=>'A'+f1(rx)+' '+f1(Math.max(ry,.5))+' '+f1(rot)+' 0 '+sw+' '+P(to);
 if(wrap){setD(ropeF,lead+arc(0,o));setD(ropeB,'M'+P(j)+arc(1,o))}
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
