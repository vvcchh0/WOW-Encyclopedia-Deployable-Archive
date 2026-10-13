var i = 0;
var t = 0;

var className = "Druid Talents";
var talentPath = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fglobal%2Ftalents%2Fdruid%2Fdata.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ftalents%2F&reason=external-or-uncollected-resource";

tree[i] = "Balance"; i++;
tree[i] = "Feral Combat"; i++;
tree[i] = "Restoration"; i++;

i = 0;

talent[i] = [0, "Starlight Wrath", 5, 1, 1]; i++;
talent[i] = [0, "Nature's Grasp", 1, 2, 1]; i++;
talent[i] = [0, "Improved Nature's Grasp", 4, 3, 1, [getTalentID("Nature's Grasp"),1]]; i++;
talent[i] = [0, "Control of Nature", 3, 1, 2]; i++; 
talent[i] = [0, "Focused Starlight", 2, 2, 2]; i++;
talent[i] = [0, "Improved Moonfire", 2, 3, 2]; i++;
talent[i] = [0, "Brambles", 3, 1, 3]; i++;
talent[i] = [0, "Insect Swarm", 1, 3, 3]; i++;
talent[i] = [0, "Nature's Reach", 2, 4, 3]; i++;
talent[i] = [0, "Vengeance", 5, 2, 4, [getTalentID("Focused Starlight"),2]]; i++;
talent[i] = [0, "Celestial Focus", 3, 3, 4]; i++;
talent[i] = [0, "Lunar Guidance", 3, 1, 5]; i++;
talent[i] = [0, "Nature's Grace", 1, 2, 5]; i++;
talent[i] = [0, "Moonglow", 3, 3, 5]; i++;
talent[i] = [0, "Moonfury", 5, 2, 6, [getTalentID("Nature's Grace"),1]]; i++;
talent[i] = [0, "Balance of Power", 2, 3, 6]; i++;
talent[i] = [0, "Dreamstate", 3, 1, 7]; i++;
talent[i] = [0, "Moonkin Form", 1, 2, 7]; i++;
talent[i] = [0, "Improved Faerie Fire", 3, 3, 7]; i++;
talent[i] = [0, "Wrath of Cenarius", 5, 2, 8]; i++;
talent[i] = [0, "Force of Nature", 1, 2, 9]; i++;

treeStartStop[t] = i -1;
t++;

//feral combat talents
talent[i] = [1, "Ferocity", 5, 2, 1]; i++;
talent[i] = [1, "Feral Aggression", 5, 3, 1]; i++;
talent[i] = [1, "Feral Instinct", 3, 1, 2]; i++;
talent[i] = [1, "Brutal Impact", 2, 2, 2]; i++;
talent[i] = [1, "Thick Hide", 3, 3, 2]; i++;
talent[i] = [1, "Feral Swiftness", 2, 1, 3]; i++;
talent[i] = [1, "Feral Charge", 1, 2, 3]; i++;
talent[i] = [1, "Sharpened Claws", 3, 3, 3]; i++;
talent[i] = [1, "Shredding Attacks", 2, 1, 4]; i++;
talent[i] = [1, "Predatory Strikes", 3, 2, 4]; i++;
talent[i] = [1, "Primal Fury", 2, 3, 4, [getTalentID("Sharpened Claws"),3]]; i++;
talent[i] = [1, "Savage Fury", 2, 1, 5]; i++;
talent[i] = [1, "Faerie Fire (Feral)", 1, 3, 5]; i++;
talent[i] = [1, "Nurturing Instinct", 2, 4, 5]; i++;
talent[i] = [1, "Heart of the Wild", 5, 2, 6, [getTalentID("Predatory Strikes"),3]]; i++;
talent[i] = [1, "Survival of the Fittest", 3, 3, 6]; i++;
talent[i] = [1, "Primal Tenacity", 3, 1, 7]; i++;
talent[i] = [1, "Leader of the Pack", 1, 2, 7]; i++;
talent[i] = [1, "Improved Leader of the Pack", 2, 3, 7, [getTalentID("Leader of the Pack"),1]]; i++;
talent[i] = [1, "Predatory Instincts", 5, 3, 8]; i++;
talent[i] = [1, "Mangle", 1, 2, 9, [getTalentID("Leader of the Pack"),1]]; i++;

