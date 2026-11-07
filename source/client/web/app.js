"use strict";
/* CollabNet UI — JavaScript thuần phía client. Nói chuyện với gateway cục bộ qua fetch/XHR và nhận cập nhật
   realtime qua Server-Sent Events. Mọi nội dung do người dùng nhập đều đi qua textContent (không dùng innerHTML). */
const $ = (id) => document.getElementById(id);
const H = { "X-Requested-With": "collabnet" };
const MAX_TEXT = 8000, HARD_MAX_UPLOAD = 2 * 1024 ** 3, SPARK_N = 60;
const S = {
  user: null, peers: [], status: "offline", online: false,
  active: "*", pane: "list", panel: false,
  convs: new Map(),            // key ("*" hoặc tên người) -> { key, items[], byId }
  unread: new Map(),           // key -> số tin chưa đọc
  drafts: new Map(), nodes: new Map(),
  files: new Map(), blobs: new Map(),   // File gốc (để gửi lại) và URL xem trước ảnh của file mình gửi
  maxFile: HARD_MAX_UPLOAD, filter: "", rtt: [], cwnd: [], nearBottom: true, pending: 0,
};

/* ───────────────────────── tiện ích DOM ───────────────────────── */
const NS = "http://www.w3.org/2000/svg";
function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
function icon(name, cls) {
  const s = document.createElementNS(NS, "svg"); s.setAttribute("class", "ic" + (cls ? " " + cls : ""));
  const u = document.createElementNS(NS, "use"); u.setAttribute("href", "#i-" + name); s.appendChild(u); return s;
}
function toast(text, kind) {
  const t = el("div", "toast " + (kind || ""), text); $("toasts").appendChild(t); setTimeout(() => t.remove(), 5200);
}
const nf = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 1 });
const fmtSize = (n) => n < 1024 ? n + " B" : n < 1048576 ? nf.format(n / 1024) + " KB" : n < 1073741824 ? nf.format(n / 1048576) + " MB" : nf.format(n / 1073741824) + " GB";
const fmtTime = (ts) => new Date(ts * 1000).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
const dayKey = (ts) => new Date(ts * 1000).toDateString();
function dayLabel(ts) {
  const d = new Date(ts * 1000), t = new Date(), y = new Date(Date.now() - 864e5);
  if (d.toDateString() === t.toDateString()) return "Hôm nay";
  if (d.toDateString() === y.toDateString()) return "Hôm qua";
  return d.toLocaleDateString("vi-VN", { weekday: "long", day: "numeric", month: "numeric" });
}
function hue(name) { let h = 0; for (const c of String(name)) h = (h * 31 + c.codePointAt(0)) % 360; return h; }
function avatar(key, cls, presence) {
  const a = el("div", "av" + (cls ? " " + cls : ""));
  if (key === "*") { a.classList.add("grp"); a.appendChild(icon("users")); }
  else { a.style.setProperty("--h", hue(key)); a.textContent = (Array.from(key)[0] || "?").toUpperCase(); }
  if (presence !== undefined) a.appendChild(el("i", "pres" + (presence ? "" : " off")));
  return a;
}
/* Chuyển thông báo lỗi tiếng Anh của server sang tiếng Việt dễ hiểu. */
function vi(t) {
  t = String(t || "");
  let m;
  if ((m = t.match(/New server pinned: (.*)/))) return "Đã ghi nhớ khoá của server (" + m[1].slice(0, 17) + "…).";
  if (/Reconnected to server/i.test(t)) return "Đã kết nối lại với server.";
  if (/Re-login failed/i.test(t)) return "Đăng nhập lại thất bại: " + vi(t.replace(/^Re-login failed:\s*/i, ""));
  if (/SERVER KEY CHANGED/i.test(t)) return "Khoá của server đã thay đổi (có thể bị tấn công man-in-the-middle). Đã từ chối kết nối.";
  if (/wrong password/i.test(t)) return "Sai mật khẩu.";
  if (/password too short/i.test(t)) return "Mật khẩu cần ít nhất 4 ký tự.";
  if (/invalid username/i.test(t)) return "Tên người dùng gồm 2–24 ký tự: chữ, số, _ . -";
  if (/is not online/i.test(t)) return "Người nhận đang offline.";
  if (/too large|invalid or too large/i.test(t)) return "File vượt quá giới hạn của server.";
  if (/corrupted or incomplete/i.test(t)) return "File bị lỗi hoặc truyền chưa đủ.";
  if (/logged in from another/i.test(t)) return "Tài khoản này vừa đăng nhập ở nơi khác.";
  if (/rejected by server/i.test(t)) return "Server từ chối file này.";
  if (/upload interrupted/i.test(t)) return "Đã dừng gửi.";
  return t;
}
async function api(path, body) {
  const r = await fetch(path, body === undefined ? {} : { method: "POST", headers: { ...H, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || r.statusText);
  return d;
}

/* ───────────────────────── dữ liệu hội thoại ───────────────────────── */
function conv(key) {
  let c = S.convs.get(key);
  if (!c) { c = { key, items: [], byId: new Map() }; S.convs.set(key, c); }
  return c;
}
const convKey = (it) => it.type === "msg" ? (it.to === "*" ? "*" : it.mine ? it.to : it.from) : (it.mine ? it.to : it.from);
/* Xếp theo ts của server: mỗi tin đi một stream riêng nên có thể đến không đúng thứ tự (đó là cái giá của việc không bị HoL). */
function addItem(it) {
  const c = conv(convKey(it));
  const old = c.byId.get(it.id);
  if (old) { Object.assign(old, it); return { c, it: old, isNew: false }; }
  c.byId.set(it.id, it);
  let i = c.items.length;
  while (i > 0 && c.items[i - 1].ts > it.ts) i--;
  c.items.splice(i, 0, it);
  return { c, it, isNew: true, last: i === c.items.length - 1 };
}
function findItem(id) {
  for (const c of S.convs.values()) { const it = c.byId.get(id); if (it) return { c, it }; }
  return null;
}
function removeItem(id) {
  const f = findItem(id); if (!f) return;
  f.c.byId.delete(id); f.c.items.splice(f.c.items.indexOf(f.it), 1);
  const n = S.nodes.get(id); if (n) { n.row.remove(); S.nodes.delete(id); }
}
function hydrate(snap) {
  for (const m of snap.history || []) addItem({ type: "msg", ...m });
  for (const f of snap.files || []) { const old = findItem(f.id); if (!old || old.it.phase !== "upload") addItem({ type: "file", phase: "net", ...f }); }
  renderAll(true);
}
function notifyIncoming(key, it) {
  if (it.mine) return;
  if (key !== S.active || document.hidden) {
    S.unread.set(key, (S.unread.get(key) || 0) + 1);
    updateTitle();
  }
}
function updateTitle() {
  let n = 0; for (const v of S.unread.values()) n += v;
  document.title = (n ? "(" + n + ") " : "") + "CollabNet";
}

/* ───────────────────────── vẽ danh sách hội thoại ───────────────────────── */
const dirty = new Set(); let raf = 0;
function schedule(k) { dirty.add(k); if (!raf) raf = requestAnimationFrame(() => { raf = 0; const d = [...dirty]; dirty.clear(); for (const x of d) ({ rail: renderRail, head: renderHead, panel: renderFiles }[x])(); }); }
const others = () => S.peers.filter((p) => p.user !== S.user);
const peerOf = (k) => S.peers.find((p) => p.user === k);
function preview(c) {
  const it = c.items[c.items.length - 1];
  if (!it) return c.key === "*" ? "Chưa có tin nhắn" : "Bắt đầu trò chuyện";
  const who = it.mine ? "Bạn: " : c.key === "*" ? it.from + ": " : "";
  return who + (it.type === "file" ? "Tệp " + it.name : it.text.replace(/\s+/g, " "));
}
function renderRail() {
  const box = $("convs"), q = S.filter.trim().toLowerCase();
  const keys = new Set(others().map((p) => p.user));
  for (const k of S.convs.keys()) if (k !== "*" && S.convs.get(k).items.length) keys.add(k);
  const act = (k) => { const it = (S.convs.get(k) || { items: [] }).items.slice(-1)[0]; return it ? it.ts : 0; };
  const list = [...keys].filter((k) => !q || k.toLowerCase().includes(q)).sort((a, b) => act(b) - act(a) || a.localeCompare(b));
  box.replaceChildren();
  const row = (k) => {
    const c = conv(k), online = k === "*" || !!peerOf(k), un = S.unread.get(k) || 0;
    const b = el("button", "conv" + (un ? " unread" : "") + (online ? "" : " gone"));
    b.dataset.key = k; b.setAttribute("aria-current", String(k === S.active));
    const body = el("div"), top = el("div", "c-top"), bot = el("div", "c-bot");
    const last = c.items[c.items.length - 1];
    top.append(el("span", "c-name", k === "*" ? "Cả nhóm" : k), el("span", "c-time", last ? fmtTime(last.ts) : ""));
    bot.appendChild(el("span", "c-prev", online ? preview(c) : "Offline · " + preview(c)));
    if (un) bot.appendChild(el("span", "badge", un > 99 ? "99+" : String(un)));
    body.append(top, bot);
    b.append(avatar(k, "", k === "*" ? undefined : online), body);
    b.onclick = () => openConv(k);
    return b;
  };
  if (!q || "cả nhóm".includes(q)) box.appendChild(row("*"));
  if (list.length) box.appendChild(el("div", "sect", "Tin nhắn riêng"));
  for (const k of list) box.appendChild(row(k));
  if (!list.length && !q) box.appendChild(el("p", "empty-note", "Chưa có ai khác online. Khi có người đăng nhập, họ sẽ hiện ở đây.")).style.padding = "10px 12px";
}
function renderHead() {
  const k = S.active, p = peerOf(k);
  $("chatTitle").textContent = k === "*" ? "Cả nhóm" : k;
  $("chatSub").textContent = k === "*" ? (others().length ? others().length + 1 + " người đang online" : "Chỉ có bạn đang online")
    : p ? "Đang online · " + p.ip + ":" + p.port : "Đang offline";
  $("headAv").replaceChildren(avatar(k, "", k === "*" ? undefined : !!p));
  updateComposer();
}
function updateComposer() {
  const k = S.active, gone = k !== "*" && !peerOf(k), ok = S.online && !gone;
  const t = $("text");
  t.disabled = !ok; $("sendBtn").disabled = !ok || !t.value.trim(); $("attach").disabled = !S.online;
  t.placeholder = !S.online ? "Đang chờ kết nối…" : gone ? k + " đang offline" : k === "*" ? "Nhắn cho cả nhóm" : "Nhắn cho " + k;
  const n = $("cnotice");
  if (gone) { n.textContent = k + " đang offline nên chưa thể nhận tin. Tin cũ vẫn được giữ lại ở đây."; n.classList.remove("hidden"); }
  else n.classList.add("hidden");
}
function openConv(k, keepPane) {
  S.drafts.set(S.active, $("text").value);
  S.active = k; S.unread.delete(k); updateTitle();
  if (!keepPane) { S.pane = "chat"; $("app").dataset.pane = "chat"; }
  $("text").value = S.drafts.get(k) || ""; autosize();
  renderRail(); renderHead(); renderLog(true); renderFiles();
  if (!matchMedia("(max-width:760px)").matches) $("text").focus();
}

/* ───────────────────────── vẽ khung tin nhắn ───────────────────────── */
const URL_RE = /(https?:\/\/[^\s<>"']+)/g;
function linkify(text) {
  const frag = document.createDocumentFragment();
  text.split(URL_RE).forEach((part, i) => {
    if (i % 2 === 0) { if (part) frag.appendChild(document.createTextNode(part)); return; }
    const m = part.match(/^(.*?)([.,;:!?)\]]*)$/), a = el("a", "", m[1]);
    a.href = m[1]; a.target = "_blank"; a.rel = "noopener noreferrer";
    frag.append(a, document.createTextNode(m[2]));
  });
  return frag;
}
const isImg = (n) => /\.(png|jpe?g|gif|webp)$/i.test(n || "");
const ext = (n) => ((n || "").split(".").pop() || "").slice(0, 4).toUpperCase() || "FILE";
function stateText(it) {
  if (it.status === "pending") return "Đang gửi…";
  if (it.status === "failed") return vi(it.error) || "Chưa gửi được";
  if (it.to === "*") return it.n === 0 ? "Chưa có ai online để nhận" : "Đã gửi tới " + it.n + " người";
  return "Đã gửi";
}
function fillMeta(it, meta) {
  meta.replaceChildren(el("span", "", fmtTime(it.ts)));
  if (!it.mine || it.type === "file") return;       // trạng thái file nằm ngay trong thẻ file
  const s = el("span", ""); s.style.display = "inline-flex"; s.style.alignItems = "center"; s.style.gap = "4px";
  if (it.status === "failed") s.appendChild(icon("alert"));
  else if (it.status === "sent") s.appendChild(icon("check"));
  s.appendChild(document.createTextNode(stateText(it)));
  meta.appendChild(s);
  if (it.status === "failed" && it.type === "msg") {
    const b = el("button"); b.append(icon("retry"), document.createTextNode("Gửi lại")); b.onclick = () => retryMsg(it); meta.appendChild(b);
  }
}
function buildRow(it, grouped) {
  const row = el("div", "row" + (it.mine ? " mine" : "") + (grouped ? " grouped" : ""));
  const group = S.active === "*" && !it.mine;
  if (group) row.appendChild(grouped ? el("div", "gap") : avatar(it.from, "sm"));
  const b = el("div", "bubble");
  if (group && !grouped) { const w = el("div", "who", it.from); w.style.setProperty("--h", hue(it.from)); b.appendChild(w); }
  const meta = el("div", "meta"), ref = { row, bubble: b, meta };
  if (it.type === "msg") { const t = el("div", "text"); t.appendChild(linkify(it.text)); b.appendChild(t); }
  else buildFile(it, b, ref);
  b.appendChild(meta); row.appendChild(b);
  S.nodes.set(it.id, ref);
  patch(it);
  return row;
}
function buildFile(it, b, ref) {
  const url = it.mine ? S.blobs.get(it.id) : null;
  ref.thumbHost = el("div"); b.appendChild(ref.thumbHost);
  const card = el("div", "fcard"), info = el("div"), act = el("div", "fact");
  ref.name = el("div", "fname", it.name); ref.sub = el("div", "fsub"); ref.bar = el("div", "pbar"); ref.fill = el("i"); ref.bar.appendChild(ref.fill);
  ref.act = act; info.append(ref.name, ref.sub, ref.bar);
  card.append(el("div", "ficon", ext(it.name)), info, act); b.appendChild(card);
  if (url) setThumb(ref, url, url);
}
function setThumb(ref, src, href) {
  if (ref.thumb) { ref.thumb.src = src; return; }
  const a = el("a"); a.href = href; a.target = "_blank"; a.rel = "noopener";
  const img = el("img", "thumb"); img.src = src; img.alt = ""; img.loading = "lazy"; a.appendChild(img);
  ref.thumb = img; ref.thumbHost.appendChild(a);
}
/* Cập nhật một mục đã vẽ (không dựng lại cả khung → không làm giật khi tiến trình file chạy). */
function patch(it) {
  const ref = S.nodes.get(it.id); if (!ref) return;
  ref.bubble.classList.toggle("failed", it.status === "failed");
  ref.bubble.classList.toggle("done", it.status === "done");
  fillMeta(it, ref.meta);
  if (it.type === "msg") return;
  const pct = it.size ? Math.min(100, (it.done / it.size) * 100) : 100;
  ref.fill.style.width = pct + "%"; ref.name.textContent = it.name;
  let sub;
  if (it.status === "failed") sub = vi(it.error) || "Không gửi được";
  else if (it.status === "done") sub = (it.mine ? "Đã gửi " : "Đã nhận ") + fmtSize(it.size);
  else if (it.phase === "upload" && it.mine) sub = "Đang chuẩn bị… " + Math.round(pct) + "%";
  else {
    const sp = it._t && it._t.speed; let eta = "";
    if (sp > 1024) { const s = Math.ceil((it.size - it.done) / sp); eta = " · còn " + (s >= 60 ? Math.ceil(s / 60) + " phút" : s + " giây"); }
    sub = (it.mine ? "Đang gửi " : "Đang nhận ") + Math.round(pct) + "% · " + fmtSize(it.done) + " / " + fmtSize(it.size) + (sp > 1024 ? " · " + fmtSize(sp) + "/s" + eta : "");
  }
  ref.sub.textContent = sub;
  ref.act.replaceChildren();
  if (it.status === "active" && it.mine && it.xhr) {
    const x = el("button"); x.title = "Huỷ gửi"; x.setAttribute("aria-label", "Huỷ gửi"); x.appendChild(icon("x")); x.onclick = () => cancelUpload(it); ref.act.appendChild(x);
  }
  if (it.status === "failed" && it.mine && S.files.has(it.id)) {
    const r = el("button"); r.title = "Gửi lại"; r.setAttribute("aria-label", "Gửi lại"); r.appendChild(icon("retry")); r.onclick = () => retryFile(it); ref.act.appendChild(r);
  }
  if (it.status === "done" && !it.mine) {
    const a = el("a"); a.href = "/api/download/" + encodeURIComponent(it.name); a.download = it.name; a.title = "Tải về"; a.setAttribute("aria-label", "Tải " + it.name); a.appendChild(icon("download")); ref.act.appendChild(a);
    if (isImg(it.name)) setThumb(ref, "/api/download/" + encodeURIComponent(it.name) + "?inline=1", "/api/download/" + encodeURIComponent(it.name) + "?inline=1");
  }
}
function emptyState() {
  const d = el("div", "empty"), k = S.active;
  d.append(el("strong", "", k === "*" ? "Chưa có tin nhắn nào" : "Trò chuyện riêng với " + k),
    document.createTextNode(k === "*" ? "Gửi lời chào để bắt đầu. Mọi người đang online đều nhận được." : "Tin nhắn ở đây chỉ gửi tới " + k + ". Bạn cũng có thể gửi file cho họ."));
  return d;
}
function renderLog(stick) {
  const log = $("log"), c = conv(S.active), keep = S.nearBottom;
  log.replaceChildren(); S.nodes.clear();
  if (!c.items.length) { log.appendChild(emptyState()); return; }
  let prev = null;
  for (const it of c.items) { appendRow(log, it, prev); prev = it; }
  if (stick || keep) scrollBottom(false);
}
function appendRow(log, it, prev) {
  const sameDay = prev && dayKey(prev.ts) === dayKey(it.ts);
  if (!sameDay) log.appendChild(el("div", "day", dayLabel(it.ts)));
  log.appendChild(buildRow(it, !!(sameDay && prev.from === it.from && it.ts - prev.ts < 180)));
}
function nearBottom() { const l = $("log"); return l.scrollHeight - l.scrollTop - l.clientHeight < 90; }
function scrollBottom(smooth) { const l = $("log"); l.style.scrollBehavior = smooth ? "smooth" : "auto"; l.scrollTop = l.scrollHeight; S.nearBottom = true; S.pending = 0; $("jump").classList.add("hidden"); }
$("log").addEventListener("scroll", () => { S.nearBottom = nearBottom(); if (S.nearBottom) { S.pending = 0; $("jump").classList.add("hidden"); } });
$("jump").onclick = () => scrollBottom(true);
/* Thêm một mục mới vào khung đang mở; nếu nó không nằm cuối (đến muộn hơn tin khác) thì vẽ lại cho đúng thứ tự. */
function showNew(res) {
  const { c, it } = res;
  if (c.key !== S.active) return;
  const log = $("log");
  if (!res.last) return renderLog(false);
  if (log.querySelector(".empty")) log.replaceChildren();
  const idx = c.items.indexOf(it), keep = S.nearBottom || it.mine;
  appendRow(log, it, idx > 0 ? c.items[idx - 1] : null);
  if (keep) scrollBottom(true);
  else { S.pending++; $("jumpText").textContent = S.pending + " tin mới"; $("jump").classList.remove("hidden"); }
}

/* ───────────────────────── bảng phải: đường truyền + tệp ───────────────────────── */
function spark(svg, data, fmt) {
  svg.replaceChildren(); if (data.length < 2) return;
  const max = Math.max(...data, 1) * 1.2, dx = 120 / (SPARK_N - 1), x0 = 120 - (data.length - 1) * dx;
  const pts = data.map((v, i) => (x0 + i * dx).toFixed(1) + "," + (38 - (v / max) * 34).toFixed(1));
  const area = document.createElementNS(NS, "path"), line = document.createElementNS(NS, "polyline");
  area.setAttribute("class", "area"); area.setAttribute("d", "M" + x0.toFixed(1) + ",40 L" + pts.join(" L") + " L120,40 Z");
  line.setAttribute("class", "line"); line.setAttribute("points", pts.join(" "));
  svg.append(area, line);
}
function showStats(s) {
  if (!s) return;
  S.stats = s;
  S.rtt.push(s.srtt_ms); S.cwnd.push(s.cwnd / 1024);
  if (S.rtt.length > SPARK_N) { S.rtt.shift(); S.cwnd.shift(); }
  $("rttNow").textContent = nf.format(s.srtt_ms) + " ms"; $("cwndNow").textContent = nf.format(s.cwnd / 1024) + " KB";
  $("stFlight").textContent = nf.format(s.in_flight / 1024) + " KB";
  $("stLost").textContent = s.lost_pkts + " / " + s.sent_pkts + (s.sent_pkts ? " (" + nf.format(s.lost_pkts / s.sent_pkts * 100) + "%)" : "");
  $("stCc").textContent = s.cc.toUpperCase() + " · " + s.cc_state;
  $("chipText").textContent = nf.format(Math.round(s.srtt_ms)) + " ms · " + s.cc.toUpperCase();
  if (S.panel) { spark($("rttSvg"), S.rtt); spark($("cwndSvg"), S.cwnd); }
}
function renderFiles() {
  const ul = $("tlist"); ul.replaceChildren();
  const group = S.active === "*";
  const pool = group ? [...S.convs.values()].flatMap((c) => c.items) : conv(S.active).items;   // chat chung: gom tệp của mọi cuộc trò chuyện
  const files = pool.filter((i) => i.type === "file").sort((a, b) => b.ts - a.ts);
  $("filesTitle").textContent = group ? "Tất cả tệp đã chia sẻ" : "Tệp trong cuộc trò chuyện";
  $("tempty").classList.toggle("hidden", files.length > 0);
  $("tempty").textContent = "Chưa có tệp nào. Kéo thả file vào khung chat để gửi.";
  for (const f of files) {
    const peer = f.mine ? f.to : f.from;
    const li = el("li"), mid = el("div");
    mid.append(el("div", "t-name", f.name), el("div", "t-sub", (f.mine ? "Bạn gửi " + peer : f.from + " gửi bạn") + " · " + fmtSize(f.size) + (f.status === "failed" ? " · lỗi" : f.status === "active" ? " · đang truyền" : "")));
    li.append(el("div", "ficon", ext(f.name)), mid);
    if (f.status === "done" && !f.mine) { const a = el("a"); a.href = "/api/download/" + encodeURIComponent(f.name); a.download = f.name; a.title = "Tải về"; a.appendChild(icon("download")); li.appendChild(a); }
    ul.appendChild(li);
  }
}
function setPanel(open) {
  S.panel = open; $("app").classList.toggle("panel-open", open); $("panelBtn").setAttribute("aria-expanded", String(open));
  if (open && S.stats) { spark($("rttSvg"), S.rtt); spark($("cwndSvg"), S.cwnd); }
}
$("panelBtn").onclick = () => setPanel(!S.panel);
$("linkChip").onclick = () => setPanel(!S.panel);

/* ───────────────────────── trạng thái kết nối ───────────────────────── */
const STATUS_VI = { online: "Đã kết nối", connecting: "Đang kết nối…", reconnecting: "Đang kết nối lại…", offline: "Chưa kết nối" };
function setStatus(s, reason) {
  S.status = s; S.online = s === "online";
  $("statusDot").className = "dot " + (S.online ? "on" : s === "offline" ? "off" : "mid");
  $("statusText").textContent = STATUS_VI[s] || s;
  $("chipDot").className = "dot " + (S.online ? "on" : s === "offline" ? "off" : "mid");
  if (!S.online) $("chipText").textContent = STATUS_VI[s] || s;
  $("linkLine").textContent = S.online ? "Kết nối ổn định, đang mã hoá AES-256-GCM." : STATUS_VI[s] || s;
  const b = $("banner");
  if (s === "reconnecting" || s === "connecting") { b.textContent = "Mất kết nối" + (reason ? " (" + vi(reason) + ")" : "") + ". Đang thử kết nối lại, tin nhắn chưa gửi sẽ không được giữ."; b.classList.remove("hidden"); }
  else b.classList.add("hidden");
  if (s === "offline") {
    S.user = null; showLogin();
    if (reason) $("loginErr").textContent = vi(reason);
  }
  updateComposer();
}
function showApp() { $("login").classList.add("hidden"); $("app").classList.remove("hidden"); }
function showLogin() { $("app").classList.add("hidden"); $("login").classList.remove("hidden"); }
function onLogin(user) {
  if (S.user && S.user !== user) { S.convs.clear(); S.unread.clear(); S.drafts.clear(); }
  S.user = user; showApp();
  $("meName").textContent = user; $("meAv").replaceChildren(avatar(user));
}

/* ───────────────────────── gửi tin nhắn ───────────────────────── */
function autosize() {
  const t = $("text"); t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight, 160) + "px";
  const n = t.value.length, c = $("counter");
  c.classList.toggle("hidden", n < MAX_TEXT * 0.8); c.textContent = n + "/" + MAX_TEXT; c.classList.toggle("warn", n >= MAX_TEXT * 0.95);
  $("sendBtn").disabled = t.disabled || !t.value.trim();
}
async function sendText() {
  const t = $("text"), text = t.value.trim();
  if (!text || t.disabled) return;
  if (text.length > MAX_TEXT) return toast("Tin nhắn dài tối đa " + MAX_TEXT + " ký tự.", "error");
  t.value = ""; autosize();
  try { await api("/api/send", { to: S.active, text }); }
  catch (err) { t.value = text; autosize(); toast(vi(err.message), "error"); }
}
async function retryMsg(it) {
  removeItem(it.id);
  try { await api("/api/send", { to: it.to, text: it.text }); } catch (err) { toast(vi(err.message), "error"); }
}
$("composer").onsubmit = (e) => { e.preventDefault(); sendText(); };
$("text").addEventListener("input", autosize);
$("text").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); sendText(); }
});
$("text").addEventListener("paste", (e) => {
  const fs = [...(e.clipboardData ? e.clipboardData.files : [])];
  if (fs.length) { e.preventDefault(); handleFiles(fs); }
});
/* Emoji */
const EMOJI = "😀 😂 🥹 😍 😎 🤔 😅 😭 👍 👎 🙏 👏 🎉 🔥 ❤️ 💯 ✅ ❌ ⚠️ 📎 📌 💡 🚀 ☕".split(" ");
for (const e of EMOJI) { const b = el("button", "", e); b.type = "button"; b.setAttribute("aria-label", e); b.onclick = () => { const t = $("text"), s = t.selectionStart; t.setRangeText(e, s, t.selectionEnd, "end"); autosize(); t.focus(); }; $("emoji").appendChild(b); }
$("emojiBtn").onclick = (e) => { e.stopPropagation(); $("emoji").classList.toggle("hidden"); };
addEventListener("click", (e) => { if (!$("emoji").contains(e.target)) $("emoji").classList.add("hidden"); });
addEventListener("keydown", (e) => { if (e.key === "Escape") $("emoji").classList.add("hidden"); });

