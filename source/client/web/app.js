"use strict";
/* CollabNet UI: plain client-side JavaScript. Talks to the local gateway over HTTP (fetch/XHR) and
   receives live updates through Server-Sent Events. All user-provided text goes through textContent. */
const $ = (id) => document.getElementById(id);
const H = { "X-Requested-With": "collabnet" };
const MAX_UPLOAD = 2 * 1024 * 1024 * 1024;
const state = { user: null, peers: [], target: "*", online: false, transfers: new Map(), pending: new Map() };

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}
function toast(text, kind) {
  const t = el("div", "toast " + (kind || ""), text);
  $("toasts").appendChild(t);
  setTimeout(() => t.remove(), 5000);
}
const fmtSize = (n) => n < 1024 ? n + " B" : n < 1048576 ? (n / 1024).toFixed(1) + " KB" : (n / 1048576).toFixed(1) + " MB";
const fmtTime = (ts) => new Date(ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

async function api(path, body) {
  const r = await fetch(path, body === undefined ? {} : { method: "POST", headers: { ...H, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || r.statusText);
  return d;
}

/* ---------------------------------------------------------------- status / stats */
function setStatus(s, extra) {
  state.online = s === "online";
  const dot = $("statusDot");
  dot.className = "dot " + (s === "online" ? "on" : s === "offline" ? "off" : "mid");
  $("statusText").textContent = s;
  const banner = $("banner");
  if (s === "reconnecting" || s === "connecting") {
    banner.textContent = "Mất kết nối" + (extra ? " (" + extra + ")" : "") + " — đang kết nối lại…";
    banner.classList.remove("hidden");
  } else banner.classList.add("hidden");
  $("text").disabled = !state.online;
  $("sendBtn").disabled = !state.online;
  $("attach").disabled = !state.online || state.target === "*";
  if (s === "offline") { $("login").classList.remove("hidden"); state.user = null; }
}
function showStats(s) {
  const c = $("stats");
  c.replaceChildren();
  if (!s) return;
  for (const t of [s.cc.toUpperCase() + " · " + s.cc_state, "RTT " + s.srtt_ms + " ms", "cwnd " + (s.cwnd / 1024).toFixed(0) + " KB",
                   "in-flight " + (s.in_flight / 1024).toFixed(0) + " KB", "lost " + s.lost_pkts + "/" + s.sent_pkts])
    c.appendChild(el("span", "", t));
}

/* ---------------------------------------------------------------- peers */
function renderPeers() {
  const ul = $("peers");
  ul.replaceChildren();
  const all = el("li", state.target === "*" ? "sel" : "");
  all.append(el("span", "", "👥 Mọi người"), el("span", "addr", "broadcast"));
  all.onclick = () => selectTarget("*");
  ul.appendChild(all);
  const others = state.peers.filter((p) => p.user !== state.user);
  for (const p of others) {
    const li = el("li", state.target === p.user ? "sel" : "");
    li.append(el("span", "", "● " + p.user), el("span", "addr", p.ip + ":" + p.port));
    li.onclick = () => selectTarget(p.user);
    ul.appendChild(li);
  }
  $("peerCount").textContent = "(" + state.peers.length + ")";
  $("peerEmpty").classList.toggle("hidden", others.length > 0);
  if (state.target !== "*" && !others.some((p) => p.user === state.target)) selectTarget("*");
}
function selectTarget(t) {
  state.target = t;
  $("chatTitle").textContent = t === "*" ? "Chat chung (broadcast)" : "Tin nhắn riêng với " + t;
  $("attach").disabled = !state.online || t === "*";
  $("attach").title = t === "*" ? "Chọn một người để gửi file" : "Gửi file";
  renderPeers();
}

/* ---------------------------------------------------------------- chat */
function addMessage(m, hist) {
  const box = el("div", "msg" + (m.mine ? " mine" : ""));
  const who = m.mine ? "Bạn" : m.from;
  const scope = m.to === "*" ? "" : m.mine ? " → " + m.to : " (riêng)";
  box.appendChild(el("div", "meta", who + scope + " · " + fmtTime(m.ts)));
  box.appendChild(el("div", "", m.text));
  if (m.mine && !hist) { const t = el("div", "tick", "…"); box.appendChild(t); state.pending.set(m.id, { box, tick: t }); }
  appendLog(box);
}
function sysLine(text) { appendLog(el("div", "sys", text)); }
function appendLog(node) {
  const log = $("log");
  const atBottom = log.scrollHeight - log.scrollTop - log.clientHeight < 80;
  log.appendChild(node);
  if (atBottom) log.scrollTo({ top: log.scrollHeight, behavior: "smooth" });
}
$("composer").onsubmit = async (e) => {
  e.preventDefault();
  const text = $("text").value.trim();
  if (!text) return;
  $("text").value = "";
  try { await api("/api/send", { to: state.target, text }); } catch (err) { toast(err.message, "error"); }
};

/* ---------------------------------------------------------------- transfers */
function transferRow(id, name, size, label) {
  let t = state.transfers.get(id);
  if (!t) {
    const li = el("li");
    const title = el("div", "", name), sub = el("div", "muted small", label), bar = el("div", "bar"), fill = el("div");
    bar.appendChild(fill);
    li.append(title, sub, bar);
    $("tlist").prepend(li);
    $("tempty").classList.add("hidden");
    t = { li, sub, bar, fill, size, name, phase: "xhr" };
    state.transfers.set(id, t);
  }
  return t;
}
function progress(id, done, size) {
  const t = state.transfers.get(id);
  if (!t) return;
  t.fill.style.width = (size ? Math.min(100, (done / size) * 100) : 100) + "%";
  t.sub.textContent = t.label + " · " + fmtSize(done) + " / " + fmtSize(size);
}
function sendFile(file) {
  if (!state.online) return toast("Chưa kết nối tới server", "error");
  if (state.target === "*") return toast("Chọn một người nhận để gửi file", "error");
  if (!file.size) return toast(file.name + ": file rỗng", "error");
  if (file.size > MAX_UPLOAD) return toast(file.name + ": file quá lớn (tối đa 2 GB)", "error");
  const id = Math.random().toString(16).slice(2, 14);
  const row = transferRow(id, file.name, file.size, "Đang đẩy lên gateway");
  row.label = "Đang đẩy lên gateway";
  row.phase = "xhr";
  progress(id, 0, file.size);
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/upload");
  for (const [k, v] of Object.entries({ ...H, "X-To": encodeURIComponent(state.target), "X-Filename": encodeURIComponent(file.name), "X-File-Id": id }))
    xhr.setRequestHeader(k, v);
  xhr.upload.onprogress = (ev) => {
    const cur = state.transfers.get(id);
    if (!ev.lengthComputable || !cur || cur.phase !== "xhr") return;
    progress(id, ev.loaded, ev.total);
  };
  xhr.onerror = () => toast("Gửi file thất bại — mất kết nối tới gateway", "error");
  xhr.onload = () => {
    if (xhr.status === 200) return;
    let msg = xhr.status === 413 ? "file quá lớn" : "Gửi file thất bại";
    try { msg = JSON.parse(xhr.responseText).error || msg; } catch (_) { /* ignore */ }
    toast(file.name + ": " + msg, "error");
    const cur = state.transfers.get(id);
    if (cur && cur.phase === "xhr") cur.sub.textContent = "✗ " + msg;
  };
  xhr.send(file);
}
$("attach").onclick = () => $("file").click();
$("file").onchange = (e) => { for (const f of e.target.files) sendFile(f); e.target.value = ""; };
let dragDepth = 0;
addEventListener("dragenter", (e) => { e.preventDefault(); dragDepth++; $("dropHint").classList.remove("hidden"); });
addEventListener("dragleave", () => { if (--dragDepth <= 0) { dragDepth = 0; $("dropHint").classList.add("hidden"); } });
addEventListener("dragover", (e) => e.preventDefault());
addEventListener("drop", (e) => { e.preventDefault(); dragDepth = 0; $("dropHint").classList.add("hidden"); for (const f of e.dataTransfer.files) sendFile(f); });

/* ---------------------------------------------------------------- live events (SSE) */
function connectEvents() {
  const es = new EventSource("/api/events");
  const on = (name, fn) => es.addEventListener(name, (e) => fn(JSON.parse(e.data)));
  on("status", (d) => { setStatus(d.status, d.reason); if (d.user) onLogin(d.user); });
  on("peers", (d) => { state.peers = d.peers; renderPeers(); });
  on("msg", addMessage);
  on("sent", (d) => { const p = state.pending.get(d.ref); if (p) { p.tick.textContent = "✓ đã gửi"; state.pending.delete(d.ref); } });
  on("error", (d) => {
    const p = state.pending.get(d.ref);
    if (p) { p.box.classList.add("failed"); p.tick.textContent = "✗ " + d.text; state.pending.delete(d.ref); }
    else toast(d.text, "error");
    const t = state.transfers.get(d.ref);
    if (t) { t.sub.textContent = "✗ " + d.text; }
  });
  on("notice", (d) => toast(d.text, d.level === "error" ? "error" : ""));
  on("stats", (d) => showStats(d.stats));
  on("file_start", (d) => {
    const label = d.dir === "up" ? "Đang gửi tới " + d.to : "Đang nhận từ " + d.frm;
    const t = transferRow(d.id, d.name, d.size, label);
    t.label = label;
    t.phase = "net";
    progress(d.id, 0, d.size);
  });
  on("file_progress", (d) => progress(d.id, d.done, d.size));
  on("file_sent", (d) => { const t = state.transfers.get(d.id); if (t) { t.bar.classList.add("done"); t.sub.textContent = "✓ Đã gửi " + fmtSize(d.size) + " tới " + d.to; } sysLine("Đã gửi file " + d.name + " tới " + d.to); });
  on("file_received", (d) => {
    const t = state.transfers.get(d.id);
    if (t) {
      t.bar.classList.add("done");
      t.sub.textContent = "✓ Đã nhận " + fmtSize(d.size) + " — ";
      const a = el("a", "", "Tải về");
      a.href = "/api/download/" + encodeURIComponent(d.name);
      a.download = d.name;
      t.sub.appendChild(a);
    }
    sysLine(d.from + " đã gửi file " + d.name);
  });
  es.onopen = () => { if (state.user && state.online === false) setStatus("online"); };
  es.onerror = () => {
    if (state.user && es.readyState === EventSource.CONNECTING) setStatus("reconnecting", "giao diện");
  };
}

/* ---------------------------------------------------------------- login */
function onLogin(user) {
  state.user = user;
  $("me").textContent = "— " + user;
  $("login").classList.add("hidden");
  selectTarget(state.target);
}
$("loginForm").onsubmit = async (e) => {
  e.preventDefault();
  $("loginErr").textContent = "";
  $("loginBtn").disabled = true;
  try {
    const d = await api("/api/login", { server: $("server").value.trim(), user: $("user").value.trim(), pass: $("pass").value });
    onLogin(d.user);
    $("pass").value = "";
    const s = await api("/api/state");
    state.peers = s.peers;
    renderPeers();
  } catch (err) { $("loginErr").textContent = err.message; }
  $("loginBtn").disabled = false;
};
$("logoutBtn").onclick = async () => { await api("/api/logout", {}); $("log").replaceChildren(); $("tlist").replaceChildren(); state.transfers.clear(); $("tempty").classList.remove("hidden"); };
$("discoverBtn").onclick = async () => {
  $("found").textContent = "Đang tìm…";
  const { servers } = await api("/api/discover");
  const box = $("found");
  box.replaceChildren();
  if (!servers.length) box.textContent = "Không thấy server nào trong LAN.";
  for (const s of servers) {
    const a = el("a", "", s.host + ":" + s.port);
    a.onclick = () => { $("server").value = s.host + ":" + s.port; };
    box.appendChild(a);
  }
};

/* ---------------------------------------------------------------- boot */
(async function boot() {
  const s = await api("/api/state");
  $("server").value = s.default_server;
  state.peers = s.peers;
  connectEvents();
  setStatus(s.status);
  if (s.status === "online") {
    onLogin(s.user);
    for (const m of s.history) addMessage(m, true);
    renderPeers();
    showStats(s.stats);
  }
})();
