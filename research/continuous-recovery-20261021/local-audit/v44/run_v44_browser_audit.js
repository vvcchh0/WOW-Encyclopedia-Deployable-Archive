#!/usr/bin/env node
/* Read-only v44 browser audit. The supplied loopback server is never started
 * or changed. All non-loopback requests are aborted and service workers are
 * blocked. */
'use strict';

const fs = require('fs');
const path = require('path');
const { chromium } = require('C:/Users/17630/AppData/Local/OpenAI/Codex/runtimes/cua_node/78fb63cda1a9e2b2/bin/node_modules/playwright-core');

const OUT_DIR = __dirname;
const SHOT_DIR = path.join(OUT_DIR, 'screenshots');
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 26473;
const SITE_PATH = '/WOW-Encyclopedia-Deployable-Archive';
const BASE = `http://127.0.0.1:${PORT}${SITE_PATH}`;
const TOTAL_LIMIT_MS = 10 * 60 * 1000;
const PAGE_LIMIT_MS = 12000;
const CLASSES = ['druid', 'hunter', 'mage', 'paladin', 'priest', 'rogue', 'shaman', 'warlock', 'warrior'];
const OLD_TARGET_FILE = path.resolve(OUT_DIR, '..', '..', '..', '..', 'research', 'continuous-recovery-20261021', 'integration', 'talents', 'full-image-scope', 'missing-targets.json');

