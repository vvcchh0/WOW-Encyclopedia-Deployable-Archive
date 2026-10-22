'use strict';

// Real-Chrome acceptance for the v55 related talent icon mapping.
// It reads the real export and lets every same-origin request continue; it
// never fulfills, substitutes, or rewrites an image response.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const MAP_PATH = 'research/continuous-recovery-20261022/integration/related-talent-icons-v55/input-map.json';
const DECISION_PATH = 'research/continuous-recovery-20261022/integration/related-talent-icons-v55/decision.json';
const PINS_PATH = 'research/continuous-recovery-20261022/integration/related-talent-icons-v55/root-input-pins.json';
const BASE_MAP_PATH = 'research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json';
const ACCEPTANCE_PATH = 'research/continuous-recovery-20261021/publication/root-talent-related-source-acceptance.json';
const AUDIT_PATH = 'research/continuous-recovery-20261022/talent-icon-reuse-audit/audit.json';
const KNOWN_GAPS_PATH = 'research/continuous-recovery-20261022/v53-known-missing-targets.json';
const EXPECTED = {
  mapSha: 'dbf7e69a081d6769e243c7c8688b46181204102c58a9c933b6388c5197b67d9b',
  decisionSha: 'eeb4706b46d4c5e71015e993bb7b79220d70d44d0201351f2dceb199861d7d24',
  pinsSha: 'b60806d4e4af534f4f7f36362a5375de058c5d54cfcf15a0444d6790892f567d',
  baseMapSha: 'db2295c57b336be03b1fcccdb5a86373e4e95047b4be8e56647a1c2c95970092',
  acceptanceSha: '4f05d6ab9ee61691cd6440ccd549fc756cd99424b3840ff92b0955c5bad53465',
  auditSha: 'fe8b6dfb6229e6c63eefafef778cffaa205b40fca9e8652389f823f64f98b520',
  knownGapsSha: '2eece825655662a6d28e207911b74ea03cb0861a3496dc14da9f474cd4375498',
  repoUrl: 'https://github.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a',
  commitSha: '4c8013cf40d0edf84625430eaf43b86d97880ae0',
  treeSha: 'e8916c038b41c2c29144f5411f8fc6ec5cd032d5',
  sourceBytes: 21820
};
const CLASS_NAMES = ['hunter', 'paladin', 'rogue', 'warrior'];

