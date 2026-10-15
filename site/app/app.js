/* ================= core ================= */
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const store = {
  get(k, d){ try { const v = localStorage.getItem("c1_" + k); return v ? JSON.parse(v) : d; } catch(e){ return d; } },
  set(k, v){ try { localStorage.setItem("c1_" + k, JSON.stringify(v)); } catch(e){} }
};
const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--){ const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const LET = "abcdefgh";
const TOP = Object.fromEntries(D.topics.map(t => [t.key, t]));
const CASE = Object.fromEntries(D.cases.map(c => [c.id, c]));
const ESS = Object.fromEntries(D.essays.map(e => [e.id, e]));
const ISS = {}; D.issues.forEach(g => g.items.forEach(i => ISS[i.id] = {...i, g: g.g}));
const tname = k => (TOP[k] ? TOP[k].name : k);

/* ================= scope toggle: citizenship and territory ================= */
const OUT_TOPICS = ["cit", "terr"], OUT_SECS = ["cit", "terr"], OUT_ISSUES = ["ppl_citizen", "ppl_dual", "terr"];
let HIDE = store.get("hideCitTerr", true);
const shownT = t => !HIDE || !OUT_TOPICS.includes(t);
const TOPS = () => D.topics.filter(t => shownT(t.key));
const CASES = () => D.cases.filter(c => shownT(c.t));
const MCQS = () => D.mcq.filter(q => shownT(q.t));
const ISSUES = () => D.issues.map(g => ({...g, items: g.items.filter(i => !HIDE || !OUT_ISSUES.includes(i.id))})).filter(g => g.items.length);

/* ================= tabs ================= */
const TABS = ["today","rules","lists","cases","exams","spot","write","print"];
function setTab(t, push){
  if (!TABS.includes(t)) t = "today";
  TABS.forEach(x => { $("v-" + x).hidden = x !== t; }); $("v-search").hidden = true;
  document.querySelectorAll(".tabs [data-tab]").forEach(b => b.setAttribute("aria-selected", b.dataset.tab === t));
  store.set("tab", t);
  if (push !== false){ try { history.replaceState(null, "", "#" + t); } catch(e){} }
  if (t === "today") renderToday();
  if (t === "print") renderPrint();
  if (t === "lists" && !$("lList").hidden) renderLists();
  if (t === "rules") requestAnimationFrame(spy);
  window.scrollTo({top: 0});
}
document.querySelector(".tabs").addEventListener("click", e => { const b = e.target.closest("[data-tab]"); if (b) setTab(b.dataset.tab); });

/* ================= countdown ================= */
function manilaToday(){ // yyyy-mm-dd in Asia/Manila
  try { return new Intl.DateTimeFormat("en-CA", {timeZone: "Asia/Manila", year: "numeric", month: "2-digit", day: "2-digit"}).format(new Date()); }
  catch(e){ return new Date().toISOString().slice(0, 10); }
}
function daysTo(iso){ const a = new Date(manilaToday() + "T00:00:00Z"), b = new Date(iso + "T00:00:00Z"); return Math.round((b - a) / 864e5); }
function renderClock(){
  const n = daysTo(D.examDate);
  if (n > 1){ $("cdN").textContent = n; $("cdL").textContent = "days to the midterm (Fri, Oct 16, 10:00 AM)"; }
  else if (n === 1){ $("cdN").textContent = "1"; $("cdL").textContent = "day to go. Light review, early night."; }
  else if (n === 0){ $("cdN").textContent = "Today"; $("cdL").textContent = "Checklist and anchor list, then go."; }
  else { $("cdN").textContent = "Done"; $("cdL").textContent = "The midterm was on Oct 16."; }
}

/* ================= case modal ================= */
function caseHTML(c){
  const t = TOP[c.t];
  return `<div class="spread"><h3 id="mTitle">${esc(c.n)}</h3><button class="btn small ghost" data-close>Close</button></div>
  ${c.hk ? `<div style="margin:2px 0 6px">${hookChip(c, true)} <span class="tiny">${esc(HC_LBL[c.hc])}</span></div>` : ""}<div class="meta">${esc(c.y)} · ${esc(c.sub || (t ? t.name : ""))}${c.a ? " · anchor case" : ""}${c.ref ? " · mentioned in the rule maps; not on the syllabus list, not drilled" : ""}</div>
  <dl>
    <div><dt>Rule</dt><dd class="rule">${esc(c.r)}</dd></div>
    ${c.test ? `<div><dt>Test</dt><dd>${esc(c.test)}</dd></div>` : ""}
    ${c.f ? `<div><dt>Facts</dt><dd>${esc(c.f)}</dd></div>` : ""}
    ${c.h ? `<div><dt>Holding</dt><dd>${esc(c.h)}</dd></div>` : ""}
    ${c.x ? `<div><dt>Use it when</dt><dd>${esc(c.x)}</dd></div>` : ""}
  </dl>
  ${c.g ? `<div class="gatn"><strong>Gatmaytan:</strong> ${esc(c.g)}</div>` : ""}
  ${c.w ? `<div class="warnn"><strong>Caution:</strong> ${esc(c.w)}</div>` : ""}
  ${c.dg ? `<details class="dgrev"><summary>2026 block reviewer: full digest</summary><div class="dgnote">Student-written class reviewer, kept as written. The card above was checked against it; where they differ, follow the card.</div>${dgHTML(c.dg)}</details>` : ""}
  ${t && t.sec ? `<div><button class="btn small" data-gosec="${t.sec}">Open the rule map: ${esc(t.name)}</button></div>` : ""}`;
}
function dgHTML(txt){
  return `<div class="dgtxt">${txt.split("\n").map(l => l.trim()).filter(Boolean).map(l => {
    const m = l.match(/^([●•○◦▪■\-–]|\d+\.|[a-z]\.)\s*/);
    const sub = m && /[○◦▪■\-–]|[a-z]\./.test(m[1]);
    const body = m && /[●•○◦▪■\-–]/.test(m[1]) ? l.slice(m[0].length) : l;
    return `<p class="${sub ? "l2" : m ? "l1" : "l0"}">${esc(body)}</p>`;
  }).join("")}</div>`;
}
let lastFocus = null;
function openModal(html){ lastFocus = document.activeElement; $("modal").innerHTML = html; $("scrim").hidden = false; const b = $("modal").querySelector("[data-close]"); if (b) b.focus(); }
function closeModal(){ $("scrim").hidden = true; $("modal").innerHTML = ""; if (lastFocus && lastFocus.focus) lastFocus.focus(); }
function openCase(id){ const c = CASE[id]; if (c) openModal(caseHTML(c)); }
$("scrim").addEventListener("click", e => {
  if (e.target === $("scrim") || e.target.closest("[data-close]")) { closeModal(); return; }
  const g = e.target.closest("[data-gosec]"); if (g){ closeModal(); setTab("rules"); openSecById(g.dataset.gosec); }
});
document.addEventListener("keydown", e => { if (e.key === "Escape" && !$("scrim").hidden) closeModal(); });
document.addEventListener("click", e => {
  const a = e.target.closest("a.cref,[data-case]"); if (a){ e.preventDefault(); openCase(a.dataset.c || a.dataset.case); return; }
  const r = e.target.closest("a.eref,[data-essay]"); if (r){ e.preventDefault(); openEssay(r.dataset.e || r.dataset.essay); return; }
  const s = e.target.closest("[data-spot]"); if (s){ e.preventDefault(); openSpot(s.dataset.spot); return; }
  const v = e.target.closest("[data-rv]"); if (v){ e.preventDefault(); setTab("rules"); goToId(v.dataset.rv); return; }
});
const caseLinks = ids => (ids || []).filter(id => CASE[id]).map(id => `<a class="cref" data-c="${id}" href="#">${esc(CASE[id].n)}</a>`).join("; ");

/* ================= SRS ================= */
const MIN = 60000, STEPS = [1, 10, 60, 360, 1440, 2880, 5760], STEP_LBL = ["1 min","10 min","1 hr","6 hr","1 day","2 days","4 days"];
let SRS = store.get("srs", {});
function rate(k, g){ // 0 again, 1 hard, 2 good, 3 easy
  const st = SRS[k] || {s: -1, n: 0, l: 0};
  if (g === 0){ st.s = 0; st.l++; } else if (g === 1){ st.s = Math.max(st.s, 0); } else if (g === 2){ st.s = Math.min(Math.max(st.s + 1, 1), STEPS.length - 1); } else { st.s = Math.min(Math.max(st.s + 2, 3), STEPS.length - 1); }
  const mins = g === 1 ? Math.max(5, STEPS[st.s] / 2) : STEPS[st.s];
  st.d = Date.now() + mins * MIN; st.n++; SRS[k] = st; store.set("srs", SRS); dueBadge();
  fixTrack(k, g);
}
function nextLbl(k, g){
  const st = SRS[k] || {s: -1}; let s = st.s;
  if (g === 0) s = 0; else if (g === 1) s = Math.max(s, 0); else if (g === 2) s = Math.min(Math.max(s + 1, 1), STEPS.length - 1); else s = Math.min(Math.max(s + 2, 3), STEPS.length - 1);
  if (g === 1){ const m = Math.max(5, STEPS[s] / 2); return m >= 60 ? Math.round(m / 60) + " hr" : m + " min"; }
  return STEP_LBL[s];
}
const isDue = k => SRS[k] && SRS[k].d <= Date.now();
const dueKeys = () => Object.keys(SRS).filter(k => isDue(k) && validKey(k));
function validKey(k){ const [p, id] = k.split(":"); if (p === "m"){ const q = D.mcq.find(x => x.id === id); return !!q && shownT(q.t); } if (p === "l") return !!LIST[id] && shownT(LIST[id].t); return ["cr", "fc", "rc"].includes(p) && !!CASE[id] && shownT(CASE[id].t); }
function dueBadge(){ const n = dueKeys().length, b = $("dueBadge"); b.textContent = n; b.hidden = n === 0; }
setInterval(dueBadge, 30000);

/* ================= TODAY ================= */
let planDay = null;
function renderToday(){
  const today = manilaToday();
  const days = D.plan;
  if (!planDay) planDay = (days.find(d => d.date === today) || (today < days[0].date ? days[0] : days[days.length - 1])).date;
  const d = days.find(x => x.date === planDay);
  $("dayH").textContent = d.label;
  $("dayF").textContent = (d.date === today ? "Today · " : "") + d.focus;
  $("dayTodo").innerHTML = d.items.map(it => `<li><span class="k">${esc(it.k)}</span><div>${esc(it.t)}${(it.rv || it.e || it.go || it.sp) ? `<div class="links">${(it.rv || []).map(id => `<button class="btn small" data-rv="${id}">${esc(rvTitle(id))}</button>`).join("")}${(it.e || []).map(id => ESS[id] ? `<button class="btn small" data-essay="${id}">Write: ${esc(ESS[id].short)}</button>` : "").join("")}${(it.sp || []).map(id => ESS[id] ? `<button class="btn small" data-spot="${id}">Spot: ${esc(ESS[id].short)}</button>` : "").join("")}${it.go ? `<button class="btn small" data-go="${it.go}">${esc(it.goL)}</button>` : ""}</div>` : ""}</div></li>`).join("");
  $("week").innerHTML = days.map(x => `<button data-day="${x.date}" aria-current="${x.date === planDay}" class="${x.date < today ? "past" : ""}"><span class="w">${esc(x.short)}</span><span>${esc(x.focus)}</span></button>`).join("");
  // stats
  const SYL = CASES().filter(c => !c.ref);
  const seen = SYL.filter(c => SRS["cr:" + c.id] || SRS["fc:" + c.id] || SRS["rc:" + c.id]).length;
  const known = SYL.filter(c => ["cr:","fc:","rc:"].some(p => SRS[p + c.id] && SRS[p + c.id].s >= 3)).length;
  const qh = store.get("qhist", {}); const qa = Object.values(qh); const qr = qa.filter(x => x.r === 1).length;
  const att = store.get("attempts", {}); const al = Object.values(att).flat(); const avg = al.length ? (al.reduce((s, a) => s + a.score, 0) / al.length) : 0;
  $("stats").innerHTML = [
    [dueKeys().length, "cards due now"],
    [`${seen}/${SYL.length}`, `cases drilled · ${known} at 1 day or more`],
    [qa.length ? Math.round(100 * qr / qa.length) + "%" : "–", `MCQ accuracy (${qa.length} answered)`],
    [al.length ? avg.toFixed(1) : "–", `average essay score /10 (${al.length} written)`]
  ].map(([v, k]) => `<div class="stat"><div class="v">${v}</div><div class="k">${k}</div></div>`).join("");
  renderSessPlan(); renderFix();
}
  // (session plan and fix list are refreshed by renderToday)
$("week").addEventListener("click", e => { const b = e.target.closest("[data-day]"); if (b){ planDay = b.dataset.day; renderToday(); const t = document.querySelector(".dayplan").getBoundingClientRect().top; if (t < 0) window.scrollTo({top: window.scrollY + t - 12, behavior: "smooth"}); } });
$("dayTodo").addEventListener("click", e => { const b = e.target.closest("[data-go]"); if (b) goAction(b.dataset.go); });
function goAction(g){
  if (g === "due"){ setTab("cases"); setCaseMode("drill"); startDrill(true); }
  else if (g.startsWith("mcq:")){ setTab("exams"); setExamMode("mcq"); qExamSel = new Set(g.slice(4).split(",")); renderQSetup(); }
  else if (g === "print") setTab("print");
  else if (g === "session") startRun(buildSession().cards, "Session");
  else if (g === "fix"){ const ks = fixKeys(); if (ks.length) $("fixGo").click(); else { setTab("cases"); setCaseMode("drill"); startDrill(true); } }
  else if (g.startsWith("lists:")){ // lists:<topic> or lists:due
    const t = g.slice(6); setTab("lists"); $("lRun").hidden = true; $("lSetup").hidden = false; $("lList").hidden = false;
    $("lq").value = ""; $("lTopic").value = t === "due" ? "" : t; renderLists();
    startLists(lDrillCards(t === "due"));
  }
  else if (g.startsWith("blur:")){ BLUR = true; store.set("blur", true); applyBlur(); setTab("rules"); openSecById(g.slice(5)); }
  else if (g.startsWith("drill:")){ // drill:<topics> or drill:<dir>:<topics>; topics "all" or "anchors"
    const p = g.split(":"); const topics = p.length === 3 ? p[2] : p[1]; if (p.length === 3) dDir = p[1];
    setTab("cases"); setCaseMode("drill");
    $("dAnchor").checked = topics === "anchors";
    dTop = new Set(topics === "all" || topics === "anchors" ? D.topics.map(t => t.key) : topics.split(","));
    renderDSetup();
  }
}
$("goDue").onclick = () => goAction("due");
$("goMcq").onclick = () => { setTab("exams"); setExamMode("mcq"); $("qN").value = "10"; startQuiz(); };

/* ================= RULE MAPS ================= */
const SECS = [...document.querySelectorAll("#rcontent section.rv")];
let curSec = 0;
function rvTitle(id){ const el = document.getElementById(id); if (!el) return id; const s = el.closest("section.rv"); return el.tagName === "SECTION" ? el.dataset.title : el.textContent; }
const secShown = i => !HIDE || !OUT_SECS.includes(SECS[i].id);
const visIdx = () => SECS.map((s, i) => i).filter(secShown);
function buildSide(){
  $("rsecs").innerHTML = SECS.map((s, i) => !secShown(i) ? "" : `<li data-i="${i}"><button data-sec="${i}">${esc(s.dataset.title)}<small>${esc(s.dataset.short)}</small></button></li>`).join("");
  $("rsel").innerHTML = SECS.map((s, i) => !secShown(i) ? "" : `<option value="${i}">${esc(s.dataset.title)}</option>`).join("");
}
function openSec(i, scroll){
  curSec = i; SECS.forEach((s, j) => s.hidden = j !== i);
  document.querySelectorAll("#rsecs>li").forEach(li => {
    const on = +li.dataset.i === i; li.classList.toggle("on", on);
    const old = li.querySelector("ul"); if (old) old.remove();
    if (on){ const hs = [...SECS[i].querySelectorAll("h3[id]")]; li.insertAdjacentHTML("beforeend", `<ul>${hs.map(h => `<li><a href="#" data-h="${h.id}">${esc(h.textContent)}</a></li>`).join("")}</ul>`); }
  });
  $("rsel").value = i;
  $("rtoc").innerHTML = `<option value="">Jump to a heading…</option>` + [...SECS[i].querySelectorAll("h3[id]")].map(h => `<option value="${h.id}">${esc(h.textContent)}</option>`).join("");
  const vis = visIdx(), prevI = vis.filter(j => j < i).pop(), nextI = vis.find(j => j > i);
  $("rprev").hidden = prevI === undefined; $("rnext").hidden = nextI === undefined;
  if (prevI !== undefined){ $("rprev").textContent = "← " + SECS[prevI].dataset.title; $("rprev").dataset.to = prevI; }
  if (nextI !== undefined){ $("rnext").textContent = SECS[nextI].dataset.title + " →"; $("rnext").dataset.to = nextI; }
  store.set("sec", i);
  if (scroll !== false) window.scrollTo({top: 0});
  buildMtoc(); updateBlurCt(); requestAnimationFrame(spy);
}
function openSecById(id){ const i = SECS.findIndex(s => s.id === id); if (i >= 0) openSec(i); }
function goToId(id){
  const el = document.getElementById(id); if (!el) return;
  const sec = el.tagName === "SECTION" ? el : el.closest("section.rv"); const i = SECS.indexOf(sec);
  if (i !== curSec) openSec(i, false);
  if (el.tagName === "SECTION"){ window.scrollTo({top: 0}); return; }
  el.scrollIntoView({block: "start"}); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1600);
}
$("rsecs").addEventListener("click", e => {
  const a = e.target.closest("[data-h]"); if (a){ e.preventDefault(); goToId(a.dataset.h); return; }
  const b = e.target.closest("[data-sec]"); if (b){ clearSearch(); openSec(+b.dataset.sec); }
});
$("rsel").onchange = () => { clearSearch(); openSec(+$("rsel").value); };
$("rtoc").onchange = () => { const v = $("rtoc").value; if (v) goToId(v); $("rtoc").value = ""; };
$("rprev").onclick = () => openSec(+$("rprev").dataset.to); $("rnext").onclick = () => openSec(+$("rnext").dataset.to);
let blocks = null, sT = null, hits = [];
function clearSearch(){ $("rq").value = ""; $("rresults").hidden = true; $("rresults").innerHTML = ""; }
function runSearch(){
  const q = $("rq").value.trim().toLowerCase(), box = $("rresults");
  if (q.length < 3){ box.hidden = true; box.innerHTML = ""; return; }
  blocks = blocks || [...document.querySelectorAll("#rcontent :is(p,li,.codal,td,h3,h4,.test,aside)")].filter(el => !el.querySelector("p,li,td"));
  hits = blocks.filter(el => el.textContent.toLowerCase().includes(q) && secShown(SECS.indexOf(el.closest("section.rv"))));
  box.hidden = false;
  box.innerHTML = `<div class="spread"><span class="lbl">${hits.length} match${hits.length === 1 ? "" : "es"}${hits.length > 120 ? " · first 120" : ""}</span><button class="btn small ghost" id="rclear">Clear</button></div>` +
    hits.slice(0, 120).map((el, k) => { const sec = el.closest("section.rv"); const txt = el.textContent.replace(/\s+/g, " ").trim(); const p = txt.toLowerCase().indexOf(q); const s = Math.max(0, p - 70);
      return `<button class="btn res" data-k="${k}"><small>${esc(sec.dataset.title)}</small>${s > 0 ? "…" : ""}${esc(txt.slice(s, p))}<mark>${esc(txt.slice(p, p + q.length))}</mark>${esc(txt.slice(p + q.length, p + q.length + 130))}…</button>`; }).join("");
}
$("rq").addEventListener("input", () => { clearTimeout(sT); sT = setTimeout(runSearch, 220); });
$("rresults").addEventListener("click", e => { if (e.target.id === "rclear"){ clearSearch(); return; } const b = e.target.closest("[data-k]"); if (b){ const el = hits[+b.dataset.k]; const sec = el.closest("section.rv"); const i = SECS.indexOf(sec); if (i !== curSec) openSec(i, false); el.scrollIntoView({block: "center"}); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1600); } });

