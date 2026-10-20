// Preview visit log (Oct 20, 2026). Shared by joshthetechtamer.com/demos/* and the demo-* Workers.
// D1 binding VISITS (database tt-preview-visits). Secrets: OWNER_KEY (Josh's device link), IP_SALT, BOX_IPS, QA_KEY (box test marker).
// Tags: qa (X-TT-QA header or tt_qa cookie = QA_KEY, or the fake test owner cookie), josh (real owner cookie), bot, prospect.
// No full IPs are stored: iph is a short salted hash for grouping only.
const VE=new TextEncoder();
const vb64=b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
async function vmac(k,m){const key=await crypto.subtle.importKey('raw',VE.encode(k),{name:'HMAC',hash:'SHA-256'},false,['sign']);return vb64(await crypto.subtle.sign('HMAC',key,VE.encode(m)));}
function veq(a,b){a=String(a);b=String(b);let d=a.length^b.length;for(let i=0;i<Math.max(a.length,b.length);i++)d|=(a.charCodeAt(i)||0)^(b.charCodeAt(i)||0);return d===0;}
export const OWNER_COOKIE='tt_owner';
export const OWNER_MAX_AGE=60*60*24*400;
export const DEMO_SLUGS=['bamamama','coffeebelt','decades','elolmito','hawknest','lemon','megsvintage','osaka','packnship','riotsrebelles','sellsauto','shafferauto','sunsetview','tresses'];
export function readCookieValue(req,name){for(const p of(req.headers.get('Cookie')||'').split(';')){const[k,...v]=p.trim().split('=');if(k===name)return decodeURIComponent(v.join('='));}return null;}
export async function ownerValue(env){return env.OWNER_KEY?vmac(env.OWNER_KEY,'tt-owner-v1'):null;}
export async function isOwner(env,req){const want=await ownerValue(env);const got=readCookieValue(req,OWNER_COOKIE);return !!(want&&got&&veq(want,got));}
export function ownerKeyOk(env,k){return !!(env.OWNER_KEY&&k&&veq(k,env.OWNER_KEY));}
export function ownerCookie(v){return `${OWNER_COOKIE}=${encodeURIComponent(v)}; Path=/; Max-Age=${OWNER_MAX_AGE}; HttpOnly; Secure; SameSite=Lax`;}
// On joshthetechtamer.com the owner cookie is set for the whole domain so <slug>.joshthetechtamer.com previews see it too.
export function ownerCookieSiteWide(v){return `${OWNER_COOKIE}=${encodeURIComponent(v)}; Domain=joshthetechtamer.com; Path=/; Max-Age=${OWNER_MAX_AGE}; HttpOnly; Secure; SameSite=Lax`;}
const BOT_UA=/bot\b|bot\/|bot;|crawl|spider|slurp|GoogleImageProxy|Google-Safety|Google-Read-Aloud|googleweblight|FeedFetcher|Google-InspectionTool|curl|wget|python|httpx|aiohttp|go-http-client|java\/|okhttp|node-fetch|node\.js|axios|undici|libwww|scrapy|HeadlessChrome|Headless|PhantomJS|Puppeteer|Playwright|Lighthouse|PageSpeed|facebookexternalhit|facebookcatalog|Slackbot|Twitterbot|LinkedInBot|Discordbot|WhatsApp|TelegramBot|SkypeUriPreview|BingPreview|YahooMailProxy|Barracuda|Proofpoint|Mimecast|urlscan|scanner|validator|uptime|monitor|preview/i;
// Cloud / mail-security networks that fetch links on behalf of mail systems (not 13335 by itself: real people use WARP/Private Relay).
const BOT_ASN=new Set([15169,396982,19527,8075,16509,14618,14061,24940,16276,63949,20473,31898,26211,22843,30031,15324,45102,132203,51167,12876,9009,60068,212238,36352,202412,403005,218785,210976,216071,8881]);
// Vulnerability-scanner networks seen right after the new certificates (Oct 20, 2026).
const SCANNER_ASN=new Set([46261,963,47007,18779]);
// Probe paths no preview ever serves.
const PROBE_PATH=/\.(env|php\d?|asp|aspx|jsp|cgi|sql|bak|old|ini|log|ya?ml|git|svn|DS_Store)(\b|$)|\/\.|wp-|xmlrpc|cgi-bin|\/api\/|\/admin|phpmyadmin|actuator|\/vendor\/|\/config|\/server-status|\/\//i;
function v6InRange(ip,prefix,bits){ // simple hex-prefix check for 2a09:bac0::/29 style ranges
 const ex=s=>{const [h,t]=s.split('::');const a=h?h.split(':'):[];const b=t!==undefined?(t?t.split(':'):[]):[];const z=Array(8-a.length-b.length).fill('0');return [...a,...z,...b].map(x=>parseInt(x||'0',16));};
 if(!ip.includes(':'))return false;const A=ex(ip.toLowerCase()),P=ex(prefix);let left=bits;for(let i=0;i<8&&left>0;i++){const take=Math.min(16,left);const mask=(0xffff<<(16-take))&0xffff;if((A[i]&mask)!==(P[i]&mask))return false;left-=take;}return true;}
