var i = 0;
var t = 0;

var className = "Mage Talents";
var talentPath = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fglobal%2Ftalents%2Fmage%2Fdata.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ftalents%2F&reason=external-or-uncollected-resource";

tree[i] = "Arcane"; i++;
tree[i] = "Fire"; i++;
tree[i] = "Frost"; i++;

i = 0;

talent[i] = [0, "Arcane Subtlety", 2, 1, 1]; i++;
talent[i] = [0, "Arcane Focus", 5, 2, 1]; i++;
talent[i] = [0, "Improved Arcane Missiles", 5, 3, 1]; i++;
talent[i] = [0, "Wand Specialization", 2, 1, 2]; i++; 
talent[i] = [0, "Magic Absorption", 5, 2, 2]; i++;
talent[i] = [0, "Arcane Concentration", 5, 3, 2]; i++;
talent[i] = [0, "Magic Attunement", 2, 1, 3]; i++;
talent[i] = [0, "Arcane Impact", 3, 2, 3]; i++;
talent[i] = [0, "Arcane Fortitude", 1, 4, 3]; i++;
talent[i] = [0, "Improved Mana Shield", 2, 1, 4]; i++;
talent[i] = [0, "Improved Counterspell", 2, 2, 4]; i++;
talent[i] = [0, "Arcane Meditation", 3, 4, 4]; i++;
talent[i] = [0, "Improved Blink", 2, 1, 5]; i++;
talent[i] = [0, "Presence of Mind", 1, 2, 5]; i++;
talent[i] = [0, "Arcane Mind", 5, 4, 5]; i++;
talent[i] = [0, "Prismatic Cloak", 2, 1, 6]; i++;
talent[i] = [0, "Arcane Instability", 3, 2, 6, [getTalentID("Presence of Mind"),1]]; i++;
talent[i] = [0, "Arcane Potency", 3, 3, 6, [getTalentID("Arcane Concentration"),5]]; i++;
talent[i] = [0, "Empowered Arcane Missiles", 3, 1, 7]; i++;
talent[i] = [0, "Arcane Power", 1, 2, 7, [getTalentID("Arcane Instability"),3]]; i++;
talent[i] = [0, "Spell Power", 2, 3, 7]; i++;
talent[i] = [0, "Mind Mastery", 5, 2, 8]; i++;
talent[i] = [0, "Slow", 1, 2, 9]; i++;
treeStartStop[t] = i -1;
t++;

//fire talents
talent[i] = [1, "Improved Fireball", 5, 2, 1]; i++;
talent[i] = [1, "Impact", 5, 3, 1]; i++;
talent[i] = [1, "Ignite", 5, 1, 2]; i++;
talent[i] = [1, "Flame Throwing", 2, 2, 2]; i++;
talent[i] = [1, "Improved Fire Blast", 3, 3, 2]; i++;
talent[i] = [1, "Incinerate", 2, 1, 3]; i++;
talent[i] = [1, "Improved Flamestrike", 3, 2, 3]; i++;
talent[i] = [1, "Pyroblast", 1, 3, 3]; i++;
talent[i] = [1, "Burning Soul", 2, 4, 3]; i++;
talent[i] = [1, "Improved Scorch", 3, 1, 4]; i++;
talent[i] = [1, "Molten Shields", 2, 2, 4]; i++;
talent[i] = [1, "Master of Elements", 3, 4, 4]; i++;
talent[i] = [1, "Playing with Fire", 3, 1, 5]; i++;
talent[i] = [1, "Critical Mass", 3, 2, 5]; i++;
talent[i] = [1, "Blast Wave", 1, 3, 5, [getTalentID("Pyroblast"),1]]; i++;
talent[i] = [1, "Blazing Speed", 2, 1, 6]; i++;
talent[i] = [1, "Fire Power", 5, 3, 6]; i++;
talent[i] = [1, "Pyromaniac", 3, 1, 7]; i++;
talent[i] = [1, "Combustion", 1, 2, 7, [getTalentID("Critical Mass"),3]]; i++;
talent[i] = [1, "Molten Fury", 2, 3, 7]; i++;
talent[i] = [1, "Empowered Fireball", 5, 3, 8]; i++;
talent[i] = [1, "Dragon's Breath", 1, 2, 9, [getTalentID("Combustion"),1]]; i++;