/* ================= rule maps: blur mode and sticky headings ================= */
// Blur mode hides case names, bold key terms and numbers (votes, periods, fractions); tap one to reveal it.
const NUMW = "one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|eighteen|twenty|twenty-one|twenty-four|twenty-five|thirty|thirty-five|forty|forty-five|fifty|sixty|ninety|hundred";
const NUMRX = new RegExp(String.raw`₱\s?[\d,.]+(?:\s(?:million|billion))?|\b\d+(?:[.,]\d+)?\s?(?:%|per\s?cent\b)|\b(?:one|two|three|four)-(?:half|thirds?|fourths?|fifths?|twelfths?)\b|\b(?:\d+|${NUMW})-(?:day|year|month|hour|week|member|seat)\b|\b(?:\d+(?:[–-]\d+)?|${NUMW})(?:\s(?:to|or|and)\s(?:\d+|${NUMW}))?\s(?:consecutive\s|calendar\s|session\s)?(?:days?|years?|months?|hours?|weeks?|members?|senators?|representatives?|votes?|nautical\smiles?|seats?|nominees?|terms?|justices?|readings?|districts?|signatures?|candidates?)\b`, "gi");
(function markBlur(){
  const root = $("rcontent"), skip = el => !!el.closest("h2,h3,h4,.lede,.art,th,a,strong,b,.legend");
  const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {acceptNode: n => n.nodeValue.trim() && !skip(n.parentElement) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT});
  const nodes = []; while (tw.nextNode()) nodes.push(tw.currentNode);
  nodes.forEach(n => {
    const t = n.nodeValue; NUMRX.lastIndex = 0; if (!NUMRX.test(t)) return; NUMRX.lastIndex = 0;
    const f = document.createDocumentFragment(); let last = 0, m;
    while ((m = NUMRX.exec(t))){ f.append(t.slice(last, m.index)); const sp = document.createElement("span"); sp.className = "num"; sp.textContent = m[0]; f.append(sp); last = m.index + m[0].length; }
    f.append(t.slice(last)); n.replaceWith(f);
  });
  root.querySelectorAll("strong,b,a.cref,.num").forEach(el => {
    if (el.closest("h2,h3,h4,.lede,.art,th,.legend") || el.parentElement.closest(".bl")) return;
    if ((el.tagName === "STRONG" || el.tagName === "B") && (/:\s*$/.test(el.textContent) || el.matches(".test>b:first-child"))) return;
    el.classList.add("bl");
  });
})();
let BLUR = store.get("blur", false);
function applyBlur(){
  $("rcontent").classList.toggle("blurmode", BLUR);
  $("blurBtn").setAttribute("aria-pressed", BLUR); $("blurBtn").textContent = BLUR ? "Blur mode: on" : "Blur mode";
  $("blurReset").hidden = !BLUR; $("blurCt").hidden = !BLUR;
  document.querySelectorAll("#rcontent .bl.shown").forEach(x => x.classList.remove("shown"));
  updateBlurCt();
}
function updateBlurCt(){
  if (!BLUR) return;
  const all = SECS[curSec].querySelectorAll(".bl").length, shown = SECS[curSec].querySelectorAll(".bl.shown").length;
  $("blurCt").textContent = `${shown} of ${all} revealed`;
}
$("blurBtn").onclick = () => { BLUR = !BLUR; store.set("blur", BLUR); applyBlur(); };
$("blurReset").onclick = () => { SECS[curSec].querySelectorAll(".bl.shown").forEach(x => x.classList.remove("shown")); updateBlurCt(); };
$("rcontent").addEventListener("click", e => {
  if (!BLUR) return;
  const el = e.target.closest(".bl:not(.shown)"); if (!el) return;
  e.preventDefault(); e.stopPropagation();
  el.classList.add("shown"); el.querySelectorAll(".bl").forEach(x => x.classList.add("shown"));
  updateBlurCt();
}, true);
// sticky mini table of contents with the current heading highlighted, plus a reading-progress line
function buildMtoc(){
  const hs = [...SECS[curSec].querySelectorAll("h3[id]")];
  $("mtoc").innerHTML = hs.map(h => `<a href="#" data-h="${h.id}" title="${esc(h.textContent)}">${esc(h.textContent)}</a>`).join("");
}
$("mtoc").addEventListener("click", e => { const a = e.target.closest("[data-h]"); if (a){ e.preventDefault(); goToId(a.dataset.h); } });
let spyCur = null, spyRaf = 0;
function spy(){
  spyRaf = 0; if ($("v-rules").hidden) return;
  const sec = SECS[curSec], off = $("rstick").getBoundingClientRect().bottom + 16;
  let cur = null; sec.querySelectorAll("h3[id]").forEach(h => { if (h.getBoundingClientRect().top <= off) cur = h.id; });
  if (cur !== spyCur){
    spyCur = cur;
    $("mtoc").querySelectorAll("a").forEach(a => { const on = a.dataset.h === cur; a.setAttribute("aria-current", on); if (on){ const bar = $("mtoc"); bar.scrollTo({left: a.offsetLeft - bar.offsetLeft - bar.clientWidth / 2 + a.offsetWidth / 2, behavior: "smooth"}); } });
    document.querySelectorAll("#rsecs ul a").forEach(a => a.classList.toggle("on", a.dataset.h === cur));
  }
  const r = sec.getBoundingClientRect(), span = Math.max(1, r.height - (innerHeight - off));
  $("rprog").style.width = Math.min(100, Math.max(0, 100 * (off - r.top) / span)) + "%";
}
window.addEventListener("scroll", () => { if (!spyRaf) spyRaf = requestAnimationFrame(spy); }, {passive: true});
window.addEventListener("resize", () => { if (!spyRaf) spyRaf = requestAnimationFrame(spy); });

