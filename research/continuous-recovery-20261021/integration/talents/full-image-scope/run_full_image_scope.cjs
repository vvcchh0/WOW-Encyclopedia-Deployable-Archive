"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { chromium } = require("C:/Users/17630/AppData/Local/OpenAI/Codex/runtimes/cua_node/78fb63cda1a9e2b2/bin/node_modules/playwright-core");
const ROOT = path.resolve(__dirname, "../../../../../");
const OUT = __dirname;
const EXPORT_ROOT = path.join(ROOT, ".scratch/pages-resources-20261021-v42");
const ROUTE_MAP_PATH = path.join(EXPORT_ROOT, "__offline/route-map.json");
const PROVENANCE_PATH = path.join(EXPORT_ROOT, "export-provenance.json");
const PORT = Number(process.env.TALENT_SCOPE_PORT || 34881);
const BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive";
const BASE = `http://127.0.0.1:${PORT}${BASE_PATH}`;
const CLASSES = ["druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock", "warrior"];
const IMAGE_EXT = /\.(?:png|jpe?g|gif|webp|svg|bmp|ico|avif)(?:$|[?#])/i;
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function sha256File(file) { return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"); }
function isLoopback(url) { try { const u = new URL(url); return u.protocol === "http:" && u.hostname === "127.0.0.1" && u.port === String(PORT); } catch (_) { return false; } }
function safeUrl(value, base) { try { return new URL(value, base).href; } catch (_) { return null; } }
function decodeRequested(value) { if (!value) return null; let result = value; for (let i = 0; i < 4; i += 1) { let next; try { next = decodeURIComponent(result); } catch (_) { break; } if (next === result) break; result = next; } return result; }
function urlPath(url) { try { return new URL(url).pathname; } catch (_) { return null; } }
function sourcePathFromUrl(url) { let p = urlPath(url); if (!p && typeof url === "string" && url.startsWith("/")) p = url.split("?", 1)[0]; if (!p) return null; let local = p; if (local.startsWith(BASE_PATH)) local = local.slice(BASE_PATH.length) || "/"; if (!local.startsWith("/")) local = `/${local}`; return local; }
function localEvidence(url, routeMap, provenanceByRoute) {
  const p = sourcePathFromUrl(url);
  if (!p || p === "/") return { route: p, local_path: null, exists: false, route_map: false, provenance: false };
  const rel = p.replace(/^\/+/, ""); const file = path.join(EXPORT_ROOT, rel); let exists = false, length = null, sha = null;
  try { const st = fs.statSync(file); exists = st.isFile(); if (exists) { length = st.size; sha = sha256File(file); } } catch (_) {}
  const routeMapPresent = !!((routeMap.routes && routeMap.routes[p]) || (routeMap.aliases && routeMap.aliases[p])); const prov = provenanceByRoute[p] || [];
  return { route: p, local_path: path.relative(ROOT, file).replaceAll(path.sep, "/"), exists, length, sha256: sha, route_map: routeMapPresent, provenance: prov.length > 0, provenance_records: prov.slice(0, 2).map((r) => ({ route: r.route, output_path: r.output_path, derived_length: r.derived_length, derived_sha256: r.derived_sha256, kind: r.kind })) };
}
function likelyImageRequest(url, type) { return type === "image" || IMAGE_EXT.test(urlPath(url) || ""); }
function parseCssUrls(css) { const out = []; const re = /url\((?:\s*["']?)([^"')]+)(?:["']?\s*)\)/gi; let m; while ((m = re.exec(css || ""))) out.push(m[1]); return out; }
function requestedInfo(absUrl) { try { const u = new URL(absUrl); if (!u.pathname.endsWith("/missing-image.svg")) return null; const raw = u.searchParams.get("requested"); return { raw, decoded: decodeRequested(raw) }; } catch (_) { return null; } }
function inferredUse(element) { const hay = `${element.selector || ""} ${element.id || ""} ${element.className || ""} ${element.alt || ""} ${element.title || ""} ${element.url || ""}`.toLowerCase(); if (hay.includes("background.jpg") || hay.includes("background.gif") || hay.includes("background.png")) return "tree-background"; if (hay.includes("/images/talents/arrows/")) return "talent-connector"; if (hay.includes("/images/talents/icon-over")) return "talent-state-overlay"; if (["bot-box", "reset.gif", "resetall.gif", "printableversion.gif", "text-classname.gif", "text-talents.gif"].some((x) => hay.includes(x))) return "talent-ui"; if (hay.includes("/global/talents/") && hay.includes("/images/")) return "talent-icon"; if (hay.includes("shared/wow-com") || hay.includes("subnav") || hay.includes("layout")) return "site-layout"; if (hay.includes("tree") || hay.includes("background")) return "tree-background-or-layout"; if (hay.includes("talent") || hay.includes("spell") || hay.includes("icon") || hay.includes("rank")) return "talent-icon"; return element.kind === "background" ? "background" : "other-image"; }
function inferredTree(target, fallback) { const p = sourcePathFromUrl(target || "") || target || ""; const parts = String(p).split("/"); const ti = parts.indexOf("talents"); if (ti >= 0 && parts[ti + 1] === "images") return "common-talents-ui"; const ii = ti >= 0 ? parts.indexOf("images", ti + 1) : -1; if (ii >= 0 && parts[ii + 2]) return parts[ii + 1]; return ii >= 0 ? "shared-talent-layout" : (fallback || null); }
function makeCsv(rows) { const fields = ["classification", "class", "trees", "uses", "target", "raw_targets", "references", "references_by_class", "pages", "elements", "local_exists", "route_map", "provenance"]; const quote = (v) => { const value = v && typeof v === "object" && !Array.isArray(v) ? JSON.stringify(v) : String(v == null ? "" : v); return `"${value.replaceAll("\"", "\"\"")}"`; }; return [fields.join(","), ...rows.map((r) => fields.map((f) => quote(Array.isArray(r[f]) ? r[f].join(" | ") : r[f])).join(","))].join("\n") + "\n"; }
async function auditPage(context, cls, routeMap, provenanceByRoute) {
  const page = await context.newPage(); const pageErrors = [], consoleErrors = [], failedRequests = [], blocked = [], responses = [];
  page.on("pageerror", (e) => pageErrors.push({ name: e.name, message: e.message, stack: e.stack || null }));
  page.on("console", (m) => { if (m.type() === "error") consoleErrors.push({ text: m.text(), location: m.location() }); });
  page.on("requestfailed", (req) => { const f = req.failure(); const item = { url: req.url(), type: req.resourceType(), error: f && f.errorText }; if (isLoopback(req.url())) failedRequests.push(item); else blocked.push(item); });
  page.on("response", (res) => { const req = res.request(); responses.push({ url: res.url(), status: res.status(), type: req.resourceType(), method: req.method(), fromServiceWorker: res.fromServiceWorker() }); });
  const target = `${BASE}/info/classes/${cls}/talents.html`; let navigationError = null; const started = Date.now();
  try { await page.goto(target, { waitUntil: "domcontentloaded", timeout: 10000 }); await page.waitForTimeout(1200); } catch (e) { navigationError = String(e && e.stack || e); }
  const observed = await page.evaluate(() => {
    function treeFor(el) { let p = el; while (p && p !== document.body) { const token = `${p.id || ""} ${typeof p.className === "string" ? p.className : ""}`.trim(); if (/tree/i.test(token)) return token.slice(0, 160); p = p.parentElement; } return null; }
    function chain(el) { const out = []; let p = el; for (let i = 0; p && i < 5; i += 1, p = p.parentElement) out.push(`${p.tagName.toLowerCase()}${p.id ? `#${p.id}` : ""}${typeof p.className === "string" && p.className.trim() ? `.${p.className.trim().split(/\s+/).slice(0, 3).join(".")}` : ""}`); return out; }
    const records = [];
    document.querySelectorAll("img").forEach((el, index) => { const style = getComputedStyle(el); records.push({ kind: "img", index, selector: `${el.tagName.toLowerCase()}${el.id ? `#${el.id}` : ""}${typeof el.className === "string" && el.className.trim() ? `.${el.className.trim().split(/\s+/).slice(0, 4).join(".")}` : ""}`, id: el.id || null, className: typeof el.className === "string" ? el.className : null, alt: el.getAttribute("alt"), title: el.getAttribute("title"), inline: el.getAttribute("style"), computedBackground: style.backgroundImage, src: el.getAttribute("src"), currentSrc: el.currentSrc || null, naturalWidth: el.naturalWidth, naturalHeight: el.naturalHeight, tree: treeFor(el), chain: chain(el) }); });
    Array.from(document.querySelectorAll("*")).forEach((el, index) => { const inline = el.getAttribute("style") || ""; const computed = getComputedStyle(el).backgroundImage || "none"; if (!/url\(/i.test(inline) && computed === "none") return; records.push({ kind: "background", index, selector: `${el.tagName.toLowerCase()}${el.id ? `#${el.id}` : ""}${typeof el.className === "string" && el.className.trim() ? `.${el.className.trim().split(/\s+/).slice(0, 4).join(".")}` : ""}`, id: el.id || null, className: typeof el.className === "string" ? el.className : null, alt: null, title: el.getAttribute("title"), inline, computedBackground: computed, src: null, currentSrc: null, naturalWidth: null, naturalHeight: null, tree: treeFor(el), chain: chain(el) }); });
    return { title: document.title, bodyText: (document.body?.innerText || "").replace(/\s+/g, " ").slice(0, 800), records, htmlLength: document.documentElement.outerHTML.length };
  });
  await page.close();
  const eventRows = [];
  for (const rec of observed.records) {
    const rawUrls = [];
    if (rec.kind === "img") { if (rec.currentSrc) rawUrls.push({ value: rec.currentSrc, attr: "currentSrc" }); else if (rec.src) rawUrls.push({ value: safeUrl(rec.src, target), attr: "src" }); }
    for (const value of [rec.inline, rec.computedBackground].filter((x) => x && x !== "none").flatMap(parseCssUrls)) rawUrls.push({ value: safeUrl(value, target), attr: "background-image" });
    for (const raw of rawUrls) { if (!raw.value) continue; const placeholder = requestedInfo(raw.value); const evidence = localEvidence(placeholder?.decoded || raw.value, routeMap, provenanceByRoute); eventRows.push({ class: cls, route: `/info/classes/${cls}/talents.html`, kind: rec.kind, selector: rec.selector, element_index: rec.index, tree: inferredTree(placeholder?.decoded || raw.value, rec.tree), use: inferredUse({ ...rec, url: placeholder?.decoded || raw.value }), attribute: raw.attr, observed_url: raw.value, original_target: placeholder?.decoded || null, placeholder_query: placeholder?.raw || null, classification: placeholder ? "static_placeholder" : "observed_dom_image", local: evidence, naturalWidth: rec.naturalWidth, naturalHeight: rec.naturalHeight, chain: rec.chain }); }
  }
  const responseRows = responses.filter((r) => isLoopback(r.url) && r.status >= 400 && likelyImageRequest(r.url, r.type)).map((r) => ({ ...r, class: cls, route: `/info/classes/${cls}/talents.html`, target: r.url, tree: inferredTree(r.url, null), use: inferredUse({ kind: "response", url: r.url }), local: localEvidence(r.url, routeMap, provenanceByRoute), classification: "dynamic_http_error" }));
  const failedImageRows = failedRequests.filter((r) => isLoopback(r.url) && likelyImageRequest(r.url, r.type) && !((urlPath(r.url) || "").endsWith("/__offline/missing-image.svg"))).map((r) => ({ ...r, class: cls, route: `/info/classes/${cls}/talents.html`, target: r.url, tree: inferredTree(r.url, null), use: inferredUse({ kind: "response", url: r.url }), local: localEvidence(r.url, routeMap, provenanceByRoute), classification: "dynamic_request_failed" }));
  return { class: cls, route: `/info/classes/${cls}/talents.html`, url: target, durationMs: Date.now() - started, title: observed.title, bodyText: observed.bodyText, htmlLength: observed.htmlLength, domRecords: observed.records.length, observations: eventRows, dynamicErrors: responseRows.concat(failedImageRows), pageErrors, consoleErrors, failedRequests, blockedExternal: blocked, responses: responses.length, navigationError };
}
function aggregate(pages) {
  const refs = pages.flatMap((p) => p.observations);
  const dynamic = pages.flatMap((p) => p.dynamicErrors);
  const staticMap = new Map(), dynamicMap = new Map(), domMissingMap = new Map();
  const add = (map, row, target, rawTarget) => {
    const key = sourcePathFromUrl(target) || target;
    let x = map.get(key);
    if (!x) { x = { target: key, rawTargets: new Set(), classification: row.classification, references: 0, referencesByClass: {}, classes: new Set(), pages: new Set(), trees: new Set(), uses: new Set(), elements: new Set(), local: row.local }; map.set(key, x); }
    x.references += 1; x.referencesByClass[row.class] = (x.referencesByClass[row.class] || 0) + 1; x.rawTargets.add(rawTarget || target); x.classes.add(row.class); x.pages.add(row.route); if (row.tree) x.trees.add(row.tree); if (row.use) x.uses.add(row.use); x.elements.add(`${row.class}:${row.selector || "response"}`);
  };
  for (const row of refs) {
    if (row.classification === "static_placeholder") add(staticMap, row, row.original_target || row.observed_url, row.original_target || row.observed_url);
    else if (!row.local?.exists && likelyImageRequest(row.observed_url, row.kind === "img" ? "image" : "style")) add(domMissingMap, { ...row, classification: "dom_local_missing" }, row.observed_url, row.observed_url);
  }
  for (const row of dynamic) add(dynamicMap, row, row.target, row.target);
  const normalize = (x) => ({ target: x.target, raw_targets: [...x.rawTargets].sort(), classification: x.classification, references: x.references, references_by_class: x.referencesByClass, classes: [...x.classes].sort(), pages: [...x.pages].sort(), trees: [...x.trees].sort(), uses: [...x.uses].sort(), elements: [...x.elements].sort(), local: x.local, local_exists: !!x.local?.exists, route_map: !!x.local?.route_map, provenance: !!x.local?.provenance });
  const staticRows = [...staticMap.values()].map(normalize), dynamicRows = [...dynamicMap.values()].map(normalize), domMissingRows = [...domMissingMap.values()].map(normalize), merged = new Map();
  for (const row of staticRows.concat(dynamicRows, domMissingRows)) {
    if (!merged.has(row.target)) merged.set(row.target, { ...row, classifications: [row.classification] });
    else { const x = merged.get(row.target); x.classifications = [...new Set([...x.classifications, row.classification])].sort(); x.references += row.references; for (const [cls, n] of Object.entries(row.references_by_class || {})) x.references_by_class[cls] = (x.references_by_class[cls] || 0) + n; x.raw_targets = [...new Set([...(x.raw_targets || []), ...(row.raw_targets || [])])].sort(); x.classes = [...new Set([...x.classes, ...row.classes])].sort(); x.pages = [...new Set([...x.pages, ...row.pages])].sort(); x.trees = [...new Set([...x.trees, ...row.trees])].sort(); x.uses = [...new Set([...x.uses, ...row.uses])].sort(); x.elements = [...new Set([...x.elements, ...row.elements])].sort(); }
  }
  const byClass = {};
  for (const cls of CLASSES) {
    const ps = pages.filter((p) => p.class === cls), sr = staticRows.filter((r) => r.classes.includes(cls)), dr = dynamicRows.filter((r) => r.classes.includes(cls)), xr = domMissingRows.filter((r) => r.classes.includes(cls)), mr = [...merged.values()].filter((r) => r.classes.includes(cls));
    byClass[cls] = { pages: 1, static_placeholder_unique: sr.length, static_placeholder_references: sr.reduce((n, r) => n + (r.references_by_class[cls] || 0), 0), dynamic_error_unique: dr.length, dynamic_error_references: dr.reduce((n, r) => n + (r.references_by_class[cls] || 0), 0), dom_local_missing_unique: xr.length, dom_local_missing_references: xr.reduce((n, r) => n + (r.references_by_class[cls] || 0), 0), merged_missing_unique: mr.length, page_errors: ps.reduce((n, p) => n + p.pageErrors.length, 0), console_errors: ps.reduce((n, p) => n + p.consoleErrors.length, 0), failed_local_requests: ps.reduce((n, p) => n + p.failedRequests.length, 0), blocked_external: ps.reduce((n, p) => n + p.blockedExternal.length, 0) };
  }
  const normal = refs.filter((r) => r.classification === "observed_dom_image" && r.local?.exists);
  return { references: refs.length, staticRows, dynamicRows, domMissingRows, mergedRows: [...merged.values()], normalReferences: normal.length, normalUniqueObserved: new Set(normal.map((r) => r.observed_url)).size, byClass };
}
async function main() {
  fs.mkdirSync(OUT, { recursive: true }); const routeMap = readJson(ROUTE_MAP_PATH), provenance = readJson(PROVENANCE_PATH), provenanceByRoute = {};
  for (const entry of provenance.files || []) if (entry && typeof entry.route === "string") (provenanceByRoute[entry.route] ||= []).push(entry);
  const browser = await chromium.launch({ headless: true, executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", args: ["--no-sandbox"] }); const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, serviceWorkers: "block" });
  await context.route("**/*", async (route) => { const url = route.request().url(); if (isLoopback(url) || url.startsWith("about:") || url.startsWith("data:") || url.startsWith("blob:")) await route.continue(); else await route.abort(); });
  const pages = []; for (const cls of CLASSES) pages.push(await auditPage(context, cls, routeMap, provenanceByRoute)); await browser.close();
  const aggregateResult = aggregate(pages), generated = new Date().toISOString(); const receipt = { schema: "talent-full-image-scope/v1", generatedUtc: generated, scope: { server: BASE, export_root: path.relative(ROOT, EXPORT_ROOT).replaceAll(path.sep, "/"), route_map: path.relative(ROOT, ROUTE_MAP_PATH).replaceAll(path.sep, "/"), provenance: path.relative(ROOT, PROVENANCE_PATH).replaceAll(path.sep, "/"), network_used: false, non_loopback_requests_aborted: true, interactions: "none; no clicks or calculator edits", classes: CLASSES }, input_sizes: { route_map_bytes: fs.statSync(ROUTE_MAP_PATH).size, provenance_bytes: fs.statSync(PROVENANCE_PATH).size }, pages, aggregate: aggregateResult };
  fs.writeFileSync(path.join(OUT, "browser-scope-receipt.json"), JSON.stringify(receipt, null, 2) + "\n", "utf8"); fs.writeFileSync(path.join(OUT, "missing-targets.json"), JSON.stringify({ schema: "talent-full-image-scope/missing-v1", generatedUtc: generated, static_placeholder_targets: aggregateResult.staticRows, dynamic_error_targets: aggregateResult.dynamicRows, dom_local_missing_targets: aggregateResult.domMissingRows, merged_missing_targets: aggregateResult.mergedRows, by_class: aggregateResult.byClass }, null, 2) + "\n", "utf8");
  const csvRows = aggregateResult.staticRows.map((r) => ({ ...r, class: r.classes, classification: "static_placeholder" })).concat(aggregateResult.dynamicRows.map((r) => ({ ...r, class: r.classes, classification: r.classification })), aggregateResult.domMissingRows.map((r) => ({ ...r, class: r.classes, classification: "dom_local_missing" }))).sort((a, b) => `${a.classification}:${a.target}`.localeCompare(`${b.classification}:${b.target}`)); fs.writeFileSync(path.join(OUT, "missing-targets.csv"), makeCsv(csvRows), "utf8");
  const lines = [`# Talent full image scope (v42)`, ``, `Generated: ${generated}`, ``, `This is a read-only initial DOM/response audit of the nine v42 talent pages at ${BASE}. No calculator controls were clicked, no points were changed, and all non-loopback requests were aborted.`, ``, `## Counts`, ``, `- DOM image/background references observed: ${aggregateResult.references}; normal non-placeholder references: ${aggregateResult.normalReferences}; unique normal DOM URLs: ${aggregateResult.normalUniqueObserved}.`, `- Static placeholder targets (decoded missing-image.svg requested): ${aggregateResult.staticRows.length} unique / ${aggregateResult.staticRows.reduce((n, r) => n + r.references, 0)} references.`, `- Dynamic image HTTP/request errors: ${aggregateResult.dynamicRows.length} unique / ${aggregateResult.dynamicRows.reduce((n, r) => n + r.references, 0)} references.`, `- DOM-observed image/background targets with no v42 local file and no image error response: ${aggregateResult.domMissingRows.length} unique / ${aggregateResult.domMissingRows.reduce((n, r) => n + r.references, 0)} references.`, `- Merged missing targets (placeholder + dynamic error + DOM-only local-missing): ${aggregateResult.mergedRows.length} unique.`, ``, `| class | static unique/refs | dynamic unique/refs | DOM-only local-missing unique/refs | merged unique | page errors | failed local requests | blocked external |`, `|---|---:|---:|---:|---:|---:|---:|---:|`, ...CLASSES.map((cls) => { const x = aggregateResult.byClass[cls]; return `| ${cls} | ${x.static_placeholder_unique}/${x.static_placeholder_references} | ${x.dynamic_error_unique}/${x.dynamic_error_references} | ${x.dom_local_missing_unique}/${x.dom_local_missing_references} | ${x.merged_missing_unique} | ${x.page_errors} | ${x.failed_local_requests} | ${x.blocked_external} |`; }), ``, `## Classification and limits`, ``, `Static placeholders are based on the actual DOM URL ending in __offline/missing-image.svg and the decoded requested query value. Dynamic errors are image-like local responses >=400 or failed image requests observed by Playwright. DOM-only local-missing targets are actual computed/inline image URLs with no v42 file and no corresponding image error response (for example tree backgrounds on hidden rows). Repeated references are retained in the receipt and counted separately from unique targets in missing-targets.json/csv.`, ``, `Local correspondence uses only the v42 export root, route-map.json, and export-provenance.json. A local file existing or a route returning a placeholder is not counted as the requested image being available.`, ``, `Uncovered: hover/state-generated talent images were not activated; stylesheet-only URLs not present in computed/inline background values are outside this DOM pass; no source, route, module, or production file was changed.`]; fs.writeFileSync(path.join(OUT, "README.md"), lines.join("\n") + "\n", "utf8");
  process.stdout.write(JSON.stringify({ pages: pages.length, references: aggregateResult.references, static_unique: aggregateResult.staticRows.length, dynamic_unique: aggregateResult.dynamicRows.length, merged_unique: aggregateResult.mergedRows.length, dom_local_missing_unique: aggregateResult.domMissingRows.length, page_errors: pages.reduce((n, p) => n + p.pageErrors.length, 0), failed_local: pages.reduce((n, p) => n + p.failedRequests.length, 0), blocked_external: pages.reduce((n, p) => n + p.blockedExternal.length, 0), outputs: ["browser-scope-receipt.json", "missing-targets.json", "missing-targets.csv", "README.md"] }) + "\n");
}
main().catch((error) => { console.error(error && error.stack || error); process.exitCode = 1; });








