var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Hunter"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Beast Mastery\
							"; school[t++] = "\
Marksmanship\
							"; school[t++] = "\
Survival\
							";  school[t++] = "\
New Spells Obtained From Talents\
							"; t = 0;

							
spellsArray.DONTLOCALIZE[t] = "aspectoftheviper";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 40;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Aspect of the Viper\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
The hunter takes on the aspects of a viper, regenerating mana equal to 25% of her intellect every 5 sec. Only one Aspect can be active at a time.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "killcommand";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 62;
spellsArray.barCost[t] = 75;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 40;
spellsArray.cooldown[t] = 5000;
spellsArray.spellName[t] = "\
							\
Kill Command\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Give the command to kill, causing your pet to instantly attack for an additional 127 damage. Can only be used after the Hunter lands a critical strike on the target.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "killcommand";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 90;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 40;
spellsArray.cooldown[t] = 5000;
spellsArray.spellName[t] = "\
							\
Kill Command\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Give the command to kill, causing your pet to instantly attack for an additional 198 damage. Can only be used after the Hunter lands a critical strike on the target.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "steadyshot";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 110;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 1500;
spellsArray.range[t] = "8-35";
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Steady Shot\
							"; spellsArray.extra[t] = "\
Requires Ranged Weapon\
							"; spellsArray.description[t] = "\
A steady shot that causes 100 damage. Causes an additional 175 damage against Dazed targets. 30% of your Ranged Attack Power is added to Steady Shot's damage.\
							"; t++;

							
spellsArray.DONTLOCALIZE[t] = "snaketrap";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 68;
spellsArray.barCost[t] = 305;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 30000;
spellsArray.spellName[t] = "\
							\
Snake Trap\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Place a trap that will release several venomous snakes to attack the first enemy to approach. The snakes will die after 15 sec. Trap will exist for 1 min. Only one trap can be active at a time.\
							"; t++;							
							

spellsArray.DONTLOCALIZE[t] = "misdirection";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 326;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 100;
spellsArray.cooldown[t] = 120000;
spellsArray.spellName[t] = "\
							\
Misdirection\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Threat caused by your next 3 attacks is redirected to the target raid member. Caster and target can only be affected by one Misdirection spell at a time. Effect lasts 30 sec.\
							"; t++;			
				
spellsArray.DONTLOCALIZE[t] = "silencingshot";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 137;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = "8-35";
spellsArray.cooldown[t] = 20000;
spellsArray.spellName[t] = "\
							\
Silencing Shot\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
A shot that deals 75% weapon damage and Silences the target for 3 sec.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "readiness";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = "8-35";
spellsArray.cooldown[t] = 300000;
spellsArray.spellName[t] = "\
							\
Readiness\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
When activated, this ability immediately finishes the cooldown on your other Hunter abilities.\
							"; t++;
							
	