#!/usr/bin/env node
"use strict";

/*
 * One bounded, loopback-only Playwright pass over the frozen v39 export.
 * This is intentionally a read-only browser audit: no DOM is injected and no
 * export/site files are changed.  The four screenshots are taken after
 * scrolling the existing gallery wrapper into view.
 */

const fs = require("fs");
const path = require("path");
const PLAYWRIGHT_DIR = String.raw`C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright`;
const { chromium } = require(PLAYWRIGHT_DIR);

const SCRIPT_DIR = __dirname;
const LOCAL_DIR = path.resolve(SCRIPT_DIR, "..");
const REPO = path.resolve(SCRIPT_DIR, "../../../..");
const PACKAGE_PATH = path.join(LOCAL_DIR, "gallery-accessibility-50.json");
const PROVENANCE_PATH = path.join(REPO, ".scratch/pages-resources-20261020-v39/export-provenance.json");
const OUTPUT_DIR = SCRIPT_DIR;
const SCREENSHOT_DIR = path.join(OUTPUT_DIR, "screenshots");
const DEPLOY_BASE = "/WOW-Encyclopedia-Deployable-Archive";
const PER_PAGE_MS = 8000;
const GLOBAL_MS = 225000;

function parseArgs() {
  const args = process.argv.slice(2);
  let base = null;
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--base") base = args[++i];
    else if (args[i] === "--help" || args[i] === "-h") {
      console.log("Usage: node run_browser_audit.js --base http://127.0.0.1:PORT/WOW-Encyclopedia-Deployable-Archive/");
      process.exit(0);
    }
  }
  if (!base) throw new Error("--base is required");
  if (!base.endsWith("/")) base += "/";
  return { base };
}

function now() {
  return new Date().toISOString();
}

function canonicalPath(value, base) {
  try {
    const parsed = new URL(value, base);
    let pathname = decodeURIComponent(parsed.pathname);
    if (pathname.startsWith(DEPLOY_BASE)) pathname = pathname.slice(DEPLOY_BASE.length) || "/";
    if (!pathname.startsWith("/")) pathname = "/" + pathname;
    return pathname;
  } catch (_) {
    return String(value || "");
  }
}

function isLoopback(urlString) {
  try {
    const u = new URL(urlString);
    return (u.protocol === "http:" || u.protocol === "https:") &&
      (u.hostname === "127.0.0.1" || u.hostname === "localhost" || u.hostname === "::1");
  } catch (_) {
    return false;
  }
}

function capPush(array, value, limit = 100) {
  if (array.length < limit) array.push(value);
}

function loadInputs() {
  const pkg = JSON.parse(fs.readFileSync(PACKAGE_PATH, "utf8"));
  const provenance = JSON.parse(fs.readFileSync(PROVENANCE_PATH, "utf8"));
  if (pkg.rows.length !== 50) throw new Error(`expected 50 static rows, got ${pkg.rows.length}`);
  if (pkg.coverage.expected_target_count !== 3368) throw new Error("static target count is not 3368");
  const guidePreviewRoutes = new Set();
  const guideCollectionRoutes = new Set();
  const guideCollectionGalleryRoutes = new Map();
  const guidePreviewGalleryRoutes = new Map();
  for (const group of (provenance.guide_previews?.groups || [])) {
    const paths = new Set((group.previews || []).map((x) => x.route));
    for (const p of paths) guidePreviewRoutes.add(p);
    guidePreviewGalleryRoutes.set(group.gallery_route, paths);
  }
  for (const group of (provenance.guide_image_collections?.groups || [])) {
    const paths = new Set((group.images || []).map((x) => x.route));
    for (const p of paths) guideCollectionRoutes.add(p);
    guideCollectionGalleryRoutes.set(group.gallery_route, paths);
  }
  return { pkg, provenance, guidePreviewRoutes, guideCollectionRoutes, guideCollectionGalleryRoutes, guidePreviewGalleryRoutes };
}

function expectedNative(row) {
  const full = [];
  const thumb = [];
  for (let i = 1; i <= row.declared_slots; i += 1) {
    full.push(`${row.source_directory}${row.filename_literal}${i}.jpg`);
    thumb.push(`${row.source_directory}${row.filename_literal}${i}-thumb.jpg`);
  }
  return { full, thumb, all: new Set(full.concat(thumb)) };
}

