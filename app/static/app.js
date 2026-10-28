// Nerede? front end. Server mode calls the FastAPI app; Browser mode runs EmbeddingGemma 2 with
// transformers.js and searches index.json locally. Without a server (static hosting) it falls back
// to Browser mode on its own.

const TRANSFORMERS = "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.2";
const MODEL = "onnx-community/embeddinggemma-2-ONNX";
// Filters can be combined: "all" turns every one on, a click on any other includes or excludes it.
const FILTERS = ["places", "photos", "devfest", "devfest2025", "gemma"];

const T = {
  tr: {
    subtitle:
      "İstanbul'u, DevFest'i ve EmbeddingGemma 2'yi anlamıyla ara. Türkçe sor, İngilizce cevaplar bul; ya da tam tersi.",
    event: "DevFest İstanbul 2026 · 19 Aralık · Wyndham Grand İstanbul Levent",
    placeholder: "balık ekmek nerede yenir? · where is DevFest?",
    go: "Ara",
    server: "Sunucu",
    browser: "Tarayıcı",
    dims: "boyut",
    where: "Model nerede çalışsın",
    tabs: {
      all: "Hepsi",
      places: "İstanbul",
      photos: "Fotoğraflar",
      devfest: "DevFest 2026",
      devfest2025: "DevFest 2025",
      gemma: "EmbeddingGemma",
    },
    filters: "Nerede arayalım",
    took: (r) => `<b>${r.ms} ms</b> · ${r.backend} · ${r.dim} boyut`,
    intent: "niyet",
    downloading: (a, t) => `Model tarayıcına iniyor… <b>${a} / ${t} MB</b> (sonra önbellekten gelir)`,
    ready: (d, n, p, dim) => `Model hazır: <b>${d}</b> · ${n} belge, ${p} fotoğraf, ${dim} boyut`,
    staticMode: "Sunucu bulunamadı, her şey tarayıcında çalışıyor.",
    findNearby: "Google Maps'te bul",
    source: "Kaynak",
    none: "Sonuç yok",
    error: "Bir şeyler ters gitti",
    photoBy: "Fotoğraf",
    byPhoto: "Fotoğrafla ara",
    photoQuery: "senin fotoğrafın",
    dropHere: "Fotoğrafı bırak, benzerlerini bulalım",
    withPhoto: "fotoğrafa kelime ekle (isteğe bağlı) · kule, tatlı, gece",
    removePhoto: "Fotoğrafı kaldır",
    vision: "Görsel kodlayıcı tarayıcına iniyor…",
    footer1: "GDG DevFest İstanbul 2026 atölye önerisi için EmbeddingGemma 2 ile yapıldı.",
    footer2:
      'Sunucu modu: FastAPI + LiteRT-LM. Tarayıcı modu: transformers.js, sorgun cihazından çıkmaz. Fotoğraflar: <a href="images/ATTRIBUTION.md">Wikimedia Commons</a>.',
    examples: {
      all: ["balık ekmek nerede yenir", "DevFest ne zaman", "model kaç dil biliyor", "gün batımı izlemek"],
      places: [
        "Bizans mozaikleri",
        "ucuz Boğaz turu",
        "çocuklarla müze",
        "yağmurlu günde ne yapılır",
        "eski kitaplar",
        "gece sokak lezzeti",
      ],
      photos: ["kubbeli cami ve minareler", "deniz kenarında kule", "köprü ve Boğaz", "saray ve bahçe"],
      devfest: ["konferans ne zaman", "metroyla nasıl gidilir", "bilet fiyatları", "konuşmacı başvurusu"],
      devfest2025: ["2025'te kaç kişi geldi", "salonların adları", "geçen yılın sponsorları", "2025 oturumları"],
      gemma: ["model kaç parametreli", "tarayıcıda çalışır mı", "vektörü küçültürsem ne olur", "arama için hangi önek"],
    },
  },
  en: {
    subtitle:
      "Search Istanbul, DevFest and EmbeddingGemma 2 by meaning. Ask in English, find Turkish answers, or the other way round.",
    event: "DevFest Istanbul 2026 · 19 December · Wyndham Grand Istanbul Levent",
    placeholder: "where to eat a fish sandwich? · DevFest ne zaman?",
    go: "Search",
    server: "Server",
    browser: "Browser",
    dims: "dims",
    where: "Where the model runs",
    tabs: {
      all: "All",
      places: "Istanbul",
      photos: "Photos",
      devfest: "DevFest 2026",
      devfest2025: "DevFest 2025",
      gemma: "EmbeddingGemma",
    },
    filters: "What to search",
    took: (r) => `<b>${r.ms} ms</b> · ${r.backend} · ${r.dim}d`,
    intent: "intent",
    downloading: (a, t) => `Downloading the model to your browser… <b>${a} / ${t} MB</b> (cached afterwards)`,
    ready: (d, n, p, dim) => `Model ready on <b>${d}</b> · ${n} docs, ${p} photos, ${dim}d`,
    staticMode: "No server found, everything runs in your browser.",
    findNearby: "Find on Google Maps",
    source: "Source",
    none: "No results",
    error: "Something went wrong",
    photoBy: "Photo",
    byPhoto: "Search by photo",
    photoQuery: "your photo",
    dropHere: "Drop a photo to find similar places",
    withPhoto: "add words to the photo (optional) · tower, dessert, at night",
    removePhoto: "Remove the photo",
    vision: "Downloading the vision encoder to your browser…",
    footer1: "Built with EmbeddingGemma 2 for a GDG DevFest Istanbul 2026 workshop proposal.",
    footer2:
      'Server mode: FastAPI + LiteRT-LM. Browser mode: transformers.js, your query never leaves your device. Photos: <a href="images/ATTRIBUTION.md">Wikimedia Commons</a>.',
    examples: {
      all: [
        "where to eat a fish sandwich",
        "when is DevFest",
        "how many languages does the model know",
        "watch the sunset",
      ],
      places: [
        "Byzantine mosaics",
        "train under the sea",
        "museum for kids",
        "what to do when it rains",
        "old books",
        "late night street food",
      ],
      photos: ["domes and minarets", "a tower by the sea", "bridge over the Bosphorus", "palace with a garden"],
      devfest: ["when is the conference", "how do I get to the venue", "Gold Pass perks", "company invoice"],
      devfest2025: ["how many people came in 2025", "room names last year", "who sponsored", "2025 sessions"],
      gemma: ["how big is the model", "does it run in the browser", "Matryoshka dimensions", "which prefix for search"],
    },
  },
};

