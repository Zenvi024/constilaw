// node site/tests/features.js [built-html] [outdir]: session, fix list, lists drill, blur mode and sticky headings
const {chromium} = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
const out = process.argv[3] || 'site/build';
require('fs').mkdirSync(out, {recursive: true});
(async () => {
  const b = await chromium.launch(); let fail = 0;
  for (const vp of [{width: 1280, height: 900}, {width: 400, height: 860}]) {
    const p = await b.newPage({viewport: vp}); const tag = vp.width;
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + file + '#today'); await p.waitForTimeout(300);
    const over = async n => { const w = await p.evaluate(() => document.documentElement.scrollWidth); if (w > vp.width + 1){ fail++; console.log(`  OVERFLOW ${tag} ${n}: ${w}`); } };
    // answer whatever card is showing; miss on purpose every other card
    const answer = async (box, k) => {
      const miss = k % 2 === 0;
      if (await p.isVisible(`${box} [data-flip]`)) { await p.click(`${box} [data-flip]`); await p.waitForSelector(`${box} .card-face .grade, ${box} .litem, ${box} .choice`, {timeout: 2000}).catch(() => {}); }
      if (await p.isVisible(`${box} .grade`)) { await p.click(`${box} .grade [data-g="${miss ? 0 : 2}"]`); return; }
      if (await p.isVisible(`${box} [data-ok]`)) { await p.click(`${box} [data-ok="${miss ? 0 : 1}"]`); return; }
      if (await p.isVisible(`${box} .litem`)) {
        await p.click(`${box} [data-all]`); if (miss) await p.click(`${box} .litem >> nth=0`), await p.click(`${box} .litem >> nth=0`);
        await p.click(`${box} [data-done]`); await p.click(`${box} [data-next]`); return;
      }
      if (await p.isVisible(`${box} .choice`)) { await p.click(`${box} .choice >> nth=${miss ? 3 : 0}`).catch(() => p.click(`${box} .choice >> nth=0`)); await p.click(`${box} [data-next], ${box} .qnext`); return; }
      throw new Error('unknown card in ' + box);
    };
    const plan = await p.textContent('#sessPlan');
    await p.click('#sessGo'); const kinds = new Set();
    for (let k = 0; k < 40; k++) {
      if (await p.isVisible('#sessRun .score')) break;
      const lbl = await p.textContent('#sessRun .lbl'); kinds.add(lbl.split('·').pop().trim());
      if (k === 1) { await p.screenshot({path: `${out}/f-${tag}-session.png`}); await over('session'); }
      await answer('#sessRun', k);
    }
    const ended = await p.isVisible('#sessRun .score');
    await p.click('#sessRun [data-a="back"]');
    const fixN = +(await p.textContent('#fixN'));
    await p.screenshot({path: `${out}/f-${tag}-today.png`, fullPage: true}); await over('today');
    await p.click('#fixGo'); const fixCard = await p.isVisible('#sessRun .card-face');
    await p.click('#sessRun [data-quit]'); await p.click('#sessRun [data-a="back"]');
    // lists
    await p.click('[data-tab="lists"]'); const nl = await p.$$eval('#lList details', x => x.length);
    await p.click('#lList details >> nth=0'); await over('lists');
    await p.click('#lStart'); await p.click('#lRun .litem >> nth=0');
    await p.screenshot({path: `${out}/f-${tag}-listcard.png`}); await over('listcard');
    await p.click('#lRun [data-done]'); await p.click('#lRun .litem >> nth=1'); await p.click('#lRun .litem >> nth=1');
    await p.click('#lRun [data-done]'); const lverdict = await p.textContent('#lRun .verdict');
    await p.click('#lRun [data-quit]'); await p.click('#lRun [data-a="back"]');
    // rule maps: blur + sticky toc
    await p.click('[data-tab="rules"]'); await p.click('#blurBtn');
    const bl = await p.evaluate(() => { const s = [...document.querySelectorAll('#rcontent section.rv')].find(x => !x.hidden); const els = s.querySelectorAll('.bl'); const c = getComputedStyle(els[0]).color; return {n: els.length, nums: s.querySelectorAll('.num').length, transparent: c === 'rgba(0, 0, 0, 0)'}; });
    const ct1 = await p.textContent('#blurCt');
    await p.evaluate(() => { const s = [...document.querySelectorAll('#rcontent section.rv')].find(x => !x.hidden); const e = s.querySelector('.bl:not(.shown)'); e.scrollIntoView({block: 'center'}); });
    await p.click('#rcontent section.rv:not([hidden]) .bl:not(.shown) >> nth=0'); const ct2 = await p.textContent('#blurCt'); const modalOpen = await p.isVisible('#scrim');
    const chips = await p.$$eval('#mtoc a', x => x.length);
    await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2)); await p.waitForTimeout(250);
    const cur = await p.$$eval('#mtoc a[aria-current="true"]', x => x.map(a => a.textContent));
    const stuck = await p.evaluate(() => document.getElementById('rstick').getBoundingClientRect().top);
    await p.screenshot({path: `${out}/f-${tag}-blur.png`}); await over('blur');
    await p.click('#mtoc a >> nth=1'); await p.waitForTimeout(200);
    const hTop = await p.evaluate(() => { const id = document.querySelectorAll('#mtoc a')[1].dataset.h; return Math.round(document.getElementById(id).getBoundingClientRect().top); });
    await p.click('#blurBtn');
    console.log(`${tag}: plan="${plan}" ended=${ended} kinds=${[...kinds].join('/')} fix=${fixN} fixCard=${fixCard} lists=${nl} listVerdict="${lverdict}" blur=${JSON.stringify(bl)} ct=${ct1}->${ct2} modalOnReveal=${modalOpen} chips=${chips} current=${cur} stickyTop=${stuck} headingTop=${hTop} errors=${JSON.stringify(errs)}`);
    if (errs.length || !ended || !fixN || !fixCard || !nl || !bl.n || !bl.transparent || ct1 === ct2 || modalOpen || !chips || !cur.length || stuck > 2 || hTop < 40 || hTop > 140) fail++;
    await p.close();
  }
  await b.close(); console.log(fail ? `FAIL (${fail})` : 'PASS'); process.exit(fail ? 1 : 0);
})();