function classifyPath(p, state, inputs) {
  if (state.expectedNative.has(p)) return "native_expected";
  if (state.guidePreviewRoutes.has(p)) return "guide_preview";
  if (state.guideCollectionRoutes.has(p)) return "guide_collection";
  return "other";
}

async function evaluatePage(page, base, state, inputs) {
  return page.evaluate(({ deployBase }) => {
    const clean = (value) => {
      try {
        const u = new URL(value, window.location.href);
        let p = decodeURIComponent(u.pathname);
        if (p.startsWith(deployBase)) p = p.slice(deployBase.length) || "/";
        return p.startsWith("/") ? p : "/" + p;
      } catch (_) {
        return String(value || "");
      }
    };
    const attrs = (node) => {
      const src = node.currentSrc || node.src || node.getAttribute("src") || "";
      let placeholderRequestedRoute = null;
      let placeholderReason = null;
      try {
        const parsed = new URL(src, window.location.href);
        if (parsed.pathname.endsWith("/__offline/missing-image.svg")) {
          const requested = parsed.searchParams.get("requested");
          placeholderRequestedRoute = requested ? clean(requested) : null;
          placeholderReason = parsed.searchParams.get("reason") || null;
        }
      } catch (_) {
        // Keep the raw image observation when a malformed URL is present.
      }
      return {
        src,
        route: clean(src),
        complete: Boolean(node.complete),
        naturalWidth: Number(node.naturalWidth || 0),
        naturalHeight: Number(node.naturalHeight || 0),
        alt: node.getAttribute("alt") || "",
        missingImagePlaceholder: Boolean(placeholderRequestedRoute),
        placeholderRequestedRoute,
        placeholderReason,
      };
    };
    const sectionData = (section) => ({
      id: section.id || null,
      group: section.getAttribute("data-guide-preview-group") || null,
      declaredCount: Number(section.getAttribute("data-guide-preview-count") || 0) || null,
      images: Array.from(section.querySelectorAll("img")).map(attrs),
      anchors: Array.from(section.querySelectorAll("a[href]")).map((a) => clean(a.href)),
    });
    const gallery = document.getElementById("galleryPictures");
    const sections = Array.from(document.querySelectorAll(".offline-guide-preview-section"));
    const shotList = Array.isArray(window.shotList) ? window.shotList.filter((x) => typeof x === "string") : null;
    const galleryImages = gallery ? Array.from(gallery.querySelectorAll("img")).map(attrs) : [];
    const allImages = Array.from(document.images).map(attrs);
    const screenieAnchors = Array.from(document.querySelectorAll("a[rel~='screenie'][href], a[rel*='screenie'][href]"))
      .map((a) => clean(a.href));
    const html = document.documentElement ? document.documentElement.outerHTML : "";
    const placeholderAnchors = Array.from(document.querySelectorAll("a[href*='__offline/missing.html']"))
      .map((a) => a.href);
    const placeholderImages = allImages.filter((x) => x.missingImagePlaceholder);
    const missingImages = allImages.filter((x) => !x.complete || x.naturalWidth === 0);
    const rect = gallery ? gallery.getBoundingClientRect() : null;
    const visibleGalleryImages = galleryImages.filter((x) => x.complete && x.naturalWidth > 0);
    return {
      readyState: document.readyState,
      title: document.title,
      documentUrl: window.location.href,
      numShots: Number.isFinite(Number(window.numShots)) ? Number(window.numShots) : null,
      shotList,
      currentShotNumber: Number.isFinite(Number(window.currentShotNumber)) ? Number(window.currentShotNumber) : null,
      reverseOrder: typeof window.reverseOrder === "boolean" ? window.reverseOrder : null,
      galleryWrapper: gallery ? {
        id: gallery.id,
        className: gallery.className,
        htmlLength: gallery.innerHTML.length,
        imageCount: galleryImages.length,
        visibleImageCount: visibleGalleryImages.length,
        rect: rect ? { top: rect.top, bottom: rect.bottom, width: rect.width, height: rect.height } : null,
      } : null,
      galleryImages,
      guidePreviewSections: sections.map(sectionData),
      guidePreviewImages: sections.flatMap((x) => Array.from(x.querySelectorAll("img")).map(attrs)),
      screenieAnchors,
      allImages,
      missingImages,
      placeholderAnchors,
      placeholderImageCount: placeholderImages.length,
      placeholderImageRequestedRoutes: placeholderImages.map((x) => x.placeholderRequestedRoute),
      htmlPlaceholderReferenceCount: (html.match(/__offline\/missing\.html/g) || []).length,
      scrollY: window.scrollY,
      viewport: { width: window.innerWidth, height: window.innerHeight },
    };
  }, { deployBase: DEPLOY_BASE });
}