treeStartStop[t] = i -1;
t++;

//frost talents
talent[i] = [2, "Frost Warding", 2, 1, 1]; i++;
talent[i] = [2, "Improved Frostbolt", 5, 2, 1]; i++;
talent[i] = [2, "Elemental Precision", 3, 3, 1]; i++;
talent[i] = [2, "Ice Shards", 5, 1, 2]; i++;
talent[i] = [2, "Frostbite", 3, 2, 2]; i++;
talent[i] = [2, "Improved Frost Nova", 2, 3, 2]; i++;
talent[i] = [2, "Permafrost", 3, 4, 2]; i++;
talent[i] = [2, "Piercing Ice", 3, 1, 3]; i++;
talent[i] = [2, "Icy Veins", 1, 2, 3]; i++;
talent[i] = [2, "Improved Blizzard", 3, 4, 3]; i++;
talent[i] = [2, "Arctic Reach", 2, 1, 4]; i++;
talent[i] = [2, "Frost Channeling", 3, 2, 4]; i++;
talent[i] = [2, "Shatter", 5, 3, 4, [getTalentID("Improved Frost Nova"),2]]; i++;
talent[i] = [2, "Frozen Core", 3, 1, 5]; i++;
talent[i] = [2, "Cold Snap", 1, 2, 5]; i++;
talent[i] = [2, "Improved Cone of Cold", 3, 3, 5]; i++;
talent[i] = [2, "Ice Floes", 2, 1, 6]; i++;
talent[i] = [2, "Winter's Chill", 5, 3, 6]; i++;
talent[i] = [2, "Ice Barrier", 1, 2, 7, [getTalentID("Cold Snap"),1]]; i++;
talent[i] = [2, "Arctic Winds", 5, 3, 7]; i++;
talent[i] = [2, "Empowered Frostbolt", 5, 2, 8]; i++;
talent[i] = [2, "Summon Water Elemental", 1, 2, 9]; i++;

treeStartStop[t] = i -1;
t++;

i = 0;

//Arcane Talents Begin

//Arcane Subtlety - Arcane
rank[i] = [
		"Reduces your target's resistance to all your spells by 5 and reduces threat of Arcane spells by 20%.",
		"Reduces your target's resistance to all your spells by 10 and reduces threat of Arcane spells by 40%."
		];
i++;		
		
//Arcane Focus - Arcane
rank[i] = [
		"Reduces the chance that the opponent can resist your Arcane spells by 2%.",
		"Reduces the chance that the opponent can resist your Arcane spells by 4%.",
		"Reduces the chance that the opponent can resist your Arcane spells by 6%.",
		"Reduces the chance that the opponent can resist your Arcane spells by 8%.",
		"Reduces the chance that the opponent can resist your Arcane spells by 10%."
		];
i++;		

//Improved Arcane Missiles - Arcane
rank[i] = [
		"Gives you a 20% chance to avoid interruption caused by damage while channeling Arcane Missiles.",
		"Gives you a 40% chance to avoid interruption caused by damage while channeling Arcane Missiles.",
		"Gives you a 60% chance to avoid interruption caused by damage while channeling Arcane Missiles.",
		"Gives you a 80% chance to avoid interruption caused by damage while channeling Arcane Missiles.",
		"Gives you a 100% chance to avoid interruption caused by damage while channeling Arcane Missiles."
		];
i++;		
		
//Wand Specialization - Arcane	
rank[i] = [
		"Increases your damage with Wands by 13%.",
		"Increases your damage with Wands by 25%."
		];
i++;		

