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

/* ================= tabs ================= */
const TABS = ["today","rules","cases","exams","spot","write","print"];
function setTab(t, push){
  if (!TABS.includes(t)) t = "today";
  TABS.forEach(x => { $("v-" + x).hidden = x !== t; });
  document.querySelectorAll(".tabs [data-tab]").forEach(b => b.setAttribute("aria-selected", b.dataset.tab === t));
  store.set("tab", t);
  if (push !== false){ try { history.replaceState(null, "", "#" + t); } catch(e){} }
  if (t === "today") renderToday();
  if (t === "print") renderPrint();
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
  if (n > 1){ $("cdN").textContent = n; $("cdL").textContent = "days to the midterm (Fri, Oct 16, morning)"; }
  else if (n === 1){ $("cdN").textContent = "1"; $("cdL").textContent = "day to go. Light review, early night."; }
  else if (n === 0){ $("cdN").textContent = "Today"; $("cdL").textContent = "Checklist and anchor list, then go."; }
  else { $("cdN").textContent = "Done"; $("cdL").textContent = "The midterm was on Oct 16."; }
}

/* ================= case modal ================= */
function caseHTML(c){
  const t = TOP[c.t];
  return `<div class="spread"><h3 id="mTitle">${esc(c.n)}</h3><button class="btn small ghost" data-close>Close</button></div>
  <div class="meta">${esc(c.y)} · ${esc(c.sub || (t ? t.name : ""))}${c.a ? " · anchor case" : ""}</div>
  <dl>
    <div><dt>Rule</dt><dd class="rule">${esc(c.r)}</dd></div>
    ${c.test ? `<div><dt>Test</dt><dd>${esc(c.test)}</dd></div>` : ""}
    ${c.f ? `<div><dt>Facts</dt><dd>${esc(c.f)}</dd></div>` : ""}
    ${c.h ? `<div><dt>Holding</dt><dd>${esc(c.h)}</dd></div>` : ""}
    ${c.x ? `<div><dt>Use it when</dt><dd>${esc(c.x)}</dd></div>` : ""}
  </dl>
  ${c.g ? `<div class="gatn"><strong>Gatmaytan:</strong> ${esc(c.g)}</div>` : ""}
  ${c.w ? `<div class="warnn"><strong>Caution:</strong> ${esc(c.w)}</div>` : ""}
  ${t && t.sec ? `<div><button class="btn small" data-gosec="${t.sec}">Open the rule map: ${esc(t.name)}</button></div>` : ""}`;
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
}
function nextLbl(k, g){
  const st = SRS[k] || {s: -1}; let s = st.s;
  if (g === 0) s = 0; else if (g === 1) s = Math.max(s, 0); else if (g === 2) s = Math.min(Math.max(s + 1, 1), STEPS.length - 1); else s = Math.min(Math.max(s + 2, 3), STEPS.length - 1);
  if (g === 1){ const m = Math.max(5, STEPS[s] / 2); return m >= 60 ? Math.round(m / 60) + " hr" : m + " min"; }
  return STEP_LBL[s];
}
const isDue = k => SRS[k] && SRS[k].d <= Date.now();
const dueKeys = () => Object.keys(SRS).filter(k => isDue(k) && validKey(k));
function validKey(k){ const [p, id] = k.split(":"); return p === "m" ? D.mcq.some(q => q.id === id) : !!CASE[id]; }
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
  $("dayTodo").innerHTML = d.items.map(it => `<li><span class="k">${esc(it.k)}</span><div>${esc(it.t)}${(it.rv || it.e || it.go) ? `<div class="links">${(it.rv || []).map(id => `<button class="btn small" data-rv="${id}">${esc(rvTitle(id))}</button>`).join("")}${(it.e || []).map(id => ESS[id] ? `<button class="btn small" data-essay="${id}">Write: ${esc(ESS[id].short)}</button>` : "").join("")}${it.go ? `<button class="btn small" data-go="${it.go}">${esc(it.goL)}</button>` : ""}</div>` : ""}</div></li>`).join("");
  $("week").innerHTML = days.map(x => `<button data-day="${x.date}" aria-current="${x.date === planDay}" class="${x.date < today ? "past" : ""}"><span class="w">${esc(x.short)}</span><span>${esc(x.focus)}</span></button>`).join("");
  // stats
  const seen = D.cases.filter(c => SRS["cr:" + c.id] || SRS["fc:" + c.id] || SRS["rc:" + c.id]).length;
  const known = D.cases.filter(c => ["cr:","fc:","rc:"].some(p => SRS[p + c.id] && SRS[p + c.id].s >= 3)).length;
  const qh = store.get("qhist", {}); const qa = Object.values(qh); const qr = qa.filter(x => x.r === 1).length;
  const att = store.get("attempts", {}); const al = Object.values(att).flat(); const avg = al.length ? (al.reduce((s, a) => s + a.score, 0) / al.length) : 0;
  $("stats").innerHTML = [
    [dueKeys().length, "cards due now"],
    [`${seen}/${D.cases.length}`, `cases drilled · ${known} at 1 day or more`],
    [qa.length ? Math.round(100 * qr / qa.length) + "%" : "–", `MCQ accuracy (${qa.length} answered)`],
    [al.length ? avg.toFixed(1) : "–", `average essay score /10 (${al.length} written)`]
  ].map(([v, k]) => `<div class="stat"><div class="v">${v}</div><div class="k">${k}</div></div>`).join("");
}
$("week").addEventListener("click", e => { const b = e.target.closest("[data-day]"); if (b){ planDay = b.dataset.day; renderToday(); } });
$("dayTodo").addEventListener("click", e => { const b = e.target.closest("[data-go]"); if (b) goAction(b.dataset.go); });
function goAction(g){
  if (g === "due"){ setTab("cases"); setCaseMode("drill"); startDrill(true); }
  else if (g.startsWith("mcq:")){ setTab("exams"); setExamMode("mcq"); qExamSel = new Set(g.slice(4).split(",")); renderQSetup(); }
  else if (g === "print") setTab("print");
  else if (g.startsWith("drill:")){ setTab("cases"); setCaseMode("drill"); dTop = new Set(g.slice(6).split(",")); renderDSetup(); }
}
$("goDue").onclick = () => goAction("due");
$("goMcq").onclick = () => { setTab("exams"); setExamMode("mcq"); $("qN").value = "10"; startQuiz(); };

