var i = 0;
var t = 0;

var className = "Priest Talents";
var talentPath = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fglobal%2Ftalents%2Fpriest%2Fdata.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ftalents%2F&reason=external-or-uncollected-resource";

tree[i] = "Discipline"; i++;
tree[i] = "Holy"; i++;
tree[i] = "Shadow"; i++;

i = 0;

talent[i] = [0, "Unbreakable Will", 5, 2, 1]; i++;
talent[i] = [0, "Wand Specialization", 5, 3, 1]; i++;
talent[i] = [0, "Silent Resolve", 5, 1, 2]; i++;
talent[i] = [0, "Improved Power Word: Fortitude", 2, 2, 2]; i++;
talent[i] = [0, "Improved Power Word: Shield", 3, 3, 2]; i++;
talent[i] = [0, "Martyrdom", 2, 4, 2]; i++; 
talent[i] = [0, "Absolution", 3, 1, 3]; i++;
talent[i] = [0, "Inner Focus", 1, 2, 3]; i++;
talent[i] = [0, "Meditation", 3, 3, 3]; i++;
talent[i] = [0, "Improved Inner Fire", 3, 1, 4]; i++;
talent[i] = [0, "Mental Agility", 5, 2, 4]; i++;
talent[i] = [0, "Improved Mana Burn", 2, 4, 4]; i++;
talent[i] = [0, "Mental Strength", 5, 2, 5]; i++;
talent[i] = [0, "Divine Spirit", 1, 3, 5, [getTalentID("Meditation"),3]]; i++;
talent[i] = [0, "Improved Divine Spirit", 2, 4, 5, [getTalentID("Divine Spirit"),1]]; i++;
talent[i] = [0, "Focused Power", 2, 1, 6]; i++;
talent[i] = [0, "Force of Will", 5, 3, 6]; i++;
talent[i] = [0, "Focused Will", 3, 1, 7]; i++;
talent[i] = [0, "Power Infusion", 1, 2, 7, [getTalentID("Mental Strength"),5]]; i++;
talent[i] = [0, "Reflective Shield", 5, 3, 7]; i++;
talent[i] = [0, "Enlightenment", 5, 2, 8]; i++;
talent[i] = [0, "Pain Suppression", 1, 2, 9]; i++;
treeStartStop[t] = i -1;
t++;

//holy talents
talent[i] = [1, "Healing Focus", 2, 1, 1]; i++;
talent[i] = [1, "Improved Renew", 3, 2, 1]; i++;
talent[i] = [1, "Holy Specialization", 5, 3, 1]; i++;
talent[i] = [1, "Spell Warding", 5, 2, 2]; i++;
talent[i] = [1, "Divine Fury", 5, 3, 2]; i++;
talent[i] = [1, "Holy Nova", 1, 1, 3]; i++;
talent[i] = [1, "Blessed Recovery", 3, 2, 3]; i++;
talent[i] = [1, "Inspiration", 3, 4, 3]; i++;
talent[i] = [1, "Holy Reach", 2, 1, 4]; i++;
talent[i] = [1, "Improved Healing", 3, 2, 4]; i++;
talent[i] = [1, "Searing Light", 2, 3, 4, [getTalentID("Divine Fury"),5]]; i++;
talent[i] = [1, "Healing Prayers", 2, 1, 5]; i++;
talent[i] = [1, "Spirit of Redemption", 1, 2, 5]; i++;
talent[i] = [1, "Spiritual Guidance", 5, 3, 5]; i++;
talent[i] = [1, "Surge of Light", 2, 1, 6]; i++; 
talent[i] = [1, "Spiritual Healing", 5, 3, 6]; i++;
talent[i] = [1, "Holy Concentration", 3, 1, 7]; i++; 
talent[i] = [1, "Lightwell", 1, 2, 7, [getTalentID("Spirit of Redemption"),1]]; i++;
talent[i] = [1, "Blessed Resilience", 3, 3, 7]; i++;
talent[i] = [1, "Empowered Healing", 5, 2, 8]; i++;
talent[i] = [1, "Circle of Healing", 1, 2, 9]; i++; 
treeStartStop[t] = i -1;
t++;