//Magic Absorption
rank[i] = [
		"Increases all resistances by 2 and causes all spells you fully resist to restore 1% of your total mana.  1 sec. cooldown.",
		"Increases all resistances by 4 and causes all spells you fully resist to restore 2% of your total mana.  1 sec. cooldown.",
		"Increases all resistances by 6 and causes all spells you fully resist to restore 3% of your total mana.  1 sec. cooldown.",
		"Increases all resistances by 8 and causes all spells you fully resist to restore 4% of your total mana.  1 sec. cooldown.",
		"Increases all resistances by 10 and causes all spells you fully resist to restore 5% of your total mana.  1 sec. cooldown."
		];
i++;		

//Arcane Concentration - Arcane	
rank[i] = [
	"Gives you a 2% chance of entering a Clearcasting state after any damage spell hits a target. The Clearcasting state reduces the mana cost of your next damage	spell by 100%.",
	"Gives you a 4% chance of entering a Clearcasting state after any damage spell hits a target. The Clearcasting state reduces the mana cost of your next damage spell by 100%.",
	"Gives you a 6% chance of entering a Clearcasting state after any damage spell hits a target. The Clearcasting state reduces the mana cost of your next damage spell by 100%.",
	"Gives you a 8% chance of entering a Clearcasting state after any damage spell hits a target. The Clearcasting state reduces the mana cost of your next damage spell by 100%.",
	"Gives you a 10% chance of entering a Clearcasting state after any damage spell hits a target. The Clearcasting state reduces the mana cost of your next damage spell by 100%."
		];
i++;		

//Improved Dampen Magic - Arcane
rank[i] = [
		"Increases the effect of your Amplify Magic and Dampen Magic spells by 25%.",
		"Increases the effect of your Amplify Magic and Dampen Magic spells by 50%."
		];
i++;		
		
//Arcane Impact - Arcane	
rank[i] = [
		"Increases the critical strike chance of your Arcane Explosion and Arcane Blast spells by an additional 2%.",
		"Increases the critical strike chance of your Arcane Explosion and Arcane Blast spells by an additional 4%.",
		"Increases the critical strike chance of your Arcane Explosion and Arcane Blast spells by an additional 6%."
		];		
i++;		

//Arcane Fortitude - Arcane		
rank[i] = [ 
		"Increases your armor by an amount equal to 100% of your Intellect."
		];
i++;	

//Improved Mana Shield - Arcane		
rank[i] = [
		"Decreases the mana lost per point of damage taken when Mana Shield is active by 10%.",
		"Decreases the mana lost per point of damage taken when Mana Shield is active by 20%."
		];
i++;		

//Improved Counterspell - Arcane	
rank[i] = [
		"Gives your Counterspell a 50% chance to silence the target for 4 sec.",
		"Gives your Counterspell a 100% chance to silence the target for 4 sec."
		];
i++;		

//Arcane Meditation - Arcane		
rank[i] = [
		"Allows 10% of your Mana regeneration to continue while casting.",
		"Allows 20% of your Mana regeneration to continue while casting.",
		"Allows 30% of your Mana regeneration to continue while casting."
		];
i++;	

//Improved Blink - Arcane	
rank[i] = [
		"For 2 sec after casting Blink, your chance to be hit by all attacks and spells is reduced by 25%.",
		"For 4 sec after casting Blink, your chance to be hit by all attacks and spells is reduced by 25%."
		];
i++;

//Presence of Mind - Arcane
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, your next Mage spell with a casting time less than 10 sec becomes an instant cast spell."
		];
i++;		

//Arcane Mind - Arcane		
rank[i] = [
		"Increases your total Intellect by 3%.",
		"Increases your total Intellect by 6%.",
		"Increases your total Intellect by 9%.",
		"Increases your total Intellect by 12%.",
		"Increases your total Intellect by 15%."
		];
i++;

//Prismatic Cloak - Arcane
rank[i]=[
"Reduces all damage taken by 2%.",
"Reduces all damage taken by 4%."
		];
i++;

//Arcane Instability - Arcane		
rank[i] = [
		"Increases your spell damage and critical strike chance by 1%.",
		"Increases your spell damage and critical strike chance by 2%.",
		"Increases your spell damage and critical strike chance by 3%."
		];		
