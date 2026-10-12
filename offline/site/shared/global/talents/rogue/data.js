var i = 0;
var t = 0;

var className = "Rogue Talents";
var talentPath = "/info/basics/talents/";

tree[i] = "Assassination"; i++;
tree[i] = "Combat"; i++;
tree[i] = "Subtlety"; i++;

i = 0;

talent[i] = [0, "Improved Eviscerate", 3, 1, 1]; i++;
talent[i] = [0, "Remorseless Attacks", 2, 2, 1]; i++;
talent[i] = [0, "Malice", 5, 3, 1]; i++;
talent[i] = [0, "Ruthlessness", 3, 1, 2]; i++; 
talent[i] = [0, "Murder", 2, 2, 2]; i++;
talent[i] = [0, "Puncturing Wounds", 3, 4, 2]; i++;
talent[i] = [0, "Relentless Strikes", 1, 1, 3]; i++;
talent[i] = [0, "Improved Expose Armor", 2, 2, 3]; i++;
talent[i] = [0, "Lethality", 5, 3, 3, [getTalentID("Malice"),5]]; i++;
talent[i] = [0, "Vile Poisons", 5, 2, 4]; i++;
talent[i] = [0, "Improved Poisons", 5, 3, 4]; i++;
talent[i] = [0, "Fleet Footed", 2, 1, 5]; i++;
talent[i] = [0, "Cold Blood", 1, 2, 5]; i++;
talent[i] = [0, "Improved Kidney Shot", 3, 3, 5]; i++;
talent[i] = [0, "Quick Recovery", 2, 4, 5]; i++;
talent[i] = [0, "Seal Fate", 5, 2, 6, [getTalentID("Cold Blood"),1]]; i++;
talent[i] = [0, "Master Poisoner", 2, 3, 6]; i++;
talent[i] = [0, "Vigor", 1, 2, 7]; i++;
talent[i] = [0, "Deadened Nerves", 5, 3, 7]; i++;
talent[i] = [0, "Find Weakness", 5, 3, 8]; i++;
talent[i] = [0, "Mutilate", 1, 2, 9, [getTalentID("Vigor"),1]]; i++;

treeStartStop[t] = i -1;
t++;

//holy talents
talent[i] = [1, "Improved Gouge", 3, 1, 1]; i++;
talent[i] = [1, "Improved Sinister Strike", 2, 2, 1]; i++;
talent[i] = [1, "Lightning Reflexes", 5, 3, 1]; i++;
talent[i] = [1, "Improved Slice and Dice", 3, 1, 2]; i++;
talent[i] = [1, "Deflection", 5, 2, 2]; i++;
talent[i] = [1, "Precision", 5, 3, 2]; i++;
talent[i] = [1, "Endurance", 2, 1, 3]; i++;
talent[i] = [1, "Riposte", 1, 2, 3, [getTalentID("Deflection"),5]]; i++;
talent[i] = [1, "Improved Sprint", 2, 4, 3]; i++;
talent[i] = [1, "Improved Kick", 2, 1, 4]; i++;
talent[i] = [1, "Dagger Specialization", 5, 2, 4]; i++;
talent[i] = [1, "Dual Wield Specialization", 5, 3, 4, [getTalentID("Precision"),5]]; i++;
talent[i] = [1, "Mace Specialization", 5, 1, 5]; i++;
talent[i] = [1, "Blade Flurry", 1, 2, 5]; i++;
talent[i] = [1, "Sword Specialization", 5, 3, 5]; i++;
talent[i] = [1, "Fist Weapon Specialization", 5, 4, 5]; i++;
talent[i] = [1, "Blade Twisting", 2, 1, 6]; i++;
talent[i] = [1, "Weapon Expertise", 2, 2, 6, [getTalentID("Blade Flurry"),1]]; i++;
talent[i] = [1, "Aggression", 3, 3, 6]; i++;
talent[i] = [1, "Vitality", 2, 1, 7]; i++;
talent[i] = [1, "Adrenaline Rush", 1, 2, 7]; i++;
talent[i] = [1, "Nerves of Steel", 2, 3, 7]; i++;
talent[i] = [1, "Combat Potency", 5, 3, 8]; i++;
talent[i] = [1, "Surprise Attacks", 1, 2, 9, [getTalentID("Adrenaline Rush"),1]]; i++;