const $ = (id) => document.getElementById(id);
const store = {
  get: (k) => {
    try {
      return localStorage.getItem(k);
    } catch {
      return null;
    }
  },
  set: (k, v) => {
    try {
      localStorage.setItem(k, v);
    } catch {
      /* private mode */
    }
  },
};
const esc = (s) =>
  String(s ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
  );

const state = {
  lang: store.get("lang") || ((navigator.language || "tr").toLowerCase().startsWith("tr") ? "tr" : "en"),
  on: new Set(FILTERS), // which filters are included
  mode: "server",
  server: null, // /api/health payload, or false when there is no server
  browser: null, // lazy {model, tokenizer, index, device}
  last: null,
  ticket: 0, // only the newest search may render
  photo: null, // {file, url, vector} while a photo is in the search bar
};
const t = () => T[state.lang];
window.nerede = state; // poke around in DevTools: nerede.last, nerede.browser.index

// ---------- chrome: language, theme, tabs, chips --------------------------------------------------
function applyLang() {
  document.documentElement.lang = state.lang;
  document.body.dataset.drop = t().dropHere;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t()[el.dataset.i18n];
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t()[el.dataset.i18nHtml];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t()[el.dataset.i18nPlaceholder];
  });
  if (state.photo) $("q").placeholder = t().withPhoto;
  document
    .querySelectorAll("[data-i18n-aria]")
    .forEach((el) => el.setAttribute("aria-label", t()[el.dataset.i18nAria]));
  document.querySelectorAll("[data-i18n-title]").forEach((el) => el.setAttribute("title", t()[el.dataset.i18nTitle]));
  document
    .querySelectorAll("[data-lang]")
    .forEach((b) => b.setAttribute("aria-pressed", b.dataset.lang === state.lang));
  renderTabs();
  renderChips();
  if (state.last) render(state.last);
}

