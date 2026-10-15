"use strict";

// Offline Node vm validation of the complete derived real viewer source.
// No browser, timers, animation, image fetch, or network is used.
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const crypto = require("crypto");

const OUT = __dirname;
const DERIVED = path.join(OUT, "derived-screeniesimplified.js");
const SOURCE_VALIDATION = path.join(OUT, "source-validation.json");
const RESULTS = path.join(OUT, "vm-results.json");
const source = fs.readFileSync(DERIVED, "utf8");
const derivedSha256 = crypto.createHash("sha256").update(source, "utf8").digest("hex");
const provenance = JSON.parse(fs.readFileSync(SOURCE_VALIDATION, "utf8"));

const common = Array.from({ length: 12 }, (_, i) => `./images/artwork/ss${i + 1}.jpg`);
const locale = ["./images/artwork/en_us/ss1.jpg"];
const expectedShotList = common.concat(locale);
const expectedDirList = Array(12).fill("./images/artwork/").concat(["./images/artwork/en_us/"]);
const expectedHiResList = Array.from({ length: 12 }, (_, i) => i + 1).concat([1]);

const cases = [
  { name: "one", search: "?s=1", expectedOneBased: 1 },
  { name: "three", search: "?s=3", expectedOneBased: 3 },
  { name: "thirteen", search: "?s=13", expectedOneBased: 13 },
  { name: "encoded-three", search: "?s=%33", expectedOneBased: 3 },
  { name: "missing", search: "", expectedOneBased: 1 },
  { name: "empty", search: "?s=", expectedOneBased: 1 },
  { name: "zero", search: "?s=0", expectedOneBased: 1 },
  { name: "negative", search: "?s=-1", expectedOneBased: 1 },
  { name: "fourteen", search: "?s=14", expectedOneBased: 1 },
  { name: "duplicate", search: "?s=3&s=4", expectedOneBased: 1 },
  { name: "unsafe-integer", search: "?s=9007199254740992", expectedOneBased: 1 },
  { name: "encoded-sentinel", search: "?s=sentinel%3D99", expectedOneBased: 1 },
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function makeElement(id) {
  return { id, style: {}, innerHTML: "", href: "", src: "", width: 0, height: 0 };
}

function executeCase(testCase) {
  const elements = new Map();
  const imageAssignments = [];
  const opened = [];
  const location = {
    href: `https://offline.invalid/wrath/artwork.xml${testCase.search}`,
    search: testCase.search,
  };
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, makeElement(id));
      return elements.get(id);
    },
    createElement(tag) {
      return makeElement(tag);
    },
    getElementsByTagName() {
      return [{ appendChild() {}, removeChild() {} }];
    },
  };
  class OfflineImage {
    constructor() {
      this.complete = true;
      this.width = 640;
      this.height = 480;
      this._src = "";
    }
    get src() {
      return this._src;
    }
    set src(value) {
      this._src = String(value);
      imageAssignments.push(this._src);
    }
  }

  // A browser-like global where window and the global object are identical.
  const context = {
    location,
    document,
    navigator: { userAgent: "Mozilla/5.0 offline-native-vm" },
    URLSearchParams,
    Image: OfflineImage,
    screenshotsCommonTotal: 12,
    screenshotsTotal: 13,
    theDirectory: "./images/artwork/",
    theLocDirectory: "./images/artwork/en_us/",
    __sentinel: 0,
    setTimeout() { return 1; },
    setInterval() { return 1; },
    clearInterval() {},
    console: { log() {}, warn() {}, error() {} },
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(source, context, { filename: "derived-screeniesimplified.js" });
  assert(typeof context.loadCheckForShot === "function", "native loadCheckForShot definition missing");
  assert(typeof context.omegaLightBox === "function", "native omegaLightBox definition missing before override");

  // Required controlled override: capture the native zero-based argument and
  // keep global nowViewing synchronized with that argument.
  context.omegaLightBox = function (index) {
    opened.push(index);
    context.nowViewing = index;
  };
  context.loadCheckForShot();

  const expectedZeroBased = testCase.expectedOneBased - 1;
  const screenLink = elements.get("screenLink");
  const expectedDir = expectedDirList[expectedZeroBased];
  const expectedHiRes = expectedHiResList[expectedZeroBased];
  const expectedHref = `${expectedDir}ss${expectedHiRes}-hires.jpg`;
  const observed = {
    nowViewing: context.nowViewing,
    openedShot: opened[0],
    shotList: context.shotList,
    dirList: context.dirList,
    hiResList: context.hiResList,
    dCurrent: elements.get("dCurrent").innerHTML,
    dTotal: elements.get("dTotal").innerHTML,
    screenLink: screenLink.href,
    sentinel: context.__sentinel,
    imageAssignmentCount: imageAssignments.length,
    imageAssignments: imageAssignments,
  };
  assert(opened.length === 1, `expected one omegaLightBox call, got ${opened.length}`);
  assert(observed.nowViewing === expectedZeroBased, `nowViewing ${observed.nowViewing} != ${expectedZeroBased}`);
  assert(observed.openedShot === expectedZeroBased, `openedShot ${observed.openedShot} != ${expectedZeroBased}`);
  assert(JSON.stringify(observed.shotList) === JSON.stringify(expectedShotList), "shotList common/locale sequence mismatch");
  assert(JSON.stringify(observed.dirList) === JSON.stringify(expectedDirList), "dirList mismatch");
  assert(JSON.stringify(observed.hiResList) === JSON.stringify(expectedHiResList), "hiResList mismatch");
  assert(observed.shotList.length === 13, "shotList length is not 13");
  assert(String(observed.dCurrent) === String(testCase.expectedOneBased), "dCurrent is not one-based selected value");
  assert(String(observed.dTotal) === "13", "dTotal is not 13");
  assert(observed.screenLink === expectedHref, `screenLink ${observed.screenLink} != ${expectedHref}`);
  assert(observed.sentinel === 0, `sentinel executed with value ${observed.sentinel}`);
  return {
    name: testCase.name,
    search: testCase.search,
    expectedOneBased: testCase.expectedOneBased,
    expectedZeroBased,
    observed,
    passed: true,
  };
}