treeStartStop[t] = i -1;
t++;

//shadow talents
talent[i] = [2, "Master of Deception", 5, 2, 1]; i++;
talent[i] = [2, "Opportunity", 5, 3, 1]; i++;
talent[i] = [2, "Sleight of Hand", 2, 1, 2]; i++;
talent[i] = [2, "Dirty Tricks", 2, 2, 2]; i++;
talent[i] = [2, "Camouflage", 5, 3, 2]; i++;
talent[i] = [2, "Initiative", 3, 1, 3]; i++;
talent[i] = [2, "Ghostly Strike", 1, 2, 3]; i++;
talent[i] = [2, "Improved Ambush", 3, 3, 3]; i++;
talent[i] = [2, "Setup", 3, 1, 4]; i++;
talent[i] = [2, "Elusiveness", 2, 2, 4]; i++;
talent[i] = [2, "Serrated Blades", 3, 3, 4]; i++;
talent[i] = [2, "Heightened Senses", 2, 1, 5]; i++;
talent[i] = [2, "Preparation", 1, 2, 5]; i++;
talent[i] = [2, "Dirty Deeds", 2, 3, 5]; i++;
talent[i] = [2, "Hemorrhage", 1, 4, 5, [getTalentID("Serrated Blades"),3]]; i++;
talent[i] = [2, "Master of Subtlety", 3, 1, 6]; i++;
talent[i] = [2, "Deadliness", 5, 3, 6]; i++;
talent[i] = [2, "Enveloping Shadows", 3, 1, 7]; i++;
talent[i] = [2, "Premeditation", 1, 2, 7, [getTalentID("Preparation"),1]]; i++;
talent[i] = [2, "Cheat Death", 3, 3, 7]; i++;
talent[i] = [2, "Sinister Calling", 5, 2, 8, [getTalentID("Premeditation"),1]]; i++;
talent[i] = [2, "Shadowstep", 1, 2, 9]; i++;

treeStartStop[t] = i -1;
t++;

i = 0;


//Assassination Talents Begin

//Improved Eviscerate - Assassination
rank[i] = [
"Increases the damage done by your Eviscerate ability by 5%.",
"Increases the damage done by your Eviscerate ability by 10%.",
"Increases the damage done by your Eviscerate ability by 15%."
		];
i++;		
		
//Remorseless Attacks - Assassination
rank[i] = [
"After killing an opponent that yields experience or honor, gives you a 20% increased critical strike chance on your next Sinister Strike, Backstab, Mutilate, Hemorrhage, Ambush, or Ghostly Strike. Lasts 20 sec.",
"After killing an opponent that yields experience or honor, gives you a 40% increased critical strike chance on your next Sinister Strike, Backstab, Mutilate, Hemorrhage, Ambush, or Ghostly Strike. Lasts 20 sec."
		];
i++;		

//Malice - Assassination	
rank[i] = [
"Increases your critical strike chance by 1%.",
"Increases your critical strike chance by 2%.",
"Increases your critical strike chance by 3%.",
"Increases your critical strike chance by 4%.",
"Increases your critical strike chance by 5%."
		];
i++;		
		
//Ruthlessness - Assassination	
rank[i] = [
"Gives your melee finishing moves a 20% chance to add a combo point to your target.",
"Gives your melee finishing moves a 40% chance to add a combo point to your target.",
"Gives your melee finishing moves a 60% chance to add a combo point to your target."
		];
i++;		

//Murder - Assassination
rank[i] = [
"Increases all damage caused against Humanoid, Giant, Beast, and Dragonkin targets by 1%",
"Increases all damage caused against Humanoid, Giant, Beast, and Dragonkin targets by 2%"
		];
