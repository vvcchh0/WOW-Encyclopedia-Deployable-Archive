"""Small, source-guarded repairs for legacy reward pages."""
import json
import re

ROUTE = "/new-hp/js/functions.js"
SOURCE16_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
MARKER = "__offline-reward-tooltip-first-hover"

def rewrite_first_reward_hover(text: str) -> tuple[str, bool]:
    if MARKER in text:
        return text, False
    pattern = r"(function showTip\(toolTipContent\)\s*\{\s*)(isShowing = true;)"
    if len(re.findall(pattern, text)) != 1:
        raise ValueError("shared reward tooltip showTip source signature changed")
    prelude = (
        "/* " + MARKER + " */\n"
        "  var hoverEvent = window.event;\n"
        "  window.mouseX = hoverEvent && typeof hoverEvent.clientX === 'number' ? hoverEvent.clientX : (typeof window.mouseX === 'number' ? window.mouseX : 0);\n"
        "  window.mouseY = hoverEvent && typeof hoverEvent.clientY === 'number' ? hoverEvent.clientY - 1 : (typeof window.mouseY === 'number' ? window.mouseY : 0);\n"
        "  window.ttipWindowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;\n  "
    )
    return re.sub(pattern, lambda m: m[1] + prelude + m[2], text, count=1), True

def rewrite_rewards_nav_fallback(text: str, base_path: str) -> tuple[str, bool]:
    marker = "__offline-legacy-reward-nav-fallback"
    if marker in text:
        return text, False
    matches = list(re.finditer(r"(?m)^[ \t]*tree\(result\);", text))
    if len(matches) != 1:
        raise ValueError("reward navtree tree(result) signature changed")
    routes = [base_path + "pvp/rewards-general-armor.html", base_path + "pvp/rewards-veterans-armor.html"]
    known_child = base_path + "pvp/rewards-vindicators-armor.html"
    block = (
        f"/* {marker}: two historical armor pages absent from the later menu */\n"
        f"if (typeof result === 'undefined' && {json.dumps(routes)}.indexOf(document.location.pathname) !== -1 &&\n"
        "    typeof Menu1_9_11 !== 'undefined' && typeof Menu1_9_11_3 !== 'undefined' &&\n"
        "    typeof stripId === 'function' && stripId(Menu1_9_11[0]) === 'Rewards' &&\n"
        f"    Menu1_9_11_3[1] === {json.dumps(known_child)}) {{ result = '1_9_11'; }}\n"
    )
    at = matches[0].start()
    return text[:at] + block + text[at:], True