/* ================= RULE MAPS ================= */
const SECS = [...document.querySelectorAll("#rcontent section.rv")];
let curSec = 0;
function rvTitle(id){ const el = document.getElementById(id); if (!el) return id; const s = el.closest("section.rv"); return el.tagName === "SECTION" ? el.dataset.title : el.textContent; }
function buildSide(){
  $("rsecs").innerHTML = SECS.map((s, i) => `<li data-i="${i}"><button data-sec="${i}">${esc(s.dataset.title)}<small>${esc(s.dataset.short)}</small></button></li>`).join("");
  $("rsel").innerHTML = SECS.map((s, i) => `<option value="${i}">${esc(s.dataset.title)}</option>`).join("");
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
  $("rprev").hidden = i === 0; $("rnext").hidden = i === SECS.length - 1;
  if (i > 0) $("rprev").textContent = "← " + SECS[i - 1].dataset.title;
  if (i < SECS.length - 1) $("rnext").textContent = SECS[i + 1].dataset.title + " →";
  store.set("sec", i);
  if (scroll !== false) window.scrollTo({top: 0});
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
$("rprev").onclick = () => openSec(curSec - 1); $("rnext").onclick = () => openSec(curSec + 1);
let blocks = null, sT = null, hits = [];
function clearSearch(){ $("rq").value = ""; $("rresults").hidden = true; $("rresults").innerHTML = ""; }
function runSearch(){
  const q = $("rq").value.trim().toLowerCase(), box = $("rresults");
  if (q.length < 3){ box.hidden = true; box.innerHTML = ""; return; }
  blocks = blocks || [...document.querySelectorAll("#rcontent :is(p,li,.codal,td,h3,h4,.test,aside)")].filter(el => !el.querySelector("p,li,td"));
  hits = blocks.filter(el => el.textContent.toLowerCase().includes(q));
  box.hidden = false;
  box.innerHTML = `<div class="spread"><span class="lbl">${hits.length} match${hits.length === 1 ? "" : "es"}${hits.length > 120 ? " · first 120" : ""}</span><button class="btn small ghost" id="rclear">Clear</button></div>` +
    hits.slice(0, 120).map((el, k) => { const sec = el.closest("section.rv"); const txt = el.textContent.replace(/\s+/g, " ").trim(); const p = txt.toLowerCase().indexOf(q); const s = Math.max(0, p - 70);
      return `<button class="btn res" data-k="${k}"><small>${esc(sec.dataset.title)}</small>${s > 0 ? "…" : ""}${esc(txt.slice(s, p))}<mark>${esc(txt.slice(p, p + q.length))}</mark>${esc(txt.slice(p + q.length, p + q.length + 130))}…</button>`; }).join("");
}
$("rq").addEventListener("input", () => { clearTimeout(sT); sT = setTimeout(runSearch, 220); });
$("rresults").addEventListener("click", e => { if (e.target.id === "rclear"){ clearSearch(); return; } const b = e.target.closest("[data-k]"); if (b){ const el = hits[+b.dataset.k]; const sec = el.closest("section.rv"); const i = SECS.indexOf(sec); if (i !== curSec) openSec(i, false); el.scrollIntoView({block: "center"}); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1600); } });

