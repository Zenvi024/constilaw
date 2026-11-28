// node site/tests/fishbowl.js [built-html]: the orals simulator (Practice → Fishbowl).
// Draw → think timer → answer timer → follow-up → model outline → self-grade; filters; news-map links into cards;
// recording falls back cleanly; phone and laptop, both themes, no horizontal scroll, no console errors.
const {chromium} = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html');
(async () => {
  const b = await chromium.launch(); let fail = 0;
  const check = (tag, name, ok, got) => { if (!ok){ fail++; console.log(`  FAIL ${tag} ${name}: ${JSON.stringify(got)}`); } };
  for (const vp of [{width: 1280, height: 900, dark: false}, {width: 400, height: 860, dark: true}]) {
    const p = await b.newPage({viewport: {width: vp.width, height: vp.height}, colorScheme: vp.dark ? 'dark' : 'light'}); const tag = vp.width + (vp.dark ? ' dark' : ' light');
    const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto('file://' + file + '#today'); await p.waitForTimeout(400);
    await p.click('.tabs [data-tab="practice"]'); await p.waitForTimeout(200);
    const open = await p.evaluate(() => ({fish: !document.getElementById('v-fish').hidden, sub: document.querySelector('#psub [data-tab="fish"]').getAttribute('aria-pressed')}));
    check(tag, 'Practice opens on the fishbowl', open.fish && open.sub === 'true', open);
    const pool = await p.evaluate(() => ({all: FW.length, news: D.fb.news.length, ess: D.essays.length, pool: document.getElementById('fwPool').textContent}));
    check(tag, 'pool has the news cards and every essay problem', pool.all === pool.news + pool.ess && /\d+ cards/.test(pool.pool), pool);
    // source filter
    await p.click('[data-fwsrc="past"]'); await p.waitForTimeout(100);
    const past = await p.evaluate(() => fwPool().every(c => c.src === 'past') && fwPool().length > 0);
    check(tag, 'past-exam filter', past, past);
    await p.click('[data-fwsrc="all"]');
    // a full round with short timers
    await p.selectOption('#fwThink', '60'); await p.evaluate(() => fwOpen('fb-cj')); await p.waitForTimeout(200);
    let st = await p.evaluate(() => ({phase: fwPhase, t: document.getElementById('fwT').textContent, title: document.querySelector('.fwtitle').textContent, facts: document.querySelector('.fwfacts').textContent.length, rec: !!document.querySelector('#fwRec [data-fwrec]')}));
    check(tag, 'card drawn in the thinking phase', st.phase === 'think' && /^0[01]:\d\d$/.test(st.t) && /Chief Justice/.test(st.title) && st.facts > 200, st);
    check(tag, 'record button offered (browser microphone fallback)', st.rec, st);
    await p.waitForTimeout(2100);
    const ticked = await p.evaluate(() => fwLeft);
    check(tag, 'thinking timer counts down', ticked <= 58, ticked);
    await p.evaluate(() => { fwLeft = 1; }); await p.waitForTimeout(1300);
    st = await p.evaluate(() => ({phase: fwPhase, left: fwLeft}));
    check(tag, 'think time up: answer phase starts by itself', st.phase === 'answer' && st.left > 200, st);
    await p.click('#fwGo'); await p.waitForTimeout(150);
    st = await p.evaluate(() => ({phase: fwPhase, fu: (document.querySelector('.fwfu p') || {}).textContent || ''}));
    check(tag, 'second round shows the follow-up', st.phase === 'follow' && st.fu.length > 20, st);
    await p.click('#fwGo'); await p.waitForTimeout(150);   // two follow-ups on this card
    await p.click('#fwGo'); await p.waitForTimeout(200);
    st = await p.evaluate(() => ({phase: fwPhase, say: !!document.querySelector('.fwsay p'), pts: document.querySelectorAll('.fwpts li').length, cases: document.querySelectorAll('.fwout a.cref').length, grade: document.querySelectorAll('[data-fwg]').length, timer: !!document.getElementById('fwT')}));
    check(tag, 'model outline with orals line, points, cases and grading', st.phase === 'outline' && st.say && st.pts >= 4 && st.cases >= 3 && st.grade === 3 && !st.timer, st);
    // a case link in the outline opens the case card, and Back returns to the outline
    await p.click('.fwout a.cref >> nth=0'); await p.waitForTimeout(200);
    const modal = await p.evaluate(() => !document.getElementById('scrim').hidden);
    check(tag, 'case link opens the card', modal, modal);
    await p.keyboard.press('Escape'); await p.waitForTimeout(200);
    await p.click('[data-fwg="2"]'); await p.waitForTimeout(150);
    st = await p.evaluate(() => ({log: JSON.parse(localStorage.getItem('c1_fw_log') || '{}')['fb-cj'], next: !!document.querySelector('[data-fwnext]'), stat: document.getElementById('fwStat').textContent}));
    check(tag, 'grade saved; next card offered', st.log && st.log.g === 2 && st.next && /1 nailed/.test(st.stat), st);
    await p.check('#fwFresh'); await p.waitForTimeout(80);
    const skip = await p.evaluate(() => !fwPool().some(c => c.id === 'fb-cj'));
    check(tag, '“skip cards I nailed” drops it', skip, skip);
    await p.uncheck('#fwFresh');
    await p.click('[data-fwnext]'); await p.waitForTimeout(200);
    const drew = await p.evaluate(() => fwPhase === 'think' && fwCur && fwCur.id !== 'fb-cj');
    check(tag, 'draws a different card', drew, drew);
    // past-exam card shows the model answer at the end
    await p.evaluate(() => fwOpen('e20f-1')); await p.click('[data-fwskip]'); await p.waitForTimeout(150);
    const pm = await p.evaluate(() => ({model: !!document.querySelector('.fwout details'), ess: !!document.querySelector('.fwout [data-essay]')}));
    check(tag, 'past-exam card: model answer and essay-trainer link', pm.model && pm.ess, pm);
    // the news map links into the fishbowl
    await p.evaluate(() => { setTab('rules'); goToId('news-cj'); }); await p.waitForTimeout(800);
    await p.click('#news a.fwref[data-fw="fb-cj"]'); await p.waitForTimeout(300);
    st = await p.evaluate(() => ({tab: localStorage.getItem('c1_tab'), id: fwCur && fwCur.id, back: !document.getElementById('navBackBtn').hidden}));
    check(tag, 'news map link opens the card, with Back', st.tab === '"fish"' && st.id === 'fb-cj' && st.back, st);
    // universal search finds a news card
    const hs = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    check(tag, 'no horizontal scroll', hs <= 1, hs);
    if (vp.width === 400) await p.screenshot({path: path.join(process.env.SHOTS || '/tmp', 'fishbowl-400.png'), fullPage: false});
    check(tag, 'no console errors', !errs.length, errs);
    await p.close();
  }
  await b.close();
  console.log(fail ? `fishbowl: ${fail} failure(s)` : 'fishbowl: all checks passed');
  process.exit(fail ? 1 : 0);
})();