treeStartStop[t] = i -1;
t++;

//restoration talents
talent[i] = [2, "Improved Mark of the Wild", 5, 2, 1]; i++;
talent[i] = [2, "Furor", 5, 3, 1]; i++;
talent[i] = [2, "Naturalist", 5, 1, 2]; i++;
talent[i] = [2, "Nature's Focus", 5, 2, 2]; i++;
talent[i] = [2, "Natural Shapeshifter", 3, 3, 2]; i++;
talent[i] = [2, "Intensity", 3, 1, 3]; i++;
talent[i] = [2, "Subtlety", 5, 2, 3]; i++;
talent[i] = [2, "Omen of Clarity", 1, 3, 3]; i++;
talent[i] = [2, "Tranquil Spirit", 5, 2, 4]; i++;
talent[i] = [2, "Improved Rejuvenation", 3, 3, 4]; i++;
talent[i] = [2, "Nature's Swiftness", 1, 1, 5, [getTalentID("Intensity"),3]]; i++;
talent[i] = [2, "Gift of Nature", 5, 2, 5]; i++;
talent[i] = [2, "Improved Tranquility", 2, 4, 5]; i++;
talent[i] = [2, "Empowered Touch", 2, 1, 6]; i++;
talent[i] = [2, "Improved Regrowth", 5, 3, 6, [getTalentID("Improved Rejuvenation"),3]]; i++;
talent[i] = [2, "Living Spirit", 3, 1, 7]; i++;
talent[i] = [2, "Swiftmend", 1, 2, 7, [getTalentID("Gift of Nature"),5]]; i++;
talent[i] = [2, "Natural Perfection", 3, 3, 7]; i++;
talent[i] = [2, "Empowered Rejuvenation", 5, 2, 8]; i++;
talent[i] = [2, "Tree of Life", 1, 2, 9, [getTalentID("Empowered Rejuvenation"),5]]; i++;

treeStartStop[t] = i -1;
t++;

i = 0;


//Balance Talents Begin

//Starlight Wrath - Balance 
rank[i] = [
"Reduces the cast time of your Wrath and Starfire spells by 0.1 sec.",
"Reduces the cast time of your Wrath and Starfire spells by 0.2 sec.",
"Reduces the cast time of your Wrath and Starfire spells by 0.3 sec.",
"Reduces the cast time of your Wrath and Starfire spells by 0.4 sec.",
"Reduces the cast time of your Wrath and Starfire spells by 0.5 sec."
		];
i++;		
		
//Nature's Grasp - Balance
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>1 min cooldown</span><br>While active, any time an enemy strikes the caster they have a 35% chance to become afflicted by Entangling Roots (Rank 1).  Only useable outdoors. 1 charge. Lasts 45 sec.\
		<br><br>&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: Entangling Roots (Rank 2)<br>\
		&nbsp;Rank 3: Entangling Roots (Rank 3)<br>\
		&nbsp;Rank 4: Entangling Roots (Rank 4)<br>\
		&nbsp;Rank 5: Entangling Roots (Rank 5)<br>\
		&nbsp;Rank 6: Entangling Roots (Rank 6)<br>\
		&nbsp;Rank 7: Entangling Roots (Rank 7)"
		];
i++;		

//Improved Nature's Grasp - Balance
rank[i] = [
"Increases the chance for your Nature's Grasp to entangle an enemy by 15%.",
"Increases the chance for your Nature's Grasp to entangle an enemy by 30%.",
"Increases the chance for your Nature's Grasp to entangle an enemy by 45%.",
"Increases the chance for your Nature's Grasp to entangle an enemy by 65%."
		];
i++;		
		
//Control of Nature - Balance
rank[i] = [
"Gives you a 40% chance to avoid interruption caused by damage while casting Entangling Roots and Cyclone.",
"Gives you a 70% chance to avoid interruption caused by damage while casting Entangling Roots and Cyclone.",
"Gives you a 100% chance to avoid interruption caused by damage while casting Entangling Roots and Cyclone."
		];
i++;		