async function auditOne(page, base, row, inputs, screenshotName, globalDeadline) {
  const route = row.source_page_route;
  const url = base + route.replace(/^\/+/, "");
  const expected = expectedNative(row);
  const state = {
    label: row.gallery,
    route,
    expectedNative: expected.all,
    guidePreviewRoutes: inputs.guidePreviewRoutes,
    guideCollectionRoutes: inputs.guideCollectionRoutes,
    startedAt: now(),
    responseCount: 0,
    statusCounts: {},
    documentStatus: null,
    documentResponses: [],
    http404s: [],
    imagePlaceholders: [],
    requestFailures: [],
    blockedExternalRequests: [],
    pageErrors: [],
    consoleErrors: [],
    screenshot: null,
    gotoError: null,
  };
  let currentState = state;
  const onResponse = (response) => {
    const status = response.status();
    const resourceType = response.request().resourceType();
    state.responseCount += 1;
    state.statusCounts[String(status)] = (state.statusCounts[String(status)] || 0) + 1;
    if (resourceType === "document") {
      state.documentStatus = status;
      capPush(state.documentResponses, { url: response.url(), status });
    }
    if (resourceType === "image" && canonicalPath(response.url(), base) === "/__offline/missing-image.svg") {
      let requestedRoute = null;
      let reason = null;
      try {
        const parsed = new URL(response.url());
        const requested = parsed.searchParams.get("requested");
        requestedRoute = requested ? canonicalPath(requested, base) : null;
        reason = parsed.searchParams.get("reason") || null;
      } catch (_) {
        // Keep the response even if the fallback query is malformed.
      }
      capPush(state.imagePlaceholders, {
        url: response.url(),
        requestedRoute,
        reason,
        status,
        classification: requestedRoute ? classifyPath(requestedRoute, state, inputs) : "other",
      }, 200);
    }
    if (status === 404) {
      const p = canonicalPath(response.url(), base);
      capPush(state.http404s, { url: response.url(), path: p, status, resourceType, classification: classifyPath(p, state, inputs) });
    }
  };
  const onFailure = (request) => {
    const item = { url: request.url(), resourceType: request.resourceType(), failure: request.failure() };
    if (isLoopback(request.url())) capPush(state.requestFailures, item);
    else capPush(state.blockedExternalRequests, item);
  };
  const onPageError = (error) => capPush(state.pageErrors, String(error && error.stack ? error.stack : error));
  const onConsole = (message) => {
    if (message.type() === "error") capPush(state.consoleErrors, message.text());
  };
  page.on("response", onResponse);
  page.on("requestfailed", onFailure);
  page.on("pageerror", onPageError);
  page.on("console", onConsole);
  const started = Date.now();
  try {
    const remaining = Math.max(500, globalDeadline - Date.now());
    const timeout = Math.min(PER_PAGE_MS, remaining);
    const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout });
    if (response && state.documentStatus === null) state.documentStatus = response.status();
    await page.waitForTimeout(Math.min(300, Math.max(0, globalDeadline - Date.now())));
    state.dom = await evaluatePage(page, base, state, inputs);
    state.runtime = {
      numShots: state.dom.numShots,
      shotListCount: state.dom.shotList ? state.dom.shotList.length : null,
      shotListUrls: state.dom.shotList || [],
      nativeSourceDirectory: row.source_directory,
      nativeExpectedFullCount: expected.full.length,
      nativeExpectedThumbCount: expected.thumb.length,
      galleryDomImageCount: state.dom.galleryImages.length,
      galleryDomImageRoutes: state.dom.galleryImages.map((x) => x.route),
      guidePreviewImageCount: state.dom.guidePreviewImages.length,
      guidePreviewRoutes: state.dom.guidePreviewImages.map((x) => x.route),
      galleryPlaceholderCount: state.dom.galleryImages.filter((x) => x.missingImagePlaceholder).length,
      galleryPlaceholderRequestedRoutes: state.dom.galleryImages.map((x) => x.placeholderRequestedRoute).filter(Boolean),
      guidePreviewPlaceholderCount: state.dom.guidePreviewImages.filter((x) => x.missingImagePlaceholder).length,
      allPlaceholderRequestedRoutes: state.dom.placeholderImageRequestedRoutes,
      guideScreenieAnchorCount: state.dom.screenieAnchors.length,
      guideScreenieAnchorRoutes: state.dom.screenieAnchors,
      guideCollectionRoutesOnPage: state.dom.screenieAnchors.filter((p) => inputs.guideCollectionRoutes.has(p)),
    };
    state.classification = {
      navigation: state.documentStatus >= 200 && state.documentStatus < 400 ? "ok" : "navigation_http_error",
      nativeImage404s: state.http404s.filter((x) => x.classification === "native_expected").length,
      guidePreviewImage404s: state.http404s.filter((x) => x.classification === "guide_preview").length,
      guideCollectionImage404s: state.http404s.filter((x) => x.classification === "guide_collection").length,
      otherLocal404s: state.http404s.filter((x) => x.classification === "other").length,
      nativeImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "native_expected").length,
      guidePreviewImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "guide_preview").length,
      guideCollectionImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "guide_collection").length,
      otherImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "other").length,
      externalActivity: state.blockedExternalRequests.length,
      pageFailure: state.gotoError || state.pageErrors.length || state.requestFailures.length ? "failures_present" : "none_recorded",
    };
    if (screenshotName) {
      await page.evaluate(() => {
        const gallery = document.getElementById("galleryPictures");
        if (gallery) gallery.scrollIntoView({ block: "center", inline: "nearest" });
        else window.scrollTo(0, Math.floor(document.body.scrollHeight / 2));
      });
      await page.waitForTimeout(100);
      const screenshotPath = path.join(SCREENSHOT_DIR, screenshotName);
      await page.screenshot({ path: screenshotPath, fullPage: false });
      state.screenshot = { path: path.relative(REPO, screenshotPath).replace(/\\/g, "/"), scrollY: await page.evaluate(() => window.scrollY) };
    }
  } catch (error) {
    state.gotoError = `${error && error.name ? error.name : "Error"}: ${error && error.message ? error.message : String(error)}`;
    state.classification = {
      navigation: "navigation_exception",
      nativeImage404s: state.http404s.filter((x) => x.classification === "native_expected").length,
      guidePreviewImage404s: state.http404s.filter((x) => x.classification === "guide_preview").length,
      guideCollectionImage404s: state.http404s.filter((x) => x.classification === "guide_collection").length,
      otherLocal404s: state.http404s.filter((x) => x.classification === "other").length,
      nativeImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "native_expected").length,
      guidePreviewImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "guide_preview").length,
      guideCollectionImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "guide_collection").length,
      otherImagePlaceholders: state.imagePlaceholders.filter((x) => x.classification === "other").length,
      externalActivity: state.blockedExternalRequests.length,
      pageFailure: "navigation_exception",
    };
  } finally {
    page.off("response", onResponse);
    page.off("requestfailed", onFailure);
    page.off("pageerror", onPageError);
    page.off("console", onConsole);
  }
  state.elapsedMs = Date.now() - started;
  state.finishedAt = now();
  // These working sets are classification inputs, not browser observations.
  // Do not serialize them as `{}` (the default JSON representation of Set),
  // because that could be mistaken for an identity inventory.  Exact native
  // identity remains in the static package named in the top-level receipt.
  state.identitySource = {
    package: "research/player-gallery-accessibility-20261020/local/gallery-accessibility-50.json",
    note: "Browser result reports observed runtime only; exact full/thumb identity is independently supplied by the static package and root acceptance."
  };
  delete state.expectedNative;
  delete state.guidePreviewRoutes;
  delete state.guideCollectionRoutes;
  // Keep a compact but auditable failure/resource record.  The full runtime
  // source URL arrays remain because they are the browser observation.
  return state;
}

