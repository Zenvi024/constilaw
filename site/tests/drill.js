// node site/tests/drill.js [built-html]: flashcard drill — flip, hook chip, streak, previous card (undo), keyboard, shuffle
const {chromium} = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
(async () => {
  const b = await chromium.launch(); let fail = 0;
  const check = (tag, name, ok, got) => { if (!ok){ fail++; console.log(`  FAIL ${tag} ${name}: ${JSON.stringify(got)}`); } };
  for (const vp of [{width: 1280, height: 900}, {width: 400, height: 860}]) {
    const p = await b.newPage({viewport: vp}); const tag = vp.width;
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + file + '#cases'); await p.waitForTimeout(300);
    await p.click('[data-cm="drill"]'); await p.click('#dDir [data-d="cr"]'); await p.click('#dStart');
    const n = s => p.$eval('#dCard .streak b', e => +e.textContent);
    const s0 = await n();
    // flip with the keyboard, check the hook chip and the colored top
    await p.keyboard.press('Space'); await p.waitForTimeout(400);
    const back = await p.evaluate(() => ({chip: !!document.querySelector('#dCard .card-face .reveal .hookchip.big'), hc: document.querySelector('#dCard .card-face').dataset.hc, prev: !!document.querySelector('#dCard [data-prev]')}));
    check(tag, 'back shows the hook', back.chip && /^(ok|no|sun|acc)$/.test(back.hc) && !back.prev, back);
    const k1 = await p.evaluate(() => { const c = document.querySelector('#dCard .card-face .prompt').textContent; return c; });
    await p.keyboard.press('3'); await p.waitForTimeout(100);   // good
    const s1 = await n();
    check(tag, 'streak goes up on good', s1 === s0 + 1, [s0, s1]);
    // previous card restores the schedule and the streak
    const srsBefore = await p.evaluate(() => JSON.stringify(JSON.parse(localStorage.getItem('c1_srs') || '{}')));
    await p.click('#dCard [data-prev]'); await p.waitForTimeout(100);
    const back1 = await p.evaluate(() => ({name: document.querySelector('#dCard .card-face .prompt').textContent, lbl: document.querySelector('#dCard .lbl').textContent, streak: +document.querySelector('#dCard .streak b').textContent}));
    check(tag, 'previous goes back and undoes the grade', back1.name === k1 && /Card 1 of/.test(back1.lbl) && back1.streak === s0, back1);
    // miss on purpose: the streak resets
    await p.click('#dCard [data-flip]'); await p.waitForTimeout(400); await p.click('#dCard .grade [data-g="0"]'); await p.waitForTimeout(100);
    check(tag, 'streak resets on again', (await n()) === 0, await n());
    // five in a row shows a toast
    for (let i = 0; i < 5; i++){ await p.click('#dCard [data-flip]'); await p.waitForTimeout(380); await p.click('#dCard .grade [data-g="2"]'); await p.waitForTimeout(60); }
    const toast = await p.isVisible('.mtoast');
    check(tag, 'streak of five', (await n()) === 5 && toast, [await n(), toast]);
    const nameCentered = await p.evaluate(() => { const e = document.querySelector('#dCard .casename'); return e && getComputedStyle(e).textAlign === 'center'; });
    check(tag, 'case name centered', nameCentered, nameCentered);
    await p.screenshot({path: `site/build/drill-${tag}.png`});
    await p.click('#dCard [data-quit]'); const end = await p.textContent('#dCard .endpanel'); check(tag, 'end shows longest run', /Longest run this round: 5/.test(end), end.slice(0, 120));
    // browse rows carry hook chips
    await p.click('#dCard [data-a="back"]'); await p.click('[data-cm="browse"]');
    const chips = await p.$$eval('#clist .hookchip', x => x.length); check(tag, 'browse hook chips', chips > 150, chips);
    const w = await p.evaluate(() => document.documentElement.scrollWidth); check(tag, 'no horizontal overflow', w <= vp.width + 1, w);
    check(tag, 'no page errors', !errs.length, errs);
    await p.close();
  }
  // phone: tap to flip, swipe right to grade good; reading progress; theme switch
  { const ctx = await b.newContext({viewport: {width: 400, height: 800}, hasTouch: true}); const p = await ctx.newPage(); const tag = 'touch';
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + file + '#cases'); await p.waitForTimeout(300);
    await p.click('[data-cm="drill"]'); await p.click('#dDir [data-d="cr"]'); await p.click('#dStart');
    const swipe = (dx, dy) => p.evaluate(([dx, dy]) => { const f = document.querySelector('#dCard .card-face .casename'), r = f.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
      const ev = (t, X, Y) => f.dispatchEvent(new PointerEvent(t, {bubbles: true, pointerId: 7, pointerType: 'touch', clientX: X, clientY: Y}));
      ev('pointerdown', x, y); ev('pointermove', x + dx / 2, y + dy / 2); ev('pointermove', x + dx, y + dy); ev('pointerup', x + dx, y + dy); }, [dx, dy]);
    const lbl = () => p.textContent('#dCard .lbl');
    await swipe(0, 0); await p.waitForTimeout(100);
    const flipped = await p.isVisible('#dCard .grade');
    const sticky = await p.$eval('#dCard .grade', e => getComputedStyle(e).position);
    await swipe(120, 0); await p.waitForTimeout(150);
    const l2 = await lbl(), st = await p.$eval('#dCard .streak b', e => +e.textContent);
    check(tag, 'tap flips, swipe right grades good, grade bar is sticky', flipped && /Card 2 of/.test(l2) && st >= 1 && sticky === 'sticky', {flipped, l2, st, sticky});
    await p.click('#fbExit'); await p.click('#dCard [data-quit]'); await p.click('#dCard [data-a="back"]');
    // reading progress
    await p.click('[data-tab="rules"]'); await p.click('#rcontent section.rv:not([hidden]) .rdone >> nth=0');
    const rd = await p.evaluate(() => ({h: document.querySelector('#rcontent section.rv:not([hidden]) h3.isread') !== null, side: document.querySelector('#rsecs [data-rp]').textContent}));
    await p.click('[data-tab="today"]'); const prog = await p.textContent('#rvProg');
    check(tag, 'reading progress', rd.h && /^1\//.test(rd.side) && /1 of \d+ parts/.test(prog), {rd, prog: prog.slice(0, 60)});
    // theme
    await p.click('#themeBtn'); const t1 = await p.evaluate(() => document.documentElement.dataset.theme); await p.click('#themeBtn'); const t2 = await p.evaluate(() => document.documentElement.dataset.theme);
    await p.click('#themeBtn'); const t3 = await p.evaluate(() => document.documentElement.dataset.theme || 'auto');
    check(tag, 'theme cycles', t1 === 'light' && t2 === 'dark' && t3 === 'auto', [t1, t2, t3]);
    check(tag, 'no page errors', !errs.length, errs);
    await ctx.close(); }
  await b.close(); console.log(fail ? `FAIL (${fail})` : 'PASS'); process.exit(fail ? 1 : 0);
})();