export function deviceOf(ua){if(/iPad|Tablet|Kindle|Silk|PlayBook/i.test(ua)||(/Android/i.test(ua)&&!/Mobile/i.test(ua)))return 'tablet';if(/Mobi|iPhone|iPod|Android|Windows Phone/i.test(ua))return 'mobile';return 'desktop';}
export async function qaMatch(env,req){if(!env.QA_KEY)return false;const h=req.headers.get('X-TT-QA');const c=readCookieValue(req,'tt_qa');return veq(h||'',env.QA_KEY)||veq(c||'',env.QA_KEY);}
export async function fakeOwnerValue(env){return env.QA_KEY?vmac(env.QA_KEY,'tt-owner-test-v1'):null;}
/** Returns {tag, rule}. Order: qa, josh, bot rules (combined signals), prospect. opts.realPath=false marks a path the demo doesn't serve. */
export async function tagOf(env,req,opts={}){
 const ip=req.headers.get('CF-Connecting-IP')||'';const ua=req.headers.get('User-Agent')||'';const cf=req.cf||{};const asn=cf.asn||0;const colo=cf.colo||'';
 const path=new URL(req.url).pathname;
 if(await qaMatch(env,req))return{tag:'qa',rule:'qa-marker'};
 const ownerCk=readCookieValue(req,OWNER_COOKIE);
 if(ownerCk){const fake=await fakeOwnerValue(env);if(fake&&veq(fake,ownerCk))return{tag:'qa',rule:'owner-test(josh-path)'};}
 if(await isOwner(env,req))return{tag:'josh',rule:'owner-cookie'};
 if(opts.realPath===false||PROBE_PATH.test(path))return{tag:'bot',rule:'bad-path'};
 if(!ua.trim())return{tag:'bot',rule:'empty-ua'};
 if(BOT_UA.test(ua))return{tag:'bot',rule:'bot-ua'};
 // Box egress: Cloudflare WARP from the box's Ashburn exit, geolocated to Fort Worth. Requires AS13335 + IAD colo + (box range or Fort Worth geo),
 // so ordinary WARP / iCloud Private Relay users (who exit near home) are not caught.
 const box=String(env.BOX_IPS||'').split(',').map(s=>s.trim()).filter(Boolean);
 const boxRange=ip.startsWith('104.28.197.')||v6InRange(ip,'2a09:bac0::',29)||box.some(e=>{const[pat,c]=e.split('@');if(c&&c!==colo)return false;return pat.endsWith('*')?ip.toLowerCase().startsWith(pat.slice(0,-1).toLowerCase()):ip===pat;});
 const fortWorth=cf.city==='Fort Worth'&&cf.region==='Texas';
 if(asn===13335&&colo==='IAD'&&(boxRange||fortWorth))return{tag:'bot',rule:'box-egress'};
 if(box.includes(ip))return{tag:'bot',rule:'box-ip'};
 if(asn===13335&&/Windows NT/.test(ua)&&/Chrome\/119\./.test(ua))return{tag:'bot',rule:'monitor-chrome119-warp'};
 if(SCANNER_ASN.has(asn))return{tag:'bot',rule:'scanner-asn'};
 if(BOT_ASN.has(asn))return{tag:'bot',rule:'cloud-asn'};
 const lang=req.headers.get('Accept-Language');
 if(!lang)return{tag:'bot',rule:'no-accept-language'};
 if(asn===3356&&cf.country!=='US')return{tag:'bot',rule:'scanner-asn-3356'};
 return{tag:'prospect',rule:'browser'};}
export function isDocRequest(req,path){if(req.method!=='GET')return false;const dest=req.headers.get('Sec-Fetch-Dest');if(dest&&dest!=='document')return false;if(/\.[a-z0-9]{1,5}$/i.test(path)&&!/\.html?$/i.test(path))return false;const acc=req.headers.get('Accept')||'';return !dest?(acc.includes('text/html')||acc===''||acc==='*/*'):true;}
export function logVisit(env,ctx,req,slug,kind,path,opts={}){
 if(!env.VISITS)return;
 const job=(async()=>{
  const ip=req.headers.get('CF-Connecting-IP')||'';const ua=(req.headers.get('User-Agent')||'').slice(0,300);const cf=req.cf||{};
  let {tag,rule}=await tagOf(env,req,opts);
  const site=opts.site||'preview'; if(site==='tt'&&tag==='prospect')tag='visitor';
  let refHost=null;try{const r=req.headers.get('Referer');if(r){const h=new URL(r).hostname;refHost=h;}}catch{}
  let utm=null;try{utm=new URL(req.url).searchParams.get('utm_source');}catch{}
  const iph=ip&&env.IP_SALT?(await vmac(env.IP_SALT,ip)).slice(0,12):null;
  await env.VISITS.prepare('INSERT INTO visits (ts,slug,kind,path,city,region,country,device,tag,iph,asn,ua,colo,rule,site,referrer,utm) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
   .bind(new Date().toISOString(),slug,kind,String(path||'').slice(0,200),cf.city||null,cf.region||null,cf.country||null,tag==='bot'?'bot':deviceOf(ua),tag,iph,cf.asn||null,ua,cf.colo||null,rule,site,refHost?refHost.slice(0,120):null,utm?String(utm).slice(0,60):null).run();
 })().catch(e=>console.log('visit log failed',String(e)));
 if(ctx&&ctx.waitUntil)ctx.waitUntil(job);}
