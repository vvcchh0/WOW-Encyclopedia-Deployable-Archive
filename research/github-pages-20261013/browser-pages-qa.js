// Static GitHub Pages preview QA.  This harness uses the export route map,
// visits a plain static server, and never starts offline_mirror or fetches the
// network.  Source XML routes may therefore resolve to concrete *.xml.html
// files while genuine manifest kind=xml records are tested as raw XML.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { chromium } = require("C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const root = path.resolve(__dirname, "../..");
const output = process.env.PAGES_QA_OUTPUT || path.join(__dirname, "browser-pages-qa");
const defaultPreview = fs.existsSync(path.join(root, ".scratch/pages-preview-final/__offline/route-map.json"))
  ? path.join(root, ".scratch/pages-preview-final")
  : path.join(root, ".scratch/pages-preview");
const previewDir = path.resolve(process.env.PAGES_PREVIEW_DIR || defaultPreview);
const routeMapPath = path.resolve(process.env.PAGES_ROUTE_MAP || path.join(previewDir, "__offline/route-map.json"));
const manifestPath = path.resolve(process.env.PAGES_MANIFEST || path.join(root, "offline/build-manifest.json"));
const baseInput = process.env.PAGES_PREVIEW_BASE || "http://127.0.0.1:8879/";

const representatives = [
  // The root alias is a meta-refresh stub.  The canonical homepage is the
  // concrete /index.xml -> /index.xml.html export; the root alias is checked
  // separately by the Pages 404/runtime probe below.
  { id: "homepage", route: "/index.xml", expected: "html" },
  { id: "encyclopedia", route: "/info/encyclopedia/index.xml", expected: "html" },
  { id: "elune", route: "/info/encyclopedia/392.xml", expected: "html" },
  { id: "gameguide", route: "/info/basics/auctionhouses.html", expected: "html" },
  { id: "media", route: "/community/machinima/index.html", expected: "html" },
  { id: "current_news", route: "/news/wow-news-01-2006.html", expected: "html" },
  { id: "cascade_js", route: "/info/encyclopedia/scripts/cascade.js", expected: "js" },
];