//Focused Starlight - Balance 
rank[i] = [
"Increases the critical strike chance of your Wrath and Starfire spells by 2%.",
"Increases the critical strike chance of your Wrath and Starfire spells by 4%."
		];
i++;		

//Improved Moonfire - Balance
rank[i] = [
"Increases the damage and critical strike chance of your Moonfire spell by 5%.",
"Increases the damage and critical strike chance of your Moonfire spell by 10%."
		];
i++;		

//Brambles - Balance
rank[i] = [ 
"Increases damage caused by your Thorns and Entangling Roots spells by 25%.",
"Increases damage caused by your Thorns and Entangling Roots spells by 50%.",
"Increases damage caused by your Thorns and Entangling Roots spells by 75%."
		];
i++;		


//Insect Swarm - Balance
rank[i]=[
		"<span style=text-align:left;float:left;>50 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>Instant cast<br>The enemy target is swarmed by insects, decreasing their chance to hit by 2% and causing 108 Nature damage over 12 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 85 Mana, 192 Damage<br>\
		&nbsp;Rank 3: 110 Mana, 300 Damage<br>\
		&nbsp;Rank 4: 135 Mana, 432 Damage<br>\
		&nbsp;Rank 5: 155 Mana, 594 Damage<br>\
		&nbsp;Rank 6: 175 Mana, 792 Damage"
		];
i++;
	

//Nature's Reach - Balance
rank[i] = [
"Increases the range of your Balance spells and Faerie Fire (Feral) ability by 10%.",
"Increases the range of your Balance spells and Faerie Fire (Feral) ability by 20%."
		];
i++;		

//Vengeance - Balance
rank[i] = [
"Increases the critical strike damage bonus of your Starfire, Moonfire, and Wrath spells by 20%.",
"Increases the critical strike damage bonus of your Starfire, Moonfire, and Wrath spells by 40%.",
"Increases the critical strike damage bonus of your Starfire, Moonfire, and Wrath spells by 60%.",
"Increases the critical strike damage bonus of your Starfire, Moonfire, and Wrath spells by 80%.",
"Increases the critical strike damage bonus of your Starfire, Moonfire, and Wrath spells by 100%."
		];
i++;		

//Celestial Focus - Balance  
rank[i] = [
"Gives your Starfire spell a 5% chance to stun the target for 3 sec and increases the chance you'll resist spell interruption when casting your Wrath spell by 25%.",
"Gives your Starfire spell a 10% chance to stun the target for 3 sec and increases the chance you'll resist spell interruption when casting your Wrath spell by 50%.",
"Gives your Starfire spell a 15% chance to stun the target for 3 sec and increases the chance you'll resist spell interruption when casting your Wrath spell by 70%."
		];
i++;

//Lunar Guidance - Balance  
rank[i] = [
"Increases your spell damage and healing by 8% of your total Intellect.",
"Increases your spell damage and healing by 16% of your total Intellect.",
"Increases your spell damage and healing by 25% of your total Intellect."
		];
i++;

//Nature's Grace - Balance
rank[i] = [
		"All spell criticals grace you with a blessing of nature, reducing the casting time of your next spell by 0.5 sec."
		];
i++;		

//Moonglow - Balance
rank[i] = [
"Reduces the Mana cost of your Moonfire, Starfire, Wrath, Healing Touch, Regrowth and Rejuvenation spells by 3%.",
"Reduces the Mana cost of your Moonfire, Starfire, Wrath, Healing Touch, Regrowth and Rejuvenation spells by 6%.",
"Reduces the Mana cost of your Moonfire, Starfire, Wrath, Healing Touch, Regrowth and Rejuvenation spells by 9%."
		];		
i++;		

//Moonfury - Balance  			
rank[i] = [
"Increases the damage done by your Starfire, Moonfire and Wrath spells by 2%.",
"Increases the damage done by your Starfire, Moonfire and Wrath spells by 4%.",
"Increases the damage done by your Starfire, Moonfire and Wrath spells by 6%.",
"Increases the damage done by your Starfire, Moonfire and Wrath spells by 8%.",
"Increases the damage done by your Starfire, Moonfire and Wrath spells by 10%."
		];
