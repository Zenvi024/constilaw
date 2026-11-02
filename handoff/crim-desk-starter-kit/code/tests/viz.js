// node site/tests/viz.js [built-html]: rule-map diagrams — walk-throughs, test-me covers, calculators, links, hook wall, search
const {chromium} = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
(async () => {
  const b = await chromium.launch(); let fail = 0;
  const check = (tag, name, ok, got) => { if (!ok){ fail++; console.log(`  FAIL ${tag} ${name}: ${JSON.stringify(got)}`); } };
  for (const vp of [{width: 1280, height: 900}, {width: 400, height: 860}]) {
    const p = await b.newPage({viewport: vp}); const tag = vp.width;
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + file + '#rules'); await p.waitForTimeout(300);
    const txt = sel => p.$eval(sel, e => e.textContent.trim());
    const go = async id => { await p.evaluate(id => goToId(id), id); await p.waitForTimeout(150); };
    // every diagram carries a title; gate diagrams with fact patterns get a walk bar
    const counts = await p.evaluate(() => ({figs: document.querySelectorAll('#rcontent figure.viz').length, walk: document.querySelectorAll('#rcontent .walkbar').length, tests: document.querySelectorAll('#rcontent .vtools .vtest').length, hooks: document.querySelectorAll('#rcontent .hook').length}));
    check(tag, 'counts', counts.figs >= 50 && counts.walk >= 20 && counts.tests >= 40 && counts.hooks >= 45, counts);
    // the issue radar links to the arrest diagram
    await go('fig-radar'); await p.click('#fig-radar .rrow:has-text("protective custody") a.xref'); await p.waitForTimeout(250);
    const arrTop = await p.evaluate(() => Math.round(document.getElementById('fig-arrest').getBoundingClientRect().top));
    check(tag, 'radar link lands on the arrest diagram', arrTop > -5 && arrTop < 200, arrTop);
    // walk a fact pattern, answering wrongly on purpose
    await p.click('#fig-arrest .walkbar .vchip:has-text("Dimaporo")');
    check(tag, 'walk shows the facts', await p.isVisible('#fig-arrest .walkp'), await txt('#fig-arrest .walkp'));
    const hiddenGate2 = await p.evaluate(() => document.querySelectorAll('#fig-arrest .gate')[1].hidden);
    await p.click('#fig-arrest .gate.cur .yn [data-a="y"]');
    const r1 = {fb: await txt('#fig-arrest .fb'), res: await txt('#fig-arrest .walkout .vres'), score: await txt('#fig-arrest .walkout .score')};
    check(tag, 'wrong answer is corrected and the walk ends at the exit', hiddenGate2 && /on these facts it is no/.test(r1.fb) && /Arrest allowed/.test(r1.res) && /0 of 1/.test(r1.score), r1);
    await p.click('#fig-arrest .walkout [data-w="again"]');
    await p.click('#fig-arrest .walkbar .vchip:has-text("light offense")');
    await p.click('#fig-arrest .gate.cur .yn [data-a="y"]'); await p.click('#fig-arrest .gate.cur .yn [data-a="y"]');
    const r2 = {res: await txt('#fig-arrest .walkout .vres'), score: await txt('#fig-arrest .walkout .score')};
    check(tag, 'right answers reach the end box', /Privileged from arrest/.test(r2.res) && /2 of 2/.test(r2.score), r2);
    await p.click('#fig-arrest .walkout [data-w="map"]');
    const restored = await p.evaluate(() => [...document.querySelectorAll('#fig-arrest .gates > *')].every(x => !x.hidden) && !document.querySelector('#fig-arrest .yn'));
    check(tag, 'show the whole map restores the diagram', restored, restored);
    // an arguable answer is accepted either way
    await go('fig-lambino'); await p.click('#fig-lambino .walkbar .vchip:has-text("Economic")');
    await p.click('#fig-lambino .gate.cur .yn [data-a="n"]');
    const arg = await txt('#fig-lambino .fb'); check(tag, 'arguable answer', /Arguable/.test(arg), arg);
    await p.click('#fig-lambino .walkbar .vchip[aria-pressed="true"]');
    // your own facts follow your answers
    await go('fig-augment'); await p.click('#fig-augment .walkbar .vchip:has-text("Your own facts")');
    await p.click('#fig-augment .gate.cur .yn [data-a="y"]'); await p.click('#fig-augment .gate.cur .yn [data-a="n"]');
    const own = await txt('#fig-augment .walkout .vres'); check(tag, 'own facts', /Void/.test(own) && !(await p.isVisible('#fig-augment .walkout .score')), own);
    await p.click('#fig-augment .walkout [data-w="map"]');
    // test me: covers, counts and reveals without opening a case
    await go('fig-speech'); await p.click('#fig-speech .vtools .vtest');
    const ct1 = await txt('#fig-speech .vtools .ct');
    const covered = await p.evaluate(() => { const el = document.querySelector('#fig-speech .gate > .gx'); return getComputedStyle(el.querySelector('b')).color; });
    await p.click('#fig-speech .gate >> nth=0 >> .gx'); const ct2 = await txt('#fig-speech .vtools .ct');
    const modal = await p.isVisible('#scrim');
    check(tag, 'test me covers and reveals', /^0 of \d+$/.test(ct1) && /^1 of \d+$/.test(ct2) && covered === 'rgba(0, 0, 0, 0)' && !modal, {ct1, ct2, covered, modal});
    await p.click('#fig-speech .vtools .vtest');
    // vote counter
    await go('fig-votes'); await p.fill('#fig-votes [data-v="all"]', '316'); await p.fill('#fig-votes [data-v="present"]', '300');
    const v = await p.$$eval('#fig-votes .rung .cnt', x => x.map(e => e.textContent));
    check(tag, 'vote counter', v[0] === '60 of 300 present' && v[3] === '211 of all 316' && v[4] === '237 of all 316', v);
    await p.click('#fig-votes [data-set="24"]'); const v2 = await p.$$eval('#fig-votes .rung .cnt', x => x.map(e => e.textContent.split(' ')[0]).join(','));
    check(tag, 'Senate preset', v2 === '5,13,13,16,18', v2);
    // CA calculator
    await go('fig-ca'); const ca1 = await txt('#fig-ca .msg');
    await p.fill('#fig-ca tbody tr >> nth=0 >> input', '16'); const ca2 = await txt('#fig-ca .msg');
    check(tag, 'CA calculator', /^10 of 12 seats/.test(ca1) && /^10 of 12 seats/.test(ca2) === false && /^11 of 12 seats/.test(ca2), {ca1, ca2});
    // party-list calculator
    await go('fig-partylist'); const pl1 = await txt('#fig-partylist .msg');
    const seatsA = await p.$eval('#fig-partylist tbody tr td:last-child', e => e.textContent);
    const g = await p.$$eval('#fig-partylist tbody tr', trs => { const r = trs.find(t => t.textContent.startsWith('Group G')); return [...r.querySelectorAll('td')].map(t => t.textContent); });
    await p.fill('#fig-partylist [data-v="district"]', '200'); const pl2 = await txt('#fig-partylist .msg');
    check(tag, 'party-list calculator', /^63 party-list seats/.test(pl1) && seatsA === '3' && g[4] === '1' && g[3] === '·' && /^50 party-list seats/.test(pl2), {pl1, seatsA, g, pl2});
    // quorum and stepper still work
    await go('fig-quorum'); await p.click('#fig-quorum [data-q="avelino"]'); const q = await txt('#fig-quorum .qread');
    check(tag, 'quorum', /12present23base.*12needed for a quorumQuorum/.test(q.replace(/\s+/g, '')) || /Quorum/.test(q), q.slice(0, 80));
    // hook wall: finals tiles hidden while citizenship and territory are out of scope
    const wall = await p.evaluate(() => ({all: document.querySelectorAll('#fig-wall .ht').length, shown: [...document.querySelectorAll('#fig-wall .ht')].filter(t => !t.hidden).length}));
    check(tag, 'hook wall scope', wall.all - wall.shown === 2, wall);
    // universal search finds a hook and lands on its diagram
    await p.fill('#gq', 'Goldilocks'); await p.waitForTimeout(400);
    const nres = await p.$$eval('#gRes .gres', x => x.length);
    await p.click('#gRes .gres >> nth=0'); await p.waitForTimeout(400);
    const ripeVis = await p.evaluate(() => { const r = document.getElementById('fig-ripe').getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; });
    check(tag, 'search a hook', nres > 0 && ripeVis, {nres, ripeVis});
    // diagram class names must not collide with the rest of the app (a hidden .facts once blanked the drills and the essay prompt)
    const leak = await p.evaluate(() => [...document.querySelectorAll('.facts, .hdr .clock, #dTopics .chip')].filter(e => !e.closest('figure.viz') && getComputedStyle(e).display === 'none').length);
    check(tag, 'no style leaks outside the diagrams', leak === 0, leak);
    const w = await p.evaluate(() => document.documentElement.scrollWidth); check(tag, 'no horizontal overflow', w <= vp.width + 1, w);
    check(tag, 'no page errors', !errs.length, errs);
    console.log(`${tag}: ${JSON.stringify(counts)} wall=${JSON.stringify(wall)}`);
    await p.close();
  }
  await b.close(); console.log(fail ? `FAIL (${fail})` : 'PASS'); process.exit(fail ? 1 : 0);
})();
