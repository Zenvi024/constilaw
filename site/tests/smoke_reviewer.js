const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROMIUM||undefined}).catch(()=>chromium.launch());
for (const vp of [{width:1280,height:900},{width:400,height:900}]){
const p=await b.newPage({viewport:vp});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+require('path').resolve(process.argv[2]||'build/site.html')+'');
await p.click('#tabRev');
await p.screenshot({path:`./build/rev${vp.width}.png`});
await p.fill('#rq','Cantor'); await p.waitForTimeout(500);
console.log(vp.width,'results',await p.$$eval('#rresults .res',x=>x.length));
await p.click('#rresults .res'); await p.waitForTimeout(300);
await p.screenshot({path:`./build/rev${vp.width}b.png`});
console.log('scrollW',await p.evaluate(()=>document.documentElement.scrollWidth),'errs',errs);
await p.close();}
await b.close();})();