function applyTheme(theme) {
  if (theme) document.documentElement.dataset.theme = theme;
  const current =
    document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document
    .querySelectorAll("[data-theme]")
    .forEach((b) => b.tagName === "BUTTON" && b.setAttribute("aria-pressed", b.dataset.theme === current));
}

function counts() {
  const s = state.server || {};
  const b = state.browser?.index;
  const c =
    s.collections || (b && b.docs.reduce((m, d) => ((m[d.collection] = (m[d.collection] || 0) + 1), m), {})) || {};
  const photos = s.photos ?? b?.images.length;
  return { all: Object.values(c).reduce((a, x) => a + x, 0) || undefined, ...c, photos };
}

const allOn = () => FILTERS.every((f) => state.on.has(f));
const docCollections = () => FILTERS.filter((f) => f !== "photos" && state.on.has(f));

function toggle(key) {
  if (key === "all") state.on = new Set(FILTERS);
  else if (state.on.has(key)) state.on.delete(key);
  else state.on.add(key);
  if (!state.on.size) state.on = new Set(FILTERS); // nothing left to search: back to all
}

function renderTabs() {
  const n = counts();
  const button = (k, on) => `<button type="button" data-tab="${k}" aria-pressed="${on}">
    ${esc(t().tabs[k])}${n[k] ? `<span class="n">${n[k]}</span>` : ""}</button>`;
  $("tabs").setAttribute("aria-label", t().filters);
  $("tabs").innerHTML = button("all", allOn()) + FILTERS.map((k) => button(k, state.on.has(k))).join("");
  $("tabs")
    .querySelectorAll("button")
    .forEach(
      (b) =>
        (b.onclick = () => {
          toggle(b.dataset.tab);
          renderTabs();
          renderChips();
          if ($("q").value.trim()) run();
        }),
    );
}

function renderChips() {
  $("chips").innerHTML = "";
  const only = state.on.size === 1 ? [...state.on][0] : "all"; // one filter: its own examples
  for (const text of t().examples[only]) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = text;
    b.onclick = () => {
      $("q").value = text;
      run();
    };
    $("chips").append(b);
  }
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll("[data-mode]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.mode === mode));
  // photos work in Browser mode (the vision encoder downloads on the first photo) and on a server with PyTorch
  $("pic").hidden = mode === "server" && !state.server?.vision;
  if ($("pic").hidden) setPhoto(null);
  if (mode === "browser") loadBrowser().catch((e) => status(`${t().error}: ${esc(e.message)}`));
}

const status = (html) => {
  $("status").innerHTML = html;
  if (html.startsWith(t().error)) busy(false);
};

// ---------- browser mode ----------------------------------------------------------------------
function downloadProgress(label = "") {
  const files = {};
  return (p) => {
    if (p.status !== "progress" || !p.total) return;
    files[p.file] = [p.loaded, p.total];
    const [a, tot] = Object.values(files).reduce(([a, b], [x, y]) => [a + x, b + y], [0, 0]);
    status(
      `${label}${t().downloading((a / 1e6).toFixed(0), (tot / 1e6).toFixed(0))}<div class="progress"><i style="--p:${((100 * a) / tot).toFixed(0)}%"></i></div>`,
    );
  };
}

