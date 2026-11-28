// node site/tests/course.js [built-html]: the whole-course pass (Batch 12).
// Every diagram outside the method, territory, citizenship and news maps has a "Say it in orals" line; the issue radar
// covers the finals parts and every row links to a diagram; the six comparison tables and the finals numbers are on the
// method map; the drill has one-tap part buttons; a midterm-era topic choice gets the finals topics once; the new print
// documents build. Phone and laptop, light and dark, no horizontal scroll, no console errors.
const {chromium} = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
(async () => {
  const b = await chromium.launch(); let fail = 0;
  const check = (tag, name, ok, got) => { if (!ok){ fail++; console.log(`  FAIL ${tag} ${name}: ${JSON.stringify(got)}`); } };
  for (const vp of [{width: 1280, height: 900, dark: true}, {width: 700, height: 900, dark: false}, {width: 400, height: 860, dark: false}]) {
    const ctx = await b.newContext({viewport: {width: vp.width, height: vp.height}, colorScheme: vp.dark ? 'dark' : 'light'});
    const p = await ctx.newPage(); const tag = vp.width + (vp.dark ? ' dark' : ' light');
    const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    // a viewer who chose midterm topics before the finals
    await p.goto('file://' + file + '#rules'); await p.waitForTimeout(300);
    await p.evaluate(() => { localStorage.setItem('c1_dtop', JSON.stringify(['jr', 'org'])); localStorage.removeItem('c1_dtop_v'); });
    await p.reload(); await p.waitForTimeout(500);
    const orals = await p.evaluate(() => { const miss = []; document.querySelectorAll('section.rv').forEach(s => { if (['method', 'terr', 'cit', 'news'].includes(s.id)) return; s.querySelectorAll('figure.viz').forEach(f => { if (!f.querySelector('.vor p')) miss.push(s.id + ':' + f.id); }); }); return {miss, n: document.querySelectorAll('figure .vor p').length}; });
    check(tag, 'every diagram has an orals line', !orals.miss.length && orals.n >= 120, orals);
    const radar = await p.evaluate(() => { const r = document.querySelector('#fig-radar'); const g = [...r.querySelectorAll('.grp')].map(x => x.querySelector('.vsub, h4, b, div').textContent); const links = [...r.querySelectorAll('a.xref')]; return {groups: r.querySelectorAll('.grp').length, rows: r.querySelectorAll('.rrow').length, bad: links.filter(a => !document.getElementById(a.dataset.h)).map(a => a.dataset.h), imp: !!r.textContent.match(/one-year bar/)}; });
    check(tag, 'issue radar covers the whole course', radar.groups >= 13 && radar.rows >= 85 && !radar.bad.length && radar.imp, radar);
    const meth = await p.evaluate(() => ({orals: !!document.getElementById('method-orals'), cmp: document.querySelectorAll('#method h3#method-compare ~ h4 + .tw').length, nums: D.numbers.length, title: document.querySelector('#method h2').textContent}));
    check(tag, 'method map: orals section, six comparison tables, finals numbers', meth.orals && meth.cmp >= 6 && meth.nums >= 27 && /exams/.test(meth.title), meth);
    // drill: the saved midterm choice now includes the finals topics; part buttons pick one part
    await p.evaluate(() => { setTab('cases'); document.querySelector('[data-cm="drill"]').click(); }); await p.waitForTimeout(200);
    const dr = await p.evaluate(() => ({fin: ['legproc', 'pres', 'concom'].every(k => dTop.has(k)), kept: dTop.has('jr'), parts: document.querySelectorAll('#dParts [data-dpart]').length}));
    check(tag, 'midterm topic choice gets the finals topics once; part buttons shown', dr.fin && dr.kept && dr.parts >= 6, dr);
    await p.click('#dParts [data-dpart="exec"]'); await p.waitForTimeout(100);
    const ex = await p.evaluate(() => ({keys: [...dTop].sort(), count: document.getElementById('dCount').textContent}));
    check(tag, 'Executive button selects only the executive topics', ex.keys.join() === 'appt,cinc,pres' && /\d+ cases selected/.test(ex.count), ex);
    await p.click('#dAll');
    // the migration runs once: clearing stays cleared after a reload
    await p.click('#dNone'); await p.waitForFunction(() => localStorage.getItem('c1_dtop') === '[]'); await p.reload(); await p.waitForTimeout(400);
    const once = await p.evaluate(() => dTop.size);
    check(tag, 'the migration runs once', once === 0, once);
    await p.evaluate(() => { dTop = new Set(D.topics.map(t => t.key)); store.set('dtop', [...dTop]); });
    // print documents
    const pd = await p.evaluate(() => { const ids = printDocs().map(d => d.id); const f = PD_BUILD.fishbowl(), o = PD_BUILD.orals(); return {ids, f: (f.match(/class="pdq"/g) || []).length, o: (o.match(/class="pdq"/g) || []).length}; });
    check(tag, 'fishbowl and orals print documents', pd.ids.includes('fishbowl') && pd.ids.includes('orals') && pd.f >= 46 && pd.o >= 110, pd);
    // phone polish: the rule-map search box keeps its normal height; the tabs fit; back to top; the fishbowl setup folds
    await p.evaluate(() => setTab('rules')); await p.waitForTimeout(200);
    const ui = await p.evaluate(() => { const t = document.querySelector('.tabs'); return {rq: Math.round(document.getElementById('rq').getBoundingClientRect().height), tabs: t.scrollWidth - t.clientWidth}; });
    check(tag, 'rule-map search box is one line high; tabs fit', ui.rq < 60 && ui.tabs <= 1, ui);
    await p.evaluate(() => window.scrollTo(0, 5000)); await p.waitForTimeout(300);
    const tt = await p.evaluate(() => !document.getElementById('toTop').hidden);
    await p.click('#toTop'); await p.waitForTimeout(200);
    const top = await p.evaluate(() => Math.round(scrollY));
    check(tag, 'back-to-top button appears and works', tt && top < 50, {tt, top});
    await p.evaluate(() => fwOpen('fb-cj')); await p.waitForTimeout(200);
    const fold = await p.evaluate(() => ({min: document.getElementById('fwSetup').classList.contains('fwmin'), draw: document.getElementById('fwDraw').textContent, opts: !document.getElementById('fwOpts').hidden}));
    await p.click('#fwOpts');
    const unfold = await p.evaluate(() => !document.getElementById('fwSetup').classList.contains('fwmin'));
    check(tag, 'fishbowl setup folds while a card is out', fold.min && fold.draw === 'Draw another' && fold.opts && unfold, {fold, unfold});
    await p.evaluate(() => { setTab('rules'); goToId('method-compare'); }); await p.waitForTimeout(800);
    const hs = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    check(tag, 'no horizontal scroll', hs <= 1, hs);
    if (vp.width === 400) await p.screenshot({path: path.join(process.env.SHOTS || '/tmp', 'course-400.png')});
    check(tag, 'no console errors', !errs.length, errs);
    await ctx.close();
  }
  await b.close();
  console.log(fail ? `course: ${fail} failure(s)` : 'course: all checks passed');
  process.exit(fail ? 1 : 0);
})();
