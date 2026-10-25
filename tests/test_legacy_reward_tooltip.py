from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import legacy_reward_tooltip as tooltips

SOURCE = """function showTip(toolTipContent)
{
  isShowing = true;
  result = [mouseX, mouseY, ttipWindowHeight, toolTipContent];
}
"""

class FirstRewardHoverTests(unittest.TestCase):
    def test_first_hover_does_not_require_a_prior_mousemove(self):
        fixed, changed = tooltips.rewrite_first_reward_hover(SOURCE)
        self.assertTrue(changed)
        node = "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
        script = "const vm=require('vm'),assert=require('assert');let c={document:{documentElement:{clientHeight:600},body:{clientHeight:600}},innerHeight:720,event:{clientX:110,clientY:210}};c.window=c;vm.createContext(c);vm.runInContext(" + repr(fixed) + ",c);vm.runInContext(\"showTip('original itemHTML')\",c);assert.deepStrictEqual(Array.from(c.result),[110,209,720,'original itemHTML']);"
        result = subprocess.run([node, "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_repeated_rewrite_and_changed_source(self):
        fixed, _ = tooltips.rewrite_first_reward_hover(SOURCE)
        self.assertEqual(tooltips.rewrite_first_reward_hover(fixed), (fixed, False))
        with self.assertRaisesRegex(ValueError, "signature"):
            tooltips.rewrite_first_reward_hover("function differentTooltip() {}")
        with self.assertRaisesRegex(ValueError, "signature"):
            tooltips.rewrite_first_reward_hover(SOURCE + SOURCE)

    def test_reward_nav_fallback_is_route_and_node_guarded(self):
        fixed, changed = tooltips.rewrite_rewards_nav_fallback("tree(result);\n", "/archive/")
        self.assertTrue(changed)
        self.assertEqual(tooltips.rewrite_rewards_nav_fallback(fixed, "/archive/"), (fixed, False))
        node = "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
        script = "const vm=require('vm'),assert=require('assert');const src=" + repr(fixed) + ";for(const [route,child,initial,expected] of [['rewards-general-armor.html','rewards-vindicators-armor.html',undefined,'1_9_11'],['rewards-veterans-armor.html','rewards-vindicators-armor.html',undefined,'1_9_11'],['unrelated.html','rewards-vindicators-armor.html',undefined,undefined],['rewards-general-armor.html','other.html',undefined,undefined],['rewards-general-armor.html','rewards-vindicators-armor.html','original','original']]){const c={result:initial,document:{location:{pathname:'/archive/pvp/'+route}},Menu1_9_11:['Rewards'],Menu1_9_11_3:['Vindicator Rewards','/archive/pvp/'+child],stripId:s=>s,tree:s=>{c.seen=s}};vm.createContext(c);vm.runInContext(src,c);assert.equal(c.seen,expected);}"
        result = subprocess.run([node, "-e", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == "__main__":
    unittest.main()
