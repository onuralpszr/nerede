// Nerede? front end. Server mode calls the FastAPI app; Browser mode runs EmbeddingGemma 2 with
// transformers.js and searches index.json locally. Without a server (static hosting) it falls back
// to Browser mode on its own.

const TRANSFORMERS = "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.2";
const MODEL = "onnx-community/embeddinggemma-2-ONNX";
const TABS = ["all", "places", "photos", "devfest", "gemma"];

const T = {
  tr: {
    subtitle: "İstanbul'u, DevFest'i ve EmbeddingGemma 2'yi anlamıyla ara. Türkçe sor, İngilizce cevaplar bul; ya da tam tersi.",
    event: "DevFest İstanbul 2026 · 19 Aralık · Wyndham Grand İstanbul Levent",
    placeholder: "balık ekmek nerede yenir? · where is DevFest?",
    go: "Ara", server: "Sunucu", browser: "Tarayıcı", dims: "boyut", where: "Model nerede çalışsın",
    tabs: { all: "Hepsi", places: "İstanbul", photos: "Fotoğraflar", devfest: "DevFest", gemma: "EmbeddingGemma" },
    took: (r) => `<b>${r.ms} ms</b> · ${r.backend} · ${r.dim} boyut`,
    intent: "niyet",
    downloading: (a, t) => `Model tarayıcına iniyor… <b>${a} / ${t} MB</b> (sonra önbellekten gelir)`,
    ready: (d, n, p, dim) => `Model hazır: <b>${d}</b> · ${n} belge, ${p} fotoğraf, ${dim} boyut`,
    staticMode: "Sunucu bulunamadı, her şey tarayıcında çalışıyor.",
    map: "Harita", source: "Kaynak", none: "Sonuç yok", error: "Bir şeyler ters gitti",
    photoBy: "Fotoğraf",
    footer1: "GDG DevFest İstanbul 2026 atölye önerisi için EmbeddingGemma 2 ile yapıldı.",
    footer2: 'Sunucu modu: FastAPI + LiteRT-LM. Tarayıcı modu: transformers.js, sorgun cihazından çıkmaz. Fotoğraflar: <a href="images/ATTRIBUTION.md">Wikimedia Commons</a>.',
    examples: {
      all: ["balık ekmek nerede yenir", "DevFest ne zaman", "model kaç dil biliyor", "gün batımı izlemek"],
      places: ["Bizans mozaikleri", "ucuz Boğaz turu", "çocuklarla müze", "yağmurlu günde ne yapılır", "eski kitaplar", "gece sokak lezzeti"],
      photos: ["kubbeli cami ve minareler", "deniz kenarında kule", "köprü ve Boğaz", "saray ve bahçe"],
      devfest: ["konferans ne zaman", "metroyla nasıl gidilir", "bilet fiyatları", "konuşmacı başvurusu"],
      gemma: ["model kaç parametreli", "tarayıcıda çalışır mı", "vektörü küçültürsem ne olur", "arama için hangi önek"],
    },
  },
  en: {
    subtitle: "Search Istanbul, DevFest and EmbeddingGemma 2 by meaning. Ask in English, find Turkish answers, or the other way round.",
    event: "DevFest Istanbul 2026 · 19 December · Wyndham Grand Istanbul Levent",
    placeholder: "where to eat a fish sandwich? · DevFest ne zaman?",
    go: "Search", server: "Server", browser: "Browser", dims: "dims", where: "Where the model runs",
    tabs: { all: "All", places: "Istanbul", photos: "Photos", devfest: "DevFest", gemma: "EmbeddingGemma" },
    took: (r) => `<b>${r.ms} ms</b> · ${r.backend} · ${r.dim}d`,
    intent: "intent",
    downloading: (a, t) => `Downloading the model to your browser… <b>${a} / ${t} MB</b> (cached afterwards)`,
    ready: (d, n, p, dim) => `Model ready on <b>${d}</b> · ${n} docs, ${p} photos, ${dim}d`,
    staticMode: "No server found, everything runs in your browser.",
    map: "Map", source: "Source", none: "No results", error: "Something went wrong",
    photoBy: "Photo",
    footer1: "Built with EmbeddingGemma 2 for a GDG DevFest Istanbul 2026 workshop proposal.",
    footer2: 'Server mode: FastAPI + LiteRT-LM. Browser mode: transformers.js, your query never leaves your device. Photos: <a href="images/ATTRIBUTION.md">Wikimedia Commons</a>.',
    examples: {
      all: ["where to eat a fish sandwich", "when is DevFest", "how many languages does the model know", "watch the sunset"],
      places: ["Byzantine mosaics", "train under the sea", "museum for kids", "what to do when it rains", "old books", "late night street food"],
      photos: ["domes and minarets", "a tower by the sea", "bridge over the Bosphorus", "palace with a garden"],
      devfest: ["when is the conference", "how do I get to the venue", "Gold Pass perks", "last year's numbers"],
      gemma: ["how big is the model", "does it run in the browser", "Matryoshka dimensions", "which prefix for search"],
    },
  },
};