i++;		


//Nature's Warrior - Balance  			
rank[i] = [
"Increases your chance to hit with all spells and reduces the chance you'll be hit by spells by 2%.",
"Increases your chance to hit with all spells and reduces the chance you'll be hit by spells by 4%."
		];
i++;


//Dreamstate - Balance  			
rank[i] = [
"Regenerate mana equal to 4% of your Intellect every 5 sec, even while casting.",
"Regenerate mana equal to 7% of your Intellect every 5 sec, even while casting.",
"Regenerate mana equal to 10% of your Intellect every 5 sec, even while casting."
		];
i++;


//Moonkin Form - Balance  
rank[i] = [
		"521 Mana<br><span style=text-align:left;float:left;>Instant cast</span><br>Transforms the Druid into Moonkin Form. While in this form the armor contribution from items is increased by 400%, attack power is increased by 150% of your level and all party members within 30 yards have their spell critical chance increased by 5%. Melee attacks in this form have a chance on hit to regenerate mana based on attack power. The Moonkin can only cast Balance and Remove Curse spells while shapeshifted.<br><br>The act of shapeshifting frees the caster of Polymorph and Movement Impairing effects."
		];
i++;


//Improved Faerie Fire - Balance  			
rank[i] = [
"Your Faerie Fire spell also increases the chance the target will be hit by melee and ranged attacks by 1%.",
"Your Faerie Fire spell also increases the chance the target will be hit by melee and ranged attacks by 2%.",
"Your Faerie Fire spell also increases the chance the target will be hit by melee and ranged attacks by 3%."
		];
i++;


//Twilight's Wrath - Balance  			
rank[i] = [
"Your Starfire spell gains an additional 4% and your Wrath gains an additional 2% of your bonus damage effects.",
"Your Starfire spell gains an additional 8% and your Wrath gains an additional 4% of your bonus damage effects.",
"Your Starfire spell gains an additional 12% and your Wrath gains an additional 6% of your bonus damage effects.",
"Your Starfire spell gains an additional 16% and your Wrath gains an additional 8% of your bonus damage effects.",
"Your Starfire spell gains an additional 20% and your Wrath gains an additional 10% of your bonus damage effects."
		];
i++;

//Force of Nature - Balance  
rank[i] = [
		"<span style=text-align:left;float:left;>284 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>3 min cooldown</span><br>Summons 3 treants to attack the enemy target for 30 sec."
		];
i++;






//Ferocity - Feral 
rank[i] = [
"Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle abilities by 1 Rage or Energy.",
"Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle abilities by 2 Rage or Energy.",
"Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle abilities by 3 Rage or Energy.",
"Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle abilities by 4 Rage or Energy.",
"Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle abilities by 5 Rage or Energy."
		];
i++;

//Feral Aggression - Feral
rank[i] = [
"Increases the Attack Power reduction of your Demoralizing Roar by 8% and the damage caused by your Ferocious Bite by 3%.",
"Increases the Attack Power reduction of your Demoralizing Roar by 16% and the damage caused by your Ferocious Bite by 6%.",
"Increases the Attack Power reduction of your Demoralizing Roar by 24% and the damage caused by your Ferocious Bite by 9%.",
"Increases the Attack Power reduction of your Demoralizing Roar by 32% and the damage caused by your Ferocious Bite by 12%.",
"Increases the Attack Power reduction of your Demoralizing Roar by 40% and the damage caused by your Ferocious Bite by 15%."
		];
i++;

//Feral Instinct - Feral
rank[i] = [
"Increases threat caused in Bear and Dire Bear Form by 5% and reduces the chance enemies have to detect you while Prowling.",
"Increases threat caused in Bear and Dire Bear Form by 10% and reduces the chance enemies have to detect you while Prowling.",
"Increases threat caused in Bear and Dire Bear Form by 15% and reduces the chance enemies have to detect you while Prowling."
		];
i++;		

//Brutal Impact - Feral
rank[i] = [
"Increases the stun duration of your Bash and Pounce abilities by 0.5 sec.",
"Increases the stun duration of your Bash and Pounce abilities by 1 sec."
		];
i++;		