function sha256(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function gitBlobSha1(bytes) {
  return crypto.createHash('sha1')
    .update(Buffer.from('blob ' + bytes.length + '\0', 'utf8'))
    .update(bytes).digest('hex');
}
function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }
function within(parent, candidate) {
  const rel = path.relative(path.resolve(parent), path.resolve(candidate));
  return rel === '' || (!rel.startsWith('..' + path.sep) && rel !== '..' && !path.isAbsolute(rel));
}
function fail(message) { throw new Error(message); }
function uniqueSorted(values) { return Array.from(new Set(values)).sort(); }
function classFromRoute(route) {
  const match = /^\/shared\/global\/talents\/([^/]+)\/images\/[^/]+\/.+\.jpg$/.exec(route);
  return match ? match[1] : null;
}
function expectedRawUrl(entry) {
  return 'https://raw.githubusercontent.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a/' +
    EXPECTED.commitSha + '/' + entry.repository_path;
}
function parseArgs(argv) {
  const positional = [];
  const options = { headed: false, preflightOnly: false };
  for (const arg of argv) {
    if (arg === '--headed') options.headed = true;
    else if (arg === '--preflight-only') options.preflightOnly = true;
    else if (arg === '--help' || arg === '-h') options.help = true;
    else if (arg.startsWith('-')) fail('Unknown option: ' + arg);
    else positional.push(arg);
  }
  if (!options.help && positional.length !== 2) fail('Expected <port> and <output-dir>');
  options.port = positional[0];
  options.outputDir = positional[1];
  return options;
}
function helpText() {
  return [
    'Usage:',
    '  node browser-check.cjs <port> <output-dir> [--headed] [--preflight-only]',
    '',
    'The server must be loopback-only and serve the supplied real export directory.',
    'The script verifies the pinned v55 map/catalog/disk files, then checks all 10',
    'talents, 20 real image responses, original data tooltips, legal rank clicks,',
    'and save-link reloads. It never replaces responses or edits talent data.'
  ].join('\n');
}
function bytesForJson(file, expectedSha, label) {
  const bytes = fs.readFileSync(file);
  assert.strictEqual(sha256(bytes), expectedSha, label + ' SHA-256 mismatch');
  const value = JSON.parse(bytes.toString('utf8'));
  assert(value && typeof value === 'object' && !Array.isArray(value), label + ' is not a JSON object');
  return { bytes, value };
}
function normalizeRoute(raw, basePath) {
  let url;
  try { url = new URL(raw, 'http://127.0.0.1'); } catch (_) { return null; }
  let pathname;
  try { pathname = decodeURIComponent(url.pathname || '/'); } catch (_) { pathname = url.pathname || '/'; }
  const prefix = String(basePath || '').replace(/\/+$/, '');
  if (prefix && pathname === prefix) pathname = '/';
  else if (prefix && pathname.startsWith(prefix + '/')) pathname = pathname.slice(prefix.length);
  const route = pathname.replace(/\/+$/, '') || '/';
  if (route.endsWith('/missing-image.svg')) {
    const nested = url.searchParams.get('requested') || url.searchParams.get('source');
    if (nested) return normalizeRoute(nested, basePath);
  }
  return route;
}
function createPreflight(port, outputDir) {
  const baseMapFile = path.join(ROOT, BASE_MAP_PATH);
  const mapResult = bytesForJson(path.join(ROOT, MAP_PATH), EXPECTED.mapSha, 'v55 input map');
  const decisionResult = bytesForJson(path.join(ROOT, DECISION_PATH), EXPECTED.decisionSha, 'v55 decision');
  const pinsResult = bytesForJson(path.join(ROOT, PINS_PATH), EXPECTED.pinsSha, 'v55 root input pins');
  const baseMapResult = bytesForJson(baseMapFile, EXPECTED.baseMapSha, 'v1 base map');
  const acceptanceResult = bytesForJson(path.join(ROOT, ACCEPTANCE_PATH), EXPECTED.acceptanceSha, 'source acceptance');
  const auditResult = bytesForJson(path.join(ROOT, AUDIT_PATH), EXPECTED.auditSha, 'semantic audit');
  const map = mapResult.value, decision = decisionResult.value, pins = pinsResult.value;
  const baseMap = baseMapResult.value, acceptance = acceptanceResult.value, audit = auditResult.value;

  assert.strictEqual(map.schema, 'wow-related-talent-icon-map/v2');
  assert.strictEqual(map.base_map, BASE_MAP_PATH);
  assert.strictEqual(map.base_map_sha256, EXPECTED.baseMapSha);
  assert.strictEqual(map.decision, DECISION_PATH);
  assert.strictEqual(map.decision_sha256, EXPECTED.decisionSha);
  assert.strictEqual(map.source_acceptance, ACCEPTANCE_PATH);
  assert.strictEqual(map.source_acceptance_sha256, EXPECTED.acceptanceSha);
  assert.strictEqual(map.semantic_audit, AUDIT_PATH);
  assert.strictEqual(map.semantic_audit_sha256, EXPECTED.auditSha);
  assert.strictEqual(map.base_icon_count, 986);
  assert.strictEqual(map.mapped_icon_count, 20);
  assert.strictEqual(map.icon_count, 1006);
  assert.strictEqual(map.mapped_source_bytes, EXPECTED.sourceBytes);
  assert.deepStrictEqual(map.source, decision.source);
  assert.strictEqual(map.source.repository_url, EXPECTED.repoUrl);
  assert.strictEqual(map.source.commit_sha, EXPECTED.commitSha);
  assert.strictEqual(map.source.tree_sha, EXPECTED.treeSha);
  assert.strictEqual(map.source.classification, 'later_related_source');
  assert.strictEqual(map.source.original_capture_timestamp, null);
  assert.strictEqual(decision.schema, 'wow-related-talent-icon-decision/v2');
  assert.strictEqual(decision.accepted_for_derived_trial, true);
  assert.strictEqual(decision.original_2008_images_recovered, 0);
  assert.strictEqual(decision.images_reencoded, false);
  assert.strictEqual(acceptance.accepted_source, true);
  assert.strictEqual(acceptance.original_2008_images_recovered, 0);
  assert.strictEqual(acceptance.raw_images_reencoded, false);
  assert.strictEqual(baseMap.icon_count, 986);
  assert.strictEqual(baseMap.entries.length, 986);
  assert.deepStrictEqual(pins, {
    map_sha256: EXPECTED.mapSha,
    decision_sha256: EXPECTED.decisionSha,
    base_map_sha256: EXPECTED.baseMapSha,
    semantic_audit_sha256: EXPECTED.auditSha,
    source_acceptance_sha256: EXPECTED.acceptanceSha,
    base_icon_count: 986,
    mapped_icon_count: 20,
    icon_count: 1006,
    mapped_source_bytes: EXPECTED.sourceBytes,
    new_network_requests: 0,
    images_reencoded: false
  });
  assert.strictEqual(audit.schema, 'wow-talent-icon-reuse-audit/v1');
  assert.strictEqual(audit.conclusion.strong_same_class_candidates, 10);
  assert.strictEqual(audit.conclusion.confirmed_2008_image_recoveries, 0);
  assert.strictEqual(audit.conclusion.automatic_aliases_created, 0);
  assert.strictEqual(map.entries.length, 20);
  assert.deepStrictEqual(map.entries, decision.entries);

  const recommendations = new Map(audit.recommendations.map(row => [row.id, row]));
  assert.strictEqual(recommendations.size, 10);
  const entriesByRoute = new Map();
  const entriesByMapping = new Map();
  const targetRoutes = new Set();
  const sourcePaths = new Set();
  let mappedBytes = 0;
  for (const entry of map.entries) {
    assert.strictEqual(entry.route, entry.route.trim());
    assert.strictEqual(entry.classification, 'later_related_source');
    assert.strictEqual(entry.original_capture_timestamp, null);
    assert.strictEqual(entry.original_2008_pixel_identity, 'unknown');
    assert.strictEqual(entry.format, 'JPEG');
    assert.strictEqual(entry.width, 36);
    assert.strictEqual(entry.height, 36);
    assert.strictEqual(entry.frames, 1);
    assert.strictEqual(classFromRoute(entry.route), entry.class);
    assert(!targetRoutes.has(entry.route), 'Duplicate v55 target ' + entry.route);
    assert(!sourcePaths.has(entry.repository_path), 'Duplicate source path ' + entry.repository_path);
    targetRoutes.add(entry.route);
    sourcePaths.add(entry.repository_path);
    assert(!baseMap.entries.some(base => base.route === entry.route), 'v2 target collides with v1 ' + entry.route);
    const recommendation = recommendations.get(entry.mapping_id);
    assert(recommendation, 'No semantic audit recommendation for ' + entry.mapping_id);
    assert.strictEqual(entry.class, recommendation.old_target.class);
    assert.strictEqual(entry.talent, recommendation.old_target.talent);
    assert(recommendation.old_target.routes.includes(entry.route), 'Target differs from same-class audit route');
    assert.strictEqual(entry.mapping_reason, recommendation.reason);
    const laterImage = recommendation.later_images.find(item => item.state === entry.state);
    assert(laterImage && laterImage.evidence_id === entry.repository_path, 'Source path differs from semantic audit');
    assert.strictEqual(entry.old_data_sha256, recommendation.old_target.old_data_evidence.v52_sha256);
    assert.deepStrictEqual(entry.old_data_talent_lines, recommendation.old_target.old_data_evidence.talent_assignment_lines);
    assert.strictEqual(entry.later_data_sha256, recommendation.later_talent.data_evidence.sha256);
    assert.deepStrictEqual(entry.later_data_talent_lines, recommendation.later_talent.data_evidence.talent_assignment_lines);
    assert.strictEqual(entry.page_route, '/info/classes/' + entry.class + '/talents.html');
    assert.strictEqual(entry.old_data_route, '/shared/global/talents/' + entry.class + '/data.js');
    assert.strictEqual(entry.source_image_url, undefined, 'Input map must not grow an unpinned URL field');
    assert(/^shared\/global\/talents\/[^/]+\/images\/.+\.jpg$/.test(entry.repository_path));
    assert.strictEqual(entry.repository_path.split('/')[3], entry.class, 'Source path crosses classes');
    assert.strictEqual(entry.state === 'off', /-off\.jpg$/.test(entry.route));
    const payloadPath = path.resolve(ROOT, entry.payload_path);
    assert(within(ROOT, payloadPath), 'Payload path escapes workspace');
    const sourceBytes = fs.readFileSync(payloadPath);
    assert.strictEqual(sourceBytes.length, entry.length, 'Pinned source length mismatch: ' + entry.route);
    assert.strictEqual(sha256(sourceBytes), entry.sha256, 'Pinned source SHA mismatch: ' + entry.route);
    assert.strictEqual(gitBlobSha1(sourceBytes), entry.git_blob_sha1, 'Pinned source blob mismatch: ' + entry.route);
    mappedBytes += sourceBytes.length;
    entriesByRoute.set(entry.route, entry);
    if (!entriesByMapping.has(entry.mapping_id)) entriesByMapping.set(entry.mapping_id, []);
    entriesByMapping.get(entry.mapping_id).push(entry);
  }
  assert.strictEqual(mappedBytes, EXPECTED.sourceBytes);
  assert.strictEqual(entriesByMapping.size, 10);
  for (const [mappingId, pair] of entriesByMapping) {
    assert.strictEqual(pair.length, 2, mappingId + ' must have on/off entries');
    assert.deepStrictEqual(uniqueSorted(pair.map(row => row.state)), ['off', 'on']);
    assert.strictEqual(pair[0].class, pair[1].class);
    assert.strictEqual(pair[0].talent, pair[1].talent);
  }
  assert.deepStrictEqual(uniqueSorted(Array.from(new Set(map.entries.map(row => row.class)))), CLASS_NAMES.slice().sort());

  const exportRoot = path.resolve(ROOT, outputDir);
  assert(fs.statSync(exportRoot).isDirectory(), 'output-dir is not an existing export directory: ' + exportRoot);
  const routeMap = readJson(path.join(exportRoot, '__offline', 'route-map.json'));
  const catalog = readJson(path.join(exportRoot, '__offline', 'related-talent-icons.json'));
  const basePath = String(routeMap.base_path || '').replace(/\/+$/, '');
  assert.strictEqual(routeMap.schema, 'github-pages-route-map/v1');
  assert(basePath, 'route-map has no base_path');
  assert.strictEqual(catalog.schema, 'wow-related-talent-icon-catalog/v2');
  assert.strictEqual(catalog.icon_count, 1006);
  assert.strictEqual(catalog.assets.length, 1006);
  assert.strictEqual(catalog.mappings.length, 20);
  assert.strictEqual(catalog.source.map_sha256, EXPECTED.mapSha);
  assert.strictEqual(catalog.source.decision_sha256, EXPECTED.decisionSha);
  assert.strictEqual(catalog.source.base_map_sha256, EXPECTED.baseMapSha);
  assert.strictEqual(catalog.source.semantic_audit_sha256, EXPECTED.auditSha);
  assert.strictEqual(catalog.source.source_acceptance_sha256, EXPECTED.acceptanceSha);
  assert.strictEqual(catalog.source.original_capture_timestamp, null);
  assert.strictEqual(catalog.source.original_2008_images_recovered, 0);
  assert.strictEqual(catalog.source.icon_count, 1006);
  const baseClassCounts = Object.fromEntries(['druid','hunter','mage','paladin','priest','rogue','shaman','warlock','warrior'].map(name => [name, 0]));
  for (const row of baseMap.entries) {
    const match = /^\/shared\/global\/talents\/([^/]+)\/images\//.exec(row.route);
    assert(match && Object.hasOwn(baseClassCounts, match[1]), 'Invalid class in base map: ' + row.route);
    baseClassCounts[match[1]]++;
  }
  for (const entry of map.entries) baseClassCounts[entry.class]++;
  assert.deepStrictEqual(catalog.class_counts, baseClassCounts);
  const catalogAssets = new Map(catalog.assets.map(asset => [asset.route, asset]));
  const catalogMappings = new Map(catalog.mappings.map(mapping => [mapping.target_route, mapping]));
  const browserEntries = [];
  const expectedData = new Map();
  for (const entry of map.entries) {
    const asset = catalogAssets.get(entry.route);
    const mapping = catalogMappings.get(entry.route);
    assert(asset, 'Catalog is missing mapped route ' + entry.route);
    assert(mapping, 'Catalog has no explicit mapping ' + entry.route);
    assert.strictEqual(asset.sha256, entry.sha256);
    assert.strictEqual(asset.length, entry.length);
    assert.strictEqual(asset.mime, 'image/jpeg');
    assert.strictEqual(asset.mapping_id, entry.mapping_id);
    assert.strictEqual(asset.source_repository_path, entry.repository_path);
    assert.strictEqual(asset.mapping_reason, entry.mapping_reason);
    assert.strictEqual(mapping.source_repository_path, entry.repository_path);
    assert.strictEqual(mapping.source_image_url, expectedRawUrl(entry));
    assert.strictEqual(mapping.sha256, entry.sha256);
    assert.strictEqual(mapping.length, entry.length);
    assert.strictEqual(mapping.original_2008_pixel_identity, 'unknown');
    assert.strictEqual(routeMap.routes[entry.route], basePath + entry.route);
    const diskFile = path.resolve(exportRoot, '.' + entry.route);
    assert(within(exportRoot, diskFile), 'Mapped output escapes export root: ' + entry.route);
    const diskBytes = fs.readFileSync(diskFile);
    assert.strictEqual(diskBytes.length, entry.length, 'Export output length mismatch: ' + entry.route);
    assert.strictEqual(sha256(diskBytes), entry.sha256, 'Export output bytes differ from pinned payload: ' + entry.route);
    assert.strictEqual(gitBlobSha1(diskBytes), entry.git_blob_sha1, 'Export output Git blob mismatch: ' + entry.route);
    browserEntries.push({ ...entry, mime: asset.mime });

    const dataRoute = entry.old_data_route;
    const dataFile = path.resolve(exportRoot, '.' + dataRoute);
    assert(within(exportRoot, dataFile), 'Class data path escapes export root: ' + dataRoute);
    const dataBytes = fs.readFileSync(dataFile);
    assert.strictEqual(sha256(dataBytes), entry.old_data_sha256, 'Export changed original class data: ' + dataRoute);
    const existing = expectedData.get(dataRoute);
    if (existing) assert.strictEqual(existing.sha256, entry.old_data_sha256, 'Class entries disagree on old data hash');
    else expectedData.set(dataRoute, { route: dataRoute, sha256: entry.old_data_sha256, length: dataBytes.length, className: entry.class });
  }
  assert.strictEqual(catalogMappings.size, 20);
  for (const [route, expected] of expectedData) {
    assert(routeMap.routes[route], 'Route-map is missing original data route ' + route);
    assert.strictEqual(routeMap.routes[route], basePath + route);
    assert(routeMap.routes['/info/classes/' + expected.className + '/talents.html']);
  }
  const knownResult = bytesForJson(path.join(ROOT, KNOWN_GAPS_PATH), EXPECTED.knownGapsSha, 'known missing-target inventory');
  assert.strictEqual(knownResult.value.count, 390);
  assert.strictEqual(knownResult.value.targets.length, 390);
  const knownMissing = new Set(knownResult.value.targets);
  const portNumber = Number(port);
  assert(Number.isInteger(portNumber) && portNumber > 0 && portNumber <= 65535, 'port must be 1..65535');
  const baseUrl = new URL('http://127.0.0.1:' + portNumber + basePath + '/');
  return {
    exportRoot, basePath, baseUrl, map, decision, pins, catalog, routeMap,
    entries: browserEntries, entriesByRoute, entriesByMapping, expectedData,
    knownMissing, knownMissingCount: knownResult.value.count,
    inputHashes: {
      map: sha256(mapResult.bytes), decision: sha256(decisionResult.bytes),
      pins: sha256(pinsResult.bytes), base_map: sha256(baseMapResult.bytes),
      source_acceptance: sha256(acceptanceResult.bytes), semantic_audit: sha256(auditResult.bytes),
      known_gaps: sha256(knownResult.bytes)
    }
  };
}