async function loadBrowser() {
  if (state.browser) return state.browser;
  if (state.loading) return state.loading;
  state.loading = (async () => {
    $("go").disabled = true;
    const { AutoConfig, AutoModel, AutoTokenizer } = await import(TRANSFORMERS);
    const forced = new URLSearchParams(location.search).get("device"); // ?device=wasm to compare backends
    const device =
      forced || (navigator.gpu && (await navigator.gpu.requestAdapter().catch(() => null)) ? "webgpu" : "wasm");
    const config = await AutoConfig.from_pretrained(MODEL);
    config.vision_config = config.audio_config = null; // text only: 270M params
    // q4 (~175 MB) needs WebGPU: the WASM backend has no GatherBlockQuantized kernel (q4 and q8 both use it),
    // so WASM falls back to fp16 (~543 MB). ?device=wasm&dtype=fp32 overrides both for testing.
    const dtype = new URLSearchParams(location.search).get("dtype") || (device === "webgpu" ? "q4" : "fp16");
    const [model, tokenizer, index] = await Promise.all([
      AutoModel.from_pretrained(MODEL, { config, device, dtype, progress_callback: downloadProgress() }),
      AutoTokenizer.from_pretrained(MODEL),
      fetch("index.json").then((r) => r.json()),
    ]);
    state.browser = { model, tokenizer, index, device, dtype, cache: {} };
    $("go").disabled = false;
    renderTabs();
    status(t().ready(device, index.docs.length, index.images.length, index.dim));
    return state.browser;
  })();
  try {
    return await state.loading;
  } finally {
    state.loading = null;
  }
}

const normalize = (v) => {
  const n = Math.hypot(...v) || 1;
  return v.map((x) => x / n);
};

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
  const cols = docCollections();
  const hybrid = !cols.length || VECTOR_ONLY ? { boost: null, intent: null } : await hybridBoosts(b, q);
  const byId = Object.fromEntries(b.index.images.map((i) => [i.id, i]));
  const top = (rows, n) => rows.sort((a, c) => c.score - a.score).slice(0, n);
  const results = cols.length
    ? top(
        matrix(b, "vectors", dim)
          .map((v, i) => ({ score: dot(v) + (hybrid.boost ? hybrid.boost[i] : 0), ...b.index.docs[i] }))
          .filter((r) => cols.includes(r.collection)),
        k,
      ).map((r) => ({ ...r, photo: byId[r.id] }))
    : [];
  const photos = state.on.has("photos")
    ? top(
        matrix(b, "image_vectors", dim).map((v, i) => ({ score: dot(v), ...b.index.images[i] })),
        cols.length ? 6 : 12,
      )
    : null;
  return {
    backend: `browser:${b.device}/${b.dtype}`,
    dim,
    intent: hybrid.intent,
    ms: (performance.now() - start).toFixed(1),
    results,
    photos,
  };
}

// The text-only model is swapped for one with the vision encoder on the first photo (about 109 MB more with q4).
// The text half comes from the browser cache, and text queries keep working with the new model.
async function loadVision() {
  const b = await loadBrowser();
  if (b.processor) return b;
  state.visionLoading ??= (async () => {
    const { AutoConfig, AutoModel, AutoProcessor, RawImage } = await import(TRANSFORMERS);
    const config = await AutoConfig.from_pretrained(MODEL);
    config.audio_config = null; // text + vision
    const [model, processor] = await Promise.all([
      AutoModel.from_pretrained(MODEL, {
        config,
        device: b.device,
        dtype: b.dtype,
        progress_callback: downloadProgress(`${t().vision} `),
      }),
      AutoProcessor.from_pretrained(MODEL),
    ]);
    const old = b.model;
    Object.assign(b, { model, processor, RawImage });
    await old.dispose?.();
    return b;
  })();
  try {
    return await state.visionLoading;
  } finally {
    state.visionLoading = null;
  }
}

const add = (a, c) => a.map((x, j) => x + c[j]);
const mean = (v) => v.reduce((s, x) => s + x, 0) / v.length;