i++;

//Arcane Potency - Arcane		
rank[i] = [
		"Increases the critical strike chance of any spell cast while Clearcasting by 10%.",
		"Increases the critical strike chance of any spell cast while Clearcasting by 20%.",
		"Increases the critical strike chance of any spell cast while Clearcasting by 30%."
		];		
i++;

//Empowered Arcane Missiles - Arcane
rank[i]=[
"Your Arcane Missiles spell gains an additional 15% of your bonus spell damage effects, but mana cost is increased by 2%.",
"Your Arcane Missiles spell gains an additional 30% of your bonus spell damage effects, but mana cost is increased by 4%.",
"Your Arcane Missiles spell gains an additional 45% of your bonus spell damage effects, but mana cost is increased by 6%."
		];
i++;

//Arcane Power - Arcane				
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, your spells deal 30% more damage while costing 30% more mana to cast. This effect lasts 15 sec."
		];
i++;		

//Spell Power - Arcane //New/Changed
rank[i]=[
"Increases critical strike damage bonus of all spells by 25%.",
"Increases critical strike damage bonus of all spells by 50%."
		];
i++;

//Mind Mastery - Arcane
rank[i]=[
"Increases spell damage by up to 5% of your total intellect.",
"Increases spell damage by up to 10% of your total intellect.",
"Increases spell damage by up to 15% of your total intellect.",
"Increases spell damage by up to 20% of your total intellect.",
"Increases spell damage by up to 25% of your total intellect."
		];
i++;


//Slow - Arcane				
rank[i] = [
		"<span style=text-align:left;float:left;>627 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><BR>Reduces target's movement speed by 50%, increases the time between ranged attacks by 50% and increases casting time by 50%. Lasts 15 sec. Slow can only affect one target at a time."
		];
i++;


//Improved Fireball - Fire	
rank[i] = [
			"Reduces the casting time of your Fireball spell by 0.1 sec.",
			"Reduces the casting time of your Fireball spell by 0.2 sec.",
			"Reduces the casting time of your Fireball spell by 0.3 sec.",
			"Reduces the casting time of your Fireball spell by 0.4 sec.",
			"Reduces the casting time of your Fireball spell by 0.5 sec."
		];
i++;



//Impact - Fire			
rank[i] = [
			"Gives your Fire spells a 2% chance to stun the target for 2 sec.",
			"Gives your Fire spells a 4% chance to stun the target for 2 sec.",
			"Gives your Fire spells a 6% chance to stun the target for 2 sec.",
			"Gives your Fire spells a 8% chance to stun the target for 2 sec.",
			"Gives your Fire spells a 10% chance to stun the target for 2 sec."
		];
i++;

//Ignite - Fire		
rank[i] = [
			"Your critical strikes from Fire damage spells cause the target to burn for an additional 8% of your spell's damage over 4 sec.",
			"Your critical strikes from Fire damage spells cause the target to burn for an additional 16% of your spell's damage over 4 sec.",
			"Your critical strikes from Fire damage spells cause the target to burn for an additional 24% of your spell's damage over 4 sec.",
			"Your critical strikes from Fire damage spells cause the target to burn for an additional 32% of your spell's damage over 4 sec.",
			"Your critical strikes from Fire damage spells cause the target to burn for an additional 40% of your spell's damage over 4 sec."
		];		
i++;		

//Flame Throwing - Fire	
rank[i] = [
			"Increases the range of your fire spells by 3 yards.",
			"Increases the range of your fire spells by 6 yards."
		];
i++;

//Improved Fire Blast - Fire	
rank[i] = [
			"Reduces the cooldown of your Fire Blast spell by 0.5 sec.",
			"Reduces the cooldown of your Fire Blast spell by 1 sec.",
			"Reduces the cooldown of your Fire Blast spell by 1.5 sec."
		];
i++;		


//Incinerate - Fire			
rank[i] = [
			"Increases the critical strike chance of your Fire Blast and Scorch spells by 2%.",
			"Increases the critical strike chance of your Fire Blast and Scorch spells by 4%."
		];