/* ───────────────────────── gửi file ───────────────────────── */
function handleFiles(files) {
  files = [...files]; if (!files.length) return;
  if (!S.online) return toast("Chưa kết nối tới server.", "error");
  const ppl = others();
  if (S.active !== "*") {
    if (!peerOf(S.active)) return toast(S.active + " đang offline nên chưa nhận được file.", "error");
    return files.forEach((f) => uploadFile(f, S.active));
  }
  if (!ppl.length) return toast("Chưa có ai khác online để nhận file.", "error");
  if (ppl.length === 1) return files.forEach((f) => uploadFile(f, ppl[0].user));
  const dlg = $("picker"), list = $("pickerList"); list.replaceChildren();
  $("pickerSub").textContent = files.length === 1 ? files[0].name : files.length + " file đã chọn. File chỉ gửi tới một người mỗi lần.";
  for (const p of ppl) {
    const b = el("button"); b.type = "button"; b.append(avatar(p.user, "sm"), document.createTextNode(p.user));
    b.onclick = () => { dlg.close(); files.forEach((f) => uploadFile(f, p.user)); }; list.appendChild(b);
  }
  dlg.showModal();
}
function uploadFile(file, to) {
  if (!file.size) return toast(file.name + ": file rỗng.", "error");
  if (file.size > S.maxFile) return toast(file.name + ": vượt giới hạn " + fmtSize(S.maxFile) + " của server.", "error");
  const id = Math.random().toString(16).slice(2, 14);
  S.files.set(id, file);
  if (isImg(file.name)) S.blobs.set(id, URL.createObjectURL(file));
  const it = { type: "file", id, from: S.user, to, name: file.name, size: file.size, ts: Date.now() / 1000, mine: true, status: "active", done: 0, phase: "upload" };
  if (S.active !== to) openConv(to);
  const res = addItem(it); showNew(res); schedule("rail"); schedule("panel");
  const xhr = new XMLHttpRequest(); it.xhr = xhr;
  xhr.open("POST", "/api/upload");
  for (const [k, v] of Object.entries({ ...H, "X-To": encodeURIComponent(to), "X-Filename": encodeURIComponent(file.name), "X-File-Id": id })) xhr.setRequestHeader(k, v);
  xhr.upload.onprogress = (ev) => { if (ev.lengthComputable && it.phase === "upload" && it.status === "active") { it.done = ev.loaded; patch(it); } };
  const fail = (msg) => { if (it.status === "active") { it.status = "failed"; it.error = msg; it.xhr = null; patch(it); schedule("panel"); } };
  xhr.onerror = () => fail("Mất kết nối tới ứng dụng khách.");
  xhr.onabort = () => fail("Đã huỷ gửi.");
  xhr.onload = () => {
    if (xhr.status === 200) return;
    let msg = xhr.status === 413 ? "File quá lớn." : "Gửi file thất bại.";
    try { msg = JSON.parse(xhr.responseText).error || msg; } catch (_) { /* giữ nguyên */ }
    fail(msg);
  };
  xhr.send(file);
}
function cancelUpload(it) { if (it.xhr) { it.cancelled = true; it.xhr.abort(); } }
function retryFile(it) { const f = S.files.get(it.id); if (!f) return; removeItem(it.id); uploadFile(f, it.to); }
$("attach").onclick = () => $("file").click();
$("file").onchange = (e) => { handleFiles(e.target.files); e.target.value = ""; };
let depth = 0;
const hasFiles = (e) => e.dataTransfer && [...e.dataTransfer.types].includes("Files");
addEventListener("dragenter", (e) => { if (!hasFiles(e) || $("app").classList.contains("hidden")) return; e.preventDefault(); depth++; $("dropSub").textContent = S.active === "*" ? "Bạn sẽ chọn người nhận" : "Gửi tới " + S.active; $("dropHint").classList.remove("hidden"); });
addEventListener("dragleave", () => { if (--depth <= 0) { depth = 0; $("dropHint").classList.add("hidden"); } });
addEventListener("dragover", (e) => { if (hasFiles(e)) e.preventDefault(); });
addEventListener("drop", (e) => { if (!hasFiles(e)) return; e.preventDefault(); depth = 0; $("dropHint").classList.add("hidden"); if (!$("app").classList.contains("hidden")) handleFiles(e.dataTransfer.files); });