i++;		

//Puncturing Wounds - Assassination
rank[i] = [
"Increases the critical strike chance of your Backstab ability by 10%, and the critical strike chance of your Mutilate ability by 5%.",
"Increases the critical strike chance of your Backstab ability by 20%, and the critical strike chance of your Mutilate ability by 10%.",
"Increases the critical strike chance of your Backstab ability by 30%, and the critical strike chance of your Mutilate ability by 15%."
		];
i++;		
		
//Relentless Strikes - Assassination  	
rank[i] = [
"Your finishing moves have a 20% chance per combo point to restore 25 energy."
		];
i++;		


//Improved Expose Armor - Assassination	
rank[i] = [ 
"Increases the armor reduced by your Expose Armor ability by 25%.",
"Increases the armor reduced by your Expose Armor ability by 50%."
		];
i++;		

//Lethality - Assassination
rank[i] = [
"Increases the critical strike damage bonus of your Sinister Strike, Gouge, Backstab, Ghostly Strike, Mutilate, Shiv, and Hemorrhage abilites by 6%.",
"Increases the critical strike damage bonus of your Sinister Strike, Gouge, Backstab, Ghostly Strike, Mutilate, Shiv, and Hemorrhage abilites by 12%.",
"Increases the critical strike damage bonus of your Sinister Strike, Gouge, Backstab, Ghostly Strike, Mutilate, Shiv, and Hemorrhage abilites by 18%.",
"Increases the critical strike damage bonus of your Sinister Strike, Gouge, Backstab, Ghostly Strike, Mutilate, Shiv, and Hemorrhage abilites by 24%.",
"Increases the critical strike damage bonus of your Sinister Strike, Gouge, Backstab, Ghostly Strike, Mutilate, Shiv, and Hemorrhage abilites by 30%."
		];
i++;		

//Vile Poisons - Assassination
rank[i] = [
"Increases the damage dealt by your poisons and Envenom ability by 4% and gives your poisons an additional 8% chance to resist dispel effects.",
"Increases the damage dealt by your poisons and Envenom ability by 8% and gives your poisons an additional 16% chance to resist dispel effects.",
"Increases the damage dealt by your poisons and Envenom ability by 12% and gives your poisons an additional 24% chance to resist dispel effects.",
"Increases the damage dealt by your poisons and Envenom ability by 16% and gives your poisons an additional 32% chance to resist dispel effects.",
"Increases the damage dealt by your poisons and Envenom ability by 20% and gives your poisons an additional 40% chance to resist dispel effects."
		];
i++;		

//Improved Poisons - Assassination	
rank[i] = [
"Increases the chance to apply poisons to your target by 2%.",
"Increases the chance to apply poisons to your target by 4%.",
"Increases the chance to apply poisons to your target by 6%.",
"Increases the chance to apply poisons to your target by 8%.",
"Increases the chance to apply poisons to your target by 10%."
		];
i++;		

//Fleet Footed - Assassination	
rank[i] = [
"Increases your chance to resist movement impairing effects by 5% and increases your movement speed by 8%. This does not stack with other movement speed increasing effects.",
"Increases your chance to resist movement impairing effects by 10% and increases your movement speed by 15%. This does not stack with other movement speed increasing effects."
		];
i++;

//Cold Blood - Assassination
rank[i] = [
			"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, increases the critical strike chance of your next offensive ability by 100%."
		];
i++;		

//Improved Kidney Shot - Assassination
rank[i] = [
"While affected by your Kidney Shot ability, target receives an additional 3% damage from all sources.",
"While affected by your Kidney Shot ability, target receives an additional 6% damage from all sources.",
"While affected by your Kidney Shot ability, target receives an additional 9% damage from all sources."
		];
i++;		

//Quick Recovery - Assassination
rank[i] = [
"All healing effects on you are increased by 10%. In addition, your finishing moves cost 40% less Energy when they fail to hit.",
"All healing effects on you are increased by 20%. In addition, your finishing moves cost 80% less Energy when they fail to hit."
		];