async function main() {
  const { base } = parseArgs();
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  const inputs = loadInputs();
  const startedAt = now();
  const startedMs = Date.now();
  const globalDeadline = startedMs + GLOBAL_MS;
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  let currentState = null;
  const blockedAtContext = [];
  await context.route("**/*", async (route) => {
    const request = route.request();
    if (!isLoopback(request.url())) {
      const item = { url: request.url(), resourceType: request.resourceType(), method: request.method() };
      capPush(blockedAtContext, item, 200);
      if (currentState) capPush(currentState.blockedExternalRequests, item, 100);
      await route.abort("blockedbyclient");
    } else {
      await route.continue();
    }
  });
  const page = await context.newPage();
  const screenshotNames = new Map([
    ["/info/dungeons/karazhan-gallery.html", "karazhan.png"],
    ["/info/dungeons/black-temple-gallery.html", "black-temple.png"],
    ["/info/professions/fishing-gallery.html", "fishing.png"],
    ["/info/events/lunarnewyears/gallery.html", "lunar-festival.png"],
  ]);
  const results = [];
  let stopped = null;
  try {
    for (const row of inputs.pkg.rows) {
      if (Date.now() >= globalDeadline) {
        stopped = { reason: "global_deadline", remainingGalleryRows: inputs.pkg.rows.slice(results.length).map((x) => x.source_page_route) };
        break;
      }
      currentState = { blockedExternalRequests: [] };
      const result = await auditOne(page, base, row, inputs, screenshotNames.get(row.source_page_route) || null, globalDeadline);
      currentState = null;
      results.push(result);
    }
    if (!stopped && Date.now() < globalDeadline) {
      const wrapperRow = inputs.pkg.rows.find((x) => x.gallery === "Zul'Aman");
      const wrapper = {
        ...wrapperRow,
        source_page_route: "/info/dungeons/zulaman.xml",
        declared_slots: 0,
        expected_direct_entities: 0,
        source_directory: "/info/dungeons/images/zulaman/",
        filename_literal: "ss",
      };
      currentState = { blockedExternalRequests: [] };
      const wrapperResult = await auditOne(page, base, wrapper, inputs, null, globalDeadline);
      wrapperResult.label = "Zul'Aman wrapper";
      wrapperResult.wrapperRoute = "/info/dungeons/zulaman.xml";
      currentState = null;
      results.push(wrapperResult);
    } else if (!stopped) {
      stopped = { reason: "global_deadline_before_wrapper" };
    }
  } finally {
    currentState = null;
    await page.close().catch(() => {});
    await context.close().catch(() => {});
    await browser.close().catch(() => {});
  }
  const output = {
    schema: "player-gallery-browser-audit/v1",
    started_at_utc: startedAt,
    finished_at_utc: now(),
    elapsed_ms: Date.now() - startedMs,
    base_url: base,
    loopback_policy: {
      allowed_hosts: ["127.0.0.1", "localhost", "::1"],
      blocked_external_request_count: blockedAtContext.length,
      blocked_external_requests: blockedAtContext,
    },
    input_static_package: path.relative(REPO, PACKAGE_PATH).replace(/\\/g, "/"),
    input_provenance_sha256: "02b1cd43766288f96c879ef464d7198bb09d1085008ae3e500773d594f6c7760",
    procedure: {
      page_timeout_ms: PER_PAGE_MS,
      global_budget_ms: GLOBAL_MS,
      serial: true,
      dom_injection: false,
      screenshots_after_gallery_scroll: true,
      native_expected_rule: "The static package's exact full/thumb URLs, derived from literal addshots()/printPages() semantics.",
      guide_preview_rule: "Guide preview sections and provenance guide collection paths are reported separately from native runtime shotList URLs.",
    },
    guide_layers: {
      provenance_guide_previews: {
        group_count: inputs.provenance.guide_previews?.group_count || 0,
        preview_count: inputs.provenance.guide_previews?.preview_count || 0,
        groups: (inputs.provenance.guide_previews?.groups || []).map((x) => ({
          group_id: x.group_id,
          gallery_route: x.gallery_route,
          preview_count: x.preview_count,
        })),
      },
      provenance_guide_image_collections: {
        group_count: inputs.provenance.guide_image_collections?.group_count || 0,
        image_count: inputs.provenance.guide_image_collections?.image_count || 0,
        groups: (inputs.provenance.guide_image_collections?.groups || []).map((x) => ({
          group_id: x.group_id,
          gallery_route: x.gallery_route,
          guide_route: x.guide_route,
          image_count: x.image_count,
        })),
      },
      browser_observed_guide_collection_routes: Array.from(new Set(results.flatMap((x) => x.runtime?.guideCollectionRoutesOnPage || []))),
      browser_observed_guide_collection_url_count: results.reduce((n, x) => n + (x.runtime?.guideCollectionRoutesOnPage?.length || 0), 0),
    },
    counts: {
      requested_gallery_pages: 50,
      visited_gallery_pages: results.filter((x) => !x.wrapperRoute).length,
      requested_extra_wrappers: 1,
      visited_extra_wrappers: results.filter((x) => x.wrapperRoute).length,
      navigation_ok: results.filter((x) => x.classification?.navigation === "ok").length,
      navigation_failures: results.filter((x) => x.classification?.navigation !== "ok").length,
      native_image_404s: results.reduce((n, x) => n + (x.classification?.nativeImage404s || 0), 0),
      guide_preview_image_404s: results.reduce((n, x) => n + (x.classification?.guidePreviewImage404s || 0), 0),
      guide_collection_image_404s: results.reduce((n, x) => n + (x.classification?.guideCollectionImage404s || 0), 0),
      other_local_404s: results.reduce((n, x) => n + (x.classification?.otherLocal404s || 0), 0),
      native_image_placeholders: results.reduce((n, x) => n + (x.classification?.nativeImagePlaceholders || 0), 0),
      guide_preview_image_placeholders: results.reduce((n, x) => n + (x.classification?.guidePreviewImagePlaceholders || 0), 0),
      guide_collection_image_placeholders: results.reduce((n, x) => n + (x.classification?.guideCollectionImagePlaceholders || 0), 0),
      other_image_placeholders: results.reduce((n, x) => n + (x.classification?.otherImagePlaceholders || 0), 0),
      pages_with_external_activity: results.filter((x) => (x.classification?.externalActivity || 0) > 0).length,
      pages_with_page_errors: results.filter((x) => (x.pageErrors || []).length > 0).length,
      screenshots: results.filter((x) => x.screenshot).length,
    },
    stopped,
    results,
  };
  const outPath = path.join(OUTPUT_DIR, "browser-audit-all50.json");
  const summaryPath = path.join(OUTPUT_DIR, "browser-audit-summary.json");
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2) + "\n", "utf8");
  const summary = {
    schema: "player-gallery-browser-audit-summary/v1",
    started_at_utc: startedAt,
    finished_at_utc: output.finished_at_utc,
    elapsed_ms: output.elapsed_ms,
    base_url: base,
    counts: output.counts,
    guide_layers: output.guide_layers,
    stopped: stopped,
    blocked_external_request_count: blockedAtContext.length,
    routes: results.map((x) => ({
      gallery: x.label,
      route: x.route,
      wrapper_route: x.wrapperRoute || null,
      document_status: x.documentStatus,
      navigation: x.classification?.navigation,
      runtime_num_shots: x.runtime?.numShots ?? null,
      runtime_shot_list_count: x.runtime?.shotListCount ?? null,
      gallery_dom_image_count: x.runtime?.galleryDomImageCount ?? null,
      guide_preview_image_count: x.runtime?.guidePreviewImageCount ?? null,
      guide_collection_routes_on_page: x.runtime?.guideCollectionRoutesOnPage?.length ?? null,
      native_image_404s: x.classification?.nativeImage404s ?? null,
      guide_preview_image_404s: x.classification?.guidePreviewImage404s ?? null,
      other_local_404s: x.classification?.otherLocal404s ?? null,
      native_image_placeholders: x.classification?.nativeImagePlaceholders ?? null,
      guide_preview_image_placeholders: x.classification?.guidePreviewImagePlaceholders ?? null,
      guide_collection_image_placeholders: x.classification?.guideCollectionImagePlaceholders ?? null,
      other_image_placeholders: x.classification?.otherImagePlaceholders ?? null,
      gallery_placeholder_count: x.runtime?.galleryPlaceholderCount ?? null,
      page_errors: x.pageErrors?.length ?? 0,
      request_failures: x.requestFailures?.length ?? 0,
      blocked_external_requests: x.blockedExternalRequests?.length ?? 0,
      screenshot: x.screenshot?.path || null,
      elapsed_ms: x.elapsedMs,
    })),
  };
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2) + "\n", "utf8");
  console.log(JSON.stringify({ output: path.relative(REPO, outPath).replace(/\\/g, "/"), summary: path.relative(REPO, summaryPath).replace(/\\/g, "/"), counts: output.counts, stopped }, null, 2));
}

main().catch((error) => {
  console.error(`${error && error.stack ? error.stack : error}`);
  process.exitCode = 1;
});

