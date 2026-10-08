const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROMIUM||undefined}).catch(()=>chromium.launch());
const p=await b.newPage({viewport:{width:400,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+require('path').resolve(process.argv[2]||'build/site.html')+'');
await p.click('#tabDrill'); console.log(await p.textContent('#dstats'));
await p.click('.dpre[data-p=mid]'); await p.click('#dstart');
for(let i=0;i<12;i++){
  const tag=await p.textContent('#dtags');
  if(await p.$('#czIn')){await p.fill('#czIn','five');await p.click('#czCheck');}
  else if(await p.$('#tk')){await p.click('#tk button');}
  else if(await p.$('#gIn')){await p.fill('#gIn','5');await p.click('#gChk');}
  else {await p.click('#dbody .choice');}
  const r=await p.$$eval('#drate button',x=>x.map(y=>y.textContent));
  if(i<4)console.log(tag.slice(0,40),'|',r.join(' / '));
  await p.click('#drate button');
}
await p.screenshot({path:'./build/d1.png'});
await p.click('#dend'); console.log(await p.textContent('#ddoneTxt'));
await p.click('[data-m=spot]'); await p.click('#dstart'); await p.click('#tk button:nth-child(3)'); await p.screenshot({path:'./build/d2.png'});
await p.click('#dend');await p.click('[data-m=grids]'); await p.click('#gCheck'); console.log('grid',await p.textContent('#gScore'));
await p.screenshot({path:'./build/d3.png'});
console.log('badge',await p.textContent('#tabDrill'),'w',await p.evaluate(()=>document.documentElement.scrollWidth),'errs',errs);
await b.close();})();
