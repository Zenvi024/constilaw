// node site/app/print_sheets.js [built-html] [outdir] -> one-page folio PDFs of the two printables
const {chromium} = require('playwright'); const path = require('path'); const fs = require('fs');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html'), out = process.argv[3] || 'site/print';
fs.mkdirSync(out, {recursive: true});
const CSS = `@page{size:8.5in 13in;margin:0.45in 0.5in}
html,body{background:#fff!important;color:#111!important}
:root{--ink:#111;--muted:#555;--line:#ccc;--accent:#1d3a9e;--card:#fff;--paper:#fff}
.page{max-width:none!important;padding:0!important}
.sheet{border:0!important;padding:0!important;max-width:none!important}
.sheet h2{font-size:15pt!important}
.cl{columns:2!important;column-gap:22px!important}
.cl ul{font-size:calc(7.6pt * var(--k,1))!important;line-height:1.27!important}
.cl .grp{margin-bottom:calc(8px * var(--k,1))!important}
.cl .grp h4{font-size:calc(9.5pt * var(--k,1))!important}
.anc{columns:3!important;column-gap:14px!important;font-size:calc(7.1pt * var(--k,1))!important;line-height:1.27!important}
.anc p{margin:0 0 calc(2.5px * var(--k,1))!important}
.anc .grp{margin-bottom:calc(6px * var(--k,1))!important;break-inside:auto!important}
.anc h4{font-size:calc(8.2pt * var(--k,1))!important}`;
const OPTS = {width: '8.5in', height: '13in', printBackground: true, margin: {top: '0.45in', bottom: '0.45in', left: '0.5in', right: '0.5in'}};
const pagesOf = buf => (buf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
// Fill the folio page: columns run top to bottom at the full printable height (no balancing),
// and the text scale is the largest at which nothing spills into an extra column.
const PAGE_W = 720, PAGE_H = 1161; // printable area in CSS px: 7.5in x 12.1in
const {execFileSync} = require('child_process');
const squash = t => t.replace(/[\s\u00ad-]+/g, '');
const pdfText = buf => execFileSync('pdftotext', ['-raw', '-', '-'], {input: buf}).toString();
async function fit(p, sel){
  const setK = k => p.evaluate(([k, sel, H]) => {
    document.documentElement.style.setProperty('--k', k);
    const el = document.querySelector(sel);
    el.style.columnFill = 'auto'; el.style.height = 'auto'; el.style.overflow = 'hidden'; // clipped, so the page can never widen and be shrunk to fit
    const top = el.getBoundingClientRect().top + window.scrollY; // from the top of the printed document
    el.style.height = Math.floor(H - top - 6 - (window.__trim || 0)) + 'px';
    return el.scrollWidth <= el.clientWidth + 1; // false if any text spilled into a clipped extra column
  }, [k, sel, PAGE_H]);
  // the last line of the sheet must be in the PDF: with top-to-bottom columns, overflow would push it off the page
  const last = squash(await p.evaluate(sel => { const els = document.querySelectorAll(sel + ' p, ' + sel + ' li'); return els[els.length - 1].textContent; }, sel)).slice(-30);
  const ok = async k => { if (!(await setK(k))) return false; const buf = await p.pdf(OPTS); return pagesOf(buf) === 1 && squash(pdfText(buf)).includes(last); };
  let trim = 0; await p.evaluate(() => window.__trim = 0);
  while (!(await ok(0.7)) && trim < 300){ trim += 6; await p.evaluate(t => window.__trim = t, trim); }
  let lo = 0.7, hi = 1.8;
  for (let i = 0; i < 11; i++){ const mid = (lo + hi) / 2; if (await ok(mid)) lo = mid; else hi = mid; }
  await setK(lo);
  return lo;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: PAGE_W, height: PAGE_H}});
  await p.goto('file://' + file + '#print'); await p.waitForTimeout(800);
  await p.addStyleTag({content: CSS}); await p.emulateMedia({media: 'print'});
  for (const full of [false, true]) {
    if (full) { await p.emulateMedia({media: 'screen'}); await p.click('#scopeBtn'); await p.click('[data-tab="today"]'); await p.click('[data-tab="print"]'); await p.emulateMedia({media: 'print'}); }
    for (const [id, name] of [['sheet1', 'issue-checklist'], ['sheet2', 'anchor-cases']]) {
      await p.evaluate(id => { for (const s of ['sheet1', 'sheet2']) document.getElementById(s).hidden = s !== id; document.querySelector('#v-print > .stack > p').hidden = true; }, id);
      const pdf = path.join(out, `consti1-${name}${full ? '-with-citizenship-territory' : ''}.pdf`);
      const k = await fit(p, id === 'sheet1' ? '#sheet1 .cl' : '#sheet2 .anc');
      await p.pdf({path: pdf, ...OPTS});
      const pages = pagesOf(fs.readFileSync(pdf));
      console.log(pdf, pages, pages === 1 ? 'page' : 'PAGES (too long)', `text scale ${k.toFixed(3)}`);
    }
  }
  await b.close();
})();