const $ = (id) => document.getElementById(id);
const store = {
  get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const state = {
  lang: store.get("lang") || ((navigator.language || "tr").toLowerCase().startsWith("tr") ? "tr" : "en"),
  tab: "all",
  mode: "server",
  server: null,     // /api/health payload, or false when there is no server
  browser: null,    // lazy {model, tokenizer, index, device}
  last: null,
  ticket: 0,        // only the newest search may render
};
const t = () => T[state.lang];
window.nerede = state; // poke around in DevTools: nerede.last, nerede.browser.index

// ---------- chrome: language, theme, tabs, chips --------------------------------------------------
function applyLang() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t()[el.dataset.i18n]; });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => { el.innerHTML = t()[el.dataset.i18nHtml]; });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => { el.placeholder = t()[el.dataset.i18nPlaceholder]; });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => el.setAttribute("aria-label", t()[el.dataset.i18nAria]));
  document.querySelectorAll("[data-lang]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.lang === state.lang));
  renderTabs();
  renderChips();
  if (state.last) render(state.last);
}

function applyTheme(theme) {
  if (theme) document.documentElement.dataset.theme = theme;
  const current = document.documentElement.dataset.theme
    || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.querySelectorAll("[data-theme]").forEach((b) => b.tagName === "BUTTON" && b.setAttribute("aria-pressed", b.dataset.theme === current));
}

function counts() {
  const s = state.server || {};
  const b = state.browser?.index;
  const c = s.collections || (b && b.docs.reduce((m, d) => ((m[d.collection] = (m[d.collection] || 0) + 1), m), {})) || {};
  const photos = s.photos ?? b?.images.length;
  return { all: Object.values(c).reduce((a, x) => a + x, 0) || undefined, ...c, photos };
}

