var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;


var theClassString = "\
Mage"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Arcane\
							"; school[t++] = "\
Fire\
							"; school[t++] = "\
Ice\
							"; school[t++] = "\
New Spells Obtained From Talents\
							"; school[t++] = "\
Water Elemental\
							"; t = 0;

							
spellsArray.DONTLOCALIZE[t] = "arcaneblast";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 190;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 2500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Arcane Blast\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Blasts the target with energy, dealing 575 to 665 Arcane damage. Each time you cast Arcane Blast, the casting time is reduced while mana cost is increased. Effect stacks up to 5 times and lasts 8 sec.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "invisibility";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 68;
spellsArray.barCost[t] = 263;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 300000;
spellsArray.spellName[t] = "\
							\
Invisibility\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Fades the caster to invisibility over 8 sec. The effect is cancelled if you perform or receive any hostile actions. While invisible, you can only see other invisible targets and those who can see invisible. Lasts 20 sec.\
							"; t++;
							

spellsArray.DONTLOCALIZE[t] = "spellsteal";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 474;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Spellsteal\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Steals a beneficial magic effect from the target. This effect lasts a maximum of 2 min.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "moltenarmor";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 62;
spellsArray.barCost[t] = 630;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Molten Armor\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Causes 75 Fire damage when hit and reduces the chance you are critically hit by melee attacks and spells by 10%. Only one type of Armor spell can be active on the Mage at any time. Lasts 30 min. \
							"; t++;
			
spellsArray.DONTLOCALIZE[t] = "icelance";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 150;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 1500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Ice Lance\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Deals 146 to 186 Frost damage to an enemy target. Causes triple damage against Frozen targets.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "slow";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 861;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Slow\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Reduces target's movement speed by 50%, increases the time between ranged attacks by 50% and increases casting time by 50%. Lasts 15 sec. Slow can only affect one target at a time.\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "dragonsbreath";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 475;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 20000;
spellsArray.spellName[t] = "\
							\
Dragon's Breath\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Targets in a cone in front of the caster take 370 to 430 Fire damage and are Disoriented for 3 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 575 Mana, 454-526 Damage<br>\
		&nbsp;Rank 3: 660 Mana, 574-666 Damage<br>\
		&nbsp;Rank 4: 700 Mana, 680-790 Damage<br>\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "summonwaterelemental";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 492;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 180000;
spellsArray.spellName[t] = "\
							\
Summon Water Elemental\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Summon a Water Elemental to fight for the caster for 45 sec.\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "waterbolt";
spellsArray.school[t] = 4;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 224;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 2500;
spellsArray.range[t] = 35;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Waterbolt\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Deals 486 to 558 Frost damage to the target.\
							"; t++;							
	
spellsArray.DONTLOCALIZE[t] = "frostnova";
spellsArray.school[t] = 4;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 313;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 35;
spellsArray.cooldown[t] = 25000;
spellsArray.spellName[t] = "\
							\
Frost Nova\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Blasts enemies in a 8 yard radius for 114 to 126 Frost damage and freezes them in place for up to 8 sec. Damage caused may interrupt the effect.\
							"; t++;							
	