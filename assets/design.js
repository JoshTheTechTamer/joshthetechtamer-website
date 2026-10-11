/* Shared design layer (Oct 2026): scroll reveal, self-drawing gold icons, gold-filling step timelines, card tilt/glow.
   Vanilla JS, no libraries. Without JS (or with reduced motion) every page is fully visible and still. */
(function(){
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

  /* 3) Step timelines: a gold line runs through the step numbers and fills as you scroll. */
  all('[data-ds-steps]').forEach(function(tl){
    var steps=all('.step',tl),nums=steps.map(function(s){return s.querySelector('.number');});
    if(steps.length<2||nums.indexOf(null)>-1)return;
    var track=d.createElement('span'),fill=d.createElement('span');
    track.className='ds-track';fill.className='ds-fill';track.setAttribute('aria-hidden','true');fill.setAttribute('aria-hidden','true');
    tl.insertBefore(fill,tl.firstChild);tl.insertBefore(track,tl.firstChild);
    var vertical=false;
    function layout(){
      var b=tl.getBoundingClientRect(),a=nums[0].getBoundingClientRect(),z=nums[nums.length-1].getBoundingClientRect();
      var ax=a.left+a.width/2-b.left,ay=a.top+a.height/2-b.top,zx=z.left+z.width/2-b.left,zy=z.top+z.height/2-b.top;
      vertical=Math.abs(zy-ay)>Math.abs(zx-ax);tl.classList.toggle('is-vertical',vertical);
      var t=5;
      if(vertical){tl.style.setProperty('--l',(ax-t/2)+'px');tl.style.setProperty('--t',ay+'px');tl.style.setProperty('--w',t+'px');tl.style.setProperty('--h',(zy-ay)+'px');}
      else{tl.style.setProperty('--l',ax+'px');tl.style.setProperty('--t',(ay-t/2)+'px');tl.style.setProperty('--w',(zx-ax)+'px');tl.style.setProperty('--h',t+'px');}
    }
    function paint(){
      var p=1;
      if(!reduce){
        var b=tl.getBoundingClientRect(),vh=w.innerHeight;
        p=vertical?(vh*.62-(b.top+nums[0].offsetHeight/2))/Math.max(1,b.height-nums[0].offsetHeight):(vh*.86-b.top)/(vh*.42);
        p=Math.max(0,Math.min(1,p));
      }
      tl.style.setProperty('--fill',p.toFixed(3));
      steps.forEach(function(s,i){if(p>=i/(steps.length-1)-.001)s.classList.add('is-on');else if(!reduce)s.classList.remove('is-on');});
    }
    layout();paint();
    var ticking=false;
    function onScroll(){if(!ticking){ticking=true;requestAnimationFrame(function(){ticking=false;paint();});}}
    if(!reduce){w.addEventListener('scroll',onScroll,{passive:true});}
    w.addEventListener('resize',function(){layout();paint();});
    w.addEventListener('load',function(){layout();paint();});
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
})();
