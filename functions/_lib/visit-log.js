// Preview visit log (Oct 20, 2026). Shared by joshthetechtamer.com/demos/* and the demo-* Workers.
// D1 binding VISITS (database tt-preview-visits). Secrets: OWNER_KEY (Josh's device link), IP_SALT, BOX_IPS.
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
const BOT_UA=/bot\b|bot\/|bot;|crawl|spider|slurp|GoogleImageProxy|Google-Safety|Google-Read-Aloud|googleweblight|FeedFetcher|Google-InspectionTool|curl|wget|python|httpx|aiohttp|go-http-client|java\/|okhttp|node-fetch|node\.js|axios|undici|libwww|scrapy|HeadlessChrome|Headless|PhantomJS|Puppeteer|Playwright|Lighthouse|PageSpeed|facebookexternalhit|facebookcatalog|Slackbot|Twitterbot|LinkedInBot|Discordbot|WhatsApp|TelegramBot|SkypeUriPreview|BingPreview|YahooMailProxy|Barracuda|Proofpoint|Mimecast|urlscan|scanner|validator|uptime|monitor|preview/i;
// Cloud / mail-security networks that fetch links on behalf of mail systems (not 13335: real people use WARP/Private Relay).
const BOT_ASN=new Set([15169,396982,19527,8075,16509,14618,14061,24940,16276,63949,20473,31898,26211,22843,30031,15324,45102,132203,51167,12876,9009,60068,212238,36352]);
export function deviceOf(ua){if(/iPad|Tablet|Kindle|Silk|PlayBook/i.test(ua)||(/Android/i.test(ua)&&!/Mobile/i.test(ua)))return 'tablet';if(/Mobi|iPhone|iPod|Android|Windows Phone/i.test(ua))return 'mobile';return 'desktop';}
export async function tagOf(env,req){
 const ip=req.headers.get('CF-Connecting-IP')||'';const ua=req.headers.get('User-Agent')||'';const asn=(req.cf&&req.cf.asn)||0;
 const box=String(env.BOX_IPS||'').split(',').map(s=>s.trim()).filter(Boolean);
 if(ip&&box.includes(ip))return 'bot';
 if(await isOwner(env,req))return 'josh';
 if(!ua||BOT_UA.test(ua)||BOT_ASN.has(asn))return 'bot';
 return 'prospect';}
export function isDocRequest(req,path){if(req.method!=='GET')return false;const dest=req.headers.get('Sec-Fetch-Dest');if(dest&&dest!=='document')return false;if(/\.[a-z0-9]{1,5}$/i.test(path)&&!/\.html?$/i.test(path))return false;const acc=req.headers.get('Accept')||'';return !dest?(acc.includes('text/html')||acc===''||acc==='*/*'):true;}
export function logVisit(env,ctx,req,slug,kind,path){
 if(!env.VISITS)return;
 const job=(async()=>{
  const ip=req.headers.get('CF-Connecting-IP')||'';const ua=(req.headers.get('User-Agent')||'').slice(0,300);const cf=req.cf||{};
  const tag=await tagOf(env,req);
  const iph=ip&&env.IP_SALT?(await vmac(env.IP_SALT,ip)).slice(0,12):null;
  await env.VISITS.prepare('INSERT INTO visits (ts,slug,kind,path,city,region,country,device,tag,iph,asn,ua) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)')
   .bind(new Date().toISOString(),slug,kind,String(path||'').slice(0,200),cf.city||null,cf.region||null,cf.country||null,tag==='bot'?'bot':deviceOf(ua),tag,iph,cf.asn||null,ua).run();
 })().catch(e=>console.log('visit log failed',String(e)));
 if(ctx&&ctx.waitUntil)ctx.waitUntil(job);}
