// node site/app/make_pdfs.js [built-html] [outdir]
// Renders every print document of the desk (printDocs() in app.js: the rule maps by syllabus part, all rule maps,
// the case compendium, recall lists, hook wall and past exams) to PDF in two paper sizes, folio and A4,
// and writes manifest.json ({doc id: {folio: {file, pages, bytes}, a4: {...}}}), which build.py embeds so the
// Printables tab can list sizes and page counts. Publish the PDFs with the desk as supporting files under pdf/.
// Run after build.py, then run build.py again so the manifest is embedded.
const {chromium} = require('playwright'); const path = require('path'); const fs = require('fs');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html'), out = path.resolve(process.argv[3] || 'site/print/pdf');
fs.mkdirSync(out, {recursive: true});
const SIZES = {folio: {width: '8.5in', height: '13in'}, a4: {format: 'A4'}};
const {execFileSync} = require('child_process');
const squash = t => t.replace(/[\s\u00ad\u2010-\u2014-]+/g, '').toLowerCase();
const pagesOf = buf => (buf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 900, height: 1200}});
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(600);
  await p.evaluate(() => { window.__pdfMode = true; }); // page.pdf() fires beforeprint; keep the chosen document
  await p.evaluate(() => document.fonts && document.fonts.ready);
  const docs = await p.evaluate(() => printDocs().map(d => ({id: d.id, title: d.title, file: d.file})));
  const manifest = {};
  await p.emulateMedia({media: 'print'});
  for (const d of docs) {
    await p.evaluate(id => preparePrint(id), d.id); await p.waitForTimeout(150);
    for (const [sz, dim] of Object.entries(SIZES)) {
      await p.evaluate(sz => { PSIZE = sz; applyPSize(); }, sz); // the page's own @page rule sets the layout, so match it to the paper
      const name = `${d.file || 'consti1-' + d.id}-${sz}.pdf`, dest = path.join(out, name);
      const footer = `<div style="font:7px Helvetica,Arial,sans-serif;color:#777;width:100%;padding:0 12mm;display:flex;justify-content:space-between"><span>Consti 1 Reviewer · ${d.title.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
      const render = () => p.pdf({path: dest, ...dim, printBackground: true, preferCSSPageSize: true, margin: {top: '12mm', bottom: '14mm', left: '12mm', right: '12mm'},
        displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: footer});
      const toc = await p.evaluate(() => [...document.querySelectorAll('#printDoc [data-toc]')].map(el => { const t = document.getElementById(el.dataset.toc); const sec = t && (t.tagName === 'SECTION' || t.hasAttribute('data-top')); const h = t && (t.tagName === 'SECTION' ? t.querySelector('h2') : t); el.textContent = '000'; return {t: h ? h.textContent : '', top: !!sec}; }));
      await render();
      if (toc.length) { // second pass: find each heading's page after the contents, in order, and print the numbers
        const pages = execFileSync('pdftotext', ['-layout', dest, '-']).toString().split('\f').map(squash);
        let i = pages.findIndex(t => t.includes(squash('The syllabus begins on the next page'))) + 1, miss = 0;
        const nums = toc.map(({t, top}) => { const k = squash(t).slice(0, 36); if (!k) return ''; for (let j = i; j < pages.length; j++) if (top ? pages[j].startsWith(k) : pages[j].includes(k)) { i = j; return String(j + 1); } miss++; return ''; }); // a map's title starts its page
        await p.evaluate(nums => [...document.querySelectorAll('#printDoc [data-toc]')].forEach((el, k) => { el.textContent = nums[k]; }), nums);
        await render();
        console.log(`  contents: ${toc.length - miss} of ${toc.length} headings located`);
        if (miss) process.exitCode = 1;
      }
      const buf = fs.readFileSync(dest);
      (manifest[d.id] = manifest[d.id] || {})[sz] = {file: name, pages: pagesOf(buf), bytes: buf.length};
      console.log(name.padEnd(52), String(pagesOf(buf)).padStart(4), 'pages', (buf.length / 1048576).toFixed(2), 'MB');
    }
    await p.evaluate(() => restorePrint());
  }
  fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 1) + '\n');
  if (errs.length) { console.log('page errors:', errs); process.exitCode = 1; }
  await b.close();
})();