/* ───────────────────────── sự kiện realtime (SSE) ───────────────────────── */
function trackSpeed(it) {
  const now = performance.now(), t = it._t;
  if (!t) { it._t = { t: now, done: it.done, speed: 0 }; return; }
  const dt = (now - t.t) / 1000;
  if (dt >= 0.5) { const inst = Math.max(0, (it.done - t.done) / dt); t.speed = t.speed ? t.speed * 0.6 + inst * 0.4 : inst; t.t = now; t.done = it.done; }
}
function connectEvents() {
  const es = new EventSource("/api/events");
  const on = (name, fn) => es.addEventListener(name, (e) => fn(JSON.parse(e.data)));
  on("status", (d) => { if (d.user && S.user !== d.user) onLogin(d.user); setStatus(d.status, d.reason); });
  on("peers", (d) => { S.peers = d.peers; renderHead(); schedule("rail"); if (S.active !== "*" && !peerOf(S.active) && !conv(S.active).items.length) openConv("*"); });
  on("msg", (m) => { const r = addItem({ type: "msg", ...m }); if (r.isNew) { notifyIncoming(convKey(r.it), r.it); showNew(r); } schedule("rail"); });
  on("sent", (d) => {
    const f = findItem(d.ref); if (!f) return;
    Object.assign(f.it, { status: "sent", n: d.n });
    const before = f.c.items.map((i) => i.id).join();
    if (d.ts) f.it.ts = d.ts;                                  // đồng hồ server làm chuẩn sắp xếp chung cho mọi người
    f.c.items.sort((a, b) => a.ts - b.ts);
    if (f.c.key === S.active && f.c.items.map((i) => i.id).join() !== before) renderLog(false); else patch(f.it);
    schedule("rail");
  });
  on("error", (d) => {
    const f = findItem(d.ref);
    if (f) {
      if (f.it.status === "failed" && f.it.error) return;
      const cancelled = f.it.cancelled;
      Object.assign(f.it, { status: "failed", error: cancelled ? "Đã huỷ gửi." : d.text, xhr: null }); patch(f.it); schedule("panel");
    } else toast(vi(d.text), "error");
  });
  on("notice", (d) => toast(vi(d.text), d.level === "error" ? "error" : ""));
  on("stats", (d) => showStats(d.stats));
  on("file_start", (d) => {
    const old = findItem(d.id);
    if (old) { Object.assign(old.it, { phase: "net", size: d.size }); patch(old.it); return; }
    const it = { type: "file", id: d.id, from: d.frm, to: d.to || S.user, name: d.name, size: d.size, ts: Date.now() / 1000, mine: d.dir === "up", status: "active", done: 0, phase: "net" };
    const r = addItem(it); notifyIncoming(convKey(it), it); showNew(r); schedule("rail"); schedule("panel");
  });
  on("file_progress", (d) => { const f = findItem(d.id); if (!f || f.it.status !== "active") return; f.it.done = d.done; f.it.phase = "net"; trackSpeed(f.it); patch(f.it); });
  on("file_sent", (d) => { const f = findItem(d.id); if (!f) return; Object.assign(f.it, { status: "done", done: d.size, xhr: null }); patch(f.it); schedule("panel"); schedule("rail"); });
  on("file_received", (d) => {
    const f = findItem(d.id); if (!f) return;
    Object.assign(f.it, { status: "done", done: d.size, name: d.name }); patch(f.it); schedule("panel"); schedule("rail");
    if (f.c.key !== S.active || document.hidden) toast(d.from + " vừa gửi file " + d.name);
  });
  es.onopen = () => { if (S.user) loadState(); };
  es.onerror = () => { if (S.user && es.readyState === EventSource.CONNECTING) setStatus("reconnecting", "giao diện"); };
}
async function loadState() {
  const s = await api("/api/state");
  S.peers = s.peers; S.maxFile = Math.min(s.max_file || HARD_MAX_UPLOAD, HARD_MAX_UPLOAD);
  if (s.user) onLogin(s.user);
  setStatus(s.status);
  if (s.user) { hydrate(s); showStats(s.stats); }
}

