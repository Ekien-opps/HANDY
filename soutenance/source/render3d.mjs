// usage: node render3d.mjs jobs.json outdir   (jobs: [{id,key,ax,ay,az}])
import {chromium} from 'playwright-core'; import fs from 'fs'; import http from 'http'; import path from 'path';
const [,,jobsFile,outDir]=process.argv; const www='/tmp/claude-0/-home-user-HANDY/36455e3e-c271-5390-ad89-57cd94b34b42/scratchpad/build/www';
const types={'.html':'text/html','.js':'text/javascript','.glb':'model/gltf-binary'};
const srv=http.createServer((q,r)=>{const f=www+decodeURIComponent(q.url.split('?')[0]); if(!fs.existsSync(f)){r.writeHead(404);return r.end();} r.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'}); fs.createReadStream(f).pipe(r);}).listen(8765);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage(); p.on('console',m=>console.log('page:',m.text()));
await p.goto('http://127.0.0.1:8765/render.html'); await p.waitForFunction('window.ready===true');
const jobs=JSON.parse(fs.readFileSync(jobsFile)); const res={}; fs.mkdirSync(outDir,{recursive:true});
for(const j of jobs){ const r=await p.evaluate(j=>window.renderJob(j),j);
  fs.writeFileSync(`${outDir}/${j.id}.png`,Buffer.from(r.png.split(',')[1],'base64')); delete r.png; res[j.id]=r; }
fs.writeFileSync(`${outDir}/meta.json`,JSON.stringify(res,null,1)); await b.close(); srv.close(); console.log('done',jobs.length);
