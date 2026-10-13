var i = 0;
var t = 0;

var className = "Warlock Talents";
var talentPath = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fglobal%2Ftalents%2Fwarlock%2Fdata.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ftalents%2F&reason=external-or-uncollected-resource";

tree[i] = "Affliction"; i++;
tree[i] = "Demonology"; i++;
tree[i] = "Destruction"; i++;

i = 0;

//rank
//horizontal position
//vertical position
talent[i] = [0, "Suppression", 5, 2, 1]; i++;
talent[i] = [0, "Improved Corruption", 5, 3, 1]; i++;
talent[i] = [0, "Improved Curse of Weakness", 2, 1, 2]; i++;
talent[i] = [0, "Improved Drain Soul", 2, 2, 2]; i++; 
talent[i] = [0, "Improved Life Tap", 2, 3, 2]; i++;
talent[i] = [0, "Soul Siphon", 2, 4, 2]; i++;
talent[i] = [0, "Improved Curse of Agony", 2, 1, 3]; i++;
talent[i] = [0, "Fel Concentration", 5, 2, 3]; i++;
talent[i] = [0, "Amplify Curse", 1, 3, 3]; i++;
talent[i] = [0, "Grim Reach", 2, 1, 4]; i++;
talent[i] = [0, "Nightfall", 2, 2, 4]; i++;
talent[i] = [0, "Empowered Corruption", 3, 4, 4]; i++;
talent[i] = [0, "Shadow Embrace", 5, 1, 5]; i++;
talent[i] = [0, "Siphon Life", 1, 2, 5]; i++;
talent[i] = [0, "Curse of Exhaustion", 1, 3, 5, [getTalentID("Amplify Curse"),1]]; i++;
talent[i] = [0, "Shadow Mastery", 5, 2, 6, [getTalentID("Siphon Life"),1]]; i++;
talent[i] = [0, "Contagion", 5, 2, 7]; i++;
talent[i] = [0, "Dark Pact", 1, 3, 7]; i++;
talent[i] = [0, "Improved Howl of Terror", 2, 1, 8]; i++;
talent[i] = [0, "Malediction", 3, 3, 8]; i++;
talent[i] = [0, "Unstable Affliction", 1, 2, 9, [getTalentID("Contagion"),5]]; i++;

treeStartStop[t] = i -1;
t++;

//demonology talents
talent[i] = [1, "Improved Healthstone", 2, 1, 1]; i++;
talent[i] = [1, "Improved Imp", 3, 2, 1]; i++;
talent[i] = [1, "Demonic Embrace", 5, 3, 1]; i++;
talent[i] = [1, "Improved Health Funnel", 2, 1, 2]; i++;
talent[i] = [1, "Improved Voidwalker", 3, 2, 2]; i++;
talent[i] = [1, "Fel Intellect", 3, 3, 2]; i++;
talent[i] = [1, "Improved Succubus", 3, 1, 3]; i++;
talent[i] = [1, "Fel Domination", 1, 2, 3]; i++;
talent[i] = [1, "Fel Stamina", 3, 3, 3]; i++;
talent[i] = [1, "Demonic Aegis", 3, 4, 3]; i++;
talent[i] = [1, "Master Summoner", 2, 2, 4, [getTalentID("Fel Domination"),1]]; i++;
talent[i] = [1, "Unholy Power", 5, 3, 4]; i++;
talent[i] = [1, "Improved Enslave Demon", 2, 1, 5]; i++;
talent[i] = [1, "Demonic Sacrifice", 1, 2, 5]; i++;
talent[i] = [1, "Master Conjuror", 2, 4, 5]; i++;
talent[i] = [1, "Mana Feed", 3, 1, 6]; i++;
talent[i] = [1, "Master Demonologist", 5, 3, 6, [getTalentID("Unholy Power"),5]]; i++;
talent[i] = [1, "Demonic Resilience", 3, 1, 7]; i++;
talent[i] = [1, "Soul Link", 1, 2, 7, [getTalentID("Demonic Sacrifice"),1]]; i++;
talent[i] = [1, "Demonic Knowledge", 3, 3, 7]; i++;
talent[i] = [1, "Demonic Tactics", 5, 2, 8]; i++;
talent[i] = [1, "Summon Felguard", 1, 2, 9]; i++;

treeStartStop[t] = i -1;
t++;