/* ───────────────────────── đăng nhập / đăng xuất ───────────────────────── */
$("loginForm").onsubmit = async (e) => {
  e.preventDefault();
  $("loginErr").textContent = ""; $("loginBtn").disabled = true; $("loginBtn").textContent = "Đang kết nối…";
  try {
    const d = await api("/api/login", { server: $("server").value.trim(), user: $("user").value.trim(), pass: $("pass").value });
    $("pass").value = ""; onLogin(d.user);
    await loadState(); openConv("*", true);
  } catch (err) { $("loginErr").textContent = vi(err.message); }
  $("loginBtn").disabled = false; $("loginBtn").textContent = "Đăng nhập";
};
$("logoutBtn").onclick = async () => {
  try { await api("/api/logout", {}); } catch (_) { /* vẫn thoát giao diện */ }
  S.convs.clear(); S.unread.clear(); S.drafts.clear(); S.nodes.clear(); S.files.clear();
  for (const u of S.blobs.values()) URL.revokeObjectURL(u);
  S.blobs.clear(); S.rtt = []; S.cwnd = []; S.active = "*"; S.user = null; updateTitle();
  $("text").value = ""; showLogin();
};
$("discoverBtn").onclick = async () => {
  const box = $("found"); box.textContent = "Đang tìm trong mạng LAN…";
  try {
    const { servers } = await api("/api/discover");
    box.replaceChildren();
    if (!servers.length) box.textContent = "Không thấy server nào trong LAN.";
    for (const s of servers) { const b = el("button", "", s.host + ":" + s.port); b.type = "button"; b.onclick = () => { $("server").value = s.host + ":" + s.port; }; box.appendChild(b); }
  } catch (err) { box.textContent = vi(err.message); }
};
$("backBtn").onclick = () => { S.pane = "list"; $("app").dataset.pane = "list"; };
$("filter").addEventListener("input", (e) => { S.filter = e.target.value; renderRail(); });

