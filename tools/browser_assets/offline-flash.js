/* Bounded manual Ruffle bridge for three validated historical exhibits. */
(function () {
  "use strict";

  var tag = document.currentScript;
  var kind = tag && tag.getAttribute("data-offline-flash");
  var basePath = tag && tag.getAttribute("data-base-path");
  var exhibits = {
    socket_anim: {
      path: "info/items/images/socket_anim.swf",
      sha256: "c289e5fea2d04180d0615d8956049649d6f0362134e71c62589bbb41a7c26576",
      width: 48,
      height: 47,
    },
    dwarf_male: {
      path: "info/races/images/dancing/gifs/dwarf_male.swf",
      sha256: "00d7e4fff668eb4a58da18571c1b9a5082c83e7197d82361c990f87942a135a9",
      width: 250,
      height: 250,
    },
    tuskarr_idle: {
      path: "wrath/flash/global/tuskarr_idle.swf",
      sha256: "544e29b972fbf8547c304232a3f7461aaa69f6431b98f627a3762e8192c9bf3e",
      width: 360,
      height: 450,
    },
  };
  var allowedRoutes = {
    socket: "/info/items/socketeditems.html",
    dance: "/info/races/dancing.html",
    tuskarr: "/wrath/features/factions/tuskarr.xml.html",
  };

  var state = {
    kind: kind,
    basePath: basePath,
    runtime: "pending",
    cases: [],
    externalResourcePolicy: "local-base-path-only",
  };
  var runtimePromise = null;
  var bytesPromises = {};
  window.__offlineFlash = state;

  function localUrl(relativePath) {
    return basePath + relativePath;
  }

  function normaliseBasePath(value) {
    if (typeof value !== "string" || !value || /[?#\\\0]/.test(value)) return "";
    try {
      var parsed = new URL(value, window.location.href);
      if (parsed.origin !== window.location.origin || parsed.search || parsed.hash) return "";
      var pathname = parsed.pathname || "/";
      if (pathname.charAt(pathname.length - 1) !== "/") pathname += "/";
      return pathname;
    } catch (ignore) {
      return "";
    }
  }

  function currentRoute() {
    var prefix = normaliseBasePath(basePath);
    if (!prefix || window.location.pathname.indexOf(prefix) !== 0) return "";
    var route = window.location.pathname.slice(prefix.length);
    if (!route || route.charAt(0) !== "/") route = "/" + route;
    return route;
  }

  function report(message) {
    state.lastMessage = String(message);
    if (window.console && typeof window.console.warn === "function") {
      window.console.warn("offline Flash: " + message);
    }
  }

  function unavailable(host, label) {
    if (!host) return;
    var caption = document.createElement("div");
    caption.className = "offline-flash-unavailable";
    caption.setAttribute("role", "img");
    caption.setAttribute("aria-label", label);
    caption.style.boxSizing = "border-box";
    caption.style.display = "flex";
    caption.style.alignItems = "center";
    caption.style.justifyContent = "center";
    caption.style.width = "100%";
    caption.style.height = "100%";
    caption.style.minHeight = "28px";
    caption.style.padding = "4px";
    caption.style.color = "#d8c59a";
    caption.style.background = "rgba(0,0,0,.35)";
    caption.style.font = "12px/1.3 Arial,sans-serif";
    caption.style.textAlign = "center";
    caption.textContent = label;
    host.replaceChildren(caption);
  }

  function loadRuntime() {
    if (runtimePromise) return runtimePromise;
    if (!basePath || (basePath.indexOf("?") >= 0) || (basePath.indexOf("#") >= 0)) {
      runtimePromise = Promise.reject(new Error("invalid offline Flash base path"));
      return runtimePromise;
    }
    window.RufflePlayer = window.RufflePlayer || {};
    window.RufflePlayer.config = {
      polyfills: false,
      allowScriptAccess: false,
      openUrlMode: "deny",
      allowNetworking: "internal",
      autoplay: "on",
      unmuteOverlay: "hidden",
      wmode: "transparent",
      allowFullscreen: false,
      showSwfDownload: false,
      contextMenu: "off",
      splashScreen: false,
      logLevel: "error",
    };
    runtimePromise = new Promise(function (resolve, reject) {
      if (window.RufflePlayer && typeof window.RufflePlayer.newest === "function") {
        state.runtime = "ready";
        resolve();
        return;
      }
      var runtime = document.createElement("script");
      runtime.async = true;
      runtime.setAttribute("data-offline-ruffle-runtime", "true");
      runtime.src = localUrl("__offline/vendor/ruffle/ruffle.js");
      runtime.onload = function () {
        if (!window.RufflePlayer || typeof window.RufflePlayer.newest !== "function") {
          state.runtime = "error";
          reject(new Error("Ruffle runtime did not expose newest()"));
          return;
        }
        state.runtime = "ready";
        resolve();
      };
      runtime.onerror = function () {
        state.runtime = "error";
        reject(new Error("Ruffle runtime failed to load"));
      };
      document.head.appendChild(runtime);
    });
    return runtimePromise;
  }

  function digest(buffer) {
    if (!window.crypto || !window.crypto.subtle) {
      return Promise.reject(new Error("Web Crypto is unavailable for SWF hash verification"));
    }
    return window.crypto.subtle.digest("SHA-256", buffer).then(function (value) {
      return Array.prototype.map.call(new Uint8Array(value), function (byte) {
        return byte.toString(16).padStart(2, "0");
      }).join("");
    });
  }

  function loadBytes(exhibit) {
    if (bytesPromises[exhibit.path]) return bytesPromises[exhibit.path];
    bytesPromises[exhibit.path] = fetch(localUrl(exhibit.path), {
      cache: "no-store",
      credentials: "omit",
    }).then(function (response) {
      if (!response.ok) throw new Error("SWF HTTP " + response.status + " for " + exhibit.path);
      return response.arrayBuffer();
    }).then(function (buffer) {
      return digest(buffer).then(function (actual) {
        if (actual.toLowerCase() !== exhibit.sha256) {
          throw new Error("SWF SHA mismatch for " + exhibit.path);
        }
        return buffer;
      });
    });
    return bytesPromises[exhibit.path];
  }

  function createPlayer(exhibit, key) {
    if (!window.RufflePlayer || typeof window.RufflePlayer.newest !== "function") {
      throw new Error("RufflePlayer.newest() unavailable");
    }
    var player = window.RufflePlayer.newest().createPlayer();
    player.setAttribute("width", String(exhibit.width));
    player.setAttribute("height", String(exhibit.height));
    player.setAttribute("data-offline-flash-exhibit", key);
    player.style.width = exhibit.width + "px";
    player.style.height = exhibit.height + "px";
    player.style.display = "block";
    player.addEventListener("contextmenu", function (event) { event.preventDefault(); });
    return player;
  }

  function loadPlayer(player, exhibit) {
    return loadBytes(exhibit).then(function (buffer) {
      return player.ruffle().load({
        data: buffer.slice(0),
        swfFileName: exhibit.path,
      });
    }).then(function () {
      var controller = player.ruffle();
      controller.resume();
      return controller;
    });
  }

  function isSocketObject(object) {
    var width = object.getAttribute("width");
    var height = object.getAttribute("height");
    if (width !== "48" || height !== "47") return false;
    var param = object.querySelector('param[name="movie"]');
    var embed = object.querySelector("embed");
    var source = (param && param.getAttribute("value")) || (embed && embed.getAttribute("src")) || "";
    return /(?:^|[\\/])socket_anim\.swf$/i.test(source);
  }

  function mountSocket(object, index) {
    var exhibit = exhibits.socket_anim;
    var host = object.parentElement || object;
    var player;
    try {
      player = createPlayer(exhibit, "socket_anim-" + index);
      object.replaceWith(player);
      return loadPlayer(player, exhibit).then(function () {
        state.cases.push({ key: "socket_anim-" + index, status: "displayed", width: exhibit.width, height: exhibit.height });
      }).catch(function (error) {
        unavailable(host, "Socket animation unavailable offline");
        state.cases.push({ key: "socket_anim-" + index, status: "unavailable", error: String(error) });
        report(error);
      });
    } catch (error) {
      unavailable(host, "Socket animation unavailable offline");
      state.cases.push({ key: "socket_anim-" + index, status: "unavailable", error: String(error) });
      report(error);
      return Promise.resolve();
    }
  }

  function setupSockets() {
    var objects = Array.prototype.filter.call(document.querySelectorAll("object"), isSocketObject);
    state.expected = 5;
    state.matched = objects.length;
    if (objects.length !== 5) report("expected five socket objects, found " + objects.length);
    return loadRuntime().then(function () {
      return Promise.all(objects.map(mountSocket));
    }).catch(function (error) {
      report(error);
      objects.forEach(function (object) { unavailable(object.parentElement || object, "Socket animation unavailable offline"); });
    });
  }

  function updateDanceDownloads(race, gender) {
    try {
      var links = window.linkList[race][gender];
      var sizes = window.sizeList[race][gender];
      function localisedZipHref(rawPath, link) {
        var requestedPath = "/info/races/" + String(rawPath).replace(/^\/+/, "");
        var requested = "https://www.worldofwarcraft.com" + requestedPath;
        var source = "https://www.worldofwarcraft.com/info/races/dancing.html";
        var existing = link && link.getAttribute("href");
        try {
          var missing = new URL(existing || localUrl("__offline/missing.html"), window.location.href);
          if (missing.pathname.indexOf("__offline/missing.html") < 0) {
            missing = new URL(localUrl("__offline/missing.html"), window.location.href);
          }
          missing.searchParams.set("source", source);
          missing.searchParams.set("requested", requested);
          missing.searchParams.set("reason", "invalid-overlay-or-uncollected-site-resource");
          return missing.pathname + missing.search;
        } catch (ignore) {
          return localUrl("__offline/missing.html") + "?source=" + encodeURIComponent(source) +
            "&requested=" + encodeURIComponent(requested) +
            "&reason=invalid-overlay-or-uncollected-site-resource";
        }
      }
      [["dl_transparent", "txt_transparent"], ["dl_black", "txt_black"], ["dl_avatar", "txt_avatar"]].forEach(function (pair, index) {
        var link = document.getElementById(pair[0]);
        var size = document.getElementById(pair[1]);
        if (link) link.setAttribute("href", localisedZipHref(links[index], link));
        if (size) size.textContent = sizes[index];
      });
    } catch (ignore) {
      /* The historical download metadata is optional to the exhibit. */
    }
  }

  function setupDance() {
    var host = document.getElementById("flashImage");
    state.expected = 1;
    if (!host) {
      report("dance host is missing");
      return Promise.resolve();
    }
    var generation = 0;
    function renderDance() {
      var race = Number(window.thisRace || 0);
      var gender = Number(window.thisGender || 0);
      updateDanceDownloads(race, gender);
      generation += 1;
      var current = generation;
      if (race !== 0 || gender !== 0) {
        unavailable(host, "This historical dance selection is unavailable offline");
        state.selection = { race: race, gender: gender, status: "unavailable" };
        return Promise.resolve();
      }
      var exhibit = exhibits.dwarf_male;
      host.replaceChildren();
      return loadRuntime().then(function () {
        if (current !== generation) return null;
        var player = createPlayer(exhibit, "dwarf_male");
        host.appendChild(player);
        return loadPlayer(player, exhibit).then(function () {
          if (current === generation) {
            state.selection = { race: race, gender: gender, status: "displayed" };
            state.cases.push({ key: "dwarf_male", status: "displayed", width: exhibit.width, height: exhibit.height });
          }
        });
      }).catch(function (error) {
        if (current === generation) {
          unavailable(host, "Dwarf dance unavailable offline");
          state.selection = { race: race, gender: gender, status: "unavailable", error: String(error) };
        }
        report(error);
      });
    }
    window.reloadData = renderDance;
    window.reloadRace = function (value) {
      window.thisRace = Number(value);
      return renderDance();
    };
    window.reloadGender = function (value) {
      window.thisGender = Number(value);
      return renderDance();
    };
    state.renderDance = renderDance;
    return renderDance();
  }

  function setupTuskarr() {
    var hosts = document.querySelectorAll("#flashchar");
    var host = hosts.length ? hosts[0] : null;
    state.expected = 1;
    if (!host) {
      report("Tuskarr host is missing");
      return Promise.resolve();
    }
    var exhibit = exhibits.tuskarr_idle;
    host.replaceChildren();
    return loadRuntime().then(function () {
      var player = createPlayer(exhibit, "tuskarr_idle");
      host.appendChild(player);
      return loadPlayer(player, exhibit).then(function () {
        state.cases.push({ key: "tuskarr_idle", status: "displayed", width: exhibit.width, height: exhibit.height });
      });
    }).catch(function (error) {
      unavailable(host, "Tuskarr animation unavailable offline");
      report(error);
    });
  }

  function start() {
    state.route = currentRoute();
    if (!state.route || allowedRoutes[kind] !== state.route) {
      state.status = "skipped";
      state.done = Promise.resolve(state);
      report("helper route/kind mismatch");
      return;
    }
    var task;
    if (kind === "socket") task = setupSockets();
    else if (kind === "dance") task = setupDance();
    else if (kind === "tuskarr") task = setupTuskarr();
    else {
      report("unsupported helper kind");
      task = Promise.resolve();
    }
    state.done = task.then(function () {
      state.status = "complete";
      return state;
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