i++;		

//Seal Fate - Assassination		
rank[i] = [
"Your critical strikes from abilities that add combo points have a 20% chance to add an additional combo point.",
"Your critical strikes from abilities that add combo points have a 40% chance to add an additional combo point.",
"Your critical strikes from abilities that add combo points have a 60% chance to add an additional combo point.",
"Your critical strikes from abilities that add combo points have a 80% chance to add an additional combo point.",
"Your critical strikes from abilities that add combo points have a 100% chance to add an additional combo point."
		];
i++;		

//Master Poisoner - Assassination
rank[i] = [
"Reduces the chance your poisons will be resisted by 5% and increases your chance to resist Poison effects by an additional 15%.",
"Reduces the chance your poisons will be resisted by 10% and increases your chance to resist Poison effects by an additional 30%."
		];
i++;		

//Vigor - Assassination
rank[i] = [
"Increases your maximum Energy by 10."
		];
i++;		

//Deadened Nerves - Assassination
rank[i] = [
"Decreases all physical damage taken by 1%.",
"Decreases all physical damage taken by 2%.",
"Decreases all physical damage taken by 3%.",
"Decreases all physical damage taken by 4%.",
"Decreases all physical damage taken by 5%."
		];
i++;		

//Find Weakness - Assassination
rank[i] = [
"Your finishing moves increase the damage of all offensive abilities by 2% for 10 sec.",
"Your finishing moves increase the damage of all offensive abilities by 4% for 10 sec.",
"Your finishing moves increase the damage of all offensive abilities by 6% for 10 sec.",
"Your finishing moves increase the damage of all offensive abilities by 8% for 10 sec.",
"Your finishing moves increase the damage of all offensive abilities by 10% for 10 sec."
		];
i++;		


//Mutilate - Assassination
rank[i] = [
			"<span style=text-align:left;float:left;>60 Energy</span><span style=text-align:right;float:right;>Melee range</span><br>Instant<br>Requires Daggers<br>Instantly attacks with both weapons for an additional 44 with each weapon. Damage is increased by 50% against Poisoned targets. Must be behind the target. Awards 2 combo points.<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 63 with each weapon<br>\
			&nbsp;Rank 3: 88 with each weapon<br>\
			&nbsp;Rank 4: 101 with each weapon"
		];
i++;		






//Improved Gouge - Combat
rank[i] = [
"Increases the effect duration of your Gouge ability by 0.5 sec.",
"Increases the effect duration of your Gouge ability by 1 sec.",
"Increases the effect duration of your Gouge ability by 1.5 sec."
		];
i++;		

//Improved Sinister Strike - Combat 
rank[i] = [
"Reduces the Energy cost of your Sinister Strike ability by 3.",
"Reduces the Energy cost of your Sinister Strike ability by 5."
		];
i++;		

//Lightning Reflexes - Combat
rank[i] = [
"Increases your Dodge chance by 1%.",
"Increases your Dodge chance by 2%.",
"Increases your Dodge chance by 3%.",
"Increases your Dodge chance by 4%.",
"Increases your Dodge chance by 5%."
		];
i++;		

//Improved Slice and Dice - Assassination
rank[i] = [
"Increases the duration of your Slice and Dice ability by 15%.",
"Increases the duration of your Slice and Dice ability by 30%.",
"Increases the duration of your Slice and Dice ability by 45%."

		];
i++;		
	
//Deflection - Combat	
rank[i] = [
"Increases your Parry chance by 1%.",
"Increases your Parry chance by 2%.",
"Increases your Parry chance by 3%.",
"Increases your Parry chance by 4%.",
"Increases your Parry chance by 5%."
		];
i++;		

//Precision - Combat 
rank[i] = [
"Increases your chance to hit with weapons by 1%.",
"Increases your chance to hit with weapons by 2%.",
"Increases your chance to hit with weapons by 3%.",
"Increases your chance to hit with weapons by 4%.",
"Increases your chance to hit with weapons by 5%."
		];