//shadow talents
talent[i] = [2, "Spirit Tap", 5, 2, 1]; i++;
talent[i] = [2, "Blackout", 5, 3, 1]; i++;
talent[i] = [2, "Shadow Affinity", 3, 1, 2]; i++;
talent[i] = [2, "Improved Shadow Word: Pain", 2, 2, 2]; i++;
talent[i] = [2, "Shadow Focus", 5, 3, 2]; i++;
talent[i] = [2, "Improved Psychic Scream", 2, 1, 3]; i++;
talent[i] = [2, "Improved Mind Blast", 5, 2, 3]; i++;
talent[i] = [2, "Mind Flay", 1, 3, 3]; i++;
talent[i] = [2, "Improved Fade", 2, 2, 4]; i++;
talent[i] = [2, "Shadow Reach", 2, 3, 4]; i++;
talent[i] = [2, "Shadow Weaving", 5, 4, 4]; i++;
talent[i] = [2, "Silence", 1, 1, 5, [getTalentID("Improved Psychic Scream"),2]]; i++;
talent[i] = [2, "Vampiric Embrace", 1, 2, 5]; i++;
talent[i] = [2, "Improved Vampiric Embrace", 2, 3, 5, [getTalentID("Vampiric Embrace"),1]]; i++;
talent[i] = [2, "Focused Mind", 3, 4, 5]; i++; 
talent[i] = [2, "Shadow Resilience", 2, 1, 6]; i++;
talent[i] = [2, "Darkness", 5, 3, 6]; i++;
talent[i] = [2, "Shadowform", 1, 2, 7, [getTalentID("Vampiric Embrace"),1]]; i++;
talent[i] = [2, "Shadow Power", 5, 3, 7]; i++;
talent[i] = [2, "Misery", 5, 3, 8]; i++; 
talent[i] = [2, "Vampiric Touch", 1, 2, 9, [getTalentID("Shadowform"),1]]; i++; 
treeStartStop[t] = i -1;
t++;

i = 0;


//Discipline Talents Begin

//Unbreakable Will - Discipline
rank[i] = [
		"Increases your chance to resist Stun, Fear, and Silence effects by an additional 3%.",
		"Increases your chance to resist Stun, Fear, and Silence effects by an additional 6%.",
		"Increases your chance to resist Stun, Fear, and Silence effects by an additional 9%.",
		"Increases your chance to resist Stun, Fear, and Silence effects by an additional 12%.",
		"Increases your chance to resist Stun, Fear, and Silence effects by an additional 15%."
		];

i++;		
		
		
//Wand Specialization - Discipline		
rank[i] = [
		"Increases your damage with Wands by 5%.",
		"Increases your damage with Wands by 10%.",
		"Increases your damage with Wands by 15%.",
		"Increases your damage with Wands by 20%.",
		"Increases your damage with Wands by 25%."
		];

i++;				
		
//Silent Resolve - Discipline
rank[i] = [
		"Reduces the threat generated by your Holy and Discipline spells by 4% and reduces the chance your spells will be dispelled by 4%.",
		"Reduces the threat generated by your Holy and Discipline spells by 8% and reduces the chance your spells will be dispelled by 8%.",
		"Reduces the threat generated by your Holy and Discipline spells by 12% and reduces the chance your spells will be dispelled by 12%.",
		"Reduces the threat generated by your Holy and Discipline spells by 16% and reduces the chance your spells will be dispelled by 16%.",
		"Reduces the threat generated by your Holy and Discipline spells by 20% and reduces the chance your spells will be dispelled by 20%."
		];

i++;		

//Improved Power Word: Fortitude - Discipline		
rank[i] = [
		"Increases the effect of your Power Word: Fortitude and Prayer of Fortitude spells by 15%.",
		"Increases the effect of your Power Word: Fortitude and Prayer of Fortitude spells by 30%."
		];

i++;		

//Improved Power Word: Shield - Discipline		
rank[i] = [
		"Increases the damage absorbed by your Power Word: Shield by 5%.",
		"Increases the damage absorbed by your Power Word: Shield by 10%.",
		"Increases the damage absorbed by your Power Word: Shield by 15%."
		];

i++;		

		
//Martyrdom - Discipline		
rank[i] = [
		"Gives you a 50% chance to gain the Focused Casting effect that lasts for 6 sec after being the victim of a melee or ranged critical strike. The Focused Casting effect prevents you from losing casting time when taking damage and increases resistance to Interrupt effects by 10%.",
		"Gives you a 100% chance to gain the Focused Casting effect that lasts for 6 sec after being the victim of a melee or ranged critical strike. The Focused Casting effect prevents you from losing casting time when taking damage and increases resistance to Interrupt effects by 20%."
		];

