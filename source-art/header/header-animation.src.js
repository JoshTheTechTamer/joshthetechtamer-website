/* Tech Tamer header: still logo first; the layered rig loads after the page has loaded and plays once.
   Layers are cut from the same logo pixels, so the rig at rest is identical to the still. */
(()=>{
const ha=document.querySelector('.header-animation .ha');if(!ha)return;
const link=ha.closest('a'),still=ha.querySelector('.ha-still'),slogan=ha.querySelector('.ha-slogan'),printer=ha.querySelector('.ha-printer'),page=printer.querySelector('.ha-page'),swoosh=[...slogan.querySelectorAll('.ha-swoosh path')];
const RM=matchMedia('(prefers-reduced-motion: reduce)'),SMALL=matchMedia('(max-width:620px)');
if(RM.matches)return;                       // reduced motion: the still banner already is the final state
const V='?v=20261011-ha1',NS='http://www.w3.org/2000/svg';
const clamp=x=>x<0?0:x>1?1:x,ease=x=>(x=clamp(x),x*x*(3-2*x)),mix=(a,b,t)=>a+(b-a)*t,PI=Math.PI;
const seg=(t,a,b)=>ease((t-a)/(b-a));
// keyframe track: [[t,v],...] eased between keys
const trk=(k,t)=>{if(t<=k[0][0])return k[0][1];for(let i=1;i<k.length;i++)if(t<=k[i][0])return mix(k[i-1][1],k[i][1],ease((t-k[i-1][0])/(k[i][0]-k[i-1][0])));return k[k.length-1][1]};
const END=7.5;
// layout in banner units (desktop 700 x 200, phone 540 x 200); logo box at (8,24), 166 units wide
const LAY={d:{W:700,PR:230,PE:612,PY:117.9,S:.85,TX:288},m:{W:540,PR:212,PE:470,PY:110.9,S:.72,TX:258}};
const U=166/1353,LX=8,LY=24,PIV=[690,910],HAND=[1150,742],COIL=[1182,881],CR=[14.4,11.8];
const lp=(x,y)=>[LX+x*U,LY+y*U];
let rig,body,coil,ropeB,ropeF,ready=false,playing=false,t0=0,pausedAt=0,raf=0,lastEnd=-1e9,L,k;
function el(tag,cls,attrs){const e=document.createElement(tag);if(cls)e.className=cls;if(attrs)for(const a in attrs)e.setAttribute(a,attrs[a]);return e}
function ropeSvg(cls){const s=document.createElementNS(NS,'svg');s.setAttribute('class','ha-rope '+cls);s.setAttribute('aria-hidden','true');s.setAttribute('focusable','false');s.hidden=true;
 const p=['k','g','t'].map(c=>{const q=document.createElementNS(NS,'path');q.setAttribute('class',c);s.appendChild(q);return q});s._p=p;return s}
function build(){
 rig=el('span','ha-rig');rig.hidden=true;rig.setAttribute('aria-hidden','true');
 const img=n=>el('img','ha-'+n,{src:'/assets/header/'+n+'.png'+V,alt:'',width:300,height:258,decoding:'async'});
 const bg=img('bg');body=el('span','ha-body');const b=img('body');coil=img('coil');body.append(b,coil);const word=img('word');
 rig.append(bg,body,word);ropeB=ropeSvg('ha-rope--back');ropeF=ropeSvg('ha-rope--front');
 ha.insertBefore(rig,slogan);ha.insertBefore(ropeB,printer);ha.appendChild(ropeF);
 return Promise.all([bg,b,coil,word].map(i=>i.decode()))
}
function layout(){L=SMALL.matches?LAY.m:LAY.d;k=ha.clientWidth/L.W;for(const s of [ropeB,ropeF])s.setAttribute('viewBox','0 0 '+L.W+' 200')}
const setD=(s,d)=>{for(const p of s._p)p.setAttribute('d',d)};
const f1=n=>Math.round(n*10)/10;
function frame(now){const t=(now-t0)/1000;if(t>=END){finish();return}render(t);raf=requestAnimationFrame(frame)}
function render(t){
 ha.classList.toggle('is-live',t>=.3&&t<7.5);   // the still logo stays on top until he actually moves
 // ---- mascot (one rigid layer, small moves so nothing behind him is ever exposed) ----
 const spin=t<1.3?0:(t-1.3)*10.2;
 let th=trk([[0,0],[.3,0],[.85,-2.4],[1.3,1],[2.7,1],[3.25,5],[3.6,2.5],[5.3,-4.5],[5.9,-1.5],[6.9,1.2],[7.5,0]],t);
 if(t>1.3&&t<2.7)th+=1.4*Math.sin(spin)*ease((t-1.3)/.3)*(1-ease((t-2.45)/.25));
 if(t>3.6&&t<5.3)th+=.7*Math.sin((t-3.6)*14)*(1-ease((t-5)/.3));
 const dx=trk([[0,0],[2.7,0],[3.25,3],[3.6,1],[5.3,-2],[6,0]],t),dy=trk([[0,0],[.3,0],[.85,-2],[1.3,-3],[2.7,-3.4],[3.3,-1.5],[5.3,-1],[6.9,-1.2],[7.5,0]],t);
 const r=th*PI/180,co=Math.cos(r),si=Math.sin(r);
 body.style.transform='translate('+(dx*k).toFixed(2)+'px,'+(dy*k).toFixed(2)+'px) rotate('+th.toFixed(3)+'deg)';
 const P=lp(...PIV),mv=q=>{const x=q[0]-P[0],y=q[1]-P[1];return[P[0]+x*co-y*si+dx,P[1]+x*si+y*co+dy]};
 const hand=mv(lp(...HAND)),coilC=mv(lp(...COIL));
 // ---- printer ----
 let px,py=0,pr=0;
 if(t<.9){const p=seg(t,.05,.85);px=mix(L.PR,L.PE,p);py=-Math.abs(Math.sin(p*PI*3))*7*(1-p*.4);pr=Math.sin(p*PI*6)*5*(1-p)}
 else if(t<3.6){px=L.PE;pr=t<3.3?Math.sin(t*19)*2.2:0;py=t<3.3?-Math.abs(Math.sin(t*9.5))*1.6:0}
 else if(t<5.45){const p=seg(t,3.6,5.4);px=mix(L.PE,L.PR,p);pr=-4*Math.sin(p*PI)+Math.sin(t*22)*1.2*(1-p);py=-Math.abs(Math.sin(p*PI*5))*1.5}
 else{px=L.PR;const q=clamp((t-5.4)/.45);pr=Math.sin(q*PI*2)*2.5*(1-q);py=-Math.sin(q*PI)*3}
 printer.style.transform='translate('+((px-L.PR)*k).toFixed(2)+'px,'+(py*k).toFixed(2)+'px) rotate('+pr.toFixed(2)+'deg)';
 printer.classList.toggle('is-grumpy',t>.05&&t<5.45);
 const pg=t<.2?1-seg(t,.02,.18):t<5.45?0:seg(t,5.45,5.85);page.style.transform='scaleY('+pg.toFixed(3)+')';page.style.visibility=pg<.02?'hidden':'';
 // slogan: only the space the printer has cleared (right of its trailing edge) shows the words
 const edge=px+49*L.S;slogan.style.clipPath='inset(-30% -10% -40% '+Math.max(0,(edge-L.TX)*k).toFixed(1)+'px)';
 const dr=t<.3?0:1-seg(t,5.55,6.25);for(const p of swoosh){p.style.strokeDashoffset=dr.toFixed(3);p.style.visibility=dr>.995?'hidden':''}
 // ---- lasso: the drawn coil hands over to a vector rope while he spins it, and back at the end ----
 const live=t>=.9&&t<7.1;coil.style.visibility=live?'hidden':'';ropeB.hidden=ropeF.hidden=!live;
 if(live){
  const pc=[px,L.PY+8+py];let c,rx,ry,a,sag=0;
  const top=[hand[0]+14,hand[1]-27];
  const sp=spin,AJ=2.05;
  const tw=[top[0]+3+Math.cos(sp)*4,top[1]+Math.sin(sp)*3],twa=AJ+.7*Math.sin(sp);
  if(t<1.3){const p=seg(t,.9,1.3);c=[mix(coilC[0],top[0]+3,p),mix(coilC[1],top[1],p)];rx=mix(CR[0],34,p);ry=mix(CR[1],8,p);a=mix(-PI/2,AJ-2*PI,p);c[0]+=4*p}
  else if(t<2.7){c=tw;rx=34;ry=8+5*Math.sin(sp);a=twa}
  else{
   const sE=10.2*1.4,end=[top[0]+3+Math.cos(sE)*4,top[1]+Math.sin(sE)*3],aE=AJ+.7*Math.sin(sE);
   const hw=49*L.S+3;
   if(t<3.3){const p=seg(t,2.7,3.3);c=[mix(end[0],pc[0],p),mix(end[1],pc[1]-4,p)-Math.sin(p*PI)*42];rx=mix(34,hw+12,p);ry=mix(8+5*Math.sin(sE),26,p);a=mix(aE,PI,p);sag=14*Math.sin(p*PI)}
   else if(t<5.7){const p=seg(t,3.3,3.6);c=[pc[0],pc[1]-4*(1-p)];rx=mix(hw+12,hw,p);ry=mix(26,11,p);a=PI;sag=mix(10,0,p)}
   else if(t<6.1){const p=seg(t,5.7,6.1);c=[pc[0],mix(pc[1],pc[1]+30*L.S,p)];rx=mix(hw,hw+8,p);ry=mix(11,7,p);a=PI;sag=8*p}
   else{const p=seg(t,6.1,7.1),lo=[L.PR,L.PY+8+30*L.S];c=[mix(lo[0],coilC[0],p),mix(lo[1],coilC[1],p)-Math.sin(p*PI)*14];rx=mix(hw+8,CR[0],p);ry=mix(7,CR[1],p);a=mix(PI,1.5*PI,p);sag=8*(1-p)}
  }
  const ca=Math.cos(a),sa=Math.sin(a),j=[c[0]+ca*rx,c[1]+sa*ry],o=[c[0]-ca*rx,c[1]-sa*ry];
  const v=[j[0]-hand[0],j[1]-hand[1]];
  const lead='M'+f1(hand[0])+' '+f1(hand[1])+'C'+f1(hand[0]+v[0]/3)+' '+f1(hand[1]+v[1]/3+sag)+' '+f1(hand[0]+v[0]*2/3)+' '+f1(hand[1]+v[1]*2/3+sag)+' '+f1(j[0])+' '+f1(j[1]);
  const arc=sw=>'A'+f1(rx)+' '+f1(Math.max(ry,.5))+' 0 0 '+sw+' '+f1(o[0])+' '+f1(o[1]);
  setD(ropeF,lead+arc(0));setD(ropeB,'M'+f1(j[0])+' '+f1(j[1])+arc(1));
 }
}
function reset(){body.style.transform='';printer.style.transform='';printer.classList.remove('is-grumpy');page.style.transform='';page.style.visibility='';slogan.style.clipPath='';for(const p of swoosh){p.style.strokeDashoffset='';p.style.visibility=''}coil.style.visibility='';ropeB.hidden=ropeF.hidden=true}
function finish(){reset();ha.classList.remove('is-live');rig.hidden=true;playing=false;lastEnd=performance.now();ha.dispatchEvent(new Event('ha:end'))}
function play(){if(playing||!ready||document.hidden)return;playing=true;layout();rig.hidden=false;t0=performance.now();raf=requestAnimationFrame(frame)}
document.addEventListener('visibilitychange',()=>{if(!playing)return;if(document.hidden){cancelAnimationFrame(raf);pausedAt=performance.now()}else{t0+=performance.now()-pausedAt;raf=requestAnimationFrame(frame)}});
addEventListener('resize',()=>{if(playing)layout()});
RM.addEventListener&&RM.addEventListener('change',()=>{if(RM.matches&&playing){cancelAnimationFrame(raf);finish()}});
// replay: hover with a mouse, or a long-press-free tap is a navigation, so touch only gets the first run
link&&link.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'&&performance.now()-lastEnd>1200)play()});
function start(){build().then(()=>{ready=true;const go=()=>setTimeout(play,500);document.hidden?document.addEventListener('visibilitychange',function v(){if(!document.hidden){document.removeEventListener('visibilitychange',v);go()}}):go()}).catch(()=>{})}
const idle=()=>(window.requestIdleCallback||(f=>setTimeout(f,200)))(start,{timeout:2500});
document.readyState==='complete'?idle():addEventListener('load',idle,{once:true});
// test hook (used by the preview recorder): freeze the scene at time t, or end it
window.__ha={play,get playing(){return playing},get ready(){return ready},END,
 seek(t){if(!ready)return;cancelAnimationFrame(raf);if(t>=END){if(playing)finish();return}playing=true;layout();rig.hidden=false;render(t)}};
})();