//destruction talents
talent[i] = [2, "Improved Shadow Bolt", 5, 2, 1]; i++;
talent[i] = [2, "Cataclysm", 5, 3, 1]; i++;
talent[i] = [2, "Bane", 5, 2, 2]; i++;
talent[i] = [2, "Aftermath", 5, 3, 2]; i++;
talent[i] = [2, "Improved Firebolt", 2, 1, 3]; i++;
talent[i] = [2, "Improved Lash of Pain", 2, 2, 3]; i++;
talent[i] = [2, "Devastation", 5, 3, 3]; i++;
talent[i] = [2, "Shadowburn", 1, 4, 3]; i++;
talent[i] = [2, "Intensity", 2, 1, 4]; i++;
talent[i] = [2, "Destructive Reach", 2, 2, 4]; i++;
talent[i] = [2, "Improved Searing Pain", 3, 4, 4]; i++;
talent[i] = [2, "Pyroclasm", 2, 1, 5, [getTalentID("Intensity"),2]]; i++;
talent[i] = [2, "Improved Immolate", 5, 2, 5]; i++;
talent[i] = [2, "Ruin", 1, 3, 5, [getTalentID("Devastation"),5]]; i++;
talent[i] = [2, "Nether Protection", 3, 1, 6]; i++;
talent[i] = [2, "Emberstorm", 5, 3, 6]; i++;
talent[i] = [2, "Backlash", 3, 1, 7]; i++; 
talent[i] = [2, "Conflagrate", 1, 2, 7, [getTalentID("Improved Immolate"),5]]; i++;
talent[i] = [2, "Soul Leech", 3, 3, 7]; i++;
talent[i] = [2, "Shadow and Flame", 5, 2, 8]; i++;
talent[i] = [2, "Shadowfury", 1, 2, 9, [getTalentID("Shadow and Flame"),5]]; i++;

treeStartStop[t] = i -1;
t++;

i = 0;


//Affliction Talents Begin

//Suppression - Affliction
rank[i] = [
"Reduces the chance for enemies to resist your Affliction spells by 2%.",
"Reduces the chance for enemies to resist your Affliction spells by 4%.",
"Reduces the chance for enemies to resist your Affliction spells by 6%.",
"Reduces the chance for enemies to resist your Affliction spells by 8%.",
"Reduces the chance for enemies to resist your Affliction spells by 10%."
		];
i++;		
		
//Improved Corruption - Affliction
rank[i] = [
"Reduces the casting time of your Corruption spell by 0.4 sec.",
"Reduces the casting time of your Corruption spell by 0.8 sec.",
"Reduces the casting time of your Corruption spell by 1.2 sec.",
"Reduces the casting time of your Corruption spell by 1.6 sec.",
"Reduces the casting time of your Corruption spell by 2 sec."
		];
i++;		

//Improved Curse of Weakness - Affliction
rank[i] = [
"Increases the effect of your Curse of Weakness by 10%.",
"Increases the effect of your Curse of Weakness by 20%."
		];
i++;		
		
//Improved Drain Soul - Affliction
rank[i] = [
"Returns 7% of your maximum mana if the target is killed by you while you drain its soul. In addition, your Affliction spells generate 5% less threat.",
"Returns 15% of your maximum mana if the target is killed by you while you drain its soul. In addition, your Affliction spells generate 10% less threat."
		];
i++;		

//Improved Life Tap - Affliction
rank[i] = [
"Increases the amount of Mana awarded by your Life Tap spell by 10%.",
"Increases the amount of Mana awarded by your Life Tap spell by 20%."
		];
i++;		

//Soul Siphon - Affliction
rank[i] = [
"Increases the amount drained by your Drain Life spell by an additional 2% for each Affliction effect on the target, up to a maximum of 24% additional effect.",
"Increases the amount drained by your Drain Life spell by an additional 4% for each Affliction effect on the target, up to a maximum of 60% additional effect."
		];
i++;		
		
//Improved Curse of Agony - Affliction
rank[i] = [
"Increases the damage done by your Curse of Agony by 5%.",
"Increases the damage done by your Curse of Agony by 10%."
		];		
i++;		


//Fel Concentration - Affliction
rank[i] = [ 
"Gives you a 14% chance to avoid interruption caused by damage while channeling the Drain Life, Drain Mana, or Drain Soul spell.",
"Gives you a 28% chance to avoid interruption caused by damage while channeling the Drain Life, Drain Mana, or Drain Soul spell.",
"Gives you a 42% chance to avoid interruption caused by damage while channeling the Drain Life, Drain Mana, or Drain Soul spell.",
"Gives you a 56% chance to avoid interruption caused by damage while channeling the Drain Life, Drain Mana, or Drain Soul spell.",
"Gives you a 70% chance to avoid interruption caused by damage while channeling the Drain Life, Drain Mana, or Drain Soul spell."
		];
