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
  await b.close(); console.log(fail ? `FAIL (${fail})` : 'PASS'); process.exit(fail ? 1 : 0);
})();
