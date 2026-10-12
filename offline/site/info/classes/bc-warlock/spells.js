var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Warlock"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Affliction\
							"; school[t++] = "\
Demonology\
							"; school[t++] = "\
Destruction\
							"; school[t++] = "\
New Spells Obtained From Talents\
							"; school[t++] = "\
Felguard\
							";  t = 0;

spellsArray.DONTLOCALIZE[t] = "seedofcorruption";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 882;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 2000;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Seed of Corruption\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Imbeds a demon seed in the enemy target, causing 1044 Shadow damage over 18 sec. When the target takes 1044 total damage, the seed will inflict 1110 to 1290 Shadow damage to all enemies within 15 yards of the target. Only one Corruption spell per Warlock can be active on any one target.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "createspellstone";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 36;
spellsArray.barCost[t] = 1150;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 5000;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Create Spellstone\
							"; spellsArray.extra[t] = "\
Reagents: Soul Shard\
							"; spellsArray.description[t] = "\
Creates a Spellstone for the caster. When equipped and used, the Master Spellstone removes all harmful magic effects from the caster. In addition, equipping the Spellstone improves your spell critical rating by 8.<br><br>Conjured items disappear if logged out for more than 15 minutes.<br><br><span style = 'color: 8d0202'>Other Spellstone Changes:<br>&nbsp;Equipped in the wand slot<br>&nbsp;Not consumed when used<br>&nbsp;Has 3 minute cooldown</span>\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "createspellstone";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 4;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 1150;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 5000;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Create Spellstone (Master)\
							"; spellsArray.extra[t] = "\
Reagents: Soul Shard\
							"; spellsArray.description[t] = "\
Creates a Master Spellstone for the caster. When equipped and used, the Master Spellstone removes all harmful magic effects from the caster. In addition, equipping the Spellstone improves your spell critical rating by 20.<br><br>Conjured items disappear if logged out for more than 15 minutes.<br><br><span style = 'color: 8d0202'>Other Spellstone Changes:<br>&nbsp;Equipped in the wand slot<br>&nbsp;Not consumed when used<br>&nbsp;Has 3 minute cooldown</span>\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "felarmor";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 62;
spellsArray.barCost[t] = 637;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Fel Armor\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Surrounds the caster with fel energy, increasing the amount of health generated through spells and effects by 20% and increasing spell damage by up to 50. Only one type of Armor spell can be active on the Warlock at any time. Lasts 30 min.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "felarmor";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 69;
spellsArray.barCost[t] = 725;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Fel Armor\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Surrounds the caster with fel energy, increasing the amount of health generated through spells and effects by 20% and increasing spell damage by up to 100. Only one type of Armor spell can be active on the Warlock at any time. Lasts 30 min.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "ritualofsouls";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 2623;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 3000;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 300000;
spellsArray.spellName[t] = "\
							\
Ritual of Souls\
							"; spellsArray.extra[t] = "\
Reagents: Soul Shard\
							"; spellsArray.description[t] = "\
Begins a ritual that creates a Soulwell. Raid members can click the Soulwell to acquire a Master Healthstone. The Soulwell lasts for 5 min or 10 charges. Requires the caster and 2 additional party members to complete the ritual. In order to participate, all players must be out of combat and right-click the soul portal and not move until the ritual is complete.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "soulshatter";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 253;
spellsArray.barType[t] = 3;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 300000;
spellsArray.spellName[t] = "\
							\
Soulshatter\
							"; spellsArray.extra[t] = "\
Reagents: Soul Shard\
							"; spellsArray.description[t] = "\
Reduces threat by 50% for all enemies within 50 yards.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "incinerate";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 256;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 2500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Incinerate\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Deals 357 to 413 Fire damage to your target and an additional 89 to 104 Fire damage if the target is affected by an Immolate spell.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "incinerate";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 300;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 2500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Incinerate\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Deals 429 to 497 Fire damage to your target and an additional 107 to 125 Fire damage if the target is affected by an Immolate spell.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "unstableaffliction";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 270;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 1500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Unstable Affliction\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Shadow energy slowly destroys the target, causing 660 damage over 18 sec. In addition, if the Unstable Affliction is dispelled it will cause 990 damage to the dispeller and silence them for 5 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 315 Mana, 930 DoT, 1395 damage to dispeller<br>\
		&nbsp;Rank 3: 400 Mana, 1050 DoT, 1575 damage to dispeller\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "summonfelguard";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 1538;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 10000;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Summon Felguard\
							"; spellsArray.extra[t] = "\
Reagents: Soul Shard\
							"; spellsArray.description[t] = "\
Summons a Felguard under the command of the Warlock.\
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "shadowfury";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 440;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 500;
spellsArray.range[t] = 30;
spellsArray.cooldown[t] = 60000;
spellsArray.spellName[t] = "\
							\
Shadowfury\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Shadowfury is unleashed, causing 343 to 407 Shadow damage and stunning all enemies within 8 yds for 2 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 545 Mana, 459-547 Damage<br>\
		&nbsp;Rank 3: 710 Mana, 612-728 Damage<br>\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "demonicfrenzy";
spellsArray.school[t] = 4;
spellsArray.rank[t] = -1;
spellsArray.level[t] = 56;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Demonic Frenzy\
							"; spellsArray.extra[t] = "\
Passive\
							"; spellsArray.description[t] = "\
The Felguard's damaging melee attacks cause a demonic frenzy, increasing attack power by 5% for 10 sec. This effect can stack up to 10 times.\
							"; t++;							
							
spellsArray.DONTLOCALIZE[t] = "avoidance";
spellsArray.school[t] = 4;
spellsArray.rank[t] = -1;
spellsArray.level[t] = 60;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = -1;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Avoidance\
							"; spellsArray.extra[t] = "\
Passive\
							"; spellsArray.description[t] = "\
Increases your chance to avoid area of effect attacks by an additional 50%.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "anguish";
spellsArray.school[t] = 4;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 90;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 5000;
spellsArray.spellName[t] = "\
							\
Anguish\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Taunts the creature, increasing the chance that it will attack the Felguard.\
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "cleave";
spellsArray.school[t] = 4;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 295;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 5;
spellsArray.cooldown[t] = 6000;
spellsArray.spellName[t] = "\
							\
Cleave\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
A sweeping attack that does your weapon damage plus 32 to the target and his nearest ally.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 295 Mana, plus 50 damage<br>\
		&nbsp;Rank 3: 295 Mana, plus 78 damage\
							"; t++;								
							
spellsArray.DONTLOCALIZE[t] = "intercept";
spellsArray.school[t] = 4;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 52;
spellsArray.barCost[t] = 145;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = "8-25";
spellsArray.cooldown[t] = 30000;
spellsArray.spellName[t] = "\
							\
Intercept\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Charge an enemy, causing 65 damage and stunning it for 3 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 160 Mana, 85 damage<br>\
		&nbsp;Rank 3: 195 Mana, 105 damage\
							"; t++;	