i++;		


//Amplify Curse - Affliction
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>Increases the effect of your next Curse of Doom or Curse of Agony by 50%, or your next Curse of Exhaustion by 20%. Lasts 30 sec."
		];
i++;		

//Grim Reach - Affliction
rank[i] = [
"Increases the range of your Affliction spells by 10%.",
"Increases the range of your Affliction spells by 20%."
		];
i++;		

//Nightfall - Affliction	
rank[i] = [
"Gives your Corruption and Drain Life spells a 2% chance to cause you to enter a Shadow Trance state after damaging the opponent. The Shadow Trance state reduces the casting time of your next Shadow Bolt spell by 100%.",
"Gives your Corruption and Drain Life spells a 4% chance to cause you to enter a Shadow Trance state after damaging the opponent. The Shadow Trance state reduces the casting time of your next Shadow Bolt spell by 100%."
		];
i++;		

//Empowered Corruption - Affliction
rank[i] = [
"Your Corruption spell gains an additional 12% of your bonus spell damage effects.",
"Your Corruption spell gains an additional 24% of your bonus spell damage effects.",
"Your Corruption spell gains an additional 36% of your bonus spell damage effects."
		];
i++;		

//Shadow Embrace
rank[i] = [
"Your Corruption, Curse of Agony, Siphon Life and Seed of Corruption spells also cause the Shadow Embrace effect, which reduces physical damage caused by 1%.",
"Your Corruption, Curse of Agony, Siphon Life and Seed of Corruption spells also cause the Shadow Embrace effect, which reduces physical damage caused by 2%.",
"Your Corruption, Curse of Agony, Siphon Life and Seed of Corruption spells also cause the Shadow Embrace effect, which reduces physical damage caused by 3%.",
"Your Corruption, Curse of Agony, Siphon Life and Seed of Corruption spells also cause the Shadow Embrace effect, which reduces physical damage caused by 4%.",
"Your Corruption, Curse of Agony, Siphon Life and Seed of Corruption spells also cause the Shadow Embrace effect, which reduces physical damage caused by 5%."
		];
i++;

//Siphon Life - Affliction
rank[i] = [
		"<span style=text-align:left;float:left;>140 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>Instant cast<br>Transfers 15 health from the target to the caster every 3 sec. Lasts 30 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 190 Mana, 22 Health<br>\
		&nbsp;Rank 3: 250 Mana, 33 Health<br>\
		&nbsp;Rank 4: 310 Mana, 45 Health<br>\
		&nbsp;Rank 5: 350 Mana, 52 Health<br>\
		&nbsp;Rank 6: 410 Mana, 63 Health"
		];
i++;		

//Curse of Exhaustion - Affliction
rank[i] = [
		"<span style=text-align:left;float:left;>156 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>Instant cast<br>Reduces the target's movement speed by 30% for 12 sec. Only one Curse per Warlock can be active on any one target."
		];		
i++;		

//Shadow Mastery - Affliction
rank[i] = [
"Increases the damage dealt or life drained by your Shadow spells by 2%.",
"Increases the damage dealt or life drained by your Shadow spells by 4%.",
"Increases the damage dealt or life drained by your Shadow spells by 6%.",
"Increases the damage dealt or life drained by your Shadow spells by 8%.",
"Increases the damage dealt or life drained by your Shadow spells by 10%."
		];
i++;

//Contagion - Affliction
rank[i] = [
"Increases the damage of Curse of Agony, Corruption and Seed of Corruption by 1% and reduces the chance your Affliction spells will be dispelled by an additional 6%.",
"Increases the damage of Curse of Agony, Corruption and Seed of Corruption by 2% and reduces the chance your Affliction spells will be dispelled by an additional 12%.",
"Increases the damage of Curse of Agony, Corruption and Seed of Corruption by 3% and reduces the chance your Affliction spells will be dispelled by an additional 18%.",
"Increases the damage of Curse of Agony, Corruption and Seed of Corruption by 4% and reduces the chance your Affliction spells will be dispelled by an additional 24%.",
"Increases the damage of Curse of Agony, Corruption and Seed of Corruption by 5% and reduces the chance your Affliction spells will be dispelled by an additional 30%."
		];
i++;


//Dark Pact - Affliction
rank[i] = [
		"30 yd range<br>Instant<br>Drains 305 of your pet's Mana, returning 100% to you.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 440 Mana<br>\
		&nbsp;Rank 3: 545 Mana<br>\
		&nbsp;Rank 4: 700 Mana"
		];
