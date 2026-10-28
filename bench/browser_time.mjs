// Times browser-mode queries in a real Chrome window.
// usage: node bench/browser_time.mjs "http://127.0.0.1:8790/demo/?mode=browser&dtype=fp16" --ozone-platform=wayland --enable-features=Vulkan
import { spawn } from "node:child_process";
const [url, ...flags] = process.argv.slice(2);
const chrome = spawn(
  "google-chrome",
  [
    "--remote-debugging-port=9335",
    "--no-first-run",
    "--user-data-dir=bench/.chrome",
    "--enable-unsafe-webgpu",
    ...flags,
    "about:blank",
  ],
  { stdio: "ignore" },
);
await new Promise((r) => setTimeout(r, 3000));
const target = await (
  await fetch(`http://127.0.0.1:9335/json/new?${encodeURIComponent(url)}`, { method: "PUT" })
).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0;
const pending = {};
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (pending[d.id]) {
    pending[d.id](d.result);
    delete pending[d.id];
  }
};
await new Promise((r) => (ws.onopen = r));
const send = (method, params = {}) =>
  new Promise((r) => {
    pending[++id] = r;
    ws.send(JSON.stringify({ id, method, params }));
  });
const js = async (expr) =>
  (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result.value;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await sleep(2000);
console.log(
  "adapter:",
  JSON.stringify(
    await js(
      `navigator.gpu ? navigator.gpu.requestAdapter().then(a => a && {vendor: a.info.vendor, arch: a.info.architecture, desc: a.info.description, fallback: a.info.isFallbackAdapter}) : "no navigator.gpu"`,
    ),
  ),
);
const t0 = Date.now();
while (Date.now() - t0 < 600000) {
  const s = await js(`document.getElementById('status').innerText`);
  if (/ready|hazır|error|hata/i.test(s)) {
    console.log(`status after ${((Date.now() - t0) / 1000).toFixed(0)} s:`, s);
    break;
  }
  await sleep(1000);
}
const qs = [
  "balık ekmek nerede yenir",
  "how do I get to the venue",
  "model kaç dil biliyor",
  "a quiet place to read",
  "boğazda kahvaltı",
  "where can I see old ships",
  "metro ile havalimanı",
  "Matryoshka nedir",
  "tarihi hamam",
  "night views of the city",
  "simit",
];
const times = [];
for (const q of qs) {
  await js(
    `document.getElementById('q').value = ${JSON.stringify(q)}; document.getElementById('status').innerText = ''; document.getElementById('go').click()`,
  );
  let s = "";
  for (let i = 0; i < 300 && !/ms/.test(s); i++) {
    await sleep(100);
    s = await js(`document.getElementById('status').innerText`);
  }
  times.push(parseFloat(s));
  console.log(q, "=>", s.split("\n")[0]);
}
const warm = times.slice(1).sort((a, b) => a - b);
console.log(`first ${times[0]} ms, median warm ${warm[Math.floor(warm.length / 2)]} ms`);
ws.close();
chrome.kill();
process.exit(0);
