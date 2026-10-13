"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const ROOT = "https://vvcchh0.github.io";
const PREFIX = "/WOW-Encyclopedia-Deployable-Archive/";
const HOME = `${ROOT}${PREFIX}`;
const ENCYCLOPEDIA = `${HOME}info/encyclopedia/index.xml.html`;
const ELUNE = `${HOME}info/encyclopedia/392.xml.html`;
const OUTPUT_DIR = __dirname;
const REPORT_PATH = path.join(OUTPUT_DIR, "online-browser-validation.json");
const SCREENSHOTS = {
  homepage: path.join(OUTPUT_DIR, "online-browser-homepage.png"),
  encyclopedia: path.join(OUTPUT_DIR, "online-browser-encyclopedia.png"),
};
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PROXY = "http://127.0.0.1:7890";
const COMMAND = `C:\\nvm4w\\nodejs\\node.exe research/github-pages-20261013/online-browser-smoke.js`;

function uniquePush(list, value) {
  const key = JSON.stringify(value);
  if (!list.some((item) => JSON.stringify(item) === key)) list.push(value);
}

function isSiteUrl(raw) {
  try { return new URL(raw).origin === ROOT; } catch (_) { return false; }
}

function isPrefixEscape(raw) {
  try {
    const url = new URL(raw);
    return url.origin === ROOT && !url.pathname.startsWith(PREFIX);
  } catch (_) { return false; }
}

function isArchiveUrl(raw) {
  try {
    const url = new URL(raw);
    const candidate = `${url.hostname}${url.pathname}${url.search}`;
    return /archive\.org/i.test(url.hostname) || /wayback/i.test(candidate) || /\/archive(?:[/?#]|$)/i.test(url.pathname);
  } catch (_) { return /archive\.org|wayback/i.test(String(raw)); }
}

function rel(file) { return path.relative(path.resolve(__dirname, "../.."), file).replaceAll("\\", "/"); }

async function waitStartup(page, label, report) {
  const wait = { label, started_utc: new Date().toISOString(), domcontentloaded: false, load: false, wowpages_present: false, wowpages_ready_property: false, wowpages_ready: false, wowpages_load_property: false, wowpages_load: false, timeout_or_error: null };
  try {
    await page.waitForLoadState("domcontentloaded", { timeout: 30000 });
    wait.domcontentloaded = true;
  } catch (error) {
    wait.timeout_or_error = `domcontentloaded: ${String(error?.message || error)}`;
  }
  try {
    await page.waitForLoadState("load", { timeout: 30000 });
    wait.load = true;
  } catch (error) {
    wait.timeout_or_error = `${wait.timeout_or_error ? `${wait.timeout_or_error}; ` : ""}load: ${String(error?.message || error)}`;
  }
  try {
    const runtime = await page.evaluate(async () => {
      const api = window.__WOWPages;
      const result = { present: Boolean(api), ready_property: false, ready: false, load_property: false, load: false };
      if (!api) return result;
      result.ready_property = Object.prototype.hasOwnProperty.call(api, "ready");
      if (api.ready && typeof api.ready.then === "function") await api.ready;
      result.ready = Boolean(api.ready);
      result.load_property = Object.prototype.hasOwnProperty.call(api, "load");
      if (api.load && typeof api.load.then === "function") await api.load;
      result.load = Boolean(api.load);
      return result;
    });
    wait.wowpages_present = runtime.present;
    wait.wowpages_ready_property = runtime.ready_property;
    wait.wowpages_ready = runtime.ready;
    wait.wowpages_load_property = runtime.load_property;
    wait.wowpages_load = runtime.load;
  } catch (error) {
    wait.timeout_or_error = `${wait.timeout_or_error ? `${wait.timeout_or_error}; ` : ""}__WOWPages.ready/load: ${String(error?.message || error)}`;
  }
  wait.finished_utc = new Date().toISOString();
  report.startup_waits.push(wait);
  return wait;
}

async function readDom(page) {
  return page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const top = document.getElementById("TopLevel");
    const menu = document.getElementById("minimizerText");
    const factions = document.getElementById("FactionsMenuGroup");
    const factionToggler = document.getElementById("FactionsToggler");
    const search = document.getElementById("searchBox");
    const searchType = document.getElementById("searchType");
    return {
      content_type: document.contentType || null,
      root_node: root?.nodeName || null,
      html_dom: root?.nodeName?.toLowerCase() === "html" && Boolean(body),
      body_present: Boolean(body),
      title: document.title || null,
      heading: document.querySelector("#headLine")?.textContent?.trim() || null,
      body_text_length: body?.innerText?.length || 0,
      top_level_present: Boolean(top),
      menu_toggle_present: Boolean(menu),
      menu_display: top ? getComputedStyle(top).display : null,
      menu_aria_expanded: menu?.getAttribute("aria-expanded") || null,
      factions_present: Boolean(factions),
      factions_toggler_present: Boolean(factionToggler),
      factions_display: factions ? getComputedStyle(factions).display : null,
      factions_aria_expanded: factionToggler?.getAttribute("aria-expanded") || null,
      search_box_present: Boolean(search),
      search_type_present: Boolean(searchType),
      search_options: searchType ? [...searchType.options].map((option) => ({ value: option.value, text: option.textContent.trim() })) : [],
      menu_links: document.querySelectorAll("#TopLevel a[href]").length,
      broken_images: [...document.images]
        .filter((image) => image.complete && image.naturalWidth === 0)
        .map((image) => ({ src: image.currentSrc || image.src, alt: image.alt || "" })),
    };
  });
}