i++;		

//Absolution - Discipline 3
rank[i] = [
		"Reduces the mana cost of your Dispel Magic, Cure Disease, Abolish Disease and Mass Dispel spells by 5%.",
		"Reduces the mana cost of your Dispel Magic, Cure Disease, Abolish Disease and Mass Dispel spells by 10%.",
		"Reduces the mana cost of your Dispel Magic, Cure Disease, Abolish Disease and Mass Dispel spells by 15%."				
		];

i++;		

//Inner Focus - Discipline		
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, reduces the Mana cost of your next spell by 100% and increases its critical effect chance by 25% if it is capable of a critical effect."
		];

i++;		


//Meditation - Discipline
rank[i] = [
		"Allows 10% of your Mana regeneration to continue while casting.",
		"Allows 20% of your Mana regeneration to continue while casting.",
		"Allows 30% of your Mana regeneration to continue while casting.",
		];

i++;	


//Improved Inner Fire - Discipline		
rank[i] = [
		"Increases the Armor bonus of your Inner Fire spell by 10%.",
		"Increases the Armor bonus of your Inner Fire spell by 20%.",
		"Increases the Armor bonus of your Inner Fire spell by 30%."
		];

i++;		


//Mental Agility - Discipline		
rank[i] = [ 
		"Reduces the mana cost of your instant cast spells by 2%.",
		"Reduces the mana cost of your instant cast spells by 4%.",
		"Reduces the mana cost of your instant cast spells by 6%.",
		"Reduces the mana cost of your instant cast spells by 8%.",
		"Reduces the mana cost of your instant cast spells by 10%."
		];

i++;		

//Improved Mana Burn - Discipline		
rank[i] = [
		"Reduces the casting time of your Mana Burn spell by 0.5 sec.",
		"Reduces the casting time of your Mana Burn spell by 1.0 sec."
		];

i++;		


//Mental Strength - Discipline		
rank[i] = [
		"Increases your maximum Mana by 2%.",
		"Increases your maximum Mana by 4%.",
		"Increases your maximum Mana by 6%.",
		"Increases your maximum Mana by 8%.",
		"Increases your maximum Mana by 10%."
		];

i++;		


	
//Divine Spirit - Discipline				
rank[i] = [
			"<span style=text-align:left;float:left;>250 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>Instant cast<br>Holy power infuses the target, increasing their Spirit by 17 for 30 min.<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 350 Mana, 23 Spirit<br>\
			&nbsp;Rank 3: 450 Mana, 33 Spirit<br>\
			&nbsp;Rank 4: 555 Mana, 40 Spirit<br>\
			&nbsp;Rank 5: 680 Mana, 50 Spirit"
		];

i++;		

//Improved Divine Spirit - Discipline				
rank[i] = [
			"Your Divine Spirit and Prayer of Spirit spells also increase the target's spell damage and healing by an amount equal to 5% of their total Spirit.",
			"Your Divine Spirit and Prayer of Spirit spells also increase the target's spell damage and healing by an amount equal to 10% of their total Spirit."
		];

i++;		
		
//Focused Power - Discipline 				
rank[i] = [
			"Your Smite, Mind Blast and Mass Dispel spells have an additional 2% chance to hit.  In addition, your Mass Dispel cast time is reduced by 0.5 sec.",
			"Your Smite, Mind Blast and Mass Dispel spells have an additional 4% chance to hit.  In addition, your Mass Dispel cast time is reduced by 1 sec."			
		];

i++;				


//Force of Will - Discipline		
rank[i] = [
		"Increases your spell damage by 1% and the critical strike chance of your offensive spells by 1%.",
		"Increases your spell damage by 2% and the critical strike chance of your offensive spells by 2%.",
		"Increases your spell damage by 3% and the critical strike chance of your offensive spells by 3%.",
		"Increases your spell damage by 4% and the critical strike chance of your offensive spells by 4%.",
		"Increases your spell damage by 5% and the critical strike chance of your offensive spells by 5%."
		];

i++;		