//Thick Hide - Feral 
rank[i] = [
"Increases your Armor contribution from items by 4%.",
"Increases your Armor contribution from items by 7%.",
"Increases your Armor contribution from items by 10%."
		];		
i++;		

//Feral Swiftness - Feral
rank[i] = [
"Increases your movement speed by 15% while outdoors in Cat Form and increases your chance to dodge while in Cat Form, Bear Form and Dire Bear Form by 2%.",
"Increases your movement speed by 30% while outdoors in Cat Form and increases your chance to dodge while in Cat Form, Bear Form and Dire Bear Form by 4%."
		];
i++;		

//Feral Charge - Feral 
rank[i] = [
		"<span style=text-align:left;float:left;>5 Rage</span><span style=text-align:right;float:right;>8-25 yd range</span><br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>15 sec cooldown</span><br>Requires Bear Form, Dire Bear Form<br>Causes you to charge an enemy, immobilizing and interrupting any spell being cast for 4 sec."
		];
i++;		

//Sharpened Claws - Feral  
rank[i] = [
"Increases your critical strike chance while in Bear, Dire Bear or Cat Form by 2%.",
"Increases your critical strike chance while in Bear, Dire Bear or Cat Form by 4%.",
"Increases your critical strike chance while in Bear, Dire Bear or Cat Form by 6%."
		];
i++;		

//Shredding Attacks - Feral 
rank[i] = [
"Reduces the energy cost of your Shred ability by 9 and the rage cost of your Lacerate ability by 1.",
"Reduces the energy cost of your Shred ability by 18 and the rage cost of your Lacerate ability by 2."
		];
i++;		

//Predatory Strikes - Feral  
rank[i] = [
"Increases your melee attack power in Cat, Bear, Dire Bear and Moonkin Forms by 50% of your level.",
"Increases your melee attack power in Cat, Bear, Dire Bear and Moonkin Forms by 100% of your level.",
"Increases your melee attack power in Cat, Bear, Dire Bear and Moonkin Forms by 150% of your level."
		];
i++;				
	
//Primal Fury - Feral 
rank[i] = [
"Gives you a 50% chance to gain an additional 5 Rage anytime you get a critical strike while in Bear and Dire Bear Form and your critical strikes from Cat Form abilities that add combo points have a 50% chance to add an additional combo point.",
"Gives you a 100% chance to gain an additional 5 Rage anytime you get a critical strike while in Bear and Dire Bear Form and your critical strikes from Cat Form abilities that add combo points have a 100% chance to add an additional combo point."
		];
i++;		

//Savage Fury - Feral 
rank[i] = [
		"Increases the damage caused by your Claw, Rake and Mangle (Cat) abilities by 10%.",
		"Increases the damage caused by your Claw, Rake and Mangle (Cat) abilities by 20%."		
		];
i++;		
		
//Faerie Fire (Feral) - Feral 

rank[i] = [
		"30 yd range<br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>6 sec cooldown</span><br>Requires Cat Form, Bear Form, Dire Bear Form<br>Decrease the armor of the target by 175 for 40 sec. While affected, the target cannot stealth or turn invisible.\
		<br><br>&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: -285 Armor<br>\
		&nbsp;Rank 3: -395 Armor<br>\
		&nbsp;Rank 4: -505 Armor<br>\
		&nbsp;Rank 5: -610 Armor"
		];
i++;

//Nurturing Instinct - Feral
rank[i]=[
"Increases your healing spells by up to 25% of your Strength.",
"Increases your healing spells by up to 50% of your Strength."
		];
i++;		


	
//Heart of the Wild - Feral
rank[i]=[
"Increases your Intellect by 4%. In addition, while in Bear or Dire Bear Form your Stamina is increased by 4% and while in Cat Form your attack power is increased by 2%.",
"Increases your Intellect by 8%. In addition, while in Bear or Dire Bear Form your Stamina is increased by 8% and while in Cat Form your attack power is increased by 4%.",
"Increases your Intellect by 12%. In addition, while in Bear or Dire Bear Form your Stamina is increased by 12% and while in Cat Form your attack power is increased by 6%.",
"Increases your Intellect by 16%. In addition, while in Bear or Dire Bear Form your Stamina is increased by 16% and while in Cat Form your attack power is increased by 8%.",
"Increases your Intellect by 20%. In addition, while in Bear or Dire Bear Form your Stamina is increased by 20% and while in Cat Form your attack power is increased by 10%."
		];