/* ================= CASES: browse ================= */
function setCaseMode(m){ document.querySelectorAll("[data-cm]").forEach(b => b.setAttribute("aria-pressed", b.dataset.cm === m)); $("c-browse").hidden = m !== "browse"; $("c-drill").hidden = m !== "drill"; if (m === "drill") renderDSetup(); }
document.querySelector("[data-cm]").parentElement.addEventListener("click", e => { const b = e.target.closest("[data-cm]"); if (b) setCaseMode(b.dataset.cm); });
$("ctopic").innerHTML = `<option value="">All topics</option>` + D.topics.map(t => `<option value="${t.key}">${esc(t.name)}</option>`).join("");
function renderCases(){
  const q = $("cq").value.trim().toLowerCase(), tp = $("ctopic").value, an = $("canchor").checked;
  const list = D.cases.filter(c => (!tp || c.t === tp) && (!an || c.a) && (!q || [c.n, c.r, c.f, c.h, c.x, c.y, c.sub].join(" ").toLowerCase().includes(q)));
  $("caseCt").textContent = `${list.length} of ${D.cases.length} cases`;
  let html = "", last = "";
  D.topics.forEach(t => {
    const g = list.filter(c => c.t === t.key); if (!g.length) return;
    html += `<div class="grouph">${esc(t.name)} <small>${esc(t.part)} · ${g.length}</small></div>`;
    html += g.map(c => `<button class="crow" data-case="${c.id}"><span class="nm">${esc(c.n)}<span class="yr">${esc(c.y)}</span></span><span>${c.a ? '<span class="tag anchor">anchor</span>' : ""}</span><span class="rl">${esc(c.r)}</span></button>`).join("");
  });
  $("clist").innerHTML = html || `<p class="empty">No case matches. Try fewer words.</p>`;
}
["cq","ctopic","canchor"].forEach(id => $(id).addEventListener(id === "cq" ? "input" : "change", renderCases));

