/*
 * Local-only continuation checker for the frozen v33 browser evidence.
 *
 * This runner is deliberately separate from the Oct18 root-gated checker. It
 * reads the frozen v33 output and r7 input, uses only a loopback HTTP server,
 * and performs bounded batches of visible/native controls. It never changes
 * site files, exporter inputs, or Oct18 evidence.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../..');
const AUDIT_ROOT = path.resolve(__dirname);
const DEFAULT_INPUT = path.join(AUDIT_ROOT, 'v33-ui-audit-input-r7.json');
const OUTPUT_ROOT = path.join(ROOT, '.scratch/pages-resources-20261018-v33');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const MAX_BATCH = 12;
const MAX_DEADLINE_MS = 720000;
const DEFAULT_TIMEOUT = 10000;

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function sha256File(file) { return sha256(fs.readFileSync(file)); }
function readJson(file, label) {
  if (!fs.existsSync(file)) throw new Error(`missing ${label}: ${file}`);
  const value = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${label} is not an object`);
  return value;
}
function rel(file) { return path.relative(ROOT, path.resolve(file)).replace(/\\/g, '/'); }
function inside(file, base, label) {
  const resolved = path.resolve(file), root = path.resolve(base);
  if (resolved !== root && !resolved.startsWith(root + path.sep)) throw new Error(`${label} escapes ${root}: ${file}`);
  return resolved;
}
function parseArgs(argv) {
  const args = { input: DEFAULT_INPUT, scope: null, batchIndex: 1, result: null, batchSize: MAX_BATCH, excludes: [] };
  for (let i = 0; i < argv.length; i++) {
    const value = argv[i];
    if (value === '--input') args.input = path.resolve(argv[++i]);
    else if (value === '--scope') args.scope = argv[++i];
    else if (value === '--batch-index') args.batchIndex = Number(argv[++i]);
    else if (value === '--batch-size') args.batchSize = Number(argv[++i]);
    else if (value === '--exclude-original') args.excludes.push(String(argv[++i]));
    else if (value === '--result') args.result = path.resolve(argv[++i]);
    else throw new Error(`unknown argument: ${value}`);
  }
  if (!['dragon', 'ordinary', 'static'].includes(args.scope)) throw new Error('--scope must be dragon, ordinary, or static');
  if (!Number.isInteger(args.batchIndex) || args.batchIndex < 1) throw new Error('--batch-index must be a positive integer');
  if (!Number.isInteger(args.batchSize) || args.batchSize < 1 || args.batchSize > MAX_BATCH) throw new Error(`--batch-size must be 1..${MAX_BATCH}`);
  if (!args.result) args.result = path.join(AUDIT_ROOT, 'results', `${args.scope}-${String(args.batchIndex).padStart(2, '0')}.json`);
  args.result = inside(args.result, AUDIT_ROOT, 'result');
  if (fs.existsSync(args.result)) throw new Error(`refusing existing result: ${args.result}`);
  return args;
}
function verifyBinding(root, raw, label) {
  if (!raw || typeof raw !== 'object' || !raw.path || !raw.sha256) throw new Error(`${label} has no path/SHA`);
  const file = inside(path.join(root, raw.path), root, label);
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) throw new Error(`missing ${label}: ${file}`);
  const actual = sha256File(file);
  if (actual.toLowerCase() !== String(raw.sha256).toLowerCase()) throw new Error(`${label} SHA mismatch: ${actual} != ${raw.sha256}`);
  return file;
}
function normalizePath(value) { return String(value || '').replace(/^\/+/, '').replace(/\\/g, '/'); }
function extMime(file) {
  const ext = path.extname(file).toLowerCase();
  return ({ '.html': 'text/html', '.htm': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp', '.svg': 'image/svg+xml' })[ext] || 'application/octet-stream';
}
function isVisibleSnapshot(value) {
  return !!value && value.display !== 'none' && value.visibility !== 'hidden' && Number(value.opacity || 1) > 0 && Number(value.width || 0) > 0 && Number(value.height || 0);
}
function waitForPageOutcome(context, page, click, timeoutMs = 3000) {
  const before = page.url();
  return new Promise((resolve, reject) => {
    let settled = false;
    let timer;
    const cleanup = () => {
      context.off('page', onPopup);
      page.off('framenavigated', onNavigate);
      clearTimeout(timer);
    };
    const finish = value => { if (settled) return; settled = true; cleanup(); resolve(value); };
    const onPopup = popup => finish({ kind: 'popup', popup });
    const onNavigate = frame => {
      if (frame === page.mainFrame() && page.url() !== before) finish({ kind: 'same-tab', url: page.url() });
    };
    context.on('page', onPopup);
    page.on('framenavigated', onNavigate);
    timer = setTimeout(() => finish({ kind: 'none', url: page.url() }), timeoutMs);
    Promise.resolve().then(click).catch(error => { if (!settled) { settled = true; cleanup(); reject(error); } });
  });
}
async function decodeImageDocument(page, expectedDimensions) {
  const dimensions = await page.evaluate(async () => {
    const image = new Image();
    image.src = location.href;
    await image.decode();
    return [image.naturalWidth, image.naturalHeight];
  });
  return { dimensions, matches: Array.isArray(expectedDimensions) ? JSON.stringify(dimensions) === JSON.stringify(expectedDimensions) : dimensions.every(value => Number(value) > 0) };
}
async function waitReady(page) {
  await page.evaluate(async () => {
    if (window.__WOWPages && window.__WOWPages.ready) await window.__WOWPages.ready;
  }).catch(() => {});
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const started = Date.now();
  const input = readJson(args.input, 'local audit input');
  if (input.status !== 'prepared_local_only') throw new Error(`unexpected input status: ${input.status}`);
  const frozen = {};
  for (const [name, binding] of Object.entries(input.frozen_bindings || {})) frozen[name] = verifyBinding(ROOT, binding, `frozen binding ${name}`);
  const r7 = readJson(frozen.browser_input_r7, 'frozen r7 input');
  const prior = readJson(frozen.browser_result_r5, 'frozen r5 result');
  if (prior.browser_executed !== true || prior.popup_full_image_links !== 21 || prior.ordinary_image_hrefs !== 23 || prior.static_render_targets !== 0) {
    throw new Error('frozen r5 is not the expected partial checkpoint');
  }
  if (prior.external_requests.length || prior.request_failures.length) throw new Error('frozen r5 had network failures');
  verifyBinding(ROOT, input.frozen_bindings.v33_provenance, 'v33 provenance');
  const outputRoot = inside(path.join(ROOT, input.output.path), ROOT, 'v33 output');
  if (!fs.existsSync(outputRoot) || !fs.statSync(outputRoot).isDirectory()) throw new Error(`missing v33 output: ${outputRoot}`);
  const provenance = readJson(path.join(ROOT, input.frozen_bindings.v33_provenance.path), 'v33 provenance');
  const allItems = [...(r7.new_originals || []), ...(r7.validated_old_originals || [])];
  const byOriginal = new Map(allItems.map(item => [String(item.original), item]));
  const priorOrdinary = new Set((prior.checks || []).filter(row => row.accepted && row.name === 'ordinary image href navigates locally' && row.original).map(row => row.original));
  for (const row of (prior.inactive_image_maps || [])) if (row.original) priorOrdinary.add(row.original);
  for (const row of (prior.unresolved_original_controls || [])) if (row.original) priorOrdinary.add(row.original);
  if (priorOrdinary.size !== 23) throw new Error(`frozen r5 ordinary checkpoint has ${priorOrdinary.size} originals, expected 23`);
  const refs = input.source_references || {};
  let rows;
  if (args.scope === 'dragon') {
    rows = (refs.ordinary_image_hrefs || []).filter(row => row.original === input.dragon_hunt_focus.original);
    if (rows.length !== 1) throw new Error(`Dragon Hunt target count is ${rows.length}`);
  } else if (args.scope === 'ordinary') {
    rows = (refs.ordinary_image_hrefs || []).filter(row => !priorOrdinary.has(row.original) && !args.excludes.includes(row.original));
  } else {
    rows = refs.static_render_targets || [];
  }
  const total = rows.length;
  const startIndex = args.scope === 'dragon' ? 0 : (args.batchIndex - 1) * args.batchSize;
  const selected = args.scope === 'dragon' ? rows : rows.slice(startIndex, startIndex + args.batchSize);
  if (args.scope !== 'dragon' && !selected.length) throw new Error(`empty ${args.scope} batch ${args.batchIndex}; total ${total}`);
  const report = {
    schema: 'wow-recovery.local-audit.v33-ui-batch.v1',
    accepted: false,
    started_utc: new Date().toISOString(),
    finished_utc: null,
    input: { path: rel(args.input), sha256: sha256File(args.input) },
    frozen_r5: { path: rel(frozen.browser_result_r5), sha256: sha256File(frozen.browser_result_r5) },
    output: { path: input.output.path, provenance_sha256: input.frozen_bindings.v33_provenance.sha256 },
    scope: args.scope,
    batch_index: args.batchIndex,
    batch_size: selected.length,
    total_pending_scope: total,
    excluded_originals: args.excludes,
    selected_rows: selected.map(row => ({ original: row.original, page_output: row.page_output, literal: row.literal, source_line: row.source_line || null })),
    target_results: [],
    page_errors: [],
    baseline_page_errors: [],
    external_requests: [],
    request_failures: [],
    network_requests: 0,
    notes: [],
  };
  const rowResult = (row, status, details = {}) => {
    const entry = { original: row.original, page_output: row.page_output, source_line: row.source_line || null, status, ...details };
    report.target_results.push(entry);
    return entry;
  };
  let server, browser, context;
  let base;
  try {
    server = http.createServer((req, res) => {
      try {
        const requestUrl = new URL(req.url || '/', base || 'http://127.0.0.1');
        if (!requestUrl.pathname.startsWith(BASE_PATH) || !['GET', 'HEAD'].includes(req.method)) throw new Error('invalid route');
        const relative = decodeURIComponent(requestUrl.pathname.slice(BASE_PATH.length));
        if (!relative || relative.includes('\\') || relative.split('/').includes('..') || relative.includes('\0')) throw new Error('unsafe path');
        const file = path.resolve(outputRoot, relative);
        if (file !== outputRoot && !file.startsWith(outputRoot + path.sep)) throw new Error('output escape');
        if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
        res.writeHead(200, { 'content-type': extMime(file), 'cache-control': 'no-store' });
        if (req.method === 'HEAD') return res.end();
        fs.createReadStream(file).pipe(res);
      } catch (_) { res.writeHead(400); res.end(); }
    });
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
    const address = server.address();
    base = `http://127.0.0.1:${address.port}${BASE_PATH}`;
    browser = await chromium.launch({ headless: true });
    context = await browser.newContext({ viewport: { width: 1550, height: 1100 } });
    context.setDefaultTimeout(DEFAULT_TIMEOUT);
    await context.route('**/*', route => {
      const requestUrl = route.request().url();
      try {
        if (new URL(requestUrl).origin === new URL(base).origin) return route.continue();
      } catch (_) {}
      report.external_requests.push(requestUrl);
      return route.abort();
    });
    context.on('request', () => { report.network_requests++; });
    context.on('requestfailed', request => {
      if (!request.url().startsWith(base)) report.request_failures.push({ url: request.url(), failure: request.failure() });
    });
    const pageErrors = new Map();
    context.on('page', page => page.on('pageerror', error => {
      const event = { url: page.url(), message: String(error), stack: String(error.stack || '') };
      report.page_errors.push(event);
      pageErrors.set(event.url, (pageErrors.get(event.url) || 0) + 1);
    }));
    const page = await context.newPage();
    const sourceUrl = pagePath => `${base}${normalizePath(pagePath)}`;
    const checkTime = () => { if (Date.now() - started > MAX_DEADLINE_MS) throw new Error('batch deadline exceeded'); };
    const openSource = async pagePath => {
      checkTime();
      const response = await page.goto(sourceUrl(pagePath), { waitUntil: 'networkidle' });
      await waitReady(page);
      if (!response || response.status() !== 200) throw new Error(`source page did not open: ${pagePath} status=${response && response.status()}`);
      return response.status();
    };
    const activateNews = async pagePath => {
      const ids = (input.news_toggle_ids || {})[pagePath] || [];
      const actions = [];
      for (const id of ids) {
        checkTime();
        const entry = page.locator(`#${String(id).replace(/(["\\])/g, '\\$1')}`);
        if (await entry.count() === 0) continue;
        const state = await entry.evaluate(element => ({ collapse: [...element.classList].some(value => value.startsWith('news-collapse')), expand: [...element.classList].some(value => value.startsWith('news-expand')), visible: isFinite(element.getBoundingClientRect().width) && element.getBoundingClientRect().width > 0 }));
        if (!state.collapse) continue;
        // The archive's visible news control is the enclosing hoverContainer.
        // Its child anchor carries the same javascript:toggleEntry URL, but
        // clicking that anchor can let the legacy URL participate in Playwright's
        // navigation wait.  Use the original visible parent event instead and
        // retain the class transition as the success condition.
        const parentToggle = entry.locator('.hoverContainer').first();
        const anchorToggle = entry.locator('.news-toggle a').first();
        const parentVisible = await parentToggle.count() > 0 && await parentToggle.isVisible();
        const toggle = parentVisible ? parentToggle : anchorToggle;
        if (await toggle.count() === 0 || !(await toggle.isVisible())) throw new Error(`news toggle not visible: ${pagePath}#${id}`);
        await toggle.click({ noWaitAfter: true });
        await page.waitForFunction(expected => {
          const element = document.getElementById(expected);
          const classes = element ? [...element.classList] : [];
          return !!element && classes.some(value => value.startsWith('news-expand')) && !classes.some(value => value.startsWith('news-collapse'));
        }, id);
        actions.push(id);
      }
      return actions;
    };
    const imageFacts = async needle => page.locator('img').evaluateAll(async (elements, value) => {
      const facts = [];
      for (const element of elements) {
        if (!(element.getAttribute('src') || '').includes(value)) continue;
        await element.decode().catch(() => {});
        const style = getComputedStyle(element), rect = element.getBoundingClientRect();
        facts.push({ src: element.getAttribute('src'), natural: [element.naturalWidth, element.naturalHeight], display: style.display, visibility: style.visibility, opacity: style.opacity, width: rect.width, height: rect.height });
      }
      return facts;
    }, needle);
    const screenieFacts = async (needle, expectedDimensions) => page.evaluate(async ({ value, expected }) => {
      const visible = element => { const s = getComputedStyle(element), r = element.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0; };
      const rows = [];
      for (const element of document.querySelectorAll('#Screenie')) {
        if (!visible(element)) continue;
        const background = String(getComputedStyle(element).backgroundImage || '');
        const match = background.match(/url\((?:"|')?(.*?)(?:"|')?\)/i);
        if (!match || !String(match[1]).includes(value)) continue;
        const image = new Image();
        image.src = new URL(match[1], document.baseURI).href;
        try { await image.decode(); } catch (_) {}
        rows.push({ url: image.src, natural: [image.naturalWidth, image.naturalHeight], box: [element.getBoundingClientRect().width, element.getBoundingClientRect().height], matches: image.naturalWidth === Number(expected?.[0]) && image.naturalHeight === Number(expected?.[1]) });
      }
      return rows;
    }, { value: needle, expected: expectedDimensions });
    const closeScreenie = async () => {
      const close = page.locator('#Screenie2,[title="Close"]').first();
      if (await close.count() && await close.isVisible()) {
        await close.click({ force: true }).catch(() => {});
        await page.waitForFunction(() => !document.querySelector('#Screenie') || getComputedStyle(document.querySelector('#Screenie')).display === 'none').catch(() => {});
      }
    };
    const controlFor = async (row, item) => {
      const needle = normalizePath(item.served_output_path);
      const candidates = await page.locator('a[href],area[href]').evaluateAll((elements, value) => elements.map((element, index) => {
        const style = getComputedStyle(element), rect = element.getBoundingClientRect();
        const image = element.querySelector('img');
        const imageStyle = image ? getComputedStyle(image) : null;
        const imageRect = image ? image.getBoundingClientRect() : null;
        return {
          index,
          tag: element.tagName,
          href: element.getAttribute('href') || '',
          visible: style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0,
          child_image_visible: !!image && imageStyle.display !== 'none' && imageStyle.visibility !== 'hidden' && imageRect.width > 0 && imageRect.height > 0,
          child_image: image ? { src: image.getAttribute('src') || '', natural: [image.naturalWidth, image.naturalHeight], width: imageRect.width, height: imageRect.height } : null,
        };
      }).filter(entry => entry.href.includes(value)), needle);
      const first = candidates.find(entry => entry.visible || entry.child_image_visible);
      const anchorLocator = first ? page.locator('a[href],area[href]').nth(first.index) : null;
      const clickLocator = first && !first.visible && first.child_image_visible ? anchorLocator.locator('img').first() : anchorLocator;
      return { candidates, locator: anchorLocator, clickLocator, selected: first };
    };
    const inspectCss = async needle => page.evaluate(async value => {
      const visible = element => { const s = getComputedStyle(element), r = element.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0; };
      const visibleDecoded = [];
      for (const element of document.querySelectorAll('*')) {
        const bg = getComputedStyle(element).backgroundImage;
        if (!String(bg).includes(value) || !visible(element)) continue;
        const match = String(bg).match(/url\(["']?(.*?)["']?\)/i);
        if (!match) continue;
        try { const image = new Image(); image.src = new URL(match[1], document.baseURI).href; await image.decode(); if (image.naturalWidth > 0 && image.naturalHeight > 0) visibleDecoded.push({ selector: element.id ? `#${element.id}` : element.tagName, url: image.src, dimensions: [image.naturalWidth, image.naturalHeight] }); } catch (_) {}
      }
      const declarations = [];
      const walk = rules => { for (const rule of rules || []) { if (rule.cssRules) walk(rule.cssRules); if (rule.selectorText && String(rule.style && rule.style.backgroundImage || '').includes(value)) { let count = 0; try { count = document.querySelectorAll(rule.selectorText).length; } catch (_) {} declarations.push({ selector: rule.selectorText, dom_matches: count, background: rule.style.backgroundImage }); } } };
      for (const sheet of document.styleSheets) { try { walk(sheet.cssRules); } catch (_) {} }
      return { visibleDecoded, declarations };
    }, needle);
    const activateStaticControls = async (row, item, needle) => {
      const tried = [];
      const visibleTarget = async () => (await imageFacts(needle)).filter(f => isVisibleSnapshot(f) && f.natural[0] > 0 && f.natural[1] > 0);
      let visible = await visibleTarget();
      if (visible.length) return { visible, tried };
      const tabs = page.locator('a[rel^="tab-"]');
      for (let i = 0; i < await tabs.count(); i++) {
        const tab = tabs.nth(i);
        if (!(await tab.isVisible())) continue;
        const relValue = String(await tab.getAttribute('rel') || '');
        tried.push({ kind: 'tab', rel: relValue });
        await tab.click();
        await page.waitForTimeout(50);
        visible = await visibleTarget();
        if (visible.length) return { visible, tried };
      }
      const profession = page.locator('#dropBox > div[onclick]').first();
      if (await profession.count() && await profession.isVisible()) {
        for (let p = 0; p < 7; p++) {
          checkTime();
          await profession.click();
          const slot = page.locator(`#slot${p} a`).first();
          if (!(await slot.count()) || !(await slot.isVisible())) continue;
          tried.push({ kind: 'profession', index: p });
          await slot.click();
          const recipes = page.locator('#recipeList a');
          for (let r = 0; r < await recipes.count(); r++) {
            const recipe = recipes.nth(r);
            if (!(await recipe.isVisible())) continue;
            tried.push({ kind: 'recipe', profession: p, index: r });
            await recipe.click();
            await page.waitForTimeout(50);
            visible = await visibleTarget();
            if (visible.length) return { visible, tried };
          }
        }
      }
      return { visible, tried };
    };
    if (args.scope === 'dragon') {
      const row = selected[0], item = byOriginal.get(row.original);
      if (!item) throw new Error(`missing Dragon Hunt item: ${row.original}`);
      await openSource(row.page_output);
      const before = await page.locator('#dragonhunt').evaluate(element => { const s = getComputedStyle(element), r = element.getBoundingClientRect(); return { display: s.display, visibility: s.visibility, width: r.width, height: r.height, className: element.className }; });
      const toggles = await page.locator('a').evaluateAll(elements => {
        return elements.map((element, index) => {
          const style = getComputedStyle(element);
          const rect = element.getBoundingClientRect();
          return {
            index,
            href: element.getAttribute('href') || '',
            onclick: element.getAttribute('onclick') || '',
            text: element.textContent.trim(),
            visible: style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0,
          };
        }).filter(entry => entry.onclick.includes('toggleComplete') && entry.onclick.includes('dragonhunt'));
      });
      if (!toggles.length || !toggles.some(toggle => toggle.visible)) throw new Error(`Dragon Hunt native toggle not visible: ${JSON.stringify(toggles)}`);
      const toggle = page.locator('a').nth(toggles.find(toggle => toggle.visible).index);
      await toggle.click();
      await page.waitForFunction(() => { const e = document.getElementById('dragonhunt'); const s = getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden'; });
      const after = await page.locator('#dragonhunt').evaluate(element => { const s = getComputedStyle(element), r = element.getBoundingClientRect(); return { display: s.display, visibility: s.visibility, width: r.width, height: r.height, className: element.className }; });
      const control = await controlFor(row, item);
      if (!control.candidates.length || !control.selected) throw new Error(`Dragon Hunt ss05 anchor is not visible after native toggle: ${JSON.stringify(control.candidates)}`);
      const candidate = control.selected;
      const outcome = await waitForPageOutcome(context, page, () => control.clickLocator.click());
      const expected = `${base}${normalizePath(item.served_output_path)}`;
      let opened;
      if (outcome.kind === 'popup') {
        await outcome.popup.waitForLoadState('domcontentloaded');
        const image = await decodeImageDocument(outcome.popup, item.dimensions);
        opened = { kind: 'popup', url: outcome.popup.url(), expected, image };
        await outcome.popup.close();
      } else if (outcome.kind === 'same-tab') {
        const image = await decodeImageDocument(page, item.dimensions);
        opened = { kind: 'same-tab', url: page.url(), expected, image };
      } else {
        opened = { kind: 'none', url: page.url(), visible: await imageFacts(normalizePath(item.served_output_path)) };
      }
      rowResult(row, opened.url === expected && opened.image && opened.image.matches ? 'passed' : 'failed', { native_toggle: { selector_matches: toggles, before, after }, control: { candidates: control.candidates, selected: candidate }, outcome: opened, expected_dimensions: item.dimensions, served_output_path: item.served_output_path });
    } else if (args.scope === 'ordinary') {
      const grouped = new Map();
      for (const row of selected) { if (!grouped.has(row.page_output)) grouped.set(row.page_output, []); grouped.get(row.page_output).push(row); }
      for (const [pagePath, pageRows] of grouped) {
        await openSource(pagePath);
        const newsActions = await activateNews(pagePath);
        for (const row of pageRows) {
          checkTime();
          const item = byOriginal.get(row.original);
          if (!item) { rowResult(row, 'failed', { reason: 'missing accepted item metadata' }); continue; }
          const control = await controlFor(row, item);
          if (!control.candidates.length) { rowResult(row, 'failed', { reason: 'no matching visible/output href control', candidates: control.candidates, news_actions: newsActions }); continue; }
          const candidate = control.selected;
          if (!candidate) { rowResult(row, 'not_visible', { reason: 'matching anchor and child image are not visible after native controls', candidates: control.candidates, news_actions: newsActions }); continue; }
          const locator = control.clickLocator;
          const activate = candidate.tag === 'AREA' ? async () => { await locator.focus(); await page.keyboard.press('Enter'); } : () => locator.click();
          const outcome = await waitForPageOutcome(context, page, activate);
          const expected = `${base}${normalizePath(item.served_output_path)}`;
          let details = { candidate, expected, outcome_kind: outcome.kind, news_actions: newsActions };
          let passed = false;
          if (outcome.kind === 'popup') { await outcome.popup.waitForLoadState('domcontentloaded'); const image = await decodeImageDocument(outcome.popup, item.dimensions); details.actual_url = outcome.popup.url(); details.image = image; passed = outcome.popup.url() === expected && image.matches; await outcome.popup.close(); }
          else if (outcome.kind === 'same-tab') { const image = await decodeImageDocument(page, item.dimensions); details.actual_url = page.url(); details.image = image; passed = page.url() === expected && image.matches; }
          else {
            const screenie = await screenieFacts(normalizePath(item.served_output_path), item.dimensions);
            if (screenie.length) {
              details.outcome_kind = 'screenie';
              details.actual_url = screenie[0].url;
              details.image = screenie[0];
              passed = screenie.some(entry => entry.matches);
              await closeScreenie();
            } else {
              details.actual_url = page.url();
              details.visible = await imageFacts(normalizePath(item.served_output_path));
              passed = details.visible.some(f => isVisibleSnapshot(f) && f.natural[0] > 0 && f.natural[1] > 0 && JSON.stringify(f.natural) === JSON.stringify(item.dimensions));
            }
          }
          rowResult(row, passed ? 'passed' : 'failed', details);
          if (outcome.kind === 'same-tab') await openSource(pagePath), await activateNews(pagePath);
        }
      }
    } else {
      const grouped = new Map();
      for (const row of selected) { if (!grouped.has(row.page_output)) grouped.set(row.page_output, []); grouped.get(row.page_output).push(row); }
      for (const [pagePath, pageRows] of grouped) {
        await openSource(pagePath);
        const newsActions = await activateNews(pagePath);
        for (const row of pageRows) {
          checkTime();
          const item = byOriginal.get(row.original);
          if (!item) { rowResult(row, 'failed', { reason: 'missing accepted item metadata' }); continue; }
          const needle = normalizePath(item.served_output_path);
          const activated = await activateStaticControls(row, item, needle);
          const direct = activated.visible;
          if (direct.length) {
            const passed = direct.some(f => JSON.stringify(f.natural) === JSON.stringify(item.dimensions));
            rowResult(row, passed ? 'passed' : 'failed', { mode: 'img', visible: direct, tried_controls: activated.tried, news_actions: newsActions });
            continue;
          }
          const css = await inspectCss(needle);
          const passed = css.visibleDecoded.some(entry => JSON.stringify(entry.dimensions) === JSON.stringify(item.dimensions));
          rowResult(row, passed ? 'passed' : (css.declarations.length && css.declarations.every(entry => Number(entry.dom_matches) === 0) ? 'unused_css_declaration' : 'not_visible'), { mode: 'css', css, tried_controls: activated.tried, news_actions: newsActions });
        }
      }
    }
    report.accepted = report.target_results.length === selected.length && report.target_results.every(entry => entry.status === 'passed');
    if (report.external_requests.length) report.notes.push('external requests were attempted and aborted; batch is not accepted');
    if (report.page_errors.length) report.notes.push('page errors are recorded as observed; root legacy baseline comparison remains separate');
  } catch (error) {
    report.errors = [String(error && error.stack || error)];
  } finally {
    report.finished_utc = new Date().toISOString();
    report.duration_ms = Date.now() - started;
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    if (server) await new Promise(resolve => server.close(resolve));
    fs.mkdirSync(path.dirname(args.result), { recursive: true });
    fs.writeFileSync(args.result, JSON.stringify(report, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify({ result: rel(args.result), sha256: sha256File(args.result), accepted: report.accepted, target_results: report.target_results.length, errors: report.errors || [], external_requests: report.external_requests.length, duration_ms: report.duration_ms }, null, 2));
    if (!report.accepted) process.exitCode = 2;
  }
}

main().catch(error => { console.error(error && error.stack || error); process.exitCode = 1; });
