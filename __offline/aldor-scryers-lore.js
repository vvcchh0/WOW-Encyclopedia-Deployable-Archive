// Source16 Aldor/Scryers lore supplement; injected only on the main page.
(function () {
  "use strict";
  var suppliedLore = {"alliance":"<h3>The Aldor</h3>Shattrath was once the draenei capital of Draenor. Its name means \"dwelling of light.\" When the Burning Legion turned the orcs against the draenei, the fiercest battle was fought there. The draenei fought tooth and nail, but in the end, the city fell. The city was left in ruins and darkness until the Sha'tar arrived. The Sha'tar, whose name means \"born from light\", are the naaru who came to Outland to fight the demons of the Burning Legion. The naaru were drawn to the ruins of Shattrath City, where a small remnant of the draenei priesthood conducted its rites inside a ruined temple. The priesthood, known as the Aldor, quickly regained its strength as word of the Sha'tar's arrival spread. Reconstruction of Shattrath was soon underway.<br /><br />It wouldn't be long, however, before the city came under attack once again...","horde":"<h3>The Scryers</h3>This time, the attack came from the armies of Illidan Stormrage. A large regiment of blood elves had been sent by Illidan's ally, Prince Kael'thas Sunstrider, to lay waste to the city. As the regiment of blood elves crossed the bridge, the Aldor's exarchs and vindicators lined up to defend the Terrace of Light. Then the unexpected happened: the blood elves laid down their weapons in front of the city's defenders. Their leader, a blood elf elder known as Voren'thal, stormed into the Terrace of Light and demanded to speak to the naaru A'dal. As the naaru approached him, Voren'thal knelt and uttered the following words: \"I've seen you in a vision, naaru. My race's only hope for survival lies with you. My followers and I are here to serve you.\"<br /><br />The defection of Voren'thal and his followers was the largest loss ever incurred by Kael'thas' forces. Nor were these just any blood elves. Many of the best and brightest amongst Kael'thas' scholars and magisters had been swayed by Voren'thal's influence. The naaru accepted the defectors, who became known as the Scryers."};
  function installLore() {
    var target = window.loreTexts;
    if (!target || typeof target !== "object") {
      target = window.loreTexts = {};
    }
    if (typeof target.alliance === "undefined" || target.alliance === null || target.alliance === "") {
      target.alliance = suppliedLore.alliance;
    }
    if (typeof target.horde === "undefined" || target.horde === null || target.horde === "") {
      target.horde = suppliedLore.horde;
    }
    var node = document.getElementById("loreText");
    if (!node) return;
    var current = node.innerHTML;
    if (current && current !== "undefined" && current !== "null") return;
    var hordeRewards = document.getElementById("hordeRewards");
    var hordeVisible = false;
    if (hordeRewards) {
      hordeVisible = window.getComputedStyle
        ? window.getComputedStyle(hordeRewards).visibility === "visible"
        : hordeRewards.style.visibility === "visible";
    }
    node.innerHTML = target[hordeVisible ? "horde" : "alliance"];
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installLore, false);
  } else {
    installLore();
  }
})();