/* ================= rule-map visuals: steppers, calculators, walk-throughs and test-me covers ================= */
document.querySelectorAll("#rcontent .stepper").forEach(st => {
  const btns = [...st.querySelectorAll(".sp-btns button")], ps = [...st.querySelectorAll(".sp-p")];
  const show = i => { btns.forEach((b, j) => b.setAttribute("aria-pressed", j === i)); ps.forEach((p, j) => p.hidden = j !== i); };
  btns.forEach((b, i) => b.addEventListener("click", () => show(i))); show(+(st.dataset.start || 0));
});
document.querySelectorAll("#rcontent .qwidget").forEach(w => {
  const N = +w.dataset.total || 24, dots = w.querySelector(".qdots"), st = new Array(N).fill(0); // 0 present, 1 absent in the country, 2 abroad
  dots.innerHTML = st.map((_, i) => `<button type="button" aria-label="Senator ${i + 1}"></button>`).join("");
  const bs = [...dots.children];
  const paint = () => {
    bs.forEach((b, i) => { b.className = ["", "out", "abroad"][st[i]]; b.title = ["present", "absent (in the country)", "abroad"][st[i]]; });
    const abroad = st.filter(x => x === 2).length, present = st.filter(x => x === 0).length, base = N - abroad, need = Math.floor(base / 2) + 1, ok = present >= need;
    w.querySelector(".qread").innerHTML = `<div class="vn plain"><b>${present}</b><span class="s">present</span></div><div class="vn plain"><b>${base}</b><span class="s">base (all ${N} minus ${abroad} abroad)</span></div><div class="vn plain"><b>${need}</b><span class="s">needed for a quorum</span></div><div class="vn ${ok ? "ok" : "no"}"><b>${ok ? "Quorum" : "No quorum"}</b><span class="s">${ok ? "may do business" : "may only adjourn or compel attendance"}</span></div><div class="vn sun"><b>${Math.floor(N / 2) + 1}</b><span class="s">votes to elect the Senate President today: a majority of <em>all</em> ${N} (Sec. 16(1))</span></div>`;
  };
  bs.forEach((b, i) => b.addEventListener("click", () => { st[i] = (st[i] + 1) % 3; paint(); }));
  w.querySelector("[data-q=reset]").onclick = () => { st.fill(0); paint(); };
  w.querySelector("[data-q=avelino]").onclick = () => { st.fill(0); st[N - 1] = 2; for (let i = N - 12; i < N - 1; i++) st[i] = 1; paint(); };
  paint();
});
// vote counter: turns each rung of the vote ladder into a head count for the chamber you pick
document.querySelectorAll("#rcontent .votec").forEach(w => {
  const all = w.querySelector("[data-v=all]"), pres = w.querySelector("[data-v=present]");
  const paint = () => {
    const n = Math.max(1, +all.value || 24), p = Math.min(n, Math.max(0, +pres.value || 0)), maj = Math.floor(n / 2) + 1;
    const val = {p5: Math.ceil(p / 5), quorum: maj, maj, two3: Math.ceil(2 * n / 3), three4: Math.ceil(3 * n / 4)};
    const how = {p5: `of ${p} present`, quorum: `of ${n} Members`, maj: `of all ${n}`, two3: `of all ${n}`, three4: `of all ${n}`};
    w.querySelectorAll(".rung[data-r]").forEach(r => { r.querySelector(".cnt").textContent = `${val[r.dataset.r]} ${how[r.dataset.r]}`; });
  };
  w.querySelectorAll("[data-set]").forEach(b => b.addEventListener("click", () => { all.value = b.dataset.set; pres.value = b.dataset.set; paint(); }));
  [all, pres].forEach(x => x.addEventListener("input", paint)); paint();
});
// Commission on Appointments: proportional representation, fractions never rounded up
document.querySelectorAll("#rcontent .cacalc").forEach(w => {
  const preset = JSON.parse(w.dataset.parties), tot = w.querySelector("[data-v=total]");
  const body = w.querySelector("tbody");
  const load = ps => { body.innerHTML = ps.map(([n, k]) => `<tr><td>${esc(n)}</td><td><input type="number" min="0" value="${k}" aria-label="${esc(n)} members"></td><td class="sh"></td><td class="hi"></td></tr>`).join(""); paint(); };
  const paint = () => {
    const T = Math.max(1, +tot.value || 24); let seats = 0, mem = 0;
    body.querySelectorAll("tr").forEach(tr => { const k = Math.max(0, +tr.querySelector("input").value || 0); mem += k; const sh = k / T * 12, s = Math.floor(sh + 1e-9); seats += s; tr.querySelector(".sh").textContent = sh.toFixed(2); tr.querySelector(".hi").textContent = s; });
    const lost = 12 - seats;
    w.querySelector(".msg").innerHTML = `<b>${seats} of 12 seats</b> filled from this chamber${lost > 0 ? `; ${lost} stay${lost === 1 ? "s" : ""} empty because no party can round a fraction up at another party’s expense. The CA can still work with fewer than 12 (Guingona v. Gonzales).` : "."}${mem !== T ? ` <span class="fill">Party members add up to ${mem}, not ${T}.</span>` : ""} A party needs at least ${Math.ceil(T / 12)} member${Math.ceil(T / 12) === 1 ? "" : "s"} (one-twelfth of the chamber) for one seat.`;
  };
  w.querySelector("[data-a=guingona]").onclick = () => { tot.value = 24; load(preset); };
  body.addEventListener("input", paint); tot.addEventListener("input", paint);
  load(preset);
});
// party-list seats: the BANAT rounds, with the 2% guaranteed seat, proportional additional seats and the three-seat cap
document.querySelectorAll("#rcontent .plcalc").forEach(w => {
  const preset = JSON.parse(w.dataset.groups), other = JSON.parse(w.dataset.others), dist = w.querySelector("[data-v=district]");
  const body = w.querySelector("tbody");
  const load = () => { dist.value = w.dataset.district; body.innerHTML = preset.map(([n, v]) => `<tr><td>${esc(n)}</td><td><input type="number" min="0" step="1000" value="${v}" aria-label="votes for ${esc(n)}"></td><td class="pc"></td><td></td><td></td><td></td><td class="hi"></td></tr>`).join("") + `<tr class="oth"><td>${other.n} others</td><td>${other.v.toLocaleString("en-US")} each</td><td class="pc"></td><td></td><td></td><td></td><td class="hi"></td></tr>`; paint(); };
  const paint = () => {
    const D = Math.max(0, +dist.value || 0), seats = Math.floor(D / 0.8 * 0.2 + 1e-9);
    const rows = [...body.querySelectorAll("tr:not(.oth)")].map(tr => ({tr, v: Math.max(0, +tr.querySelector("input").value || 0)}));
    const total = rows.reduce((a, r) => a + r.v, 0) + other.n * other.v;
    const gs = rows.map(r => ({...r, p: total ? r.v / total : 0})).concat(Array.from({length: other.n}, () => ({v: other.v, p: total ? other.v / total : 0, o: 1})));
    gs.sort((a, b) => b.v - a.v);
    gs.forEach(g => { g.r1 = g.p >= 0.02 ? 1 : 0; g.r2 = 0; g.r3 = 0; });
    let left = seats - gs.reduce((a, g) => a + g.r1, 0);
    if (left < 0){ let k = seats; gs.forEach(g => { if (g.r1){ if (k > 0) k--; else g.r1 = 0; } }); left = 0; }
    const pool = left;
    gs.forEach(g => { const want = Math.floor(pool * g.p + 1e-9), room = 3 - g.r1; g.r2 = Math.max(0, Math.min(want, room, left)); g.capped = want > room; left -= g.r2; });
    for (const g of gs){ if (left <= 0) break; if (g.r1 + g.r2 === 0){ g.r3 = 1; left--; } }
    rows.forEach(r => { const g = gs.find(x => x.tr === r.tr), td = r.tr.querySelectorAll("td");
      td[2].textContent = (g.p * 100).toFixed(2) + "%"; td[3].textContent = g.r1 || "·"; td[4].textContent = g.r2 || "·"; td[4].className = g.capped ? "cap" : ""; td[5].textContent = g.r3 || "·"; td[6].textContent = g.r1 + g.r2 + g.r3; });
    const os = gs.filter(g => g.o), otd = body.querySelector(".oth").querySelectorAll("td");
    otd[2].textContent = (other.v / (total || 1) * 100).toFixed(2) + "% each"; otd[3].textContent = os.reduce((a, g) => a + g.r1, 0) || "·"; otd[4].textContent = os.reduce((a, g) => a + g.r2, 0) || "·"; const o3 = os.reduce((a, g) => a + g.r3, 0); otd[5].textContent = o3 || "·"; otd[6].textContent = o3 ? `${o3} groups × 1` : "0";
    const r1 = gs.reduce((a, g) => a + g.r1, 0), r2 = gs.reduce((a, g) => a + g.r2, 0), r3 = gs.reduce((a, g) => a + g.r3, 0);
    w.querySelector(".msg").innerHTML = `<b>${seats} party-list seats</b> = ${D} district seats ÷ 0.80 × 0.20, whole seats only. Round 1 gave <b>${r1}</b> guaranteed seats (2% or more); round 2 split the remaining <b>${pool}</b> by vote share (whole numbers, no 2% floor, cap of three in all) for <b>${r2}</b> more; round 3 gave <b>${r3}</b> groups next in rank one seat each.${left > 0 ? ` ${left} seat${left === 1 ? "" : "s"} could not be filled.` : ""} Divisor: all ${total.toLocaleString("en-US")} valid party-list votes.`;
  };
  w.querySelector("[data-a=reset]").onclick = load; body.addEventListener("input", paint); dist.addEventListener("input", paint);
  load();
});
// walk-throughs: run one fact pattern through the gates, one question at a time
document.querySelectorAll("#rcontent figure.viz .gates").forEach(G => {
  const fig = G.closest("figure.viz"), kids = [...G.children], gs = kids.filter(x => x.classList.contains("gate")), end = G.querySelector(":scope>.gend");
  const fx = G.nextElementSibling && G.nextElementSibling.classList.contains("vfacts") ? [...G.nextElementSibling.querySelectorAll(".vfact")] : [];
  if (!fx.length) return;
  const bar = document.createElement("div"); bar.className = "walkbar";
  bar.innerHTML = `<span class="vlab">Walk it</span>` + fx.map((f, i) => `<button type="button" class="vchip" data-f="${i}">${esc(f.querySelector(".fn").textContent)}</button>`).join("") + `<button type="button" class="vchip" data-f="own">Your own facts</button>`;
  const panel = document.createElement("div"); panel.className = "walkp"; panel.hidden = true;
  const out = document.createElement("div"); out.className = "walkout"; out.hidden = true;
  G.before(bar); bar.after(panel); G.after(out);
  let path = null, fact = null, right = 0, asked = 0;
  const yes = a => a === "y" ? "yes" : "no";
  function clear(){
    G.classList.remove("walking"); kids.forEach(c => { c.hidden = false; c.classList.remove("cur", "done", "hit"); });
    G.querySelectorAll(".yn,.fb").forEach(x => x.remove()); panel.hidden = out.hidden = true;
    bar.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", "false"));
  }
  function ask(i){
    const g = gs[i]; g.hidden = false; g.classList.add("cur");
    const box = document.createElement("div"); box.className = "yn";
    box.innerHTML = `<button type="button" class="btn small" data-a="y">Yes</button><button type="button" class="btn small" data-a="n">No</button>`;
    g.querySelector(".q").append(box); box.querySelector("button").focus({preventScroll: true});
    box.addEventListener("click", e => { const b = e.target.closest("[data-a]"); if (b) answer(i, b.dataset.a); });
  }
  function answer(i, a){
    const g = gs[i]; g.querySelector(".yn").remove(); g.classList.remove("cur"); g.classList.add("done");
    let exp = path ? (path[i] || a) : a; const loose = exp.endsWith("?"); exp = exp.replace("?", "");
    const fb = document.createElement("div"); fb.className = "fb";
    if (path){ asked++; const ok = loose || a === exp; if (ok) right++; fb.classList.add(ok ? "good" : "bad");
      fb.textContent = loose && a !== exp ? `Arguable: “${yes(a)}” can be defended, but the walk follows “${yes(exp)}”.` : loose ? `✓ ${yes(a)} (arguable, but the better reading).` : ok ? `✓ ${yes(a)}: right.` : `✕ You said ${yes(a)}; on these facts it is ${yes(exp)}.`;
    } else fb.textContent = `You said ${yes(a)}.`;
    g.querySelector(".q").append(fb);
    if (exp === (g.dataset.exit === "yes" ? "y" : "n")){ g.classList.add("hit"); return finish(g.querySelector(".gx")); }
    const nx = g.nextElementSibling; if (nx && nx.classList.contains("ve")) nx.hidden = false;
    if (i + 1 < gs.length) ask(i + 1); else { end.hidden = false; finish(end); }
  }
  function finish(node){
    out.hidden = false;
    out.innerHTML = `<span class="vlab">Result</span><div class="vres">${node.innerHTML}</div>` + (fact ? `<p class="vwhy">${fact.querySelector(".vwhy").innerHTML}</p>` : "") + (path ? `<p class="score">You matched ${right} of ${asked} answer${asked === 1 ? "" : "s"}.</p>` : "") + `<div class="row"><button type="button" class="btn small" data-w="again">Walk another</button><button type="button" class="btn small ghost" data-w="map">Show the whole map</button></div>`;
    out.scrollIntoView({block: "nearest", behavior: "smooth"});
  }
  bar.addEventListener("click", e => {
    const c = e.target.closest("[data-f]"); if (!c) return;
    if (c.getAttribute("aria-pressed") === "true"){ clear(); return; }
    clear(); setTest(fig, false); G.classList.add("walking"); c.setAttribute("aria-pressed", "true");
    fact = c.dataset.f === "own" ? null : fx[+c.dataset.f]; path = fact ? fact.dataset.path.split(",") : null; right = asked = 0;
    panel.hidden = false;
    panel.innerHTML = fact ? `<span class="vlab">The facts</span>${fact.querySelector(".vft").innerHTML}` : `<span class="vlab">Your own facts</span>Keep the problem in front of you and answer each question for those facts.`;
    kids.forEach(k => k.hidden = true); ask(0);
  });
  out.addEventListener("click", e => { const b = e.target.closest("[data-w]"); if (!b) return; clear(); if (b.dataset.w === "again") bar.scrollIntoView({block: "nearest", behavior: "smooth"}); });
});
// test me: cover the details of a figure; tap each one to check your recall
const COVER = ".vn .s, .vcmp .c, .vtl .t, .rung .lab, .gate>.gx, .gend, .acro .w, .wr .ln>span, [data-cover]";
const coverEls = fig => [...fig.querySelectorAll(COVER)].filter(el => !el.closest(".calc,.vfacts,.walkp,.walkout") && !(el.parentElement.closest(COVER) && fig.contains(el.parentElement.closest(COVER))));
function setTest(fig, on){
  const b = fig.querySelector(".vtools .vtest"); if (!b) return;
  fig.classList.toggle("testing", on); b.setAttribute("aria-pressed", on); b.textContent = on ? "Done" : "Test me";
  fig.querySelectorAll(".rv").forEach(x => x.classList.remove("rv")); updTest(fig);
}
function updTest(fig){
  const ct = fig.querySelector(".vtools .ct"); if (!ct) return;
  if (!fig.classList.contains("testing")){ ct.textContent = ""; return; }
  const els = coverEls(fig); ct.textContent = `${els.filter(x => x.classList.contains("rv")).length} of ${els.length}`;
}
document.querySelectorAll("#rcontent figure.viz").forEach(fig => {
  if (fig.hasAttribute("data-notest") || !coverEls(fig).length) return;
  const t = document.createElement("span"); t.className = "vtools"; t.innerHTML = `<span class="ct"></span><button type="button" class="vchip vtest" aria-pressed="false" title="Cover the details, then tap each to check yourself">Test me</button>`;
  fig.querySelector(".vt").append(t);
  t.querySelector(".vtest").addEventListener("click", () => {
    const on = !fig.classList.contains("testing");
    if (on){ const w = fig.querySelector(".walkbar [aria-pressed=true]"); if (w) w.click(); }
    setTest(fig, on);
  });
});
document.addEventListener("click", e => {
  const fig = e.target.closest("#rcontent figure.viz.testing"); if (!fig || e.target.closest(".vtools,.walkbar,.calc,.yn,input,select")) return;
  let el = e.target.closest(COVER); if (!el || !fig.contains(el)) return;
  for (let up = el.parentElement.closest(COVER); up && fig.contains(up); up = up.parentElement.closest(COVER)) el = up;
  if (el.classList.contains("rv")) return;
  e.preventDefault(); e.stopPropagation();
  el.classList.add("rv"); el.querySelectorAll(COVER).forEach(x => x.classList.add("rv")); updTest(fig);
}, true);
// links from one diagram (or the hook wall and the issue radar) to another
$("rcontent").addEventListener("click", e => { const a = e.target.closest("a.xref"); if (a){ e.preventDefault(); goToId(a.dataset.h); } });
function applyScopeMarks(){ document.querySelectorAll("#rcontent [data-scope]").forEach(x => x.hidden = HIDE && OUT_SECS.includes(x.dataset.scope)); }

/* ================= CASES: browse ================= */
function setCaseMode(m){ document.querySelectorAll("[data-cm]").forEach(b => b.setAttribute("aria-pressed", b.dataset.cm === m)); $("c-browse").hidden = m !== "browse"; $("c-drill").hidden = m !== "drill"; if (m === "drill") renderDSetup(); }
document.querySelector("[data-cm]").parentElement.addEventListener("click", e => { const b = e.target.closest("[data-cm]"); if (b) setCaseMode(b.dataset.cm); });
function fillTopicSel(){ const v = $("ctopic").value; $("ctopic").innerHTML = `<option value="">All topics</option>` + TOPS().map(t => `<option value="${t.key}">${esc(t.name)}</option>`).join(""); $("ctopic").value = TOPS().some(t => t.key === v) ? v : ""; }
fillTopicSel();
function renderCases(){
  const q = $("cq").value.trim().toLowerCase(), tp = $("ctopic").value, an = $("canchor").checked;
  const list = CASES().filter(c => (!tp || c.t === tp) && (!an || c.a) && (!q || [c.n, c.r, c.f, c.h, c.x, c.y, c.sub].join(" ").toLowerCase().includes(q)));
  $("caseCt").textContent = `${list.length} of ${CASES().length} cases`;
  let html = "", last = "";
  TOPS().forEach(t => {
    const g = list.filter(c => c.t === t.key); if (!g.length) return;
    html += `<div class="grouph">${esc(t.name)} <small>${esc(t.part)} · ${g.length}</small></div>`;
    html += g.map(c => `<button class="crow" data-case="${c.id}"><span class="nm">${esc(c.n)}<span class="yr">${esc(c.y)}</span> ${hookChip(c)}</span><span>${c.a ? '<span class="tag anchor">anchor</span>' : c.ref ? '<span class="tag">mentioned only</span>' : ""}</span><span class="rl">${esc(c.r)}</span></button>`).join("");
  });
  $("clist").innerHTML = html || `<p class="empty">No case matches. Try fewer words.</p>`;
}
["cq","ctopic","canchor"].forEach(id => $(id).addEventListener(id === "cq" ? "input" : "change", renderCases));