i++;		

//Endurance - Combat
rank[i] = [
"Reduces the cooldown of your Sprint and Evasion abilities by 45 sec",
"Reduces the cooldown of your Sprint and Evasion abilities by 1.5 min."
		];
i++;		

//Riposte - Combat
rank[i] = [
			"<span style=text-align:left;float:left;>10 Energy</span><span style=text-align:right;float:right;>Melee range</span><br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>6 sec cooldown</span><br>A strike that becomes active after parrying an opponent's attack. This attack deals 150% weapon damage and disarms the target for 6 sec."
		];
i++;		

//Improved Sprint - Combat
rank[i] = [
"Gives a 50% chance to remove all movement imparing effects when you activate your Sprint ability.",
"Gives a 100% chance to remove all movement imparing effects when you activate your Sprint ability."
		];
i++;		

//Improved Kick - Combat 
rank[i] = [
"Gives your Kick ability a 50% chance to silence the target for 2 sec.",
"Gives your Kick ability a 100% chance to silence the target for 2 sec."
		];
i++;		

//Dagger Specialization - Combat  
rank[i] = [
"Increases your chance to get a critical strike with Daggers by 1%.",
"Increases your chance to get a critical strike with Daggers by 2%.",
"Increases your chance to get a critical strike with Daggers by 3%.",
"Increases your chance to get a critical strike with Daggers by 4%.",
"Increases your chance to get a critical strike with Daggers by 5%."
		];
i++;		


//Dual Wield Specialization - Combat  
rank[i] = [
"Increases the damage done by your offhand weapon by 10%.",
"Increases the damage done by your offhand weapon by 20%.",
"Increases the damage done by your offhand weapon by 30%.",
"Increases the damage done by your offhand weapon by 40%.",
"Increases the damage done by your offhand weapon by 50%."
		];
i++;		

//Mace Specialization - Combat 
rank[i] = [
"Increases the damage dealt by your critical strikes with maces by 1%, and gives you a 1% chance to stun your target for 3 sec with a mace.",
"Increases the damage dealt by your critical strikes with maces by 2%, and gives you a 2% chance to stun your target for 3 sec with a mace.",
"Increases the damage dealt by your critical strikes with maces by 3%, and gives you a 3% chance to stun your target for 3 sec with a mace.",
"Increases the damage dealt by your critical strikes with maces by 4%, and gives you a 4% chance to stun your target for 3 sec with a mace.",
"Increases the damage dealt by your critical strikes with maces by 5%, and gives you a 6% chance to stun your target for 3 sec with a mace."
		];
i++;
		
//Blade Flurry - Combat  
rank[i]=[
			"25 Energy<br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>2 min cooldown</span><br>Increases your attack speed by 20%. In addition, attacks strike an additional nearby opponent. Lasts 15 sec."
			];
i++;			
			
//Sword Specialization - Combat
rank[i]=[
"Gives you a 1% chance to get an extra attack on the same target after dealing damage with your Sword.",
"Gives you a 2% chance to get an extra attack on the same target after dealing damage with your Sword.",
"Gives you a 3% chance to get an extra attack on the same target after dealing damage with your Sword.",
"Gives you a 4% chance to get an extra attack on the same target after dealing damage with your Sword.",
"Gives you a 5% chance to get an extra attack on the same target after dealing damage with your Sword."
		];
i++;		
		
//Fist Weapon Specialization - Combat 
rank[i]=[
"Increases your chance to get a critical strike with Fist Weapons by 1%.",
"Increases your chance to get a critical strike with Fist Weapons by 2%.",
"Increases your chance to get a critical strike with Fist Weapons by 3%.",
"Increases your chance to get a critical strike with Fist Weapons by 4%.",
"Increases your chance to get a critical strike with Fist Weapons by 5%."
		];
i++;