i++;

//Improved Howl of Terror - Affliction
rank[i] = [
"Reduces the casting time of your Howl of Terror spell by 0.8 sec.",
"Reduces the casting time of your Howl of Terror spell by 1.5 sec."
		];
i++;

//Malediction - Affliction
rank[i] = [
"Increases the damage bonus effect of your Curse of Shadows and Curse of the Elements spells by an additional 1%.",
"Increases the damage bonus effect of your Curse of Shadows and Curse of the Elements spells by an additional 2%.",
"Increases the damage bonus effect of your Curse of Shadows and Curse of the Elements spells by an additional 3%."
		];
i++;

//Unstable Affliction - Demonology 
rank[i]=[
		"<span style=text-align:left;float:left;>270 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>1.5 sec cast<br>Shadow energy slowly destroys the target, causing 660 damage over 18 sec. In addition, if the Unstable Affliction is dispelled it will cause 990 damage to the dispeller and silence them for 5 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 330 Mana, 840 DoT, 1260 damage to dispeller<br>\
		&nbsp;Rank 3: 400 Mana, 1050 DoT, 1575 damage to dispeller"
			];
i++;	

















//Improved Healthstone - Demonology
rank[i] = [
"Increases the amount of Health restored by your Healthstone by 10%.",
"Increases the amount of Health restored by your Healthstone by 20%."
		];
i++;		

//Improved Imp - Demonology
rank[i] = [
"Increases the effect of your Imp's Firebolt, Fire Shield, and Blood Pact spells by 10%.",
"Increases the effect of your Imp's Firebolt, Fire Shield, and Blood Pact spells by 20%.",
"Increases the effect of your Imp's Firebolt, Fire Shield, and Blood Pact spells by 30%."
		];
i++;

//Demonic Embrace - Demonology
rank[i] = [
"Increases your total Stamina by 3% but reduces your total Spirit by 1%.",
"Increases your total Stamina by 6% but reduces your total Spirit by 2%.",
"Increases your total Stamina by 9% but reduces your total Spirit by 3%.",
"Increases your total Stamina by 12% but reduces your total Spirit by 4%.",
"Increases your total Stamina by 15% but reduces your total Spirit by 5%."
		];
i++;		

//Improved Health Funnel - Demonology
rank[i] = [
"Increases the amount of Health transfered by your Health Funnel spell by 10% and reduces the initial health cost by 10%.",
"Increases the amount of Health transfered by your Health Funnel spell by 20% and reduces the initial health cost by 20%."
		];		
i++;		

//Improved Voidwalker - Demonology
rank[i] = [

"Increases the effectiveness of your Voidwalker's Torment, Consume Shadows, Sacrifice and Suffering spells by 10%.",
"Increases the effectiveness of your Voidwalker's Torment, Consume Shadows, Sacrifice and Suffering spells by 20%.",
"Increases the effectiveness of your Voidwalker's Torment, Consume Shadows, Sacrifice and Suffering spells by 30%."
		];
i++;		

//Fel Intellect - Demonology
rank[i] = [
"Increases the Intellect of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 5% and increases your maximum mana by 1%.",
"Increases the Intellect of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 10% and increases your maximum mana by 2%.",
"Increases the Intellect of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 15% and increases your maximum mana by 3%."
		];
i++;		

//Improved Succubus - Demonology
rank[i] = [
"Increases the effect of your Succubus' Lash of Pain and Soothing Kiss spells by 10%, and increases the duration of your Succubus' Seduction and Lesser Invisibility spells by 10%.",
"Increases the effect of your Succubus' Lash of Pain and Soothing Kiss spells by 20%, and increases the duration of your Succubus' Seduction and Lesser Invisibility spells by 20%.",
"Increases the effect of your Succubus' Lash of Pain and Soothing Kiss spells by 30%, and increases the duration of your Succubus' Seduction and Lesser Invisibility spells by 30%."
		];
i++;		

//Fel Domination - Demonology
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>15 min cooldown</span><br>Your next Imp, Voidwalker, Succubus, Felhunter or Felguard Summon spell has its casting time reduced by 5.5 sec and its Mana cost reduced by 50%."
		];
i++;		

//Fel Stamina - Demonology
rank[i] = [
"Increases the Stamina of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 5% and increases your maximum health by 1%.",
"Increases the Stamina of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 10% and increases your maximum health by 2%.",
"Increases the Stamina of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 15% and increases your maximum health by 3%."
		];i++;		