i++;

//Survival of the Fittest - Feral
rank[i]=[
"Increases all attributes by 1% and reduces the chance you'll be critically hit by melee attacks by 1%.",
"Increases all attributes by 2% and reduces the chance you'll be critically hit by melee attacks by 2%.",
"Increases all attributes by 3% and reduces the chance you'll be critically hit by melee attacks by 3%."
		];
i++;

//Primal Tenacity - Feral
rank[i]=[
"Increases your chance to resist Stun and Fear mechanics by 5%.",
"Increases your chance to resist Stun and Fear mechanics by 10%.",
"Increases your chance to resist Stun and Fear mechanics by 15%."
		];
i++;

//Leader of the Pack - Feral
rank[i]=[
"While in Cat, Bear or Dire Bear Form, the Leader of the Pack increases ranged and melee critical chance of all party members within 45 yards by 5%."
		];
i++;

//Improved Leader of the Pack - Feral
rank[i]=[
"Your Leader of the Pack ability also causes affected targets to have a 100% chance to heal themselves for 2% of their total health when they critically hit with a melee or ranged attack. The healing effect cannot occur more than once every 6 sec.",
"Your Leader of the Pack ability also causes affected targets to have a 100% chance to heal themselves for 4% of their total health when they critically hit with a melee or ranged attack. The healing effect cannot occur more than once every 6 sec."
		];
i++;

//Predatory Instincts - Feral
rank[i]=[
"While in Cat Form, Bear Form, or Dire Bear Form, increases your damage from melee critical strikes by 2% and your chance to avoid area effect attacks by 3%.",
"While in Cat Form, Bear Form, or Dire Bear Form, increases your damage from melee critical strikes by 4% and your chance to avoid area effect attacks by 6%.",
"While in Cat Form, Bear Form, or Dire Bear Form, increases your damage from melee critical strikes by 6% and your chance to avoid area effect attacks by 9%.",
"While in Cat Form, Bear Form, or Dire Bear Form, increases your damage from melee critical strikes by 8% and your chance to avoid area effect attacks by 12%.",
"While in Cat Form, Bear Form, or Dire Bear Form, increases your damage from melee critical strikes by 10% and your chance to avoid area effect attacks by 15%."
		];
i++;

//Mangle - Feral
rank[i]=[
"Mangle the target, inflicting damage and causing the target to take additional damage from bleed effects for 12 sec. This ability can be used in Cat Form or Dire Bear Form.\
		<br><br>&nbsp;Bear Form:<br>\
		&nbsp;20 Rage, Melee range, Instant, 6 sec cooldown, 1.5 sec global cooldown.<br>\
		&nbsp;115% normal damage plus x, and 30% additional damage from Shred and bleed effects for 12 sec.<br>\
		&nbsp;Rank 1: +86<br>\
		&nbsp;Rank 2: +121<br>\
		&nbsp;Rank 3: +155\
		<br><br>&nbsp;Cat Form:<br>\
		&nbsp;45 Energy, Melee range, Instant, Awards 1 combo point.<br>\
		&nbsp;160% damage plus x, and 30% additional damage from Shred and bleed effects for 12 sec.<br>\
		&nbsp;Rank 1: +158<br>\
		&nbsp;Rank 2: +205<br>\
		&nbsp;Rank 3: +264"


		];
i++;



		
//Improved Mark of the Wild - Restoration
rank[i]=[
"Increases the effects of your Mark of the Wild and Gift of the Wild spells by 7%.",
"Increases the effects of your Mark of the Wild and Gift of the Wild spells by 14%.",
"Increases the effects of your Mark of the Wild and Gift of the Wild spells by 21%.",
"Increases the effects of your Mark of the Wild and Gift of the Wild spells by 28%.",
"Increases the effects of your Mark of the Wild and Gift of the Wild spells by 35%."
		];
i++;		
		
