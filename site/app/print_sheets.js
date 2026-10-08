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
.cl ul{font-size:7.6pt!important;line-height:1.27!important}
.cl .grp{margin-bottom:8px!important}
.cl .grp h4{font-size:9.5pt!important}
.anc{columns:3!important;column-gap:14px!important;font-size:7.1pt!important;line-height:1.27!important}
.anc p{margin:0 0 2.5px!important}
.anc .grp{margin-bottom:6px!important;break-inside:auto!important}
.anc h4{font-size:8.2pt!important}`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + file + '#print'); await p.waitForTimeout(800);
  await p.addStyleTag({content: CSS}); await p.emulateMedia({media: 'print'});
  for (const [id, name] of [['sheet1', 'issue-checklist'], ['sheet2', 'anchor-cases']]) {
    await p.evaluate(id => { for (const s of ['sheet1', 'sheet2']) document.getElementById(s).hidden = s !== id; document.querySelector('#v-print > .stack > p').hidden = true; }, id);
    const pdf = path.join(out, `consti1-${name}.pdf`);
    await p.pdf({path: pdf, width: '8.5in', height: '13in', printBackground: true, margin: {top: '0.45in', bottom: '0.45in', left: '0.5in', right: '0.5in'}});
    const pages = (fs.readFileSync(pdf, 'latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    console.log(pdf, pages, pages === 1 ? 'page' : 'PAGES (too long)');
  }
  await b.close();
})();