/* ================= CASES: drill ================= */
const DIRS = {
  cr: {p: "cr", help: "You see the case name. Say the rule out loud, then flip and grade yourself honestly."},
  fc: {p: "fc", help: "You see the facts. Name the case out loud, then flip and grade yourself honestly."},
  rc: {p: "rc", help: "You see the rule. Name the case that laid it down, then flip and grade yourself honestly."},
  mix: {p: "mix", help: "Any of the three, shuffled: a case name, a rule or a set of facts. Answer out loud, flip, grade."}
};
// formats a case can be drilled in; in Mixed, prefer a format that is due, then one never seen, else any
const FMTS = c => ["cr", ...(c.f ? ["fc"] : []), ...(c.r ? ["rc"] : [])];
function fmtFor(c){
  if (dDir !== "mix") return dDir;
  const f = FMTS(c), due = f.filter(x => isDue(x + ":" + c.id)), fr = f.filter(x => !SRS[x + ":" + c.id]);
  return shuffle(due.length ? due : fr.length ? fr : f)[0];
}
let dDir = store.get("ddir", "cr"), dTop = new Set(store.get("dtop", D.topics.map(t => t.key))), R = [], ri = 0, rDone = 0, rRight = 0;
function dPool(){ return CASES().filter(c => !c.ref && dTop.has(c.t) && (!$("dAnchor").checked || c.a) && (dDir === "cr" || dDir === "mix" || (dDir === "fc" ? c.f : c.r))); }
function renderDSetup(){
  document.querySelectorAll("#dDir [data-d]").forEach(b => b.setAttribute("aria-pressed", b.dataset.d === dDir));
  $("dDirHelp").textContent = DIRS[dDir].help;
  $("dTopics").innerHTML = TOPS().map(t => `<label class="chip${dTop.has(t.key) ? " on" : ""}" for="dt_${t.key}"><input type="checkbox" id="dt_${t.key}" data-t="${t.key}"${dTop.has(t.key) ? " checked" : ""}>${esc(t.name)}</label>`).join("");
  const fm = c => dDir === "mix" ? FMTS(c) : [dDir], p = dPool(), due = p.filter(c => fm(c).some(x => isDue(x + ":" + c.id))).length, fresh = p.filter(c => fm(c).some(x => !SRS[x + ":" + c.id])).length;
  $("dCount").textContent = `${p.length} cases selected · ${due} due · ${fresh} not yet seen`;
  $("dSetup").hidden = false; $("dCard").hidden = true;
  store.set("ddir", dDir); store.set("dtop", [...dTop]);
}
$("dDir").addEventListener("click", e => { const b = e.target.closest("[data-d]"); if (b){ dDir = b.dataset.d; renderDSetup(); } });
$("dTopics").addEventListener("change", e => { const t = e.target.dataset.t; if (!t) return; e.target.checked ? dTop.add(t) : dTop.delete(t); renderDSetup(); });
$("dAll").onclick = () => { dTop = new Set(D.topics.map(t => t.key)); renderDSetup(); };
$("dNone").onclick = () => { dTop = new Set(); renderDSetup(); };
$("dAnchor").onchange = renderDSetup;
function startDrill(dueOnly){
  let cards;
  if (dueOnly){
    cards = dueKeys().map(k => { const [p, id] = k.split(":"); return {p, id}; });
    if (!cards.length){ renderDSetup(); $("dCount").textContent = "Nothing is due right now. Start a new round instead."; return; }
    cards = shuffle(cards).slice(0, 30);
  } else {
    const p = dPool(); if (!p.length){ $("dCount").textContent = "Pick at least one topic."; return; }
    // due cards first, then unseen, then the soonest reviews; the round itself is then shuffled so topics and formats interleave
    const all = shuffle(p).map(c => ({p: fmtFor(c), id: c.id})), k = x => x.p + ":" + x.id;
    const due = all.filter(x => isDue(k(x))), fresh = all.filter(x => !SRS[k(x)]), rest = all.filter(x => SRS[k(x)] && !isDue(k(x))).sort((a, b) => SRS[k(a)].d - SRS[k(b)].d);
    cards = shuffle([...due, ...fresh, ...rest].slice(0, 20));
  }
  $("dSetup").hidden = true;
  runCards($("dCard"), cards, {label: "Card", onEnd: drillEnd});
}
$("dStart").onclick = () => startDrill(false);
function drillEnd(box, r){
  let run = 0, top = 0; r.res.forEach(x => { if (x === undefined) return; run = x ? run + 1 : 0; top = Math.max(top, run); });
  box.innerHTML = `<div class="panel endpanel"><div class="score"><span class="big">${r.right}/${r.done}</span><span class="tiny">remembered or answered correctly this round</span></div><div class="row" style="gap:8px"><span class="hookchip hc-sun">Longest run this round: ${top}</span>${streakHTML()}</div><p class="tiny" style="margin:0">Missed cards come back in about a minute and go on your fix list; known cards move out to hours and days. ${dueKeys().length} cards are due now.</p><div class="row"><button class="btn primary" data-a="again">Another round</button><button class="btn" data-a="due">Review due cards</button><button class="btn ghost" data-a="back">Change settings</button></div></div>`;
  box.querySelector('[data-a="again"]').onclick = () => startDrill(false); box.querySelector('[data-a="due"]').onclick = () => startDrill(true); box.querySelector('[data-a="back"]').onclick = renderDSetup;
  dueBadge();
}
const STOPW = new Set("people republic philippines philippine commission elections comelec secretary executive house representatives senate court appeals city government association national department office party list board inc corporation union finance justice president tribunal electoral sandiganbayan ombudsman congress municipality province".split(" "));
function maskName(text, c){
  const toks = c.n.replace(/\(.*?\)/g, " ").split(/[^A-Za-zÀ-ÿñÑ’'-]+/).filter(w => w.length >= 4 && !STOPW.has(w.toLowerCase()));
  let t = text || "";
  toks.forEach(w => { t = t.replace(new RegExp("\\b" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "gi"), "▁▁▁"); });
  return t;
}
/* ================= card runner: case drills, lists, sessions, fix list ================= */
const KIND_LBL = {cr: "Case → rule", fc: "Facts → case", rc: "Rule → case", m: "Multiple choice", l: "List", i: "Missed issue"};
function cardOK({p, id}){
  if (p === "i"){ const [e, i] = id.split(":"); return !!ESS[e] && !!ISS[i] && !(HIDE && OUT_ISSUES.includes(i)); }
  return validKey(p + ":" + id) && (p !== "fc" || !!(CASE[id] || {}).f);
}
function runCards(box, cards, opts){
  box._r = {cards: cards.filter(cardOK), i: 0, done: 0, right: 0, res: [], snap: [], dir: "fwd", opts: opts || {}};
  box.hidden = false; drawCard(box);
}
function endRun(box){ const r = box._r; dueBadge(); (r.opts.onEnd || drillEnd)(box, r); }
// streak: correct answers in a row, kept across rounds; the best is remembered
let STREAK = store.get("streak", {cur: 0, best: 0});
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const streakHTML = () => `<span class="streak${STREAK.cur ? " on" : ""}" title="Correct in a row. Best: ${STREAK.best}"><span class="fl" aria-hidden="true">🔥</span><b>${STREAK.cur}</b><small>in a row · best ${STREAK.best}</small></span>`;
function cardDone(box, ok){
  const r = box._r; if (r.res[r.i] !== undefined) return;
  r.done++; if (ok) r.right++; r.res[r.i] = ok;
  if (r.snap[r.i]) r.snap[r.i].st = {...STREAK};
  STREAK.cur = ok ? STREAK.cur + 1 : 0; STREAK.best = Math.max(STREAK.best, STREAK.cur); store.set("streak", STREAK);
  const el = box.querySelector(".streak");
  if (el){ el.outerHTML = streakHTML(); const n = box.querySelector(".streak"); if (!REDUCED) n.classList.add(ok ? "pulse" : "drop"); }
  if (ok && [5, 10, 15, 20, 30, 40, 50, 75, 100].includes(STREAK.cur)) toast(`🔥 ${STREAK.cur} in a row${STREAK.cur === STREAK.best ? " · a new best" : ""}`);
}
function toast(msg){
  const t = document.createElement("div"); t.className = "mtoast"; t.setAttribute("role", "status"); t.textContent = msg; document.body.append(t);
  setTimeout(() => t.classList.add("bye"), 1700); setTimeout(() => t.remove(), 2200);
}
// go back one card: undo its grade (and the current card's, if graded) so the schedule is exactly as before
function undoCard(r, j){
  const sn = r.snap[j]; if (!sn || r.res[j] === undefined) return;
  if (sn.s) SRS[sn.k] = sn.s; else delete SRS[sn.k];
  if (sn.f) FIX[sn.k] = sn.f; else delete FIX[sn.k];
  if (sn.st){ STREAK = {...sn.st}; store.set("streak", STREAK); }
  store.set("srs", SRS); store.set("fix", FIX);
  r.done--; if (r.res[j]) r.right--; r.res[j] = undefined;
}
function prevCard(box){
  const r = box._r; if (r.i <= 0) return;
  undoCard(r, r.i); undoCard(r, r.i - 1); r.i--; r.dir = "back"; drawCard(box); dueBadge();
}
function nextCard(box){
  const r = box._r, f = box.querySelector(".card-face"), ok = r.res[r.i];
  let ghost = null;
  if (f && !REDUCED){ // the answered card slides off while the next one comes in
    ghost = f.cloneNode(true); ghost.className = "card-ghost " + (ok === false ? "out-miss" : "out-ok"); ghost.setAttribute("aria-hidden", "true");
    ghost.querySelectorAll("button,input,[hidden]").forEach(x => x.remove());
    ghost.querySelectorAll("*").forEach(x => { x.removeAttribute("id"); x.removeAttribute("class"); x.removeAttribute("data-g"); x.removeAttribute("data-case"); });
    ghost.style.top = f.offsetTop + "px"; ghost.style.height = f.offsetHeight + "px"; ghost.style.width = f.offsetWidth + "px";
  }
  r.i++; r.dir = "fwd"; drawCard(box);
  if (ghost && box._r === r && r.i < r.cards.length){ box.append(ghost); setTimeout(() => ghost.remove(), 420); }
  const top = box.getBoundingClientRect().top; if (top < 0) window.scrollTo({top: window.scrollY + top - 12});
}
// flip a flashcard: the face turns edge-on, the answer is swapped in, and it turns back
function flipFace(face, swap){
  face.classList.add("flipped");
  if (REDUCED){ swap(); return; }
  face.classList.remove("in-fwd", "in-back"); face.classList.add("flipping");
  setTimeout(() => { if (face.isConnected) swap(); }, 160); setTimeout(() => face.classList.remove("flipping"), 340);
}
const HC_LBL = {ok: "upheld or valid", no: "struck down or void", sun: "dismissed on procedure, or a twist", acc: "a principle or a definition"};
const hookChip = (c, big) => c && c.hk ? `<span class="hookchip hc-${c.hc}${big ? " big" : ""}" title="Hook · ${HC_LBL[c.hc]}">${esc(c.hk)}</span>` : "";
function gradeRow(k){ return `<div class="grade">${[["again","Again",0],["hard","Hard",1],["good","Good",2],["easy","Easy",3]].map(([cl, l, g]) => `<button class="btn ${cl}" data-g="${g}">${l}<small>${nextLbl(k, g)}</small></button>`).join("")}</div>`; }
function drawCard(box){
  const r = box._r;
  if (r.i >= r.cards.length) return endRun(box);
  const {p, id} = r.cards[r.i];
  if (!r.snap[r.i]){ const k = p + ":" + id; r.snap[r.i] = {k, s: SRS[k] ? {...SRS[k]} : null, f: FIX[k] ? {...FIX[k]} : null}; }
  const head = `<div class="spread runhead"><span class="lbl">${esc(r.opts.label || "Card")} ${r.i + 1} of ${r.cards.length} · ${KIND_LBL[p]}</span>${streakHTML()}<span class="row" style="gap:6px">${r.i > 0 ? `<button class="btn small ghost" data-prev title="Back to the previous card (←)">← Previous</button>` : ""}<button class="btn small ghost" data-quit>${esc(r.opts.quit || "End round")}</button></span></div><div class="dprog"><i style="width:${100 * r.i / r.cards.length}%"></i></div>`;
  if (p === "m") mcqCard(box, head, D.mcq.find(x => x.id === id));
  else if (p === "l") listCard(box, head, LIST[id]);
  else if (p === "i") issueCard(box, head, id);
  else if (p === "cr") crCard(box, head, CASE[id]);
  else pickCard(box, head, p, CASE[id]);
  box.querySelector("[data-quit]").onclick = () => endRun(box);
  const pv = box.querySelector("[data-prev]"); if (pv) pv.onclick = () => prevCard(box);
  const face = box.querySelector(".card-face"); if (face && !REDUCED) face.classList.add(r.dir === "back" ? "in-back" : "in-fwd");
}
// keyboard: space or enter flips, 1-4 grade (again, hard, good, easy), left arrow goes back
document.addEventListener("keydown", e => {
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || !$("scrim").hidden || e.metaKey || e.ctrlKey || e.altKey) return;
  const box = [...document.querySelectorAll("#dCard,#sessRun,#lRun")].find(b => !b.hidden && b.offsetParent && b._r && b.querySelector(".card-face")); if (!box) return;
  const fl = box.querySelector(".card-face [data-flip]:not([hidden])");
  if ((e.key === " " || e.key === "Enter") && fl){ e.preventDefault(); fl.click(); return; }
  if (/^[1-4]$/.test(e.key)){ const g = box.querySelector(`.card-face .grade [data-g="${+e.key - 1}"]`); if (g && g.offsetParent){ e.preventDefault(); g.click(); } return; }
  if (e.key === "ArrowLeft"){ const pv = box.querySelector("[data-prev]"); if (pv){ e.preventDefault(); pv.click(); } }
});
function mcqCard(box, head, q){
  box.innerHTML = head + `<div class="card-face">${mcqBody(q, null)}</div>`;
  bindMcq(box, q, (ok) => { qhist[q.id] = {r: ok ? 1 : 0, n: ((qhist[q.id] || {}).n || 0) + 1}; store.set("qhist", qhist); rate("m:" + q.id, ok ? 2 : 0); cardDone(box, ok); }, () => nextCard(box));
}
function crCard(box, head, c){
  const k = "cr:" + c.id;
  box.innerHTML = head + `<div class="card-face"><div class="tags"><span class="tag">${esc(tname(c.t))}</span><span class="tag">${esc(c.y)}</span>${c.a ? '<span class="tag anchor">anchor</span>' : ""}</div><div class="prompt" style="font-style:italic">${esc(c.n)}</div><p class="tiny" style="margin:0">What rule or test does this case stand for? What fact decided it?</p><button class="btn primary" data-flip>Show the rule</button><div class="reveal" hidden></div></div>`;
  const rev = box.querySelector(".reveal");
  box.querySelector("[data-flip]").onclick = e => { e.target.hidden = true; const face = box.querySelector(".card-face"); flipFace(face, () => {
    rev.hidden = false; face.dataset.hc = c.hc || "";
    rev.innerHTML = `${hookChip(c, true)}<div class="prompt facts" style="font-size:1.05rem">${esc(c.r)}</div>${c.test ? `<p class="tiny" style="margin:0"><b>Test:</b> ${esc(c.test)}</p>` : ""}${c.h ? `<p class="tiny" style="margin:0"><b>Holding:</b> ${esc(c.h)}</p>` : ""}${gradeRow(k)}<button class="btn small ghost" data-case="${c.id}">Open full card</button>`;
    rev.querySelector(".grade").onclick = ev => { const b = ev.target.closest("[data-g]"); if (!b) return; const g = +b.dataset.g; rate(k, g); cardDone(box, g >= 2); nextCard(box); };
  }); };
}
// facts → case and rule → case: name the case yourself, then flip (no multiple choice)
function pickCard(box, head, p, c){
  const k = p + ":" + c.id, front = p === "fc" ? maskName(c.f, c) : maskName(c.r, c);
  box.innerHTML = head + `<div class="card-face"><div class="tags"><span class="tag">${esc(tname(c.t))}</span>${c.a ? '<span class="tag anchor">anchor</span>' : ""}</div><div class="prompt facts">${esc(front)}</div>${p === "rc" && c.test ? `<p class="tiny" style="margin:0"><b>Test:</b> ${esc(maskName(c.test, c))}</p>` : ""}<p class="tiny" style="margin:0">${p === "fc" ? "Which case is this? Say the name, then the rule it stands for." : "Which case laid down this rule? Say the name and the fact that decided it."}</p><button class="btn primary" data-flip>Show the case</button><div class="reveal" hidden></div></div>`;
  const rev = box.querySelector(".reveal");
  box.querySelector("[data-flip]").onclick = e => { e.target.hidden = true; const face = box.querySelector(".card-face"); flipFace(face, () => {
    rev.hidden = false; face.dataset.hc = c.hc || "";
    rev.innerHTML = `${hookChip(c, true)}<div class="prompt" style="font-style:italic">${esc(c.n)} <span class="tiny" style="font-style:normal">(${esc(c.y)})</span></div>${p === "fc" ? `<p style="margin:0">${esc(c.r)}</p>` : c.f ? `<p class="tiny" style="margin:0"><b>Facts:</b> ${esc(c.f)}</p>` : ""}${c.h ? `<p class="tiny" style="margin:0"><b>Holding:</b> ${esc(c.h)}</p>` : ""}${gradeRow(k)}<button class="btn small ghost" data-case="${c.id}">Open full card</button>`;
    rev.querySelector(".grade").onclick = ev => { const b = ev.target.closest("[data-g]"); if (!b) return; const g = +b.dataset.g; rate(k, g); cardDone(box, g >= 2); nextCard(box); };
  }); };
}
function issueCard(box, head, id){
  const [eid, iid] = id.split(":"), e = ESS[eid], is = ISS[iid], k = "i:" + id;
  box.innerHTML = head + `<div class="card-face"><div class="tags"><span class="tag">Issue spotter</span><span class="tag${e.news ? " news" : ""}">${esc(e.exam)}${e.n ? " · Q" + e.n : ""}</span></div><div class="story">${esc(e.prompt)}</div><div class="prompt" style="font-size:1.05rem">You missed an issue in this problem last time. Which issue is it, and what is the rule?</div><button class="btn primary" data-flip>Show the issue</button><div class="reveal" hidden></div></div>`;
  const rev = box.querySelector(".reveal");
  box.querySelector("[data-flip]").onclick = ev => {
    ev.target.hidden = true; rev.hidden = false;
    rev.innerHTML = `<div class="prompt facts" style="font-size:1.05rem"><b>${esc(is.l)}.</b> ${esc(is.h)}</div><div class="row"><a href="#" data-rv="${esc(is.rv)}" class="btn small ghost">Open the rule map</a></div><div class="row"><button class="btn again" data-ok="0">I missed it again</button><button class="btn good" data-ok="1">I got it</button></div>`;
    rev.querySelectorAll("[data-ok]").forEach(b => b.onclick = () => { const ok = b.dataset.ok === "1"; fixTrack(k, ok ? 2 : 0); cardDone(box, ok); nextCard(box); });
  };
}
function listCard(box, head, L){
  const k = "l:" + L.id;
  box.innerHTML = head + `<div class="card-face"><div class="tags"><span class="tag">${esc(tname(L.t))}</span><span class="tag">${L.items.length} items${L.ordered ? " · in order" : ""}</span></div><div class="prompt">${esc(L.ask)}</div><p class="tiny lhelp" style="margin:0">List every item in your head or on paper first. Then tap each item to check it, and tap it again if you missed it.</p><${L.ordered ? "ol" : "ul"} class="litems">${L.items.map((t, i) => `<li><button class="litem" data-li="${i}" data-s=""><span class="lt">${esc(t)}</span><span class="lm"></span></button></li>`).join("")}</${L.ordered ? "ol" : "ul"}><div class="row"><button class="btn" data-all>Reveal all</button><button class="btn primary" data-done>Done</button></div><div class="lres"></div></div>`;
  const items = [...box.querySelectorAll(".litem")]; let locked = false;
  const paint = b => { const st = b.dataset.s; b.querySelector(".lm").textContent = st === "ok" ? "✓" : st === "miss" ? "✗ missed" : "tap"; b.setAttribute("aria-label", st ? b.querySelector(".lt").textContent + (st === "miss" ? " (missed)" : " (recalled)") : "Hidden item " + (+b.dataset.li + 1)); };
  items.forEach(paint);
  box.querySelector(".litems").onclick = e => { const b = e.target.closest(".litem"); if (!b || locked) return; b.dataset.s = b.dataset.s === "ok" ? "miss" : "ok"; paint(b); };
  box.querySelector("[data-all]").onclick = () => items.forEach(b => { if (!b.dataset.s){ b.dataset.s = "ok"; paint(b); } });
  box.querySelector("[data-done]").onclick = e => {
    if (locked) return;
    if (items.some(b => !b.dataset.s)){ items.forEach(b => { if (!b.dataset.s){ b.dataset.s = "ok"; paint(b); } }); box.querySelector(".lhelp").textContent = "All items are showing. Tap any you missed, then press Done."; box.querySelector(".lhelp").classList.add("nudge"); return; }
    locked = true; e.target.hidden = true; box.querySelector("[data-all]").hidden = true;
    const miss = items.filter(b => b.dataset.s === "miss").map(b => +b.dataset.li), n = items.length;
    const g = miss.length === 0 ? 2 : miss.length * 2 > n ? 0 : 1;
    rate(k, g); if (miss.length && g !== 0) fixAdd(k);
    LRES[L.id] = {m: miss, t: Date.now()}; store.set("lres", LRES);
    cardDone(box, miss.length === 0);
    box.querySelector(".lres").innerHTML = `<div class="expl"><div class="verdict ${miss.length ? "no" : "ok"}">${miss.length ? `You missed ${miss.length} of ${n}. It is on your fix list and comes back soon.` : `All ${n} recalled.`}</div>${L.hook ? `<div class="lhook">${esc(L.hook)}</div>` : ""}<p class="tiny">Source: ${esc(L.src)}${L.cases && L.cases.length ? " · " + caseLinks(L.cases) : ""}${L.rv ? ` · <a href="#" data-rv="${esc(L.rv)}">rule map</a>` : ""}</p><div class="row"><button class="btn primary" data-next>Next</button></div></div>`;
    const nx = box.querySelector("[data-next]"); nx.onclick = () => nextCard(box); nx.focus({preventScroll: true});
  };
}

/* ================= fix list ================= */
let FIX = store.get("fix", {});
const fixValid = k => { const [p, ...r] = k.split(":"); return cardOK({p, id: r.join(":")}); };
const fixKeys = () => Object.keys(FIX).filter(fixValid).sort((a, b) => FIX[a].t - FIX[b].t);
function fixAdd(k){ const f = FIX[k] || {t: Date.now(), n: 0}; f.s = 0; f.n++; FIX[k] = f; store.set("fix", FIX); }
function fixTrack(k, g){ // g: 0 missed, 1 hard (no change), 2+ correct; two correct answers clear an item
  if (g === 0) return fixAdd(k);
  if (g >= 2 && FIX[k]){ FIX[k].s = (FIX[k].s || 0) + 1; if (FIX[k].s >= 2) delete FIX[k]; store.set("fix", FIX); }
}
function fixLabel(k){
  const [p, a, b] = k.split(":");
  if (p === "m"){ const q = D.mcq.find(x => x.id === a); return `${q.exam} #${q.n}: ${q.q.length > 80 ? q.q.slice(0, 80) + "…" : q.q}`; }
  if (p === "l") return `List: ${LIST[a].title}`;
  if (p === "i") return `Spotter: ${ISS[b].l} (${ESS[a].short})`;
  return `${KIND_LBL[p]}: ${CASE[a].n}`;
}
function renderFix(){
  const ks = fixKeys(), n = ks.length;
  $("fixN").textContent = n; $("fixN").classList.toggle("zero", !n);
  $("fixMsg").textContent = n ? "Everything you missed: MCQs, cards you marked Again, list items, and issues you missed in the spotter. Answer an item correctly twice to clear it." : "Empty for now. Misses from drills, MCQs, lists and the spotter land here automatically.";
  $("fixGo").disabled = !n; $("fixGo").textContent = n ? `Review fix list (${Math.min(n, 20)})` : "Review fix list";
  $("fixD").hidden = !n;
  $("fixUl").innerHTML = ks.slice(0, 60).map(k => `<li>${esc(fixLabel(k))}${FIX[k].s ? ' <span class="fixs">1 of 2</span>' : ""}</li>`).join("");
}
$("fixGo").onclick = () => { const ks = fixKeys().slice(0, 20); if (!ks.length) return; startRun(ks.map(k => { const [p, ...r] = k.split(":"); return {p, id: r.join(":")}; }), "Fix"); };

/* ================= session: one button, 15 to 20 minutes ================= */
function planTopics(){
  const today = manilaToday(); if (today > D.examDate) return TOPS().map(t => t.key);
  const secs = new Set();
  D.plan.filter(d => d.date <= today).forEach(d => d.items.forEach(it => (it.rv || []).forEach(id => { const el = document.getElementById(id); const sec = el && (el.tagName === "SECTION" ? el : el.closest("section.rv")); if (sec) secs.add(sec.id); })));
  const ts = new Set(); secs.forEach(sid => { D.topics.filter(t => t.sec === sid).forEach(t => ts.add(t.key)); if (sid === "priv") ts.add("org"); });
  const out = [...ts].filter(shownT);
  return out.length ? out : TOPS().map(t => t.key);
}
function buildSession(){
  const seen = new Set(), fix = [], rest = [];
  const add = (arr, p, id) => { const k = p + ":" + id; if (seen.has(k)) return; seen.add(k); arr.push({p, id}); };
  fixKeys().slice(0, 6).forEach(k => { const [p, ...r] = k.split(":"); add(fix, p, r.join(":")); });
  shuffle(dueKeys()).slice(0, 10).forEach(k => { const [p, id] = k.split(":"); add(rest, p, id); });
  const nDue = rest.length, tp = new Set(planTopics()), room = Math.max(0, 20 - fix.length - rest.length);
  const newL = shuffle(LISTS().filter(l => tp.has(l.t) && !SRS["l:" + l.id])).slice(0, Math.min(4, Math.ceil(room / 3)));
  const newM = shuffle(MCQS().filter(q => tp.has(q.t) && q.cov === "in" && !qhist[q.id] && !SRS["m:" + q.id])).slice(0, Math.min(3, Math.floor(room / 5)));
  const cs = CASES().filter(c => !c.ref && tp.has(c.t) && !SRS["cr:" + c.id]);
  const newC = [...shuffle(cs.filter(c => c.a)), ...shuffle(cs.filter(c => !c.a))].slice(0, Math.max(0, room - newL.length - newM.length));
  newL.forEach(l => add(rest, "l", l.id)); newM.forEach(q => add(rest, "m", q.id)); newC.forEach(c => add(rest, "cr", c.id));
  if (fix.length + rest.length < 12){ // everything is fresh in memory: review ahead, soonest due first
    CASES().filter(c => !c.ref && tp.has(c.t) && SRS["cr:" + c.id]).sort((a, b) => SRS["cr:" + a.id].d - SRS["cr:" + b.id].d).slice(0, 15 - fix.length - rest.length).forEach(c => add(rest, "cr", c.id));
  }
  const cards = [...fix, ...shuffle(rest)];
  return {cards, nFix: fix.length, nDue, nNew: rest.length - nDue, topics: [...tp], mins: Math.round(cards.reduce((s, c) => s + (c.p === "l" ? 1.5 : c.p === "m" ? 1.2 : 0.8), 0))};
}
const joinNames = a => a.length <= 2 ? a.join(" and ") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];
function renderSessPlan(){
  const s = buildSession(), parts = [];
  if (s.nFix) parts.push(`${s.nFix} from your fix list`);
  if (s.nDue) parts.push(`${s.nDue} due for review`);
  if (s.nNew) parts.push(`${s.nNew} new or review-ahead from ${joinNames(s.topics.map(tname))}`);
  $("sessPlan").textContent = s.cards.length ? `About ${Math.max(5, s.mins)} minutes: ${joinNames(parts)}. Cases, lists and multiple choice, mixed. You can stop at any card.` : "Nothing to review right now.";
  $("sessGo").disabled = !s.cards.length;
}
function startRun(cards, label){
  $("sessStart").hidden = true; $("todayGrid").hidden = true;
  if ($("v-today").hidden) setTab("today");
  runCards($("sessRun"), cards, {label, quit: "End session", onEnd: sessEnd});
  window.scrollTo({top: 0});
}
$("sessGo").onclick = () => startRun(buildSession().cards, "Session");
function sessEnd(box, r){
  const tp = new Set(planTopics()), spotted = store.get("sphist", {});
  const pool = D.essays.filter(e => !spotted[e.id] && e.cov === "in" && e.t.some(t => tp.has(t)));
  const pick = (pool.length ? pool : D.essays.filter(e => !spotted[e.id]))[0];
  box.innerHTML = `<div class="score"><span class="big">${r.right}/${r.done}</span><span class="tiny">right this ${esc((r.opts.label || "session").toLowerCase())} · ${fixKeys().length} on your fix list · ${dueKeys().length} due</span></div>
  <div class="row">${pick ? `<button class="btn primary" data-spot="${pick.id}">Finish with one spot problem (5 min): ${esc(pick.short)}</button>` : ""}<button class="btn" data-a="more">Another session</button><button class="btn ghost" data-a="back">Back to Today</button></div>`;
  box.querySelector('[data-a="more"]').onclick = () => startRun(buildSession().cards, "Session");
  box.querySelector('[data-a="back"]').onclick = closeRun;
  const sp = box.querySelector("[data-spot]"); if (sp) sp.addEventListener("click", closeRun);
}
function closeRun(){ $("sessRun").hidden = true; $("sessRun").innerHTML = ""; $("sessStart").hidden = false; $("todayGrid").hidden = false; renderToday(); }

