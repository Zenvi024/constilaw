// node site/tests/digests.js [built-html]: the finals Digests tab — list, reader (one digest per case), recall mode, card link, phone layout,
// and the completeness check: every word of every source digest, except the hidden WRITE boxes and 5×8 card, appears in the rendered reader text.
const {chromium} = require('playwright');
const path = require('path'), fs = require('fs');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
const SRC = JSON.parse(fs.readFileSync(path.resolve('finals-intake/parsed/source_words.json'), 'utf8'));
const LABELS = new Set(['write', 'front', 'back', 'facts', 'final', 'decision', 'issue', 'headnote']);
const words = t => { const m = {}; for (const w of (t.toLowerCase().match(/[\p{L}\p{N}_]+/gu) || [])) m[w] = (m[w] || 0) + 1; return m; };
(async () => {
  const b = await chromium.launch(); let fail = 0;
  const check = (tag, name, ok, got) => { if (!ok){ fail++; console.log(`  FAIL ${tag} ${name}: ${JSON.stringify(got).slice(0, 400)}`); } };
  for (const [vp, scheme] of [[{width: 1280, height: 900}, 'light'], [{width: 400, height: 860}, 'dark'], [{width: 1280, height: 900}, 'dark'], [{width: 400, height: 860}, 'light']]) {
    const p = await b.newPage({viewport: vp, colorScheme: scheme}); const tag = `${scheme}-${vp.width}`;
    const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error' && !/fonts|net::/.test(m.text())) errs.push(m.text()); });
    await p.goto('file://' + file + '#digests'); await p.waitForTimeout(500);
    const rows = await p.$$eval('#fdList .fdrow', r => r.length);
    check(tag, 'finals list shows every finals case', rows === 170, rows);
    // open the first case, then one with two digests
    await p.click('#fdList .fdrow'); await p.waitForSelector('#fdDoc .fddoc');
    const first = await p.evaluate(() => ({title: document.querySelector('#fdRead h2').textContent, hn: !!document.querySelector('#fdDoc .fdhn'), jump: document.querySelectorAll('#fdRead .fdjump button').length}));
    check(tag, 'reader shows the digest', first.title.length > 5 && first.hn && first.jump >= 3, first);
    // one digest per case: no version tabs, no WRITE boxes, no 5×8 card, no source labels; a decision and its resolution read as one
    const plain = await p.evaluate(() => ({ver: !!document.querySelector('#fdRead .fdver'), write: /WRITE ▸|5×8 recit card/.test(document.querySelector('#fdRead').innerText), tags: [...document.querySelectorAll('#fdList .fdtag')].filter(t => /digests/.test(t.textContent)).length, src: /Zen|manual digest|block i-b|\.docx/i.test(document.querySelector('#fdRead').innerText)}));
    check(tag, 'one digest, no versions, no WRITE boxes or 5×8 card, no source labels', !plain.ver && !plain.write && !plain.tags && !plain.src, plain);
    const two = await p.evaluate(() => { const r = [...document.querySelectorAll('#fdList .fdrow')].find(x => /Gonzales III/.test(x.textContent)); if (r) r.click(); return !!r; });
    await p.waitForTimeout(300);
    const vers = await p.evaluate(() => ({next: document.querySelectorAll('#fdDoc .fdnext').length, btn: [...document.querySelectorAll('#fdRead .fdjump button')].some(b => /Resolution|Next ruling/.test(b.textContent))}));
    check(tag, 'decision and resolution read as one digest', two && vers.next === 1 && vers.btn, [two, vers]);
    const hlc = await p.evaluate(() => [...new Set([...document.querySelectorAll('#fdDoc .hl-y, #fdDoc .hl-p, #fdDoc .hl-o')].map(h => getComputedStyle(h).backgroundColor))]);
    check(tag, 'one highlight color', hlc.length === 1, hlc);
    // recall mode hides highlights; tapping one reveals it (use a digest that has highlights)
    await p.evaluate(() => { const rows = [...document.querySelectorAll('#fdList .fdrow')]; const r = rows.find(x => /Funa v\. Commission on Audit/.test(x.textContent)) || rows[20]; r.click(); });
    await p.waitForTimeout(300);
    await p.click('[data-fdblur]'); await p.waitForTimeout(150);
    const blur = await p.evaluate(() => { const h = document.querySelector('#fdDoc.fdblur .hl-y, #fdDoc.fdblur .hl-p'); return h ? getComputedStyle(h).color : null; });
    check(tag, 'recall mode covers highlights', blur === 'rgba(0, 0, 0, 0)', blur);
    await p.click('[data-fdblur]');
    // search inside the digests (on phones, go back to the list first)
    if (vp.width === 400) await p.click('[data-fdback]');
    await p.fill('#fdq', 'sui generis'); await p.waitForTimeout(500);
    const hits = await p.$$eval('#fdList .fdrow', r => r.length);
    check(tag, 'full-text search finds digests', hits >= 1 && hits < 170, hits);
    await p.fill('#fdq', ''); await p.waitForTimeout(300);
    // whole-syllabus view keeps citizenship and territory hidden while the scope toggle is on
    await p.click('[data-fdscope="all"]'); await p.waitForTimeout(300);
    const all = await p.evaluate(() => ({n: document.querySelectorAll('#fdList .fdrow').length, cit: [...document.querySelectorAll('#fdList .fdrow')].some(r => /Tecson|Magallona/.test(r.textContent))}));
    check(tag, 'whole syllabus listed without citizenship and territory', all.n > 290 && !all.cit, all);
    await p.click('[data-fdscope="fin"]');
    // a case card links to its digest
    await p.goto('file://' + file + '#cases'); await p.waitForTimeout(300);
    await p.evaluate(() => openCase('francisco')); await p.waitForTimeout(150);
    const link = await p.$('[data-fdcard]');
    check(tag, 'case card has a full-digest button', !!link, '');
    if (link){ await link.evaluate(b => b.scrollIntoView({block: 'center'})); await p.waitForTimeout(250); await link.click(); await p.waitForSelector('#fdDoc .fddoc'); check(tag, 'button opens the digest', /Francisco/i.test(await p.textContent('#fdRead h2')), await p.textContent('#fdRead h2')); }
    // no horizontal scroll, on the list and in the reader
    await p.goto('file://' + file + '#digests'); await p.waitForTimeout(400);
    for (const k of [0, 40, 120]){
      await p.evaluate(k => document.querySelectorAll('#fdList .fdrow')[k].click(), k); await p.waitForTimeout(250);
      const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      check(tag, 'no horizontal scroll in the reader ' + k, ov <= 0, ov);
    }
    if (vp.width === 400){
      const st = await p.evaluate(() => ({list: getComputedStyle(document.querySelector('.fdside')).display, back: getComputedStyle(document.querySelector('[data-fdback]')).display}));
      check(tag, 'phone: reading hides the list and shows Back', st.list === 'none' && st.back !== 'none', st);
      await p.click('[data-fdback]'); await p.waitForTimeout(150);
      check(tag, 'phone: Back returns to the list', await p.evaluate(() => getComputedStyle(document.querySelector('.fdside')).display !== 'none'), '');
    }
    if (vp.width === 1280 && scheme === 'light'){
      // completeness: render every digest and compare its text with the source .docx words
      const ids = Object.keys(SRC); let bad = 0;
      for (const id of ids){
        const txt = await p.evaluate(async id => { const box = document.createElement('div'); box.className = 'fd'; box.style.cssText = 'position:absolute;left:0;top:0;width:900px'; box.innerHTML = await window.__fdRender(id); document.body.append(box); const t = box.innerText + ' ' + (window.FDZ ? '' : ''); box.remove(); return t; }, id);
        const have = words(txt), miss = {};
        for (const [w, n] of Object.entries(SRC[id])) if (!LABELS.has(w) && (have[w] || 0) < n) miss[w] = n - (have[w] || 0);
        if (Object.keys(miss).length){ bad++; if (bad < 6) console.log('  missing in', id, JSON.stringify(miss).slice(0, 200)); }
      }
      check(tag, `every word of all ${ids.length} digests is on the page`, bad === 0, bad);
      console.log(`  completeness: ${ids.length} digests rendered, ${bad} with missing words`);
      await p.screenshot({path: (process.env.SHOTS || '.') + '/fd-1280.png'}).catch(() => {});
    }
    if (vp.width === 400 && scheme === 'dark') await p.screenshot({path: (process.env.SHOTS || '.') + '/fd-400-dark.png'}).catch(() => {});
    check(tag, 'no page errors', errs.length === 0, errs);
    console.log(`${tag}: rows=${rows} first=${JSON.stringify(first)} merged=${JSON.stringify(vers)} search=${hits} all=${all.n} errors=${errs.length}`);
    await p.close();
  }
  await b.close();
  console.log(fail ? `FAIL (${fail})` : 'PASS'); process.exit(fail ? 1 : 0);
})();