//Focused Will - Discipline		
rank[i] = [
		"After taking a critical hit you gain the Focused Will effect, reducing all damage taken by 1% and increasing healing effects on you by 4%.  Stacks up to 3 times.  Lasts 8 sec.",
		"After taking a critical hit you gain the Focused Will effect, reducing all damage taken by 3% and increasing healing effects on you by 7%.  Stacks up to 3 times.  Lasts 8 sec.",
		"After taking a critical hit you gain the Focused Will effect, reducing all damage taken by 5% and increasing healing effects on you by 10%.  Stacks up to 3 times.  Lasts 8 sec.",
		];

i++;		


//Power Infusion - Discipline				
rank[i] = [
			"<span style=text-align:left;float:left;>419 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>3 min cooldown</span><br>Infuses the target with power, increasing spell casting speed by 20% and reducing the mana cost of all spells by 20%. Lasts 15 sec."
		];
i++;			
		
//Reflective Shield - Discipline		
rank[i] = [
		"Causes 10% of the damage absorbed by your Power Word: Shield to reflect back at the attacker. This damage causes no threat.",
		"Causes 20% of the damage absorbed by your Power Word: Shield to reflect back at the attacker. This damage causes no threat.",
		"Causes 30% of the damage absorbed by your Power Word: Shield to reflect back at the attacker. This damage causes no threat.",
		"Causes 40% of the damage absorbed by your Power Word: Shield to reflect back at the attacker. This damage causes no threat.",
		"Causes 50% of the damage absorbed by your Power Word: Shield to reflect back at the attacker. This damage causes no threat."								
		];

i++;

	

//Misery - Discipline 	
rank[i] = [
		"Increases your total Stamina, Intellect, and Spirit by 1%.",
		"Increases your total Stamina, Intellect, and Spirit by 2%.",
		"Increases your total Stamina, Intellect, and Spirit by 3%.",
		"Increases your total Stamina, Intellect, and Spirit by 4%.",						
		"Increases your total Stamina, Intellect, and Spirit by 5%."
		];

i++;


//Pain Suppression - Discipline				
rank[i] = [
			"<span style=text-align:left;float:left;>209 Mana</span><span style=text-align:right;float:right;>40 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>2 min cooldown</span><br>Instantly reduces a friendly target's threat by 5%, reduces all damage taken by 40% and increases resistance to Dispel mechanics by 65% for 8 sec."
		];
i++;			
	
		
//Healing Focus - Holy
	
rank[i] = [
			"Gives you a 35% chance to avoid interruption caused by damage while casting any healing spell.",
			"Gives you a 70% chance to avoid interruption caused by damage while casting any healing spell."
		];		

i++;				
		
		
//Improved Renew - Holy 
	
rank[i] = [
			"Increases the amount healed by your Renew spell by 5%.",
			"Increases the amount healed by your Renew spell by 10%.",
			"Increases the amount healed by your Renew spell by 15%."
		];		

i++;		
		
//Holy Specialization - Holy

rank[i] = [
			"Increases the critical effect chance of your Holy spells by 1%.",
			"Increases the critical effect chance of your Holy spells by 2%.",
			"Increases the critical effect chance of your Holy spells by 3%.",
			"Increases the critical effect chance of your Holy spells by 4%.",
			"Increases the critical effect chance of your Holy spells by 5%."
		];

i++;		


//Spell Warding - Holy
		
rank[i] = [
			"Reduces all spell damage taken by 2%.",
			"Reduces all spell damage taken by 4%.",
			"Reduces all spell damage taken by 6%.",
			"Reduces all spell damage taken by 8%.",
			"Reduces all spell damage taken by 10%."
		];

i++;	


//Divine Fury - Holy

rank[i] = [
			"Reduces the casting time of your Smite, Holy Fire, Heal and Greater Heal spells by 0.1 sec.",
			"Reduces the casting time of your Smite, Holy Fire, Heal and Greater Heal spells by 0.2 sec.",
			"Reduces the casting time of your Smite, Holy Fire, Heal and Greater Heal spells by 0.3 sec.",
			"Reduces the casting time of your Smite, Holy Fire, Heal and Greater Heal spells by 0.4 sec.",
			"Reduces the casting time of your Smite, Holy Fire, Heal and Greater Heal spells by 0.5 sec."
		];

i++;

//Holy Nova - Holy		
		