i++;		

//Improved Flamestrike - Fire		
rank[i] = [
			"Increases the critical strike chance of your Flamestrike spell by 5%.",
			"Increases the critical strike chance of your Flamestrike spell by 10%.",
			"Increases the critical strike chance of your Flamestrike spell by 15%."
		];
i++;		

//Pyroblast - Fire	
rank[i] = [
		"<span style=text-align:left;float:left;>125 Mana</span><span style=text-align:right;float:right;>35 yd range</span><br><span style=text-align:left;float:left;>6 sec cast</span><br>Hurls an immense fiery boulder that causes 148 to 195 Fire damage and an additional 56 Fire damage over 12 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 150 Mana, 193-250 Damage, 72/12 sec<br>\
		&nbsp;Rank 3: 195 Mana, 270-343 Damage, 96/12 sec<br>\
		&nbsp;Rank 4: 240 Mana, 347-437 Damage, 124/12 sec<br>\
		&nbsp;Rank 5: 285 Mana, 427-536 Damage, 156/12 sec<br>\
		&nbsp;Rank 6: 335 Mana, 525-654 Damage, 188/12 sec<br>\
		&nbsp;Rank 7: 385 Mana, 625-776 Damage, 228/12 sec<br>\
		&nbsp;Rank 8: 440 Mana, 743-918 Damage, 268/12 sec<br>\
		&nbsp;Rank 9: 460 Mana, 877-1087 Damage, 324/12 sec"
		];		
i++;		



//Burning Soul - Fire
rank[i] = [
			"Gives your Fire spells a 35% chance to not lose casting time when you take damage and reduces the threat caused by your Fire spells by 5%.",
			"Gives your Fire spells a 70% chance to not lose casting time when you take damage and reduces the threat caused by your Fire spells by 10%."
		];
i++;		

//Improved Scorch - Fire	
rank[i] = [
			"Your Scorch spells have a 33% chance to cause your target to be vulnerable to Fire damage. This vulnerability increases the Fire damage dealt to your target by 3% and lasts 30 sec.  Stacks up to 5 times.",
			"Your Scorch spells have a 66% chance to cause your target to be vulnerable to Fire damage. This vulnerability increases the Fire damage dealt to your target by 3% and lasts 30 sec.  Stacks up to 5 times.",
			"Your Scorch spells have a 100% chance to cause your target to be vulnerable to Fire damage. This vulnerability increases the Fire damage dealt to your target by 3% and lasts 30 sec.  Stacks up to 5 times."
		];
i++;		

//Improved MOLTEN SHIELDS - Fire	
rank[i] = [
			"Causes your Fire Ward to have a 10% chance to reflect Fire spells while active. In addition, your Molten Armor has a 50% chance to affect ranged and spell attacks.",
			"Causes your Fire Ward to have a 20% chance to reflect Fire spells while active. In addition, your Molten Armor has a 100% chance to affect ranged and spell attacks."
		];
i++;		

//Master of Elements - Fire	
rank[i] = [
			"Your Fire and Frost spell criticals will refund 10% of their base mana cost.",
			"Your Fire and Frost spell criticals will refund 20% of their base mana cost.",
			"Your Fire and Frost spell criticals will refund 30% of their base mana cost."
		]; i++;

//Playing with Fire - Fire	
rank[i] = [
			"Increases all spell damage caused by 1% and all spell damage taken by 1%.",
			"Increases all spell damage caused by 2% and all spell damage taken by 2%.",
			"Increases all spell damage caused by 3% and all spell damage taken by 3%."
		]; i++;

//Critical Mass - Fire	
rank[i] = [
			"Increases the critical strike chance of your fire spells by 2%.",
			"Increases the critical strike chance of your fire spells by 4%.",
			"Increases the critical strike chance of your fire spells by 6%."
		];i++;		