function sha256File(file) { return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"); }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function normPrefix(value) {
  let out = String(value || "/");
  if (!out.startsWith("/")) out = `/${out}`;
  if (!out.endsWith("/")) out += "/";
  return out.replace(/\/{2,}/g, "/");
}
function normRoute(value) {
  let out = String(value || "/");
  if (!out.startsWith("/")) out = `/${out}`;
  out = out.replace(/\/+/g, "/");
  return out.length > 1 ? out.replace(/\/$/, "") : "/";
}
function unique(list, value) {
  const key = JSON.stringify(value);
  if (!list.some((item) => JSON.stringify(item) === key)) list.push(value);
}
function recordFor(files, route) {
  const wanted = normRoute(route);
  return files.find((item) => normRoute(item.route || "") === wanted) || null;
}
function writeReport(report) {
  fs.mkdirSync(output, { recursive: true });
  const file = path.join(output, "browser-validation.json");
  fs.writeFileSync(file, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  return file;
}

function configFor(routeMap, manifest) {
  const input = new URL(baseInput.endsWith("/") ? baseInput : `${baseInput}/`);
  const origin = input.origin;
  const prefix = normPrefix(routeMap.base_path || input.pathname);
  const base = new URL(prefix.replace(/^\/+/, ""), `${origin}/`);
  const routes = routeMap.routes || {};
  const aliases = routeMap.aliases || {};
  const resolve = (logical) => {
    const route = normRoute(logical);
    const keys = [route, route.endsWith("/") ? route.slice(0, -1) : `${route}/`];
    let mapped = null;
    let mapKind = null;
    for (const key of keys) {
      if (typeof routes[key] === "string") { mapped = routes[key]; mapKind = "routes"; break; }
      if (typeof aliases[key] === "string") { mapped = aliases[key]; mapKind = "aliases"; break; }
    }
    const actual = new URL(mapped || `${prefix}${route.replace(/^\/+/, "")}`, origin).href;
    return {
      logical: route,
      actual,
      static_path: new URL(actual).pathname,
      mapped: Boolean(mapped),
      map_kind: mapKind,
      manifest: recordFor(manifest.files || [], route),
    };
  };
  return { routeMap, manifest, origin, prefix, base, resolve };
}

async function domState(page) {
  return page.evaluate(() => {
    const rootNode = document.documentElement;
    const body = document.body;
    const top = document.getElementById("TopLevel");
    return {
      content_type: document.contentType,
      root_node: rootNode?.nodeName || null,
      html_dom: Boolean(body) && rootNode?.nodeName?.toLowerCase() === "html",
      title: document.title || null,
      heading: document.querySelector("#headLine")?.textContent?.trim() || null,
      body_text_length: body?.innerText?.length || 0,
      menu_links: document.querySelectorAll("#TopLevel a[href]").length,
      menu_display: top ? getComputedStyle(top).display : null,
      broken_images: [...document.images].filter((image) => image.complete && image.naturalWidth === 0)
        .map((image) => ({ src: image.src, alt: image.alt })),
    };
  });
}

async function interaction(report, label, action) {
  try {
    const details = await action();
    report.interactions.push({ label, passed: true, details });
    return details;
  } catch (error) {
    report.interactions.push({ label, passed: false, error: String(error?.stack || error) });
    return null;
  }
}

async function main() {
  const report = {
    schema: "github-pages-browser-qa/v2",
    started_utc: new Date().toISOString(),
    preview_dir: path.relative(root, previewDir).replaceAll("\\", "/"),
    route_map_path: path.relative(root, routeMapPath).replaceAll("\\", "/"),
    manifest_path: path.relative(root, manifestPath).replaceAll("\\", "/"),
    server_contract: "plain static server; no offline_mirror backend",
    ready: false,
    route_map_sha256: null,
    manifest_sha256: null,
    base: null,
    origin: null,
    project_prefix: null,
    route_resolution: [],
    xml_probes: [],
    root_alias: null,
    pages: [],
    interactions: [],
    legacy_xml_entry: null,
    missing_image_natural_size: null,
    forms: null,
    form_scope_check: null,
    screenshots: [],
    browser_version: null,
    console_errors: [],
    page_errors: [],
    resource_failures: [],
    expected_failures: [],
    nonlocal_requests: [],
    prefix_escape_requests: [],
    failures: [],
  };
  let browser;
  let cfg;
  try {
    if (!fs.existsSync(routeMapPath)) throw new Error(`route map is not ready: ${routeMapPath}`);
    if (!fs.existsSync(manifestPath)) throw new Error(`manifest is missing: ${manifestPath}`);
    report.route_map_sha256 = sha256File(routeMapPath);
    report.manifest_sha256 = sha256File(manifestPath);
    cfg = configFor(readJson(routeMapPath), readJson(manifestPath));
    report.ready = true;
    report.base = cfg.base.href;
    report.origin = cfg.origin;
    report.project_prefix = cfg.prefix;

    const specs = representatives.map((spec) => {
      const resolved = cfg.resolve(spec.route);
      const item = { ...spec, ...resolved, manifest_kind: resolved.manifest?.kind || null };
      report.route_resolution.push(item);
      return item;
    });
    const xmlRecords = (cfg.manifest.files || []).filter((item) => item.kind === "xml").slice(0, 4);
    for (const record of xmlRecords) {
      const resolved = cfg.resolve(record.route);
      report.xml_probes.push({ route: record.route, manifest_kind: record.kind, manifest_mime: record.mime || null, role: record.role || null, ...resolved });
    }
    if (report.xml_probes.length !== 4) report.failures.push({ label: "manifest_xml_probe_count", details: { expected: 4, actual: report.xml_probes.length } });

    const isLocal = (url) => { try { return new URL(url).origin === cfg.origin; } catch (_) { return false; } };
    const escapes = (url) => isLocal(url) && cfg.prefix !== "/" && !new URL(url).pathname.startsWith(cfg.prefix);
    const legacyUrl = new URL(`${cfg.prefix}info/encyclopedia/index.xml`, cfg.origin).href;

    browser = await chromium.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: true });
    report.browser_version = browser.version();
    const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    await context.route("**/*", async (route) => {
      const url = route.request().url();
      if (/^(data:|blob:|about:)/.test(url)) return route.continue();
      if (!isLocal(url)) {
        unique(report.nonlocal_requests, { url, type: route.request().resourceType() });
        return route.abort("blockedbyclient");
      }
      if (escapes(url)) unique(report.prefix_escape_requests, { url, type: route.request().resourceType() });
      return route.continue();
    });
    const page = await context.newPage();
    page.setDefaultNavigationTimeout(30000);
    let legacyCheckActive = false;
    page.on("console", (message) => {
      if (message.type() !== "error") return;
      const item = { page: page.url(), text: message.text() };
      if (legacyCheckActive && /failed to load resource/i.test(item.text)) report.expected_failures.push({ kind: "legacy_xml_console", ...item });
      else report.console_errors.push(item);
    });
    page.on("pageerror", (error) => report.page_errors.push({ page: page.url(), message: error.message, stack: error.stack }));
    page.on("response", (response) => {
      if (response.status() >= 400) {
        const item = { page: page.url(), url: response.url(), status: response.status(), type: response.request().resourceType() };
        if (response.url() === legacyUrl && response.status() === 404) report.expected_failures.push({ ...item, reason: "legacy_xml_entry" });
        else report.resource_failures.push(item);
      }
    });
    page.on("requestfailed", (request) => {
      if (request.url() !== legacyUrl) report.resource_failures.push({ page: page.url(), url: request.url(), failure: request.failure()?.errorText || null, type: request.resourceType() });
    });

    // Check the generated root alias without putting its meta-refresh
    // navigation into the page navigation queue used by the route checks.
    try {
      const rootAliasUrl = cfg.resolve("/").actual;
      const rootAliasResponse = await context.request.get(rootAliasUrl, { timeout: 30000 });
      const rootAliasBody = await rootAliasResponse.text();
      report.root_alias = { requested: rootAliasUrl, status: rootAliasResponse.status(), mime: rootAliasResponse.headers()["content-type"] || null, contains_canonical_target: /index\.xml\.html/i.test(rootAliasBody) };
      if (rootAliasResponse.status() !== 200 || !report.root_alias.contains_canonical_target) report.failures.push({ label: "root_alias", details: report.root_alias });
    } catch (error) {
      report.root_alias = { error: String(error?.stack || error) };
      report.failures.push({ label: "root_alias_exception", details: report.root_alias });
    }

    const visit = async (spec, screenshot = false) => {
      let response;
      let entry;
      try {
        response = await page.goto(spec.actual, { waitUntil: "domcontentloaded", timeout: 30000 });
        // The root alias is a real static meta-refresh page.  Give the
        // browser one turn to finish that navigation before inspecting DOM.
        await page.waitForTimeout(spec.id === "homepage" ? 400 : 80);
        const dom = await domState(page);
        const mime = response?.headers()["content-type"] || null;
        entry = { id: spec.id || `xml:${spec.route}`, logical_route: spec.route, requested: spec.actual, final_url: page.url(), status: response?.status() ?? null, mime, mapped: spec.mapped, map_kind: spec.map_kind, manifest_kind: spec.manifest_kind || spec.manifest?.kind || spec.expected || null, ...dom };
        if (entry.status !== 200) report.failures.push({ label: "route_status", details: entry });
        if (spec.expected === "html" && !/^text\/html\b/i.test(mime || "")) report.failures.push({ label: "html_mime", details: entry });
        if (spec.expected === "js" && !/(?:javascript|ecmascript)\b/i.test(mime || "")) report.failures.push({ label: "js_mime", details: entry });
        if (screenshot && dom.html_dom) {
          const shot = path.join(output, `${spec.id}.png`);
          fs.mkdirSync(output, { recursive: true });
          await page.screenshot({ path: shot, fullPage: true });
          report.screenshots.push(path.relative(root, shot).replaceAll("\\", "/"));
        }
      } catch (error) {
        entry = { id: spec.id || `xml:${spec.route}`, logical_route: spec.route, requested: spec.actual, error: String(error?.stack || error) };
        report.failures.push({ label: "route_exception", details: entry });
      }
      report.pages.push(entry);
      return entry;
    };

    for (const spec of specs) await visit(spec, spec.id === "homepage" || spec.id === "encyclopedia");
    for (const probe of report.xml_probes) {
      const entry = await visit({ id: `xml:${probe.route}`, route: probe.route, actual: probe.actual, mapped: probe.mapped, map_kind: probe.map_kind, manifest: probe.manifest, manifest_kind: "xml", expected: "xml" });
      entry.expected_manifest_mime = probe.manifest_mime;
      const expectedType = String(probe.manifest_mime || "").split(";")[0];
      // A plain static server may report either XML registration used by the
      // source manifest (application/xml) or its standard text/xml alias.
      // Both are XML MIME types and keep the raw XML probe distinct from the
      // transformed *.xml.html article pages.
      if (entry.status === 200 && expectedType && !/^(?:application|text)\/xml\b/i.test(entry.mime || "")) report.failures.push({ label: "manifest_xml_mime", details: { probe, entry } });
    }

    try {
      legacyCheckActive = true;
      const response = await page.goto(legacyUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.waitForTimeout(500);
      const body = await page.locator("body").innerText().catch(() => "");
      const mappedLegacy = cfg.resolve("/info/encyclopedia/index.xml").actual;
      report.legacy_xml_entry = { requested: legacyUrl, initial_status: response?.status() ?? null, initial_mime: response?.headers()["content-type"] || null, final_url: page.url(), mapped_target: mappedLegacy, runtime_resolved: page.url() === mappedLegacy, body_prefix: body.slice(0, 240) };
      if (response?.status() !== 404) report.failures.push({ label: "legacy_xml_entry_status", details: report.legacy_xml_entry });
      if (page.url() !== mappedLegacy) report.failures.push({ label: "legacy_xml_runtime_mapping", details: report.legacy_xml_entry });
    } catch (error) {
      report.legacy_xml_entry = { requested: legacyUrl, error: String(error?.stack || error) };
      report.failures.push({ label: "legacy_xml_entry_exception", details: report.legacy_xml_entry });
    } finally {
      legacyCheckActive = false;
    }

    const encyclopedia = specs.find((spec) => spec.id === "encyclopedia");
    if (encyclopedia) await page.goto(encyclopedia.actual, { waitUntil: "domcontentloaded", timeout: 30000 });
    if (!(await domState(page)).html_dom) {
      report.interactions.push({ label: "menu/search", passed: false, skipped: true, reason: "mapped encyclopedia route was not an HTML DOM" });
    } else {
      await interaction(report, "menu toggle", async () => {
        const before = await domState(page);
        await page.locator("#minimizerText").click({ timeout: 3000 });
        const after = await domState(page);
        if (before.menu_display === after.menu_display) throw new Error(`menu display did not change: ${before.menu_display}`);
        return { before_display: before.menu_display, after_display: after.menu_display, menu_links: after.menu_links };
      });
      await interaction(report, "Factions category toggle", async () => {
        const group = page.locator('[id="FactionsMenuGroup"]');
        const before = await group.evaluate((el) => getComputedStyle(el).display);
        await page.locator('[id="FactionsToggler"]').click({ timeout: 3000 });
        const after = await group.evaluate((el) => getComputedStyle(el).display);
        if (before === after) throw new Error(`Factions display did not change: ${before}`);
        return { before, after };
      });
      await interaction(report, "Elune title search", async () => {
        await page.locator("#searchBox").fill("Elune");
        await page.locator("#searchType").selectOption("encyclopedia");
        await page.locator(".searchBoxButton a").click({ timeout: 3000 });
        await page.waitForTimeout(250);
        const state = await domState(page);
        const text = await page.locator("body").innerText();
        if (!isLocal(page.url()) || escapes(page.url())) throw new Error(`title search escaped project prefix: ${page.url()}`);
        if (!/elune|392/i.test(`${page.url()} ${state.title || ""} ${state.heading || ""} ${text}`)) throw new Error(`title search did not reach Elune content: ${page.url()}`);
        return { url: page.url(), title: state.title, heading: state.heading };
      });
      await page.goto(encyclopedia.actual, { waitUntil: "domcontentloaded", timeout: 30000 });
      await interaction(report, "full-site search uncollected route", async () => {
        const options = await page.locator("#searchType option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent.trim() })));
        const site = options.find((item) => !/encyclopedia/i.test(`${item.value} ${item.text}`));
        if (!site) throw new Error(`no full-site search option: ${JSON.stringify(options)}`);
        await page.locator("#searchBox").fill("offline-qa-uncollected-route");
        await page.locator("#searchType").selectOption(site.value);
        await page.locator(".searchBoxButton a").click({ timeout: 3000 });
        await page.waitForTimeout(250);
        const state = await domState(page);
        const text = await page.locator("body").innerText();
        if (!isLocal(page.url()) || escapes(page.url())) throw new Error(`full-site search escaped project prefix: ${page.url()}`);
        if (!/__offline\/uncollected|not collected|uncollected/i.test(`${page.url()} ${state.title || ""} ${text}`)) throw new Error(`full-site search did not produce local missing notice: ${page.url()}`);
        return { url: page.url(), title: state.title, option: site, body_prefix: text.slice(0, 240) };
      });
      await page.goto(encyclopedia.actual, { waitUntil: "domcontentloaded", timeout: 30000 });
    }

    const missing = cfg.resolve("/info/encyclopedia/315.xml");
    try {
      await page.goto(missing.actual, { waitUntil: "domcontentloaded", timeout: 30000 });
      report.missing_image_natural_size = await page.evaluate(() => [...document.images].filter((image) => /missing-image|placeholder/i.test(image.src)).map((image) => ({ src: image.src, complete: image.complete, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight, alt: image.alt })));
      if (report.missing_image_natural_size.some((image) => image.naturalWidth <= 0 || image.naturalHeight <= 0)) report.failures.push({ label: "missing_image_natural_size", details: report.missing_image_natural_size });
    } catch (error) { report.missing_image_natural_size = { skipped: true, error: String(error?.stack || error) }; }

    await page.goto(encyclopedia.actual, { waitUntil: "domcontentloaded", timeout: 30000 });
    report.forms = await page.evaluate(() => [...document.forms].map((form) => {
      const controls = [...form.elements].map((element) => ({ tag: element.tagName, type: element.type || null, name: element.name || null, disabled: Boolean(element.disabled) }));
      return { action: form.action || null, method: form.method || null, controls, all_controls_disabled: controls.length > 0 && controls.every((item) => item.disabled) };
    }));
    const unsafeForms = report.forms.filter((form) => {
      try { const url = new URL(form.action || page.url()); return url.origin !== cfg.origin || escapes(url.href); } catch (_) { return true; }
    });
    report.form_scope_check = { unsafe_form_count: unsafeForms.length, unsafe_forms: unsafeForms, passed: unsafeForms.every((form) => form.all_controls_disabled) };
    if (!report.form_scope_check.passed) report.failures.push({ label: "form_scope", details: report.form_scope_check });
  } catch (error) {
    report.failures.push({ label: "browser_harness_exception", details: String(error?.stack || error) });
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    const expected = new Set(report.expected_failures.map((item) => `${item.url}|${item.status}`));
    const actualFailures = report.resource_failures.filter((item) => !expected.has(`${item.url}|${item.status}`));
    report.accepted = report.ready && report.failures.length === 0 && report.nonlocal_requests.length === 0 && report.prefix_escape_requests.length === 0 && report.page_errors.length === 0 && report.console_errors.length === 0 && actualFailures.length === 0;
    report.summary = { accepted: report.accepted, pages: report.pages.length, xml_probes: report.xml_probes.length, interactions: report.interactions.length, screenshots: report.screenshots.length, nonlocal_requests: report.nonlocal_requests.length, prefix_escape_requests: report.prefix_escape_requests.length, page_errors: report.page_errors.length, console_errors: report.console_errors.length, resource_failures: actualFailures.length, expected_failures: report.expected_failures.length, failures: report.failures.length };
    report.output = path.relative(root, writeReport(report)).replaceAll("\\", "/");
  }
  console.log(JSON.stringify(report.summary || { accepted: false, ready: report.ready }, null, 2));
  if (!report.accepted) process.exitCode = 1;
}

main();