rank[i] = [
			"185 Mana<br><span style=text-align:left;float:left;>Instant cast</span><br>Causes an explosion of holy light around the caster, causing 29 to 34 Holy damage to all enemy targets within 10 yards and healing all party members within 10 yards for 54 to 63. These effects cause no threat.<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 290 Mana, 52-61 Damage, 89-101 Health<br>\
			&nbsp;Rank 3: 400 Mana, 79-92 Damage, 124-143 Health<br>\
			&nbsp;Rank 4: 520 Mana, 110-127 Damage, 165-192 Health<br>\
			&nbsp;Rank 5: 635 Mana, 146-168 Damage, 239-276 Health<br>\
			&nbsp;Rank 6: 750 Mana, 188-217 Damage, 307-356 Health<br>\
			&nbsp;Rank 7: 875 Mana, 244-283 Damage, 386-448 Health<br>"

		];

i++;


//Blessed Recovery - Holy	
		
rank[i] = [
			"After being struck by a melee or ranged critical hit, heal 8% of the damage taken over 6 sec.",
			"After being struck by a melee or ranged critical hit, heal 16% of the damage taken over 6 sec.",
			"After being struck by a melee or ranged critical hit, heal 25% of the damage taken over 6 sec."
		];

i++;	

//Inspiration - Holy 
		
rank[i] = [
			"Increases your target's armor by 8% for 15 sec after getting a critical effect from your Flash Heal, Heal, Greater Heal, Binding Heal, Prayer of Healing, or Circle of Healing spell.",
			"Increases your target's armor by 16% for 15 sec after getting a critical effect from your Flash Heal, Heal, Greater Heal, Binding Heal, Prayer of Healing, or Circle of Healing spell.",
			"Increases your target's armor by 25% for 15 sec after getting a critical effect from your Flash Heal, Heal, Greater Heal, Binding Heal, Prayer of Healing, or Circle of Healing spell."
		];

i++;		





//Holy Reach - Holy 

rank[i] = [
			"Increases the range of your Smite and Holy Fire spells and the radius of your Prayer of Healing, Holy Nova, and Circle of Healing spells by 10%.",
			"Increases the range of your Smite and Holy Fire spells and the radius of your Prayer of Healing, Holy Nova, and Circle of Healing spells by 20%."
		];

i++;		

//Improved Healing - Holy

rank[i] = [
			"Reduces the Mana cost of your Lesser Heal, Heal, and Greater Heal spells by 5%.",
			"Reduces the Mana cost of your Lesser Heal, Heal, and Greater Heal spells by 10%.",
			"Reduces the Mana cost of your Lesser Heal, Heal, and Greater Heal spells by 15%."
		];

i++;		

//Searing Light - Holy

rank[i] = [
			"Increases the damage of your Smite and Holy Fire spells by 5%.",
			"Increases the damage of your Smite and Holy Fire spells by 10%."
		];

i++;		




//Healing Prayers - Holy	
		
rank[i] = [
			"Reduces the Mana cost of your Prayer of Healing and Prayer of Mending spells by 10%.",
			"Reduces the Mana cost of your Prayer of Healing and Prayer of Mending spells by 20%."
		];

i++;

//Spirit of Redemption - Holy
		
rank[i] = [
			"Increases total Spirit by 5% and upon death, the priest becomes the Spirit of Redemption for 15 sec.  The Spirit of Redemption cannot move, attack, be attacked or targeted by any spells or effects.  While in this form, the priest can cast any healing spell free of cost.  When the effect ends, the priest dies."
		];

i++;		




//Spiritual Guidance - Holy
		
rank[i] = [
			"Increases spell damage and healing by up to 5% of your total Spirit.",
			"Increases spell damage and healing by up to 10% of your total Spirit.",
			"Increases spell damage and healing by up to 15% of your total Spirit.",
			"Increases spell damage and healing by up to 20% of your total Spirit.",
			"Increases spell damage and healing by up to 25% of your total Spirit."
		];

i++;

//Surge of Light - Holy
rank[i]=[
			"Your spell criticals have a 25% chance to cause your next Smite spell to be instant cast, cost no mana but be incapable of a critical hit. This effect lasts 10 sec.",
			"Your spell criticals have a 50% chance to cause your next Smite spell to be instant cast, cost no mana but be incapable of a critical hit. This effect lasts 10 sec."
			];
i++;	

//Spiritual Healing - Holy