async function allocateLegally(page, talentName) {
  return page.evaluate(name => {
    const matches = [];
    for (let i = 0; window.talent[i]; i++) if (window.talent[i][1] === name) matches.push(i);
    if (matches.length !== 1) throw new Error('Expected one original data entry for ' + name + ', found ' + matches.length);
    const target = matches[0];
    const tree = window.talent[target][0];
    const targetTier = window.talent[target][4];
    const targetMax = window.talent[target][2];
    if (!window.rankTopOnClick || !window.canUnlearn || !window.checkRequiredTalent) {
      throw new Error('Original calculator legality handlers are not available');
    }
    if (window.rankTop[target][0] !== 0) throw new Error('Target did not start at rank zero: ' + name);
    const eventLog = [];
    const exactParents = new Map();
    const walkRequirements = (id, active = new Set()) => {
      if (active.has(id)) throw new Error('Cycle in original prerequisite data at talent ' + id);
      active.add(id);
      const req = window.talent[id][5];
      if (req) {
        const parentId = req[0], requiredRank = req[1];
        const previous = exactParents.get(parentId);
        if (previous !== undefined && previous !== requiredRank) {
          throw new Error('Conflicting exact prerequisite ranks for talent ' + parentId);
        }
        exactParents.set(parentId, requiredRank);
        walkRequirements(parentId, active);
      }
      active.delete(id);
    };
    walkRequirements(target);

    const clickOne = (id, why) => {
      const beforeRank = window.rankTop[id][0];
      const beforePoints = window.rankPoints;
      window.rankTopOnClick(id);
      const afterRank = window.rankTop[id][0];
      const afterPoints = window.rankPoints;
      if (afterRank !== beforeRank + 1 || afterPoints !== beforePoints - 1) {
        throw new Error(why + ': original rankTopOnClick rejected talent ' + id +
          ' (rank ' + beforeRank + ' -> ' + afterRank + ', points ' + beforePoints + ' -> ' + afterPoints + ')');
      }
      const event = { talent_index: id, rank_before: beforeRank, rank_after: afterRank,
        points_before: beforePoints, points_after: afterPoints };
      event.reason = why;
      eventLog.push(event);
    };
    const spendTierFiller = (forId, active) => {
      const forTree = window.talent[forId][0];
      const tier = window.talent[forId][4];
      const requiredTreePoints = (tier - 1) * 5;
      let guard = 0;
      while (window.pointsTree[forTree] < requiredTreePoints) {
        if (++guard > 61) throw new Error('Filler allocation exceeded 61-point guard for ' + name);
        const candidates = [];
        for (let i = 0; window.talent[i]; i++) {
          const row = window.talent[i];
          if (row[0] !== forTree || i === forId || row[4] >= tier) continue;
          const rank = window.rankTop[i][0], maxRank = row[2];
          if (rank >= maxRank) continue;
          const exactParentRank = exactParents.get(i);
          if (exactParentRank !== undefined && rank >= exactParentRank) continue;
          if (!window.canUnlearn(i, 0, window.maxTierArray[forTree])) continue;
          candidates.push(i);
        }
        candidates.sort((a, b) => window.talent[a][4] - window.talent[b][4] || a - b);
        if (!candidates.length) throw new Error('No legal lower-tier filler can unlock talent ' + forId + ' (' + name + ')');
        const candidate = candidates[0];
        clickOne(candidate, 'tier filler for ' + name);
      }
    };
    const ensureRank = (id, goal, active = new Set()) => {
      if (active.has(id)) throw new Error('Cycle while resolving prerequisite for ' + name + ' at ' + id);
      const current = window.rankTop[id][0];
      const exact = exactParents.get(id);
      if (exact !== undefined && current > exact) throw new Error('Prerequisite rank exceeded required exact rank for ' + id);
      if (goal > window.talent[id][2]) throw new Error('Requested rank exceeds original talent maximum for ' + id);
      if (current >= goal) return;
      if (current === 0 && window.talent[id][5]) {
        active.add(id);
        const [parentId, requiredRank] = window.talent[id][5];
        ensureRank(parentId, requiredRank, active);
        active.delete(id);
        if (window.rankTop[parentId][0] !== requiredRank) {
          throw new Error('Prerequisite rank is not exact for talent ' + id);
        }
      }
      while (window.rankTop[id][0] < goal) {
        spendTierFiller(id, active);
        clickOne(id, id === target ? 'activate ' + name : 'required prerequisite for ' + name);
        if (exact !== undefined && window.rankTop[id][0] > exact) {
          throw new Error('Required prerequisite was raised above exact rank for ' + id);
        }
        if (window.rankPoints < 0) throw new Error('Original calculator has negative remaining points');
      }
    };
    for (const [parentId, rank] of exactParents) ensureRank(parentId, rank);
    if (window.rankTop[target][0] === 0 && window.talent[target][5]) {
      const [parentId, requiredRank] = window.talent[target][5];
      if (window.rankTop[parentId][0] !== requiredRank) throw new Error('Target prerequisite rank is not exact');
    }
    ensureRank(target, 1);
    if (window.rankTop[target][0] !== 1) throw new Error('Target was not activated at rank one');
    return {
      index: target,
      tree,
      tier: targetTier,
      max_rank: targetMax,
      final_rank: window.rankTop[target][0],
      remaining_points: window.rankPoints,
      tree_points: window.pointsTree[tree],
      prerequisites: exactParents.size ? Array.from(exactParents, ([index, required_rank]) => ({ index, required_rank })) : [],
      legal_rank_events: eventLog
    };
  }, talentName);
}

