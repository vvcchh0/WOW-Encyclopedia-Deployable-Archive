'use strict';
// Formal local Chrome acceptance.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const ROOT = path.resolve(__dirname, '../../../..');
const MAP_SHA = 'f795ed587062553831afd24d682aaba516ac07bdc6360636119a28aca2bf8355';
const DECISION_SHA = '958ae52a9bde6ff505522ba920257936971231650db0e3db1ef92241853fc304';
const SOURCE_SHA = '4f05d6ab9ee61691cd6440ccd549fc756cd99424b3840ff92b0955c5bad53465';
const AUDIT_SHA = '338189047192160b11846c628d653f56dfd1b82aba73818d570c9c82c1546af2';
const GEOMETRIES = ['across-left', 'across-right', 'down-1', 'down-2', 'down-4', 'down-right'];
const COLORS = ['grey', 'green', 'yellow'];
const MAP_PATH = 'research/continuous-recovery-20261022/integration/related-talent-ui-v54/input-map.json';
const DECISION_PATH = 'research/continuous-recovery-20261022/integration/related-talent-ui-v54/decision.json';
const PINS_PATH = 'research/continuous-recovery-20261022/integration/related-talent-ui-v54/root-input-pins.json';
const SOURCE_PATH = 'research/continuous-recovery-20261021/publication/root-talent-related-source-acceptance.json';
const AUDIT_PATH = 'research/continuous-recovery-20261022/talent-arrow-review/audit.json';
const BASELINE_PATH = 'research/continuous-recovery-20261022/talent-arrow-prototype/prototype-receipt.json';
const KNOWN_GAPS_PATH = 'research/continuous-recovery-20261022/v53-known-missing-targets.json';
const KNOWN_GAPS_SHA = '2eece825655662a6d28e207911b74ea03cb0861a3496dc14da9f474cd4375498';

function sha256(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function gitBlobSha1(bytes) { return crypto.createHash('sha1').update(Buffer.from('blob ' + bytes.length + '\0', 'utf8')).update(bytes).digest('hex'); }
function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }
function fail(message) { throw new Error(message); }
function isWithin(parent, candidate) {
  const rel = path.relative(path.resolve(parent), path.resolve(candidate));
  return rel === '' || (!rel.startsWith('..' + path.sep) && rel !== '..' && !path.isAbsolute(rel));
}
function uniqueSorted(items) { return Array.from(new Set(items)).sort(); }
function normalizeRoutePath(raw, basePath) {
  let url;
  try { url = new URL(raw, 'http://127.0.0.1'); } catch (_) { return null; }
  const nested = url.searchParams.get('requested') || url.searchParams.get('source');
  if (nested && nested !== raw) {
    const nestedRoute = normalizeRoutePath(nested, basePath);
    if (nestedRoute) return nestedRoute;
  }
  let pathname = decodeURIComponent(url.pathname || '/');
  const prefix = String(basePath || '').replace(/\/+$/, '');
  if (prefix && pathname === prefix) pathname = '/';
  else if (prefix && pathname.startsWith(prefix + '/')) pathname = pathname.slice(prefix.length);
  return pathname.replace(/\/+$/, '') || '/';
}
function arrowRoutes() {
  const routes = [];
  for (const geometry of GEOMETRIES) for (const color of COLORS) {
    routes.push('/shared/global/talents/images/talents/arrows/' + geometry + '-' + color + '.gif');
  }
  return routes;
}
function legacyRoutes() {
  return [
    '/shared/global/talents/images/talents/icon-over-grey.gif',
    '/shared/global/talents/images/talents/icon-over-green.gif',
    '/shared/global/talents/images/talents/icon-over-yellow.gif',
    '/shared/global/talents/includes/images/reset.gif',
    '/shared/global/talents/includes/images/resetall.gif',
    '/shared/global/talents/includes/images/printableversion.gif'
  ];
}
function parseArgs(argv) {
  const out = { headed: false, preflightOnly: false };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') { out.help = true; continue; }
    if (arg === '--headed') { out.headed = true; continue; }
    if (arg === '--preflight-only') { out.preflightOnly = true; continue; }
    const opts = { '--base-url': 'baseUrl', '--baseURL': 'baseUrl', '--export-root': 'exportRoot', '--exportRoot': 'exportRoot', '--evidence-dir': 'evidenceDir' };
    if (!opts[arg]) fail('Unknown argument: ' + arg);
    if (!argv[i + 1]) fail('Missing value for ' + arg);
    out[opts[arg]] = argv[++i];
  }
  return out;
}
function helpText() {
  return [
    'Usage:',
    '  node check_v54_talent_ui.cjs --base-url http://127.0.0.1:24783/WOW-Encyclopedia-Deployable-Archive/ --export-root .scratch/<v54-export>',
    '',
    'Options: --base-url/--baseURL, --export-root/--exportRoot, --evidence-dir, --headed, --preflight-only',
    'The full run tests six accepted arrow geometries and the held down-3 talent-data control.',
    'All requests stay on the supplied loopback origin; no response is fabricated or replaced.'
  ].join('\n');
}
function entryMap(entries, key) { return new Map(entries.map(entry => [entry[key], entry])); }