// Same as Index.search_by_photo in Python: each place gets two votes, its photo (image -> image) and its text
// (image -> text). Text scores run lower, so they are shifted onto the photo scale, then the two are averaged.
function placesByPhoto(b, qv, dim, k) {
  const dot = (v) => v.reduce((s, x, j) => s + x * qv[j], 0);
  const docs = matrix(b, "vectors", dim);
  const photoScore = new Map(matrix(b, "image_vectors", dim).map((v, i) => [b.index.images[i].id, dot(v)]));
  const rows = b.index.docs.map((d, i) => [d, i]).filter(([d]) => d.collection === "places");
  const text = rows.map(([, i]) => dot(docs[i]));
  const known = rows.map(([d]) => photoScore.get(d.id)).filter((x) => x !== undefined);
  const photo = known.length ? rows.map(([d]) => photoScore.get(d.id) ?? mean(known)) : text;
  const shift = mean(photo) - mean(text);
  const byId = Object.fromEntries(b.index.images.map((i) => [i.id, i]));
  return rows
    .map(([d], j) => ({ score: (photo[j] + text[j] + shift) / 2, ...d, photo: byId[d.id] }))
    .sort((a, c) => c.score - a.score)
    .slice(0, k);
}

async function searchPhotoBrowser(q, k) {
  const b = await loadVision();
  const start = performance.now();
  // the photo is embedded once; editing the words only re-embeds the text
  state.photo.vector ??= Array.from(
    (await b.model(await b.processor(null, await b.RawImage.fromBlob(state.photo.file)))).sentence_embedding.data,
  );
  let v = normalize(state.photo.vector);
  if (q) {
    const { sentence_embedding } = await b.model(await b.tokenizer([`task: search result | query: ${q}`]));
    v = normalize(add(v, normalize(Array.from(sentence_embedding.data))));
  }
  const dim = Math.min(b.index.dim, Number($("dim").value));
  const qv = normalize(v.slice(0, dim));
  const dot = (x) => x.reduce((s, y, j) => s + y * qv[j], 0);
  const photos = matrix(b, "image_vectors", dim)
    .map((x, i) => ({ score: dot(x), ...b.index.images[i] }))
    .sort((a, c) => c.score - a.score)
    .slice(0, 12);
  return {
    backend: `browser:${b.device}/${b.dtype}`,
    dim,
    ms: (performance.now() - start).toFixed(1),
    results: placesByPhoto(b, qv, dim, k),
    photos,
  };
}

// ---------- hybrid boosts for short queries ----------------------------------------------------
// Same as nerede/keywords.py and Index.boosts in Python, keep them in sync. A one- or two-word query gets a small
// boost for the Router's intent (when it is confident) and for keyword (BM25) matches; longer queries stay pure vector.
// ?search=vector turns it off, to compare.
const VECTOR_ONLY = new URLSearchParams(location.search).get("search") === "vector";
const STOPWORDS = new Set(
  `a an and are at be by can do for from how i in is it me my of on or the to what when where which who
  with you your bir bu da de en gibi hangi icin ile mi mu ne nasil nerede neden olan siz sen ve veya ya`.split(/\s+/),
);
const fold = (s) =>
  s
    .replace(/İ/g, "i")
    .replace(/I/g, "ı")
    .toLowerCase()
    .replace(/ı/g, "i")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "");
const tokens = (s) => (fold(s).match(/[a-z0-9]+/g) || []).filter((w) => w.length > 1 && !STOPWORDS.has(w));
const wordMatch = (q, w) => w === q || (q.length >= 4 && w.startsWith(q));

function keywordScores(b, text) {
  b.kw ??= b.index.docs.map((d) =>
    tokens([d.title || "", d.district && d.district !== "Everywhere" ? d.district : "", d.text || ""].join(" ")),
  );
  const n = b.kw.length,
    avg = b.kw.reduce((s, d) => s + d.length, 0) / Math.max(1, n);
  const out = new Array(n).fill(0);
  for (const q of new Set(tokens(text))) {
    const tf = b.kw.map((doc) => doc.filter((w) => wordMatch(q, w)).length);
    const df = tf.filter((x) => x > 0).length;
    if (!df) continue;
    const idf = Math.log(1 + (n - df + 0.5) / (df + 0.5)); // BM25, k1 = 1.2, b = 0.75
    tf.forEach((f, i) => {
      out[i] += (idf * f * 2.2) / (f + 1.2 * (0.25 + (0.75 * b.kw[i].length) / avg));
    });
  }
  return out;
}

