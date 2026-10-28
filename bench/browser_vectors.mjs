// Embeds 8 queries in browser mode and saves the full vectors, to compare with PyTorch.
// usage: node bench/browser_vectors.mjs "http://127.0.0.1:8790/demo/?mode=browser&dtype=q4" bench/vectors_q4.json [chrome flags]
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
const [url, out, ...flags] = process.argv.slice(2);
const chrome = spawn("google-chrome", ["--remote-debugging-port=9336", "--no-first-run", "--user-data-dir=bench/.chrome",
  "--enable-unsafe-webgpu", ...flags, "about:blank"], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 3000));
const target = await (await fetch(`http://127.0.0.1:9336/json/new?${encodeURIComponent(url)}`, { method: "PUT" })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0; const pending = {};
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (pending[d.id]) { pending[d.id](d.result); delete pending[d.id]; } };
await new Promise((r) => (ws.onopen = r));
const send = (method, params = {}) => new Promise((r) => { pending[++id] = r; ws.send(JSON.stringify({ id, method, params })); });
const js = async (expr) => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result;
await new Promise((r) => setTimeout(r, 2000));
const qs = JSON.stringify(["balık ekmek nerede yenir", "how do I get to the venue", "model kaç dil biliyor", "a quiet place to read",
  "boğazda kahvaltı", "where can I see old ships", "metro ile havalimanı", "Matryoshka nedir"]);
const r = await js(`(async () => { for (let i = 0; i < 600 && !window.nerede.browser; i++) await new Promise(r => setTimeout(r, 1000));
  const b = window.nerede.browser, out = [];
  for (const q of ${qs}) { const { sentence_embedding } = await b.model(await b.tokenizer([\`task: search result | query: \${q}\`])); out.push(Array.from(sentence_embedding.data)); }
  return { device: b.device, out }; })()`);
writeFileSync(out, JSON.stringify(r.value));
console.log("device", r.value.device);
ws.close(); chrome.kill(); process.exit(0);