function preflight(opts, baseUrl) {
  const mapBytes = fs.readFileSync(path.join(ROOT, MAP_PATH));
  const decisionBytes = fs.readFileSync(path.join(ROOT, DECISION_PATH));
  const sourceBytes = fs.readFileSync(path.join(ROOT, SOURCE_PATH));
  const auditBytes = fs.readFileSync(path.join(ROOT, AUDIT_PATH));
  const map = JSON.parse(mapBytes.toString('utf8'));
  const decision = JSON.parse(decisionBytes.toString('utf8'));
  const pins = readJson(path.join(ROOT, PINS_PATH));
  const audit = JSON.parse(auditBytes.toString('utf8'));
  assert.strictEqual(sha256(mapBytes), MAP_SHA, 'Pinned input-map SHA mismatch');
  assert.strictEqual(sha256(decisionBytes), DECISION_SHA, 'Pinned decision SHA mismatch');
  assert.strictEqual(sha256(sourceBytes), SOURCE_SHA, 'Pinned source acceptance SHA mismatch');
  assert.strictEqual(sha256(auditBytes), AUDIT_SHA, 'Pinned arrow-audit SHA mismatch');
  assert.strictEqual(map.schema, 'wow-related-talent-ui-map/v2');
  assert.strictEqual(map.ui_count, 24);
  assert.strictEqual(pins.map_sha256, MAP_SHA);
  assert.strictEqual(pins.decision_sha256, DECISION_SHA);
  assert.strictEqual(pins.source_acceptance_sha256, SOURCE_SHA);
  assert.strictEqual(pins.map_schema, map.schema);
  assert.strictEqual(pins.ui_count, 24);
  assert.strictEqual(pins.source_bytes, 26930);
  assert.strictEqual(pins.new_arrow_count, 18);
  assert.strictEqual(pins.held_arrow_count, 3);
  assert.strictEqual(map.source_acceptance_sha256, SOURCE_SHA);
  assert.strictEqual(map.source.classification, 'later_related_source');
  assert.strictEqual(map.source.original_capture_timestamp, null);
  assert.strictEqual(decision.accepted_for_browser_supplement, true);
  assert.strictEqual(decision.accepted_ui_count, 24);
  assert.strictEqual(decision.classification, 'later_related_source');
  assert.strictEqual(decision.original_capture_timestamp, null);
  assert.strictEqual(decision.compatibility_audit.sha256, AUDIT_SHA);
  assert.deepStrictEqual(uniqueSorted(decision.root_visual_selection.accepted_geometries), GEOMETRIES.slice().sort());
  assert.strictEqual(map.entries.length, 24);

  const expectedArrows = arrowRoutes();
  const expectedAll = uniqueSorted(expectedArrows.concat(legacyRoutes()));
  assert.deepStrictEqual(uniqueSorted(map.entries.map(entry => entry.target_route)), expectedAll, 'Map is not exactly the 18-arrow + six-legacy scope');
  assert(!map.entries.some(entry => /\/arrows\/down-3-/.test(entry.target_route)), 'Held down-3 target unexpectedly appears in map');
  assert.strictEqual(map.entries.filter(entry => /\/arrows\//.test(entry.target_route)).length, 18);
  for (const entry of map.entries) {
    assert.strictEqual(entry.classification, 'later_related_source', entry.target_route + ': classification mismatch');
    assert.strictEqual(entry.original_capture_timestamp, null, entry.target_route + ': capture timestamp must remain null');
    assert(Number.isSafeInteger(entry.length) && entry.length > 0);
    assert(/^[0-9a-f]{64}$/.test(entry.sha256));
    assert(/^[0-9a-f]{40}$/.test(entry.git_blob_sha1));
    assert.strictEqual(entry.frames, 1, entry.target_route + ': expected one frame');
    assert(entry.route.startsWith('/__offline/related-talent-ui/'));
    const sourcePath = path.resolve(ROOT, entry.payload_path);
    assert(isWithin(ROOT, sourcePath), 'Input path escapes workspace: ' + entry.payload_path);
    const bytes = fs.readFileSync(sourcePath);
    assert.strictEqual(bytes.length, entry.length, entry.target_route + ': pinned input length mismatch');
    assert.strictEqual(sha256(bytes), entry.sha256, entry.target_route + ': pinned input SHA mismatch');
    assert.strictEqual(gitBlobSha1(bytes), entry.git_blob_sha1, entry.target_route + ': pinned input Git blob mismatch');
  }
  const exportRoot = path.resolve(opts.exportRoot);
  assert(fs.statSync(exportRoot).isDirectory(), 'exportRoot is not a directory: ' + exportRoot);
  const catalog = readJson(path.join(exportRoot, '__offline', 'related-talent-ui.json'));
  const routeMap = readJson(path.join(exportRoot, '__offline', 'route-map.json'));
  const basePath = String(routeMap.base_path || '').replace(/\/+$/, '');
  assert(basePath, 'Export route-map has no base_path');
  assert.strictEqual(baseUrl.pathname.replace(/\/+$/, ''), basePath, 'baseURL path differs from export route-map base_path');
  assert.strictEqual(catalog.source.map_sha256, MAP_SHA, 'Export catalog map binding mismatch');
  assert.strictEqual(catalog.source.decision_sha256, DECISION_SHA, 'Export catalog decision binding mismatch');
  assert.strictEqual(catalog.source.source_acceptance_sha256, SOURCE_SHA);
  assert.strictEqual(catalog.source.classification, 'later_related_source');
  assert.strictEqual(catalog.source.original_capture_timestamp, null);
  assert.strictEqual(catalog.source.repository_url, map.source.repository_url);
  assert.strictEqual(catalog.source.commit_sha, map.source.commit_sha);
  assert.strictEqual(catalog.source.tree_sha, map.source.tree_sha);
  assert.strictEqual(catalog.source.accepted_source_bytes, 26930);
  assert.strictEqual(catalog.source.original_2008_images_recovered, 0);
  assert.strictEqual(catalog.ui_count, 24);
  assert.strictEqual(catalog.assets.length, 24);
  const catalogByTarget = entryMap(catalog.assets, 'target_route');
  const byTarget = entryMap(map.entries, 'target_route');
  for (const entry of map.entries) {
    const asset = catalogByTarget.get(entry.target_route);
    assert(asset, 'Export catalog omitted ' + entry.target_route);
    assert.strictEqual(asset.route, entry.route, entry.target_route + ': catalog route mismatch');
    assert.strictEqual(asset.sha256, entry.sha256, entry.target_route + ': catalog SHA mismatch');
    assert.strictEqual(asset.length, entry.length, entry.target_route + ': catalog length mismatch');
    assert.strictEqual(asset.mime, 'image/' + entry.format.toLowerCase(), entry.target_route + ': catalog MIME mismatch');
    assert.strictEqual(asset.width, entry.width);
    assert.strictEqual(asset.height, entry.height);
    assert.strictEqual(asset.frames, entry.frames);
    assert.strictEqual(routeMap.routes[entry.target_route], basePath + entry.route, entry.target_route + ': output alias mismatch');
    const diskPath = path.resolve(exportRoot, '.' + entry.route);
    assert(isWithin(exportRoot, diskPath), 'Output path escapes exportRoot: ' + entry.route);
    const diskBytes = fs.readFileSync(diskPath);
    assert.strictEqual(diskBytes.length, entry.length, entry.target_route + ': export disk length mismatch');
    assert.strictEqual(sha256(diskBytes), entry.sha256, entry.target_route + ': export disk SHA mismatch');
    assert.strictEqual(gitBlobSha1(diskBytes), entry.git_blob_sha1, entry.target_route + ': export disk Git blob mismatch');
  }
  assert.strictEqual(decision.root_visual_selection.held.length, 3);
  for (const held of decision.root_visual_selection.held) {
    assert(/\/arrows\/down-3-(?:grey|green|yellow)\.gif$/.test(held.target_route));
    assert(!byTarget.has(held.target_route) && !catalogByTarget.has(held.target_route), 'Held down-3 route present in map/catalog');
  }
  const baseline = readJson(path.join(ROOT, BASELINE_PATH));
  const knownBytes = fs.readFileSync(path.join(ROOT, KNOWN_GAPS_PATH));
  assert.strictEqual(sha256(knownBytes), KNOWN_GAPS_SHA, 'Known v53 missing-target inventory drifted');
  const known = JSON.parse(knownBytes.toString('utf8'));
  assert.strictEqual(known.count, 390);
  assert.strictEqual(known.targets.length, 390);
  assert.strictEqual(known.source16_exact_target_entities_absent, true);
  const baselineRoutes = uniqueSorted((baseline.http_errors || []).map(item => normalizeRoutePath(item.url, basePath)).filter(Boolean).concat(known.targets));
  return {
    root: ROOT, exportRoot: exportRoot, baseURL: baseUrl.href, basePath: basePath,
    map: map, decision: decision, audit: audit, catalog: catalog, routeMap: routeMap,
    byTarget: byTarget, expectedArrowRoutes: expectedArrows,
    baselineErrorObservations: (baseline.http_errors || []).length,
    baselineKnownNonArrowRoutes: baselineRoutes,
    mapSha256: sha256(mapBytes), decisionSha256: sha256(decisionBytes),
    sourceAcceptanceSha256: sha256(sourceBytes), auditSha256: sha256(auditBytes)
  };
}
function selectedSequences(audit) {
  const accepted = audit.test_sequences.filter(seq => GEOMETRIES.includes(seq.geometry));
  assert.strictEqual(accepted.length, 5, 'Expected five audited geometries plus corrected across-left');
  assert.deepStrictEqual(uniqueSorted(accepted.map(seq => seq.geometry)), uniqueSorted(GEOMETRIES.filter(g => g !== 'across-left')));
  accepted.push({
    geometry: 'across-left', class: 'paladin', url: '/info/classes/paladin/talents.html',
    edge_child_index: 37, edge_child: 'Improved Holy Shield', parent_index: 38,
    parent: 'Holy Shield', required_parent_rank: 1,
    green_setup: [[20, 5], [24, 5], [28, 5], [30, 3], [31, 2], [33, 1], [34, 4], [36, 5], [38, 1]],
    yellow_target_rank: [[37, 1]],
    correction: 'Paladin data.js uses [i+1,1]: child 37 depends on parent 38.'
  });
  return GEOMETRIES.map(geometry => {
    const seq = accepted.find(item => item.geometry === geometry);
    const name = seq.edge_child || seq.child;
    assert(typeof name === 'string' && name, geometry + ': audit has no child label');
    return { ...seq, edge_child: name };
  });
}
function expectedTarget(raw, basePath, byTarget, byOutput) {
  const route = normalizeRoutePath(raw, basePath);
  if (route && (byTarget.has(route) || byOutput.has(route))) return byTarget.get(route) || byOutput.get(route);
  let u;
  try { u = new URL(raw, 'http://127.0.0.1'); } catch (_) { return null; }
  const requested = u.searchParams.get('requested') || u.searchParams.get('source');
  if (!requested) return null;
  const requestedRoute = normalizeRoutePath(requested, basePath);
  return requestedRoute ? (byTarget.get(requestedRoute) || byOutput.get(requestedRoute) || null) : null;
}
function classifyGap(route, baselineSet) {
  if (!route) return 'unmapped';
  if (/\/arrows\/down-3-(?:grey|green|yellow)\.gif$/.test(route)) return 'expected_held_down3';
  if (/\/arrows\//.test(route)) return 'unexpected_arrow_response';
  if (baselineSet.has(route)) return 'known_baseline_non_arrow_gap';
  return 'unexpected_non_arrow_gap';
}

async function readTargetState(page, seq, expectedState) {
  return page.evaluate(({ child, parent, geometry, expectedState }) => {
    const greenSpan = document.getElementById('arrowGreen' + child);
    const yellowSpan = document.getElementById('arrowYellow' + child);
    if (!greenSpan || !yellowSpan) throw new Error('Missing arrow spans for ' + geometry + ' child ' + child);
    const greenWrapper = greenSpan.parentElement.parentElement;
    const yellowWrapper = yellowSpan.parentElement.parentElement;
    const greyWrapper = greenWrapper.previousElementSibling;
    const describeImage = wrapper => {
      const image = wrapper && wrapper.querySelector('img');
      if (!image) return null;
      const rect = image.getBoundingClientRect(), style = getComputedStyle(image);
      return {
        src: image.getAttribute('src'), currentSrc: image.currentSrc,
        complete: image.complete, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight,
        visibility: style.visibility, display: style.display,
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        renderedWidth: rect.width, renderedHeight: rect.height
      };
    };
    const clickNode = index => Array.from(document.querySelectorAll('[onclick]')).find(node =>
      (node.getAttribute('onclick') || '').indexOf('rankTopOnClick(' + index + ')') >= 0) || null;
    const nodeRect = node => {
      const image = node && node.tagName === 'IMG' ? node : node && node.querySelector('img');
      if (!image) return null;
      const rect = image.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    };
    const iconRect = index => {
      const wrapper = document.getElementById('talentThumb' + index);
      const image = wrapper && wrapper.querySelector('img');
      if (!image) return null;
      const rect = image.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height, complete: image.complete, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight };
    };
    const grey = describeImage(greyWrapper), green = describeImage(greenWrapper), yellow = describeImage(yellowWrapper);
    const req = window.talent[child][5];
    const cssNode = greenWrapper.querySelector('[class^="arrow"]');
    return {
      geometry: geometry, expectedState: expectedState,
      arrowClass: cssNode && cssNode.className,
      grey: grey, green: green, yellow: yellow,
      visibility: { grey: grey && grey.visibility, green: green && green.visibility, yellow: yellow && yellow.visibility },
      parentCell: nodeRect(clickNode(parent)), childCell: nodeRect(clickNode(child)),
      parentIcon: iconRect(parent), childIcon: iconRect(child),
      ranks: {
        parent: window.rankTop[parent][0], child: window.rankTop[child][0],
        all: Array.from({ length: window.talent.length }, (_, i) => window.rankTop[i] ? window.rankTop[i][0] : 0)
      },
      requirement: req ? { parentIndex: req[0], requiredRank: req[1] } : null,
      parentData: JSON.stringify(window.talent[parent]), childData: JSON.stringify(window.talent[child]),
      points: {
        remaining: window.rankPoints,
        availableText: document.getElementById('modifyRankPoints') && document.getElementById('modifyRankPoints').innerText,
        levelRequiredText: document.getElementById('levelRequired') && document.getElementById('levelRequired').innerText,
        byTree: Array.from(window.pointsTree || []),
        byTier: Array.from(window.pointsTier || [], row => Array.from(row || []))
      },
      arrowCss: cssNode ? { top: getComputedStyle(cssNode).top, left: getComputedStyle(cssNode).left } : null
    };
  }, { child: seq.edge_child_index, parent: seq.parent_index, geometry: seq.geometry, expectedState: expectedState });
}
function visible(state, color) { return !!state[color] && state[color].visibility === 'visible'; }
function assertLayerStack(state, byTarget, geometry) {
  assert(state.grey && state.green && state.yellow, geometry + ': all three layer images must exist');
  for (const color of COLORS) {
    const route = '/shared/global/talents/images/talents/arrows/' + geometry + '-' + color + '.gif';
    const entry = byTarget.get(route);
    assert(entry, 'Missing map entry ' + route);
    const image = state[color];
    assert(image.complete, route + ': browser image not complete');
    assert.strictEqual(image.naturalWidth, entry.width, route + ': decoded width mismatch');
    assert.strictEqual(image.naturalHeight, entry.height, route + ': decoded height mismatch');
    assert.strictEqual(image.renderedWidth, entry.width, route + ': rendered width must remain native');
    assert.strictEqual(image.renderedHeight, entry.height, route + ': rendered height must remain native');
  }
}
function contactMetrics(geometry, state) {
  const parent = state.parentIcon, child = state.childIcon, arrow = state.grey && state.grey.rect;
  if (!parent || !child || !arrow) return null;
  const r = n => Number(n.toFixed(2));
  if (geometry.indexOf('down-') === 0 && geometry !== 'down-right') return {
    type: 'vertical', parent_bottom_to_arrow_top_px: r(arrow.y - (parent.y + parent.height)),
    arrow_bottom_to_child_top_px: r(child.y - (arrow.y + arrow.height))
  };
  if (geometry === 'across-right') return {
    type: 'horizontal-right', parent_right_to_arrow_left_px: r(arrow.x - (parent.x + parent.width)),
    arrow_right_to_child_left_px: r(child.x - (arrow.x + arrow.width))
  };
  if (geometry === 'across-left') return {
    type: 'horizontal-left', child_right_to_arrow_left_px: r(arrow.x - (child.x + child.width)),
    arrow_right_to_parent_left_px: r(parent.x - (arrow.x + arrow.width))
  };
  return {
    type: 'diagonal', parent_right_to_arrow_left_px: r(arrow.x - (parent.x + parent.width)),
    parent_bottom_to_arrow_top_px: r(arrow.y - (parent.y + parent.height)),
    arrow_right_to_child_left_px: r(child.x - (arrow.x + arrow.width)),
    arrow_bottom_to_child_top_px: r(child.y - (arrow.y + arrow.height))
  };
}
function assertGeometryPosition(geometry, state, metrics) {
  const p = state.parentIcon, c = state.childIcon, a = state.grey.rect;
  assert(p && c && a, geometry + ': missing parent, child, or arrow rectangle');
  if (geometry === 'across-right') {
    assert(p.x < a.x && a.x < c.x, 'across-right arrow is not between parent and child');
    assert(Math.abs(metrics.parent_right_to_arrow_left_px) <= 2, 'across-right parent edge drifted');
    assert(Math.abs(metrics.arrow_right_to_child_left_px) <= 8, 'across-right child gap/overlap exceeds accepted native fit');
    assert(Math.abs((a.y + a.height / 2) - (p.y + p.height / 2)) <= 8, 'across-right arrow is not vertically aligned');
  } else if (geometry === 'across-left') {
    assert(c.x < a.x && a.x < p.x, 'across-left arrow is not between child 37 and parent 38');
    assert(Math.abs(metrics.child_right_to_arrow_left_px) <= 8, 'across-left child gap/overlap exceeds accepted native fit');
    assert(Math.abs(metrics.arrow_right_to_parent_left_px) <= 8, 'across-left parent gap/overlap exceeds accepted native fit');
    assert(Math.abs((a.y + a.height / 2) - (p.y + p.height / 2)) <= 8, 'across-left arrow is not vertically aligned');
  } else if (geometry === 'down-right') {
    assert(p.x < c.x && p.y < c.y && a.x < c.x && a.y < c.y, 'down-right arrow is not on the parent-to-child diagonal');
    assert(Math.abs(metrics.parent_right_to_arrow_left_px) <= 2, 'down-right arrow does not start at parent edge');
    assert(metrics.arrow_right_to_child_left_px < 0, 'down-right arrow does not reach child column');
    assert(Math.abs(metrics.arrow_bottom_to_child_top_px) <= 3, 'down-right arrow does not reach child row');
  } else {
    assert(p.y < a.y && a.y < c.y, geometry + ' arrow is not between parent and child vertically');
    assert(Math.abs(metrics.parent_bottom_to_arrow_top_px) <= 2, geometry + ' parent vertical edge drifted');
    assert(Math.abs(metrics.arrow_bottom_to_child_top_px) <= 8, geometry + ' child gap/overlap exceeds accepted native fit');
    assert(Math.abs((a.x + a.width / 2) - (p.x + p.width / 2)) <= 2, geometry + ' arrow is not centered in the talent column');
  }
}
function screenshotClip(state, viewport) {
  const rects = [state.grey && state.grey.rect, state.parentIcon, state.childIcon, state.parentCell, state.childCell]
    .filter(r => r && r.width > 0 && r.height > 0);
  const x = Math.max(0, Math.floor(Math.min.apply(null, rects.map(r => r.x)) - 16));
  const y = Math.max(0, Math.floor(Math.min.apply(null, rects.map(r => r.y)) - 16));
  const right = Math.min(viewport.width, Math.ceil(Math.max.apply(null, rects.map(r => r.x + r.width)) + 16));
  const bottom = Math.min(viewport.height, Math.ceil(Math.max.apply(null, rects.map(r => r.y + r.height)) + 16));
  return { x: x, y: y, width: Math.max(1, right - x), height: Math.max(1, bottom - y) };
}
async function saveScreenshot(page, runDir, seq, name, state) {
  const viewport = await page.evaluate(() => ({ width: innerWidth, height: innerHeight }));
  const clip = screenshotClip(state, viewport);
  const file = path.join(runDir, 'screenshots', seq.geometry + '-' + name + '.png');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  await page.screenshot({ path: file, clip: clip });
  return { state: name, path: path.relative(ROOT, file).split(path.sep).join('/'), clip: clip };
}
async function applyLegalRanks(page, pairs, label) {
  return page.evaluate(({ pairs, label }) => {
    const performed = [];
    for (const pair of pairs) {
      const id = pair[0], count = pair[1];
      for (let n = 0; n < count; n++) {
        const beforeRank = window.rankTop[id][0], beforePoints = window.rankPoints;
        window.rankTopOnClick(id);
        const afterRank = window.rankTop[id][0], afterPoints = window.rankPoints;
        if (afterRank !== beforeRank + 1 || afterPoints !== beforePoints - 1) {
          throw new Error(label + ': original rankTopOnClick rejected allocation for talent ' + id + ' rank ' + (n + 1));
        }
        performed.push({ talent_index: id, rank_before: beforeRank, rank_after: afterRank, points_before: beforePoints, points_after: afterPoints });
      }
    }
    return performed;
  }, { pairs: pairs, label: label });
}
async function captureTooltip(page, index, expectedName, parentName, requiredRank) {
  const control = page.locator('img[onclick*="rankTopOnClick(' + index + ')"]').last();
  assert((await control.count()) > 0, 'No original rankTopOnClick hover target for talent ' + index);
  await control.hover({ force: true });
  await page.waitForFunction(i => {
    const node = document.getElementById('talentMouseOver' + i);
    return node && getComputedStyle(node).visibility === 'visible';
  }, index, { timeout: 5000 });
  const data = await page.evaluate(i => {
    const tooltip = document.getElementById('talentMouseOver' + i);
    const req = document.getElementById('requiresTalent' + i);
    return { visible: !!tooltip && getComputedStyle(tooltip).visibility === 'visible', text: tooltip ? tooltip.innerText : '', requirementText: req ? req.innerText : null };
  }, index);
  assert(data.visible, 'Tooltip did not show for talent ' + index);
  assert(data.text.indexOf(expectedName) >= 0, 'Tooltip missing talent name ' + expectedName);
  if (parentName) {
    assert(data.requirementText, 'Tooltip missing prerequisite row for ' + index);
    assert(data.requirementText.indexOf(parentName) >= 0, 'Tooltip missing prerequisite parent ' + parentName);
    assert(data.requirementText.indexOf(String(requiredRank)) >= 0, 'Tooltip missing prerequisite rank ' + requiredRank);
  }
  await page.mouse.move(0, 0);
  return data;
}
async function getSnapshot(page) {
  return page.evaluate(() => ({
    ranks: Array.from({ length: window.talent.length }, (_, i) => window.rankTop[i] ? window.rankTop[i][0] : 0),
    rankPoints: window.rankPoints,
    pointsTree: Array.from(window.pointsTree || []),
    pointsTier: Array.from(window.pointsTier || [], row => Array.from(row || [])),
    levelRequired: document.getElementById('levelRequired') && document.getElementById('levelRequired').innerText,
    pointsAvailableText: document.getElementById('modifyRankPoints') && document.getElementById('modifyRankPoints').innerText,
    tabPointsText: document.getElementById('tabPointsAvailable') && document.getElementById('tabPointsAvailable').innerText
  }));
}
function assertSnapshotEqual(a, b, where) {
  assert.deepStrictEqual(b.ranks, a.ranks, where + ': ranks changed');
  assert.strictEqual(b.rankPoints, a.rankPoints, where + ': remaining points changed');
  assert.deepStrictEqual(b.pointsTree, a.pointsTree, where + ': per-tree points changed');
  assert.deepStrictEqual(b.pointsTier, a.pointsTier, where + ': per-tier points changed');
  assert.strictEqual(b.levelRequired, a.levelRequired, where + ': required level changed');
  assert.strictEqual(b.pointsAvailableText, a.pointsAvailableText, where + ': points-left text changed');
  assert.strictEqual(b.tabPointsText, a.tabPointsText, where + ': spent-points text changed');
}
async function oneSequence(context, pf, seq, runDir, report, events) {
  const page = await context.newPage();
  const row = {
    geometry: seq.geometry, class: seq.class, page: seq.url,
    parent: { index: seq.parent_index, name: seq.parent, required_rank: seq.required_parent_rank },
    child: { index: seq.edge_child_index, name: seq.edge_child, correction: seq.correction || null },
    status: 'running', screenshots: []
  };
  report.sequence_results.push(row);
  page.on('pageerror', error => events.pageErrors.push({ page: seq.url, error: String(error) }));
  page.on('requestfailed', request => {
    const entry = expectedTarget(request.url(), pf.basePath, events.byTarget, events.byOutput);
    const route = normalizeRoutePath(request.url(), pf.basePath);
    if (entry || /\/arrows\/down-3-(?:grey|green|yellow)\.gif$/.test(route || '')) {
      events.resourceFailures.push({ page: seq.url, url: request.url(), target_route: entry ? entry.target_route : route, error: request.failure() && request.failure().errorText });
    }
  });
  try {
    const pageUrl = new URL(seq.url.replace(/^\//, ''), pf.baseURL).href;
    const response = await page.goto(pageUrl, { waitUntil: 'load', timeout: 60000 });
    assert(response && response.status() === 200, 'Talent page did not return 200: ' + pageUrl);
    await page.waitForFunction(index => typeof window.rankTopOnClick === 'function' && document.getElementById('arrowGreen' + index), seq.edge_child_index, { timeout: 30000 });
    await page.locator('img[onclick*="rankTopOnClick(' + seq.edge_child_index + ')"]').last().scrollIntoViewIfNeeded();
    const before = await page.evaluate(({ child, parent }) => ({
      parentData: JSON.stringify(window.talent[parent]), childData: JSON.stringify(window.talent[child]),
      requirement: window.talent[child][5] ? Array.from(window.talent[child][5]) : null,
      childName: window.talent[child][1], parentName: window.talent[parent][1], childMaxRank: window.talent[child][2]
    }), { child: seq.edge_child_index, parent: seq.parent_index });
    assert.deepStrictEqual(before.requirement, [seq.parent_index, seq.required_parent_rank], seq.geometry + ': source prerequisite data changed');
    assert.strictEqual(before.childName, seq.edge_child, seq.geometry + ': child name mismatch');
    assert.strictEqual(before.parentName, seq.parent, seq.geometry + ': parent name mismatch');

    let state = await readTargetState(page, seq, 'grey');
    assertLayerStack(state, pf.byTarget, seq.geometry);
    assert(visible(state, 'grey') && !visible(state, 'green') && !visible(state, 'yellow'), seq.geometry + ': initial state is not grey-only');
    assert.strictEqual(state.ranks.parent, 0);
    assert.strictEqual(state.ranks.child, 0);
    row.initial_state = { visibility: state.visibility, points: state.points, requirement: state.requirement };
    row.screenshots.push(await saveScreenshot(page, runDir, seq, 'grey', state));

    const setupEvents = await applyLegalRanks(page, seq.green_setup, seq.geometry + ' green setup');
    row.legal_rank_events = setupEvents;
    const setupSpent = seq.green_setup.reduce((sum, pair) => sum + pair[1], 0);
    await page.waitForTimeout(80);
    state = await readTargetState(page, seq, 'green');
    assertLayerStack(state, pf.byTarget, seq.geometry);
    assert.strictEqual(state.ranks.parent, seq.required_parent_rank, seq.geometry + ': prerequisite rank is not exact');
    assert.strictEqual(state.ranks.child, 0);
    assert.deepStrictEqual(state.requirement, { parentIndex: seq.parent_index, requiredRank: seq.required_parent_rank });
    assert(visible(state, 'grey') && visible(state, 'green') && !visible(state, 'yellow'), seq.geometry + ': green stage layers mismatch');
    assert.strictEqual(state.points.remaining, 61 - setupSpent, seq.geometry + ': green-stage point total mismatch');
    row.parent_tooltip = await captureTooltip(page, seq.parent_index, seq.parent, null, null);
    row.child_tooltip = await captureTooltip(page, seq.edge_child_index, seq.edge_child, seq.parent, seq.required_parent_rank);
    row.green_state = { visibility: state.visibility, points: state.points, ranks: { parent: state.ranks.parent, child: state.ranks.child } };
    row.screenshots.push(await saveScreenshot(page, runDir, seq, 'green', state));
    const firstClick = await applyLegalRanks(page, [[seq.edge_child_index, 1]], seq.geometry + ' first child rank');
    row.legal_rank_events = row.legal_rank_events.concat(firstClick);
    await page.waitForTimeout(80);
    state = await readTargetState(page, seq, 'yellow');
    assertLayerStack(state, pf.byTarget, seq.geometry);
    assert.strictEqual(state.ranks.parent, seq.required_parent_rank, seq.geometry + ': parent rank changed after child click');
    assert.strictEqual(state.ranks.child, 1, seq.geometry + ': first child rank missing');
    assert(visible(state, 'yellow') && visible(state, 'green'), seq.geometry + ': expected green/yellow overlap after first child rank');
    assert.deepStrictEqual(state.requirement, { parentIndex: seq.parent_index, requiredRank: seq.required_parent_rank });
    const rects = { grey: state.grey.rect, green: state.green.rect, yellow: state.yellow.rect };
    assert.deepStrictEqual(rects.green, rects.grey, seq.geometry + ': green arrow frame geometry changed');
    assert.deepStrictEqual(rects.yellow, rects.grey, seq.geometry + ': yellow arrow frame geometry changed');
    const contact = contactMetrics(seq.geometry, state);
    assertGeometryPosition(seq.geometry, state, contact);
    row.yellow_state = { visibility: state.visibility, points: state.points, ranks: { parent: state.ranks.parent, child: state.ranks.child }, geometry_contact_px: contact };
    row.screenshots.push(await saveScreenshot(page, runDir, seq, 'yellow', state));

    const maxRank = before.childMaxRank;
    assert(maxRank >= 1);
    if (maxRank > 1) {
      const extra = Array.from({ length: maxRank - 1 }, () => [seq.edge_child_index, 1]);
      row.legal_rank_events = row.legal_rank_events.concat(await applyLegalRanks(page, extra, seq.geometry + ' complete target ranks'));
    }
    const complete = await getSnapshot(page);
    assert.strictEqual(complete.ranks[seq.edge_child_index], maxRank);
    assert.strictEqual(complete.ranks[seq.parent_index], seq.required_parent_rank);
    assert.strictEqual(complete.rankPoints, 61 - setupSpent - maxRank, seq.geometry + ': point total before save mismatch');
    const saved = await page.evaluate(() => {
      const digits = document.getElementById('copyURL') && document.getElementById('copyURL').innerText;
      if (!digits) throw new Error('The original save-template digits are empty');
      return {
        digits: digits,
        link: new URL(window.location.pathname + '?' + digits, window.location.href).href,
        label: document.getElementById('copyURL').parentElement.innerText
      };
    });
    assert.strictEqual(saved.digits, complete.ranks.join(''), seq.geometry + ': displayed save digits do not match live ranks');
    row.saved_link = saved;
    await page.goto(saved.link, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction(index => typeof window.rankTopOnClick === 'function' && window.rankTop[index] && window.rankTop[index][0] > 0, seq.edge_child_index, { timeout: 30000 });
    const reloaded = await getSnapshot(page);
    assertSnapshotEqual(complete, reloaded, seq.geometry + ' save-link reload');
    assert.strictEqual(new URL(page.url()).search.slice(1), saved.digits);
    const savedState = await readTargetState(page, seq, 'saved-complete');
    assertLayerStack(savedState, pf.byTarget, seq.geometry);
    assert.strictEqual(savedState.ranks.parent, seq.required_parent_rank);
    assert.strictEqual(savedState.ranks.child, maxRank);
    assert(visible(savedState, 'yellow') && !visible(savedState, 'green'), seq.geometry + ': saved max-rank state should restore yellow-only');
    row.save_reload = {
      query_digits: saved.digits, ranks_equal: true, points_before: complete,
      points_after: reloaded, restored_arrow_visibility: savedState.visibility,
      saved_target_max_rank: maxRank
    };

    const resetControl = page.locator('a[onclick*="resetTreeAll"]').first();
    assert((await resetControl.count()) > 0, seq.geometry + ': original reset-all control missing');
    await resetControl.click({ force: true });
    await page.waitForTimeout(80);
    const reset = await getSnapshot(page);
    assert(reset.ranks.every(rank => rank === 0), seq.geometry + ': reset-all left talent ranks');
    assert.strictEqual(reset.rankPoints, 61, seq.geometry + ': reset-all did not restore all points');
    assert(reset.pointsTree.every(points => points === 0), seq.geometry + ': reset-all left tree points');
    assert(reset.pointsTier.every(row => row.every(points => points === 0)), seq.geometry + ': reset-all left tier points');
    const resetState = await readTargetState(page, seq, 'reset-grey');
    assertLayerStack(resetState, pf.byTarget, seq.geometry);
    assert(visible(resetState, 'grey') && !visible(resetState, 'green') && !visible(resetState, 'yellow'), seq.geometry + ': reset did not restore grey-only');
    row.reset = { all_ranks_zero: true, remaining_points: reset.rankPoints, tree_points: reset.pointsTree, arrow_visibility: resetState.visibility };
    row.status = 'passed';
  } catch (error) {
    row.status = 'failed'; row.failure = String(error); row.stack = error.stack; throw error;
  } finally { await page.close(); }
}

async function heldDown3Control(context, pf, report, events) {
  const page = await context.newPage();
  const row = {
    geometry: 'down-3', class: 'paladin', page: '/info/classes/paladin/talents.html',
    purpose: 'retain corrected legal talent allocation while all 3 down-3 arrows stay excluded',
    corrected_setup: [[43, 5], [46, 5], [48, 5], [53, 3], [52, 2], [54, 3], [55, 1], [56, 1]],
    status: 'running'
  };
  report.held_down3_control = row;
  page.on('pageerror', error => events.pageErrors.push({ page: row.page, error: String(error) }));
  try {
    const response = await page.goto(new URL(row.page.replace(/^\//, ''), pf.baseURL).href, { waitUntil: 'load', timeout: 60000 });
    assert(response && response.status() === 200, 'Held down-3 control page did not return 200');
    await page.waitForFunction(() => typeof window.rankTopOnClick === 'function' && window.talent[57] && window.rankTop[57], null, { timeout: 30000 });
    row.rank_events = await applyLegalRanks(page, row.corrected_setup, 'corrected held down-3 green setup');
    const data = await page.evaluate(() => ({
      prerequisite: window.talent[57][5] ? Array.from(window.talent[57][5]) : null,
      parentRank: window.rankTop[48][0], childRank: window.rankTop[57][0],
      childName: window.talent[57][1], parentName: window.talent[48][1],
      rankPoints: window.rankPoints,
      greenVisible: getComputedStyle(document.getElementById('arrowGreen57')).visibility === 'visible',
      greenImageSrc: document.getElementById('arrowGreen57').querySelector('img').getAttribute('src')
    }));
    assert.deepStrictEqual(data.prerequisite, [48, 5]);
    assert.strictEqual(data.parentRank, 5);
    assert.strictEqual(data.childRank, 0);
    assert.strictEqual(data.childName, 'Vengeance');
    assert.strictEqual(data.parentName, 'Conviction');
    assert.strictEqual(data.rankPoints, 36, 'Corrected setup should spend 25 points');
    assert.strictEqual(data.greenVisible, true, 'Corrected setup should make down-3 child eligible');
    row.runtime_check = data;
    row.excluded_routes = [
      '/shared/global/talents/images/talents/arrows/down-3-grey.gif',
      '/shared/global/talents/images/talents/arrows/down-3-green.gif',
      '/shared/global/talents/images/talents/arrows/down-3-yellow.gif'
    ];
    row.no_down3_map_or_catalog_entry = row.excluded_routes.every(route => !pf.byTarget.has(route) && !pf.catalog.assets.some(asset => asset.target_route === route));
    assert(row.no_down3_map_or_catalog_entry);
    await page.locator('a[onclick*="resetTreeAll"]').first().click({ force: true });
    const afterReset = await getSnapshot(page);
    assert(afterReset.ranks.every(rank => rank === 0) && afterReset.rankPoints === 61);
    row.reset = { all_ranks_zero: true, remaining_points: 61 };
    row.status = 'passed';
  } catch (error) {
    row.status = 'failed'; row.failure = String(error); row.stack = error.stack; throw error;
  } finally { await page.close(); }
}
function uniqueErrors(items) {
  const seen = new Set(), out = [];
  for (const item of items) {
    const key = [item.target_route, item.status, item.category].join('|');
    if (!seen.has(key)) { seen.add(key); out.push(item); }
  }
  return out;
}
async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) { process.stdout.write(helpText() + '\n'); return; }
  if (!opts.baseUrl) fail('Required --base-url is missing');
  if (!opts.exportRoot) fail('Required --export-root is missing');
  const baseUrl = new URL(opts.baseUrl);
  const allowedHosts = new Set(['127.0.0.1', 'localhost', '[::1]', '::1']);
  if (!['http:', 'https:'].includes(baseUrl.protocol) || !allowedHosts.has(baseUrl.hostname)) fail('baseURL must be loopback-only: ' + baseUrl.origin);
  if (baseUrl.search || baseUrl.hash) fail('baseURL cannot contain query or fragment');
  if (!baseUrl.pathname.endsWith('/')) baseUrl.pathname += '/';
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const runDir = opts.evidenceDir ? path.resolve(opts.evidenceDir) : path.join(__dirname, 'runs', 'v54-' + stamp);
  if (!isWithin(__dirname, runDir)) fail('evidence-dir must remain inside owned v54-browser directory');
  fs.mkdirSync(runDir, { recursive: true });
  process.env.TEMP = path.join(ROOT, '.scratch/test-temp-20261022');
  process.env.TMP = process.env.TEMP;
  process.env.TMPDIR = process.env.TEMP;
  fs.mkdirSync(process.env.TEMP, { recursive: true });

  const report = {
    schema: 'wow-v54-talent-ui-browser-acceptance/v1',
    prepared_script: path.relative(ROOT, __filename).split(path.sep).join('/'),
    started_utc: new Date().toISOString(),
    run_directory: path.relative(ROOT, runDir).split(path.sep).join('/'),
    run_mode: opts.preflightOnly ? 'preflight-only' : (opts.headed ? 'headed-real-browser' : 'headless-real-browser'),
    response_policy: 'loopback only; local requests continue unchanged; off-origin requests abort; no response replacement',
    production_export_verified: false, sequence_results: [], asset_response_checks: [],
    non_arrow_http_errors: { known_baseline: [], unexpected: [] },
    unexpected_arrow_http_errors: [],
    held_down3_http_errors: [],
    external_requests: [], page_errors: [], resource_failures: []
  };
  let browser = null, context = null, pf = null, events = null;
  try {
    pf = preflight(opts, baseUrl);
    report.baseURL = pf.baseURL;
    report.exportRoot = pf.exportRoot;
    report.pinned_inputs = {
      map_sha256: pf.mapSha256, decision_sha256: pf.decisionSha256,
      source_acceptance_sha256: pf.sourceAcceptanceSha256, arrow_audit_sha256: pf.auditSha256,
      known_v53_missing_targets_sha256: KNOWN_GAPS_SHA,
      accepted_arrow_geometries: GEOMETRIES, accepted_arrow_count: 18,
      held_down3_routes: pf.decision.root_visual_selection.held.map(item => item.target_route),
      source_classification: pf.map.source.classification,
      original_capture_timestamp: pf.map.source.original_capture_timestamp
    };
    report.export_preflight = {
      catalog_ui_count: pf.catalog.ui_count, route_map_base_path: pf.basePath,
      all_24_disk_payloads_match: true, all_24_catalog_aliases_match: true
    };
    report.baseline_non_arrow_gap_reference = {
      source: BASELINE_PATH, observed_error_count: pf.baselineErrorObservations,
      unique_known_routes: pf.baselineKnownNonArrowRoutes
    };
    if (opts.preflightOnly) {
      report.status = 'preflight_passed_only';
      report.production_export_verified = false;
      return;
    }

    browser = await chromium.launch({ headless: !opts.headed, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
    context = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1480, height: 1250 }, deviceScaleFactor: 1 });
    const byTarget = entryMap(pf.map.entries, 'target_route');
    const byOutput = entryMap(pf.map.entries, 'route');
    events = {
      byTarget: byTarget, byOutput: byOutput, responseTasks: [], responseRecords: [],
      httpErrors: [], heldDown3Responses: [], missingFallbacks: [], pageErrors: report.page_errors,
      external: report.external_requests, resourceFailures: report.resource_failures,
      baselineSet: new Set(pf.baselineKnownNonArrowRoutes), basePath: pf.basePath
    };
    await context.route('**/*', async route => {
      const request = route.request(), u = new URL(request.url());
      if (['data:', 'blob:', 'about:'].includes(u.protocol)) return route.continue();
      if (u.origin !== baseUrl.origin) {
        events.external.push({ url: request.url(), resource_type: request.resourceType() });
        return route.abort();
      }
      return route.continue();
    });
    context.on('page', page => {
      page.on('response', response => {
        const task = (async () => {
          const responseUrl = response.url(), requestUrl = response.request().url();
          const entry = expectedTarget(responseUrl, pf.basePath, byTarget, byOutput) || expectedTarget(requestUrl, pf.basePath, byTarget, byOutput);
          const requestedRoute = normalizeRoutePath(requestUrl, pf.basePath) || normalizeRoutePath(responseUrl, pf.basePath);
          let fallbackPath = false;
          try { fallbackPath = new URL(responseUrl).pathname.endsWith('/__offline/missing-image.svg'); } catch (_) {}
          if (fallbackPath) {
            const routeName = entry ? entry.target_route : requestedRoute;
            const category = entry && /\/arrows\//.test(entry.target_route) ? 'unexpected_arrow_response' : classifyGap(routeName, events.baselineSet);
            events.missingFallbacks.push({
              target_route: routeName, request_url: requestUrl, response_url: responseUrl,
              status: response.status(), category: category
            });
          }
          if (/\/arrows\/down-3-(?:grey|green|yellow)\.gif$/.test(requestedRoute || '')) {
            events.heldDown3Responses.push({
              target_route: requestedRoute, request_url: requestUrl, response_url: responseUrl,
              status: response.status(), content_type: response.headers()['content-type'] || null,
              excluded_from_map: true
            });
          }
          if (response.status() >= 400) {
            const routeName = entry ? entry.target_route : requestedRoute;
            const category = entry && /\/arrows\//.test(entry.target_route) ? 'unexpected_arrow_response' : classifyGap(routeName, events.baselineSet);
            events.httpErrors.push({ request_url: requestUrl, response_url: responseUrl, status: response.status(), target_route: routeName, category: category });
            return;
          }
          if (!entry) return;
          const body = await response.body(), headers = response.headers();
          events.responseRecords.push({
            target_route: entry.target_route, expected_output_route: entry.route,
            request_url: requestUrl, response_url: responseUrl, status: response.status(),
            length: body.length, sha256: sha256(body), git_blob_sha1: gitBlobSha1(body),
            content_type: headers['content-type'] || null,
            expected_mime: 'image/' + entry.format.toLowerCase(),
            expected_length: entry.length, expected_sha256: entry.sha256,
            expected_git_blob_sha1: entry.git_blob_sha1,
            expected_dimensions: { width: entry.width, height: entry.height },
            expected_frames: entry.frames
          });
        })().catch(error => events.resourceFailures.push({ url: response.url(), error: String(error) }));
        events.responseTasks.push(task);
      });
    });

    for (const seq of selectedSequences(pf.audit)) await oneSequence(context, pf, seq, runDir, report, events);
    await heldDown3Control(context, pf, report, events);
    await Promise.all(events.responseTasks);
    report.asset_response_checks = events.responseRecords;
    report.http_errors = events.httpErrors;
    report.held_down3_responses = events.heldDown3Responses;
    report.missing_image_fallbacks = events.missingFallbacks;
    report.page_errors = events.pageErrors;
    report.resource_failures = events.resourceFailures;
    for (const error of events.httpErrors) {
      if (error.category === 'expected_held_down3') report.held_down3_http_errors.push(error);
      else if (error.category === 'unexpected_arrow_response') report.unexpected_arrow_http_errors.push(error);
      else if (error.category === 'known_baseline_non_arrow_gap') report.non_arrow_http_errors.known_baseline.push(error);
      else report.non_arrow_http_errors.unexpected.push(error);
    }
    for (const fallback of events.missingFallbacks) {
      if (fallback.category === 'expected_held_down3') continue;
      if (fallback.category === 'unexpected_arrow_response') report.unexpected_arrow_http_errors.push(fallback);
      else if (fallback.category === 'known_baseline_non_arrow_gap') report.non_arrow_http_errors.known_baseline.push(fallback);
      else report.non_arrow_http_errors.unexpected.push(fallback);
    }
    const arrowRecords = events.responseRecords.filter(record => /\/arrows\//.test(record.target_route));
    const arrowRoutesSeen = uniqueSorted(arrowRecords.map(record => record.target_route));
    const checks = pf.expectedArrowRoutes.map(route => {
      const entry = byTarget.get(route), rows = arrowRecords.filter(record => record.target_route === route);
      const exact = rows.some(row => row.status === 200 && row.length === entry.length &&
        row.sha256 === entry.sha256 && row.git_blob_sha1 === entry.git_blob_sha1 &&
        String(row.content_type || '').split(';')[0].trim().toLowerCase() === ('image/' + entry.format.toLowerCase()));
      return { target_route: route, observed_response_count: rows.length, exact_response_match: exact };
    });
    report.arrow_response_coverage = {
      expected_selected_arrow_count: 18, observed_unique_selected_arrow_count: arrowRoutesSeen.length,
      observed_selected_arrow_targets: arrowRoutesSeen, checks: checks,
      all_18_actual_responses_match_map: checks.every(item => item.exact_response_match)
    };
    report.other_ui_asset_responses = events.responseRecords.filter(record => !/\/arrows\//.test(record.target_route));
    report.non_arrow_http_errors.known_baseline = uniqueErrors(report.non_arrow_http_errors.known_baseline);
    report.non_arrow_http_errors.unexpected = uniqueErrors(report.non_arrow_http_errors.unexpected);
    report.unexpected_arrow_http_errors = uniqueErrors(report.unexpected_arrow_http_errors);
    report.held_down3_http_errors = uniqueErrors(report.held_down3_http_errors);
    report.summary = {
      accepted_sequences_passed: report.sequence_results.filter(row => row.status === 'passed').length,
      expected_accepted_sequences: 6,
      held_down3_control_passed: report.held_down3_control && report.held_down3_control.status === 'passed',
      exact_arrow_responses: checks.filter(item => item.exact_response_match).length,
      expected_arrow_responses: checks.length,
      known_baseline_non_arrow_gap_routes: uniqueSorted(report.non_arrow_http_errors.known_baseline.map(item => item.target_route)).length,
      held_down3_http_errors: report.held_down3_http_errors.length,
      held_down3_missing_image_fallbacks: report.missing_image_fallbacks.filter(item => item.category === 'expected_held_down3').length,
      unexpected_new_non_arrow_http_errors: report.non_arrow_http_errors.unexpected.length,
      unexpected_arrow_http_errors: report.unexpected_arrow_http_errors.length,
      external_requests_aborted: report.external_requests.length,
      page_errors: report.page_errors.length, failed_resource_reads: report.resource_failures.length
    };
    assert.strictEqual(report.summary.accepted_sequences_passed, 6, 'Not all six accepted sequences passed');
    assert.strictEqual(report.summary.held_down3_control_passed, true, 'Corrected held down-3 data control failed');
    assert.strictEqual(report.summary.exact_arrow_responses, 18, 'Not all selected arrow responses match the v2 map');
    assert.strictEqual(report.non_arrow_http_errors.unexpected.length, 0, 'Unexpected new non-arrow HTTP errors outside the known baseline');
    assert.strictEqual(report.unexpected_arrow_http_errors.length, 0, 'Unexpected selected-arrow HTTP error');
    assert.strictEqual(report.external_requests.length, 0, 'A non-loopback request was attempted');
    assert.strictEqual(report.page_errors.length, 0, 'Browser page errors occurred');
    assert.strictEqual(report.resource_failures.length, 0, 'Image response/request failures occurred');
    report.status = 'browser_checks_passed_pending_parent_visual_acceptance';
    report.production_export_verified = false;
  } catch (error) {
    report.status = 'failed';
    report.failure = String(error);
    report.stack = error.stack;
    if (events) {
      await Promise.allSettled(events.responseTasks);
      report.asset_response_checks = events.responseRecords;
      report.http_errors = events.httpErrors;
      report.held_down3_responses = events.heldDown3Responses;
      report.missing_image_fallbacks = events.missingFallbacks;
      report.held_down3_http_errors = events.httpErrors.filter(item => item.category === 'expected_held_down3');
      report.unexpected_arrow_http_errors = events.httpErrors.filter(item => item.category === 'unexpected_arrow_response');
      report.page_errors = events.pageErrors;
      report.resource_failures = events.resourceFailures;
    }
    process.exitCode = 1;
  } finally {
    if (context) await context.close();
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    const receipt = path.join(runDir, 'browser-acceptance.json');
    fs.writeFileSync(receipt, JSON.stringify(report, null, 2) + '\n');
    process.stdout.write(JSON.stringify({ status: report.status || 'failed', receipt: receipt, summary: report.summary || null, failure: report.failure || null }) + '\n');
  }
}
main().catch(error => { process.stderr.write(String(error) + '\n'); process.exitCode = 1; });