/* ================= LISTS ================= */
const LIST = Object.fromEntries(D.lists.map(l => [l.id, l]));
const LISTS = () => D.lists.filter(l => shownT(l.t));
let LRES = store.get("lres", {});
function fillLTopic(){ const v = $("lTopic").value; $("lTopic").innerHTML = `<option value="">All topics</option>` + TOPS().filter(t => LISTS().some(l => l.t === t.key)).map(t => `<option value="${t.key}">${esc(t.name)} (${LISTS().filter(l => l.t === t.key).length})</option>`).join(""); $("lTopic").value = [...$("lTopic").options].some(o => o.value === v) ? v : ""; }
function lPool(){ const tp = $("lTopic").value, q = $("lq").value.trim().toLowerCase(); return LISTS().filter(l => (!tp || l.t === tp) && (!q || [l.title, l.ask, l.src, l.hook || "", ...l.items].join(" ").toLowerCase().includes(q))); }
function renderLists(){
  const p = lPool(), due = p.filter(l => isDue("l:" + l.id)).length, fresh = p.filter(l => !SRS["l:" + l.id]).length;
  $("lCount").textContent = `${p.length} lists · ${due} due · ${fresh} not yet drilled`;
  $("lDue").disabled = !due; $("lDue").textContent = due ? `Due lists only (${due})` : "Due lists only";
  let html = "";
  TOPS().forEach(t => {
    const g = p.filter(l => l.t === t.key); if (!g.length) return;
    html += `<div class="grouph">${esc(t.name)} <small>${esc(t.part)} · ${g.length}</small></div>`;
    html += g.map(l => { const r = LRES[l.id], mk = !r ? `<span class="mk">–</span>` : r.m.length ? `<span class="mk no">✗</span>` : `<span class="mk ok">✓</span>`, tag = l.ordered ? "ol" : "ul";
      return `<details class="item" data-lid="${l.id}"><summary>${mk}<span class="t"><b>${esc(l.title)}</b> <span class="tiny">· ${l.items.length}</span></span></summary><div class="body"><p class="tiny" style="margin:0">${esc(l.ask)}</p><${tag} class="lbody">${l.items.map((x, i) => `<li${r && r.m.includes(i) ? ' class="missed" title="Missed last time"' : ""}>${esc(x)}</li>`).join("")}</${tag}>${l.hook ? `<div class="lhook">${esc(l.hook)}</div>` : ""}<p class="tiny" style="margin:0">Source: ${esc(l.src)}${l.cases && l.cases.length ? " · " + caseLinks(l.cases) : ""}${l.rv ? ` · <a href="#" data-rv="${esc(l.rv)}">rule map</a>` : ""}</p><div class="row"><button class="btn small" data-drill1="${l.id}">Drill this list</button></div></div></details>`; }).join("");
  });
  $("lList").innerHTML = html || `<p class="empty">No list matches.</p>`;
}
function startLists(cards){
  if (!cards.length) return;
  $("lSetup").hidden = true; $("lList").hidden = true;
  runCards($("lRun"), cards, {label: "List", onEnd: listsEnd}); window.scrollTo({top: 0});
}
function lDrillCards(dueOnly){
  const p = lPool(), k = l => "l:" + l.id;
  const due = shuffle(p.filter(l => isDue(k(l)))); if (dueOnly) return due.map(l => ({p: "l", id: l.id}));
  const fresh = shuffle(p.filter(l => !SRS[k(l)])), rest = p.filter(l => SRS[k(l)] && !isDue(k(l))).sort((a, b) => SRS[k(a)].d - SRS[k(b)].d);
  return [...due, ...fresh, ...rest].slice(0, 10).map(l => ({p: "l", id: l.id}));
}
function listsEnd(box, r){
  box.innerHTML = `<div class="panel"><div class="score"><span class="big">${r.right}/${r.done}</span><span class="tiny">lists recalled in full</span></div><p class="tiny" style="margin:0">Lists with any missed item go on your fix list and come back sooner.</p><div class="row"><button class="btn primary" data-a="more">Another 10</button><button class="btn ghost" data-a="back">Back to all lists</button></div></div>`;
  box.querySelector('[data-a="more"]').onclick = () => startLists(lDrillCards(false));
  box.querySelector('[data-a="back"]').onclick = () => { box.hidden = true; box.innerHTML = ""; $("lSetup").hidden = false; $("lList").hidden = false; renderLists(); };
}
$("lStart").onclick = () => startLists(lDrillCards(false));
$("lDue").onclick = () => startLists(lDrillCards(true));
$("lTopic").onchange = renderLists;
$("lq").addEventListener("input", () => { clearTimeout(sT); sT = setTimeout(renderLists, 200); });
$("lList").addEventListener("click", e => { const b = e.target.closest("[data-drill1]"); if (b) startLists([{p: "l", id: b.dataset.drill1}]); });