function clip(value, n = 1600) { return String(value == null ? '' : value).slice(0, n); }
function textNorm(value) { return String(value || '').replace(/\s+/g, ' ').trim(); }
function safeName(value) { return value.replace(/[^a-z0-9_.-]+/gi, '_').replace(/^_+|_+$/g, '').slice(0, 120); }
function loopback(url) {
  try { const u = new URL(url); return u.protocol === 'http:' && u.hostname === '127.0.0.1' && Number(u.port || 80) === PORT; }
  catch (_) { return false; }
}
function remaining(start) { return Math.max(500, Math.min(PAGE_LIMIT_MS, TOTAL_LIMIT_MS - (Date.now() - start))); }
function normalizeTarget(value) {
  if (typeof value !== 'string' || !value.trim()) return null;
  let s = value.trim().replace(/\\/g, '/');
  const replay = s.match(/(?:id|im)_\//);
  if (replay) s = s.slice(replay.index + replay[0].length);
  try { if (/^https?:\/\//i.test(s)) s = new URL(s).pathname || '/'; } catch (_) {}
  for (let i = 0; i < 4; i++) { try { const d = decodeURIComponent(s); if (d === s) break; s = d; } catch (_) { break; } }
  s = s.split('?', 1)[0].split('#', 1)[0];
  const host = s.search(/(?:www\.)?worldofwarcraft\.com(?:_80)?\//i);
  if (host >= 0) s = '/' + s.slice(s.indexOf('/', host) + 1);
  s = s.replace(/^\/+/, '/');
  for (const prefix of ['/WOW-Encyclopedia-Deployable-Archive', '/www.worldofwarcraft.com_80', '/www.worldofwarcraft.com', '/worldofwarcraft.com']) {
    if (s === prefix) s = '/';
    else if (s.startsWith(prefix + '/')) s = s.slice(prefix.length);
  }
  return s || '/';
}
function loadOldTargets() {
  try {
    const d = JSON.parse(fs.readFileSync(OLD_TARGET_FILE, 'utf8'));
    const rows = d.merged_missing_targets || d.static_placeholder_targets || d.targets || [];
    const out = new Set();
    for (const row of rows) {
      const v = typeof row === 'string' ? row : row && (row.target || row.route || row.url);
      const n = normalizeTarget(v);
      if (n) out.add(n);
    }
    return { path: path.relative(path.resolve(OUT_DIR, '..', '..', '..', '..'), OLD_TARGET_FILE).replace(/\\/g, '/'), count: out.size, set: out };
  } catch (error) { return { path: OLD_TARGET_FILE, count: 0, set: new Set(), error: String(error) }; }
}
function makeListeners(page) {
  const state = { page_errors: [], console_errors: [], failed_requests: [], http_errors: [], external_blocks: [], seen_http: new Set() };
  page.on('pageerror', error => state.page_errors.push(clip(error && error.stack ? error.stack : error)));
  page.on('console', msg => { if (msg.type() === 'error' || msg.type() === 'warning') state.console_errors.push({ type: msg.type(), text: clip(msg.text(), 1000), location: msg.location() }); });
  page.on('requestfailed', request => {
    const row = { url: request.url(), resource_type: request.resourceType(), failure: request.failure() && request.failure().errorText };
    state.failed_requests.push(row);
    if (!loopback(row.url) && !/^data:|^blob:|^about:/i.test(row.url)) state.external_blocks.push({ ...row, reason: 'aborted_by_probe' });
  });
  page.on('response', response => {
    if (response.status() < 400) return;
    const row = { url: response.url(), status: response.status(), resource_type: response.request().resourceType() };
    const key = row.status + ' ' + row.url;
    if (!state.seen_http.has(key)) { state.seen_http.add(key); state.http_errors.push(row); }
  });
  return state;
}
function finishListeners(out, state) {
  out.page_errors = state.page_errors.slice(0, 160);
  out.console_errors = state.console_errors.slice(0, 160);
  out.failed_requests = state.failed_requests.slice(0, 160);
  out.http_errors = state.http_errors.slice(0, 240);
  out.blocked_non_loopback_requests = state.external_blocks.slice(0, 160);
}

async function pageEvidence(page, phraseConfig = {}) {
  return page.evaluate(({ phraseSelector, phrases }) => {
    const visible = el => {
      if (!el) return false;
      const s = getComputedStyle(el); const r = el.getBoundingClientRect();
      return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
    };
    const clean = el => (el && (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim()) || '';
    const parseMissing = (value, source) => {
      const raw = String(value || '');
      if (!/__offline\/missing-image\.svg/i.test(raw)) return null;
      const match = raw.match(/(?:https?:\/\/[^\s"']+)?[^\s"']*__offline\/missing-image\.svg[^\s"']*/i);
      const candidate = match ? match[0].replace(/^url\(['"]?/, '').replace(/['"]?\)$/, '') : raw;
      try {
        const u = new URL(candidate, document.baseURI);
        const requestedRaw = raw.match(/[?&]requested=([^&"'\s]+)/i);
        let requested = u.searchParams.get('requested');
        if (requestedRaw) { try { requested = decodeURIComponent(requestedRaw[1]); } catch (_) { requested = requestedRaw[1]; } }
        return { source, raw: raw.slice(0, 900), current: u.href, requested, reason: u.searchParams.get('reason') };
      } catch (_) { return { source, raw: raw.slice(0, 900), current: candidate, requested: null, reason: null }; }
    };
    const main = document.querySelector(phraseSelector || '#contentContainer') || document.querySelector('#main-content') || document.body;
    const mainText = clean(main); const bodyText = clean(document.body);
    const blocks = Array.from(main.querySelectorAll('h1,h2,h3,h4,p,li,article,main,td,div'))
      .filter(visible).map(el => ({ selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''), text: clean(el).slice(0, 320) }))
      .filter(x => x.text).slice(0, 16);
    const missingImage = Array.from(document.images).map(img => ({ src: img.getAttribute('src'), current_src: img.currentSrc || img.src, natural_width: img.naturalWidth, natural_height: img.naturalHeight, complete: img.complete, alt: img.alt || null }))
      .map(x => ({ ...x, missing: parseMissing(x.src, 'img.src') || parseMissing(x.current_src, 'img.currentSrc') })).filter(x => x.missing).map(x => ({ ...x.missing, src: x.src, current_src: x.current_src, natural_width: x.natural_width, natural_height: x.natural_height, complete: x.complete, alt: x.alt }));
    const missingCss = [];
    for (const el of Array.from(document.querySelectorAll('*'))) {
      if (!visible(el)) continue;
      const s = getComputedStyle(el); const bg = s.backgroundImage || ''; const inline = el.getAttribute('style') || '';
      const m = parseMissing(bg, 'computed.backgroundImage') || parseMissing(inline, 'inline.style');
      if (m) missingCss.push({ ...m, tag: el.tagName.toLowerCase(), id: el.id || null, class_name: String(el.className || '').slice(0, 180) });
    }
    const anchors = Array.from(document.querySelectorAll('a'));
    const forms = Array.from(document.forms).map(form => ({ id: form.id || null, action: form.getAttribute('action') || form.action || '', method: (form.method || 'get').toLowerCase(), visible: visible(form), controls: Array.from(form.querySelectorAll('input,button,select,textarea')).map(el => ({ tag: el.tagName.toLowerCase(), type: el.type || null, id: el.id || null, name: el.name || null, value: el.value || null, text: clean(el).slice(0, 180), visible: visible(el) })) }));
    const mailto = anchors.filter(a => /^mailto:/i.test(a.getAttribute('href') || '')).map(a => ({ href: a.getAttribute('href'), text: clean(a).slice(0, 220), visible: visible(a) }));
    const submit = Array.from(document.querySelectorAll('input[type=submit],button[type=submit],button')).filter(visible).map(el => ({ tag: el.tagName.toLowerCase(), type: el.type || null, id: el.id || null, text: clean(el).slice(0, 220), value: el.value || null }));
    const downloads = anchors.filter(a => /download|\.zip(?:$|[?#])|\.pdf(?:$|[?#])|\.exe(?:$|[?#])/i.test((a.getAttribute('href') || '') + ' ' + clean(a))).map(a => ({ href: a.getAttribute('href'), text: clean(a).slice(0, 220), visible: visible(a) }));
    const phraseChecks = (phrases || []).map(phrase => ({ phrase, found: mainText.includes(phrase) }));
    const sourceNotice = /unofficial historical educational preservation|archive reconstruction based on 2008-05-12/i.test(bodyText);
    const talentImages = Array.from(document.querySelectorAll('#replaceMeWithTalents img[onclick*="rankTopOnClick"], #replaceMeWithTalents img')).filter(visible).map(img => ({ src: img.currentSrc || img.src, natural_width: img.naturalWidth, natural_height: img.naturalHeight, broken: img.complete && img.naturalWidth === 0, alt: img.alt || null })).slice(0, 80);
    const rankTop = Array.isArray(window.rankTop) ? window.rankTop : null;
    const rankTrees = rankTop ? rankTop.map(tree => Array.isArray(tree) ? { ranks: tree.length, max: tree.reduce((n, x) => n + (Number(x) || 0), 0) } : null) : [];
    const levelControls = Array.from(document.querySelectorAll('input,select,option,span,div')).filter(el => /level|points|61/i.test([el.id, el.getAttribute('name'), el.textContent].filter(Boolean).join(' '))).slice(0, 30).map(el => ({ tag: el.tagName.toLowerCase(), id: el.id || null, name: el.getAttribute('name'), value: el.value || null, text: clean(el).slice(0, 160), visible: visible(el) }));
    return { title: document.title || '', body_text: bodyText.slice(0, 2600), body_text_length: bodyText.length, main_text_length: mainText.length, blocks, phrase_checks: phraseChecks, source_notice_visible: sourceNotice, forms, mailto_links: mailto, submit_controls: submit, download_links: downloads, missing_images: missingImage, missing_css: missingCss, talent: { rank_points: typeof window.rankPoints === 'number' ? window.rankPoints : null, available: document.getElementById('tabPointsAvailable')?.textContent || null, spent: document.getElementById('modifyRankPoints')?.textContent || null, rendered_length: document.querySelector('#replaceMeWithTalents')?.innerHTML?.length || 0, talent_nodes: document.querySelectorAll('#replaceMeWithTalents img[onclick*="rankTopOnClick"]').length, rendered_images: document.querySelectorAll('#replaceMeWithTalents img').length, visible_icons: talentImages.length, visible_icon_samples: talentImages.slice(0, 8), rank_trees: rankTrees, globals: Object.fromEntries(['rankTop','resetTree','resetTreeAll','saveTheTemplate','rankTopOnClick'].map(k => [k, typeof window[k]])), level_controls: levelControls } };
  }, { phraseSelector: phraseConfig.selector || '#contentContainer', phrases: phraseConfig.phrases || [] });
}

async function gotoWait(page, url, start) {
  let navError = null; let response = null;
  try { response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: Math.min(9000, remaining(start)) }); await page.waitForTimeout(Math.min(650, Math.max(100, remaining(start) - 300))); }
  catch (error) { navError = clip(error && error.stack ? error.stack : error); }
  return { response, navError };
}

async function runTalent(context, name, oldTargets, overallStart) {
  const page = await context.newPage(); const start = Date.now(); const listener = makeListeners(page);
  const out = { id: `talent-${name}`, kind: 'talent', path: `/info/classes/${name}/talents.html`, class_name: name, status: null, final_url: null, navigation_error: null, initial: null, after_add: null, saved_template: null, after_reset: null, after_reopen: null, after_refresh: null, evidence: null, screenshot: null, old_target_intersection: [], new_not_old_missing: [], page_errors: [], console_errors: [], failed_requests: [], http_errors: [], blocked_non_loopback_requests: [], duration_ms: null };
  try {
    const nav = await gotoWait(page, BASE + out.path, start); out.navigation_error = nav.navError; out.status = nav.response ? nav.response.status() : null; out.final_url = page.url();
    out.initial = await pageEvidence(page, { selector: '#replaceMeWithTalents', phrases: ['Archive reconstruction based on 2008-05-12'] });
    const first = page.locator('img[onclick*="rankTopOnClick"]').first();
    if (await first.count()) { await first.click({ force: true, timeout: Math.min(3500, remaining(start)) }); await page.waitForTimeout(120); out.after_add = await pageEvidence(page, { selector: '#replaceMeWithTalents' }); }
    const popupPromise = page.waitForEvent('popup', { timeout: 2500 }).catch(() => null);
    try { await page.evaluate(() => { if (typeof window.saveTheTemplate === 'function') window.saveTheTemplate(); }); } catch (error) { out.saved_template = { error: clip(error && error.stack ? error.stack : error) }; }
    const popup = await popupPromise;
    let savedText = '';
    if (popup) { await popup.waitForTimeout(120).catch(() => {}); savedText = await popup.evaluate(() => (document.body && document.body.innerText) || '').catch(() => ''); out.saved_template = { popup: true, url: popup.url(), text: savedText.slice(0, 1800) }; await popup.close().catch(() => {}); }
    else if (!out.saved_template) { savedText = await page.evaluate(() => (document.body && document.body.innerText) || ''); out.saved_template = { popup: false, url: page.url(), text: savedText.slice(0, 1800) }; }
    const candidate = (savedText.match(/(?:https?:\/\/[^\s"'<>]+|\/[^\s"'<>]+)talents\.html\?[0-9]+/) || [])[0] || null;
    if (candidate) { try { const u = new URL(candidate, BASE + '/'); const query = u.searchParams.toString(); out.saved_template.path = u.pathname.replace(SITE_PATH, '') + (query ? '?' + query : ''); out.saved_template.template_code = u.search.slice(1); out.saved_template.nonzero_code = /[1-9]/.test(out.saved_template.template_code); } catch (_) {} }
    if (await page.locator('#hideReset0').count()) { await page.locator('#hideReset0').click({ force: true, timeout: Math.min(3000, remaining(start)) }); }
    else await page.evaluate(() => { if (typeof window.resetTreeAll === 'function') window.resetTreeAll(); });
    await page.waitForTimeout(120); out.after_reset = await pageEvidence(page, { selector: '#replaceMeWithTalents' });
    if (out.saved_template && out.saved_template.path && out.saved_template.nonzero_code) {
      const templateUrl = BASE + out.saved_template.path;
      const reopened = await gotoWait(page, templateUrl, start); out.saved_template.reopen_navigation_error = reopened.navError; out.after_reopen = await pageEvidence(page, { selector: '#replaceMeWithTalents' });
      try { await page.reload({ waitUntil: 'domcontentloaded', timeout: Math.min(9000, remaining(start)) }); await page.waitForTimeout(Math.min(700, Math.max(120, remaining(start) - 250))); out.after_refresh = await pageEvidence(page, { selector: '#replaceMeWithTalents' }); } catch (error) { out.saved_template.refresh_error = clip(error && error.stack ? error.stack : error); }
    }
    if (remaining(start) > 900) { const screenshot = `talent-${name}.png`; await page.screenshot({ path: path.join(SHOT_DIR, screenshot), fullPage: true, animations: 'disabled', timeout: Math.min(5000, remaining(start)) }); out.screenshot = `screenshots/${screenshot}`; }
    out.evidence = out.after_refresh || out.after_reopen || out.initial;
    const allMissing = [...(out.evidence?.missing_images || []), ...(out.evidence?.missing_css || [])];
    for (const row of allMissing) { const normalized = normalizeTarget(row.requested); if (!normalized) continue; if (oldTargets.set.has(normalized)) out.old_target_intersection.push(normalized); else out.new_not_old_missing.push(normalized); }
    out.old_target_intersection = [...new Set(out.old_target_intersection)]; out.new_not_old_missing = [...new Set(out.new_not_old_missing)];
  } catch (error) { out.error = clip(error && error.stack ? error.stack : error); }
  finishListeners(out, listener); out.duration_ms = Date.now() - start; await page.close().catch(() => {}); return out;
}

async function runControl(context, target, overallStart) {
  const page = await context.newPage(); const start = Date.now(); const listener = makeListeners(page);
  const out = { id: target.id, kind: target.kind || 'control', path: target.path, status: null, final_url: null, navigation_error: null, evidence: null, actions: [], screenshot: null, page_errors: [], console_errors: [], failed_requests: [], http_errors: [], blocked_non_loopback_requests: [], duration_ms: null };
  try {
    const nav = await gotoWait(page, BASE + target.path, start); out.navigation_error = nav.navError; out.status = nav.response ? nav.response.status() : null; out.final_url = page.url(); out.evidence = await pageEvidence(page, { selector: target.selector || '#contentContainer', phrases: target.phrases || [] });
    if (target.id === 'legacy-news-06-2005') {
      const action = { name: 'click-historical-contest', heading_found: false, expanded: false, link_found: false, clicked: false, after_status: null, after_url: null, after_title: null, after_body: null, error: null };
      try {
        const heading = page.locator('h3').filter({ hasText: 'Insider Battlegrounds Screen Shot Contest' }).first(); action.heading_found = await heading.count() > 0;
        if (action.heading_found) {
          const parent = heading.locator('xpath=..'); const post = parent.locator('.postBody').first(); action.expanded = await post.count() > 0 && await post.isVisible().catch(() => false);
          const link = page.getByRole('link', { name: 'View historical contest', exact: true }).first(); action.link_found = await link.count() > 0;
          if (action.link_found) { action.clicked = true; const navPromise = page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: Math.min(6000, remaining(start)) }).catch(() => null); await link.click({ timeout: Math.min(4000, remaining(start)) }); const response = await navPromise; await page.waitForTimeout(250); action.after_status = response ? response.status() : null; action.after_url = page.url(); action.after_title = await page.title().catch(() => null); action.after_body = await page.evaluate(() => { const text = (document.body?.innerText || '').replace(/\s+/g, ' ').trim(); const visibleContinue = Array.from(document.querySelectorAll('a,button,input[type=submit],img')).filter(el => { const s = getComputedStyle(el), r = el.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0 && /continue/i.test((el.innerText || el.alt || el.value || el.getAttribute('title') || '')); }).map(el => ({ tag: el.tagName.toLowerCase(), text: el.innerText || el.alt || el.value || '', src: el.getAttribute('src'), href: el.getAttribute('href') })); return { text: text.slice(0, 5000), text_length: text.length, past_markers: ['historical','archived','planned'].filter(x => text.toLowerCase().includes(x)), present_action_phrases: ['is giving away','to enter','submit your screenshot','we will announce'].filter(x => text.toLowerCase().includes(x)), continue_controls: visibleContinue }; }); }
        }
      } catch (error) { action.error = clip(error && error.stack ? error.stack : error); }
      out.actions.push(action);
      if (remaining(start) > 900) { const screenshot = 'legacy-news-06-2005-after-click.png'; await page.screenshot({ path: path.join(SHOT_DIR, screenshot), fullPage: true, animations: 'disabled', timeout: Math.min(5000, remaining(start)) }); out.screenshot = `screenshots/${screenshot}`; }
    }
    if (remaining(start) > 900 && !out.screenshot) { const screenshot = `${safeName(target.id)}.png`; await page.screenshot({ path: path.join(SHOT_DIR, screenshot), fullPage: true, animations: 'disabled', timeout: Math.min(5000, remaining(start)) }); out.screenshot = `screenshots/${screenshot}`; }
  } catch (error) { out.error = clip(error && error.stack ? error.stack : error); }
  finishListeners(out, listener); out.duration_ms = Date.now() - start; await page.close().catch(() => {}); return out;
}

(async () => {
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  const oldTargets = loadOldTargets(); const started = Date.now();
  const browser = await chromium.launch({ headless: true, executablePath: CHROME, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, serviceWorkers: 'block' });
  await context.route('**/*', async route => { const url = route.request().url(); if (loopback(url) || /^data:|^blob:|^about:/i.test(url)) await route.continue(); else await route.abort(); });
  const result = { schema: 'wow-continuous-recovery-20261021/v44-browser-audit-v1', server: { base: BASE, port: PORT, site_path: SITE_PATH, external_requests_blocked: true, service_workers: 'block' }, old_target_scope: { path: oldTargets.path, count: oldTargets.count, load_error: oldTargets.error || null }, started_at_utc: new Date().toISOString(), classes: CLASSES, pages: [], deviations: [] };
  try {
    for (const name of CLASSES) { if (Date.now() - started > TOTAL_LIMIT_MS - 15000) break; result.pages.push(await runTalent(context, name, oldTargets, started)); }
    const controls = [
      { id: 'legacy-news-06-2005', kind: 'legacy_news', path: '/news/wow-news-06-2005.html', selector: '#main-content', phrases: ['Insider Battlegrounds Screen Shot Contest', 'June 20th, 2005'] },
      { id: 'fan-site-program', kind: 'source16_control', path: '/misc/fan-site-program.html', selector: '#contentContainer', phrases: ['historical fan site program', 'does not accept applications'] },
      { id: 'source16-content-index', kind: 'source16_control', path: '/info/basics/content-index.html', selector: '#contentContainer', phrases: ['Battlegrounds Mini-Site', 'Warlock Talents'] },
      { id: 'source16-patch-092904', kind: 'source16_control', path: '/patchnotes/patch-9-29-04.shtml.html', selector: '#contentContainer', phrases: ['Warlock Talents Added', 'New Model & Animation System'] },
    ];
    for (const target of controls) { if (Date.now() - started > TOTAL_LIMIT_MS - 15000) break; result.pages.push(await runControl(context, target, started)); }
  } finally { await context.close().catch(() => {}); await browser.close().catch(() => {}); }
  result.finished_at_utc = new Date().toISOString(); result.duration_ms = Date.now() - started;
  const talents = result.pages.filter(x => x.kind === 'talent'); const allMissingImages = new Set(); const allMissingCss = new Set(); const all404 = new Set(); const oldIntersection = new Set(); const newNotOld = new Set();
  for (const row of talents) { for (const x of (row.evidence?.missing_images || [])) { const n = normalizeTarget(x.requested); if (n) allMissingImages.add(n); } for (const x of (row.evidence?.missing_css || [])) { const n = normalizeTarget(x.requested); if (n) allMissingCss.add(n); } for (const n of row.old_target_intersection || []) oldIntersection.add(n); for (const n of row.new_not_old_missing || []) newNotOld.add(n); for (const x of row.http_errors || []) if (x.status === 404) all404.add(x.url); }
  result.aggregate = { pages_checked: result.pages.length, talent_pages_checked: talents.length, controls_checked: result.pages.filter(x => x.kind !== 'talent').length, talent_rankpoints_61: talents.filter(x => x.initial?.talent?.rank_points === 61).length, talent_source_notice_visible: talents.filter(x => x.initial?.source_notice_visible).length, talent_visible_icon_pages: talents.filter(x => (x.evidence?.talent?.visible_icons || 0) > 0).length, talent_nonzero_save: talents.filter(x => x.saved_template?.nonzero_code === true).length, talent_reopen_nonzero: talents.filter(x => Number(x.after_reopen?.talent?.spent || 0) > 0).length, talent_refresh_nonzero: talents.filter(x => Number(x.after_refresh?.talent?.spent || 0) > 0).length, static_missing_unique: allMissingImages.size, dynamic_css_missing_unique: allMissingCss.size, missing_image_requested: [...allMissingImages].sort(), missing_css_requested: [...allMissingCss].sort(), missing_404_unique: all404.size, old_target_intersection_unique: oldIntersection.size, new_not_old_unique: newNotOld.size, old_target_intersection: [...oldIntersection].sort(), new_not_old: [...newNotOld].sort(), page_errors: result.pages.reduce((n, x) => n + (x.page_errors || []).length, 0), real_http_errors: result.pages.reduce((n, x) => n + (x.http_errors || []).length, 0), external_block_events: result.pages.reduce((n, x) => n + (x.blocked_non_loopback_requests || []).length, 0), control_mailto_visible: result.pages.filter(x => x.kind !== 'talent').reduce((n, x) => n + (x.evidence?.mailto_links || []).filter(y => y.visible).length, 0), control_sensitive_inputs: result.pages.filter(x => x.kind !== 'talent').reduce((n, x) => n + (x.evidence?.forms || []).flatMap(f => f.controls || []).filter(c => c.visible && /password|email|file|token/i.test([c.type, c.name, c.id].filter(Boolean).join(' '))).length, 0) };
  fs.writeFileSync(path.join(OUT_DIR, 'v44-browser-receipt.json'), JSON.stringify(result, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ output: 'v44-browser-receipt.json', duration_ms: result.duration_ms, aggregate: result.aggregate }) + '\n');
})().catch(error => { fs.writeFileSync(path.join(OUT_DIR, 'v44-browser-probe.error.txt'), String(error && error.stack ? error.stack : error), 'utf8'); console.error(error && error.stack ? error.stack : error); process.exitCode = 1; });
