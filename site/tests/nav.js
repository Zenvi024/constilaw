// node site/tests/nav.js [built-html]: "← Back" returns to where a link was followed (tab, scroll, open case card),
// from the digest reader, the case card, the floating button, Esc and the browser's back gesture.
const {chromium} = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
(async () => {
  const b = await chromium.launch(); let fail = 0;
  const check = (tag, name, ok, got) => { if (!ok){ fail++; console.log(`  FAIL ${tag} ${name}: ${JSON.stringify(got)}`); } };
  for (const vp of [{width: 1280, height: 900}, {width: 400, height: 860}]) {
    const p = await b.newPage({viewport: vp}); const tag = vp.width;
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + file + '#rules'); await p.waitForTimeout(400);
    const state = () => p.evaluate(() => ({tab: localStorage.getItem('c1_tab'), y: Math.round(scrollY), modal: !document.getElementById('scrim').hidden,
      title: (document.querySelector('#modal h3') || {}).textContent || '', reader: !document.getElementById('v-digests').hidden && !!document.querySelector('#fdDoc .fddoc'),
      fab: !document.getElementById('navBackBtn').hidden}));
    // 0. three-level case card: summary, doctrine, quick facts and ruling, detailed summary per issue, full digest
    await p.evaluate(() => openCase('gutierrez')); await p.waitForTimeout(200);
    const card = await p.evaluate(() => ({sum: !!document.querySelector('#modal .cksum'), doc: !!document.querySelector('#modal .ckdoc .ckrule'), glance: document.querySelectorAll('#modal .ckq3').length,
      closed: !document.querySelector('#modal .ckdet').open, iss: document.querySelectorAll('#modal .ckiss li').length, dig: !!document.querySelector('#modal [data-fdcard]')}));
    check(tag, 'three-level case card', card.sum && card.doc && card.glance === 2 && card.closed && card.iss >= 3 && card.dig, card);
    const plain = await p.evaluate(() => { openCase('obergefell'); return !document.querySelector('#modal .ckdet') && !!document.querySelector('#modal dd.rule'); });
    check(tag, 'cards without a digest keep the old layout', plain, plain);
    await p.keyboard.press('Escape'); await p.waitForTimeout(150);
    // 1. rule map → case card → full digest → Back (button in the reader)
    await p.evaluate(() => goToId('fig-initiate')); await p.waitForTimeout(1200);
    await p.evaluate(() => scrollBy(0, 120)); await p.waitForTimeout(100);
    const before = await state();
    await p.click('#fig-initiate a.cref[data-c="gutierrez"] >> nth=0'); await p.waitForTimeout(200);
    await p.click('[data-fdcard="gutierrez"]'); await p.waitForSelector('#fdDoc .fddoc'); await p.waitForTimeout(200);
    const inReader = await state();
    check(tag, 'digest opens from the case card', inReader.reader && !inReader.modal, inReader);
    await p.click('#fdRead [data-navback]'); await p.waitForTimeout(500);
    const back1 = await state();
    check(tag, 'Back returns to the rule map with the case card open', back1.tab === '"rules"' && back1.modal && /Gutierrez/.test(back1.title) && Math.abs(back1.y - before.y) < 60, {before, back1});
    // 2. same trip, back with Esc
    await p.click('[data-fdcard="gutierrez"]'); await p.waitForSelector('#fdDoc .fddoc'); await p.waitForTimeout(200);
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    const back2 = await state();
    check(tag, 'Esc goes back too', back2.tab === '"rules"' && back2.modal && /Gutierrez/.test(back2.title), back2);
    // 3. same trip, back with the browser's back gesture
    await p.click('[data-fdcard="gutierrez"]'); await p.waitForSelector('#fdDoc .fddoc'); await p.waitForTimeout(200);
    await p.goBack(); await p.waitForTimeout(600);
    const back3 = await state();
    check(tag, 'browser back goes back too', back3.tab === '"rules"' && back3.modal && /Gutierrez/.test(back3.title), back3);
    // Esc on an open card only closes it (no extra step back)
    await p.keyboard.press('Escape'); await p.waitForTimeout(200);
    const closed = await state();
    check(tag, 'Esc on a case card just closes it', !closed.modal && closed.tab === '"rules"', closed);
    // 4. a link between diagrams → the floating Back button
    await p.evaluate(() => goToId('fig-cvotes')); await p.waitForTimeout(1200);
    const xr = await p.$('#ocong a.xref'); if (xr){ await xr.scrollIntoViewIfNeeded(); await p.waitForTimeout(200); }
    const y0 = (await state()).y;
    if (xr){ await xr.click(); await p.waitForTimeout(300); }
    const moved = await state();
    check(tag, 'floating Back appears after a diagram link', !!xr && moved.fab, moved);
    await p.click('#navBackBtn'); await p.waitForTimeout(500);
    const back4 = await state();
    check(tag, 'floating Back restores the scroll position', Math.abs(back4.y - y0) < 60 && !back4.fab, {y0, back4});
    // a tab click starts fresh: no Back button left over
    await p.click('.tabs [data-tab="cases"]'); await p.waitForTimeout(200);
    check(tag, 'tab bar clears the trail', !(await state()).fab, '');
    const w = await p.evaluate(() => document.documentElement.scrollWidth); check(tag, 'no horizontal overflow', w <= vp.width + 1, w);
    check(tag, 'no page errors', !errs.length, errs);
    console.log(`${tag}: back=${JSON.stringify(back1)} esc=${back2.modal} browser=${back3.modal}`);
    await p.close();
  }
  await b.close(); console.log(fail ? `FAIL (${fail})` : 'PASS'); process.exit(fail ? 1 : 0);
})();
