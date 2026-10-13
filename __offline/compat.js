/*
 * Minimal compatibility layer for the 2008 Warcraft Encyclopedia mirror.
 *
 * The archived page already contains the original menu implementation.  This
 * file only supplies the browser-independent parts that the original code
 * assumed: reliable element selection, visible open/closed state when the
 * image glyphs are unavailable, keyboard activation, local same-site links,
 * and an offline target for the built-in site/encyclopedia search.
 *
 * It deliberately performs no network requests and does not replace article
 * content or missing article artwork.
 */
(function (window, document) {
    "use strict";

    var root = document.documentElement;
    function addClass(element, name) {
        if (!element) { return; }
        if (element.classList) {
            element.classList.add(name);
            return;
        }
        if ((" " + element.className + " ").indexOf(" " + name + " ") < 0) {
            element.className = (element.className ? element.className + " " : "") + name;
        }
    }

    function removeClass(element, name) {
        var re;
        if (!element) { return; }
        if (element.classList) {
            element.classList.remove(name);
            return;
        }
        re = new RegExp("(^|\\s)" + name + "(?=\\s|$)", "g");
        element.className = element.className.replace(re, " ").replace(/^\s+|\s+$/g, "");
    }

    function setExpandedState(control, expanded) {
        if (!control) { return; }
        addClass(control, expanded ? "offline-toggle-open" : "offline-toggle-closed");
        removeClass(control, expanded ? "offline-toggle-closed" : "offline-toggle-open");
        control.setAttribute("aria-expanded", expanded ? "true" : "false");
    }

    function lastElement(parent) {
        var i;
        var child;
        if (!parent) { return null; }
        if (parent.lastElementChild) { return parent.lastElementChild; }
        for (i = parent.childNodes.length - 1; i >= 0; i -= 1) {
            child = parent.childNodes[i];
            if (child.nodeType === 1) { return child; }
        }
        return null;
    }

    function computedDisplay(element) {
        var style;
        if (!element) { return "none"; }
        if (element.style && element.style.display) { return element.style.display; }
        if (window.getComputedStyle) {
            style = window.getComputedStyle(element, null);
            if (style) { return style.display; }
        }
        return "block";
    }

    function categoryGroup(categoryElement, categoryName) {
        var named = document.getElementById(categoryName + "MenuGroup");
        return named || lastElement(categoryElement);
    }

    function toggleCategory(categoryName) {
        var category = document.getElementById(categoryName);
        var group;
        var toggler;
        var open;
        if (!category) { return false; }
        group = categoryGroup(category, categoryName);
        if (!group || group === category) { return false; }
        open = computedDisplay(group) === "none";
        group.style.display = open ? "block" : "none";
        toggler = document.getElementById(categoryName + "Toggler");
        if (toggler) {
            toggler.style.backgroundImage = "none";
            toggler.setAttribute("aria-controls", group.id || categoryName + "MenuGroup");
            setExpandedState(toggler, open);
        }
        group.setAttribute("aria-hidden", open ? "false" : "true");
        return false;
    }

    function minimizeToggle() {
        var menu = document.getElementById("TopLevel");
        var container = document.getElementById("dragMenuContainer");
        var control = document.getElementById("minimizerText");
        var open;
        if (!menu) { return false; }
        open = computedDisplay(menu) === "none";
        menu.style.display = open ? "block" : "none";
        if (container) {
            addClass(container, open ? "offline-menu-open" : "offline-menu-closed");
            removeClass(container, open ? "offline-menu-closed" : "offline-menu-open");
            container.setAttribute("aria-expanded", open ? "true" : "false");
        }
        if (control) {
            control.setAttribute("aria-controls", "TopLevel");
            setExpandedState(control, open);
        }
        menu.setAttribute("aria-hidden", open ? "false" : "true");
        return false;
    }

    function keyboardToggle(event, callback) {
        var key = event.key || event.keyCode;
        if (key === "Enter" || key === " " || key === "Spacebar" || key === 13 || key === 32) {
            if (event.preventDefault) { event.preventDefault(); }
            callback();
        }
    }

    function decorateControls() {
        var togglers = document.getElementsByTagName("span");
        var i;
        var toggler;
        var group;
        var minimizer = document.getElementById("minimizerText");
        for (i = 0; i < togglers.length; i += 1) {
            toggler = togglers[i];
            if (!/(^|\s)plusSign(\s|$)/.test(toggler.className)) { continue; }
            group = document.getElementById(toggler.id.replace(/Toggler$/, "MenuGroup"));
            addClass(toggler, "offline-category-toggle");
            toggler.setAttribute("role", "button");
            toggler.setAttribute("tabindex", "0");
            if (group) {
                toggler.setAttribute("aria-controls", group.id);
                setExpandedState(toggler, computedDisplay(group) !== "none");
            }
            toggler.style.backgroundImage = "none";
            toggler.onkeydown = (function (target) {
                return function (event) {
                    keyboardToggle(event || window.event, function () {
                        toggleCategory(target.id.replace(/Toggler$/, ""));
                    });
                };
            }(toggler));
        }
        if (minimizer) {
            var menuContainer = document.getElementById("dragMenuContainer");
            var top;
            var topOpen;
            addClass(minimizer, "offline-menu-toggle");
            minimizer.setAttribute("aria-controls", "TopLevel");
            minimizer.setAttribute("role", "button");
            // The archived anchor uses href="javascript:minimizeToggle();".
            // Replace it with one ordinary click handler so the original
            // href and this compatibility handler cannot toggle twice.
            minimizer.setAttribute("href", "#");
            minimizer.onclick = function (event) {
                if (event && event.preventDefault) { event.preventDefault(); }
                minimizeToggle();
                return false;
            };
            top = document.getElementById("TopLevel");
            if (top) {
                topOpen = computedDisplay(top) !== "none";
                setExpandedState(minimizer, topOpen);
                if (menuContainer) {
                    addClass(menuContainer, topOpen ? "offline-menu-open" : "offline-menu-closed");
                    removeClass(menuContainer, topOpen ? "offline-menu-closed" : "offline-menu-open");
                    menuContainer.setAttribute("aria-expanded", topOpen ? "true" : "false");
                }
            }
        }
    }

    function localSameSitePath(value) {
        var parsed;
        var host;
        if (!value || !/^https?:\/\//i.test(value)) { return value; }
        try {
            parsed = new window.URL(value, window.location.href);
            host = (parsed.hostname || "").toLowerCase();
            if (host !== "www.worldofwarcraft.com" && host !== "worldofwarcraft.com") {
                return value;
            }
            return parsed.pathname + parsed.search + parsed.hash;
        } catch (ignore) {
            return value.replace(/^https?:\/\/www\.worldofwarcraft\.com(?::80)?/i, "");
        }
    }

    function normalizeInternalLinks() {
        var links = document.getElementsByTagName("a");
        var forms = document.getElementsByTagName("form");
        var i;
        var href;
        var action;
        for (i = 0; i < links.length; i += 1) {
            href = links[i].getAttribute("href");
            if (href) {
                href = localSameSitePath(href);
                links[i].setAttribute("href", href);
            }
        }
        for (i = 0; i < forms.length; i += 1) {
            action = forms[i].getAttribute("action");
            if (action) { forms[i].setAttribute("action", localSameSitePath(action)); }
        }
    }

    function topicTitleTarget(value) {
        var topics = window.topicsArray;
        var key;
        var wanted;
        if (!topics || !value) { return null; }
        wanted = String(value).replace(/^\s+|\s+$/g, "").toLowerCase();
        if (!wanted) { return null; }
        for (key in topics) {
            if (Object.prototype.hasOwnProperty.call(topics, key) &&
                    String(key).toLowerCase() === wanted && topics[key].linkString) {
                return topics[key].linkString;
            }
        }
        return null;
    }

    function uncollectedSearchTarget(kind, value, intendedTarget) {
        return "/WOW-Encyclopedia-Deployable-Archive/__offline/uncollected/index.html?kind=search&searchType=" +
            encodeURIComponent(kind) + "&query=" + encodeURIComponent(value || "") +
            "&target=" + encodeURIComponent(intendedTarget || "");
    }

    function archivedSearchTarget(kind, value) {
        var escaped = encodeURIComponent(value || "");
        if (kind === "techsupport" || kind === "ingamesupport") {
            return "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fus.blizzard.com%2Fsupport%2Findex.xml%3FgameId%3D11&reason=external-or-uncollected-resource" + escaped;
        }
        if (kind === "betaforum") {
            return "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fbeta.worldofwarcraft.com%2Fsearch.html%3FforumId%3D10001%26sid%3D1%26searchText%3D&reason=external-or-uncollected-resource" + escaped;
        }
        if (kind === "site") {
            return "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2Findex.xml%3Fq%3D&reason=external-or-uncollected-resource" + escaped;
        }
        if (kind === "encyclopedia") {
            return "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2Findex.xml%3Fq%3D&reason=external-or-uncollected-resource" + escaped + "&restrict=Encyclopedia";
        }
        return "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2Findex.xml%3Fq%3D&reason=external-or-uncollected-resource" + escaped;
    }

    function offlineSearchCall() {
        var form = document.getElementById("topSearch") || document.topSearch;
        var type;
        var input;
        var value;
        var target;
        var exactTopic;
        if (!form) { return false; }
        type = form.searchType || document.getElementById("searchType");
        input = form.searchBox || document.getElementById("searchBox");
        type = type && type.options ? type.options[type.selectedIndex].value : "encyclopedia";
        value = input ? input.value : "";
        target = archivedSearchTarget(type, value);
        if (type === "encyclopedia") {
            exactTopic = topicTitleTarget(value);
            if (exactTopic) {
                window.location.href = exactTopic;
                return false;
            }
            target = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2Findex.xml%3Fq%3D&reason=external-or-uncollected-resource" + encodeURIComponent(value) + "&restrict=Encyclopedia";
        } else if (type === "site") {
            target = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2Findex.xml%3Fq%3D&reason=external-or-uncollected-resource" + encodeURIComponent(value);
        } else {
            window.location.href = uncollectedSearchTarget(type, value, target);
            return false;
        }
        if (window.location.pathname.indexOf("/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2F&reason=external-or-uncollected-resource") !== -1) {
            target = target.replace("/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2Findex.xml&reason=external-or-uncollected-resource", "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2F__offline%2Fcompat.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsearch%2FsearchResults.html&reason=external-or-uncollected-resource");
        }
        // Search pages are not part of the bounded mirror.  Keep this
        // navigation local and let the server's explicit placeholder explain
        // the uncollected target instead of going online.
        window.location.href = uncollectedSearchTarget(type, value, target);
        return false;
    }

    function install() {
        if (!root) { return; }
        root.setAttribute("data-offline-compat", "2008-encyclopedia");
        window.toggleCategory = toggleCategory;
        window.minimizeToggle = minimizeToggle;
        window.searchCall = offlineSearchCall;
        normalizeInternalLinks();
        decorateControls();
    }

    if (document.addEventListener) {
        document.addEventListener("DOMContentLoaded", install, false);
    }
    install();

    window.WowOfflineCompat = {
        version: "2008.1",
        install: install,
        normalizeInternalLinks: normalizeInternalLinks,
        toggleCategory: toggleCategory,
        minimizeToggle: minimizeToggle,
        searchCall: offlineSearchCall
    };
}(window, document));