async function snapshot(page) {
  return page.evaluate(() => ({
    ranks: Array.from({ length: window.talent.length }, (_, i) => window.rankTop[i] ? window.rankTop[i][0] : 0),
    rankPoints: window.rankPoints,
    pointsTree: Array.from(window.pointsTree || []),
    pointsTier: Array.from(window.pointsTier || [], row => Array.from(row || [])),
    targetRanksText: document.getElementById('copyURL') && document.getElementById('copyURL').innerText
  }));
}
function assertSnapshotEqual(before, after, label) {
  assert.deepStrictEqual(after.ranks, before.ranks, label + ': ranks changed');
  assert.strictEqual(after.rankPoints, before.rankPoints, label + ': point total changed');
  assert.deepStrictEqual(after.pointsTree, before.pointsTree, label + ': tree totals changed');
  assert.deepStrictEqual(after.pointsTier, before.pointsTier, label + ': tier totals changed');
  assert.strictEqual(after.targetRanksText, before.targetRanksText, label + ': saved rank digits changed');
}
function normalizeText(value) { return String(value || '').replace(/\s+/g, ' ').trim(); }
async function checkTooltip(page, index, talentName) {
  const control = page.locator('img[onclick*="rankTopOnClick(' + index + ')"]').last();
  assert.strictEqual(await control.count() > 0, true, 'No original talent click/hover target for ' + talentName);
  await control.hover({ force: true });
  await page.waitForFunction(i => {
    const tooltip = document.getElementById('talentMouseOver' + i);
    return tooltip && getComputedStyle(tooltip).visibility === 'visible';
  }, index, { timeout: 5000 });
  const result = await page.evaluate(i => {
    const tooltip = document.getElementById('talentMouseOver' + i);
    const source = document.createElement('div');
    source.innerHTML = window.rank[i][0];
    const description = source.textContent || source.innerText || '';
    const nextSource=document.createElement('div');
    const current=window.rankTop[i][0],maximum=window.talent[i][2];
    if(current>0&&current<maximum)nextSource.innerHTML=window.rank[i][current];
    const displayed = document.getElementById('modifyDescriptionTop' + i);
    const requirement = document.getElementById('requiresTalent' + i);
    return {
      visible: !!tooltip && getComputedStyle(tooltip).visibility === 'visible',
      tooltip_text: tooltip ? tooltip.innerText : '',
      source_first_rank_description: description,
      source_next_rank_description: nextSource.textContent||'',
      next_rank_label: window.textNextRank,
      displayed_rank_description: displayed ? displayed.innerText : '',
      requirement_text: requirement ? requirement.innerText : null,
      source_rank_count: window.rank[i].length,
      current_rank: window.rankTop[i][0],
      max_rank: window.talent[i][2]
    };
  }, index);
  assert(result.visible, 'Tooltip is not visible for ' + talentName);
  assert(result.tooltip_text.includes(talentName), 'Original tooltip omits 2008 talent name ' + talentName);
  const sourceDescription = normalizeText(result.source_first_rank_description);
  assert(sourceDescription.length > 8, 'Original talent data has no usable first-rank description for ' + talentName);
  const expectedDisplayed=normalizeText(sourceDescription+(result.current_rank>0&&result.current_rank<result.max_rank?' '+result.next_rank_label+' '+result.source_next_rank_description:''));
  // Rendered tables and <br> introduce whitespace absent from textContent.
  // Compare every non-whitespace character, including numbers and punctuation.
  const compact=value=>normalizeText(value).replace(/\s+/g,'');
  assert.strictEqual(compact(result.displayed_rank_description), compact(expectedDisplayed),
    'Visible rank text differs from the original rank array for ' + talentName);
  assert(compact(result.tooltip_text).includes(compact(sourceDescription)),
    'Tooltip does not show the original rank description for ' + talentName);
  await page.mouse.move(0, 0);
  return result;
}
async function readImageState(page, entry, basePath, index, expectedRank) {
  const onRoute = entry.route.replace(/-off\.jpg$/, '.jpg');
  const offRoute = entry.route.endsWith('-off.jpg') ? entry.route : entry.route.replace(/\.jpg$/, '-off.jpg');
  const state = await page.evaluate(({ onRoute, offRoute, basePath, index }) => {
    const prefix = String(basePath || '').replace(/\/+$/, '');
    const routeOf = image => {
      let p;
      try { p = decodeURIComponent(new URL(image.currentSrc || image.src, location.href).pathname); }
      catch (_) { return null; }
      if (prefix && p.startsWith(prefix + '/')) p = p.slice(prefix.length);
      return p;
    };
    const allImages = Array.from(document.images);
    const on = allImages.find(image => routeOf(image) === onRoute) || null;
    const off = allImages.find(image => routeOf(image) === offRoute) || null;
    const active = document.getElementById('talentThumb' + index);
    return {
      on: on ? { src: on.currentSrc || on.src, route: routeOf(on), complete: on.complete, width: on.naturalWidth, height: on.naturalHeight } : null,
      off: off ? { src: off.currentSrc || off.src, route: routeOf(off), complete: off.complete, width: off.naturalWidth, height: off.naturalHeight } : null,
      active_visibility: active ? getComputedStyle(active).visibility : null,
      current_rank: window.rankTop[index][0],
      max_rank: window.talent[index][2]
    };
  }, { onRoute, offRoute, basePath, index });
  assert(state.on, 'Page has no on-state image request for ' + onRoute);
  assert(state.off, 'Page has no off-state image request for ' + offRoute);
  for (const [kind, image] of [['on', state.on], ['off', state.off]]) {
    assert(image.complete && image.width === 36 && image.height === 36,
      kind + ' state image did not decode at 36x36 for ' + entry.talent + ': ' + JSON.stringify(image));
  }
  assert.strictEqual(state.current_rank, expectedRank, 'Talent rank does not match requested visual state');
  if (expectedRank === 0) assert.strictEqual(state.active_visibility, 'hidden', 'Rank-zero on icon should remain hidden');
  else assert.strictEqual(state.active_visibility, 'visible', 'Activated on icon should be visible');
  return state;
}

