var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Priest"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Discipline\
							"; school[t++] = "\
Holy\
							"; school[t++] = "\
Shadow\
							"; school[t++] = "\
New Spells Obtained From Talents\
							"; school[t++] = "\
Draenei\
							"; school[t++] = "\
Blood Elf\
							";    t = 0;

spellsArray.DONTLOCALIZE[t] = "massdispel";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 1181;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 1500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Mass Dispel\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Dispels magic in a 15 yard radius, removing 1 harmful spell from each friendly target and 1 beneficial spell from each enemy target. Affects a maximum of 5 friendly targets and 5 enemy targets. This dispel is potent enough to remove Magic effects that are normally undispellable.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "bindingheal";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 1034;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 1500;
spellsArray.range[t] = 40;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Binding Heal\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Heals a friendly target and the caster for 1053 to 1350.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "prayerofmending";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 68;
spellsArray.barCost[t] = 976;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Prayer of Mending\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Places a spell on the target that heals them for 702 to 858 the next time they take damage. When the heal occurs, Prayer of Mending jumps to a nearby raid target. Jumps up to 5 times and lasts 1 min after each jump. This spell can only be placed on one target at a time.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "shadoworddeath";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 62;
spellsArray.barCost[t] = 243;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 6000;
spellsArray.spellName[t] = "\
							\
Shadow Word: Death\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
A word of dark binding that inflicts 450 to 522 Shadow damage to the target. If the target is not killed by Shadow Word: Death, the caster takes damage equal to the damage inflicted upon the target.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "shadoworddeath";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 309;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 6000;
spellsArray.spellName[t] = "\
							\
Shadow Word: Death\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
A word of dark binding that inflicts 572 to 664 Shadow damage to the target. If the target is not killed by Shadow Word: Death, the caster takes damage equal to the damage inflicted upon the target.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "shadowfiend";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 210;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 300000;
spellsArray.spellName[t] = "\
							\
Shadowfiend\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Creates a shadowy fiend to attack the target. Caster receives mana when the Shadowfiend deals damage. Lasts 15 sec.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "painsuppression";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 154;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 180000;
spellsArray.spellName[t] = "\
							\
Pain Suppression\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Reduces all damage taken by 60% for 8 sec.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "circleofhealing";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 400;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 40;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Circle of Healing\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Heals target party member and other party members within 15 yards of the target for 289 to 319.\
			<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 450 Mana, 337 to 372 Healing<br>\
			&nbsp;Rank 3: 500 Mana, 385 to 426 Healing<br>\
			&nbsp;Rank 4: 550 Mana, 434 to 479 Healing<br>\
			&nbsp;Rank 5: 600 Mana, 475 to 525 Healing\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "vampirictouch";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 325;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 1500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Vampiric Touch\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
			Causes 450 Shadow damage over 15 sec to your target and causes all party members to gain mana equal to 5% of any Shadow spell damage you deal.\
			<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 400 Mana, 635 to 640 Damage<br>\
			&nbsp;Rank 3: 425 Mana, 685 to 690 Damage\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "fearward";
spellsArray.school[t] = 4;
spellsArray.rank[t] = -1;
spellsArray.level[t] = 20;
spellsArray.barCost[t] = 100;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 30000;
spellsArray.spellName[t] = "\
							\
Fear Ward\
							"; spellsArray.extra[t] = "\
Race: Draenei\
							"; spellsArray.description[t] = "\
			Wards the friendly target against Fear. The next Fear effect used against the target will fail, using up the ward. Lasts 10 min.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "consumemagic";
spellsArray.school[t] = 5;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 20;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 120000;
spellsArray.spellName[t] = "\
							\
Consume Magic\
							"; spellsArray.extra[t] = "\
Race: Blood Elf\
							"; spellsArray.description[t] = "\
			Dispels one beneficial Magic effect from the caster and gives them 120 to 154 mana. (453 to 488 mana at level 70)\
							"; t++;	