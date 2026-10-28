// Drives the web UI in headless Chrome. On a static host (no /api) the page must switch to Browser mode itself.
// usage: node bench/browser_test.mjs http://127.0.0.1:8790/demo/ [browser]
import { spawn } from "node:child_process";
const url = process.argv[2] || "http://127.0.0.1:8765/";
const forceBrowser = process.argv[3] === "browser";
const chrome = spawn("google-chrome", ["--headless=new", "--remote-debugging-port=9333", "--no-first-run",
  "--user-data-dir=bench/.chrome", "--enable-unsafe-webgpu", "--enable-features=Vulkan", "about:blank"], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 2000));
const target = await (await fetch(`http://127.0.0.1:9333/json/new?${encodeURIComponent(url)}`, { method: "PUT" })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0; const pending = {};
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (pending[d.id]) { pending[d.id](d.result); delete pending[d.id]; } };
await new Promise((r) => (ws.onopen = r));
const send = (method, params = {}) => new Promise((r) => { pending[++id] = r; ws.send(JSON.stringify({ id, method, params })); });
const js = async (expr) => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result.value;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await sleep(2500);
if (forceBrowser) await js(`document.querySelector('[data-mode=browser]').click()`);
console.log("server toggle hidden:", await js(`document.getElementById('modes').hidden`));
const t0 = Date.now();
while (Date.now() - t0 < 300000) {
  const s = await js(`document.getElementById('status').innerText`);
  if (/ready|hazır|wrong|ters/i.test(s)) { console.log("status:", s); break; }
  await sleep(1000);
}
const ask = async (tab, q) => {
  await js(`document.querySelector('[data-tab=${tab}]').click(); document.getElementById('q').value = ${JSON.stringify(q)}; document.getElementById('go').click()`);
  await sleep(5000);
  const sel = tab === "photos" ? "figure b" : "li h2";
  console.log(`${tab} | ${q} =>`, await js(`document.getElementById('status').innerText + " | " + [...document.querySelectorAll('${sel}')].slice(0,3).map(e => e.innerText).join(", ")`));
};
await ask("all", "balık ekmek nerede yenir");
await ask("devfest", "how do I get to the venue");
await ask("gemma", "model kaç dil biliyor");
await ask("photos", "domes and minarets");
ws.close(); chrome.kill();