const start = new Date().toISOString();
const results = [];
for (const testCase of cases) {
  try {
    results.push(executeCase(testCase));
  } catch (error) {
    results.push({ name: testCase.name, search: testCase.search, passed: false, error: String(error && error.stack || error) });
  }
}
const end = new Date().toISOString();
const assertions = {
  case_count: results.length,
  expected_case_count: 12,
  all_cases_passed: results.length === 12 && results.every((item) => item.passed),
  all_shot_lists_13: results.every((item) => item.passed && item.observed.shotList.length === 13),
  common12_locale1: results.every((item) => item.passed && JSON.stringify(item.observed.shotList) === JSON.stringify(expectedShotList)),
  dir_list_verified: results.every((item) => item.passed && JSON.stringify(item.observed.dirList) === JSON.stringify(expectedDirList)),
  hires_list_verified: results.every((item) => item.passed && JSON.stringify(item.observed.hiResList) === JSON.stringify(expectedHiResList)),
  one_based_to_zero_based_verified: results.every((item) => item.passed && item.observed.nowViewing === item.expectedZeroBased && item.observed.openedShot === item.expectedZeroBased),
  screen_link_hires_verified: results.every((item) => item.passed && item.observed.screenLink.endsWith("-hires.jpg")),
  dcurrent_dtotal_verified: results.every((item) => item.passed && String(item.observed.dTotal) === "13"),
  sentinel_never_executed: results.every((item) => item.passed && item.observed.sentinel === 0),
  image_stub_no_network: true,
};
const output = {
  schema: "native-viewer-vm-012-results/v1",
  batch_id: "NATIVE-VIEWER-VM-012",
  simulation: true,
  network_requests: 0,
  node_version: process.version,
  start_utc: start,
  end_utc: end,
  derived_sha256: derivedSha256,
  raw_sha256: provenance.inputs.raw_viewer.sha256,
  raw_bytes: provenance.inputs.raw_viewer.bytes,
  source_definition_execution: "complete derived JS in fresh vm context per case; native loadCheckForShot called; no animation/browser run",
  source_directories: { common: "./images/artwork/", locale: "./images/artwork/en_us/", common_count: 12, locale_count: 1 },
  assertions,
  cases: results,
  scope_not_covered: ["browser layout/paint", "network image fetch", "animation timers and next/previous animation behavior", "full build/export"],
};
fs.writeFileSync(RESULTS, JSON.stringify(output, null, 2) + "\n", "utf8");
console.log(JSON.stringify({ batch_id: output.batch_id, simulation: true, network_requests: 0, node_version: process.version, start_utc: start, end_utc: end, assertions, results }, null, 2));
if (!assertions.all_cases_passed) process.exitCode = 1;
