const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROMIUM||undefined}).catch(()=>chromium.launch());
const p=await b.newPage({viewport:{width:400,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+require('path').resolve(process.argv[2]||'build/site.html')+'');
console.log('pool',await p.textContent('#poolCt'));
await p.click('[data-p=mid]');console.log('mid',await p.textContent('#poolCt'));
await p.selectOption('#nq','20');await p.click('#startBtn');
for(let i=0;i<20;i++){await p.click('#qchoices [data-i="0"]');await p.click('#nextBtn');}
console.log(await p.textContent('#rScore'));
await p.screenshot({path:'./build/r.png',fullPage:false});
const w=await p.evaluate(()=>document.documentElement.scrollWidth);console.log('width',w,'errs',errs);
await b.close();})();
