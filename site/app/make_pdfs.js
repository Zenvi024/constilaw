// node site/app/make_pdfs.js [built-html] [outdir]
// Renders every print document of the desk (printDocs() in app.js: the full reviewer, the rule maps by syllabus part,
// the case compendium, recall lists, hook wall and past exams) to PDF in two paper sizes, folio and A4.
// For each PDF: finds the page of every heading in pdfOutline() by reading the rendered text in order, fills the
// reviewer's contents with those page numbers (second render), then site/app/pdf_post.py adds bookmarks and a
// running header in the part's colour (needs PyMuPDF: pip install pymupdf). Writes manifest.json
// ({doc id: {folio: {file, pages, bytes}, a4: {...}}}), which build.py embeds for the Printables tab.
// Run after build.py, then run build.py again so the manifest is embedded.
const {chromium} = require('playwright'); const path = require('path'); const fs = require('fs');
const {execFileSync} = require('child_process');
const file = path.resolve(process.argv[2] || 'site/dist/consti1-midterm-desk.html'), out = path.resolve(process.argv[3] || 'site/print/pdf');
fs.mkdirSync(out, {recursive: true});
const SIZES = {folio: {width: '8.5in', height: '13in'}, a4: {format: 'A4'}};
const squash = t => t.replace(/[\s­‐-—-]+/g, '').toLowerCase();
const pagesOf = buf => (buf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
let POST = true; try { execFileSync('python3', ['-c', 'import pymupdf']); } catch (e) { POST = false; console.log('PyMuPDF missing: no bookmarks or running headers (pip install pymupdf)'); }
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 900, height: 1200}});
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(600);
  await p.evaluate(() => { window.__pdfMode = true; }); // page.pdf() fires beforeprint; keep the chosen document
  await p.evaluate(() => document.fonts && document.fonts.ready);
  const docs = await p.evaluate(() => printDocs().map(d => ({id: d.id, title: d.title, file: d.file})));
  const manifest = {}; let bad = 0;
  await p.emulateMedia({media: 'print'});
  for (const d of docs) {
    await p.evaluate(id => preparePrint(id), d.id); await p.waitForTimeout(150);
    for (const [sz, dim] of Object.entries(SIZES)) {
      await p.evaluate(sz => { PSIZE = sz; applyPSize(); }, sz); // the page's own @page rule sets the layout, so match it to the paper
      const name = `${d.file || 'consti1-' + d.id}-${sz}.pdf`, dest = path.join(out, name);
      const footer = `<div style="font:7px Helvetica,Arial,sans-serif;color:#777;width:100%;padding:0 18mm;display:flex;justify-content:space-between"><span>Consti 1 Reviewer · ${d.title.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
      const render = () => p.pdf({path: dest, ...dim, printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: footer});
      const hasToc = await p.evaluate(() => { const ts = document.querySelectorAll('#printDoc [data-toc]'); ts.forEach(el => el.textContent = '000'); return ts.length > 0; });
      const outline = await p.evaluate(() => pdfOutline());
      await render();
      // find each heading's page, in document order (map titles and forced breaks start their page)
      const pages = execFileSync('pdftotext', ['-layout', dest, '-']).toString().split('\f').map(squash);
      let i = 0, miss = 0;
      for (const o of outline) {
        if (o.same) continue;
        const k = squash(o.text).slice(0, 36); let hit = -1;
        for (let j = i; j < pages.length; j++) if (o.top ? pages[j].startsWith(k) : pages[j].includes(k)) { hit = j; break; }
        if (hit < 0) { miss++; o.page = 0; continue; }
        o.page = hit + 1; i = hit;
        if (o.el === 'pd-toc') i = Math.max(i, pages.findIndex(t => t.includes(squash('The rule maps begin on the next page'))) + 1);
      }
      outline.forEach((o, k) => { if (o.same) { const n = outline.slice(k + 1).find(x => !x.same && x.page); o.page = n ? n.page : 0; } });
      if (hasToc) { await p.evaluate(nums => document.querySelectorAll('#printDoc [data-toc]').forEach(el => { el.textContent = nums[el.dataset.toc] || ''; }), Object.fromEntries(outline.filter(o => o.page).map(o => [o.el, String(o.page)]))); await render(); }
      if (POST) { const j = dest + '.json'; fs.writeFileSync(j, JSON.stringify(outline.filter(o => o.page))); execFileSync('python3', [path.join(__dirname, 'pdf_post.py'), dest, j]); fs.unlinkSync(j); }
      const buf = fs.readFileSync(dest);
      (manifest[d.id] = manifest[d.id] || {})[sz] = {file: name, pages: pagesOf(buf), bytes: buf.length};
      console.log(name.padEnd(52), String(pagesOf(buf)).padStart(4), 'pages', (buf.length / 1048576).toFixed(2), 'MB', miss ? `(${miss} of ${outline.length} headings not found)` : `(${outline.length} headings)`);
      if (miss) bad++;
    }
    await p.evaluate(() => restorePrint());
  }
  fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 1) + '\n');
  if (errs.length) { console.log('page errors:', errs); process.exitCode = 1; }
  if (bad) process.exitCode = 1;
  await b.close();
})();
