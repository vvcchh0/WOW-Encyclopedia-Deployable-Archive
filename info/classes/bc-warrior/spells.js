var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Warrior"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Arms\
							"; school[t++] = "\
Fury\
							"; school[t++] = "\
Protection\
							"; school[t++] = "\
New Spells Obtained From Talents\
							"; t = 0;

spellsArray.DONTLOCALIZE[t] = "heroicstrike";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 10;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 15;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Heroic Strike\
							"; spellsArray.extra[t] = "\
Next melee<br>\
Requires Melee Weapon\
							"; spellsArray.description[t] = "\
A strong attack that increases melee damage by 182 and causes a high amount of threat. <span class = 'newEffect'>Causes additional damage against dazed targets.</span>\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "heroicstrike";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 11;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 15;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Heroic Strike\
							"; spellsArray.extra[t] = "\
Next melee<br>\
Requires Melee Weapon\
							"; spellsArray.description[t] = "\
A strong attack that increases melee damage by 247 and causes a high amount of threat. <span class = 'newEffect'>Causes additional damage against dazed targets.</span>\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "victoryrush";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 62;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 15000;
spellsArray.spellName[t] = "\
							\
Victory Rush\
							"; spellsArray.extra[t] = "\
Requires Battle Stance, Berserker Stance\
							"; spellsArray.description[t] = "\
Instantly attack the target causing 235 damage. Can only be used within 15 sec after you kill an enemy that yields experience or honor. Damage is based on your attack power.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "commandingshout";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 68;
spellsArray.barCost[t] = 10;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Commanding Shout\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Increases total health of all party members within 20 yards by 730. Lasts 2 min.\
							"; t++;



spellsArray.DONTLOCALIZE[t] = "stancemastery";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 20;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Stance Mastery\
							"; spellsArray.extra[t] = "\
Passive\
							"; spellsArray.description[t] = "\
You retain up to 10 of your rage points when you change stances.\
							"; t++;			
							
							
spellsArray.DONTLOCALIZE[t] = "spellreflection";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 25;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 10000;
spellsArray.spellName[t] = "\
							\
Spell Reflection\
							"; spellsArray.extra[t] = "\
Requires Shields<br>\
Requires Battle Stance, Defensive Stance\
							"; spellsArray.description[t] = "\
Raise your shield, reflecting the next spell cast on you. Lasts 5 sec.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "intervene";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 10;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = "8-25";
spellsArray.cooldown[t] = 30000;
spellsArray.spellName[t] = "\
							\
Intervene\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Run at high speed towards a party member, intercepting the next melee or ranged attack made against them.\
							"; t++;							
							
							
spellsArray.DONTLOCALIZE[t] = "shieldbash";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 4;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 10;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 12000;
spellsArray.spellName[t] = "\
							\
Shield Bash\
							"; spellsArray.extra[t] = "\
Requires Shields<br>\
Requires Battle Stance, Defensive Stance\
							"; spellsArray.description[t] = "\
Bashes the target with your shield for 67 damage. <span class = 'newEffect'>It also dazes the target</span> and interrupts spellcasting, preventing any spell in that school from being cast for 6 sec.\
							"; t++;								
							
spellsArray.DONTLOCALIZE[t] = "rampage";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 30;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Rampage\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Warrior goes on a rampage, increasing attack power by 30 and causing most successful melee attacks to increase attack power by an additional 30. This effect will stack up to 5 times. Lasts 30 sec. This ability can only be used after scoring a critical hit.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;&nbsp;Rank 2: +40 Attack Power<br>\
		&nbsp;&nbsp;Rank 3: +50 Attack Power\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "devastate";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 15;
spellsArray.barType[t] = 2;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Devastate\
							"; spellsArray.extra[t] = "\
Requires One-Handed Melee Weapon\
							"; spellsArray.description[t] = "\
		An instant weapon attack that causes 50% of weapon damage plus 15 and additional threat for each application of Sunder Armor on the target. In addition, this attack will renew the duration of the Sunder Armor effect.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;&nbsp;Rank 2: +25 Damage<br>\
		&nbsp;&nbsp;Rank 3: +35 Damage\
							"; t++;
							
	