//Blade Twisting - Combat 
rank[i]=[
"Gives your Sinister Strike, Backstab, Gouge and Shiv abilities a 10% chance to Daze the target for 8 sec.",
"Gives your Sinister Strike, Backstab, Gouge and Shiv abilities a 20% chance to Daze the target for 8 sec."
];
i++;

//Weapon Expertise - Combat 
rank[i]=[
"Increases your expertise by 5.",
"Increases your expertise by 10."
		];
i++;		

//Aggression - Combat 
rank[i]=[
"Increases the damage of your Sinister Strike, Backstab, and Eviscerate abilities by 2%.",
"Increases the damage of your Sinister Strike, Backstab, and Eviscerate abilities by 4%.",
"Increases the damage of your Sinister Strike, Backstab, and Eviscerate abilities by 6%."
		];
i++;		

//Vitality - Combat 
rank[i]=[
"Increases your total Stamina by 2% and your total Agility by 1%.",
"Increases your total Stamina by 4% and your total Agility by 2%."
		];
i++;
		
//Adrenaline Rush - Combat  
rank[i]=[
			"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>5 min cooldown</span><br>Increases your Energy regeneration rate by 100% for 15 sec."
		];
i++;		

//Nerves of Steel - Combat 
rank[i]=[
"Increases your chance to resist Stun and Fear effects by an additional 5%.",
"Increases your chance to resist Stun and Fear effects by an additional 10%."
		];
i++;

//Combat Potency - Combat 
rank[i]=[
"Gives your successful off-hand melee attacks a 20% chance to generate 3 Energy.",
"Gives your successful off-hand melee attacks a 20% chance to generate 6 Energy.",
"Gives your successful off-hand melee attacks a 20% chance to generate 9 Energy.",
"Gives your successful off-hand melee attacks a 20% chance to generate 12 Energy.",
"Gives your successful off-hand melee attacks a 20% chance to generate 15 Energy."
		];
i++;

//Surprise Attack - Combat
rank[i] = [
			"Your finishing moves can no longer be dodged, and the damage dealt by your Sinister Strike, Backstab, Shiv and Gouge abilities is increased by 10%."
		];
i++;		








		
//Master of Deception - Subtlety
rank[i]=[
"Reduces the chance enemies have to detect you while in Stealth mode.",
"Reduces the chance enemies have to detect you while in Stealth mode. More effective than Master of Deception (Rank 1).",
"Reduces the chance enemies have to detect you while in Stealth mode. More effective than Master of Deception (Rank 2).",
"Reduces the chance enemies have to detect you while in Stealth mode. More effective than Master of Deception (Rank 3).",
"Reduces the chance enemies have to detect you while in Stealth mode. More effective than Master of Deception (Rank 4)."
		];
i++;		

//Opportunity - Subtlety
rank[i]=[
"Increases the damage dealt when striking from behind with your Backstab, Garrote, Mutilate, and Ambush abilities by 4%.",
"Increases the damage dealt when striking from behind with your Backstab, Garrote, Mutilate, and Ambush abilities by 8%.",
"Increases the damage dealt when striking from behind with your Backstab, Garrote, Mutilate, and Ambush abilities by 12%.",
"Increases the damage dealt when striking from behind with your Backstab, Garrote, Mutilate, and Ambush abilities by 16%.",
"Increases the damage dealt when striking from behind with your Backstab, Garrote, Mutilate, and Ambush abilities by 20%."
		];
i++;		
		
//Sleight of Hand - Subtlety 
rank[i]=[
"Reduces the chance you are critically hit by melee and ranged attacks by 1% and increases the threat reduction of your Feint ability by 10%.",
"Reduces the chance you are critically hit by melee and ranged attacks by 2% and increases the threat reduction of your Feint ability by 20%."
		];
i++;				
		
//Dirty Tricks - Subtlety
rank[i]=[
"Increases the range of your Blind and Sap abilities by 2 yards and reduces the energy cost of your Blind and Sap abilities by 25%.",
"Increases the range of your Blind and Sap abilities by 5 yards and reduces the energy cost of your Blind and Sap abilities by 50%."

		];
