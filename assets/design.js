/* Shared design layer (Oct 2026): scroll reveal, self-drawing gold icons, gold-filling step timelines, card tilt/glow.
   Vanilla JS, no libraries. Without JS (or with reduced motion) every page is fully visible and still. */
(function(){var go=function(){
  var d=document,root=d.documentElement,w=window;
  var mm=function(q){return w.matchMedia&&w.matchMedia(q).matches;};
  var reduce=mm('(prefers-reduced-motion: reduce)');
  var fine=mm('(hover: hover) and (pointer: fine)');
  var hasIO='IntersectionObserver' in w;
  var all=function(sel,ctx){return [].slice.call((ctx||d).querySelectorAll(sel));};
  var icons=all('.icon');

  /* 1) Scroll reveal: section intros, cards, notices, FAQ groups, the map, CTA bands. Never inside the hero,
        the review carousel or a form. Blocks already on screen show at once (no flash). */
  var groups='main .section-head, main .home-paths-intro, main .grid3>*, main .grid2>*, main .price-layout>*, main .product-grid>*, main .notice, main .faq, main .area-map, main .story>*, main .about-tease>*, main .business-intro>*, main .contact-grid>*, main .cta .wrap>*, main .review-carousel, main .review-links, main .local-review-grid>*, main .home-local';
  var rv=all(groups).filter(function(el){return !el.closest('.ds-hero')&&!el.closest('form')&&!(el.parentElement&&el.parentElement.closest('.review-carousel'))&&!el.querySelector('form');});
  if(!reduce&&hasIO){
    rv.forEach(function(el){
      var sib=el.parentElement?[].indexOf.call(el.parentElement.children,el):0;
      el.classList.add('ds-rv');el.style.setProperty('--i',Math.min(sib,5));
      if(el.getBoundingClientRect().top<w.innerHeight*.92)el.classList.add('is-in');
    });
    root.classList.add('ds-anim');
    var settle=function(el){setTimeout(function(){el.style.removeProperty('--i');},1400);};
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-in');settle(e.target);io.unobserve(e.target);}});},{rootMargin:'0px 0px -8% 0px',threshold:.1});
    rv.forEach(function(el){if(el.classList.contains('is-in'))settle(el);else io.observe(el);});

    /* 2) Gold icons draw themselves in when they come into view. */
    var ico=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var el=e.target;requestAnimationFrame(function(){requestAnimationFrame(function(){el.classList.add('is-drawn');});});ico.unobserve(el);}});},{rootMargin:'0px 0px -10% 0px',threshold:.5});
    icons.forEach(function(el){ico.observe(el);});
  }else{icons.forEach(function(el){el.classList.add('is-drawn');});}

  /* 3) Step timelines: a twisted gold rope runs through the number circles (above the headings) and draws itself in
        when the steps scroll into view; each step lights up as the rope reaches it. */
  all('[data-ds-steps]').forEach(function(tl){
    var steps=all('.step',tl),nums=steps.map(function(s){return s.querySelector('.number');});
    if(steps.length<2||nums.indexOf(null)>-1)return;
    var rope=d.createElement('span');rope.className='ds-rope';rope.setAttribute('aria-hidden','true');
    tl.insertBefore(rope,tl.firstChild);tl.classList.add('has-rope');
    /* layout from offsets (not getBoundingClientRect) so reveal/scale transforms can't shift the rope off the circles */
    function at(el){var x=el.offsetWidth/2,y=el.offsetHeight/2;while(el&&el!==tl){x+=el.offsetLeft;y+=el.offsetTop;el=el.offsetParent;}return[x,y];}
    var pts=[];
    function layout(){
      pts=nums.map(at);var a=pts[0],z=pts[pts.length-1];
      var vertical=Math.abs(z[1]-a[1])>Math.abs(z[0]-a[0]),t=parseFloat(getComputedStyle(tl).getPropertyValue('--ds-rope'))||10;
      tl.classList.toggle('is-vertical',vertical);
      if(vertical){tl.style.setProperty('--l',(a[0]-t/2)+'px');tl.style.setProperty('--t',a[1]+'px');tl.style.setProperty('--w',t+'px');tl.style.setProperty('--h',(z[1]-a[1])+'px');}
      else{tl.style.setProperty('--l',a[0]+'px');tl.style.setProperty('--t',(a[1]-t/2)+'px');tl.style.setProperty('--w',(z[0]-a[0])+'px');tl.style.setProperty('--h',t+'px');}
      tl._v=vertical;
    }
    layout();
    w.addEventListener('load',layout);
    if(reduce||!hasIO){tl.style.setProperty('--fill','1');steps.forEach(function(s){s.classList.add('is-on');});w.addEventListener('resize',layout);return;}
    /* same behaviour as the Get a Website timeline: the rope draws through the numbers as you scroll,
       and each number lights up as the rope reaches it */
    tl.classList.add('ds-scroll');
    var ticking=false,active=false;
    function update(){
      ticking=false;
      var b=tl.getBoundingClientRect(),mid=w.innerHeight*.62,a=pts[0],z=pts[pts.length-1],ax=tl._v?a[1]:a[0],zx=tl._v?z[1]:z[0];
      var base=tl._v?b.top:b.left,pos=tl._v?mid-base:(mid-(b.top+a[1]))/(w.innerHeight*.35)*(zx-ax)+ax;
      var f=Math.max(0,Math.min(1,(pos-ax)/(zx-ax)));
      tl.style.setProperty('--fill',f.toFixed(4));
      steps.forEach(function(s,i){var p=tl._v?pts[i][1]:pts[i][0];s.classList.toggle('is-on',ax+f*(zx-ax)>=p-1);});
    }
    function onScroll(){if(active&&!ticking){ticking=true;w.requestAnimationFrame(update);}}
    new IntersectionObserver(function(es){active=es[0].isIntersecting;if(active)update();},{rootMargin:'200px 0px'}).observe(tl);
    w.addEventListener('scroll',onScroll,{passive:true});
    w.addEventListener('resize',function(){layout();onScroll();},{passive:true});
  });

  /* 4) Cards: subtle tilt + glow for mouse users only (no tilt on touch, none with reduced motion). */
  if(fine&&!reduce){
    all('.path-card, .service-card, .price-card, .product').forEach(function(card){
      if(card.closest('.review-carousel')||card.querySelector('form'))return;
      var glow=d.createElement('span');glow.className='ds-glow';glow.setAttribute('aria-hidden','true');card.appendChild(glow);
      card.classList.add('ds-tilt');
      var max=Math.max(1.2,Math.min(4,1100/card.offsetWidth));
      card.addEventListener('pointermove',function(e){
        if(e.pointerType!=='mouse')return;
        var r=card.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;
        card.classList.add('is-tilt');
        card.style.setProperty('--ry',((x-.5)*2*max).toFixed(2)+'deg');card.style.setProperty('--rx',((.5-y)*2*max).toFixed(2)+'deg');
        card.style.setProperty('--mx',(x*100).toFixed(1)+'%');card.style.setProperty('--my',(y*100).toFixed(1)+'%');
      });
      card.addEventListener('pointerleave',function(){card.classList.remove('is-tilt');card.style.setProperty('--rx','0deg');card.style.setProperty('--ry','0deg');});
    });
  }
};
  /* Off the critical path: run after first paint, in idle time (chunked away from input). */
  var start=function(){('requestIdleCallback' in window)?requestIdleCallback(go,{timeout:800}):setTimeout(go,120);};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){requestAnimationFrame(start);},{once:true});else requestAnimationFrame(start);
})();