/* ================= PAST EXAMS: MCQ ================= */
function setExamMode(m){ document.querySelectorAll("[data-em]").forEach(b => b.setAttribute("aria-pressed", b.dataset.em === m)); $("e-mcq").hidden = m !== "mcq"; $("e-essay").hidden = m !== "essay"; if (m === "essay") renderEssays(); else renderQSetup(); }
document.querySelector("[data-em]").parentElement.addEventListener("click", e => { const b = e.target.closest("[data-em]"); if (b) setExamMode(b.dataset.em); });
const EXAMS = [...new Set(D.mcq.map(q => q.exam))];
let qExamSel = new Set(store.get("qexams", EXAMS));
let qhist = store.get("qhist", {});
function qPool(){
  let p = MCQS().filter(q => qExamSel.has(q.exam) && (!$("inCov").checked || q.cov === "in"));
  if ($("qMissed").checked) p = p.filter(q => qhist[q.id] && qhist[q.id].r === 0);
  return p;
}
function renderQSetup(){
  $("qExams").innerHTML = EXAMS.map(x => { const n = MCQS().filter(q => q.exam === x && (!$("inCov").checked || q.cov === "in")).length; return `<label class="chip${qExamSel.has(x) ? " on" : ""}" for="qe_${x.replace(/\W/g, "")}"><input type="checkbox" id="qe_${x.replace(/\W/g, "")}" data-x="${esc(x)}"${qExamSel.has(x) ? " checked" : ""}>${esc(x)} <span class="tiny">${n}</span></label>`; }).join("");
  $("qMissedCt").textContent = `(${MCQS().filter(q => qhist[q.id] && qhist[q.id].r === 0).length})`;
  $("qPool").textContent = `${qPool().length} items in this selection`;
  store.set("qexams", [...qExamSel]);
  $("qSetup").hidden = false; $("qBox").hidden = true;
}
$("qExams").addEventListener("change", e => { const x = e.target.dataset.x; if (!x) return; e.target.checked ? qExamSel.add(x) : qExamSel.delete(x); renderQSetup(); });
$("qMissed").onchange = renderQSetup;
$("inCov").onchange = () => { if (!$("e-essay").hidden) renderEssays(); else renderQSetup(); };
let Q = [], qi = 0, qans = [];
function startQuiz(){
  let p = qPool(); if (!p.length){ $("qPool").textContent = "No items. Tick at least one exam."; return; }
  p = $("qN").value === "all" ? p : shuffle(p).slice(0, +$("qN").value);
  if ($("qN").value === "all") p = p.slice().sort((a, b) => EXAMS.indexOf(a.exam) - EXAMS.indexOf(b.exam) || a.n - b.n);
  Q = p; qi = 0; qans = new Array(Q.length).fill(null); $("qSetup").hidden = true; $("qBox").hidden = false; renderQ();
}
$("qStart").onclick = startQuiz;
function mcqBody(q, a){
  const story = q.story && D.stories[q.story];
  return `<div class="tags"><span class="tag${q.exam.includes("news") ? " news" : ""}">${esc(q.exam)} · item ${q.n}</span><span class="tag">${esc(tname(q.t))}</span>${q.cov === "beyond" ? '<span class="tag beyond">beyond midterm coverage</span>' : ""}</div>
  ${story ? `<div class="story">${esc(story)}</div>` : ""}
  <p class="stem">${esc(q.q)}</p>
  <div class="choices">${q.c.map((c, i) => `<button class="choice" data-i="${i}"><span class="L">${LET[i]}.</span><span>${esc(c)}</span></button>`).join("")}</div><div class="qfb"></div>`;
}
function fbHTML(q, a){
  const ok = a === q.a;
  return `<div class="expl"><div class="verdict ${ok ? "ok" : "no"}">${ok ? "Correct." : "Not quite."} Answer: ${LET[q.a]}. ${esc(q.c[q.a])}</div><p>${esc(q.e)}</p>${q.k ? `<div class="keynote"><b>Key note:</b> ${esc(q.k)}</div>` : ""}${q.cs && q.cs.length ? `<p class="tiny" style="margin:0">Cases: ${caseLinks(q.cs)}</p>` : ""}</div>`;
}
function bindMcq(root, q, onAnswer, onNext, preset){
  const box = root.querySelector(".choices"), fb = root.querySelector(".qfb");
  const show = a => { box.querySelectorAll("[data-i]").forEach((x, i) => { x.disabled = true; if (i === q.a) x.classList.add("right"); else if (i === a) x.classList.add("wrong"); }); fb.innerHTML = fbHTML(q, a) + `<div class="row" style="margin-top:10px"><button class="btn primary qnext">Next</button></div>`; fb.querySelector(".qnext").onclick = onNext; };
  if (preset !== null && preset !== undefined){ show(preset); return; }
  box.onclick = e => { const b = e.target.closest("[data-i]"); if (!b || b.disabled) return; const a = +b.dataset.i; onAnswer(a === q.a, a); show(a); fb.querySelector(".qnext").focus({preventScroll: true}); fb.scrollIntoView({block: "nearest", behavior: "smooth"}); };
}
function renderQ(){
  const q = Q[qi], right = qans.filter((a, i) => a !== null && a === Q[i].a).length, done = qans.filter(a => a !== null).length;
  $("qBox").innerHTML = `<div class="spread"><span class="lbl">Item ${qi + 1} of ${Q.length} · ${right}/${done} correct</span><div class="row"><button class="btn small ghost" id="qPrev"${qi === 0 ? " disabled" : ""}>Previous</button><button class="btn small ghost" id="qEnd">End</button></div></div><div class="prog"><i style="width:${100 * (qi + 1) / Q.length}%"></i></div>` + mcqBody(q, qans[qi]);
  bindMcq($("qBox"), q, (ok, a) => { qans[qi] = a; qhist[q.id] = {r: ok ? 1 : 0, n: ((qhist[q.id] || {}).n || 0) + 1}; store.set("qhist", qhist); rate("m:" + q.id, ok ? 2 : 0); }, () => { if (qi < Q.length - 1){ qi++; renderQ(); window.scrollTo({top: 0}); } else endQuiz(); }, qans[qi]);
  $("qPrev").onclick = () => { qi--; renderQ(); }; $("qEnd").onclick = endQuiz;
}
function endQuiz(){
  const right = Q.filter((q, i) => qans[i] === q.a).length;
  $("qBox").innerHTML = `<div class="score"><span class="big">${right} / ${Q.length}</span><span class="tiny">${Math.round(100 * right / Math.max(1, Q.length))}% · ${qans.filter(a => a === null).length} skipped</span></div>
  <div class="row"><button class="btn primary" id="qRetry">Retake the ones I missed</button><button class="btn ghost" id="qNew">New set</button></div>
  <div class="lbl">Missed and skipped</div>
  <div class="stack" style="gap:8px">${Q.map((q, i) => [q, qans[i]]).filter(([q, a]) => a !== q.a).map(([q, a]) => `<details class="item"><summary><span class="mk no">${a === null ? "–" : "✗"}</span><span class="t">${esc(q.exam)} #${q.n}: ${esc(q.q.length > 160 ? q.q.slice(0, 160) + "…" : q.q)}</span></summary><div class="body"><ul class="anslist">${q.c.map((c, j) => `<li class="${j === q.a ? "c" : ""}">${LET[j]}. ${esc(c)}</li>`).join("")}</ul><p style="margin:0">${esc(q.e)}</p>${q.k ? `<div class="keynote"><b>Key note:</b> ${esc(q.k)}</div>` : ""}</div></details>`).join("") || '<p class="empty">Nothing missed.</p>'}</div>`;
  $("qRetry").onclick = () => { const m = Q.filter((q, i) => qans[i] !== q.a); if (!m.length) return; Q = shuffle(m); qi = 0; qans = new Array(Q.length).fill(null); renderQ(); };
  $("qNew").onclick = renderQSetup;
}