rank[i] = [
			"Increases the amount healed by your healing spells by 2%.",
			"Increases the amount healed by your healing spells by 4%.",
			"Increases the amount healed by your healing spells by 6%.",
			"Increases the amount healed by your healing spells by 8%.",
			"Increases the amount healed by your healing spells by 10%."
		];		

i++;

//Holy Concentration - Holy

rank[i] = [
			"Gives you a 2% chance to enter a Clearcasting state after casting any Flash Heal, Binding Heal, or Greater Heal spell.  The Clearcasting state reduces the mana cost of your next Flash Heal, Binding Heal, or Greater Heal spell by 100%.",
			"Gives you a 4% chance to enter a Clearcasting state after casting any Flash Heal, Binding Heal, or Greater Heal spell.  The Clearcasting state reduces the mana cost of your next Flash Heal, Binding Heal, or Greater Heal spell by 100%.",
			"Gives you a 6% chance to enter a Clearcasting state after casting any Flash Heal, Binding Heal, or Greater Heal spell.  The Clearcasting state reduces the mana cost of your next Flash Heal, Binding Heal, or Greater Heal spell by 100%."			
		];		

i++;	


//Lightwell - Holy

rank[i] = [
			"<span style=text-align:left;float:left;>225 Mana</span><span style=text-align:right;float:right;>40 yd range</span><br><span style=text-align:left;float:left;>1.5 sec cast</span><span style=text-align:right;float:right;>6 min cooldown</span><br>Creates a holy Lightwell.  Members of your raid or party can click the Lightwell to restore 801 health over 6 sec. Any damage taken will cancel the effect.  Lightwell lasts for 3 min or 5 charges.<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 295 Mana, 1164 Health<br>\
			&nbsp;Rank 3: 365 Mana, 1599 Health<br>\
			&nbsp;Rank 4: 445 Mana, 2361 Health"
		];		

i++;	

//Blessed Resilience - Holy
		
rank[i] = [
			"Critical hits made against you have a 20% chance to to prevent you from being critically hit again for 6 sec.",
			"Critical hits made against you have a 40% chance to to prevent you from being critically hit again for 6 sec.",
			"Critical hits made against you have a 60% chance to to prevent you from being critically hit again for 6 sec."						
		];

i++;		

//Empowered Healing - Holy
rank[i]=[
			"Your Greater Heal spell gains an additional 4% and your Flash Heal and Binding Heal gains an additional 2% of your bonus healing effects.",
			"Your Greater Heal spell gains an additional 8% and your Flash Heal and Binding Heal gains an additional 4% of your bonus healing effects.",
			"Your Greater Heal spell gains an additional 12% and your Flash Heal and Binding Heal gains an additional 6% of your bonus healing effects.",
			"Your Greater Heal spell gains an additional 16% and your Flash Heal and Binding Heal gains an additional 8% of your bonus healing effects.",
			"Your Greater Heal spell gains an additional 20% and your Flash Heal and Binding Heal gains an additional 10% of your bonus healing effects."												
			];
i++;			
		
//Circle of Healing - Holy 
rank[i]=[
			"<span style=text-align:left;float:left;>300 Mana</span><span style=text-align:right;float:right;>40 yd range</span><br>Instant cast<br>Heals friendly target and that target's party members within 15 yards of the target for 250 to 274.<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 337 Mana, 292 to 323 Healing<br>\
			&nbsp;Rank 3: 375 Mana, 332 to 367 Healing<br>\
			&nbsp;Rank 4: 412 Mana, 376 to 415 Healing<br>\
			&nbsp;Rank 5: 450 Mana, 409 to 451 Healing<br>"
			];
i++;					
		
//Spirit Tap - Shadow
rank[i]=[
			"Gives you a 20% chance to gain a 100% bonus to your Spirit after killing a target that yields experience or honor.  For the duration, your Mana will regenerate at a 50% rate while casting. Lasts 15 sec.",
			"Gives you a 40% chance to gain a 100% bonus to your Spirit after killing a target that yields experience or honor.  For the duration, your Mana may regenerate at a 50% rate while casting. Lasts 15 sec.",
			"Gives you a 60% chance to gain a 100% bonus to your Spirit after killing a target that yields experience or honor.  For the duration, your Mana may regenerate at a 50% rate while casting. Lasts 15 sec.",
			"Gives you a 80% chance to gain a 100% bonus to your Spirit after killing a target that yields experience or honor.  For the duration, your Mana may regenerate at a 50% rate while casting. Lasts 15 sec.",
			"Gives you a 100% chance to gain a 100% bonus to your Spirit after killing a target that yields experience or honor.  For the duration, your Mana may regenerate at a 50% rate while casting. Lasts 15 sec."
			];
