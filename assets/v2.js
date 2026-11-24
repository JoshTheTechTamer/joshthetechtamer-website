/* Tech Tamer v2 motion. Every effect has a resting end frame for reduced motion and no-JS. */
(function(){
var d=document,root=d.documentElement,reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
root.classList.remove('no-js');root.classList.add('js');

/* current page in nav */
var path=location.pathname.replace(/\.html$/,'').replace(/\/$/,'')||'/';
d.querySelectorAll('.navlinks a[href^="/"]').forEach(function(a){var h=a.getAttribute('href').split(/[?#]/)[0];if(h!=='/'&&h===path)a.setAttribute('aria-current','page')});

/* header shadow after scrolling */
var hd=d.querySelector('.hd');
if(hd){var onS=function(){hd.classList.toggle('is-scrolled',scrollY>8)};addEventListener('scroll',onS,{passive:true});onS()}

/* scroll reveals (staggered children with data-stagger) */
d.querySelectorAll('[data-stagger]').forEach(function(g){var step=+g.getAttribute('data-stagger')||90;g.querySelectorAll('.msg,.price,.check,.reveal').forEach(function(el,i){el.style.transitionDelay=(i*step)+'ms'})});
var watch=d.querySelectorAll('.reveal,.visit,.closer');
if(reduce||!('IntersectionObserver' in window)){watch.forEach(function(el){el.classList.add('is-in')})}
else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -12% 0px',threshold:.12});watch.forEach(function(el){io.observe(el)})}

/* hero fix-it scene: grumpy printer, Josh steps in, gold rope, printer cheers up */
var st=d.querySelector('[data-stage]');
if(st){
 var timers=[],T=function(f,ms){timers.push(setTimeout(f,ms))};
 var clear=function(){timers.forEach(clearTimeout);timers=[];st.classList.remove('s-grump','s-josh','s-rope','s-fixed','is-done','is-end')};
 var play=function(){
  clear();
  if(reduce){st.classList.add('is-end','is-done');return}
  void st.offsetWidth;
  st.classList.add('s-grump');
  T(function(){st.classList.add('s-josh')},1300);
  T(function(){st.classList.add('s-rope')},2300);
  T(function(){st.classList.remove('s-grump');st.classList.add('s-fixed')},3900);
  T(function(){st.classList.add('is-done')},5600);
 };
 st.classList.remove('is-end');
 var btn=st.querySelector('.stage__replay');if(btn)btn.addEventListener('click',play);
 var started=false,go=function(){if(started)return;started=true;play()};
 if(reduce||!('IntersectionObserver' in window)){go()}
 else{var sio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&e.intersectionRatio>=.6){sio.disconnect();if(d.readyState==='complete')setTimeout(go,150);else addEventListener('load',function(){setTimeout(go,150)})}})},{threshold:[0,.6,1]});var obs=function(){sio.observe(st)};(d.fonts&&d.fonts.ready?d.fonts.ready.then(obs):obs())}
}

/* "What's going on?" picker */
var pk=d.querySelector('[data-picker]');
if(pk){
 var chips=pk.querySelectorAll('.chip'),panel=pk.querySelector('.answer'),answers=pk.querySelectorAll('.ans');
 chips.forEach(function(c){c.addEventListener('click',function(){
  var id=c.getAttribute('aria-controls');
  chips.forEach(function(o){o.setAttribute('aria-pressed',o===c?'true':'false')});
  answers.forEach(function(a){a.classList.toggle('is-on',a.id===id)});
  panel.classList.remove('is-answered');void panel.offsetWidth;panel.classList.add('is-answered');
  if(innerWidth<980){var r=panel.getBoundingClientRect();if(r.top>innerHeight*.6||r.top<0)panel.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'})}
 })});
}

/* reviews: show all */
var wall=d.querySelector('.rv-wall'),more=d.querySelector('[data-rv-more]');
if(wall&&more){wall.classList.add('is-clipped');more.hidden=false;more.addEventListener('click',function(){var open=wall.classList.toggle('is-clipped');more.setAttribute('aria-expanded',open?'false':'true');more.textContent=open?more.getAttribute('data-open'):more.getAttribute('data-close');if(!open){wall.querySelectorAll('.rv.is-extra').forEach(function(r){r.classList.add('is-in')})}})}
})();