i++;		

//Camouflage - Subtlety 
rank[i]=[
"Increases your speed while stealthed by 3% and reduces the cooldown of your Stealth ability by 1 sec.",
"Increases your speed while stealthed by 6% and reduces the cooldown of your Stealth ability by 2 sec.",
"Increases your speed while stealthed by 9% and reduces the cooldown of your Stealth ability by 3 sec.",
"Increases your speed while stealthed by 12% and reduces the cooldown of your Stealth ability by 4 sec.",
"Increases your speed while stealthed by 15% and reduces the cooldown of your Stealth ability by 5 sec."
		];
i++;		
		
	
//Initiative - Subtlety 
rank[i]=[
"Gives you a 25% chance to add an additional combo point to your target when using your Ambush, Garrote, or Cheap Shot ability.",
"Gives you a 50% chance to add an additional combo point to your target when using your Ambush, Garrote, or Cheap Shot ability.",
"Gives you a 75% chance to add an additional combo point to your target when using your Ambush, Garrote, or Cheap Shot ability."
		];
i++;		
		
//Ghostly Strike - Subtlety
rank[i]=[
			"<span style=text-align:left;float:left;>40 Energy</span><span style=text-align:right;float:right;>5 yd range</span><br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>20 sec cooldown</span><br><span style='text-align:left;float:left;'>Requires Melee Weapon</span><br>A strike that deals 125% weapon damage and increases your chance to dodge by 15% for 7 sec. Awards 1 combo point."
		];
i++;		
		
//Improved Ambush - Subtlety
rank[i]=[
"Increases the critical strike chance of your Ambush ability by 15%.",
"Increases the critical strike chance of your Ambush ability by 30%.",
"Increases the critical strike chance of your Ambush ability by 45%."
		];
i++;
		
//Setup - Subtlety 
rank[i]=[
"Gives you a 15% chance to add a combo point to your target after dodging their attack or fully resisting one of their spells.",
"Gives you a 30% chance to add a combo point to your target after dodging their attack or fully resisting one of their spells.",
"Gives you a 45% chance to add a combo point to your target after dodging their attack or fully resisting one of their spells."
		];
i++;		
		
//Elusiveness - Subtlety 
rank[i]=[
"Reduces the cooldown of your Vanish and Blind abilities by 45 sec.",
"Reduces the cooldown of your Vanish and Blind abilities by 1.5 min.",
"Reduces the cooldown of your Evasion, Vanish, and Blind abilities by 1.3 min."
		];
i++;		
		
//Serrated Blades - Subtlety
rank[i]=[
"Causes your attacks to ignore 186 of your target's Armor and increases the damage dealt by your Rupture ability by 10%.  The amount of Armor reduced increases with your level.",
"Causes your attacks to ignore 373 of your target's Armor and increases the damage dealt by your Rupture ability by 20%.  The amount of Armor reduced increases with your level.",
"Causes your attacks to ignore 560 of your target's Armor and increases the damage dealt by your Rupture ability by 30%.  The amount of Armor reduced increases with your level."
		];
i++;				
		
//Heightened Senses - Subtlety
rank[i]=[
"Increases your Stealth detection and reduces the chance you are hit by spells and ranged attacks by 2%.",
"Increases your Stealth detection and reduces the chance you are hit by spells and ranged attacks by 4%. More effective than Heightened Senses (Rank 1)."
		];
i++;			
		
//Preparation - Subtlety 
rank[i]=[
			"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>10 min cooldown</span><br>When activated, this ability immediately finishes the cooldown on your Evasion, Sprint, Vanish, Cold Blood, Shadowstep and Premeditation abilities."
		];
i++;		
	
//Dirty Deeds - Subtlety 
rank[i]=[
			"Reduces the Energy Cost of your Cheap Shot and Garrote abilities by 10. Additionally, your special abilities cause 10% more damage against targets below 35% health.",
			"Reduces the Energy Cost of your Cheap Shot and Garrote abilities by 20. Additionally, your special abilities cause 20% more damage against targets below 35% health."
		];
