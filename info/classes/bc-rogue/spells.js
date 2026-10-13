var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Rogue"; var theClassStringLowerCase = theClassString.toLowerCase();	school[t++] = "\
Assassination\
							"; school[t++] = "\
Combat\
							"; school[t++] = "\
Poisons\
							"; school[t++] = "\
New Spells Obtained From Talents\
							"; t = 0;

spellsArray.DONTLOCALIZE[t] = "deadlythrow";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 35;
spellsArray.barType[t] = 1;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = "8-30";
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Deadly Throw\
							"; spellsArray.extra[t] = "\
Requires Thrown\
							"; spellsArray.description[t] = "\
Finishing move that reduces the movement of the target by 50% for 5 sec and causes thrown weapon damage plus additional damage per combo point:<br>\
&nbsp;&nbsp;1 point : 132-228 damage<br>\
&nbsp;&nbsp;2 points: 216-312 damage<br>\
&nbsp;&nbsp;3 points: 300-396 damage<br>\
&nbsp;&nbsp;4 points: 384-480 damage<br>\
&nbsp;&nbsp;5 points: 468-564 damage\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "envenom";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 62;
spellsArray.barCost[t] = 35;
spellsArray.barType[t] = 1;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Envenom\
							"; spellsArray.extra[t] = "\
Requires Melee Weapon\
							"; spellsArray.description[t] = "\
Finishing move that consumes your Deadly Poison doses on the target and deals instant poison damage. One dose is consumed for each combo point.<br>\
&nbsp;&nbsp;1 dose: 168 damage<br>\
&nbsp;&nbsp;2 doses: 335 damage<br>\
&nbsp;&nbsp;3 doses: 503 damage<br>\
&nbsp;&nbsp;4 doses: 670 damage<br>\
&nbsp;&nbsp;5 doses: 838 damage\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "envenom";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 69;
spellsArray.barCost[t] = 35;
spellsArray.barType[t] = 1;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Envenom\
							"; spellsArray.extra[t] = "\
Requires Melee Weapon\
							"; spellsArray.description[t] = "\
Finishing move that consumes your Deadly Poison doses on the target and deals instant poison damage. One dose is consumed for each combo point.<br>\
&nbsp;&nbsp;1 dose: 204 damage<br>\
&nbsp;&nbsp;2 doses: 407 damage<br>\
&nbsp;&nbsp;3 doses: 611 damage<br>\
&nbsp;&nbsp;4 doses: 814 damage<br>\
&nbsp;&nbsp;5 doses: 1018 damage\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "garrote";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 6;
spellsArray.level[t] = 61;
spellsArray.barCost[t] = 50;
spellsArray.barType[t] = 1;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Garrote\
							"; spellsArray.extra[t] = "\
Requires Stealth\
							"; spellsArray.description[t] = "\
Garrote the enemy, <span class = 'newEffect'>Silencing them for 3 seconds</span> and causing 666 damage over 18 sec, increased by Attack Power. Must be stealthed and behind the target. Awards 1 combo point.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "garrote";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 7;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 50;
spellsArray.barType[t] = 1;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Garrote\
							"; spellsArray.extra[t] = "\
Requires Stealth\
							"; spellsArray.description[t] = "\
Garrote the enemy, <span class = 'newEffect'>Silencing them for 3 seconds</span> and causing 978 damage over 18 sec, increased by Attack Power. Must be stealthed and behind the target. Awards 1 combo point.\
							"; t++;

							
spellsArray.DONTLOCALIZE[t] = "shiv";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = "33 - 49";
spellsArray.barType[t] = 1;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Shiv\
							"; spellsArray.extra[t] = "\
Requires Melee Weapon\
							"; spellsArray.description[t] = "\
Performs an instant off-hand weapon attack that automatically applies the poison from your off-hand weapon to the target. Slower weapons require more Energy. Awards 1 combo point.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "evasion";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 300000;
spellsArray.spellName[t] = "\
							\
Evasion\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Increases the rogue's dodge chance by 50% <span class = 'newEffect'>and reduces the chance ranged attacks hit the rogue by 25%.</span> Lasts 15 sec.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "anestheticpoison";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 68;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Anesthetic Poison\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Coats a weapon with poison that lasts for 30 minutes. Each strike has a 20% chance of reducing threat by a moderate amount. 120 charges.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "mutilate";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 60;
spellsArray.barType[t] = 1;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Mutilate\
							"; spellsArray.extra[t] = "\
Requires Daggers\
							"; spellsArray.description[t] = "\
Instantly attacks with both weapons for an additional 44 with each weapon. Damage is increased by 50% against Poisoned targets. Must be behind the target. Awards 2 combo points.<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 63 with each weapon<br>\
			&nbsp;Rank 3: 88 with each weapon<br>\
			&nbsp;Rank 4: 101 with each weapon\
							"; t++;
							
																	
spellsArray.DONTLOCALIZE[t] = "cloakofshadows";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 120000;
spellsArray.spellName[t] = "\
							\
Cloak of Shadows\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Instantly removes all existing harmful spell effects and increases your chance to resist all spells by 90% for 5 sec.\
							"; t++;
							