i++;			
			
//Blackout - Shadow
rank[i]=[
			"Gives your Shadow damage spells a 2% chance to stun the target for 3 sec.",
			"Gives your Shadow damage spells a 4% chance to stun the target for 3 sec.",
			"Gives your Shadow damage spells a 6% chance to stun the target for 3 sec.",
			"Gives your Shadow damage spells a 8% chance to stun the target for 3 sec.",
			"Gives your Shadow damage spells a 10% chance to stun the target for 3 sec."
		];

i++;		
		
//Shadow Affinity - Shadow
rank[i]=[
			"Reduces the threat generated by your Shadow spells by 8%.",
			"Reduces the threat generated by your Shadow spells by 16%.",
			"Reduces the threat generated by your Shadow spells by 25%."
		];

i++;		
		
//Improved Shadow Word: Pain - Shadow
rank[i]=[
			"Increases the duration of your Shadow Word: Pain spell by 3 sec.",
			"Increases the duration of your Shadow Word: Pain spell by 6 sec."
		];

i++;		
		
//Shadow Focus - Shadow
rank[i]=[
			"Reduces your target's chance to resist your Shadow spells by 2%.",
			"Reduces your target's chance to resist your Shadow spells by 4%.",
			"Reduces your target's chance to resist your Shadow spells by 6%.",
			"Reduces your target's chance to resist your Shadow spells by 8%.",
			"Reduces your target's chance to resist your Shadow spells by 10%."
		];

i++;		
		
//Improved Psychic Scream - Shadow
rank[i]=[
			"Reduces the cooldown of your Psychic Scream spell by 2 sec.",
			"Reduces the cooldown of your Psychic Scream spell by 4 sec."
		];

i++;		
		
//Improved Mind Blast - Shadow
rank[i]=[
			"Reduces the cooldown of your Mind Blast spell by 0.5 sec.",
			"Reduces the cooldown of your Mind Blast spell by 1 sec.",
			"Reduces the cooldown of your Mind Blast spell by 1.5 sec.",
			"Reduces the cooldown of your Mind Blast spell by 2 sec.",
			"Reduces the cooldown of your Mind Blast spell by 2.5 sec."
		];

i++;		
		
//Mind Flay - Shadow
rank[i]=[
			"<span style=text-align:left;float:left;>45 Mana</span><span style=text-align:right;float:right;>20 yd range</span><br>Channeled<br>Assault the target's mind with Shadow energy, causing 75 damage over 3 sec and slowing their movement speed by 50%.\
			<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 70 Mana, 126 Damage<br>\
			&nbsp;Rank 3: 100 Mana, 186 Damage<br>\
			&nbsp;Rank 4: 135 Mana, 261 Damage<br>\
			&nbsp;Rank 5: 165 Mana, 330 Damage<br>\
			&nbsp;Rank 6: 205 Mana, 426 Damage<br>\
			&nbsp;Rank 7: 230 Mana, 528 Damage"
		];

i++;		
		
//Improved Fade - Shadow
rank[i]=[
			"Decreases the cooldown of your Fade ability by 3 sec.",
			"Decreases the cooldown of your Fade ability by 6 sec."
		];

i++;		
		
//Shadow Reach - Shadow
rank[i]=[
			"Increases the range of your offensive Shadow spells by 10%.",
			"Increases the range of your offensive Shadow spells by 20%."
		];

i++;		
		
		
//Shadow Weaving - Shadow
rank[i]=[
			"Your Shadow damage spells have a 20% chance to cause your target to be vulnerable to Shadow damage. This vulnerability increases the Shadow damage dealt to your target by 2% and lasts 15 sec. Stacks up to 5 times.",
			"Your Shadow damage spells have a 40% chance to cause your target to be vulnerable to Shadow damage. This vulnerability increases the Shadow damage dealt to your target by 2% and lasts 15 sec. Stacks up to 5 times.",
			"Your Shadow damage spells have a 60% chance to cause your target to be vulnerable to Shadow damage. This vulnerability increases the Shadow damage dealt to your target by 2% and lasts 15 sec. Stacks up to 5 times.",
			"Your Shadow damage spells have a 80% chance to cause your target to be vulnerable to Shadow damage. This vulnerability increases the Shadow damage dealt to your target by 2% and lasts 15 sec. Stacks up to 5 times.",
			"Your Shadow damage spells have a 100% chance to cause your target to be vulnerable to Shadow damage. This vulnerability increases the Shadow damage dealt to your target by 2% and lasts 15 sec. Stacks up to 5 times."
		];

