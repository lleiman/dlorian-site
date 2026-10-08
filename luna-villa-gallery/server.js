const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.resolve(__dirname);
const TYPES = {'.html':'text/html; charset=utf-8','.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.json':'application/json; charset=utf-8','.txt':'text/plain; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8'};
http.createServer((req,res)=>{
 let url;
 try {url = new URL(req.url,'http://localhost');} catch {res.writeHead(400).end();return}
 let reqPath = decodeURIComponent(url.pathname);
 if (reqPath==='/' || reqPath==='/index.html') reqPath='/index.html';
 const full=path.resolve(ROOT,'.'+reqPath);
 if(!(full===ROOT || full.startsWith(ROOT+path.sep))){res.writeHead(403).end();return}
 fs.stat(full,(err,stat)=>{
  if(err || !stat.isFile()){res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'}).end('Not found');return}
  const type=TYPES[path.extname(full).toLowerCase()]||'application/octet-stream';
  const cache=full.endsWith('index.html')?'public, max-age=300':'public, max-age=86400';
  res.writeHead(200,{'Content-Type':type,'Content-Length':stat.size,'Cache-Control':cache,'X-Content-Type-Options':'nosniff'});
  fs.createReadStream(full).pipe(res);
 });
}).listen(Number(process.env.PORT||3000),'0.0.0.0');
