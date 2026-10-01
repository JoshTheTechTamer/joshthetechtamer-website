import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.xml':'application/xml'};
http.createServer((req,res)=>{let name;try{name=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);return res.end('Bad request')};if(name==='/')name='/index.html';const full=path.resolve(root,'.'+name);if(!full.startsWith(root+path.sep)||name.includes('/.')||name.startsWith('/scripts/')||name.startsWith('/backups/')){res.writeHead(403);return res.end('Forbidden')};fs.readFile(full,(err,data)=>{if(err){res.writeHead(404);return res.end('Not found')};res.writeHead(200,{'Content-Type':types[path.extname(full)]||'application/octet-stream','Cache-Control':'no-store'});res.end(data)})}).listen(4173,'0.0.0.0',()=>console.log('Preview ready'));
