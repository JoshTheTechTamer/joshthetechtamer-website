// Shared preview-gate page (Oct 20, 2026): restrained, matches joshthetechtamer.com.
// Same markup is inlined into the demo-* Workers (see /workspace/tpl/gate/build_gate.py).
export const GH=s=>String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
export function gatePage({name,action,next,error}){
const N=GH(name);
return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>${N} website preview | The Tech Tamer</title><link rel="icon" href="https://joshthetechtamer.com/favicon.ico"><style>@font-face{font-family:"Montserrat DS";font-style:normal;font-weight:900;font-display:swap;src:url(https://joshthetechtamer.com/assets/fonts/montserrat-900-latin.woff2) format("woff2")}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:flex;flex-direction:column;background:#f3f5f9;color:#202d4b;font:17px/1.6 Arial,Helvetica,sans-serif}
.top{background:#23335c;color:#fff;font-size:13px;letter-spacing:.025em;padding:7px 20px;text-align:center}.top a{color:#fff;text-decoration:none}
header{background:#fff;border-bottom:1px solid #dce2ed;padding:12px 20px}header a{display:inline-flex;align-items:center;gap:10px;color:#23335c;text-decoration:none;font-family:"Montserrat DS",Arial,Helvetica,sans-serif;font-weight:900;font-size:17px;letter-spacing:-.01em}header img{width:46px;height:auto}
.wrap{max-width:1000px;margin:0 auto}
main{flex:1;display:flex;align-items:flex-start;justify-content:center;padding:48px 18px}
.card{width:100%;max-width:440px;background:#fff;border:1px solid #dce2ed;border-radius:8px;padding:30px 28px}
h1{margin:0 0 10px;font-family:"Montserrat DS","Montserrat",Arial,Helvetica,sans-serif;font-weight:900;font-size:clamp(1.45rem,4.6vw,1.8rem);line-height:1.15;letter-spacing:-.02em;color:#23335c}
.lead{margin:0 0 22px;color:#56617a;font-size:16px}
label{display:block;font-weight:700;font-size:15px;margin:0 0 6px;color:#23335c}
input[type=password]{width:100%;font:inherit;font-size:17px;padding:12px 14px;border:1px solid #b9c3d6;border-radius:4px;background:#fff;color:#202d4b}
input[type=password]:focus{border-color:#00a3ed;outline:3px solid rgba(0,163,237,.25);outline-offset:0}
button{margin-top:14px;width:100%;min-height:50px;font:inherit;font-weight:700;font-size:15px;color:#fff;background:#23335c;border:1px solid #23335c;border-radius:4px;cursor:pointer}
button:hover{background:#424d7d}button:focus-visible,a:focus-visible{outline:3px solid #00a3ed;outline-offset:3px}
.err{margin:0 0 14px;color:#8a2f1f;font-size:15px}
.foot{margin:22px 0 0;font-size:15px;color:#56617a}.foot a{color:#23335c;font-weight:700;text-decoration:none}
footer{padding:18px 20px;text-align:center;font-size:13px;color:#56617a}footer a{color:#56617a}
@media (max-width:420px){main{padding:28px 14px}.card{padding:24px 20px}}</style></head><body><div class="top">Muscatine based. Proudly serving Eastern Iowa.</div><header><div class="wrap"><a href="https://joshthetechtamer.com/"><img src="https://joshthetechtamer.com/assets/optimized/hero-logo-400.webp" alt="" width="400" height="344">The Tech Tamer</a></div></header><main><div class="card"><h1>${N}</h1><p class="lead">This private website preview was built for ${N} by Josh Sargent, The Tech Tamer, Muscatine, IA.</p>${error?`<p class="err" role="alert">${GH(error)}</p>`:''}<form method="post" action="${GH(action)}"><input type="hidden" name="next" value="${GH(next)}"><label for="pw">Password (from Josh's email)</label><input id="pw" name="password" type="password" autocomplete="current-password" required autofocus><button type="submit">View preview</button></form><p class="foot">Questions? Call or text Josh at <a href="tel:+15632610200">563-261-0200</a>.</p></div></main><footer>&copy; The Tech Tamer LLC &middot; <a href="https://joshthetechtamer.com/">joshthetechtamer.com</a></footer></body></html>`;}