/* ================= PAST EXAMS: essays ================= */
function renderEssays(){
  const src = $("esrc").value, cov = $("inCov").checked, att = store.get("attempts", {});
  const list = D.essays.filter(e => (src === "all" || (src === "news") === e.news) && (!cov || e.cov === "in"));
  $("elist").innerHTML = list.map(e => { const a = att[e.id] || []; const best = a.length ? Math.max(...a.map(x => x.score)) : null;
    return `<article class="ecard"><div class="spread"><div class="tags"><span class="tag${e.news ? " news" : ""}">${esc(e.exam)}${e.n ? " · Q" + e.n : ""}</span>${e.t.map(t => `<span class="tag">${esc(tname(t))}</span>`).join("")}</div>${best !== null ? `<span class="sc">best ${best}/10 · ${a.length} attempt${a.length === 1 ? "" : "s"}</span>` : ""}</div>
    <div class="ask">${esc(e.ask)}</div><p class="tiny" style="margin:0">${esc(e.prompt.slice(0, 220))}${e.prompt.length > 220 ? "…" : ""}</p>
    <div class="row"><button class="btn primary small" data-essay="${e.id}">Write it (22 min)</button><button class="btn small" data-spot="${e.id}">Spot the issues</button><button class="btn small ghost" data-show="${e.id}">Model answer</button></div><div data-m="${e.id}" hidden></div></article>`; }).join("") || '<p class="empty">No questions match.</p>';
}
$("esrc").onchange = renderEssays;
$("elist").addEventListener("click", e => { const b = e.target.closest("[data-show]"); if (!b) return; const box = $("elist").querySelector(`[data-m="${b.dataset.show}"]`); const es = ESS[b.dataset.show]; box.hidden = !box.hidden; if (!box.innerHTML) box.innerHTML = modelHTML(es, false); b.textContent = box.hidden ? "Model answer" : "Hide model answer"; });
const CLEAR_L = [["C", "Conclusion"], ["L", "Legal basis"], ["E", "Exception"], ["A", "Analysis"], ["R", "Restatement"]];
const clearWords = c => CLEAR_L.reduce((n, [k]) => n + (c[k] ? c[k].trim().split(/\s+/).length : 0), 0);
function clearHTML(c){
  return `<div class="model clear">${CLEAR_L.filter(([k]) => c[k]).map(([k, l]) => `<p><b class="ck" title="${l}">${k}</b> ${esc(c[k])}</p>`).join("")}</div>`;
}
function modelHTML(e, withRubric){
  return `<div class="stack" style="gap:10px">${e.clear ? `<div class="lbl">Back-page answer in CLEAR · ${clearWords(e.clear)} words · the length that fits</div>${clearHTML(e.clear)}<details class="fullm"><summary class="lbl">Full model answer for study · ${e.model.split(/\s+/).length} words</summary><div class="model">${esc(e.model)}</div></details>` : `<div class="lbl">Model answer · ${e.model.split(/\s+/).length} words</div><div class="model">${esc(e.model)}</div>`}
  <div class="lbl">Must-hit points</div><ul class="core">${e.core.map(c => `<li>${esc(c)}</li>`).join("")}</ul>
  ${e.cases && e.cases.length ? `<p class="tiny" style="margin:0">Cases: ${caseLinks(e.cases)}</p>` : ""}
  ${e.note ? `<div class="keynote"><b>Note:</b> ${esc(e.note)}</div>` : ""}
  ${e.src ? `<p class="tiny" style="margin:0">Sources (as of ${esc(e.asof || "")}): ${e.src.map(([t, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>`).join(" · ")}</p>` : ""}</div>`;
}

/* ================= ISSUE SPOTTER ================= */
let spId = store.get("spid", D.essays[0].id), spHist = store.get("sphist", {});
$("spSel").innerHTML = D.essays.map(e => `<option value="${e.id}">${esc(e.exam)}${e.n ? " Q" + e.n : ""}: ${esc(e.short)}</option>`).join("");
$("spGroups").innerHTML = D.issues.map(g => `<div class="igroup"><h4>${esc(g.g)}</h4><div class="ilist">${g.items.map(i => `<label class="iitem" data-iid="${i.id}" for="is_${i.id}"><input type="checkbox" id="is_${i.id}" value="${i.id}"><span>${esc(i.l)}<span class="h">${esc(i.h)}</span><span class="why"></span></span></label>`).join("")}</div></div>`).join("");
function applySpotScope(){ document.querySelectorAll(".iitem").forEach(l => { const off = HIDE && OUT_ISSUES.includes(l.dataset.iid); l.classList.toggle("off", off); if (off) l.querySelector("input").checked = false; }); }
function openSpot(id){ setTab("spot"); spId = id; renderSpot(); }
function renderSpot(){
  const e = ESS[spId] || D.essays[0]; spId = e.id; store.set("spid", spId); $("spSel").value = spId;
  $("spTags").innerHTML = `<span class="tag${e.news ? " news" : ""}">${esc(e.exam)}${e.n ? " · Q" + e.n : ""}</span>`;
  $("spFacts").textContent = e.prompt; $("spAsk").textContent = e.ask;
  $("spResult").hidden = true; $("spResult").innerHTML = "";
  document.querySelectorAll(".iitem").forEach(l => { l.classList.remove("hitok", "miss", "extra"); l.querySelector("input").checked = false; l.querySelector(".why").textContent = ""; });
  const h = Object.values(spHist); $("spStat").textContent = h.length ? `${h.length} problems checked · ${Math.round(100 * h.reduce((s, x) => s + x.hit, 0) / Math.max(1, h.reduce((s, x) => s + x.of, 0)))}% of model issues found` : "";
}
$("spSel").onchange = () => { spId = $("spSel").value; renderSpot(); };
$("spRand").onclick = () => { const pool = D.essays.filter(e => !spHist[e.id] && e.id !== spId); const pick = (pool.length ? pool : D.essays)[Math.floor(Math.random() * (pool.length || D.essays.length))]; spId = pick.id; renderSpot(); };
$("spReset").onclick = renderSpot;
$("spCheck").onclick = () => {
  const e = ESS[spId], want = new Set(e.issues), got = new Set([...document.querySelectorAll(".iitem input:checked")].map(x => x.value));
  let hit = 0;
  document.querySelectorAll(".iitem").forEach(l => { const id = l.dataset.iid, w = want.has(id), g = got.has(id), why = l.querySelector(".why");
    l.classList.toggle("hitok", w && g); l.classList.toggle("miss", w && !g); l.classList.toggle("extra", !w && g);
    why.textContent = w && g ? "Found" : w ? "Missed: the model answer turns on this" : g ? "Not in the model answer. Fine if you can tie it to a fact." : ""; if (w && g) hit++; });
  spHist[spId] = {hit, of: want.size}; store.set("sphist", spHist);
  e.issues.forEach(id => { const k = "i:" + spId + ":" + id; if (!(HIDE && OUT_ISSUES.includes(id))) got.has(id) ? fixTrack(k, 2) : fixAdd(k); });
  $("spResult").hidden = false;
  $("spResult").innerHTML = `<div class="expl"><div class="verdict ${hit === want.size ? "ok" : "no"}">You found ${hit} of ${want.size} issues.</div>
  <ul class="core" style="margin:0">${e.issues.map(id => ISS[id] ? `<li><b>${esc(ISS[id].l)}</b>${got.has(id) ? "" : " (missed)"}: <a href="#" data-rv="${ISS[id].rv}">rule map</a></li>` : "").join("")}</ul>
  <div class="lbl">What the answer has to say</div><ul class="core" style="margin:0">${e.core.map(c => `<li>${esc(c)}</li>`).join("")}</ul>
  ${e.cases && e.cases.length ? `<p class="tiny" style="margin:0">Anchor cases: ${caseLinks(e.cases)}</p>` : ""}
  <div class="row"><button class="btn primary small" data-essay="${e.id}">Now write it</button><button class="btn small" id="spNext">Next problem</button></div></div>`;
  $("spNext").onclick = () => $("spRand").click();
  $("spResult").scrollIntoView({block: "nearest", behavior: "smooth"});
};

/* ================= ESSAY TRAINER ================= */
let wId = store.get("wid", D.essays[0].id), drafts = store.get("drafts", {}), tLeft = 22 * 60, tRun = null;
$("wSel").innerHTML = `<optgroup label="Past exams">` + D.essays.filter(e => !e.news).map(e => `<option value="${e.id}">${esc(e.exam)}${e.n ? " Q" + e.n : ""}: ${esc(e.short)}</option>`).join("") + `</optgroup><optgroup label="2026 news (practice)">` + D.essays.filter(e => e.news).map(e => `<option value="${e.id}">${esc(e.short)}</option>`).join("") + `</optgroup>`;
function openEssay(id){ if (!ESS[id]) return; setTab("write"); wId = id; renderWrite(); }
function renderWrite(){
  const e = ESS[wId] || D.essays[0]; wId = e.id; store.set("wid", wId); $("wSel").value = wId;
  $("wTags").innerHTML = `<span class="tag${e.news ? " news" : ""}">${esc(e.exam)}${e.n ? " · Q" + e.n : ""}</span>${e.cov === "beyond" ? '<span class="tag beyond">partly beyond coverage</span>' : ""}`;
  $("wFacts").textContent = e.prompt; $("wAsk").textContent = e.ask;
  $("pad").value = drafts[wId] || ""; wc();
  $("wModel").hidden = true; $("wModel").innerHTML = "";
  resetTimer();
}
$("wSel").onchange = () => { wId = $("wSel").value; renderWrite(); };
function words(s){ return (s.trim().match(/\S+/g) || []).length; }
function wc(){
  const n = words($("pad").value), max = 200;
  $("wcN").textContent = n;
  $("wcBar").querySelector("i").style.width = Math.min(100, 100 * n / max) + "%";
  $("wcBar").querySelector(".band").style.left = (100 * 80 / max) + "%"; $("wcBar").querySelector(".band").style.width = (100 * 40 / max) + "%";
  $("wcBar").classList.toggle("over", n > 150);
  $("wcMsg").textContent = n === 0 ? "" : n < 60 ? "Too thin: you need the rule and the analysis" : n <= 120 ? "Fits your box on the back page" : n <= 150 ? "Long: four of these will not fit on the back" : "A dissertation: cut to C, L, A, R";
}
let saveT = null;
$("pad").addEventListener("input", () => { wc(); clearTimeout(saveT); saveT = setTimeout(() => { drafts[wId] = $("pad").value; store.set("drafts", drafts); }, 400); });
function fmt(s){ const neg = s < 0; s = Math.abs(s); return (neg ? "+" : "") + String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); }
function paintT(){ const t = $("tT"); t.textContent = fmt(tLeft); t.classList.toggle("low", tLeft <= 180 && tLeft > 0); t.classList.toggle("over", tLeft <= 0); }
function resetTimer(){ clearInterval(tRun); tRun = null; tLeft = +$("tLen").value * 60; $("tGo").textContent = "Start"; paintT(); }
$("tLen").onchange = resetTimer; $("tReset").onclick = resetTimer;
$("tGo").onclick = () => {
  if (tRun){ clearInterval(tRun); tRun = null; $("tGo").textContent = "Resume"; return; }
  $("tGo").textContent = "Pause"; $("pad").focus();
  tRun = setInterval(() => { tLeft--; paintT(); if (tLeft === 0) $("wcMsg").textContent = "Time. Finish your sentence, then reveal the model answer."; }, 1000);
};
$("wClear").onclick = () => { if ($("wClear").dataset.sure !== "1"){ $("wClear").dataset.sure = "1"; $("wClear").textContent = "Tap again to clear"; setTimeout(() => { $("wClear").dataset.sure = ""; $("wClear").textContent = "Clear"; }, 2500); return; } $("pad").value = ""; drafts[wId] = ""; store.set("drafts", drafts); wc(); $("wClear").dataset.sure = ""; $("wClear").textContent = "Clear"; };
$("wCopy").onclick = () => { const t = $("pad").value; const done = () => { $("wCopy").textContent = "Copied"; setTimeout(() => $("wCopy").textContent = "Copy my answer", 1500); };
  try { navigator.clipboard.writeText(t).then(done, () => { $("pad").select(); }); } catch(e){ $("pad").select(); } };
$("wReveal").onclick = () => {
  const e = ESS[wId]; if (tRun){ clearInterval(tRun); tRun = null; $("tGo").textContent = "Resume"; }
  const used = +$("tLen").value * 60 - tLeft;
  $("wModel").hidden = false;
  $("wModel").innerHTML = `<div class="panel"><h2>Grade yourself</h2><p class="tiny" style="margin:0">Tick only what your answer actually does. Gatmaytan grades ‘mastery’ and ‘comprehensive and accurate arguments’; 7 of 10 passes.</p>
  <div class="rubric" id="rub">${e.points.map(([t, p], i) => `<label for="rb_${i}"><input type="checkbox" id="rb_${i}" data-p="${p}"><span>${esc(t)}</span><span class="p">${p} pt${p === 1 ? "" : "s"}</span></label>`).join("")}</div>
  <div class="spread"><span class="score"><span class="big" id="rbS">0</span><span class="tiny">/ 10</span></span><button class="btn primary" id="rbSave">Save this attempt</button></div>
  <div class="hist" id="rbHist"></div>
  <div class="clearchk"><div class="lbl">Format check (not scored)</div>${["Conclusion is the first sentence", "Legal basis names the rule (a case only if you are sure)", "Analysis uses the specific facts", "Restatement agrees with the conclusion", "Fits the box: about 80–120 words", "Every word would be readable by hand"].map((t, i) => `<label for="cc_${i}"><input type="checkbox" id="cc_${i}"> ${t}</label>`).join("")}</div></div>` + `<div class="panel">${modelHTML(e, true)}</div>`;
  const sum = () => { const s = [...document.querySelectorAll("#rub input:checked")].reduce((a, x) => a + +x.dataset.p, 0); $("rbS").textContent = s; return s; };
  $("rub").onchange = sum;
  const hist = () => { const a = store.get("attempts", {})[wId] || []; $("rbHist").innerHTML = a.length ? a.slice(-6).reverse().map(x => `<span>${esc(x.date)} · ${x.score}/10 · ${x.words} words · ${x.mins} min</span>`).join("") : ""; };
  hist();
  $("rbSave").onclick = () => { const att = store.get("attempts", {}); (att[wId] = att[wId] || []).push({score: sum(), words: words($("pad").value), mins: Math.max(1, Math.round(used / 60)), date: manilaToday()}); store.set("attempts", att); $("rbSave").textContent = "Saved"; $("rbSave").disabled = true; hist(); };
  $("wModel").scrollIntoView({block: "start", behavior: "smooth"});
};

/* ================= PRINTABLES ================= */
function firstSentence(r){ const m = r.match(/^.*?[a-z0-9)’'”][.;](?=\s+[A-Z(‘“]|$)/); let s = m ? m[0] : r; if (s.length > 135) s = s.slice(0, 130).replace(/\s+\S*$/, "") + "…"; return s; }
let printed = false;
function renderPrint(){
  if (printed) return; printed = true;
  $("sheet1").innerHTML = `<h2>Issue checklist</h2><div class="sub">Consti 1 midterm · run it in the margin of every problem · 22 minutes each: read twice 4, outline 4, write 11, check 3</div>
  <div class="cl">${ISSUES().map(g => `<div class="grp"><h4>${esc(g.g)}</h4><ul>${g.items.map(i => `<li><b>${esc(i.l)}.</b> ${esc(i.h)}</li>`).join("")}</ul></div>`).join("")}
  <div class="grp"><h4>Numbers</h4><ul>${D.numbers.map(([a, b]) => `<li><b>${esc(a)}:</b> ${esc(b)}</li>`).join("")}</ul></div>
  <div class="grp"><h4>Write it in CLEAR</h4><ul><li><b>C</b> Conclusion first (valid/void; Yes/No).</li><li><b>L</b> Rule + provision; a case only if you are sure (else ‘in one case, the Court held…’).</li><li><b>E</b> Exception only if one applies.</li><li><b>A</b> Apply to the exact words of the law or story.</li><li><b>R</b> Restate; it must agree with C.</li><li>80–120 words; all answers fit on the back of the questionnaire.</li><li>Did you answer the question asked (‘in his favor’, ‘no procedural issues’)?</li></ul></div>
  <div class="grp"><h4>Exam room (5.0 if broken)</h4><ul><li>Student ID number only; no name or other marks.</li><li>Write at the back of the questionnaire; everything must fit.</li><li>Pen and correction tape only; no devices; nothing else on the table.</li><li>No talking or signals. Write legibly: unreadable = wrong.</li></ul></div></div>`;
  const anc = CASES().filter(c => c.a);
  $("sheet2").innerHTML = `<h2>Anchor cases</h2><div class="sub">${anc.length} cases that carry a test · grouped by syllabus part${HIDE ? " · citizenship and territory left out" : ""}</div><div class="anc">${TOPS().map(t => { const g = anc.filter(c => c.t === t.key); return g.length ? `<div class="grp"><h4>${esc(t.name)}</h4>${g.map(c => `<p><b>${esc(c.n)}</b> (${esc(c.y)}): ${esc(c.s || firstSentence(c.r))}</p>`).join("")}</div>` : ""; }).join("")}</div>`;
}

/* ================= universal search ================= */
// One box in the header searches rule maps (and their diagrams), cases, lists, the issue checklist, numbers, MCQs and essays.
const fold = s => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
let GIDX = null, gT = null, gPrevTab = "today", gRx = {};
function gIndex(){
  const items = [];
  const heads = new Map();
  SECS.forEach(sec => { let h = sec.dataset.title; sec.querySelectorAll("h3, :is(p,li,.codal,td,h4,.test,aside,.vn,figcaption,.vt,.hk,.ln,.vft,.rrow)").forEach(el => {
    if (el.tagName === "H3"){ h = el.textContent; }
    heads.set(el, `${sec.dataset.title} › ${h}`);
  }); });
  [...document.querySelectorAll("#rcontent :is(p,li,.codal,td,h3,h4,.test,aside,.vn,figcaption,.vt,.hk,.ln,.vft,.rrow)")].filter(el => !el.querySelector("p,li,td,.vn,.test,aside,.rrow") && !el.closest(".calc,.hwall,.walkbar,.walkp,.walkout,.vtools,.qread") && el.textContent.trim().length > 2).forEach(el => {
    const sec = el.closest("section.rv"), isHead = /^H[34]$/.test(el.tagName) || el.classList.contains("vt");
    const sm = el.querySelector("small"), vtt = el.querySelector(".vtt"), title = isHead ? (vtt ? vtt.textContent : el.textContent.replace(sm ? sm.textContent : "", "")).trim() : "";
    let text = el.textContent;
    if (isHead){ let nx = el.classList.contains("vt") ? el.parentElement.querySelector("figcaption") : el.nextElementSibling; while (nx && nx.tagName === "FIGURE") nx = nx.nextElementSibling; text = nx ? nx.textContent : ""; }
    items.push({g: "rule", el: el.classList.contains("vt") || el.closest(".vfacts") ? el.closest("figure") : el, sec, title, text: text.replace(/\s+/g, " ").trim(), ctx: heads.get(el) || sec.dataset.title});
  });
  D.cases.forEach(c => items.push({g: "case", id: c.id, t: c.t, title: c.n + " (" + c.y + ")", text: [c.s, c.r, c.test, c.f, c.h, c.x, c.g, c.sub].filter(Boolean).join(" · "), ctx: tname(c.t) + (c.a ? " · anchor" : c.ref ? " · mentioned only" : "")}));
  D.lists.forEach(l => items.push({g: "list", id: l.id, t: l.t, title: l.title, text: [l.ask, ...l.items, l.src, l.hook].filter(Boolean).join(" · "), ctx: tname(l.t) + " · " + l.items.length + " items"}));
  D.issues.forEach(gr => gr.items.forEach(i => items.push({g: "issue", id: i.id, title: i.l, text: i.h, ctx: gr.g, rv: i.rv})));
  D.numbers.forEach(([a, b]) => items.push({g: "num", title: a, text: b, ctx: "Numbers he can alter"}));
  D.mcq.forEach(q => items.push({g: "mcq", id: q.id, t: q.t, title: `${q.exam} #${q.n}`, text: [q.q, ...q.c, q.e, q.k].filter(Boolean).join(" · "), ctx: tname(q.t)}));
  D.essays.forEach(e => items.push({g: "essay", id: e.id, title: `${e.exam}${e.n ? " Q" + e.n : ""}: ${e.short}`, text: [e.ask, e.prompt, ...(e.core || []), e.model].join(" · "), ctx: e.news ? "2026 news problem" : "Past essay question"}));
  items.forEach(it => { it.ft = fold(it.title); it.fx = fold(it.text); });
  return items;
}
const G_LBL = {rule: "Rule maps", case: "Cases", list: "Lists and requisites", issue: "Issue checklist", num: "Numbers", mcq: "Past exams: multiple choice", essay: "Essay and news problems"};
function gVisible(it){
  if (it.g === "rule") return secShown(SECS.indexOf(it.sec));
  if (it.g === "issue") return !(HIDE && OUT_ISSUES.includes(it.id));
  return !it.t || shownT(it.t);
}
const G_STOP = new Set("of the a an and in on to for by or is at as v vs".split(" "));
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
function gScore(it, terms, phrase){
  let s = 0;
  for (const t of terms){ const rx = gRx[t], a = rx.test(it.ft), b = a || rx.test(it.fx); if (!a && !b) return 0; s += a ? 10 : 2; }
  if (phrase && (it.ft.includes(phrase))) s += 25; else if (phrase && it.fx.includes(phrase)) s += 6;
  if (it.ft.startsWith(terms[0])) s += 6;
  if (it.g === "case" || it.g === "list") s += 3;
  return s;
}
function gMark(text, terms, len){
  const f = fold(text); let i = -1;
  for (const t of terms){ const k = f.indexOf(t); if (k >= 0 && (i < 0 || k < i)) i = k; }
  let a = 0, b = text.length;
  if (len && text.length > len){ a = Math.max(0, i - Math.floor(len / 3)); b = Math.min(text.length, a + len); }
  const sub = text.slice(a, b), fs = f.slice(a, b), aligned = f.length === text.length;
  let out = "", pos = 0;
  if (aligned){
    const hits = [];
    terms.forEach(t => { let k = fs.indexOf(t); while (k >= 0){ hits.push([k, k + t.length]); k = fs.indexOf(t, k + t.length); } });
    hits.sort((x, y) => x[0] - y[0]);
    hits.forEach(([x, y]) => { if (x < pos) return; out += esc(sub.slice(pos, x)) + "<mark>" + esc(sub.slice(x, y)) + "</mark>"; pos = y; });
  }
  out += esc(sub.slice(pos));
  return (a > 0 ? "…" : "") + out + (b < text.length ? "…" : "");
}
function gSearch(){
  const raw = $("gq").value.trim(), q = fold(raw);
  if (q.length < 2){ if (!$("v-search").hidden) gClose(); return; }
  GIDX = GIDX || gIndex();
  const all = q.split(/\s+/).filter(Boolean), kept = all.filter(t => !G_STOP.has(t)), terms = kept.length ? kept : all, phrase = all.length > 1 ? q : "";
  gRx = Object.fromEntries(terms.map(t => [t, new RegExp("(?:^|[^a-z0-9])" + reEsc(t))]));
  const res = GIDX.filter(gVisible).map(it => ({it, s: gScore(it, terms, phrase)})).filter(r => r.s > 0).sort((x, y) => y.s - x.s);
  if ($("v-search").hidden){ gPrevTab = store.get("tab", "today"); TABS.forEach(x => $("v-" + x).hidden = true); document.querySelectorAll(".tabs [data-tab]").forEach(b => b.setAttribute("aria-selected", false)); $("v-search").hidden = false; window.scrollTo({top: 0}); }
  $("gHead").textContent = `Results for “${raw}”`;
  $("gSum").textContent = res.length ? `${res.length} match${res.length === 1 ? "" : "es"}. Tap a result to go there. Press Esc to close.` : "No matches. Try fewer or shorter words (for example “quorum”, “two-thirds”, “Avelino”).";
  const groups = Object.keys(G_LBL).map(g => [g, res.filter(r => r.it.g === g)]).filter(([, r]) => r.length);
  const best = res.slice(0, 5);
  const card = (r, i) => { const it = r.it; return `<button class="gres" data-gi="${GIDX.indexOf(it)}"><span class="gk">${esc(G_LBL[it.g].split(":")[0])} · ${esc(it.ctx)}</span>${it.title ? `<b>${gMark(it.title, terms)}</b>` : ""}<span class="gx">${gMark(it.text, terms, it.title ? 170 : 240)}</span></button>`; };
  $("gRes").innerHTML = (res.length > 6 ? `<section><div class="lbl">Best matches</div><div class="glist">${best.map(card).join("")}</div></section>` : "") +
    groups.map(([g, r]) => `<section data-gg="${g}"><div class="lbl">${G_LBL[g]} · ${r.length}</div><div class="glist">${r.slice(0, 8).map(card).join("")}</div>${r.length > 8 ? `<button class="btn small ghost gmore" data-gm="${g}">Show all ${r.length}</button>` : ""}</section>`).join("");
  $("gRes").querySelectorAll("[data-gm]").forEach(b => b.onclick = () => { const r = groups.find(([g]) => g === b.dataset.gm)[1]; b.previousElementSibling.innerHTML = r.map(card).join(""); b.remove(); });
}
function gClose(){ $("v-search").hidden = true; setTab(gPrevTab || "today"); }
function gGo(it){
  if (it.g === "rule"){ setTab("rules"); const i = SECS.indexOf(it.sec); if (i !== curSec) openSec(i, false); requestAnimationFrame(() => { it.el.scrollIntoView({block: "center"}); it.el.classList.add("flash"); setTimeout(() => it.el.classList.remove("flash"), 1800); }); return; }
  if (it.g === "case") return openCase(it.id);
  if (it.g === "list"){ setTab("lists"); $("lRun").hidden = true; $("lSetup").hidden = false; $("lList").hidden = false; $("lq").value = ""; $("lTopic").value = ""; renderLists(); const d = $("lList").querySelector(`[data-lid="${it.id}"]`); if (d){ d.open = true; d.scrollIntoView({block: "center"}); d.classList.add("flash"); setTimeout(() => d.classList.remove("flash"), 1800); } return; }
  if (it.g === "issue"){ setTab("rules"); goToId(it.rv); return; }
  if (it.g === "num"){ setTab("rules"); goToId("method-numbers"); return; }
  if (it.g === "mcq"){ const q = D.mcq.find(x => x.id === it.id); openModal(`<div class="spread"><h3 id="mTitle" style="font-style:normal">${esc(q.exam)} · item ${q.n}</h3><button class="btn small ghost" data-close>Close</button></div>${mcqBody(q, null)}`); bindMcq($("modal"), q, ok => { qhist[q.id] = {r: ok ? 1 : 0, n: ((qhist[q.id] || {}).n || 0) + 1}; store.set("qhist", qhist); rate("m:" + q.id, ok ? 2 : 0); }, closeModal); return; }
  if (it.g === "essay"){ const e = ESS[it.id]; openModal(`<div class="spread"><h3 id="mTitle" style="font-style:normal">${esc(it.title)}</h3><button class="btn small ghost" data-close>Close</button></div><div class="facts" style="font-size:.95rem">${esc(e.prompt)}</div><div class="askbox">${esc(e.ask)}</div><div class="row"><button class="btn primary small" data-essay="${e.id}">Write it (22 min)</button><button class="btn small" data-spot="${e.id}">Spot the issues</button></div><details class="dgrev"><summary>Show the answer</summary><div style="padding:0 12px 12px">${modelHTML(e, false)}</div></details>`); $("modal").querySelectorAll("[data-essay],[data-spot]").forEach(b => b.addEventListener("click", closeModal)); }
}
$("gq").addEventListener("input", () => { clearTimeout(gT); gT = setTimeout(gSearch, 160); });
$("gq").addEventListener("keydown", e => { if (e.key === "Escape"){ $("gq").value = ""; gClose(); $("gq").blur(); } if (e.key === "Enter"){ clearTimeout(gT); gSearch(); const f = $("gRes").querySelector(".gres"); if (f && e.altKey) f.click(); } });
$("gBack").onclick = () => { $("gq").value = ""; gClose(); };
$("gRes").addEventListener("click", e => { const b = e.target.closest("[data-gi]"); if (b) gGo(GIDX[+b.dataset.gi]); });
document.addEventListener("keydown", e => { if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && $("scrim").hidden){ e.preventDefault(); $("gq").focus(); $("gq").select(); } });

/* ================= scope toggle wiring ================= */
function applyScope(){
  $("scopeBtn").setAttribute("aria-pressed", HIDE); $("scopeState").textContent = HIDE ? "hidden" : "shown";
  store.set("hideCitTerr", HIDE);
  buildSide(); if (!secShown(curSec)) openSec(visIdx()[0], false); else openSec(curSec, false);
  if ($("rq").value) runSearch();
  fillTopicSel(); renderCases(); applySpotScope(); dueBadge();
  if ($("c-drill").hidden === false && $("dSetup").hidden === false) renderDSetup();
  if ($("qSetup").hidden === false) renderQSetup();
  printed = false; if (!$("v-print").hidden) renderPrint();
  fillLTopic(); if (!$("lList").hidden) renderLists();
  if (!$("v-today").hidden) renderToday();
  if (!$("v-search").hidden) gSearch();
  applyScopeMarks();
}
$("scopeBtn").onclick = () => { HIDE = !HIDE; applyScope(); };

/* ================= boot ================= */
renderClock(); setInterval(renderClock, 60000);
buildSide(); openSec(Math.min(store.get("sec", 0), SECS.length - 1), false);
$("scopeBtn").setAttribute("aria-pressed", HIDE); $("scopeState").textContent = HIDE ? "hidden" : "shown";
if (!secShown(curSec)) openSec(visIdx()[0], false);
fillLTopic(); renderLists(); applyBlur(); applyScopeMarks();
applySpotScope(); renderCases(); renderDSetup(); setCaseMode("browse"); renderQSetup(); renderSpot(); renderWrite(); dueBadge();
(() => { const h = (location.hash || "").slice(1); setTab(TABS.includes(h) ? h : store.get("tab", "today"), false); })();
