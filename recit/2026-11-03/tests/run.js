const {chromium} = require('playwright'); const fs = require('fs'); const path = require('path');
const src = fs.readFileSync(process.argv[2], 'utf8');
const page_html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>${src}</body></html>`;
const tmp = path.join(path.dirname(process.argv[2]), 'test', '_wrapped.html'); fs.writeFileSync(tmp, page_html);
(async () => {
  const b = await chromium.launch(); const errs = [];
  const ctx = await b.newContext({viewport: {width: 1280, height: 900}}); const p = await ctx.newPage();
  p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/fonts|ERR_|net::/.test(m.text())) errs.push('console ' + m.text()); });
  await p.goto('file://' + tmp); await p.waitForSelector('.hero');
  // completeness dump: digest mode with WRITE on, colours on, blur off
  const dump = await p.evaluate(() => { const out = {}; S.wr = true; S.blur = false; S.hl = true; applyFlags(); S.mode = 'digest';
    for (const c of ALLC){ openCase(c.id); out[c.file] = document.getElementById('view').innerText; } return out; });
  fs.writeFileSync(path.join(path.dirname(tmp), 'rendered.json'), JSON.stringify(dump));
  // card mode + split each also render without errors
  const res = {};
  for (const m of ['card', 'split']) res[m] = await p.evaluate(m => { let n = 0; for (const c of ALLC){ openCase(c.id); S.mode = m; render(); n += document.querySelectorAll('#view .ic').length; } return n; }, m);
  await p.evaluate(() => openCase(CASES[0].id));
  await p.click('[data-set="nov5"]'); res.setSwitch = await p.evaluate(() => [S.set, CASES.length, ALL.length, BY[S.id].set]);
  await p.click('[data-set="nov3"]');
  // tabs
  for (const t of ['wall', 'compare', 'sheet', 'drill']){ await p.click(`.tabs [data-tab="${t}"]`); await p.waitForTimeout(80); res[t] = (await p.innerText('#view')).length; }
  // drill all modes: reveal through and grade
  for (const dm of ['call', 'issue', 'facts', 'doc']){
    await p.click(`[data-dm="${dm}"]`);
    for (let k = 0; k < 3; k++){ let g = 0; while (await p.$('[data-dnext]') && g++ < 6){ await p.keyboard.press('Space'); } await p.keyboard.press('3'); }
    res['drill_' + dm] = await p.evaluate(() => [DK.i, DK.items.length, STREAK.cur]);
  }
  await p.click('[data-dprev]'); res.prevOk = await p.evaluate(() => DK.i);
  await p.selectOption('[data-dgr]', 'both'); res.both = await p.evaluate(() => DK.items.length);
  await p.click('[data-set="nov5"]'); await p.click('[data-dm="call"]'); res.bothAfterSwitch = await p.evaluate(() => [S.dg, DK.items.length]);
  await p.selectOption('[data-dgr]', 'immu'); res.immu = await p.evaluate(() => DK.items.map(x => x.c));
  await p.click('.tabs [data-tab="wall"]'); await p.selectOption('[data-wg]', 'remo'); res.wallRemo = await p.$$eval('.wcard', x => x.length);
  await p.click('.tabs [data-tab="compare"]'); res.cmpNov5 = await p.$$eval('.tl-lab', x => x.length);
  await p.click('[data-set="nov3"]');
  // search
  await p.click('.tabs [data-tab="read"]'); await p.fill('#q', 'Beltran Macasiar'); await p.waitForTimeout(100); res.search = await p.$$eval('#sres [data-hit]', x => x.length);
  await p.click('#sres [data-hit]'); res.searchOpened = await p.evaluate(() => S.id);
  // blur
  await p.click('#blBtn'); res.blurred = await p.$$eval('#view .hl-y,#view .hl-p,#view .hl-o', x => x.length);
  const one = await p.$('#view .hl-p'); if (one){ await one.click(); res.revealed = await p.$$eval('#view .shown', x => x.length); } await p.click('#blBtn');
  // ready + focus
  await p.keyboard.press('r'); res.ready = await p.innerText('#progTxt'); await p.keyboard.press('r');
  await p.keyboard.press('f'); res.focus = await p.evaluate(() => getComputedStyle(document.querySelector('.top')).display); await p.keyboard.press('Escape');
  await p.screenshot({path: path.join(path.dirname(tmp), 'shot-1280.png')});
  // overflow sweep
  for (const [w, h] of [[400, 860], [1280, 900]]) for (const th of ['light', 'dark']) for (const set of ['nov3', 'nov5']){
    const c2 = await b.newContext({viewport: {width: w, height: h}, hasTouch: w < 500, colorScheme: th}); const q = await c2.newPage();
    q.on('pageerror', e => errs.push(`pageerror ${w}${th} ` + e.message));
    await q.goto('file://' + tmp); await q.waitForSelector('.hero');
    for (const t of ['read', 'wall', 'drill', 'compare', 'sheet']) for (const m of (t === 'read' ? ['digest', 'card', 'split'] : [''])){
      await q.evaluate(([t, m, set]) => { useSet(set); S.tab = t; if (m) S.mode = m; DK = null; render(); }, [t, m, set]);
      const ids = t === 'read' && m === 'digest' ? await q.evaluate(() => CASES.map(c => c.id)) : [null];
      for (const cid of ids){
        if (cid) await q.evaluate(id => { S.id = id; render(); }, cid);
        const ov = await q.evaluate(() => document.documentElement.scrollWidth - innerWidth);
        if (ov > 0) errs.push(`overflow ${w} ${th} ${set} ${t} ${m} ${cid}: ${ov}`);
      }
    }
    await q.evaluate(() => { S.tab = 'read'; S.mode = 'digest'; S.id = CASES[0].id; render(); });
    await q.waitForTimeout(300);
    await q.screenshot({path: path.join(path.dirname(tmp), `shot-${w}-${th}-${set}.png`)}); await c2.close();
  }
  console.log(JSON.stringify(res)); console.log('ERRORS', errs.length, errs.slice(0, 20));
  await b.close();
})();