//Blast Wave - Fire	
rank[i] = [
			"215 Mana<br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>30 sec cooldown</span><br>A wave of flame radiates outward from the caster, damaging all enemies caught within the blast for 160 to 192 Fire damage, and dazing them for 6 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 270 Mana, 201-241 Damage<br>\
		&nbsp;Rank 3: 355 Mana, 277-329 Damage<br>\
		&nbsp;Rank 4: 450 Mana, 365-433 Damage<br>\
		&nbsp;Rank 5: 545 Mana, 462-544 Damage<br>\
		&nbsp;Rank 6: 595 Mana, 640-754 Damage"
		]; i++;		

//Blazing Speed - Fire	
rank[i] = [
			"Gives you a 5% chance when hit by a melee or ranged attack to increase your movement speed by 50% and dispel all movement impairing effects. This effect lasts 8 sec.",
			"Gives you a 10% chance when hit by a melee or ranged attack to increase your movement speed by 50% and dispel all movement impairing effects. This effect lasts 8 sec."
		]; i++;

//Fire Power - Fire	
rank[i] = [
			"Increases the damage done by your fire spells by 2%.",
			"Increases the damage done by your fire spells by 4%.",
			"Increases the damage done by your fire spells by 6%.",
			"Increases the damage done by your fire spells by 8%.",
			"Increases the damage done by your fire spells by 10%."		
		]; i++;

//Pyromaniac - Fire	
rank[i] = [
			"Increases chance to critically hit and reduces the mana cost of all Fire spells by an additional 1%.",
			"Increases chance to critically hit and reduces the mana cost of all Fire spells by an additional 2%.",
			"Increases chance to critically hit and reduces the mana cost of all Fire spells by an additional 3%."			
		]; 
i++;
		
//Combustion - Fire
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, this spell causes each of your Fire damage spell hits to increase your critical strike chance with Fire damage spells by 10%. This effect lasts until you have caused 3 critical strikes with Fire spells."
		];
i++;
		
//Molten Fury - Fire	
rank[i] = [
			"Increases damage of all spells against targets with less than 20% health by 10%.",
			"Increases damage of all spells against targets with less than 20% health by 20%."
		]; 
i++;

//Empowered Fireball - Fire	
rank[i] = [
			"Your Fireball spell gains an additional 3% of your bonus spell damage effects.",
			"Your Fireball spell gains an additional 6% of your bonus spell damage effects.",
			"Your Fireball spell gains an additional 9% of your bonus spell damage effects.",
			"Your Fireball spell gains an additional 12% of your bonus spell damage effects.",
			"Your Fireball spell gains an additional 15% of your bonus spell damage effects."
		]; 
i++;

//Dragon's Breath - Fire

rank[i] = [
		"<span style=text-align:left;float:left;>475 Mana</span><BR><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>20 sec cooldown</span><br>Targets in a cone in front of the caster take 382 to 442 Fire damage and are Disoriented for 3 sec. Any direct damaging attack will revive targets. Turns off your attack when used.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 575 Mana, 463-536 Damage<br>\
		&nbsp;Rank 3: 660 Mana, 584-677 Damage<br>\
		&nbsp;Rank 4: 700 Mana, 680-790 Damage<br>"
		];
i++;










		
//Frost Warding - Frost
rank[i]=[
"Increases the armor and resistances given by your Frost Armor and Ice Armor spells by 15%. In addition, gives your Frost Ward a 10% chance to reflect Frost spells and effects while active.",
"Increases the armor and resistances given by your Frost Armor and Ice Armor spells by 30%. In addition, gives your Frost Ward a 20% chance to reflect Frost spells and effects while active."
		];
i++;				



//Improved Frost Bolt - Frost
rank[i]=[
			"Reduces the casting time of your Frostbolt spell by 0.1 sec.",
			"Reduces the casting time of your Frostbolt spell by 0.2 sec.",
			"Reduces the casting time of your Frostbolt spell by 0.3 sec.",
			"Reduces the casting time of your Frostbolt spell by 0.4 sec.",
			"Reduces the casting time of your Frostbolt spell by 0.5 sec."
			];
i++;			
			
