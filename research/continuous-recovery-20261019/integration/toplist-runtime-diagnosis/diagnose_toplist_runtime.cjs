/* One bounded, loopback-only Toplist runtime diagnosis for v37. */
'use strict';

const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../..');
const OUTPUT_ROOT = path.join(ROOT, '.scratch/pages-resources-20261019-v37');
const PROVENANCE_PATH = path.join(OUTPUT_ROOT, 'export-provenance.json');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const RESULT_PATH = path.join(__dirname, 'results/toplist-runtime-diagnosis.json');

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function normalizePath(value) { return String(value || '').replace(/^\/+/, '').replace(/\\/g, '/'); }
function inside(file, base, label) {
  const resolved = path.resolve(file), root = path.resolve(base);
  if (resolved !== root && !resolved.startsWith(root + path.sep)) throw new Error(`${label} escapes ${root}: ${file}`);
  return resolved;
}
function readJson(file, label) {
  if (!fs.existsSync(file)) throw new Error(`missing ${label}: ${file}`);
  const value = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${label} is not an object`);
  return value;
}
function mime(file) {
  const ext = path.extname(file).toLowerCase();
  return ({
    '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
    '.xml': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
    '.png': 'image/png', '.webp': 'image/webp', '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  })[ext] || 'application/octet-stream';
}
function safeValue(value) {
  if (value === null || value === undefined) return value;
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return value;
  if (Array.isArray(value)) return { type: 'array', length: value.length, sample: value.slice(0, 5).map(safeValue) };
  if (typeof value === 'object') return { type: 'object', keys: Object.keys(value).slice(0, 50) };
  return { type: typeof value };
}
function manifestToplistData(provenance) {
  return (provenance.files || []).filter(row => normalizePath(row.output_path).startsWith('toplist/data/')).map(row => ({
    output_path: row.output_path,
    route: row.route || null,
    role: row.role || null,
    mime: row.mime || null,
    derived_length: row.derived_length ?? null,
    derived_sha256: row.derived_sha256 || null,
    original_url: row.original_url || row.source_url || row.static_url || null,
    source_url: row.source_url || null,
  }));
}
function filesystemToplistData() {
  const root = path.join(OUTPUT_ROOT, 'toplist/data');
  if (!fs.existsSync(root)) return [];
  const rows = [];
  const walk = current => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.isFile()) {
        const bytes = fs.readFileSync(full);
        rows.push({ output_path: normalizePath(path.relative(OUTPUT_ROOT, full)), length: bytes.length, sha256: sha256(bytes), mime: mime(full) });
      }
    }
  };
  walk(root);
  return rows;
}
function createServer(report) {
  const server = http.createServer((request, response) => {
    const requestUrl = new URL(request.url || '/', 'http://127.0.0.1');
    const record = { url: requestUrl.href, path: requestUrl.pathname, method: request.method, status: null, scope: 'outside_base' };
    const finish = (status, headers = {}) => {
      record.status = status;
      report.server_requests.push(record);
      response.writeHead(status, headers);
      return response.end();
    };
    if (!['GET', 'HEAD'].includes(request.method)) return finish(405);
    if (!requestUrl.pathname.startsWith(BASE_PATH)) return finish(404);
    const relative = normalizePath(decodeURIComponent(requestUrl.pathname.slice(BASE_PATH.length)));
    record.scope = 'base'; record.relative_path = relative;
    if (!relative || relative.includes('\\') || relative.includes('\0') || relative.split('/').includes('..')) return finish(400);
    let file;
    try { file = inside(path.join(OUTPUT_ROOT, relative), OUTPUT_ROOT, 'output request'); } catch (error) { record.error = String(error); return finish(400); }
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return finish(404);
    const body = fs.readFileSync(file);
    record.status = 200; record.mime = mime(file); record.length = body.length; record.sha256 = sha256(body);
    report.server_requests.push(record);
    response.writeHead(200, { 'Content-Type': record.mime, 'Content-Length': body.length, 'Cache-Control': 'no-store' });
    if (request.method === 'HEAD') return response.end();
    response.end(body);
  });
  return server;
}
async function listen(server) {
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return `http://127.0.0.1:${server.address().port}`;
}
async function closeServer(server) { if (server) await new Promise(resolve => server.close(() => resolve())); }
async function collectState(page) {
  return page.evaluate(() => {
    const visible = element => {
      if (!element) return false;
      const style = getComputedStyle(element), rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
    };
    const spells = document.spells || null;
    const data = spells && typeof spells.data === 'object' ? spells.data : null;
    const matchingFields = object => Object.fromEntries(Object.entries(object || {}).filter(([key]) => /missing|error/i.test(key)).map(([key, value]) => [key, safe(value)]));
    const safe = value => {
      if (value === null || value === undefined || typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return value;
      if (Array.isArray(value)) return { type: 'array', length: value.length, sample: value.slice(0, 5).map(safe) };
      if (typeof value === 'object') return { type: 'object', keys: Object.keys(value).slice(0, 50) };
      return { type: typeof value };
    };
    const cssCandidates = ['body.wide a.next', 'body.wide a.prev'].map(selector => {
      const elements = Array.from(document.querySelectorAll(selector));
      return { selector, matches: elements.length, rows: elements.map(element => {
        const style = getComputedStyle(element), rect = element.getBoundingClientRect();
        return { visible: visible(element), rect: [rect.width, rect.height], background_image: style.backgroundImage || 'none', href: element.getAttribute('href') };
      }) };
    });
    return {
      ready_state: document.readyState,
      body_class: document.body ? document.body.className : null,
      body_wide: !!document.body && document.body.classList.contains('wide'),
      title: document.title,
      text_excerpt: (document.body?.innerText || '').trim().slice(0, 1200),
      spells_type: typeof document.spells,
      spells_keys: spells ? Object.keys(spells) : [],
      spells_missing_error_fields: matchingFields(spells),
      data_type: spells ? typeof spells.data : 'absent',
      data_keys: data ? Object.keys(data) : [],
      data_key_count: data ? Object.keys(data).length : 0,
      data_missing_error_fields: matchingFields(data),
      data_missing_value: spells?.dataMissing ?? spells?.data_missing ?? data?.dataMissing ?? data?.data_missing ?? null,
      data_error_value: spells?.error ?? spells?.errorMessage ?? data?.error ?? data?.errorMessage ?? null,
      containers: {
        info: { exists: !!document.querySelector('#infoContainer'), visible: visible(document.querySelector('#infoContainer')) },
        intro: { exists: !!document.querySelector('#intro'), visible: visible(document.querySelector('#intro')), text: (document.querySelector('#intro')?.innerText || '').trim().slice(0, 300) },
        stats: { exists: !!document.querySelector('#stats'), visible: visible(document.querySelector('#stats')), rows: document.querySelector('#stats')?.querySelectorAll('tr').length || 0, text: (document.querySelector('#stats')?.innerText || '').trim().slice(0, 500) },
      },
      css_candidates: cssCandidates,
    };
  });
}
async function main() {
  if (fs.existsSync(RESULT_PATH)) throw new Error(`refusing existing diagnosis result: ${RESULT_PATH}`);
  const provenance = readJson(PROVENANCE_PATH, 'v37 provenance');
  const report = {
    schema: 'wow-recovery.integration.toplist-runtime-diagnosis.v1',
    status: 'running', started_utc: new Date().toISOString(),
    output: { path: '.scratch/pages-resources-20261019-v37', provenance_sha256: sha256(fs.readFileSync(PROVENANCE_PATH)) },
    manifest_toplist_data: manifestToplistData(provenance),
    filesystem_toplist_data: filesystemToplistData(),
    server_requests: [], page_requests: [], page_responses: [], request_failures: [],
    external_requests: [], console_messages: [], page_errors: [], state: null, error: null,
  };
  let server = null, browser = null;
  try {
    server = createServer(report);
    const origin = await listen(server);
    report.origin = origin;
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
    await context.route('**/*', async route => {
      const requestUrl = new URL(route.request().url());
      const local = requestUrl.hostname === '127.0.0.1' && Number(requestUrl.port) === Number(new URL(origin).port);
      if (!local && !['data:', 'blob:'].includes(requestUrl.protocol)) {
        report.external_requests.push({ url: route.request().url(), method: route.request().method(), resource_type: route.request().resourceType() });
        return route.abort();
      }
      return route.continue();
    });
    const page = await context.newPage();
    page.on('request', request => report.page_requests.push({ url: request.url(), method: request.method(), resource_type: request.resourceType() }));
    page.on('response', response => report.page_responses.push({ url: response.url(), status: response.status(), content_type: response.headers()['content-type'] || null }));
    page.on('requestfailed', request => report.request_failures.push({ url: request.url(), method: request.method(), failure: request.failure() }));
    page.on('console', message => report.console_messages.push({ type: message.type(), text: message.text(), location: message.location() }));
    page.on('pageerror', error => report.page_errors.push({ message: String(error && error.message || error), stack: String(error && error.stack || '') }));
    const targetUrl = `${origin}${BASE_PATH}toplist/index.html`;
    const response = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(800);
    report.page = { url: targetUrl, status: response ? response.status() : null, content_type: response ? response.headers()['content-type'] || null : null };
    report.state = await collectState(page);
    await page.close(); await context.close();
    report.status = report.external_requests.length === 0 && report.page_errors.length === 0 ? 'completed' : 'completed_with_external_or_page_errors';
  } catch (error) {
    report.status = 'failed'; report.error = String(error && error.stack || error);
  } finally {
    if (browser) await browser.close().catch(() => {});
    await closeServer(server);
  }
  report.finished_utc = new Date().toISOString();
  report.local_404s = report.server_requests.filter(row => row.status === 404).map(row => ({ url: row.url, path: row.path, scope: row.scope, relative_path: row.relative_path || null }));
  report.browser_404_responses = report.page_responses.filter(row => row.status === 404);
  report.console_error_messages = report.console_messages.filter(row => row.type === 'error');
  fs.mkdirSync(path.dirname(RESULT_PATH), { recursive: true });
  fs.writeFileSync(RESULT_PATH, JSON.stringify(report, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ status: report.status, result: RESULT_PATH, local_404_count: report.local_404s.length, browser_404_count: report.browser_404_responses.length, console_error_count: report.console_error_messages.length, external_requests: report.external_requests.length }));
  if (report.status === 'failed') process.exitCode = 1;
}
main().catch(error => { process.stderr.write(String(error && error.stack || error)); process.exitCode = 1; });