//Demonic Aegis - Demonology 
rank[i] = [
"Increases the effectiveness of your Demon Armor and Fel Armor spells by 10%.",
"Increases the effectiveness of your Demon Armor and Fel Armor spells by 20%.",
"Increases the effectiveness of your Demon Armor and Fel Armor spells by 30%."
		];
i++;		
		
//Master Summoner - Demonology 
rank[i] = [
"Reduces the casting time of your Imp, Voidwalker, Succubus, Felhunter and Felguard Summoning spells by 2 sec and the Mana cost by 20%.",
"Reduces the casting time of your Imp, Voidwalker, Succubus, Felhunter and Felguard Summoning spells by 4 sec and the Mana cost by 40%."
		];
i++;		

//Unholy Power - Demonology 
rank[i] = [
"Increases the damage done by your Voidwalker, Succubus, Felhunter and Felguard's melee attacks and your Imp's Firebolt by 4%.",
"Increases the damage done by your Voidwalker, Succubus, Felhunter and Felguard's melee attacks and your Imp's Firebolt by 8%.",
"Increases the damage done by your Voidwalker, Succubus, Felhunter and Felguard's melee attacks and your Imp's Firebolt by 12%.",
"Increases the damage done by your Voidwalker, Succubus, Felhunter and Felguard's melee attacks and your Imp's Firebolt by 16%.",
"Increases the damage done by your Voidwalker, Succubus, Felhunter and Felguard's melee attacks and your Imp's Firebolt by 20%."
		];
i++;

//Improved Enslave Demon - Demonology

rank[i] = [
"Reduces the Attack Speed and Casting Speed penalty of your Enslave Demon spell by 5% and reduces the resist chance by 5%.",
"Reduces the Attack Speed and Casting Speed penalty of your Enslave Demon spell by 10% and reduces the resist chance by 10%."
		];
i++;
		
//Demonic Sacrifice - Demonology 
rank[i]=[
		"100 yd range<br>Instant<br>When activated, sacrifices your summoned demon to grant you an effect that lasts 30 min. The effect is canceled if any Demon is summoned.<br><br>Imp: Increases your Fire damage by 15%.<br><br>Voidwalker: Restores 2% of total Health every 4 sec.<br><br>Succubus: Increases your Shadow damage by 15%.<br><br>Felhunter: Restores 3% of total Mana every 4 sec.<br><br>Felguard: Increases your Shadow damage by 10% and restores 2% of total mana every 4 sec."
			];
i++;			
			
//Master Conjuror - Demonology
rank[i]=[
"Increases the bonus Fire damage from Firestones and the Firestone effect by 15% and increases the spell critical strike rating bonus of your Spellstone by 15%.",
"Increases the bonus Fire damage from Firestones and the Firestone effect by 30% and increases the spell critical strike rating bonus of your Spellstone by 30%."
		];
i++;		

//Mana Feed - Demonology
rank[i]=[
"When you gain mana from Drain Mana or Life Tap spells, your pet gains 33% of the mana you gain",
"When you gain mana from Drain Mana or Life Tap spells, your pet gains 66% of the mana you gain",
"When you gain mana from Drain Mana or Life Tap spells, your pet gains 100% of the mana you gain"
		];
i++;				
		
//Master Demonologist - Demonology 
rank[i]=[
"Grants both the Warlock and the summoned demon an effect as long as that demon is active.<br><br>Imp - Reduces threat caused by 4%.<br><br>Voidwalker - Reduces physical damage taken by 2%.<br><br>Succubus - Increases all damage caused by 2%.<br><br>Felhunter - Increases all resistances by .2 per level.<br><br>Felguard - Increases all damage caused by 1% and all resistances by .1 per level.",
"Grants both the Warlock and the summoned demon an effect as long as that demon is active.<br><br>Imp - Reduces threat caused by 8%.<br><br>Voidwalker - Reduces physical damage taken by 4%.<br><br>Succubus - Increases all damage caused by 4%.<br><br>Felhunter - Increases all resistances by .4 per level.<br><br>Felguard - Increases all damage caused by 2% and all resistances by .2 per level.",
"Grants both the Warlock and the summoned demon an effect as long as that demon is active.<br><br>Imp - Reduces threat caused by 12%.<br><br>Voidwalker - Reduces physical damage taken by 6%.<br><br>Succubus - Increases all damage caused by 6%.<br><br>Felhunter - Increases all resistances by .6 per level.<br><br>Felguard - Increases all damage caused by 3% and all resistances by .3 per level.",
"Grants both the Warlock and the summoned demon an effect as long as that demon is active.<br><br>Imp - Reduces threat caused by 16%.<br><br>Voidwalker - Reduces physical damage taken by 8%.<br><br>Succubus - Increases all damage caused by 8%.<br><br>Felhunter - Increases all resistances by .8 per level.<br><br>Felguard - Increases all damage caused by 4% and all resistances by .4 per level.",
"Grants both the Warlock and the summoned demon an effect as long as that demon is active.<br><br>Imp - Reduces threat caused by 20%.<br><br>Voidwalker - Reduces physical damage taken by 10%.<br><br>Succubus - Increases all damage caused by 10%.<br><br>Felhunter - Increases all resistances by 1 per level.<br><br>Felguard - Increases all damage caused by 5% and all resistances by .5 per level."
		];