//Furor - Restoration
rank[i]=[
"Gives you 20% chance to gain 10 Rage when you shapeshift into Bear and Dire Bear Form or 40 Energy when you shapeshift into Cat Form.",
"Gives you 40% chance to gain 10 Rage when you shapeshift into Bear and Dire Bear Form or 40 Energy when you shapeshift into Cat Form.",
"Gives you 60% chance to gain 10 Rage when you shapeshift into Bear and Dire Bear Form or 40 Energy when you shapeshift into Cat Form.",
"Gives you 80% chance to gain 10 Rage when you shapeshift into Bear and Dire Bear Form or 40 Energy when you shapeshift into Cat Form.",
"Gives you 100% chance to gain 10 Rage when you shapeshift into Bear and Dire Bear Form or 40 Energy when you shapeshift into Cat Form."
		];
i++;		

//Naturalist - Restoration
rank[i]=[
"Reduces the cast time of your Healing Touch spell by 0.1 sec and increases the damage you deal with physical attacks in all forms by 2%.",
"Reduces the cast time of your Healing Touch spell by 0.2 sec and increases the damage you deal with physical attacks in all forms by 4%.",
"Reduces the cast time of your Healing Touch spell by 0.3 sec and increases the damage you deal with physical attacks in all forms by 6%.",
"Reduces the cast time of your Healing Touch spell by 0.4 sec and increases the damage you deal with physical attacks in all forms by 8%.",
"Reduces the cast time of your Healing Touch spell by 0.5 sec and increases the damage you deal with physical attacks in all forms by 10%."
		];
i++;		
		
//Nature's Focus - Restoration 
rank[i]=[
"Gives you a 14% chance to avoid interruption caused by damage while casting the Healing Touch, Regrowth and Tranquility spells.",
"Gives you a 28% chance to avoid interruption caused by damage while casting the Healing Touch, Regrowth and Tranquility spells.",
"Gives you a 42% chance to avoid interruption caused by damage while casting the Healing Touch, Regrowth and Tranquility spells.",
"Gives you a 56% chance to avoid interruption caused by damage while casting the Healing Touch, Regrowth and Tranquility spells.",
"Gives you a 70% chance to avoid interruption caused by damage while casting the Healing Touch, Regrowth and Tranquility spells."
		];
i++;		
	
//Natural Shapeshifter - Balance 
rank[i] = [
"Reduces the mana cost of all shapeshifting by 10%.",
"Reduces the mana cost of all shapeshifting by 20%.",
"Reduces the mana cost of all shapeshifting by 30%."
		];		
i++;		
		
//Intensity - Restoration 
rank[i]=[
"Allows 10% of your Mana regeneration to continue while casting and causes your Enrage ability to instantly generate 4 rage.",
"Allows 20% of your Mana regeneration to continue while casting and causes your Enrage ability to instantly generate 7 rage.",
"Allows 30% of your Mana regeneration to continue while casting and causes your Enrage ability to instantly generate 10 rage."
		];
i++;

//Subtlety - Restoration 
rank[i]=[
"Reduces the threat generated by your spells by 4% and reduces the chance your spells will be dispelled by 6%.",
"Reduces the threat generated by your spells by 8% and reduces the chance your spells will be dispelled by 12%.",
"Reduces the threat generated by your spells by 12% and reduces the chance your spells will be dispelled by 18%.",
"Reduces the threat generated by your spells by 16% and reduces the chance your spells will be dispelled by 24%.",
"Reduces the threat generated by your spells by 20% and reduces the chance your spells will be dispelled by 30%."
		];
i++;
		
//Omen of Clarity - Balance 
rank[i] = [
		"120 Mana<br><span style=text-align:left;float:left;>Instant cast</span><br>Imbues the Druid with natural energy. Each of the Druid's melee attacks has a chance of causing the caster to enter a Clearcasting state. The Clearcasting state reduces the Mana, Rage or Energy cost of your next damage or healing spell or offensive ability by 100%. Lasts 30 min."
		];
i++;
		