//Elemental Focus
rank[i]=[
"Reduces the mana cost and chance targets resist your Frost and Fire spells by 1%.",
"Reduces the mana cost and chance targets resist your Frost and Fire spells by 2%.",
"Reduces the mana cost and chance targets resist your Frost and Fire spells by 3%."
		];
i++;				
		
//Ice Shards - Frost
rank[i]=[
"Increases the critical strike damage bonus of your Frost spells by 20%.",
"Increases the critical strike damage bonus of your Frost spells by 40%.",
"Increases the critical strike damage bonus of your Frost spells by 60%.",
"Increases the critical strike damage bonus of your Frost spells by 80%.",
"Increases the critical strike damage bonus of your Frost spells by 100%."
		];
i++;		

//Frostbite - Frost
rank[i]=[
"Gives your Chill effects a 5% chance to freeze the target for 5 sec.",
"Gives your Chill effects a 10% chance to freeze the target for 5 sec.",
"Gives your Chill effects a 15% chance to freeze the target for 5 sec."
		];
i++;	

//Improved Frost Nova - Frost
rank[i]=[
"Reduces the cooldown of your Frost Nova spell by 2 sec.",
"Reduces the cooldown of your Frost Nova spell by 4 sec."
		];
i++;				
		
//Permafrost - Frost
rank[i]=[
			"Increases the duration of your Chill effects by 1 sec and reduces the target's speed by an additional 4%.",
			"Increases the duration of your Chill effects by 2 sec and reduces the target's speed by an additional 7%.",
			"Increases the duration of your Chill effects by 3 sec and reduces the target's speed by an additional 10%."
		];
i++;		



//Piercing Ice - Frost
rank[i]=[
"Increases the damage done by your Frost spells by 2%.",
"Increases the damage done by your Frost spells by 4%.",
"Increases the damage done by your Frost spells by 6%."
		];
i++;		

//Icy Veins - Frost
rank[i]=[
		"<span style=text-align:left;float:left;>67 Mana</span><br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>Hastens your spellcasting, increasing spell casting speed by 20% and gives you 100% chance to avoid interruption caused by damage while casting. Lasts 20 sec."
		];
i++;		

//Improved Blizzard - Frost
rank[i]=[
"Adds a chill effect to your Blizzard spell. This effect lowers the target's movement speed by 30%. Lasts 1.50 sec.",
"Adds a chill effect to your Blizzard spell. This effect lowers the target's movement speed by 50%. Lasts 1.50 sec.",
"Adds a chill effect to your Blizzard spell. This effect lowers the target's movement speed by 65%. Lasts 1.50 sec."
		];
i++;		

//Arctic Reach - Frost
rank[i]=[
"Increases the range of your Frostbolt and Blizzard spells and the radius of your Frost Nova and Cone of Cold spells by 10%.",
"Increases the range of your Frostbolt and Blizzard spells and the radius of your Frost Nova and Cone of Cold spells by 20%."
		];
i++;		
		

//Frost Channeling - Frost
rank[i]=[
"Reduces the mana cost of your frost spells by 5% and reduces the threat caused by your Frost spells by 4%.",
"Reduces the mana cost of your frost spells by 10% and reduces the threat caused by your Frost spells by 7%.",
"Reduces the mana cost of your frost spells by 15% and reduces the threat caused by your Frost spells by 10%."
		];
i++;		
		
//Shatter - Frost
rank[i]=[
"Increases the critical strike chance of all your spells against frozen targets by 10%.",
"Increases the critical strike chance of all your spells against frozen targets by 20%.",
"Increases the critical strike chance of all your spells against frozen targets by 30%.",
"Increases the critical strike chance of all your spells against frozen targets by 40%.",
"Increases the critical strike chance of all your spells against frozen targets by 50%."
		];
i++;

//Frozen Core - Frost
rank[i]=[
"Reduces the damage taken by Frost and Fire effects by 2%.",
"Reduces the damage taken by Frost and Fire effects by 4%.",
"Reduces the damage taken by Frost and Fire effects by 6%."
		];
