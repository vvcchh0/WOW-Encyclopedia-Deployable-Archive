var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Druid"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Balance\
							"; school[t++] = "\
Feral Combat\
							"; school[t++] = "\
Restoration\
							"; school[t++] = "\
New Spells Obtained From Talents\
							";  t = 0;

//**start spell copy

spellsArray.DONTLOCALIZE[t] = "cyclone";		//spell name (lower case, no spaces, no punctuation) this is used for the icon and screenshot images
spellsArray.school[t] = 0;							//0 for Balance, 1 for Feral, 2 for Restoration
spellsArray.rank[t] = 0;							//the Rank
spellsArray.level[t] = 70;							//Level required (found on the trainer)
spellsArray.barCost[t] = 249;						//How much mana, energy, or rage the spell costs
spellsArray.barType[t] = 0;							//0 for mana, 1 for energy, 2 for rage
spellsArray.castTime[t] = 1500;						//cast time (in milliseconds), put -1 if you don't want to display "Instant Cast"
spellsArray.range[t] = 30;							//range
spellsArray.cooldown[t] = 0;						//cool down (in milliseconds)
spellsArray.spellName[t] = "\
							\
Cyclone\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Tosses the enemy target into the air, preventing all action but making them invulnerable for up to 6 sec. Only one target can be affected by your Cyclone at a time.\
							"; t++;
							
//*end spell copy




//**start spell copy

spellsArray.DONTLOCALIZE[t] = "maim";		//spell name (lower case, no spaces, no punctuation) this is used for the icon and screenshot images
spellsArray.school[t] = 1;							//0 for Balance, 1 for Feral, 2 for Restoration
spellsArray.rank[t] = 1;							//the Rank
spellsArray.level[t] = 62;							//Level required (found on the trainer)
spellsArray.barCost[t] = 35;						//How much mana, energy, or rage the spell costs
spellsArray.barType[t] = 1;							//0 for mana, 1 for energy, 2 for rage
spellsArray.castTime[t] = 0;						//cast time (in milliseconds), put -1 if you don't want to display "Instant Cast"
spellsArray.range[t] = 9;							//range
spellsArray.cooldown[t] = 10000;						//cool down (in milliseconds)
spellsArray.spellName[t] = "\
							\
Maim\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
<span style='color:#ff0000;'>Requires Cat Form</span><br>\
Finishing move that causes damage plus an additional amount and incapacitates the opponent. Any damage caused will revive the target. Causes more damage and lasts longer per combo point:<br>\
&nbsp;&nbsp;&nbsp;1 point: 129 damage and 2 seconds<br>\
&nbsp;&nbsp;&nbsp;2 points: 213 damage and 3 seconds<br>\
&nbsp;&nbsp;&nbsp;3 points: 297 damage and 4 seconds<br>\
&nbsp;&nbsp;&nbsp;4 points: 381 damage and 5 seconds<br>\
&nbsp;&nbsp;&nbsp;5 points: 465 damage and 6 seconds\
							"; t++;
							
//*end spell copy




//**start spell copy

spellsArray.DONTLOCALIZE[t] = "lacerate";		//spell name (lower case, no spaces, no punctuation) this is used for the icon and screenshot images
spellsArray.school[t] = 1;							//0 for Balance, 1 for Feral, 2 for Restoration
spellsArray.rank[t] = 1;							//the Rank
spellsArray.level[t] = 66;							//Level required (found on the trainer)
spellsArray.barCost[t] = 15;						//How much mana, energy, or rage the spell costs
spellsArray.barType[t] = 2;							//0 for mana, 1 for energy, 2 for rage
spellsArray.castTime[t] = 0;						//cast time (in milliseconds), put -1 if you don't want to display "Instant Cast"
spellsArray.range[t] = 0;							//range
spellsArray.cooldown[t] = 0;						//cool down (in milliseconds)
spellsArray.spellName[t] = "\
							\
Lacerate\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
<span style='color:#ff0000;'>Requires Bear Form, Dire Bear Form</span><br>\
Lacerates the enemy target, making them bleed for 155 damage over 15 sec and causing a high amount of threat. This effect stacks up to 5 times on the same target.\
							"; t++;
							
