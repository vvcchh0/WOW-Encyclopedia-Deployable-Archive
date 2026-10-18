/* Bounded v33 browser delta checker.
 *
 * This file is intentionally a checker, never an exporter.  It requires an
 * accepted root browser gate and both explicit GO flags before it starts the
 * local server or Chromium.  All requests are constrained to the generated
 * v33 output tree; external requests are recorded and aborted.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const RUN = path.join(ROOT, 'research/continuous-recovery-20261018');
const INTEGRATION = path.join(RUN, 'integration/v33');
const DEFAULT_INPUT = path.join(INTEGRATION, 'browser/v33-browser-input.json');
const DEFAULT_RESULT = path.join(INTEGRATION, 'browser/results/v33-browser-result.json');
const OUTPUT = path.join(ROOT, '.scratch/pages-resources-20261018-v33');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const ROOT_BROWSER_GATE = path.join(RUN, 'publication/root-v33-browser-input-acceptance.json');
const DEADLINE_MS = 480000;
const PLAYWRIGHT_TIMEOUT = 12000;
const ORDINARY_RACE_TIMEOUT = 2500;

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function sha256File(file) { return sha256(fs.readFileSync(file)); }
function readJson(file, label) {
  if (!fs.existsSync(file)) throw new Error(`missing ${label}: ${file}`);
  const value = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${label} is not an object`);
  return value;
}
function rel(file) { return path.relative(ROOT, path.resolve(file)).replace(/\\/g, '/'); }
function inside(file, label) {
  const resolved = path.resolve(file), root = path.resolve(ROOT);
  if (resolved !== root && !resolved.startsWith(root + path.sep)) throw new Error(`${label} escapes workspace: ${file}`);
  return resolved;
}
function normalizeMime(value) { return String(value || '').split(';', 1)[0].trim().toLowerCase(); }
function extMime(file) {
  const ext = path.extname(file).toLowerCase();
  return ({'.html':'text/html', '.htm':'text/html', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.png':'image/png', '.gif':'image/gif', '.webp':'image/webp', '.bmp':'image/bmp', '.svg':'image/svg+xml'})[ext] || 'application/octet-stream';
}
function parseArgs(argv) {
  const args = { input: DEFAULT_INPUT, result: DEFAULT_RESULT, rootGate: ROOT_BROWSER_GATE, go: false, rootBrowserGo: false };
  for (let i = 0; i < argv.length; i++) {
    const value = argv[i];
    if (value === '--input') args.input = path.resolve(argv[++i]);
    else if (value === '--result') args.result = path.resolve(argv[++i]);
    else if (value === '--root-gate') args.rootGate = path.resolve(argv[++i]);
    else if (value === '--go') args.go = true;
    else if (value === '--root-browser-go') args.rootBrowserGo = true;
    else throw new Error(`unknown argument: ${value}`);
  }
  return args;
}
function verifyBinding(raw, label) {
  if (!raw || typeof raw !== 'object' || !raw.path || !raw.sha256) throw new Error(`${label} has no path/SHA`);
  const file = inside(path.join(ROOT, String(raw.path)), label);
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) throw new Error(`missing ${label}: ${file}`);
  const actual = sha256File(file);
  if (actual.toLowerCase() !== String(raw.sha256).toLowerCase()) throw new Error(`${label} SHA changed: ${actual}`);
  return file;
}
function verifyGate(inputPath, input, gatePath = ROOT_BROWSER_GATE) {
  gatePath = inside(gatePath, 'root browser gate');
  if (path.dirname(gatePath) !== path.join(RUN, 'publication')) throw new Error('browser gate must be a root publication receipt');
  const gate = readJson(gatePath, 'root v33 browser input acceptance');
  if (gate.accepted !== true) throw new Error('root v33 browser input acceptance is not accepted');
  const inputSha = sha256File(inputPath);
  const declared = gate.input_sha256 || gate.browser_input_sha256 || (gate.input && gate.input.sha256);
  if (String(declared || '').toLowerCase() !== inputSha.toLowerCase()) throw new Error(`root browser gate input SHA mismatch: ${declared} != ${inputSha}`);
  if (![0, null].includes(gate.network_requests) || gate.browser_executed === true) throw new Error('root browser gate records prior network/browser execution');
  if (input.status !== 'prepared_waiting_root_v33_browser_go') throw new Error(`unexpected browser input status: ${input.status}`);
  return { path: rel(gatePath), sha256: sha256File(gatePath) };
}
function checkDeadline(started) { if (Date.now() - started > DEADLINE_MS) throw new Error('v33 browser delta deadline exceeded'); }

function popupArgument(value) {
  const match = String(value || '').match(/\bpopUpOmega\s*\(\s*(['"])(.*?)\1/i);
  return match ? String(match[2]).replace(/\\(['"])/g, '$1') : null;
}

function assetKey(value, base) {
  try {
    const parsed = new URL(String(value), base);
    if (!['http:', 'https:'].includes(parsed.protocol) || !parsed.hostname) return null;
    return `${parsed.hostname.toLowerCase()}${parsed.pathname}${parsed.search}`;
  } catch (_) { return null; }
}

function sameAssetTarget(actual, expected, base) {
  const actualKey = assetKey(actual, base);
  const expectedKey = assetKey(expected, base);
  return !!actualKey && actualKey === expectedKey;
}

function selectPopupControlIndex(candidates, row, pageUrl) {
  const expectedArgument = popupArgument(row && row.literal);
  if (!expectedArgument) return -1;
  const sourceBase = String((row && row.source_base_url) || pageUrl || '');
  return (Array.isArray(candidates) ? candidates : []).findIndex(candidate => {
    const actualArgument = popupArgument(`${candidate.onclick || ''}\n${candidate.href || ''}`);
    return actualArgument === expectedArgument && sameAssetTarget(actualArgument, row.original, sourceBase);
  });
}

function removeListener(emitter, event, listener) {
  if (typeof emitter.off === 'function') emitter.off(event, listener);
  else if (typeof emitter.removeListener === 'function') emitter.removeListener(event, listener);
}

function waitForOrdinaryNavigation(context, currentPage, click, timeoutMs = ORDINARY_RACE_TIMEOUT) {
  const before = currentPage.url();
  return new Promise((resolve, reject) => {
    let settled = false;
    let timer = null;
    const cleanup = () => {
      removeListener(context, 'page', onPopup);
      removeListener(currentPage, 'framenavigated', onNavigate);
      if (timer) clearTimeout(timer);
    };
    const finish = value => {
      if (settled) return;
      settled = true;
      cleanup();
      resolve(value);
    };
    const onPopup = popup => finish({ kind: 'popup', popup });
    const onNavigate = frame => {
      if (frame === currentPage.mainFrame() && currentPage.url() !== before) finish({ kind: 'same-tab', url: currentPage.url() });
    };
    context.on('page', onPopup);
    currentPage.on('framenavigated', onNavigate);
    timer = setTimeout(() => finish({ kind: 'none', url: currentPage.url() }), timeoutMs);
    Promise.resolve().then(click).catch(error => {
      if (settled) return;
      settled = true;
      cleanup();
      reject(error);
    });
  });
}

function classifyCssInspection({ declarations = [], visibleDecoded = [] } = {}) {
  const domMatches = declarations.reduce((total, declaration) => total + Number(declaration.dom_matches || 0), 0);
  if (visibleDecoded.length) return { kind: 'rendered', dom_matches: domMatches, visible_decoded: visibleDecoded };
  if (declarations.length && domMatches === 0) return { kind: 'declaration_only', dom_matches: 0, declarations };
  if (!declarations.length) throw new Error('image has neither a visible element nor an actual CSS declaration');
  throw new Error(`CSS image has DOM matches but no visible decoded background (${domMatches})`);
}

function interactiveActivationPlan(pagePath, facts = {}) {
  const route = String(pagePath || '').replace(/^\/+/, '');
  return {
    equipment_tabs: route === 'pvp/tournament/items.xml.html' && Number(facts.equipment_tab_count || 0) > 0,
    profession_selectors: route === 'burningcrusade/townhall/professions.html' && Number(facts.profession_dropdown_count || 0) > 0,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.go || !args.rootBrowserGo) throw new Error('v33 browser checker requires --go --root-browser-go');
  if (fs.existsSync(args.result)) throw new Error(`refusing existing browser result: ${args.result}`);
  if (!fs.existsSync(OUTPUT) || !fs.statSync(OUTPUT).isDirectory()) throw new Error(`missing v33 output: ${OUTPUT}`);
  const input = readJson(args.input, 'v33 browser input');
  const gate = verifyGate(args.input, input, args.rootGate);
  for (const [name, binding] of Object.entries(input.source_bindings || {})) verifyBinding(binding, `browser input ${name}`);
  const provenanceBinding = input.output && input.output.provenance;
  verifyBinding(provenanceBinding, 'v33 output provenance');
  const provenancePath = path.join(ROOT, provenanceBinding.path);
  if (sha256File(provenancePath).toLowerCase() !== String(provenanceBinding.sha256).toLowerCase()) throw new Error('v33 provenance binding changed');
  const outputRoot = path.resolve(OUTPUT);
  const started = Date.now();
  const report = {
    schema: 'wow-recovery.integration.v33-browser-result.v1', accepted: false,
    started_utc: new Date().toISOString(), finished_utc: null,
    input: { path: rel(args.input), sha256: sha256File(args.input) }, root_gate: gate,
    checks: [], errors: [], page_error_events: [], baseline_page_errors: [], inactive_image_maps: [], external_requests: [], request_failures: [], screenshots: [],
    popup_full_image_links: 0, ordinary_image_hrefs: 0, static_render_targets: 0,
    declaration_only_images: [], network_requests: 0, browser_executed: true,
  };
  const check = (name, ok, details = {}) => { report.checks.push({ name, accepted: !!ok, ...details }); if (!ok) throw new Error(`${name}: ${JSON.stringify(details)}`); checkDeadline(started); };
    const items = Array.isArray(input.new_originals) ? input.new_originals : [];
    const frozenItems = Array.isArray(input.validated_old_originals) ? input.validated_old_originals : [];
    const validatedItems = [...frozenItems, ...items];
    const byOriginal = new Map(validatedItems.map(item => [String(item.original), item]));
  const localUrl = item => `${base}${String(item.served_output_path).replace(/^\/+/, '')}`;
  let server, browser, context;
  let base;
  try {
    server = http.createServer((req, res) => {
      try {
        const url = new URL(req.url || '/', base || 'http://127.0.0.1');
        if (!url.pathname.startsWith(BASE_PATH) || !['GET', 'HEAD'].includes(req.method)) throw new Error('route/method');
        const relative = decodeURIComponent(url.pathname.slice(BASE_PATH.length));
        if (!relative || relative.includes('\\') || relative.split('/').includes('..') || relative.includes('\0')) throw new Error('unsafe path');
        const file = path.resolve(outputRoot, relative);
        if (file !== outputRoot && !file.startsWith(outputRoot + path.sep)) throw new Error('escape');
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
    context.setDefaultTimeout(PLAYWRIGHT_TIMEOUT);
    await context.route('**/*', route => {
      const requestUrl = route.request().url();
      try {
        if (new URL(requestUrl).origin === new URL(base).origin) return route.continue();
      } catch (_) {}
      report.external_requests.push(requestUrl);
      return route.abort();
    });
    context.on('requestfailed', request => { if (request.url() !== base) report.request_failures.push({ url: request.url(), failure: request.failure() }); });
    context.on('page', page => page.on('pageerror', error => {
      const event = { url: page.url(), message: String(error), stack: String(error.stack || '') };
      report.page_error_events.push(event);
      const relative = page.url().startsWith(base) ? page.url().slice(base.length) : '';
      const known = (input.known_baseline_error_rules || []).some(rule => rule.page === relative && rule.message === event.message && event.stack.includes(rule.stack_marker));
      if (known) report.baseline_page_errors.push(event);
      else report.errors.push(event.message);
    }));
    const page = await context.newPage();

    check('new originals are distinct', items.length === Number(input.new_original_count) && new Set(items.map(item => item.original)).size === items.length, { count: items.length });
    for (const item of items) {
      checkDeadline(started);
      const response = await context.request.get(localUrl(item));
      const body = await response.body();
      const headerMime = normalizeMime(response.headers()['content-type']);
      check('exact original bytes served', response.status() === 200 && body.length === Number(item.served_length) && sha256(body) === String(item.served_sha256).toLowerCase() && headerMime === normalizeMime(item.mime), { original: item.original, output_path: item.served_output_path });
      const dimensions = await page.evaluate(async url => { const image = new Image(); image.src = url; await image.decode(); return [image.naturalWidth, image.naturalHeight]; }, localUrl(item));
      check('original dimensions decode', JSON.stringify(dimensions) === JSON.stringify(item.dimensions), { original: item.original, dimensions });
    }

    const activateNews = async (currentPage, pagePath) => {
      await currentPage.evaluate(async () => { if (window.__WOWPages && window.__WOWPages.ready) await window.__WOWPages.ready; });
      const ids = (input.browser_plan?.news_toggle_ids || {})[pagePath] || [];
      for (const id of ids) {
        const escaped = String(id).replace(/"/g, '\\"');
        const entry = currentPage.locator(`[id="${escaped}"]`);
        if (!await entry.count()) throw new Error(`news entry missing: ${id}`);
        const collapsed = await entry.evaluate(element => element.classList.contains('news-collapse'));
        if (!collapsed) continue;
        const toggle = entry.locator('.news-toggle a').first();
        if (!await toggle.count()) throw new Error(`news entry has no original toggle: ${id}`);
        await toggle.click({ force: true });
        await currentPage.waitForFunction(expectedId => {
          const element = document.getElementById(expectedId);
          return !!element && element.classList.contains('news-expand') && !element.classList.contains('news-collapse');
        }, id);
      }
    };
    const imageIsVisible = async (currentPage, needle) => currentPage.locator('img').evaluateAll(async (elements, value) => {
      const matches = elements.filter(element => (element.getAttribute('src') || '').includes(value));
      await Promise.all(matches.map(element => element.decode().catch(() => {})));
      return matches.some(element => {
        const style = getComputedStyle(element), bounds = element.getBoundingClientRect();
        return element.naturalWidth > 0 && style.display !== 'none' && style.visibility !== 'hidden' && bounds.width > 0 && bounds.height > 0;
      });
    }, needle);
    const activateHiddenControls = async (currentPage, pagePath, needle) => {
      if (await imageIsVisible(currentPage, needle)) return;
      const facts = await currentPage.evaluate(() => ({
        equipment_tab_count: document.querySelectorAll('a[rel^="tab-"]').length,
        profession_dropdown_count: document.querySelectorAll('#dropBox > div[onclick]').length,
      }));
      const plan = interactiveActivationPlan(pagePath, facts);
      if (plan.equipment_tabs) {
        const tabs = currentPage.locator('a[rel^="tab-"]');
        for (let index = 0; index < await tabs.count(); index++) {
          const tab = tabs.nth(index);
          const relValue = String(await tab.getAttribute('rel') || '');
          const panelId = `#${relValue.replace(/^tab-/, 'tab-')}`;
          await tab.click({ force: true });
          await currentPage.locator(panelId).waitFor({ state: 'visible' });
          if (await imageIsVisible(currentPage, needle)) return plan;
        }
      }
      if (plan.profession_selectors) {
        const drop = currentPage.locator('#dropBox > div[onclick]').first();
        for (let profession = 0; profession < 7; profession++) {
          if (await currentPage.evaluate(() => window.previousProfession) !== profession) {
            await drop.click({ force: true });
            const slot = currentPage.locator(`#slot${profession} a`).first();
            await slot.click({ force: true });
            await currentPage.waitForFunction(expected => window.previousProfession === expected, profession);
          }
          const recipes = currentPage.locator('#recipeList a');
          for (let recipe = 0; recipe < await recipes.count(); recipe++) {
            const link = recipes.nth(recipe);
            const name = await link.innerText();
            await link.click({ force: true });
            await currentPage.waitForFunction(expected => document.getElementById('recipeName')?.innerText === expected, name);
            if (await imageIsVisible(currentPage, needle)) return plan;
          }
        }
      }
      return plan;
    };
    const openImagePopup = async (currentPage, item, row, label) => {
      const routeNeedle = String(item.served_output_path).replace(/\\/g, '/');
      const indices = await currentPage.locator('a').evaluateAll((elements, needle) => elements.map((element, index) => ({ index, href: element.getAttribute('href') || '', onclick: element.getAttribute('onclick') || '' })).filter(entry => entry.href.includes('popUpOmega') || entry.onclick.includes('popUpOmega') || entry.href.includes(needle)), routeNeedle);
      if (!indices.length) throw new Error(`${label}: no image popup control for ${item.original}`);
      const matchIndex = selectPopupControlIndex(indices, row, currentPage.url());
      if (matchIndex < 0) throw new Error(`${label}: exact popUpOmega image control missing for ${item.original}`);
      const locator = currentPage.locator('a').nth(indices[matchIndex].index);
      const popupPromise = context.waitForEvent('page', { timeout: PLAYWRIGHT_TIMEOUT }).catch(() => null);
      await locator.click({ force: true });
      const popup = await popupPromise;
      if (!popup) throw new Error(`${label}: click opened no popup for ${item.original}`);
      await popup.waitForLoadState('domcontentloaded');
      const expected = localUrl(item);
      check(`${label} opens expected local image`, popup.url() === expected, { expected, actual: popup.url(), page: row.page_output });
      const image = popup.locator('img').first();
      await image.waitFor({ state: 'attached' });
      await image.evaluate(element => element.decode());
      const dimensions = await image.evaluate(element => [element.naturalWidth, element.naturalHeight]);
      check(`${label} image decodes`, JSON.stringify(dimensions) === JSON.stringify(item.dimensions), { dimensions, original: item.original });
      check(`${label} popup has no opener`, await popup.evaluate(() => window.opener === null));
      await popup.close();
    };
    const checkImageDocument = async (currentPage, item, label) => {
      const dimensions = await currentPage.evaluate(async url => {
        const image = new Image();
        image.src = url;
        await image.decode();
        return [image.naturalWidth, image.naturalHeight];
      }, currentPage.url());
      const validDimensions = dimensions.every(value => Number(value) > 0) && (!item.dimensions || JSON.stringify(dimensions) === JSON.stringify(item.dimensions));
      check(`${label} image decodes`, validDimensions, { dimensions, expected: item.dimensions || 'positive intrinsic dimensions', original: item.original });
    };

    const popupRows = Array.isArray(input.source_references?.popup_full_image_links) ? input.source_references.popup_full_image_links : [];
    const popupPages = new Map();
    for (const row of popupRows) { if (!popupPages.has(row.page_output)) popupPages.set(row.page_output, []); popupPages.get(row.page_output).push(row); }
    for (const [pagePath, rows] of popupPages) {
      checkDeadline(started);
      const response = await page.goto(base + pagePath.replace(/^\/+/, ''), { waitUntil: 'networkidle' });
      check('popup source page opens', !!response && response.status() === 200, { page: pagePath });
      await activateNews(page, pagePath);
      for (const row of rows) { const item = byOriginal.get(row.original); if (!item) throw new Error(`popup row has no item: ${row.original}`); await openImagePopup(page, item, row, 'popup full-size image'); report.popup_full_image_links++; }
    }

    const ordinaryRows = Array.isArray(input.source_references?.ordinary_image_hrefs) ? input.source_references.ordinary_image_hrefs : [];
    const ordinaryUnique = new Map(ordinaryRows.map(row => [row.original, row]));
    const ordinaryPages = new Map();
    for (const row of ordinaryUnique.values()) { if (!ordinaryPages.has(row.page_output)) ordinaryPages.set(row.page_output, []); ordinaryPages.get(row.page_output).push(row); }
    for (const [pagePath, rows] of ordinaryPages) {
      checkDeadline(started);
      const response = await page.goto(base + pagePath.replace(/^\/+/, ''), { waitUntil: 'networkidle' });
      check('ordinary image source page opens', !!response && response.status() === 200, { page: pagePath });
      await activateNews(page, pagePath);
      for (const row of rows) {
        const item = byOriginal.get(row.original); if (!item) throw new Error(`ordinary row has no item: ${row.original}`);
        const needle = String(item.served_output_path).replace(/\\/g, '/');
        await activateHiddenControls(page, pagePath, needle);
        const fallback = page.locator('a[href],area[href]').evaluateAll((elements, value) => elements.map((element, index) => ({ index, href: element.getAttribute('href') || '', tag: element.tagName })).filter(entry => entry.href.includes(value)), needle);
        const fallbackRows = await fallback;
        if (!fallbackRows.length) throw new Error(`ordinary image href control missing: ${row.original}`);
        const control = page.locator('a[href],area[href]').nth(fallbackRows[0].index);
        if (fallbackRows[0].tag === 'AREA') {
          const map = await control.evaluate(element => {
            const map = element.closest('map'), name = map && (map.name || map.id);
            const images = [...document.querySelectorAll('img[usemap]')].filter(image => image.getAttribute('usemap') === `#${name}`);
            return { name, associated_images: images.length, href: element.href };
          });
          if (map.name && map.associated_images === 0) {
            check('historical image-map declaration has no associated image', map.href === localUrl(item), { page: pagePath, original: row.original, map });
            report.inactive_image_maps.push({ page: pagePath, original: row.original, map, image_bytes_and_dimensions_checked: true });
            report.ordinary_image_hrefs++;
            continue;
          }
        }
        const activate = fallbackRows[0].tag === 'AREA'
          ? async () => { await control.focus(); await page.keyboard.press('Enter'); }
          : () => control.click({ force: true });
        const outcome = await waitForOrdinaryNavigation(context, page, activate);
        if (outcome.kind === 'popup') {
          const popup = outcome.popup;
          await popup.waitForLoadState('domcontentloaded');
          check('ordinary image href opens local image', popup.url() === localUrl(item), { original: row.original, actual: popup.url() });
          await checkImageDocument(popup, item, 'ordinary popup');
          await popup.close();
        } else if (outcome.kind === 'same-tab') {
          check('ordinary image href navigates locally', page.url() === localUrl(item), { original: row.original, actual: page.url() });
          await checkImageDocument(page, item, 'ordinary same-tab');
          // A same-tab ordinary href consumes the source page. Reopen the
          // frozen source route before the next unique original on this page.
          await page.goto(base + pagePath.replace(/^\/+/, ''), { waitUntil: 'networkidle' });
          await activateNews(page, pagePath);
        } else {
          throw new Error(`ordinary image href produced no popup or same-tab navigation: ${row.original}`);
        }
        report.ordinary_image_hrefs++;
      }
    }

    const staticRows = Array.isArray(input.source_references?.static_render_targets) ? input.source_references.static_render_targets : [];
    const staticPages = new Map();
    for (const row of staticRows) { if (!staticPages.has(row.page_output)) staticPages.set(row.page_output, []); staticPages.get(row.page_output).push(row); }
    for (const [pagePath, rows] of staticPages) {
      checkDeadline(started);
      const response = await page.goto(base + pagePath.replace(/^\/+/, ''), { waitUntil: 'networkidle' });
      check('static source page opens', !!response && response.status() === 200, { page: pagePath });
      await activateNews(page, pagePath);
      for (const row of rows) {
        const item = byOriginal.get(row.original); if (!item) throw new Error(`static row has no item: ${row.original}`);
        const needle = String(item.served_output_path).replace(/\\/g, '/');
        await activateHiddenControls(page, pagePath, needle);
        const visible = await page.locator('img').evaluateAll((elements, value) => elements.filter(element => {
          const style = getComputedStyle(element);
          const bounds = element.getBoundingClientRect();
          return (element.getAttribute('src') || '').includes(value) && element.naturalWidth > 0 && element.naturalHeight > 0 && style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && bounds.width > 0 && bounds.height > 0;
        }).map(element => ({ width: element.naturalWidth, height: element.naturalHeight })), needle);
        if (visible.length) check('static image element renders', visible.some(dim => JSON.stringify([dim.width, dim.height]) === JSON.stringify(item.dimensions)), { page: pagePath, original: row.original, visible });
        else {
          const cssInspection = await page.evaluate(async value => {
            const declarations = [];
            const visibleDecoded = [];
            const visible = element => {
              const style = getComputedStyle(element), bounds = element.getBoundingClientRect();
              return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && bounds.width > 0 && bounds.height > 0;
            };
            const decodeBackground = async (element, background) => {
              const match = String(background || '').match(/url\(["']?(.*?)["']?\)/i);
              if (!match) return null;
              try {
                const image = new Image(); image.src = new URL(match[1], document.baseURI).href; await image.decode();
                if (image.naturalWidth <= 0 || image.naturalHeight <= 0) return null;
                return { selector: element.id ? `#${element.id}` : element.className ? `.${String(element.className).split(/\s+/).filter(Boolean).join('.')}` : element.tagName, url: image.src, dimensions: [image.naturalWidth, image.naturalHeight] };
              } catch (_) { return null; }
            };
            for (const element of document.querySelectorAll('*')) {
              const background = getComputedStyle(element).backgroundImage;
              if (!String(background).includes(value)) continue;
              if (visible(element)) {
                const decoded = await decodeBackground(element, background);
                if (decoded) visibleDecoded.push(decoded);
              }
            }
            const walk = rules => {
              for (const rule of rules || []) {
                if (rule.cssRules) walk(rule.cssRules);
                if (rule.selectorText && String(rule.style?.backgroundImage || '').includes(value)) {
                  let count = 0;
                  try { count = document.querySelectorAll(rule.selectorText).length; } catch (_) {}
                  declarations.push({ selector: rule.selectorText, dom_matches: count, background: rule.style.backgroundImage });
                }
              }
            };
            for (const sheet of document.styleSheets) { try { walk(sheet.cssRules); } catch (_) {} }
            return { declarations, visibleDecoded };
          }, needle);
          const classification = classifyCssInspection(cssInspection);
          if (classification.kind === 'rendered') {
            const expected = item.dimensions ? JSON.stringify(item.dimensions) : null;
            check('static CSS image decodes visibly', classification.visible_decoded.some(entry => !expected || JSON.stringify(entry.dimensions) === expected), { page: pagePath, original: row.original, css: classification });
          } else {
            report.declaration_only_images.push({ original: row.original, page: pagePath, declarations: cssInspection.declarations });
          }
        }
        report.static_render_targets++;
      }
    }
    const screenshotTargets = Array.isArray(input.browser_plan?.screenshot_targets) ? input.browser_plan.screenshot_targets : [];
    for (const target of screenshotTargets) {
      const name = String(target.name || 'v33-browser.png');
      const pagePath = String(target.page_output || '');
      if (!pagePath) { report.screenshots.push({ name, skipped: true, reason: 'no matching source reference in frozen manifest' }); continue; }
      const file = path.join(path.dirname(args.result), path.basename(args.result, '.json'), name);
      if (fs.existsSync(file)) throw new Error(`refusing existing browser screenshot: ${file}`);
      const response = await page.goto(base + pagePath, { waitUntil: 'networkidle' }).catch(() => null);
      if (response && response.status() === 200) { fs.mkdirSync(path.dirname(file), { recursive: true }); await page.screenshot({ path: file, fullPage: true }); report.screenshots.push(rel(file)); }
    }
    check('no external requests', report.external_requests.length === 0, { count: report.external_requests.length });
    check('no failed requests', report.request_failures.length === 0, { count: report.request_failures.length });
    check('no new page errors', report.errors.length === 0, { count: report.errors.length, recorded_baseline_errors: report.baseline_page_errors.length });
    report.accepted = true;
  } catch (error) {
    report.errors.push(String(error && error.stack || error));
  } finally {
    report.finished_utc = new Date().toISOString();
    report.output_provenance_sha256 = sha256File(path.join(OUTPUT, 'export-provenance.json'));
    fs.mkdirSync(path.dirname(args.result), { recursive: true });
    fs.writeFileSync(args.result, JSON.stringify(report, null, 2) + '\n', { encoding: 'utf8', flag: 'wx' });
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    if (server) await new Promise(resolve => server.close(resolve));
  }
  process.stdout.write(JSON.stringify({ accepted: report.accepted, checks: report.checks.length, popup_full_image_links: report.popup_full_image_links, ordinary_image_hrefs: report.ordinary_image_hrefs, static_render_targets: report.static_render_targets, errors: report.errors, external_requests: report.external_requests }) + '\n');
  if (!report.accepted) process.exitCode = 1;
}

if (require.main === module) {
  main().catch(error => { process.stderr.write(String(error && error.stack || error) + '\n'); process.exitCode = 1; });
}

module.exports = {
  ORDINARY_RACE_TIMEOUT,
  popupArgument,
  sameAssetTarget,
  selectPopupControlIndex,
  waitForOrdinaryNavigation,
  classifyCssInspection,
  interactiveActivationPlan,
};