async function hybridBoosts(b, q) {
  const h = b.index.hybrid;
  if (!h || tokens(q).length > h.short_query_words) return { boost: null, intent: null };
  const { sentence_embedding } = await b.model(await b.tokenizer([`task: classification | query: ${q.trim()}`]));
  const cv = normalize(Array.from(sentence_embedding.data));
  const sims = h.label_vectors.map((v) => v.reduce((s, x, j) => s + x * cv[j], 0));
  const best = sims.indexOf(Math.max(...sims)),
    label = h.labels[best];
  const inIntent = (d) =>
    label === "ai"
      ? d.collection === "gemma"
      : label === "devfest"
        ? d.collection.startsWith("devfest")
        : d.collection === "places" && d.category === label;
  const kw = keywordScores(b, q),
    top = Math.max(...kw);
  const boost = b.index.docs.map(
    (d, i) =>
      (sims[best] >= h.intent_min_confidence && inIntent(d) ? h.intent_boost : 0) +
      (top > 0 ? (h.keyword_boost * kw[i]) / top : 0),
  );
  return { boost, intent: label };
}

// ---------- server mode -----------------------------------------------------------------------
async function searchServer(q, k) {
  const cols = docCollections();
  const get = async (path, params) => {
    const r = await fetch(`api/${path}?${params}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  };
  const docs = new URLSearchParams({ q, k, dim: $("dim").value });
  cols.forEach((c) => docs.append("collection", c));
  if (VECTOR_ONLY) docs.set("mode", "vector");
  const [d, p] = await Promise.all([
    cols.length ? get("search", docs) : null,
    state.on.has("photos")
      ? get("photos", new URLSearchParams({ q, k: cols.length ? 6 : 12, dim: $("dim").value }))
      : null,
  ]);
  return {
    ...(d || p),
    results: d ? d.results : [],
    photos: p ? p.results : null,
    ms: d && p ? Math.max(d.ms, p.ms) : (d || p).ms,
  };
}

// ---------- rendering -------------------------------------------------------------------------
const credit = (p) => `${t().photoBy}: ${p.author} · ${p.license}`;

function card(r, i = 0) {
  const img = r.photo
    ? `<img src="images/${esc(r.photo.file)}" alt="${esc(r.title)}" loading="lazy" title="${esc(credit(r.photo))}">`
    : "";
  const where = r.district && r.district !== "Everywhere" ? `<span>${esc(r.district)}</span>` : "";
  const link = (href, label) => `<a href="${href}" target="_blank" rel="noopener">${label}</a>`;
  const gmaps = (q) => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`;
  // places with coordinates get a pin on both maps; dishes and tips without one get a Google Maps search
  const map =
    r.lat != null
      ? link(`https://www.openstreetmap.org/?mlat=${r.lat}&mlon=${r.lon}#map=16/${r.lat}/${r.lon}`, "OpenStreetMap") +
        link(gmaps(`${r.lat},${r.lon}`), "Google Maps")
      : r.collection === "places"
        ? link(gmaps(`${r.title.replace(/\s*\(.*?\)/g, "")} İstanbul`), t().findNearby)
        : "";
  const src =
    r.source && /^https?:/.test(r.source)
      ? `<a href="${esc(r.source)}" target="_blank" rel="noopener">${t().source}</a>`
      : "";
  return `<li class="card" style="--i:${i}">${img}<div class="body">
    <h2>${esc(r.title)}</h2>
    <div class="meta"><span class="lang">${esc(r.lang).toUpperCase()}</span>${where}<span class="c-${esc(r.collection)}">${esc(r.category)}</span></div>
    <p>${esc(r.text)}</p>
    <div class="foot"><span class="score"><i style="--w:${Math.max(0, Math.min(100, r.score * 110)).toFixed(0)}%"></i>${r.score.toFixed(3)}</span>${map}${src}</div>
  </div></li>`;
}

function photo(r, i = 0) {
  return `<figure class="photo" style="--i:${i}"><a href="${esc(r.source)}" target="_blank" rel="noopener">
    <img src="images/${esc(r.file)}" alt="${esc(r.title)}" loading="lazy"></a>
    <figcaption><b>${esc(r.title)}</b><span class="score">${r.score.toFixed(3)}</span></figcaption>
    <small>${esc(credit(r))}</small></figure>`;
}

function render(res) {
  busy(false);
  const intent = res.intent ? ` · ${t().intent} <span class="badge">${esc(res.intent)}</span>` : "";
  const words = res.queryText ? `+ <b>${esc(res.queryText)}</b> · ` : "";
  const query = res.queryImage
    ? `<img class="qthumb" src="${res.queryImage}" alt="${esc(t().photoQuery)}"> ${words}`
    : "";
  status(query + t().took(res) + intent);
  const docs = res.results.length ? `<ol class="results">${res.results.map(card).join("")}</ol>` : "";
  const pics = res.photos?.length
    ? `${docs ? `<h3 class="strip">${esc(t().tabs.photos)}</h3>` : ""}
    <div class="photos">${res.photos.map(photo).join("")}</div>`
    : "";
  $("out").innerHTML = docs + pics || `<p class="empty">${t().none}</p>`;
}

// ---------- UI only: loading state ----------------------------------------------------------------
// A search starts on submit, on a chip, or on a tab click with a query, and ends in render() or an error
// status. In between, dim the old results (or show placeholder cards) and pulse the status dots.
const SKELETON = `<ol class="results skeleton" aria-hidden="true">${'<li class="card"><i></i><b></b><b></b><b></b></li>'.repeat(3)}</ol>`;

function busy(on) {
  const out = $("out");
  out.classList.toggle("busy", on);
  out.setAttribute("aria-busy", on);
  $("status").classList.toggle("busy", on);
  if (on && !out.querySelector(".card:not(.skeleton .card), .photo")) out.innerHTML = SKELETON;
  if (!on) out.querySelector(".skeleton")?.remove();
}

$("form").addEventListener("submit", () => {
  if (!$("q").value.trim()) return;
  busy(true);
  if (matchMedia("(pointer: coarse)").matches) $("q").blur(); // drop the on-screen keyboard so results show
});
// a small ring on every letter: two identical animations take turns, so each key restarts it
$("q").addEventListener("input", () => {
  const bar = $("form");
  const next = bar.classList.contains("key-a") ? "key-b" : "key-a";
  bar.classList.remove("key-a", "key-b");
  bar.classList.add(next);
});
$("chips").addEventListener("click", (e) => e.target.closest("button") && busy(true));
$("tabs").addEventListener("click", (e) => e.target.closest("button") && $("q").value.trim() && busy(true));
if (new URLSearchParams(location.search).get("q")) busy(true);

async function run() {
  const q = $("q").value.trim();
  if (!q && !state.photo) return;
  const ticket = ++state.ticket; // searches may overlap (tab clicks, typing); only the newest renders
  const k = 6;
  busy(true);
  try {
    const res = state.photo
      ? await searchPhoto(q, k)
      : state.mode === "server"
        ? await searchServer(q, k)
        : await searchBrowser(q, k);
    if (ticket !== state.ticket) return; // a newer search started while this one ran
    state.last = res;
    render(res);
    const url = new URL(location.href);
    if (q) url.searchParams.set("q", q);
    else url.searchParams.delete("q");
    url.searchParams.delete("tab");
    if (allOn()) url.searchParams.delete("only");
    else url.searchParams.set("only", [...state.on].join(","));
    history.replaceState(null, "", url);
  } catch (e) {
    if (ticket === state.ticket) status(`${t().error}: ${esc(e.message)}`);
  }
}

// ---------- search by photo, alone or with words --------------------------------------------------
// The photo sits as a chip in the search bar until removed. With words in the box, photo and text are added into
// one query vector (normalize(photo + text)): "kule" next to a Galata photo with a ferry in front finds the tower.
function setPhoto(file) {
  if (state.photo) URL.revokeObjectURL(state.photo.url);
  state.photo = file ? { file, url: URL.createObjectURL(file), vector: null } : null;
  $("chip").hidden = !state.photo;
  if (state.photo) $("chip").querySelector("img").src = state.photo.url;
  $("q").placeholder = state.photo ? t().withPhoto : t().placeholder;
}

async function searchPhoto(q, k) {
  const shown = { queryImage: state.photo.url, queryText: q };
  if (state.mode === "browser") return { ...(await searchPhotoBrowser(q, k)), ...shown };
  const params = new URLSearchParams({ k, dim: $("dim").value });
  if (q) params.set("q", q);
  const r = await fetch(`api/search/image?${params}`, {
    method: "POST",
    body: state.photo.file,
    headers: { "Content-Type": state.photo.file.type },
  });
  if (!r.ok) throw new Error((await r.json().catch(() => null))?.detail || `HTTP ${r.status}`);
  return { ...(await r.json()), ...shown };
}

function usePhoto(file) {
  if (!file?.type.startsWith("image/") || $("pic").hidden) return false;
  setPhoto(file);
  run();
  return true;
}

$("chip").querySelector("button").onclick = () => {
  setPhoto(null);
  if ($("q").value.trim()) run();
  else {
    state.last = null;
    $("out").innerHTML = "";
    status("");
  }
  $("q").focus();
};
$("pic").onclick = () => $("file").click();
$("file").onchange = () => {
  usePhoto($("file").files[0]);
  $("file").value = "";
};
// drop a photo anywhere on the page, or paste one (Ctrl+V)
addEventListener("dragover", (e) => {
  if ($("pic").hidden || ![...e.dataTransfer.items].some((i) => i.type.startsWith("image/"))) return;
  e.preventDefault();
  document.body.classList.add("dropping");
});
addEventListener("dragleave", (e) => {
  if (!e.relatedTarget) document.body.classList.remove("dropping");
});
addEventListener("drop", (e) => {
  document.body.classList.remove("dropping");
  const file = [...(e.dataTransfer?.files || [])].find((f) => f.type.startsWith("image/"));
  if (usePhoto(file)) e.preventDefault();
});
addEventListener("paste", (e) => {
  const file = [...(e.clipboardData?.files || [])].find((f) => f.type.startsWith("image/"));
  if (usePhoto(file)) e.preventDefault();
});

// ---------- boot ------------------------------------------------------------------------------
document.querySelectorAll("[data-lang]").forEach(
  (b) =>
    (b.onclick = () => {
      state.lang = b.dataset.lang;
      store.set("lang", state.lang);
      applyLang();
    }),
);
document.querySelectorAll("button[data-theme]").forEach(
  (b) =>
    (b.onclick = () => {
      store.set("theme", b.dataset.theme);
      applyTheme(b.dataset.theme);
    }),
);
document.querySelectorAll("[data-mode]").forEach((b) => (b.onclick = () => setMode(b.dataset.mode)));
$("form").onsubmit = (e) => {
  e.preventDefault();
  run();
};

applyTheme(store.get("theme"));
const params = new URLSearchParams(location.search);
// ?only=places,photos picks filters; the older ?tab=photos still works
const only = (params.get("only") || params.get("tab") || "").split(",").filter((f) => FILTERS.includes(f));
if (only.length) state.on = new Set(only);
if (T[params.get("lang")]) state.lang = params.get("lang"); // shareable: ?lang=tr
applyLang();

state.server = await fetch("api/health")
  .then((r) => (r.ok ? r.json() : false))
  .catch(() => false);
if (state.server) {
  setMode(params.get("mode") === "browser" ? "browser" : "server");
  renderTabs();
} else {
  $("modes").hidden = true;
  status(t().staticMode);
  setMode("browser");
}
if (params.get("q")) {
  $("q").value = params.get("q");
  run();
}
