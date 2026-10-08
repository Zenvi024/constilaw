// Smoke test: node site/tests/smoke.js [path-to-html] [screenshot-dir]
const {chromium} = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
const out = process.argv[3] || 'site/build';
require('fs').mkdirSync(out, {recursive: true});
(async () => {
  const b = await chromium.launch();
  let fail = 0;
  for (const scheme of ['light', 'dark']) for (const vp of [{width: 1280, height: 900}, {width: 400, height: 860}]) {
    const p = await b.newPage({viewport: vp, colorScheme: scheme});
    const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error' && !/fonts\.g/.test(m.text())) errs.push(m.text()); });
    await p.goto('file://' + file);
    const tag = `${scheme}-${vp.width}`;
    const sw = async () => p.evaluate(() => document.documentElement.scrollWidth);
    const check = async (name) => { const w = await sw(); if (w > vp.width + 1){ fail++; console.log(`  OVERFLOW ${tag} ${name}: ${w}`); } };
    await p.screenshot({path: `${out}/${tag}-today.png`}); await check('today');
    // rule maps + search + case modal
    await p.click('[data-tab="rules"]'); await check('rules');
    await p.fill('#rq', 'ABAKADA'); await p.waitForTimeout(400);
    const hits = await p.$$eval('#rresults .res', x => x.length);
    await p.click('#rresults .res'); await p.waitForTimeout(200);
    await p.evaluate(() => { const i=[...document.querySelectorAll('#rcontent section.rv')].findIndex(s=>s.id==='powers'); const s=document.getElementById('rsel'); s.value=i; s.dispatchEvent(new Event('change')); });
    await p.click('#rcontent section.rv:not([hidden]) a.cref'); await p.waitForTimeout(100);
    const modal = await p.isVisible('#scrim'); await p.screenshot({path: `${out}/${tag}-modal.png`});
    await p.keyboard.press('Escape');
    await p.screenshot({path: `${out}/${tag}-rules.png`});
    // cases browse + drill (all three directions)
    await p.click('[data-tab="cases"]'); await p.fill('#cq', 'foundling'); await p.waitForTimeout(100);
    const cn = await p.$$eval('#clist .crow', x => x.length); await check('cases');
    await p.click('[data-cm="drill"]'); await p.click('#dStart'); await p.click('#dFlip'); await p.click('.grade [data-g="2"]');
    await p.click('#dQuit'); await p.click('#dBack');
    await p.click('[data-d="fc"]'); await p.click('#dStart'); await p.click('#dCard .choice'); const fb = await p.isVisible('#dNext');
    await p.screenshot({path: `${out}/${tag}-drill.png`}); await check('drill');
    await p.click('#dQuit'); await p.click('#dBack'); await p.click('[data-d="rc"]'); await p.click('#dStart'); await p.click('#dCard .choice');
    // past exams: mcq
    await p.click('[data-tab="exams"]'); await p.click('#qStart'); await p.click('#qBox .choice'); const expl = await p.isVisible('#qBox .expl');
    await p.screenshot({path: `${out}/${tag}-mcq.png`}); await check('mcq');
    await p.click('#qBox .qnext'); await p.click('#qEnd');
    await p.click('[data-em="essay"]'); await p.click('#elist [data-show]'); await check('essays');
    await p.screenshot({path: `${out}/${tag}-essays.png`});
    // spotter
    await p.click('#elist [data-spot]'); await p.click('#spGroups .iitem'); await p.click('#spCheck');
    const spr = await p.isVisible('#spResult'); await p.screenshot({path: `${out}/${tag}-spot.png`}); await check('spot');
    // trainer
    await p.click('#spResult [data-essay]'); await p.fill('#pad', 'Yes. The expulsion is void. '.repeat(25)); await p.click('#tGo'); await p.waitForTimeout(1100);
    const tt = await p.textContent('#tT'); await p.click('#wReveal'); await p.click('#rub label'); await p.click('#rbSave');
    const wn = await p.textContent('#wcN'); await p.screenshot({path: `${out}/${tag}-write.png`, fullPage: false}); await check('write');
    // printables + today again
    await p.click('[data-tab="print"]'); await p.screenshot({path: `${out}/${tag}-print.png`, fullPage: true}); await check('print');
    await p.click('[data-tab="today"]'); await p.click('#week [data-day="2026-10-11"]'); await p.screenshot({path: `${out}/${tag}-today2.png`}); await check('today2');
    console.log(`${tag}: search=${hits} modal=${modal} cases=${cn} drillfb=${fb} mcq=${expl} spot=${spr} timer=${tt} words=${wn} errors=${JSON.stringify(errs)}`);
    if (errs.length || !modal || !hits || !expl || !spr || !fb) fail++;
    await p.close();
  }
  await b.close();
  console.log(fail ? `FAIL (${fail})` : 'PASS');
  process.exit(fail ? 1 : 0);
})();
