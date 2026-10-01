const menu=document.querySelector('.menu'), nav=document.querySelector('.navlinks');
if(menu&&nav){menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);menu.textContent=open?'Close ✕':'Menu ☰'});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.textContent='Menu ☰';menu.focus()}})}
const form=document.querySelector('#request-form');
if(form){form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const data=new FormData(form),name=String(data.get('name')).trim(),issue=String(data.get('issue')).trim();if(!name||!issue){document.querySelector('#form-status').textContent='Please enter your name and a brief description.';return}const body=`Name: ${name}\nContact: ${data.get('contact')}\nHelp needed: ${data.get('service')}\nLocation: ${data.get('location')}\n\n${issue}`;const url='mailto:joshthetechtamer@gmail.com?subject='+encodeURIComponent('Tech Tamer consultation: '+data.get('service'))+'&body='+encodeURIComponent(body);window.location.href=url;document.querySelector('#form-status').textContent='Your email app should open with your request ready to review. Press Send there to contact Josh. If it did not open, call or text 563-261-0200.'})}
if(location.pathname.endsWith('/')||location.pathname.endsWith('index.html')){const old={services:'services.html',kits:'digital-kits.html',rates:'rates.html',about:'about.html',booking:'contact.html'};const dest=old[location.hash.slice(1)];if(dest)location.replace(dest)}
// Preserve existing measurement on the approved production domain only.
if(location.hostname==='joshthetechtamer.com'||location.hostname==='www.joshthetechtamer.com'){
 window.dataLayer=window.dataLayer||[];
 window.gtag=function(){window.dataLayer.push(arguments)};
 window.gtag('js',new Date());window.gtag('config','G-MTSTNDKSQH');
 const analytics=document.createElement('script');analytics.async=true;analytics.src='https://www.googletagmanager.com/gtag/js?id=G-MTSTNDKSQH';document.head.append(analytics);
 document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href')||'';const event=href.startsWith('sms:')?'sms_click':href.startsWith('tel:')?'call_click':href.includes('gumroad.com')?'kit_click':null;if(event)window.gtag('event',event,{page:location.pathname,cta:a.textContent.trim()})});
}
