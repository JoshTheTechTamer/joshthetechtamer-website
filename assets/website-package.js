/* Website Package showcase: scroll reveal, gold-filling timeline, before/after slider, price-card tilt, phone auto-scroll.
   Vanilla JS, no libraries. Everything degrades to a static, fully visible page without JS or with reduced motion. */
(function(){
  var d=document,root=d.documentElement,w=window;
  var reduce=w.matchMedia&&w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine=w.matchMedia&&w.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var hasIO='IntersectionObserver' in w;

  /* 1) Scroll reveal. Blocks already on screen are shown at once (no flash); the rest fade/slide in. */
  var rv=[].slice.call(d.querySelectorAll('[data-rv]'));
  if(!reduce&&hasIO){
    rv.forEach(function(el){if(el.getBoundingClientRect().top<w.innerHeight*.92)el.classList.add('is-in');});
    root.classList.add('wp-anim');
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-in');io.unobserve(e.target);}});},{rootMargin:'0px 0px -8% 0px',threshold:.12});
    rv.forEach(function(el){if(!el.classList.contains('is-in'))io.observe(el);});
  }

  /* 2) Timeline: the gold line fills as you scroll; each step lights up when the line reaches it. */
  var tl=d.querySelector('[data-wp-timeline]');
  if(tl){
    var steps=[].slice.call(tl.querySelectorAll('[data-step]'));
    if(reduce||!hasIO){tl.style.setProperty('--fill','1');steps.forEach(function(s){s.classList.add('is-on','is-seen');});}
    else{
      root.classList.add('wp-tl-anim');
      var ticking=false,active=false;
      var update=function(){
        ticking=false;
        var r=tl.getBoundingClientRect(),mid=w.innerHeight*.62;
        var f=Math.max(0,Math.min(1,(mid-r.top)/r.height));
        tl.style.setProperty('--fill',f.toFixed(4));
        steps.forEach(function(s){var n=s.querySelector('.wp-step-num').getBoundingClientRect();var on=n.top+n.height/2<mid+1;s.classList.toggle('is-on',on);if(on)s.classList.add('is-seen');});
      };
      var onScroll=function(){if(active&&!ticking){ticking=true;w.requestAnimationFrame(update);}};
      new IntersectionObserver(function(es){active=es[0].isIntersecting;if(active)update();},{rootMargin:'200px 0px'}).observe(tl);
      w.addEventListener('scroll',onScroll,{passive:true});w.addEventListener('resize',onScroll,{passive:true});
      update();
    }
  }

  /* 3) Before/after slider. The native range input does the work (keyboard, touch, screen readers); we only paint. */
  [].forEach.call(d.querySelectorAll('[data-wp-ba]'),function(ba){
    var r=ba.querySelector('.wp-ba-range');if(!r)return;
    var paint=function(){var v=+r.value;ba.style.setProperty('--pos',v+'%');r.setAttribute('aria-valuetext',v+'% Facebook page, '+(100-v)+'% website');};
    r.addEventListener('input',paint);paint();ba.classList.add('is-ready');
  });

  /* 4) Price cards: subtle tilt and a glow that follows the mouse. Mouse/trackpad only, never on touch or reduced motion. */
  if(fine&&!reduce){
    [].forEach.call(d.querySelectorAll('[data-tilt]'),function(c){
      var g=d.createElement('span');g.className='wp-glow';g.setAttribute('aria-hidden','true');c.appendChild(g);
      var raf=0;
      c.addEventListener('pointermove',function(e){
        if(e.pointerType!=='mouse')return;
        cancelAnimationFrame(raf);raf=requestAnimationFrame(function(){
          var b=c.getBoundingClientRect(),x=(e.clientX-b.left)/b.width,y=(e.clientY-b.top)/b.height;
          c.style.setProperty('--rx',((.5-y)*5).toFixed(2)+'deg');c.style.setProperty('--ry',((x-.5)*6).toFixed(2)+'deg');
          c.style.setProperty('--mx',(x*100).toFixed(1)+'%');c.style.setProperty('--my',(y*100).toFixed(1)+'%');c.classList.add('is-tilt');
        });
      });
      c.addEventListener('pointerleave',function(){cancelAnimationFrame(raf);c.classList.remove('is-tilt');c.style.setProperty('--rx','0deg');c.style.setProperty('--ry','0deg');});
    });
  }

  /* 5) Phone mockup: after the page has loaded, swap in a tall homepage screenshot and let CSS scroll it.
        Paused off-screen and on demand (pause button), skipped entirely with reduced motion. */
  var scr=d.querySelector('.wp-phone-screen[data-tall-300]');
  if(scr&&!reduce){
    var start=function(){
      var src=(w.devicePixelRatio||1)*scr.clientWidth>300?scr.getAttribute('data-tall-450'):scr.getAttribute('data-tall-300');
      var img=new Image();img.alt='';img.decoding='async';img.className='wp-phone-tall';img.setAttribute('aria-hidden','true');
      img.onload=function(){
        scr.appendChild(img);scr.classList.add('is-scrolling');
        var btn=d.querySelector('.wp-phone-toggle');
        if(btn){btn.hidden=false;btn.addEventListener('click',function(){var p=scr.classList.toggle('is-paused');btn.setAttribute('aria-pressed',p?'true':'false');btn.querySelector('.sr-only').textContent=p?'Resume the phone preview scrolling':'Pause the phone preview scrolling';});}
        if(hasIO)new IntersectionObserver(function(es){scr.classList.toggle('is-offscreen',!es[0].isIntersecting);}).observe(scr);
      };
      img.src=src;
    };
    if(d.readyState==='complete')setTimeout(start,600);else w.addEventListener('load',function(){setTimeout(start,600);});
  }
})();