//*end spell copy


//**start spell copy

spellsArray.DONTLOCALIZE[t] = "flightform";		//spell name (lower case, no spaces, no punctuation) this is used for the icon and screenshot images
spellsArray.school[t] = 1;							//0 for Balance, 1 for Feral, 2 for Restoration
spellsArray.rank[t] = 0;							//the Rank
spellsArray.level[t] = 68;							//Level required (found on the trainer)
spellsArray.barCost[t] = 498;						//How much mana, energy, or rage the spell costs
spellsArray.barType[t] = 0;							//0 for mana, 1 for energy, 2 for rage
spellsArray.castTime[t] = 0;						//cast time (in milliseconds), put -1 if you don't want to display "Instant Cast"
spellsArray.range[t] = 0;							//range
spellsArray.cooldown[t] = 0;						//cool down (in milliseconds)
spellsArray.spellName[t] = "\
							\
Flight Form (Shapeshift)\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Transforms the Druid into a flight form, increasing movement speed by 60% and allowing you to fly. Can only use this form in Outland.<br><br>\
The act of shapeshifting frees the caster of Polymorph and Movement Impairing effects.\
							"; t++;
							
//*end spell copy





spellsArray.DONTLOCALIZE[t] = "lifebloom";		//spell name (lower case, no spaces, no punctuation) this is used for the icon and screenshot images
spellsArray.school[t] = 2;							//0 for Balance, 1 for Feral, 2 for Restoration
spellsArray.rank[t] = 1;							//the Rank
spellsArray.level[t] = 64;							//Level required (found on the trainer)
spellsArray.barCost[t] = 220;						//How much mana, energy, or rage the spell costs
spellsArray.barType[t] = 0;							//0 for mana, 1 for energy, 2 for rage
spellsArray.castTime[t] = 0;						//cast time (in milliseconds), put -1 if you don't want to display "Instant Cast", put 1 for "Next melee"
spellsArray.range[t] = 40;							//range
spellsArray.cooldown[t] = 0;						//cool down (in milliseconds)
spellsArray.spellName[t] = "\
							\
Lifebloom\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Heals the target for 273 over 7 sec. When Lifebloom completes its duration or is dispelled, the target is instantly healed for 600. This effect can stack up to 3 times on the same target.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "mangle";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Mangle\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Mangle the target, inflicting damage and causing the target to take additional damage from bleed effects for 10 sec. This ability can be used in Cat Form or Dire Bear Form.\
		<br><br>&nbsp;Bear Form:<br>\
		&nbsp;20 Rage, 5 yd range, Instant, 6 sec cooldown<br>\
		&nbsp;130% damage plus x, +25% damage from bleed effects.<br>\
		&nbsp;Rank 1: +98<br>\
		&nbsp;Rank 2: +137<br>\
		&nbsp;Rank 3: +176\
		<br><br>&nbsp;Cat Form:<br>\
		&nbsp;45 Energy, 5 yd range, Instant, Awards 1 combo point.<br>\
		&nbsp;150% damage plus x, +25% damage from bleed effects.<br>\
		&nbsp;Rank 1: +140<br>\
		&nbsp;Rank 2: +180<br>\
		&nbsp;Rank 3: +233\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "forceofnature";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 374;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 180000;
spellsArray.spellName[t] = "\
							\
Force of Nature\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Summons 3 treants to attack the enemy target for 30 sec.\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "treeoflife";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 872;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Tree of Life\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Transforms the Druid into the Tree of Life Form. While in this form you increase healing done by 25% of your total Spirit for all party members within 40 yards, your movement speed is reduced by 20%, and you can only cast Swiftmend and healing over time spells, but the mana cost of these spells is reduced by 20%.<br><br>The act of shapeshifting frees the caster of Polymorph and Movement Impairing effects.\
							"; t++;							
							