i++;				
		
//Silence - Shadow
rank[i]=[
			"<span style=text-align:left;float:left;>225 Mana</span><span style=text-align:right;float:right;>20 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>45 sec cooldown</span><br>Silences the target, preventing them from casting spells for 5 sec."
		];

i++;		
		

		
//Vampiric Embrace
rank[i]=[
			"<span style=text-align:left;float:left;>52 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>10 sec cooldown</span><br>Afflicts your target with Shadow energy that causes all party members to be healed for 15% of any Shadow damage you deal for 1 min."
		];

i++;		


//Improved Vampiric Embrace
rank[i]=[
			"Increases the percentage healed by Vampiric Embrace by an additional 5%.",
			"Increases the percentage healed by Vampiric Embrace by an additional 10%."
		];

i++;		
		
//Focused Mind - Shadow 
rank[i]=[
			"Reduces the mana cost of your Mind Blast, Mind Control and Mind Flay spells by 5%.",
			"Reduces the mana cost of your Mind Blast, Mind Control and Mind Flay spells by 10%.",
			"Reduces the mana cost of your Mind Blast, Mind Control and Mind Flay spells by 15%."
		];

i++;				
		
//Shadow Resilience
rank[i]=[
			"Reduces the chance you'll be critically hit by all spells by 2%.",
			"Reduces the chance you'll be critically hit by all spells by 4%."			
		];

i++;						
		
//Darkness - Shadoww
rank[i]=[
			"Increases your Shadow spell damage by 2%.",
			"Increases your Shadow spell damage by 4%.",
			"Increases your Shadow spell damage by 6%.",
			"Increases your Shadow spell damage by 8%.",
			"Increases your Shadow spell damage by 10%."
		];

i++;		
		
//Shadow Form - Shadoow
rank[i]=[
			"838 Mana<br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>1.5 sec cooldown</span><br>Assume a Shadowform, increasing your Shadow damage by 15% and reducing Physical damage done to you by 15%.  However, you may not cast Holy spells while in this form."
		];
i++;		
		
//Shadow Power - Shadoww
rank[i]=[
			"Increases the critical strike chance of your Mind Blast and Shadow Word: Death spells by 3%.",
			"Increases the critical strike chance of your Mind Blast and Shadow Word: Death spells by 6%.",
			"Increases the critical strike chance of your Mind Blast and Shadow Word: Death spells by 9%.",
			"Increases the critical strike chance of your Mind Blast and Shadow Word: Death spells by 12%.",
			"Increases the critical strike chance of your Mind Blast and Shadow Word: Death spells by 15%."												
		];

i++;				
		
		
//Misery - Shadow 
rank[i] = [
		"Your Shadow Word: Pain, Mind Flay and Vampiric Touch spells also cause the target to take an additional 1% spell damage.",
		"Your Shadow Word: Pain, Mind Flay and Vampiric Touch spells also cause the target to take an additional 2% spell damage.",
		"Your Shadow Word: Pain, Mind Flay and Vampiric Touch spells also cause the target to take an additional 3% spell damage.",
		"Your Shadow Word: Pain, Mind Flay and Vampiric Touch spells also cause the target to take an additional 4% spell damage.",
		"Your Shadow Word: Pain, Mind Flay and Vampiric Touch spells also cause the target to take an additional 5% spell damage."
		];

i++;				

//Vampiric Touch - Shadow 
rank[i]=[
			"<span style=text-align:left;float:left;>325 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>1.5 sec cast<br>\
			Causes 450 Shadow damage over 15 sec to your target and causes all party members to gain mana equal to 5% of any Shadow spell damage you deal.\
			<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 400 Mana, 600 Damage<br>\
			&nbsp;Rank 3: 425 Mana, 650 Damage"
		];		
		
i++;		

//Shadow Talents End^^