/* ================= CASES: drill ================= */
const DIRS = {
  cr: {p: "cr", help: "You see the case name. Say the rule out loud, then flip and grade yourself honestly."},
  fc: {p: "fc", help: "You see the facts. Pick the case. Wrong answers come from the same topic, so read closely."},
  rc: {p: "rc", help: "You see the rule. Pick the case that laid it down."}
};
let dDir = store.get("ddir", "cr"), dTop = new Set(store.get("dtop", D.topics.map(t => t.key))), R = [], ri = 0, rDone = 0, rRight = 0;
function dPool(){ return D.cases.filter(c => dTop.has(c.t) && (!$("dAnchor").checked || c.a) && (dDir === "cr" || (dDir === "fc" ? c.f : c.r))); }
function renderDSetup(){
  document.querySelectorAll("#dDir [data-d]").forEach(b => b.setAttribute("aria-pressed", b.dataset.d === dDir));
  $("dDirHelp").textContent = DIRS[dDir].help;
  $("dTopics").innerHTML = D.topics.map(t => `<label class="chip${dTop.has(t.key) ? " on" : ""}" for="dt_${t.key}"><input type="checkbox" id="dt_${t.key}" data-t="${t.key}"${dTop.has(t.key) ? " checked" : ""}>${esc(t.name)}</label>`).join("");
  const p = dPool(), due = p.filter(c => isDue(dDir + ":" + c.id)).length, fresh = p.filter(c => !SRS[dDir + ":" + c.id]).length;
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
    const due = shuffle(p.filter(c => isDue(dDir + ":" + c.id))), fresh = shuffle(p.filter(c => !SRS[dDir + ":" + c.id])), rest = shuffle(p.filter(c => SRS[dDir + ":" + c.id] && !isDue(dDir + ":" + c.id))).sort((a, b) => SRS[dDir + ":" + a.id].d - SRS[dDir + ":" + b.id].d);
    cards = [...due, ...fresh, ...rest].slice(0, 20).map(c => ({p: dDir, id: c.id}));
  }
  R = cards; ri = 0; rDone = 0; rRight = 0; $("dSetup").hidden = true; $("dCard").hidden = false; showCard();
}
$("dStart").onclick = () => startDrill(false);
const STOPW = new Set("people republic philippines philippine commission elections comelec secretary executive house representatives senate court appeals city government association national department office party list board inc corporation union finance justice president tribunal electoral sandiganbayan ombudsman congress municipality province".split(" "));
function maskName(text, c){
  const toks = c.n.replace(/\(.*?\)/g, " ").split(/[^A-Za-zÀ-ÿñÑ’'-]+/).filter(w => w.length >= 4 && !STOPW.has(w.toLowerCase()));
  let t = text || "";
  toks.forEach(w => { t = t.replace(new RegExp("\\b" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "gi"), "▁▁▁"); });
  return t;
}
function distractors(c, n){
  const same = shuffle(D.cases.filter(x => x.id !== c.id && x.t === c.t)), other = shuffle(D.cases.filter(x => x.id !== c.id && x.t !== c.t));
  return [...same, ...other].slice(0, n);
}
function showCard(){
  if (ri >= R.length){ return endRound(); }
  const {p, id} = R[ri]; const c = CASE[id];
  const head = `<div class="spread"><span class="lbl">Card ${ri + 1} of ${R.length} · ${p === "cr" ? "Case → rule" : p === "fc" ? "Facts → case" : p === "rc" ? "Rule → case" : "MCQ"}</span><button class="btn small ghost" id="dQuit">End round</button></div><div class="dprog"><i style="width:${100 * ri / R.length}%"></i></div>`;
  if (p === "m"){ // MCQ item due from the exam bank
    const q = D.mcq.find(x => x.id === id);
    $("dCard").innerHTML = head + `<div class="card-face">${mcqBody(q, null)}</div>`;
    bindMcq($("dCard"), q, (ok) => { rate("m:" + q.id, ok ? 2 : 0); rDone++; if (ok) rRight++; }, () => { ri++; showCard(); });
  } else if (p === "cr"){
    $("dCard").innerHTML = head + `<div class="card-face"><div class="tags"><span class="tag">${esc(tname(c.t))}</span><span class="tag">${esc(c.y)}</span>${c.a ? '<span class="tag anchor">anchor</span>' : ""}</div><div class="prompt" style="font-style:italic">${esc(c.n)}</div><p class="tiny" style="margin:0">What rule or test does this case stand for? What fact decided it?</p><button class="btn primary" id="dFlip">Show the rule</button><div class="reveal" id="dRev" hidden></div></div>`;
    $("dFlip").onclick = () => {
      $("dFlip").hidden = true; const k = "cr:" + c.id;
      $("dRev").hidden = false;
      $("dRev").innerHTML = `<div class="prompt facts" style="font-size:1.05rem">${esc(c.r)}</div>${c.test ? `<p class="tiny" style="margin:0"><b>Test:</b> ${esc(c.test)}</p>` : ""}${c.h ? `<p class="tiny" style="margin:0"><b>Holding:</b> ${esc(c.h)}</p>` : ""}<div class="grade">${[["again","Again",0],["hard","Hard",1],["good","Good",2],["easy","Easy",3]].map(([cl, l, g]) => `<button class="btn ${cl}" data-g="${g}">${l}<small>${nextLbl(k, g)}</small></button>`).join("")}</div><button class="btn small ghost" data-case="${c.id}">Open full card</button>`;
      $("dRev").querySelector(".grade").onclick = e => { const b = e.target.closest("[data-g]"); if (!b) return; const g = +b.dataset.g; rate(k, g); rDone++; if (g >= 2) rRight++; ri++; showCard(); };
    };
  } else {
    const opts = shuffle([c, ...distractors(c, 3)]);
    const prompt = p === "fc" ? maskName(c.f, c) : maskName(c.r, c);
    $("dCard").innerHTML = head + `<div class="card-face"><div class="tags"><span class="tag">${esc(tname(c.t))}</span></div><div class="prompt facts">${esc(prompt)}</div><div class="choices">${opts.map((o, i) => `<button class="choice" data-i="${i}"><span class="L">${LET[i]}.</span><span><i>${esc(o.n)}</i> <span class="tiny">(${esc(o.y)})</span></span></button>`).join("")}</div><div id="dFb"></div></div>`;
    const box = $("dCard").querySelector(".choices");
    box.onclick = e => {
      const b = e.target.closest("[data-i]"); if (!b || b.disabled) return;
      const pick = opts[+b.dataset.i], ok = pick.id === c.id;
      box.querySelectorAll("[data-i]").forEach((x, i) => { x.disabled = true; if (opts[i].id === c.id) x.classList.add("right"); else if (x === b) x.classList.add("wrong"); });
      rate(p + ":" + c.id, ok ? 2 : 0); rDone++; if (ok) rRight++;
      $("dFb").innerHTML = `<div class="expl"><div class="verdict ${ok ? "ok" : "no"}">${ok ? "Correct." : "Not this one."} ${esc(c.n)} (${esc(c.y)})</div><p>${esc(p === "fc" ? c.r : (c.f || c.h || ""))}</p>${!ok ? `<p class="tiny">You picked <a class="cref" data-c="${pick.id}" href="#">${esc(pick.n)}</a>: ${esc(pick.r)}</p>` : ""}<div class="row"><button class="btn primary" id="dNext">Next card</button></div></div>`;
      $("dNext").onclick = () => { ri++; showCard(); }; $("dNext").focus();
    };
  }
  $("dQuit").onclick = endRound;
}
function endRound(){
  $("dCard").innerHTML = `<div class="panel"><div class="score"><span class="big">${rRight}/${rDone}</span><span class="tiny">remembered or answered correctly this round</span></div><p class="tiny" style="margin:0">Missed cards come back in about a minute; known cards move out to hours and days. ${dueKeys().length} cards are due now.</p><div class="row"><button class="btn primary" id="dAgain">Another round</button><button class="btn" id="dDue">Review due cards</button><button class="btn ghost" id="dBack">Change settings</button></div></div>`;
  $("dAgain").onclick = () => startDrill(false); $("dDue").onclick = () => startDrill(true); $("dBack").onclick = renderDSetup;
  dueBadge();
}

/* ================= PAST EXAMS: MCQ ================= */
function setExamMode(m){ document.querySelectorAll("[data-em]").forEach(b => b.setAttribute("aria-pressed", b.dataset.em === m)); $("e-mcq").hidden = m !== "mcq"; $("e-essay").hidden = m !== "essay"; if (m === "essay") renderEssays(); else renderQSetup(); }
document.querySelector("[data-em]").parentElement.addEventListener("click", e => { const b = e.target.closest("[data-em]"); if (b) setExamMode(b.dataset.em); });
const EXAMS = [...new Set(D.mcq.map(q => q.exam))];
let qExamSel = new Set(store.get("qexams", EXAMS));
let qhist = store.get("qhist", {});
function qPool(){
  let p = D.mcq.filter(q => qExamSel.has(q.exam) && (!$("inCov").checked || q.cov === "in"));
  if ($("qMissed").checked) p = p.filter(q => qhist[q.id] && qhist[q.id].r === 0);
  return p;
}
function renderQSetup(){
  $("qExams").innerHTML = EXAMS.map(x => { const n = D.mcq.filter(q => q.exam === x && (!$("inCov").checked || q.cov === "in")).length; return `<label class="chip${qExamSel.has(x) ? " on" : ""}" for="qe_${x.replace(/\W/g, "")}"><input type="checkbox" id="qe_${x.replace(/\W/g, "")}" data-x="${esc(x)}"${qExamSel.has(x) ? " checked" : ""}>${esc(x)} <span class="tiny">${n}</span></label>`; }).join("");
  $("qMissedCt").textContent = `(${D.mcq.filter(q => qhist[q.id] && qhist[q.id].r === 0).length})`;
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
function modelHTML(e, withRubric){
  return `<div class="stack" style="gap:10px"><div class="lbl">Model answer · ${e.model.split(/\s+/).length} words</div><div class="model">${esc(e.model)}</div>
  <div class="lbl">Must-hit points</div><ul class="core">${e.core.map(c => `<li>${esc(c)}</li>`).join("")}</ul>
  ${e.cases && e.cases.length ? `<p class="tiny" style="margin:0">Cases: ${caseLinks(e.cases)}</p>` : ""}
  ${e.note ? `<div class="keynote"><b>Note:</b> ${esc(e.note)}</div>` : ""}
  ${e.src ? `<p class="tiny" style="margin:0">Sources (as of ${esc(e.asof || "")}): ${e.src.map(([t, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>`).join(" · ")}</p>` : ""}</div>`;
}

/* ================= ISSUE SPOTTER ================= */
let spId = store.get("spid", D.essays[0].id), spHist = store.get("sphist", {});
$("spSel").innerHTML = D.essays.map(e => `<option value="${e.id}">${esc(e.exam)}${e.n ? " Q" + e.n : ""}: ${esc(e.short)}</option>`).join("");
$("spGroups").innerHTML = D.issues.map(g => `<div class="igroup"><h4>${esc(g.g)}</h4><div class="ilist">${g.items.map(i => `<label class="iitem" data-iid="${i.id}" for="is_${i.id}"><input type="checkbox" id="is_${i.id}" value="${i.id}"><span>${esc(i.l)}<span class="h">${esc(i.h)}</span><span class="why"></span></span></label>`).join("")}</div></div>`).join("");
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
  const n = words($("pad").value), max = 240;
  $("wcN").textContent = n;
  $("wcBar").querySelector("i").style.width = Math.min(100, 100 * n / max) + "%";
  $("wcBar").querySelector(".band").style.left = (100 * 150 / max) + "%"; $("wcBar").querySelector(".band").style.width = (100 * 30 / max) + "%";
  $("wcBar").classList.toggle("over", n > 220);
  $("wcMsg").textContent = n === 0 ? "" : n < 120 ? "Too thin: name the rule and a case" : n <= 190 ? "Good length" : n <= 220 ? "Long: four of these will not fit on one sheet" : "Too long: cut to the decisive issues";
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
  <div class="hist" id="rbHist"></div></div>` + `<div class="panel">${modelHTML(e, true)}</div>`;
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
  $("sheet1").innerHTML = `<h2>Issue checklist</h2><div class="sub">Consti 1 midterm · run it in the margin of every problem · 22 minutes each: read 3, outline 3, write 14, check 2</div>
  <div class="cl">${D.issues.map(g => `<div class="grp"><h4>${esc(g.g)}</h4><ul>${g.items.map(i => `<li><b>${esc(i.l)}.</b> ${esc(i.h)}</li>`).join("")}</ul></div>`).join("")}
  <div class="grp"><h4>Numbers</h4><ul>${D.numbers.map(([a, b]) => `<li><b>${esc(a)}:</b> ${esc(b)}</li>`).join("")}</ul></div>
  <div class="grp"><h4>Write it</h4><ul><li>Answer first (Yes/No; valid/void).</li><li>Rule + provision + one anchor case per issue.</li><li>Apply to the exact words of the law or story.</li><li>One-line conclusion. 150–180 words.</li><li>Did you answer the question asked (‘in his favor’, ‘no procedural issues’)?</li></ul></div></div>`;
  const anc = D.cases.filter(c => c.a);
  $("sheet2").innerHTML = `<h2>Anchor cases</h2><div class="sub">${anc.length} cases that carry a test · grouped by syllabus part</div><div class="anc">${D.topics.map(t => { const g = anc.filter(c => c.t === t.key); return g.length ? `<div class="grp"><h4>${esc(t.name)}</h4>${g.map(c => `<p><b>${esc(c.n)}</b> (${esc(c.y)}): ${esc(c.s || firstSentence(c.r))}</p>`).join("")}</div>` : ""; }).join("")}</div>`;
}

/* ================= boot ================= */
renderClock(); setInterval(renderClock, 60000);
buildSide(); openSec(Math.min(store.get("sec", 0), SECS.length - 1), false);
renderCases(); renderDSetup(); setCaseMode("browse"); renderQSetup(); renderSpot(); renderWrite(); dueBadge();
(() => { const h = (location.hash || "").slice(1); setTab(TABS.includes(h) ? h : store.get("tab", "today"), false); })();