/* ───────────────────────── giao diện sáng / tối ───────────────────────── */
function applyTheme(t) {
  if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
  const dark = (t || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light")) === "dark";
  $("themeBtn").replaceChildren(icon(dark ? "sun" : "moon"));
}
$("themeBtn").onclick = () => {
  const dark = document.documentElement.dataset.theme === "dark" || (!document.documentElement.dataset.theme && matchMedia("(prefers-color-scheme:dark)").matches);
  const t = dark ? "light" : "dark"; applyTheme(t); try { localStorage.setItem("collabnet-theme", t); } catch (_) { /* bỏ qua */ }
};
document.addEventListener("visibilitychange", () => { if (!document.hidden && S.unread.delete(S.active)) { updateTitle(); schedule("rail"); } });

/* ───────────────────────── khởi động ───────────────────────── */
function renderAll(stick) { renderRail(); renderHead(); renderLog(stick); renderFiles(); }
(async function boot() {
  let t = null; try { t = localStorage.getItem("collabnet-theme"); } catch (_) { /* bỏ qua */ }
  applyTheme(t); setPanel(S.panel);
  const s = await api("/api/state");
  $("server").value = s.default_server;
  connectEvents();
  if (s.user && (s.status === "online" || s.status === "reconnecting")) { onLogin(s.user); await loadState(); openConv("*", true); }
  else { showLogin(); renderAll(true); }
})();