i++;	

//Demonic Resilience - Demonology 
rank[i]=[
"Reduces the chance you'll be critically hit by melee and spells by 1% and reduces all damage your summoned demon takes by 5%.",
"Reduces the chance you'll be critically hit by melee and spells by 2% and reduces all damage your summoned demon takes by 10%.",
"Reduces the chance you'll be critically hit by melee and spells by 3% and reduces all damage your summoned demon takes by 15%."
		];
i++;
		
//Soul Link - Demonology
rank[i]=[
		"<span style=text-align:left;float:left;>418 Mana</span><span style=text-align:right;float:right;>100 yd range</span><br>Instant cast<br>When active, 20% of all damage taken by the caster is taken by your Imp, Voidwalker, Succubus, Felhunter, Felguard, or enslaved demon instead.  That damage cannot be prevented.  In addition, both the demon and master will inflict 5% more damage.  Lasts as long as the demon is active and controlled."
		];
i++;		
		
//Demonic Knowledge - Demonology 
rank[i]=[
"Increases your spell damage by an amount equal to 4% of the total of your active demon's Stamina plus Intellect.",
"Increases your spell damage by an amount equal to 8% of the total of your active demon's Stamina plus Intellect.",
"Increases your spell damage by an amount equal to 12% of the total of your active demon's Stamina plus Intellect."
		];
i++;		


//Demonic Tactics - Demonology 
rank[i]=[
"Increases melee and spell critical strike chance for you and your summoned demon by 1%.",
"Increases melee and spell critical strike chance for you and your summoned demon by 2%.",
"Increases melee and spell critical strike chance for you and your summoned demon by 3%.",
"Increases melee and spell critical strike chance for you and your summoned demon by 4%.",
"Increases melee and spell critical strike chance for you and your summoned demon by 5%."
		];
i++;	

//Summon Felguard - Demonology 
rank[i]=[
	"<span style=text-align:left;float:left;>2092 Mana</span><BR><span style=text-align:left;float:left;>10 sec cast</span><br>Reagents: Soul Shard<BR>Summons a Felguard under the command of the Warlock."
		];
i++;















		
//Improved Shadow Bolt - Destruction  
rank[i]=[
"Your Shadow Bolt critical strikes increase Shadow damage dealt to the target by 4% until 4 non-periodic damage sources are applied. Effect lasts a maximum of 12 sec.",
"Your Shadow Bolt critical strikes increase Shadow damage dealt to the target by 8% until 4 non-periodic damage sources are applied. Effect lasts a maximum of 12 sec.",
"Your Shadow Bolt critical strikes increase Shadow damage dealt to the target by 12% until 4 non-periodic damage sources are applied. Effect lasts a maximum of 12 sec.",
"Your Shadow Bolt critical strikes increase Shadow damage dealt to the target by 16% until 4 non-periodic damage sources are applied. Effect lasts a maximum of 12 sec.",
"Your Shadow Bolt critical strikes increase Shadow damage dealt to the target by 20% until 4 non-periodic damage sources are applied. Effect lasts a maximum of 12 sec."
		];
i++;		
		
//Cataclysm - Destruction
rank[i]=[
"Reduces the Mana cost of your Destruction spells by 1%.",
"Reduces the Mana cost of your Destruction spells by 2%.",
"Reduces the Mana cost of your Destruction spells by 3%.",
"Reduces the Mana cost of your Destruction spells by 4%.",
"Reduces the Mana cost of your Destruction spells by 5%."
		];
i++;		
		
