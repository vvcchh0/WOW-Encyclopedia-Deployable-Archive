const assert = require('assert');
const { EventEmitter } = require('events');
const checker = require('./check_v33_browser.cjs');

async function testExactPopupSelection() {
  const candidates = [
    { index: 0, onclick: "javascript:popUpOmega('images/arena/ss1.jpg',800,611)", href: '' },
    { index: 1, onclick: "javascript:popUpOmega('images/arena/ss2.jpg',800,611)", href: '' },
  ];
  const row = {
    literal: "javascript:popUpOmega('images/arena/ss2.jpg',800,611)",
    source_base_url: 'http://www.worldofwarcraft.com/pvp/arena/index.xml',
    original: 'http://www.worldofwarcraft.com/pvp/arena/images/arena/ss2.jpg',
  };
  assert.strictEqual(checker.popupArgument(candidates[1].onclick), 'images/arena/ss2.jpg');
  assert.strictEqual(checker.selectPopupControlIndex(candidates, row, row.source_base_url), 1);
  assert.strictEqual(checker.selectPopupControlIndex(candidates, { ...row, original: row.original.replace('ss2', 'ss3') }, row.source_base_url), -1);
}

async function testOrdinaryNavigationRaceCleansListeners() {
  const context = new EventEmitter();
  const page = new EventEmitter();
  const frame = {};
  let currentUrl = 'http://127.0.0.1/source.html';
  page.url = () => currentUrl;
  page.mainFrame = () => frame;
  let outcome = await checker.waitForOrdinaryNavigation(context, page, async () => {
    currentUrl = 'http://127.0.0.1/image.jpg';
    page.emit('framenavigated', frame);
  }, 100);
  assert.deepStrictEqual(outcome, { kind: 'same-tab', url: 'http://127.0.0.1/image.jpg' });
  assert.strictEqual(context.listenerCount('page'), 0);
  assert.strictEqual(page.listenerCount('framenavigated'), 0);

  const popup = { id: 'popup' };
  currentUrl = 'http://127.0.0.1/source.html';
  outcome = await checker.waitForOrdinaryNavigation(context, page, async () => {
    context.emit('page', popup);
  }, 100);
  assert.strictEqual(outcome.kind, 'popup');
  assert.strictEqual(outcome.popup, popup);
  assert.strictEqual(context.listenerCount('page'), 0);
  assert.strictEqual(page.listenerCount('framenavigated'), 0);
}

async function testCssClassificationRequiresVisibleDecodedBackground() {
  const unused = checker.classifyCssInspection({ declarations: [{ selector: '.unused', dom_matches: 0 }], visibleDecoded: [] });
  assert.strictEqual(unused.kind, 'declaration_only');
  const rendered = checker.classifyCssInspection({ declarations: [{ selector: '.chart', dom_matches: 1 }], visibleDecoded: [{ dimensions: [1226, 701] }] });
  assert.strictEqual(rendered.kind, 'rendered');
  assert.throws(() => checker.classifyCssInspection({ declarations: [{ selector: '.hidden', dom_matches: 1 }], visibleDecoded: [] }), /DOM matches but no visible decoded background/);
  assert.throws(() => checker.classifyCssInspection({ declarations: [], visibleDecoded: [] }), /neither a visible element nor an actual CSS declaration/);
}

async function testScopedInteractiveActivationPlan() {
  assert.deepStrictEqual(checker.interactiveActivationPlan('pvp/tournament/items.xml.html', { equipment_tab_count: 10, profession_dropdown_count: 0 }), { equipment_tabs: true, profession_selectors: false });
  assert.deepStrictEqual(checker.interactiveActivationPlan('burningcrusade/townhall/professions.html', { equipment_tab_count: 0, profession_dropdown_count: 1 }), { equipment_tabs: false, profession_selectors: true });
  assert.deepStrictEqual(checker.interactiveActivationPlan('news/rss-08-2007.xml.html', { equipment_tab_count: 10, profession_dropdown_count: 1 }), { equipment_tabs: false, profession_selectors: false });
}

async function testSourceKeepsOneCollapsedNewsToggleAndNoFixedOrdinaryWait() {
  const source = require('fs').readFileSync(require('path').join(__dirname, 'check_v33_browser.cjs'), 'utf8');
  assert.match(source, /classList\.contains\('news-collapse'\)/);
  assert.match(source, /\.locator\('\.news-toggle a'\)\.first\(\)/);
  assert.match(source, /waitForOrdinaryNavigation\(context, page/);
  const ordinaryBlock = source.slice(source.indexOf('const ordinaryRows'), source.indexOf('const staticRows'));
  assert.ok(!ordinaryBlock.includes("context.waitForEvent('page'"));
}

(async () => {
  await testExactPopupSelection();
  await testOrdinaryNavigationRaceCleansListeners();
  await testCssClassificationRequiresVisibleDecodedBackground();
  await testScopedInteractiveActivationPlan();
  await testSourceKeepsOneCollapsedNewsToggleAndNoFixedOrdinaryWait();
  process.stdout.write('5 browser behavior tests passed\n');
})().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