function renderTabs() {
  const n = counts();
  $("tabs").innerHTML = TABS.map((k) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${k === state.tab}">
    ${esc(t().tabs[k])}${n[k] ? `<span class="n">${n[k]}</span>` : ""}</button>`).join("");
  $("tabs").querySelectorAll("button").forEach((b) => b.onclick = () => {
    state.tab = b.dataset.tab;
    renderTabs();
    renderChips();
    if ($("q").value.trim()) run();
  });
}

function renderChips() {
  $("chips").innerHTML = "";
  for (const text of t().examples[state.tab]) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = text;
    b.onclick = () => { $("q").value = text; run(); };
    $("chips").append(b);
  }
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll("[data-mode]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.mode === mode));
  if (mode === "browser") loadBrowser().catch((e) => status(`${t().error}: ${esc(e.message)}`));
}

const status = (html) => { $("status").innerHTML = html; };

// ---------- browser mode ----------------------------------------------------------------------
async function loadBrowser() {
  if (state.browser) return state.browser;
  if (state.loading) return state.loading;
  state.loading = (async () => {
    $("go").disabled = true;
    const { AutoConfig, AutoModel, AutoTokenizer } = await import(TRANSFORMERS);
    const forced = new URLSearchParams(location.search).get("device"); // ?device=wasm to compare backends
    const device = forced || ((navigator.gpu && await navigator.gpu.requestAdapter().catch(() => null)) ? "webgpu" : "wasm");
    const config = await AutoConfig.from_pretrained(MODEL);
    config.vision_config = config.audio_config = null; // text only: 270M params
    // q4 (~175 MB) needs WebGPU: the WASM backend has no GatherBlockQuantized kernel (q4 and q8 both use it),
    // so WASM falls back to fp16 (~543 MB). ?device=wasm&dtype=fp32 overrides both for testing.
    const dtype = new URLSearchParams(location.search).get("dtype") || (device === "webgpu" ? "q4" : "fp16");
    const files = {};
    const progress = (p) => {
      if (p.status !== "progress" || !p.total) return;
      files[p.file] = [p.loaded, p.total];
      const [a, tot] = Object.values(files).reduce(([a, b], [x, y]) => [a + x, b + y], [0, 0]);
      status(`${t().downloading((a / 1e6).toFixed(0), (tot / 1e6).toFixed(0))}<div class="progress"><i style="--p:${(100 * a / tot).toFixed(0)}%"></i></div>`);
    };
    const [model, tokenizer, index] = await Promise.all([
      AutoModel.from_pretrained(MODEL, { config, device, dtype, progress_callback: progress }),
      AutoTokenizer.from_pretrained(MODEL),
      fetch("index.json").then((r) => r.json()),
    ]);
    state.browser = { model, tokenizer, index, device: `${device}/${dtype}`, cache: {} };
    $("go").disabled = false;
    renderTabs();
    status(t().ready(device, index.docs.length, index.images.length, index.dim));
    return state.browser;
  })();
  try { return await state.loading; } finally { state.loading = null; }
}

const normalize = (v) => { const n = Math.hypot(...v) || 1; return v.map((x) => x / n); };

function matrix(b, key, dim) {
  const id = `${key}:${dim}`;
  b.cache[id] ??= b.index[key].map((v) => normalize(v.slice(0, dim)));
  return b.cache[id];
}

async function searchBrowser(q, k) {
  const b = await loadBrowser();
  const start = performance.now();
  const { sentence_embedding } = await b.model(await b.tokenizer([`task: search result | query: ${q}`]));
  const dim = Math.min(b.index.dim, Number($("dim").value));
  const qv = normalize(Array.from(sentence_embedding.data).slice(0, dim));
  const dot = (v) => v.reduce((s, x, j) => s + x * qv[j], 0);
  const photos = state.tab === "photos";
  const records = photos ? b.index.images : b.index.docs;
  const byId = Object.fromEntries(b.index.images.map((i) => [i.id, i]));
  const results = matrix(b, photos ? "image_vectors" : "vectors", dim)
    .map((v, i) => ({ score: dot(v), ...records[i] }))
    .filter((r) => photos || state.tab === "all" || r.collection === state.tab)
    .sort((a, c) => c.score - a.score).slice(0, k)
    .map((r) => (photos ? r : { ...r, photo: byId[r.id] }));
  return { backend: `browser:${b.device}`, dim, intent: null, ms: (performance.now() - start).toFixed(1), results, photos };
}

// ---------- server mode -----------------------------------------------------------------------
async function searchServer(q, k) {
  const photos = state.tab === "photos";
  const params = new URLSearchParams({ q, k, dim: $("dim").value });
  if (!photos) params.set("collection", state.tab);
  const r = await fetch(`api/${photos ? "photos" : "search"}?${params}`);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return { ...(await r.json()), photos };
}

// ---------- rendering -------------------------------------------------------------------------
const credit = (p) => `${t().photoBy}: ${p.author} · ${p.license}`;

function card(r) {
  const img = r.photo ? `<img src="images/${esc(r.photo.file)}" alt="${esc(r.title)}" loading="lazy" title="${esc(credit(r.photo))}">` : "";
  const where = r.district && r.district !== "Everywhere" ? `<span>${esc(r.district)}</span>` : "";
  const map = r.lat != null ? `<a href="https://www.openstreetmap.org/?mlat=${r.lat}&mlon=${r.lon}#map=16/${r.lat}/${r.lon}" target="_blank" rel="noopener">${t().map}</a>` : "";
  const src = r.source && /^https?:/.test(r.source) ? `<a href="${esc(r.source)}" target="_blank" rel="noopener">${t().source}</a>` : "";
  return `<li class="card">${img}<div class="body">
    <h2>${esc(r.title)}</h2>
    <div class="meta"><span class="lang">${esc(r.lang).toUpperCase()}</span>${where}<span class="c-${esc(r.collection)}">${esc(r.category)}</span></div>
    <p>${esc(r.text)}</p>
    <div class="foot"><span class="score"><i style="--w:${Math.max(0, Math.min(100, r.score * 110)).toFixed(0)}%"></i>${r.score.toFixed(3)}</span>${map}${src}</div>
  </div></li>`;
}

function photo(r) {
  return `<figure class="photo"><a href="${esc(r.source)}" target="_blank" rel="noopener">
    <img src="images/${esc(r.file)}" alt="${esc(r.title)}" loading="lazy"></a>
    <figcaption><b>${esc(r.title)}</b><span class="score">${r.score.toFixed(3)}</span></figcaption>
    <small>${esc(credit(r))}</small></figure>`;
}

function render(res) {
  const intent = res.intent ? ` · ${t().intent} <span class="badge">${esc(res.intent)}</span>` : "";
  status(t().took(res) + intent);
  if (!res.results.length) { $("out").innerHTML = `<p class="empty">${t().none}</p>`; return; }
  $("out").innerHTML = res.photos
    ? `<div class="photos">${res.results.map(photo).join("")}</div>`
    : `<ol class="results">${res.results.map(card).join("")}</ol>`;
}

async function run() {
  const q = $("q").value.trim();
  if (!q) return;
  const ticket = ++state.ticket; // searches may overlap (tab clicks, typing); only the newest renders
  const k = state.tab === "photos" ? 12 : 6;
  try {
    const res = state.mode === "server" ? await searchServer(q, k) : await searchBrowser(q, k);
    if (ticket !== state.ticket) return; // a newer search started while this one ran
    state.last = res;
    render(res);
    const url = new URL(location.href);
    url.searchParams.set("q", q);
    url.searchParams.set("tab", state.tab);
    history.replaceState(null, "", url);
  } catch (e) {
    if (ticket === state.ticket) status(`${t().error}: ${esc(e.message)}`);
  }
}

// ---------- boot ------------------------------------------------------------------------------
document.querySelectorAll("[data-lang]").forEach((b) => b.onclick = () => { state.lang = b.dataset.lang; store.set("lang", state.lang); applyLang(); });
document.querySelectorAll("button[data-theme]").forEach((b) => b.onclick = () => { store.set("theme", b.dataset.theme); applyTheme(b.dataset.theme); });
document.querySelectorAll("[data-mode]").forEach((b) => b.onclick = () => setMode(b.dataset.mode));
$("form").onsubmit = (e) => { e.preventDefault(); run(); };

applyTheme(store.get("theme"));
const params = new URLSearchParams(location.search);
if (TABS.includes(params.get("tab"))) state.tab = params.get("tab");
if (T[params.get("lang")]) state.lang = params.get("lang"); // shareable: ?lang=tr
applyLang();

state.server = await fetch("api/health").then((r) => (r.ok ? r.json() : false)).catch(() => false);
if (state.server) {
  setMode(params.get("mode") === "browser" ? "browser" : "server");
  renderTabs();
} else {
  $("modes").hidden = true;
  status(t().staticMode);
  setMode("browser");
}
if (params.get("q")) { $("q").value = params.get("q"); run(); }
