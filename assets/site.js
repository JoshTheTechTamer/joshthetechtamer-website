const menu=document.querySelector('.menu'),nav=document.querySelector('.navlinks');
if(menu&&nav){menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);menu.textContent=open?'Close ✕':'Menu ☰'});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.textContent='Menu ☰';menu.focus()}})}
const preview=window.TECH_TAMER_PREVIEW===true;
function track(event,params={}){if(!preview&&typeof window.gtag==='function')window.gtag('event',event,params)}
const form=document.querySelector('#request-form');
if(form){
 const reply=form.querySelector('#reply'),contact=form.querySelector('#contact'),service=form.querySelector('#service'),status=form.querySelector('#form-status'),button=form.querySelector('[type="submit"]');
 function replyType(){const email=reply.value==='email';contact.type=email?'email':'tel';contact.autocomplete=email?'email':'tel';contact.inputMode=email?'email':'tel';form.querySelector('label[for="contact"]').textContent=email?'Email address *':'Phone number *'}
 reply.addEventListener('change',replyType);replyType();
 const requested=new URLSearchParams(window.TECH_TAMER_QUERY||location.search).get('service');if(requested&&Array.from(service.options).some(o=>o.value===requested))service.value=requested;
 form.addEventListener('submit',e=>{
  e.preventDefault();if(!form.reportValidity())return;
  const data=new FormData(form);status.className='status';
  const value=key=>String(data.get(key)||'').trim();
  if(!value('name')||!value('issue')){status.textContent='Please enter your name and a brief description.';return}
  if(value('_gotcha')){status.textContent='Please call or text Josh to arrange help.';return}
  if(reply.value!=='email'&&value('contact').replace(/\D/g,'').length<10){status.textContent='Please enter a phone number with area code.';contact.focus();return}
  const subject=`Tech Tamer request: ${value('service')} — ${value('name')}`;
  const replyLabel={text:'Text message',phone:'Phone call',email:'Email'}[reply.value];
  const body=[`Name: ${value('name')}`,`Service: ${value('service')}`,`Reply by: ${replyLabel}`,`Contact: ${value('contact')}`,`City / service location: ${value('location')||'Not specified'}`,`Good times to reach me: ${value('preferred_time')||'Not specified'}`,'','Request:',value('issue')].join('\r\n');
  const email='mailto:joshthetechtamer@gmail.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
  status.textContent='Your email app will open with your request filled in. Review it and press Send there. If it does not open, email joshthetechtamer@gmail.com or call/text 563-261-0200. Your details remain here.';
  track('email_draft_open',{placement:'contact_form',service:service.value});
  window.location.href=email;
 });
}
const carousel=document.querySelector('.review-carousel');
if(carousel){
 const cards=Array.from(carousel.querySelectorAll('.review-card')),controls=carousel.querySelector('.review-controls'),count=carousel.querySelector('.review-count'),pause=carousel.querySelector('[data-review="pause"]');
 let index=0,paused=matchMedia('(prefers-reduced-motion: reduce)').matches,hovered=false,timer;
 carousel.classList.add('is-enhanced');controls.hidden=false;
 function show(n,automatic=false){index=(n+cards.length)%cards.length;cards.forEach((c,i)=>c.hidden=i!==index);count.setAttribute('aria-live',automatic?'off':'polite');count.textContent=`${index+1} / ${cards.length}`}
 function schedule(){clearInterval(timer);pause.textContent=paused?'Play rotation':'Pause rotation';if(!paused&&!hovered&&!document.hidden)timer=setInterval(()=>show(index+1,true),10000)}
 controls.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const action=b.dataset.review;if(action==='pause')paused=!paused;else{paused=true;show(index+(action==='next'?1:-1))}schedule()});
 carousel.addEventListener('mouseenter',()=>{hovered=true;schedule()});carousel.addEventListener('mouseleave',()=>{hovered=false;schedule()});
 carousel.addEventListener('focusin',()=>{paused=true;schedule()});document.addEventListener('visibilitychange',schedule);show(0);schedule();
}
if(!preview&&(location.pathname.endsWith('/')||location.pathname.endsWith('index.html'))){const old={services:'/services.html',kits:'/digital-kits.html',rates:'/rates.html',about:'/about.html',booking:'/contact.html'};const dest=old[location.hash.slice(1)];if(dest)location.replace(dest)}
if(!preview&&(location.hostname==='joshthetechtamer.com'||location.hostname==='www.joshthetechtamer.com')){
 window.dataLayer=window.dataLayer||[];window.gtag=function(){window.dataLayer.push(arguments)};
 window.gtag('js',new Date());window.gtag('config','G-MTSTNDKSQH');
 const analytics=document.createElement('script');analytics.async=true;analytics.src='https://www.googletagmanager.com/gtag/js?id=G-MTSTNDKSQH';document.head.append(analytics);
 document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href')||'';const event=href.startsWith('sms:')?'sms_click':href.startsWith('tel:')?'call_click':href.startsWith('mailto:')?'email_click':href.includes('gumroad.com')?'kit_click':null;
 if(event){const region=a.closest('header,footer,section,.mobile-contact,.ribbon');track(event,{page:location.pathname,cta:a.textContent.trim(),placement:region?(region.id||region.className||region.tagName.toLowerCase()):'other',kit:href.includes('gumroad.com')?href.split('/l/')[1]?.split('?')[0]:undefined})}});
}
