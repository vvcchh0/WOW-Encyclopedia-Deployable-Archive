var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Paladin"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Holy\
							"; school[t++] = "\
Protection\
							"; school[t++] = "\
Retribution\
							"; school[t++] = "\
New Spells Obtained From Talents\
							";  t = 0;

spellsArray.DONTLOCALIZE[t] = "consecration";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 20;
spellsArray.barCost[t] = 120;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 8000;
spellsArray.spellName[t] = "\
							\
Consecration\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Consecrates the land beneath Paladin, doing 64 Holy damage over 8 sec to enemies who enter the area.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "consecration";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 6;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 670;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 8000;
spellsArray.spellName[t] = "\
							\
Consecration\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Consecrates the land beneath Paladin, doing 592 Holy damage over 8 sec to enemies who enter the area.\
							"; t++;
							


spellsArray.DONTLOCALIZE[t] = "righteousdefense";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 14;
spellsArray.barCost[t] = 138;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 40;
spellsArray.cooldown[t] = 15000;
spellsArray.spellName[t] = "\
							\
Righteous Defense\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Come to the defense of a friendly target, commanding up to 3 enemies attacking the target to attack the Paladin instead.\
							"; t++;							
					
spellsArray.DONTLOCALIZE[t] = "spiritualattunement";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 18;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Spiritual Attunement\
							"; spellsArray.extra[t] = "\
							"; spellsArray.description[t] = "\
A passive ability that gives the Paladin mana when healed by other friendly targets. The amount of mana gained is equal to 8% of the amount healed. \
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "spiritualattunement";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Spiritual Attunement\
							"; spellsArray.extra[t] = "\
							"; spellsArray.description[t] = "\
A passive ability that gives the Paladin mana when healed by other friendly targets. The amount of mana gained is equal to 10% of the amount healed. \
							"; t++;
							
							
spellsArray.DONTLOCALIZE[t] = "sealofjustice";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 48;
spellsArray.barCost[t] = 225;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Seal of Justice\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Fills the Paladin with the spirit of justice for 30 sec, giving each melee attack a chance to stun for 2 sec. Only one Seal can be active on the Paladin at any one time.<br><br>\
Unleashing this Seal's energy will judge an enemy for 10 sec, preventing them from fleeing <span class = 'newEffect'>and limiting their movement speed</span>. Your melee strikes will refresh the spell's duration. Only one Judgement per Paladin can be active at any one time.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "crusaderaura";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Crusader Aura\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Increases the mounted speed by 20% for all party members within 30 yards. Players may only have one Aura on them per Paladin at any one time.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "sealofblood";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 210;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Seal of Blood\
							"; spellsArray.extra[t] = hordeOnly; spellsArray.description[t] = "\
All melee attacks deal additional Holy damage equal to 40% normal weapon damage, but the Paladin loses health equal to 10% of the total damage inflicted.<br><br>\
Unleashing this Seal's energy will judge an enemy, instantly causing 445 to 488 Holy damage at the cost of 148 to 163 health.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "sealofvengeance";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 250;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Seal of Vengeance\
							"; spellsArray.extra[t] = allianceOnly; spellsArray.description[t] = "\
Fills the Paladin with holy power, granting each melee attack a chance to cause 80 Holy damage over 12 sec. This effect can stack up to 5 times. Only one Seal can be active on the Paladin at any one time. Lasts 30 sec.<br><br>\
Unleashing this Seal's energy will judge an enemy, instantly causing 86 Holy damage per application of Holy Vengeance.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "avengingwrath";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 180000;
spellsArray.spellName[t] = "\
							\
Avenging Wrath\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Increases all damage caused by 30% for 20 sec. Causes Forebearance.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "crusaderstrike";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 276;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 10000;
spellsArray.spellName[t] = "\
							\
Crusader Strike\
							"; spellsArray.extra[t] = "\
Requires Melee Weapon\
							"; spellsArray.description[t] = "\
An instant strike that causes weapon damage plus 40% of your Holy spell damage and refreshes all Judgements on the target.\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "avengersshield";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 500;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 1000;
spellsArray.range[t] = "8-30";
spellsArray.cooldown[t] = 30000;
spellsArray.spellName[t] = "\
							\
Avenger's Shield\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Hurls a holy shield at the enemy, dealing 270 to 330 Holy damage, dazing them and then jumping to nearby enemies. Affects 3 total targets. Lasts 3 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 615 Mana, 370-452 Holy Damage<br>\
		&nbsp;Rank 3: 825 Mana, 581-709 Holy Damage\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "divineillumination";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 180000;
spellsArray.spellName[t] = "\
							\
Divine Illumination\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Reduces the mana cost of all spells by 50% for 10 sec.\
							"; t++;							
							

