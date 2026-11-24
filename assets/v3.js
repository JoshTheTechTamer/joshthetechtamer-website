/* Tech Tamer v3 motion. Transform/opacity only, passive listeners, reduced motion = end frames. */
(()=>{
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE=matchMedia('(hover:hover) and (pointer:fine)').matches;
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const IO=(cb,opt)=>('IntersectionObserver' in window)?new IntersectionObserver(cb,opt):null;

/* reveals */
const rv=$$('.rvl');
if(RM||!('IntersectionObserver' in window)){rv.forEach(e=>e.classList.add('is-in'))}else{
 const o=IO(es=>es.forEach(e=>{if(e.isIntersecting){const el=e.target;const sib=[...el.parentElement.children].filter(c=>c.classList.contains('rvl'));const i=Math.max(0,sib.indexOf(el));el.style.transitionDelay=Math.min(i,5)*110+'ms';el.classList.add('is-in');o.unobserve(el)}}),{rootMargin:'0px 0px -8% 0px',threshold:.12});
 rv.forEach(e=>o.observe(e));}
$$('[data-closer]').forEach(c=>{const o=IO(es=>es.forEach(e=>{if(e.isIntersecting){c.classList.add('is-in');o.disconnect()}}),{threshold:.4});o?o.observe(c):c.classList.add('is-in')});

/* hero copy + stage story */
const hero=$('[data-hero]'), st=$('[data-stage]');
const go=()=>{hero&&hero.classList.add('is-go');$$('.phero').forEach(p=>p.classList.add('is-go'))};
if(RM){go()}else{(document.fonts&&document.fonts.ready||Promise.resolve()).then(()=>requestAnimationFrame(go))}
if(st){
 const T=[];const clr=()=>{T.forEach(clearTimeout);T.length=0};
 const set=(...c)=>{st.className='stage '+c.join(' ')};
 const play=()=>{clr();set('s0');void st.offsetWidth;
  T.push(setTimeout(()=>set('s0','s1'),250));
  T.push(setTimeout(()=>set('s0','s1','s2'),1500));
  T.push(setTimeout(()=>set('s1','s3'),2900));
  T.push(setTimeout(()=>set('s1','s3','s4'),3900));
  T.push(setTimeout(()=>set('s1','s4','is-done'),5600));};
 const end=()=>{clr();set('is-end','is-done')};
 if(RM){end()}else{
  set('s0');
  const start=()=>{const o=IO(es=>es.forEach(e=>{if(e.isIntersecting){play();o.disconnect()}}),{threshold:.5});o?o.observe(st):play()};
  (document.fonts&&document.fonts.ready||Promise.resolve()).then(start);
 }
 const b=$('.st-replay',st);b&&b.addEventListener('click',()=>RM?end():play());
 if(FINE&&!RM){let raf=0;const box=st.closest('.hero')||st;
  box.addEventListener('pointermove',e=>{if(raf)return;raf=requestAnimationFrame(()=>{raf=0;const r=box.getBoundingClientRect();st.style.setProperty('--px',((e.clientX-r.left)/r.width-.5).toFixed(3));st.style.setProperty('--py',((e.clientY-r.top)/r.height-.5).toFixed(3))})},{passive:true});
  box.addEventListener('pointerleave',()=>{st.style.setProperty('--px',0);st.style.setProperty('--py',0)});}
}
/* page-hero art parallax on pointer */
if(FINE&&!RM)$$('.phero').forEach(h=>{const a=$('.phero__art',h);if(!a)return;h.addEventListener('pointermove',e=>{const r=h.getBoundingClientRect();a.style.setProperty('--px',(((e.clientX-r.left)/r.width-.5)*16).toFixed(1));a.style.setProperty('--py',(((e.clientY-r.top)/r.height-.5)*12).toFixed(1))},{passive:true})});

/* compact bar + quiet phone bar after the header leaves */
const hd=$('.site-header'), mini=$('[data-mini]'), qbar=$('[data-qbar]');
if(hd&&mini){const toggle=on=>{mini.classList.toggle('is-on',on);mini.setAttribute('aria-hidden',String(!on));$$('a,button',mini).forEach(x=>on?x.removeAttribute('tabindex'):x.setAttribute('tabindex','-1'));if(!on){const n=$('nav',mini);n&&n.classList.remove('open');const mb=$('.mini__menu',mini);mb&&mb.setAttribute('aria-expanded','false')}};
 const o=IO(es=>es.forEach(e=>{const past=!e.isIntersecting&&e.boundingClientRect.top<0;toggle(past);qbar&&qbar.classList.toggle('is-on',past)}),{threshold:0});o&&o.observe(hd);
 const mb=$('.mini__menu',mini),mn=$('nav',mini);mb&&mb.addEventListener('click',()=>{const op=mn.classList.toggle('open');mb.setAttribute('aria-expanded',String(op));mb.textContent=op?'Close':'Menu'});}

/* timeline fill */
$$('[data-tl]').forEach(tl=>{const steps=$$('[data-step]',tl);
 const so=IO(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-seen');so.unobserve(e.target)}}),{threshold:.3});steps.forEach(s=>so?so.observe(s):s.classList.add('is-seen'));
 if(RM){tl.style.setProperty('--fill',1);steps.forEach(s=>s.classList.add('is-on','is-seen'));return}
 let raf=0;const upd=()=>{raf=0;const r=tl.getBoundingClientRect(),mid=innerHeight*.62;const f=Math.max(0,Math.min(1,(mid-r.top)/r.height));tl.style.setProperty('--fill',f.toFixed(3));steps.forEach(s=>{const n=$('.tl__num',s).getBoundingClientRect();s.classList.toggle('is-on',n.top+n.height/2<mid)})};
 addEventListener('scroll',()=>{if(!raf)raf=requestAnimationFrame(upd)},{passive:true});addEventListener('resize',upd);upd();});

/* before/after slider */
$$('[data-ba]').forEach(b=>{const r=$('.ba__range',b);if(!r)return;const s=()=>{b.style.setProperty('--pos',r.value+'%');r.setAttribute('aria-valuetext',r.value+'% social page shown')};r.addEventListener('input',s);s();
 if(!RM){const o=IO(es=>es.forEach(e=>{if(e.isIntersecting){b.classList.add('hint');o.disconnect()}}),{threshold:.6});o&&o.observe(b)}});

/* tilt + glow */
if(FINE&&!RM)$$('[data-tilt]').forEach(c=>{let raf=0;c.addEventListener('pointermove',e=>{if(raf)return;raf=requestAnimationFrame(()=>{raf=0;const r=c.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;c.style.setProperty('--ry',((x-.5)*7).toFixed(2)+'deg');c.style.setProperty('--rx',((.5-y)*6).toFixed(2)+'deg');c.style.setProperty('--mx',(x*100).toFixed(1)+'%');c.style.setProperty('--my',(y*100).toFixed(1)+'%');c.classList.add('is-tilt')})},{passive:true});
 c.addEventListener('pointerleave',()=>{c.style.setProperty('--rx','0deg');c.style.setProperty('--ry','0deg');c.classList.remove('is-tilt')})});

/* count up */
$$('[data-count]').forEach(el=>{if(RM)return;const n=+el.dataset.count;const o=IO(es=>es.forEach(e=>{if(!e.isIntersecting)return;o.disconnect();const t0=performance.now();const f=t=>{const k=Math.min(1,(t-t0)/1200),v=Math.round(n*(1-Math.pow(1-k,3)));el.textContent='$'+v;if(k<1)requestAnimationFrame(f)};requestAnimationFrame(f)}),{threshold:.6});o&&o.observe(el)});

/* reviews show all */
$$('[data-rv-more]').forEach(b=>{const w=$('[data-rv-wall]');if(!w)return;b.addEventListener('click',()=>{const open=w.classList.toggle('is-clipped')===false;b.setAttribute('aria-expanded',String(open));b.textContent=open?b.dataset.close:b.dataset.open;if(open)$$('.rv.is-extra',w).forEach(x=>x.classList.add('is-in'))})});

/* phone mockup auto-scroll */
$$('[data-devices]').forEach(d=>{const o=IO(es=>es.forEach(e=>{if(e.isIntersecting){d.classList.add('is-in');o.disconnect()}}),{threshold:.25});o?o.observe(d):d.classList.add('is-in');
 const sc=$('.phone__screen',d),img=sc&&$('img',sc);if(!img||RM)return;const fit=()=>{const end=-(img.offsetHeight-sc.offsetHeight);if(end<0){img.style.setProperty('--end',end+'px');sc.classList.add('is-scrolling')}};img.complete?fit():img.addEventListener('load',fit);addEventListener('resize',fit)});
})();