//Bane - Destruction
rank[i]=[
"Reduces the casting time of your Shadow Bolt and Immolate spells by 0.1 sec and your Soul Fire spell by 0.4 sec.",
"Reduces the casting time of your Shadow Bolt and Immolate spells by 0.2 sec and your Soul Fire spell by 0.8 sec.",
"Reduces the casting time of your Shadow Bolt and Immolate spells by 0.3 sec and your Soul Fire spell by 1.2 sec.",
"Reduces the casting time of your Shadow Bolt and Immolate spells by 0.4 sec and your Soul Fire spell by 1.6 sec.",
"Reduces the casting time of your Shadow Bolt and Immolate spells by 0.5 sec and your Soul Fire spell by 2.0 sec."
		];
i++;		
		
//Aftermath - Destruction
rank[i]=[
"Gives your Destruction spells a 2% chance to daze the target for 5 sec.",
"Gives your Destruction spells a 4% chance to daze the target for 5 sec.",
"Gives your Destruction spells a 6% chance to daze the target for 5 sec.",
"Gives your Destruction spells a 8% chance to daze the target for 5 sec.",
"Gives your Destruction spells a 10% chance to daze the target for 5 sec."
		];
i++;		
		
//Improved Firebolt - Destruction
rank[i]=[
"Reduces the casting time of your Imp's Firebolt spell by 0.25 sec.",
"Reduces the casting time of your Imp's Firebolt spell by 0.5 sec."
		];
i++;		
		
//Improved Lash of Pain - Destruction
rank[i]=[
"Reduces the cooldown of your Succubus' Lash of Pain spell by 3 sec.",
"Reduces the cooldown of your Succubus' Lash of Pain spell by 6 sec."
		];
i++;		
		
//Devastation - Destruction
rank[i]=[
"Increases the critical strike chance of your Destruction spells by 1%.",
"Increases the critical strike chance of your Destruction spells by 2%.",
"Increases the critical strike chance of your Destruction spells by 3%.",
"Increases the critical strike chance of your Destruction spells by 4%.",
"Increases the critical strike chance of your Destruction spells by 5%."
		];
i++;		
		
//Shadowburn - Destruction 
rank[i]=[
		"<span style=text-align:left;float:left;>105 Mana</span><span style=text-align:right;float:right;>20 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>15 sec cooldown</span><br>Reagents: Soul Shard<br>Instantly blasts the target for 91 to 104 Shadow damage. If the target dies within 5 secs of Shadowburn, and yields experience or honor, the caster gains a Soul Shard.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 130 Mana, 123-140 Damage<br>\
		&nbsp;Rank 3: 190 Mana, 196-221 Damage<br>\
		&nbsp;Rank 4: 245 Mana, 274-307 Damage<br>\
		&nbsp;Rank 5: 305 Mana, 365-408 Damage<br>\
		&nbsp;Rank 6: 365 Mana, 468-520 Damage<br>\
		&nbsp;Rank 7: 435 Mana, 538-599 Damage<br>\
		&nbsp;Rank 8: 515 Mana, 597-665 Damage"
		];
i++;		
		
//Intensity - Destruction
rank[i]=[
"Gives you a 35% chance to resist interruption caused by damage while casting or channeling any Destruction spell.",
"Gives you a 70% chance to resist interruption caused by damage while casting or channeling any Destruction spell."
		];
i++;		
		
//Destructive Reach - Destruction  
rank[i]=[
"Increases the range of your Destruction spells by 10% and reduces threat caused by Destruction spells by 5%.",
"Increases the range of your Destruction spells by 20% and reduces threat caused by Destruction spells by 10%."
		];
i++;	
		
//Improved Searing Pain - Destruction   
rank[i]=[
"Increases the critical strike chance of your Searing Pain spell by 4%.",
"Increases the critical strike chance of your Searing Pain spell by 7%.",
"Increases the critical strike chance of your Searing Pain spell by 10%."
		];
i++;	


//Pyroclasm - Destruction
rank[i]=[
"Gives your Rain of Fire, Hellfire, and Soul Fire spells a 13% chance to stun the target for 3 sec.",
"Gives your Rain of Fire, Hellfire, and Soul Fire spells a 26% chance to stun the target for 3 sec."
		];
i++;	


//Improved Immolate - Destruction 
rank[i]=[
"Increases the initial damage of your Immolate spell by 5%.",
"Increases the initial damage of your Immolate spell by 10%.",
"Increases the initial damage of your Immolate spell by 15%.",
"Increases the initial damage of your Immolate spell by 20%.",
"Increases the initial damage of your Immolate spell by 25%."
		];
i++;	


