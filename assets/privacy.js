/* Optional analytics: no Google Analytics request until the visitor opts in. */
(()=>{
 const KEY='tt-analytics-choice',ID='G-MTSTNDKSQH';
 const live=!window.TECH_TAMER_PREVIEW&&['joshthetechtamer.com','www.joshthetechtamer.com'].includes(location.hostname);
 let choice=null,loaded=false;
 try{choice=localStorage.getItem(KEY)}catch{}
 const box=document.createElement('section');box.className='privacy-choice';box.setAttribute('aria-label','Optional analytics');
 const inner=document.createElement('div');inner.className='wrap privacy-choice-inner';
 const text=document.createElement('p');text.textContent='May I use optional analytics to see which pages are helpful? Your choice won’t affect getting help. ';
 const link=document.createElement('a');link.href='/privacy';link.textContent='Privacy details';text.append(link);
 const actions=document.createElement('div');actions.className='privacy-actions';
 const allow=document.createElement('button'),deny=document.createElement('button');allow.type=deny.type='button';allow.textContent='Allow analytics';deny.textContent='No thanks';
 actions.append(allow,deny);inner.append(text,actions);box.append(inner);document.body.append(box);
 box.hidden=choice==='allow'||choice==='deny';
 function start(){
  if(!live||loaded)return;loaded=true;window['ga-disable-'+ID]=false;
  window.dataLayer=window.dataLayer||[];window.gtag=function(){window.dataLayer.push(arguments)};
  window.gtag('js',new Date());window.gtag('config',ID);
  const script=document.createElement('script');script.async=true;script.src='https://www.googletagmanager.com/gtag/js?id='+ID;document.head.append(script);
 }
 function clearCookies(){
  for(const entry of document.cookie.split(';')){const name=entry.split('=')[0].trim();if(!/^_ga(?:_|$)/.test(name))continue;
   for(const domain of ['',location.hostname,'.joshthetechtamer.com'])document.cookie=name+'=; Max-Age=0; path=/'+(domain?'; domain='+domain:'')+'; SameSite=Lax; Secure';
  }
 }
 function choose(value){choice=value;try{localStorage.setItem(KEY,value)}catch{};
  if(value==='allow'){window['ga-disable-'+ID]=false;start()}else{window['ga-disable-'+ID]=true;clearCookies()}
  box.hidden=true;if(lastTrigger){lastTrigger.focus();lastTrigger=null}
 }
 let lastTrigger;
 allow.addEventListener('click',()=>choose('allow'));deny.addEventListener('click',()=>choose('deny'));
 document.querySelectorAll('.privacy-settings').forEach(button=>button.addEventListener('click',()=>{lastTrigger=button;box.hidden=false;box.scrollIntoView({block:'nearest',behavior:'auto'});(choice==='allow'?allow:deny).focus()}));
 if(choice==='allow')start();else window['ga-disable-'+ID]=true;
})();