async function main() {
  const started = Date.now();
  const report = {
    schema: "github-pages-online-browser-smoke/v1",
    started_utc: new Date().toISOString(),
    command: COMMAND,
    target_commit: "9ee94f1bbcaf3ec819b65b7dcfb4128e3819d443",
    public_urls: { homepage: HOME, encyclopedia: ENCYCLOPEDIA, expected_elune: ELUNE },
    browser: { executable: CHROME, proxy: PROXY, headless: true, viewport: { width: 1920, height: 1080 }, version: null },
    startup_waits: [],
    pages: [],
    interactions: [],
    screenshots: [],
    nonlocal_requests: [],
    prefix_escape_requests: [],
    archive_requests: [],
    resource_failures: [],
    request_failures: [],
    page_errors: [],
    console_errors: [],
    failures: [],
    limitations: [
      "This is a bounded smoke test of the public homepage, encyclopedia page, and Elune title-search result; it does not re-scan the full archive.",
      "Network requests outside the public GitHub Pages origin are recorded and blocked by the fresh browser context.",
      "An explicit SVG missing-image placeholder with HTTP 200 is recorded as a placeholder and is not treated as restoration of the missing source resource.",
    ],
  };
  let browser = null;
  let context = null;
  try {
    browser = await chromium.launch({ executablePath: CHROME, headless: true, proxy: { server: PROXY } });
    report.browser.version = browser.version();
    context = await browser.newContext({ viewport: report.browser.viewport, deviceScaleFactor: 1 });
    await context.route("**/*", async (route) => {
      const request = route.request();
      const url = request.url();
      const details = { url, type: request.resourceType(), method: request.method() };
      if (isArchiveUrl(url)) {
        uniquePush(report.archive_requests, details);
        return route.abort("blockedbyclient");
      }
      if (!isSiteUrl(url)) {
        uniquePush(report.nonlocal_requests, details);
        return route.abort("blockedbyclient");
      }
      if (isPrefixEscape(url)) uniquePush(report.prefix_escape_requests, details);
      return route.continue();
    });
    const page = await context.newPage();
    page.setDefaultNavigationTimeout(30000);
    page.on("pageerror", (error) => {
      report.page_errors.push({ page: page.url(), message: error.message, stack: error.stack || null });
    });
    page.on("console", (message) => {
      if (message.type() === "error") report.console_errors.push({ page: page.url(), text: message.text(), location: message.location() });
    });
    page.on("response", (response) => {
      if (response.status() < 400) return;
      const url = response.url();
      const details = { page: page.url(), url, status: response.status(), type: response.request().resourceType() };
      if (isArchiveUrl(url)) uniquePush(report.archive_requests, details);
      else if (!isSiteUrl(url)) uniquePush(report.nonlocal_requests, details);
      else if (isPrefixEscape(url)) uniquePush(report.prefix_escape_requests, details);
      else uniquePush(report.resource_failures, details);
    });
    page.on("requestfailed", (request) => {
      const url = request.url();
      const details = { page: page.url(), ...request, url, failure: request.failure()?.errorText || null, type: request.resourceType() };
      delete details._initializer;
      if (isArchiveUrl(url)) uniquePush(report.archive_requests, { url, type: request.resourceType(), method: request.method(), failure: request.failure()?.errorText || null });
      else if (!isSiteUrl(url)) uniquePush(report.nonlocal_requests, { url, type: request.resourceType(), method: request.method(), failure: request.failure()?.errorText || null });
      else if (isPrefixEscape(url)) uniquePush(report.prefix_escape_requests, { url, type: request.resourceType(), method: request.method(), failure: request.failure()?.errorText || null });
      else uniquePush(report.request_failures, details);
    });

    async function visit(id, url, screenshotPath) {
      const requestedAt = new Date().toISOString();
      let response = null;
      let wait = null;
      let dom = null;
      try {
        response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
        if (id === "homepage") {
          // The public root is a static meta-refresh alias.  Wait for the
          // canonical HTML document before reading DOM state or taking its
          // screenshot; page.goto may return for the alias response first.
          await page.waitForURL((target) => target.origin === ROOT && /\/index\.xml\.html$/.test(target.pathname), { timeout: 30000 });
        }
        wait = await waitStartup(page, id, report);
        dom = await readDom(page);
        const item = {
          id,
          requested: url,
          requested_utc: requestedAt,
          final_url: page.url(),
          status: response?.status() ?? null,
          mime: response?.headers()["content-type"] || null,
          wait,
          dom,
        };
        report.pages.push(item);
        if (item.status !== 200) report.failures.push({ label: `${id}:status`, details: item });
        if (!dom.html_dom || !dom.body_present || dom.body_text_length === 0) report.failures.push({ label: `${id}:html_dom`, details: item });
        if (id === "homepage" && !/\/index\.xml\.html(?:[?#].*)?$/.test(new URL(item.final_url).pathname)) {
          report.failures.push({ label: "homepage:canonical_target", details: { expected_path_suffix: "/index.xml.html", final_url: item.final_url } });
        }
        if (id === "encyclopedia" && new URL(item.final_url).pathname !== new URL(ENCYCLOPEDIA).pathname) {
          report.failures.push({ label: "encyclopedia:final_url", details: { expected: ENCYCLOPEDIA, final_url: item.final_url } });
        }
        if (screenshotPath && dom.html_dom) {
          await page.screenshot({ path: screenshotPath, fullPage: true });
          report.screenshots.push(rel(screenshotPath));
        }
        return item;
      } catch (error) {
        const item = { id, requested: url, requested_utc: requestedAt, final_url: page.url(), wait, dom, error: String(error?.stack || error) };
        report.pages.push(item);
        report.failures.push({ label: `${id}:exception`, details: item });
        return item;
      }
    }

    await visit("homepage", HOME, SCREENSHOTS.homepage);
    await visit("encyclopedia", ENCYCLOPEDIA, SCREENSHOTS.encyclopedia);

    const encyclopediaPage = report.pages.find((item) => item.id === "encyclopedia");
    if (encyclopediaPage?.dom?.html_dom) {
      const beforeMenu = await readDom(page);
      try {
        await page.locator("#minimizerText").click({ timeout: 3000 });
        const opened = await readDom(page);
        await page.locator("#minimizerText").click({ timeout: 3000 });
        const closed = await readDom(page);
        const passed = beforeMenu.menu_display !== opened.menu_display && opened.menu_display !== closed.menu_display;
        report.interactions.push({ label: "menu open and close", passed, before: { display: beforeMenu.menu_display, aria_expanded: beforeMenu.menu_aria_expanded }, opened: { display: opened.menu_display, aria_expanded: opened.menu_aria_expanded }, closed: { display: closed.menu_display, aria_expanded: closed.menu_aria_expanded } });
        if (!passed) report.failures.push({ label: "menu_toggle", details: report.interactions.at(-1) });
      } catch (error) {
        report.interactions.push({ label: "menu open and close", passed: false, error: String(error?.stack || error) });
        report.failures.push({ label: "menu_toggle_exception", details: report.interactions.at(-1) });
      }

      try {
        const menuBeforeFactions = await readDom(page);
        if (menuBeforeFactions.menu_display === "none") await page.locator("#minimizerText").click({ timeout: 3000 });
        const before = await page.locator("#FactionsMenuGroup").evaluate((element) => ({ display: getComputedStyle(element).display, aria_expanded: document.getElementById("FactionsToggler")?.getAttribute("aria-expanded") || null }));
        await page.locator("#FactionsToggler").click({ timeout: 3000 });
        const expanded = await page.locator("#FactionsMenuGroup").evaluate((element) => ({ display: getComputedStyle(element).display, aria_expanded: document.getElementById("FactionsToggler")?.getAttribute("aria-expanded") || null }));
        const passed = before.display !== expanded.display && expanded.display !== "none";
        report.interactions.push({ label: "Factions expand", passed, before, expanded });
        if (!passed) report.failures.push({ label: "factions_toggle", details: report.interactions.at(-1) });
      } catch (error) {
        report.interactions.push({ label: "Factions expand", passed: false, error: String(error?.stack || error) });
        report.failures.push({ label: "factions_toggle_exception", details: report.interactions.at(-1) });
      }

      try {
        await page.locator("#searchBox").fill("Elune");
        await page.locator("#searchType").selectOption("encyclopedia");
        const navigation = page.waitForURL((target) => target.origin === ROOT && target.pathname === new URL(ELUNE).pathname, { timeout: 30000 });
        await page.locator(".searchBoxButton a").click({ timeout: 3000 });
        await navigation;
        const wait = await waitStartup(page, "elune-search-result", report);
        const dom = await readDom(page);
        const passed = page.url() === ELUNE && dom.html_dom && /elune/i.test(`${dom.title || ""} ${dom.heading || ""} ${documentText(dom)}`);
        const details = { passed, url: page.url(), expected_url: ELUNE, wait, dom: { title: dom.title, heading: dom.heading, html_dom: dom.html_dom } };
        report.interactions.push({ label: "Elune title search to 392.xml.html", ...details });
        if (!passed) report.failures.push({ label: "elune_search", details });
      } catch (error) {
        report.interactions.push({ label: "Elune title search to 392.xml.html", passed: false, error: String(error?.stack || error), final_url: page.url() });
        report.failures.push({ label: "elune_search_exception", details: report.interactions.at(-1) });
      }
    } else {
      report.interactions.push({ label: "encyclopedia interactions", passed: false, skipped: true, reason: "encyclopedia did not produce an HTML DOM" });
    }
  } catch (error) {
    report.failures.push({ label: "browser_harness_exception", details: String(error?.stack || error) });
  } finally {
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    report.finished_utc = new Date().toISOString();
    report.duration_ms = Date.now() - started;
    report.accepted = report.failures.length === 0 && report.nonlocal_requests.length === 0 && report.prefix_escape_requests.length === 0 && report.archive_requests.length === 0 && report.resource_failures.length === 0 && report.request_failures.length === 0 && report.page_errors.length === 0 && report.console_errors.length === 0 && report.pages.length === 2 && report.interactions.length === 3;
    report.summary = {
      accepted: report.accepted,
      pages: report.pages.length,
      interactions: report.interactions.length,
      screenshots: report.screenshots.length,
      nonlocal_requests: report.nonlocal_requests.length,
      prefix_escape_requests: report.prefix_escape_requests.length,
      archive_requests: report.archive_requests.length,
      resource_failures: report.resource_failures.length,
      request_failures: report.request_failures.length,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      failures: report.failures.length,
    };
    fs.writeFileSync(REPORT_PATH, `${JSON.stringify(report, null, 2)}\n`, "utf8");
    console.log(JSON.stringify(report.summary, null, 2));
  }
  if (!report.accepted) process.exitCode = 1;
}

function documentText(dom) { return `${dom.title || ""} ${dom.heading || ""}`; }

main();