i++;	
		
//Hemorrhage - Subtlety 
rank[i]=[
			"<span style=text-align:left;float:left;>35 Energy</span><span style=text-align:right;float:right;>Melee range</span><br>Instant<br>Requires Melee Weapon<br>An instant strike that deals 110% weapon damage and causes the target to hemorrhage, increasing any Physical damage dealt to the target by up to 13.  Lasts 10 charges or 15 sec.  Awards 1 combo point.<br><br>\
			&nbsp;Trainable Ranks Listed Below:<br>\
			&nbsp;Rank 2: 18 Damage<br>\
			&nbsp;Rank 3: 25 Damage<br>\
			&nbsp;Rank 4: 36 Damage"
		];
i++;		
		
//Master of Subtlety - Subtlety
rank[i]=[
"Attacks made while stealthed and for 6 seconds after breaking stealth cause an additional 4% damage.",
"Attacks made while stealthed and for 6 seconds after breaking stealth cause an additional 7% damage.",
"Attacks made while stealthed and for 6 seconds after breaking stealth cause an additional 10% damage."		];
i++;				
		
		
//Deadliness - Subtlety
rank[i]=[
"Increases your Attack Power by 2%.",
"Increases your Attack Power by 4%.",
"Increases your Attack Power by 6%.",
"Increases your Attack Power by 8%.",
"Increases your Attack Power by 10%."
		];
i++;		
		
//Enveloping Shadows - Subtlety
rank[i]=[
"Increases your chance to avoid area of effect attacks by an additional 5%.",
"Increases your chance to avoid area of effect attacks by an additional 10%.",
"Increases your chance to avoid area of effect attacks by an additional 15%."
		];
i++;				
	
//Premeditation - Subtlety 
rank[i]=[
			"30 yd range<br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>2 min cooldown</span><br><span style=color:eb0504>Requires Stealth</span><br>When used, adds 2 combo points to your target. You must add to or use those combo points within 10 sec or the combo points are lost."
		];
i++;	
	
//Cheat Death - Subtlety
rank[i]=[
"You have a 33% chance to completely avoid any damaging attack that would otherwise kill you and reduce all damage taken by 90% for 3 sec.  This effect cannot occur more than once per minute.",
"You have a 66% chance to completely avoid any damaging attack that would otherwise kill you and reduce all damage taken by 90% for 3 sec.  This effect cannot occur more than once per minute.",
"You have a 100% chance to completely avoid any damaging attack that would otherwise kill you and reduce all damage taken by 90% for 3 sec.  This effect cannot occur more than once per minute."
		];
i++;	
		
//Sinister Calling - Subtlety
rank[i]=[
"Increases your total Agility by 3% and increases the percentage damage bonus of Backstab and Hemorrhage by an additional 2%.",
"Increases your total Agility by 6% and increases the percentage damage bonus of Backstab and Hemorrhage by an additional 4%.",
"Increases your total Agility by 9% and increases the percentage damage bonus of Backstab and Hemorrhage by an additional 6%.",
"Increases your total Agility by 12% and increases the percentage damage bonus of Backstab and Hemorrhage by an additional 8%.",
"Increases your total Agility by 15% and increases the percentage damage bonus of Backstab and Hemorrhage by an additional 10%."
		];
i++;			

//Shadowstep - Subtlety 
rank[i]=[
			"<span style=text-align:left;float:left;>10 Energy</span><span style=text-align:right;float:right;>25 yd range</span><br><span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>30 sec cooldown</span><br>Attempts to step through the shadows and reappear behind your enemy and increases movement speed by 70% for 3 sec. The damage of your next ability is increased by 20% and the threat caused is reduced by 50%. Lasts 10 sec."
		];
i++;			
		
		
//Subtlety Talents End^^
jsLoaded=true;//needed for ajax script loading