//Ruin - Destruction  
rank[i]=[
"Increases the critical strike damage bonus of your Destruction spells by 100%."
		];
i++;	


//Nether Protection - Destruction 
rank[i]=[
"After being hit with a Shadow or Fire spell, you have a 10% chance to become immune to Shadow and Fire spells for 4 sec.",
"After being hit with a Shadow or Fire spell, you have a 20% chance to become immune to Shadow and Fire spells for 4 sec.",
"After being hit with a Shadow or Fire spell, you have a 30% chance to become immune to Shadow and Fire spells for 4 sec."
		];
i++;

//Emberstorm - Destruction 
rank[i]=[
"Increases the damage done by your Fire spells by 2% and reduces the cast time of your Incinerate spell by 2%.",
"Increases the damage done by your Fire spells by 4% and reduces the cast time of your Incinerate spell by 4%.",
"Increases the damage done by your Fire spells by 6% and reduces the cast time of your Incinerate spell by 6%.",
"Increases the damage done by your Fire spells by 8% and reduces the cast time of your Incinerate spell by 8%.",
"Increases the damage done by your Fire spells by 10% and reduces the cast time of your Incinerate spell by 10%."
		];
i++;	

//Backlash - Destruction //New/Changed
rank[i]=[
"Increases your critical strike chance with spells by an additional 1% and gives you a 8% chance when hit by a physical attack to reduce the cast time of your next Shadow Bolt or Incinerate spell by 100%. This effect lasts 8 sec and will not occur more than once every 8 seconds.",
"Increases your critical strike chance with spells by an additional 2% and gives you a 16% chance when hit by a physical attack to reduce the cast time of your next Shadow Bolt or Incinerate spell by 100%. This effect lasts 8 sec and will not occur more than once every 8 seconds.",
"Increases your critical strike chance with spells by an additional 3% and gives you a 25% chance when hit by a physical attack to reduce the cast time of your next Shadow Bolt or Incinerate spell by 100%. This effect lasts 8 sec and will not occur more than once every 8 seconds."
		];
i++;

//Conflagrate - Destruction 
rank[i]=[

		"<span style=text-align:left;float:left;>165 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br><span style=text-align:left;float:left;>Instant Cast</span><span style=text-align:right;float:right;>10 sec cooldown</span><br>Ignites a target that is already afflicted by Immolate, dealing 249 to 316 Fire damage and consuming the Immolate spell.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 200 Mana, 326-407 Damage<br>\
		&nbsp;Rank 3: 230 Mana, 395-491 Damage<br>\
		&nbsp;Rank 4: 255 Mana, 455-566 Damage<br>\
		&nbsp;Rank 5: 280 Mana, 521-648 Damage<br>\
		&nbsp;Rank 6: 305 Mana, 579-721 Damage"
		];
i++;	

//Soul Leech - Destruction 
rank[i]=[
"Gives your Shadow Bolt, Shadowburn, Soul Fire, Incinerate, Searing Pain and Conflagrate spells a 10% chance to return health equal to 20% of the damage caused.",
"Gives your Shadow Bolt, Shadowburn, Soul Fire, Incinerate, Searing Pain and Conflagrate spells a 20% chance to return health equal to 20% of the damage caused.",
"Gives your Shadow Bolt, Shadowburn, Soul Fire, Incinerate, Searing Pain and Conflagrate spells a 30% chance to return health equal to 20% of the damage caused."
		];
i++;

//Shadow and Flame - Destruction 
rank[i]=[
"Your Shadow Bolt and Incinerate spells gain an additional 4% of your bonus spell damage effects.",
"Your Shadow Bolt and Incinerate spells gain an additional 8% of your bonus spell damage effects.",
"Your Shadow Bolt and Incinerate spells gain an additional 12% of your bonus spell damage effects.",
"Your Shadow Bolt and Incinerate spells gain an additional 16% of your bonus spell damage effects.",
"Your Shadow Bolt and Incinerate spells gain an additional 20% of your bonus spell damage effects."
		];
i++;

//Shadowfury - Demonology 
rank[i]=[
		"<span style=text-align:left;float:left;>440 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br><span style=text-align:left;float:left;>0.5 sec cast</span><span style=text-align:right;float:right;>20 sec cooldown</span><br>Shadowfury is unleashed, causing 357 to 422 Shadow damage and stunning all enemies within 8 yds for 2 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 545 Mana, 476-565 Damage<br>\
		&nbsp;Rank 3: 710 Mana, 612-728 Damage<br>"
		];
i++;	

		
//Destruction Talents End^^

