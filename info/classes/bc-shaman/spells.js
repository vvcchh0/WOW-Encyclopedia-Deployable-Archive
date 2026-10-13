var spellsArray = new spell();spellsArray.spellName = new Array;spellsArray.school = new Array;spellsArray.level = new Array;spellsArray.rank = new Array;spellsArray.description = new Array;spellsArray.DONTLOCALIZE = new Array;spellsArray.range = new Array;spellsArray.barCost = new Array;spellsArray.barType = new Array;spellsArray.extra = new Array;spellsArray.cooldown = new Array;spellsArray.castTime = new Array;var school = new Array();t = 0;

var theClassString = "\
Shaman"; var theClassStringLowerCase = theClassString.toLowerCase(); school[t++] = "\
Elemental\
							"; school[t++] = "\
Enhancement\
							"; school[t++] = "\
Restoration\
							"; school[t++] = "\
New Spells Obtained From Talents\
							";  t = 0;

spellsArray.DONTLOCALIZE[t] = "fireelementaltotem";
spellsArray.school[t] = 0;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 68;
spellsArray.barCost[t] = 680;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 1200000;
spellsArray.spellName[t] = "\
							\
Fire Elemental Totem\
							"; spellsArray.extra[t] = "\
Tools: Fire Totem\
							"; spellsArray.description[t] = "\
Summons an elemental totem that calls forth a greater fire elemental to rain destruction on the caster's enemies. Lasts 2 min.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "wrathofairtotem";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 64;
spellsArray.barCost[t] = 320;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Wrath of Air Totem\
							"; spellsArray.extra[t] = "\
Tools: Air Totem\
							"; spellsArray.description[t] = "\
Summons a Wrath of Air Totem with 5 health at the feet of the caster. Party members within 20 yards of the totem have their magical damage from spells and effects increased by up to 101. Lasts 2 min. \
							"; t++;							

spellsArray.DONTLOCALIZE[t] = "earthelementaltotem";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 66;
spellsArray.barCost[t] = 705;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 1200000;
spellsArray.spellName[t] = "\
							\
Earth Elemental Totem\
							"; spellsArray.extra[t] = "\
Tools: Earth Totem\
							"; spellsArray.description[t] = "\
Summons an elemental totem that calls forth a greater earth elemental to protect the caster and his allies. Lasts 2 min.\
							"; t++;							
							
							
spellsArray.DONTLOCALIZE[t] = "bloodlust";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 750;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 600000;
spellsArray.spellName[t] = "\
							\
Bloodlust\
							"; spellsArray.extra[t] = hordeOnly; spellsArray.description[t] = "\
Increases melee, ranged, and spell casting speed by 35% for all party members. Lasts 1 min.\
							"; t++;

spellsArray.DONTLOCALIZE[t] = "heroism";
spellsArray.school[t] = 1;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 70;
spellsArray.barCost[t] = 750;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 600000;
spellsArray.spellName[t] = "\
							\
Heroism\
							"; spellsArray.extra[t] = allianceOnly; spellsArray.description[t] = "\
Increases melee, ranged, and spell casting speed by 35% for all party members. Lasts 1 min.\
							"; t++;
							

							
spellsArray.DONTLOCALIZE[t] = "watershield";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 62;
spellsArray.barCost[t] = 50;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Water Shield\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
The caster is surrounded by 3 globes of water. When a spell, melee or ranged attack hits the caster, 95 mana is restored to the caster. This expends one water globe. Only one globe will activate every few seconds. Lasts 10 min. Only one Elemental Shield can be active on the Shaman at any one time. \
							"; t++;

spellsArray.DONTLOCALIZE[t] = "watershield";
spellsArray.school[t] = 2;
spellsArray.rank[t] = 2;
spellsArray.level[t] = 69;
spellsArray.barCost[t] = 63;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Water Shield\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
The caster is surrounded by 3 globes of water. When a spell, melee or ranged attack hits the caster, 123 to 124 mana is restored to the caster. This expends one water globe. Only one globe will activate every few seconds. Lasts 10 min. Only one Elemental Shield can be active on the Shaman at any one time. \
							"; t++;
							
spellsArray.DONTLOCALIZE[t] = "totemofwrath";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 166;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Totem of Wrath\
							"; spellsArray.extra[t] = "\
Tools: Fire Totem\
							"; spellsArray.description[t] = "\
Summons a Totem of Wrath with 5 health at the feet of the caster. The totem increases the chance to hit and critically hit with spells by 3% to all party members if they are within 20 yards. Lasts 2 min.\
							"; t++;
							
						
spellsArray.DONTLOCALIZE[t] = "shamanisticrage";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 0;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 0;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 0;
spellsArray.cooldown[t] = 120000;
spellsArray.spellName[t] = "\
							\
Shamanistic Rage\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Gives your successful melee attacks a chance to regenerate mana equal to 15% of your attack power. Lasts 30 sec.\
							"; t++;


spellsArray.DONTLOCALIZE[t] = "earthshield";
spellsArray.school[t] = 3;
spellsArray.rank[t] = 1;
spellsArray.level[t] = 50;
spellsArray.barCost[t] = 600;
spellsArray.barType[t] = 0;
spellsArray.castTime[t] = 0;
spellsArray.range[t] = 40;
spellsArray.cooldown[t] = 0;
spellsArray.spellName[t] = "\
							\
Earth Shield\
							"; spellsArray.extra[t] = ""; spellsArray.description[t] = "\
Protects the target with an earthen shield, giving a 30% chance of ignoring spell interruption when damaged and causing melee attacks to heal the shielded target for 150. This effect can only occur once every few seconds. 10 charges. Lasts 10 min. This shield can only be placed on one target at a time.\
		<br><br>&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 745 Mana, Heals for 205<br>\
		&nbsp;Rank 3: 900 Mana, Heals for 270\
							"; t++;