async function runTalent(context, pf, mappingId, pair, runDir, report, events) {
  const on = pair.find(row => row.state === 'on');
  const off = pair.find(row => row.state === 'off');
  const row = {
    mapping_id: mappingId, class: on.class, talent: on.talent, page: on.page_route,
    old_data_route: on.old_data_route, old_data_sha256: on.old_data_sha256,
    off_route: off.route, on_route: on.route, status: 'running', screenshots: []
  };
  report.talent_checks.push(row);
  const page = await context.newPage();
  page.on('pageerror', error => events.pageErrors.push({ page: on.page_route, error: String(error) }));
  page.on('requestfailed', request => {
    const route = normalizeRoute(request.url(), pf.basePath);
    const kind = pf.entriesByRoute.has(route) ? 'mapped_image' : pf.expectedData.has(route) ? 'class_data' : pf.knownMissing.has(route) ? 'known_baseline_missing' : 'unexpected_resource_failure';
    events.requestFailures.push({ page: on.page_route, route, url: request.url(), failure: request.failure() && request.failure().errorText, kind });
  });
  try {
    const targetUrl = new URL(on.page_route.replace(/^\//, ''), pf.baseUrl).href;
    const response = await page.goto(targetUrl, { waitUntil: 'load', timeout: 60000 });
    assert(response && response.status() === 200, 'Talent page did not return 200: ' + targetUrl);
    await page.waitForFunction(() => typeof window.rankTopOnClick === 'function' &&
      Array.isArray(window.talent) && Array.isArray(window.rankTop) && window.rankPoints >= 0, null, { timeout: 30000 });
    const runtime = await page.evaluate(name => {
      const matches = [];
      for (let i = 0; window.talent[i]; i++) if (window.talent[i][1] === name) matches.push(i);
      if (matches.length !== 1) throw new Error('Expected exactly one 2008 talent row for ' + name + ', saw ' + matches.length);
      const index = matches[0];
      return {
        index,
        talent: Array.from(window.talent[index]),
        source_rank: Array.from(window.rank[index]),
        current_rank: window.rankTop[index][0],
        available_points: window.rankPoints,
        class_name: window.className
      };
    }, on.talent);
    assert.strictEqual(runtime.talent[1], on.talent);
    assert.strictEqual(runtime.current_rank, 0, on.talent + ' did not begin unspent');
    assert.strictEqual(runtime.talent[2] > 0, true, on.talent + ' has no valid rank count');
    row.original_data = {
      talent_index: runtime.index, talent_row: runtime.talent,
      rank_zero_description: runtime.source_rank[0], rank_count: runtime.source_rank.length,
      page_points_available: runtime.available_points,
      page_data_sha256: on.old_data_sha256
    };
    await page.locator('img[onclick*="rankTopOnClick(' + runtime.index + ')"]').last().scrollIntoViewIfNeeded();
    await page.waitForFunction(({ index, onRoute, offRoute, prefix }) => {
      const routeOf = image => {
        let p;
        try { p = decodeURIComponent(new URL(image.currentSrc || image.src, location.href).pathname); } catch (_) { return ''; }
        const base = String(prefix || '').replace(/\/+$/, '');
        return base && p.startsWith(base + '/') ? p.slice(base.length) : p;
      };
      const routes = Array.from(document.images, routeOf);
      return routes.includes(onRoute) && routes.includes(offRoute) && !!document.getElementById('talentThumb' + index);
    }, { index: runtime.index, onRoute: on.route, offRoute: off.route, prefix: pf.basePath }, { timeout: 20000 });
    const initial = await readImageState(page, off, pf.basePath, runtime.index, 0);
    row.initial_off_state = initial;
    const initialSnap = await snapshot(page);
    assert.strictEqual(initialSnap.rankPoints, runtime.available_points, 'Point count changed before the legal click');
    row.screenshots.push(await saveShot(page, runDir, mappingId, 'off'));

    const allocation = await allocateLegally(page, on.talent);
    assert.strictEqual(allocation.index, runtime.index, 'Original data index changed while allocating');
    assert.strictEqual(allocation.final_rank, 1, 'Legal allocator did not add exactly one rank');
    row.allocation = allocation;
    const activated = await readImageState(page, on, pf.basePath, runtime.index, 1);
    row.activated_on_state = activated;
    row.tooltip = await checkTooltip(page, runtime.index, on.talent);
    row.screenshots.push(await saveShot(page, runDir, mappingId, 'on'));

    const complete = await snapshot(page);
    assert.strictEqual(complete.ranks[runtime.index], 1);
    assert.strictEqual(initialSnap.rankPoints - complete.rankPoints, allocation.legal_rank_events.length,
      'Remaining-point delta does not equal original-handler clicks');
    const saved = await page.evaluate(() => {
      const node = document.getElementById('copyURL');
      const digits = node && node.innerText.trim();
      if (!digits) throw new Error('Original save-template digits are empty');
      return { digits, href: new URL(window.location.pathname + '?' + digits, window.location.href).href };
    });
    assert.strictEqual(saved.digits, complete.ranks.join(''), 'Save-link digits differ from live ranks');
    row.saved_link = { digits: saved.digits, href: saved.href };
    const reloadResponse = await page.goto(saved.href, { waitUntil: 'load', timeout: 60000 });
    assert(reloadResponse && reloadResponse.status() === 200, 'Saved URL reload did not return 200');
    await page.waitForFunction(index => typeof window.rankTopOnClick === 'function' &&
      window.rankTop[index] && window.rankTop[index][0] === 1, runtime.index, { timeout: 30000 });
    const afterReload = await snapshot(page);
    assertSnapshotEqual(complete, afterReload, on.talent + ' save/reload');
    assert.strictEqual(new URL(page.url()).search.slice(1), saved.digits, 'Reload query differs from saved rank digits');
    const reloadImage = await readImageState(page, on, pf.basePath, runtime.index, 1);
    row.save_reload = {
      exact_saved_digits: true,
      ranks_preserved: true,
      remaining_points_before: complete.rankPoints,
      remaining_points_after: afterReload.rankPoints,
      tree_points_preserved: true,
      active_image_after_reload: reloadImage.on
    };
    row.status = 'passed';
  } catch (error) {
    row.status = 'failed';
    row.failure = String(error);
    row.stack = error.stack;
    throw error;
  } finally {
    await page.close();
  }
}

async function saveShot(page, runDir, mappingId, state) {
  const safe = mappingId.replace(/[^a-z0-9-]/gi, '-');
  const file = path.join(runDir, safe + '-' + state + '.png');
  await page.screenshot({ path: file, fullPage: false });
  return path.relative(ROOT, file).split(path.sep).join('/');
}

function classifyError(route, pf, events) {
  if (route && pf.entriesByRoute.has(route)) return 'mapped_image_error';
  if (route && pf.expectedData.has(route)) return 'original_data_error';
  if (route && pf.knownMissing.has(route)) return 'known_baseline_missing';
  return 'unexpected_new_error';
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) { process.stdout.write(helpText() + '\n'); return; }
  const port = Number(options.port);
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const runDir = path.join(__dirname, 'runs', 'v55-' + stamp);
  fs.mkdirSync(runDir, { recursive: true });
  const tempDir = path.join(ROOT, '.scratch', 'test-temp-20261022');
  fs.mkdirSync(tempDir, { recursive: true });
  process.env.TEMP = tempDir;
  process.env.TMP = tempDir;
  process.env.TMPDIR = tempDir;

  const report = {
    schema: 'wow-related-talent-icons-v55-browser-check/v1',
    started_utc: new Date().toISOString(),
    status: 'running',
    run_mode: options.preflightOnly ? 'preflight-only' : (options.headed ? 'headed-real-chrome' : 'headless-real-chrome'),
    response_policy: 'loopback origin only; same-origin responses continue unchanged; off-origin requests abort; no fulfill or substitution',
    production_export_verified: false,
    source_classification: 'later_related_source',
    original_2008_pixel_identity: 'unknown',
    talent_checks: [],
    image_response_checks: [],
    class_data_response_checks: [],
    known_baseline_missing: [],
    unexpected_new_errors: [],
    mapped_image_errors: [],
    external_requests_aborted: [],
    page_errors: [],
    request_failures: []
  };
  let browser = null, context = null, events = null, pf = null;
  try {
    pf = createPreflight(port, options.outputDir);
    report.export_root = pf.exportRoot;
    report.base_url = pf.baseUrl.href;
    report.pinned_inputs = pf.inputHashes;
    report.preflight = {
      map_count: pf.map.entries.length,
      catalog_count: pf.catalog.assets.length,
      explicit_mappings: pf.catalog.mappings.length,
      local_payloads_match: true,
      original_data_files_unchanged: true,
      known_missing_baseline_count: pf.knownMissingCount,
      classes: CLASS_NAMES
    };
    if (options.preflightOnly) {
      report.status = 'preflight_passed_only';
      return;
    }

    browser = await chromium.launch({
      headless: !options.headed,
      executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe'
    });
    context = await browser.newContext({
      serviceWorkers: 'block',
      viewport: { width: 1480, height: 1250 },
      deviceScaleFactor: 1
    });
    events = {
      responses: [], responseTasks: [], failures: report.request_failures,
      pageErrors: report.page_errors, external: report.external_requests_aborted,
      basePath: pf.basePath, entriesByRoute: pf.entriesByRoute, expectedData: pf.expectedData,
      knownMissing: pf.knownMissing
    };
    await context.route('**/*', async route => {
      const request = route.request();
      let url;
      try { url = new URL(request.url()); } catch (_) { return route.continue(); }
      if (['data:', 'blob:', 'about:'].includes(url.protocol)) return route.continue();
      if (url.origin !== pf.baseUrl.origin) {
        events.external.push({ url: request.url(), resource_type: request.resourceType() });
        return route.abort();
      }
      return route.continue();
    });
    context.on('page', page => {
      page.on('response', response => {
        const task = (async () => {
          const requestUrl = response.request().url();
          const requestRoute = normalizeRoute(requestUrl, pf.basePath);
          const responseRoute = normalizeRoute(response.url(), pf.basePath);
          const route = pf.entriesByRoute.has(requestRoute) ? requestRoute :
            pf.entriesByRoute.has(responseRoute) ? responseRoute :
              pf.expectedData.has(requestRoute) ? requestRoute :
                pf.expectedData.has(responseRoute) ? responseRoute : requestRoute;
          const isFallback = (() => {
            try { return new URL(response.url()).pathname.endsWith('/__offline/missing-image.svg'); }
            catch (_) { return false; }
          })();
          if (response.status() >= 400 || isFallback) {
            const row = {
              route,
              request_url: requestUrl,
              response_url: response.url(),
              status: response.status(),
              kind: classifyError(route, pf, events),
              missing_image_fallback: isFallback
            };
            if (row.kind === 'known_baseline_missing') events.failures.push(row);
            else if (row.kind === 'mapped_image_error' || row.kind === 'original_data_error') events.failures.push(row);
            else events.failures.push(row);
          }
          const asset = pf.entriesByRoute.get(route);
          const data = pf.expectedData.get(route);
          if (!asset && !data) return;
          const body = await response.body();
          const headers = response.headers();
          const record = {
            route, request_url: requestUrl, response_url: response.url(), status: response.status(),
            length: body.length, sha256: sha256(body), git_blob_sha1: gitBlobSha1(body),
            content_type: (headers['content-type'] || '').split(';')[0].trim().toLowerCase()
          };
          if (asset) {
            record.expected_sha256 = asset.sha256;
            record.expected_git_blob_sha1 = asset.git_blob_sha1;
            record.expected_length = asset.length;
            record.expected_mime = 'image/jpeg';
            record.exact = response.status() === 200 && body.length === asset.length &&
              record.sha256 === asset.sha256 && record.git_blob_sha1 === asset.git_blob_sha1 &&
              record.content_type === 'image/jpeg';
          } else {
            record.expected_sha256 = data.sha256;
            record.expected_length = data.length;
            record.expected_mime = 'application/javascript';
            record.exact = response.status() === 200 && body.length === data.length &&
              record.sha256 === data.sha256 &&
              ['application/javascript', 'text/javascript', 'text/plain'].includes(record.content_type);
          }
          events.responses.push(record);
        })().catch(error => events.failures.push({ route: null, kind: 'response_read_failure', error: String(error), url: response.url() }));
        events.responseTasks.push(task);
      });
    });

    for (const [mappingId, pair] of pf.entriesByMapping) {
      await runTalent(context, pf, mappingId, pair, runDir, report, events);
    }
    await Promise.all(events.responseTasks);
    report.image_response_checks = events.responses.filter(row => pf.entriesByRoute.has(row.route));
    report.class_data_response_checks = events.responses.filter(row => pf.expectedData.has(row.route));
    for (const route of pf.entriesByRoute.keys()) {
      const rows = report.image_response_checks.filter(row => row.route === route);
      if (!rows.some(row => row.exact)) {
        report.mapped_image_errors.push({ route, observed_response_count: rows.length, response_rows: rows });
      }
    }
    for (const route of pf.expectedData.keys()) {
      const rows = report.class_data_response_checks.filter(row => row.route === route);
      if (!rows.some(row => row.exact)) {
        report.unexpected_new_errors.push({ route, category: 'original_data_response_mismatch', response_rows: rows });
      }
    }
    for (const failure of events.failures) {
      if (failure.kind === 'known_baseline_missing') report.known_baseline_missing.push(failure);
      else if (failure.kind === 'mapped_image_error') report.mapped_image_errors.push(failure);
      else if (failure.kind === 'original_data_error') report.unexpected_new_errors.push(failure);
      else report.unexpected_new_errors.push(failure);
    }
    for (const failure of report.request_failures) {
      const row = { ...failure, category: failure.kind };
      if (failure.kind === 'known_baseline_missing') report.known_baseline_missing.push(row);
      else if (failure.kind === 'mapped_image') report.mapped_image_errors.push(row);
      else if (failure.kind === 'class_data') report.unexpected_new_errors.push(row);
      else report.unexpected_new_errors.push(row);
    }
    const unique = rows => Array.from(new Map(rows.map(row => [JSON.stringify(row), row])).values());
    report.known_baseline_missing = unique(report.known_baseline_missing);
    report.unexpected_new_errors = unique(report.unexpected_new_errors);
    report.mapped_image_errors = unique(report.mapped_image_errors);
    report.summary = {
      talent_checks_passed: report.talent_checks.filter(row => row.status === 'passed').length,
      expected_talent_checks: 10,
      mapped_image_routes_exact: pf.entries.filter(entry =>
        report.image_response_checks.some(row => row.route === entry.route && row.exact)).length,
      expected_mapped_image_routes: 20,
      original_class_data_routes_exact: pf.expectedData.size - report.unexpected_new_errors.filter(row => row.category === 'original_data_response_mismatch').length,
      expected_class_data_routes: pf.expectedData.size,
      known_baseline_missing_observations: report.known_baseline_missing.length,
      unexpected_new_errors: report.unexpected_new_errors.length,
      mapped_image_errors: report.mapped_image_errors.length,
      external_requests_aborted: report.external_requests_aborted.length,
      page_errors: report.page_errors.length
    };
    assert.strictEqual(report.summary.talent_checks_passed, 10, 'Not all ten talent checks passed');
    assert.strictEqual(report.summary.mapped_image_routes_exact, 20, 'Not all 20 image routes had exact real responses');
    assert.strictEqual(report.summary.original_class_data_routes_exact, pf.expectedData.size, 'Original class data responses changed');
    assert.strictEqual(report.summary.unexpected_new_errors, 0, 'Unexpected requests failed outside the 390-route baseline');
    assert.strictEqual(report.summary.mapped_image_errors, 0, 'A mapped icon request failed or differed from its pinned bytes');
    assert.strictEqual(report.summary.external_requests_aborted, 0, 'An off-origin request was attempted');
    assert.strictEqual(report.summary.page_errors, 0, 'Browser page errors occurred');
    report.status = 'browser_checks_passed_pending_parent_review';
    report.production_export_verified = false;
  } catch (error) {
    report.status = 'failed';
    report.failure = String(error);
    report.stack = error.stack;
    if (events) {
      await Promise.allSettled(events.responseTasks);
      report.image_response_checks = events.responses.filter(row => pf.entriesByRoute.has(row.route));
      report.class_data_response_checks = events.responses.filter(row => pf.expectedData.has(row.route));
    }
    process.exitCode = 1;
  } finally {
    if (context) await context.close();
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    report.receipt_path = path.relative(ROOT, path.join(runDir, 'browser-check.json')).split(path.sep).join('/');
    fs.writeFileSync(path.join(runDir, 'browser-check.json'), JSON.stringify(report, null, 2) + '\n');
    process.stdout.write(JSON.stringify({ status: report.status, receipt: report.receipt_path, summary: report.summary || null, failure: report.failure || null }) + '\n');
  }
}

main().catch(error => { process.stderr.write(String(error) + '\n'); process.exitCode = 1; });