//Tranquil Spirit - Restoration  
rank[i]=[
"Reduces the mana cost of your Healing Touch and Tranquility spells by 2%.",
"Reduces the mana cost of your Healing Touch and Tranquility spells by 4%.",
"Reduces the mana cost of your Healing Touch and Tranquility spells by 6%.",
"Reduces the mana cost of your Healing Touch and Tranquility spells by 8%.",
"Reduces the mana cost of your Healing Touch and Tranquility spells by 10%."
		];
i++;		
		
//Improved Rejuvenation - Restoration   
rank[i]=[
"Increases the effect of your Rejuvenation spell by 5%.",
"Increases the effect of your Rejuvenation spell by 10%.",
"Increases the effect of your Rejuvenation spell by 15%."
		];
i++;	
		
//Nature's Swiftness - Restoration   
rank[i]=[
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, your next Nature spell becomes an instant cast spell."
		];
i++;	


//Gift of Nature - Restoration 
rank[i]=[
"Increases the effect of all healing spells by 2%.",
"Increases the effect of all healing spells by 4%.",
"Increases the effect of all healing spells by 6%.",
"Increases the effect of all healing spells by 8%.",
"Increases the effect of all healing spells by 10%."
		];
i++;	


//Improved Tranquility - Restoration
rank[i]=[
"Reduces threat caused by Tranquility by 50%.",
"Reduces threat caused by Tranquility by 100%."
		];
i++;	


//Empowered Touch - Restoration
rank[i]=[
"Your Healing Touch spell gains an additional 10% of your bonus healing effects.",
"Your Healing Touch spell gains an additional 20% of your bonus healing effects."
		];
i++;	


//Improved Regrowth - Restoration 
rank[i]=[
"Increases the critical effect chance of your Regrowth spell by 10%.",
"Increases the critical effect chance of your Regrowth spell by 20%.",
"Increases the critical effect chance of your Regrowth spell by 30%.",
"Increases the critical effect chance of your Regrowth spell by 40%.",
"Increases the critical effect chance of your Regrowth spell by 50%."
		];
i++;

//Living Spirit - Restoration 
rank[i]=[
"Increases your total Spirit by 5%.",
"Increases your total Spirit by 10%.",
"Increases your total Spirit by 15%."
		];
i++;	

//Swiftmend - Restoration 
rank[i]=[
		"<span style=text-align:left;float:left;>379 Mana</span><span style=text-align:right;float:right;>40 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>15 sec cooldown</span><br>Consumes a Rejuvenation or Regrowth effect on a friendly target to instantly heal them an amount equal to 12 sec. of Rejuvenation or 18 sec. of Regrowth."
		];
i++;


//Natural Perfection - Restoration 
rank[i]=[
"Your critical strike chance with all spells is increased by 1% and critical strikes against you give you the Natural Perfection effect reducing all damage taken by 2%.  Stacks up to 3 times.  Lasts 8 sec.",
"Your critical strike chance with all spells is increased by 2% and critical strikes against you give you the Natural Perfection effect reducing all damage taken by 3%.  Stacks up to 3 times.  Lasts 8 sec.",
"Your critical strike chance with all spells is increased by 3% and critical strikes against you give you the Natural Perfection effect reducing all damage taken by 4%.  Stacks up to 3 times.  Lasts 8 sec."
		];
i++;

//Empowered Rejuvenation - Restoration 
rank[i]=[
"The bonus healing effects of your healing over time spells is increased by 4%.",
"The bonus healing effects of your healing over time spells is increased by 8%.",
"The bonus healing effects of your healing over time spells is increased by 12%.",
"The bonus healing effects of your healing over time spells is increased by 16%.",
"The bonus healing effects of your healing over time spells is increased by 20%."
		];
i++;

//Tree of Life - Restoration 
rank[i]=[
		"<span>663 Mana</span><br><span>Instant cast</span><br>Transforms the Druid into the Tree of Life Form.  While in this form you increase healing received by 25% of your total Spirit for all party members within 45 yards, your movement speed is reduced by 20%, and you can only cast Swiftmend, Innervate, Nature's Swiftness, Rebirth, poison removing and healing over time spells, but the mana cost of these spells is reduced by 20%.<br><br>The act of shapeshifting frees the caster of Polymorph and Movement Impairing effects."
		];
i++;
	
//Restoration Talents End^^