i++;

//Cold Snap - Frost
rank[i]=[
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>8 min cooldown</span><br>When activated, this spell finishes the cooldown on all Frost spells you recently cast."
		];
i++;	
		
	
//Improved Cone of Cold - Frost
rank[i]=[
"Increases the damage dealt by your Cone of Cold spell by 15%.",
"Increases the damage dealt by your Cone of Cold spell by 25%.",
"Increases the damage dealt by your Cone of Cold spell by 35%."
		];
i++;	

//Ice Floes - Frost	
rank[i] = [
		"Reduces the cooldown of your Cone of Cold, Cold Snap, Ice Barrier and Ice Block spells by 10%.",
		"Reduces the cooldown of your Cone of Cold, Cold Snap, Ice Barrier and Ice Block spells by 20%."
		];
i++;

//Winter's Chill - Frost
rank[i]=[
"Gives your Frost damage spells a 20% chance to apply the Winter's Chill effect, which increases the chance a Frost spell will critically hit the target by 2% for 15 sec. Stacks up to 5 times.",
"Gives your Frost damage spells a 40% chance to apply the Winter's Chill effect, which increases the chance a Frost spell will critically hit the target by 2% for 15 sec. Stacks up to 5 times.",
"Gives your Frost damage spells a 60% chance to apply the Winter's Chill effect, which increases the chance a Frost spell will critically hit the target by 2% for 15 sec. Stacks up to 5 times.",
"Gives your Frost damage spells a 80% chance to apply the Winter's Chill effect, which increases the chance a Frost spell will critically hit the target by 2% for 15 sec. Stacks up to 5 times.",
"Gives your Frost damage spells a 100% chance to apply the Winter's Chill effect, which increases the chance a Frost spell will critically hit the target by 2% for 15 sec. Stacks up to 5 times."
		];
i++;

//Ice Barrier - Frost
rank[i]=[
		"<span style=text-align:left;float:left;>305 Mana</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>30 sec cooldown</span><br>Instantly shields you, absorbing 454 damage. Lasts 1 min. While the shield holds, spells will not be interrupted.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: Absorbs 568 Damage<br>\
		&nbsp;Rank 3: Absorbs 699 Damage<br>\
		&nbsp;Rank 4: Absorbs 842 Damage<br>\
		&nbsp;Rank 5: Absorbs 951 Damage<br>\
		&nbsp;Rank 6: Absorbs 1075 Damage"
		];
i++;	

//Arctic Winds - Frost
rank[i]=[
"Increases all Frost damage you cause by 1% and reduces the chance melee and ranged attacks will hit you by 1%.",
"Increases all Frost damage you cause by 2% and reduces the chance melee and ranged attacks will hit you by 2%.",
"Increases all Frost damage you cause by 3% and reduces the chance melee and ranged attacks will hit you by 3%.",
"Increases all Frost damage you cause by 4% and reduces the chance melee and ranged attacks will hit you by 4%.",
"Increases all Frost damage you cause by 5% and reduces the chance melee and ranged attacks will hit you by 5%."
		];
i++;

//Empowered Frostbolt - Frost
rank[i]=[
"Your Frostbolt spell gains an additional 2% of your bonus spell damage effects and an additional 1% chance to critically strike.",
"Your Frostbolt spell gains an additional 4% of your bonus spell damage effects and an additional 2% chance to critically strike.",
"Your Frostbolt spell gains an additional 6% of your bonus spell damage effects and an additional 3% chance to critically strike.",
"Your Frostbolt spell gains an additional 8% of your bonus spell damage effects and an additional 4% chance to critically strike.",
"Your Frostbolt spell gains an additional 10% of your bonus spell damage effects and an additional 5% chance to critically strike."
		];
i++;

//Summon Water Elemental - Frost
rank[i]=[
		"358 Mana<br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>3 min cooldown</span><br>Summon a Water Elemental to fight for the caster for 45 sec."
		];
i++;	
		
//Frost Talents End^^
jsLoaded=true;//needed for ajax script loading
