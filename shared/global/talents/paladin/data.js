var i = 0;
var t = 0;

var className = "Paladin Talents";
var talentPath = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fglobal%2Ftalents%2Fpaladin%2Fdata.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ftalents%2F&reason=external-or-uncollected-resource";

tree[i] = "Holy"; i++;
tree[i] = "Protection"; i++;
tree[i] = "Retribution"; i++;

i = 0;

talent[i] = [0, "Divine Strength", 5, 2, 1]; i++;
talent[i] = [0, "Divine Intellect", 5, 3, 1]; i++;
talent[i] = [0, "Spiritual Focus", 5, 2, 2]; i++;
talent[i] = [0, "Improved Seal of Righteousness", 5, 3, 2]; i++; 
talent[i] = [0, "Healing Light", 3, 1, 3]; i++;
talent[i] = [0, "Aura Mastery", 1, 2, 3]; i++;
talent[i] = [0, "Improved Lay on Hands", 2, 3, 3]; i++;
talent[i] = [0, "Unyielding Faith", 2, 4, 3]; i++;
talent[i] = [0, "Illumination", 5, 2, 4]; i++;
talent[i] = [0, "Improved Blessing of Wisdom", 2, 3, 4]; i++;
talent[i] = [0, "Pure of Heart", 3, 1, 5]; i++;
talent[i] = [0, "Divine Favor", 1, 2, 5, [getTalentID("Illumination"),5]]; i++;
talent[i] = [0, "Sanctified Light", 3, 3, 5]; i++;
talent[i] = [0, "Purifying Power", 2, 1, 6]; i++;
talent[i] = [0, "Holy Power", 5, 3, 6]; i++;
talent[i] = [0, "Light's Grace", 3, 1, 7]; i++;
talent[i] = [0, "Holy Shock", 1, 2, 7, [getTalentID("Divine Favor"),1]]; i++;
talent[i] = [0, "Blessed Life", 3, 3, 7]; i++;
talent[i] = [0, "Holy Guidance", 5, 2, 8]; i++;
talent[i] = [0, "Divine Illumination", 1, 2, 9]; i++;

treeStartStop[t] = i -1;
t++;

//protection talents
talent[i] = [1, "Improved Devotion Aura", 5, 2, 1]; i++;
talent[i] = [1, "Redoubt", 5, 3, 1]; i++;
talent[i] = [1, "Precision", 3, 1, 2]; i++;
talent[i] = [1, "Guardian's Favor", 2, 2, 2]; i++;
talent[i] = [1, "Toughness", 5, 4, 2]; i++;
talent[i] = [1, "Blessing of Kings", 1, 1, 3]; i++;
talent[i] = [1, "Improved Righteous Fury", 3, 2, 3]; i++;
talent[i] = [1, "Shield Specialization", 3, 3, 3, [getTalentID("Redoubt"),5]]; i++;
talent[i] = [1, "Anticipation", 5, 4, 3]; i++;
talent[i] = [1, "Stoicism", 2, 1, 4]; i++;
talent[i] = [1, "Improved Hammer of Justice", 3, 2, 4]; i++;
talent[i] = [1, "Improved Concentration Aura", 3, 3, 4]; i++;
talent[i] = [1, "Spell Warding", 2, 1, 5]; i++;
talent[i] = [1, "Blessing of Sanctuary", 1, 2, 5]; i++;
talent[i] = [1, "Reckoning", 5, 3, 5]; i++;
talent[i] = [1, "Sacred Duty", 2, 1, 6]; i++;
talent[i] = [1, "One-Handed Weapon Specialization", 5, 3, 6]; i++;
talent[i] = [1, "Improved Holy Shield", 2, 1, 7, [i+1,1]]; i++;
talent[i] = [1, "Holy Shield", 1, 2, 7, [getTalentID("Blessing of Sanctuary"),1]]; i++;
talent[i] = [1, "Ardent Defender", 5, 3, 7]; i++;
talent[i] = [1, "Combat Expertise", 5, 3, 8]; i++;
talent[i] = [1, "Avenger's Shield", 1, 2, 9, [getTalentID("Holy Shield"),1]]; i++;

treeStartStop[t] = i -1;
t++;

//retribution talents
talent[i] = [2, "Improved Blessing of Might", 5, 2, 1]; i++;
talent[i] = [2, "Benediction", 5, 3, 1]; i++;
talent[i] = [2, "Improved Judgement", 2, 1, 2]; i++;
talent[i] = [2, "Improved Seal of the Crusader", 3, 2, 2]; i++;
talent[i] = [2, "Deflection", 5, 3, 2]; i++;
talent[i] = [2, "Vindication", 3, 1, 3]; i++;
talent[i] = [2, "Conviction", 5, 2, 3]; i++;
talent[i] = [2, "Seal of Command", 1, 3, 3]; i++;
talent[i] = [2, "Pursuit of Justice", 3, 4, 3]; i++;
talent[i] = [2, "Eye for an Eye", 2, 1, 4]; i++;
talent[i] = [2, "Improved Retribution Aura", 2, 3, 4]; i++;
talent[i] = [2, "Crusade", 3, 4, 4]; i++;
talent[i] = [2, "Two-Handed Weapon Specialization", 3, 1, 5]; i++;
talent[i] = [2, "Sanctity Aura", 1, 3, 5]; i++;
talent[i] = [2, "Improved Sanctity Aura", 2, 4, 5, [getTalentID("Sanctity Aura"),1]]; i++;
talent[i] = [2, "Vengeance", 5, 2, 6, [getTalentID("Conviction"),5]]; i++;
talent[i] = [2, "Sanctified Judgement", 3, 3, 6]; i++;
talent[i] = [2, "Sanctified Seals", 3, 1, 7]; i++;
talent[i] = [2, "Repentance", 1, 2, 7]; i++;
talent[i] = [2, "Divine Purpose", 3, 3, 7]; i++;
talent[i] = [2, "Fanaticism", 5, 2, 8, [getTalentID("Repentance"),1]]; i++;
talent[i] = [2, "Crusader Strike", 1, 2, 9]; i++;

treeStartStop[t] = i -1;
t++;

i = 0;


//Holy Talents Begin

//Divine Strength - Holy
rank[i] = [
"Increases your total Strength by 2%",
"Increases your total Strength by 4%",
"Increases your total Strength by 6%",
"Increases your total Strength by 8%",
"Increases your total Strength by 10%"
		];
i++;		
		
//Divine Intellect - Holy
rank[i] = [
"Increases your total Intellect by 2%.",
"Increases your total Intellect by 4%.",
"Increases your total Intellect by 6%.",
"Increases your total Intellect by 8%.",
"Increases your total Intellect by 10%."
		];
i++;		

//Spiritual Focus - Holy
rank[i] = [
"Gives your Flash of Light and Holy Light spells a 14% chance to not lose casting time when you take damage.",
"Gives your Flash of Light and Holy Light spells a 28% chance to not lose casting time when you take damage.",
"Gives your Flash of Light and Holy Light spells a 42% chance to not lose casting time when you take damage.",
"Gives your Flash of Light and Holy Light spells a 56% chance to not lose casting time when you take damage.",
"Gives your Flash of Light and Holy Light spells a 70% chance to not lose casting time when you take damage."
		];
i++;		
		
//Improved Seal of Righteousness - Holy
rank[i] = [
"Increases the damage done by your Seal of Righteousness and Judgement of Righteousness by 3%.",
"Increases the damage done by your Seal of Righteousness and Judgement of Righteousness by 6%.",
"Increases the damage done by your Seal of Righteousness and Judgement of Righteousness by 9%.",
"Increases the damage done by your Seal of Righteousness and Judgement of Righteousness by 12%.",
"Increases the damage done by your Seal of Righteousness and Judgement of Righteousness by 15%."
		];
i++;		

//Healing Light - Holy
rank[i] = [
"Increases the amount healed by your Holy Light and Flash of Light spells by 4%.",
"Increases the amount healed by your Holy Light and Flash of Light spells by 8%.",
"Increases the amount healed by your Holy Light and Flash of Light spells by 12%."
		];
i++;		

//Aura Mastery - Retribution 
rank[i]=[
		"Increases the radius of your Auras to 40 yards."
		];
i++;	

//Improved Lay on Hands - Holy
rank[i] = [
		"Gives the target of your Lay on Hands spell a 15% bonus to their armor value from items for 2 min. In addition, the cooldown for your Lay on Hands spell is reduced by 10 min.",
		"Gives the target of your Lay on Hands spell a 30% bonus to their armor value from items for 2 min. In addition, the cooldown for your Lay on Hands spell is reduced by 20 min."
		];		
i++;		


//Unyielding Faith - Holy
rank[i] = [ 
"Increases your chance to resist Fear and Disorient effects by an additional 5%.",
"Increases your chance to resist Fear and Disorient effects by an additional 10%."
		];
i++;		

//Illumination - Holy
rank[i] = [
"After getting a critical effect from your Flash of Light, Holy Light, or Holy Shock heal spell, gives you a 20% chance to gain Mana equal to 60% of the base cost of your spell.",
"After getting a critical effect from your Flash of Light, Holy Light, or Holy Shock heal spell, gives you a 40% chance to gain Mana equal to 60% of the base cost of your spell.",
"After getting a critical effect from your Flash of Light, Holy Light, or Holy Shock heal spell, gives you a 60% chance to gain Mana equal to 60% of the base cost of your spell.",
"After getting a critical effect from your Flash of Light, Holy Light, or Holy Shock heal spell, gives you a 80% chance to gain Mana equal to 60% of the base cost of your spell.",
"After getting a critical effect from your Flash of Light, Holy Light, or Holy Shock heal spell, gives you a 100% chance to gain Mana equal to 60% of the base cost of your spell."
		];
i++;		

//Improved Blessing of Wisdom - Holy 
rank[i] = [
"Increases the effect of your Blessing of Wisdom spell by 10%.",
"Increases the effect of your Blessing of Wisdom spell by 20%."
		];
i++;		

//Pure of Heart - Holy 
rank[i] = [
"Increases your resistance to Curse and Disease effects by 5%.",
"Increases your resistance to Curse and Disease effects by 10%.",
"Increases your resistance to Curse and Disease effects by 15%."
		];
i++;		

//Divine Favor - Holy 
rank[i] = [
		"88 Mana<br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>2 min cooldown</span><br>When activated, gives your next Flash of Light, Holy Light, or Holy Shock spell a 100% critical effect chance."
		];
i++;		

//Sanctified Light - Holy
rank[i] = [
		"Increases the critical strike chance of your Holy Light spell by 2%.",
		"Increases the critical strike chance of your Holy Light spell by 4%.",
		"Increases the critical strike chance of your Holy Light spell by 6%."		
		];
i++;		
		

//Purifying Power - Holy
rank[i] = [
		"Reduces the mana cost of your Cleanse, Purify, and Consecration spells by 5% and increases the critical strike chance of your Exorcism and Holy Wrath spells by 10%.",
		"Reduces the mana cost of your Cleanse, Purify, and Consecration spells by 10% and increases the critical strike chance of your Exorcism and Holy Wrath spells by 20%."
		];
i++;		


//Holy Power - Holy
rank[i] = [
"Increases the critical effect chance of your Holy spells by 1%.",
"Increases the critical effect chance of your Holy spells by 2%.",
"Increases the critical effect chance of your Holy spells by 3%.",
"Increases the critical effect chance of your Holy spells by 4%.",
"Increases the critical effect chance of your Holy spells by 5%."
		];
i++;		

//Light's Grace - Holy
rank[i] = [
"Gives your Holy Light spell a 33% chance to reduce the cast time of your next Holy Light spell by 0.5 sec. This effect lasts 15 sec.",
"Gives your Holy Light spell a 66% chance to reduce the cast time of your next Holy Light spell by 0.5 sec. This effect lasts 15 sec.",
"Gives your Holy Light spell a 100% chance to reduce the cast time of your next Holy Light spell by 0.5 sec. This effect lasts 15 sec."
		];
i++;		

//Holy Shock - Holy			
rank[i] = [
		"<span style=text-align:left;float:left;>225 Mana</span><span style=text-align:right;float:right;>20 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>15 sec cooldown</span><br>Blasts the target with Holy energy, causing 204 to 220 Holy damage to an enemy, or 204 to 220 healing to an ally.\
		<br><br>&nbsp;Trainable Ranks Listed Below<br>\
		&nbsp;Rank 2: 275 Mana, 279-302 Damage or Healing<br>\
		&nbsp;Rank 3: 325 Mana, 365-396 Damage or Healing<br>\
		&nbsp;Rank 4: 385 Mana, 452-488 Damage or Healing<br>\
		&nbsp;Rank 5: 435 Mana, 530-574 Damage or Healing"
		];
i++;		

//Blessed Life - Holy
rank[i] = [
"All attacks against you have a 4% chance to cause half damage.",
"All attacks against you have a 7% chance to cause half damage.",
"All attacks against you have a 10% chance to cause half damage."
		];
i++;		

//Holy Guidance - Holy
rank[i] = [
"Increases your spell damage and healing by 7% of your total Intellect.",
"Increases your spell damage and healing by 14% of your total Intellect.",
"Increases your spell damage and healing by 21% of your total Intellect.",
"Increases your spell damage and healing by 28% of your total Intellect.",
"Increases your spell damage and healing by 35% of your total Intellect."
		];
i++;	

//Divine Illumination - Holy			
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>Reduces the mana cost of all spells by 50% for 15 sec."
		];
i++;

//Improved Devotion Aura - Protection 
rank[i] = [
"Increases the armor bonus of your Devotion Aura by 8%.",
"Increases the armor bonus of your Devotion Aura by 16%.",
"Increases the armor bonus of your Devotion Aura by 24%.",
"Increases the armor bonus of your Devotion Aura by 32%.",
"Increases the armor bonus of your Devotion Aura by 40%."
		];
i++;		

//Redoubt - Protection
rank[i] = [
"Damaging melee and ranged attacks against you have a 10% chance to increase your chance to block by 6%.  Lasts 10 sec or 5 blocks.",
"Damaging melee and ranged attacks against you have a 10% chance to increase your chance to block by 12%.  Lasts 10 sec or 5 blocks.",
"Damaging melee and ranged attacks against you have a 10% chance to increase your chance to block by 18%.  Lasts 10 sec or 5 blocks.",
"Damaging melee and ranged attacks against you have a 10% chance to increase your chance to block by 24%.  Lasts 10 sec or 5 blocks.",
"Damaging melee and ranged attacks against you have a 10% chance to increase your chance to block by 30%.  Lasts 10 sec or 5 blocks."
		];
i++;

//Precision - Protection
rank[i] = [
"Increases your chance to hit with melee weapons and spells by 1%.",
"Increases your chance to hit with melee weapons and spells by 2%.",
"Increases your chance to hit with melee weapons and spells by 3%."
		];
i++;		

//Guardian's Favor - Protection 
rank[i] = [
"Reduces the cooldown of your Blessing of Protection by 60 sec and increases the duration of your Blessing of Freedom by 2 sec.",
"Reduces the cooldown of your Blessing of Protection by 120 sec and increases the duration of your Blessing of Freedom by 4 sec."
		];		
i++;		

//Toughness - Protection 
rank[i] = [
		"Increases your armor value from items by 2%.",
		"Increases your armor value from items by 4%.",
		"Increases your armor value from items by 6%.",
		"Increases your armor value from items by 8%.",
		"Increases your armor value from items by 10%."		
		];
i++;		

//Blessing of Kings - Retribution 
rank[i]=[
		"<span style=text-align:left;float:left;>177 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>Instant cast<br>Places a Blessing on the friendly target, increasing total stats by 10% for 10 min. Players may only have one Blessing on them per Paladin at any one time."
		];
i++;	

//Improved Righteous Fury - Protection 
rank[i] = [
"While Righteous Fury is active, all damage taken is reduced by 2% and increases the amount of threat generated by your Righteous Fury spell by 16%.",
"While Righteous Fury is active, all damage taken is reduced by 4% and increases the amount of threat generated by your Righteous Fury spell by 33%.",
"While Righteous Fury is active, all damage taken is reduced by 6% and increases the amount of threat generated by your Righteous Fury spell by 50%."
		];
i++;		

//Shield Specialization - Protection 
rank[i] = [
"Increases the amount of damage absorbed by your shield by 10%.",
"Increases the amount of damage absorbed by your shield by 20%.",
"Increases the amount of damage absorbed by your shield by 30%."
		];
i++;		

//Anticipation - Protection
rank[i] = [
"Increases your Defense skill by 4.",
"Increases your Defense skill by 8.",
"Increases your Defense skill by 12.",
"Increases your Defense skill by 16.",
"Increases your Defense skill by 20.",
		];
i++;		

//Stoicism - Protection
rank[i] = [
"Increases your resistance to Stun effects by an additional 5% and reduces the chance your spells will be dispelled by an additional 15%.",
"Increases your resistance to Stun effects by an additional 10% and reduces the chance your spells will be dispelled by an additional 30%."
		];
i++;		

//Improved Hammer of Justice - Protection 
rank[i] = [
"Decreases the cooldown of your Hammer of Justice spell by 5 sec.",
"Decreases the cooldown of your Hammer of Justice spell by 10 sec.",
"Decreases the cooldown of your Hammer of Justice spell by 15 sec."
		];
i++;		

//Improved Concentration Aura - Protection
rank[i] = [
"Increases the effect of your Concentration Aura by an additional 5% and reduces the duration of any Silence or Interrupt effect used against an affected group member by 10%.  The duration reduction does not stack with any other effects.",
"Increases the effect of your Concentration Aura by an additional 10% and reduces the duration of any Silence or Interrupt effect used against an affected group member by 20%.  The duration reduction does not stack with any other effects.",
"Increases the effect of your Concentration Aura by an additional 15% and reduces the duration of any Silence or Interrupt effect used against an affected group member by 30%.  The duration reduction does not stack with any other effects."
		];i++;		

//Spell Warding - Protection
rank[i] = [
"All spell damage taken is reduced by 2%.",
"All spell damage taken is reduced by 4%."
		];i++;		

//Blessing of Sanctuary - Protection 
rank[i] = [
		"<span style=text-align:left;float:left;>60 Mana</span><span style=text-align:right;float:right;>30 yd range</span><br>Instant cast<br>Places a Blessing on the friendly target, reducing damage dealt from all sources by up to 10 for 10 min.  In addition, when the target blocks a melee attack the attacker will take 14 Holy damage. Players may only have one Blessing on them per Paladin at any one time.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 85 Mana, 14 Damage Reduction, 21 Holy Damage<br>\
		&nbsp;Rank 3: 110 Mana, 19 Damage Reduction, 28 Holy Damage<br>\
		&nbsp;Rank 4: 135 Mana, 24 Damage Reduction, 35 Holy Damage<br>\
		&nbsp;Rank 5: 180 Mana, 80 Damage Reduction, 46 Holy Damage"
		];
i++;		

//Reckoning - Protection
rank[i] = [
		"Gives you a 2% chance after being hit by any damaging attack that the next 4 weapon swings within 8 sec will generate an additional attack.",
		"Gives you a 4% chance after being hit by any damaging attack that the next 4 weapon swings within 8 sec will generate an additional attack.",
		"Gives you a 6% chance after being hit by any damaging attack that the next 4 weapon swings within 8 sec will generate an additional attack.",
		"Gives you a 8% chance after being hit by any damaging attack that the next 4 weapon swings within 8 sec will generate an additional attack.",
		"Gives you a 10% chance after being hit by any damaging attack that the next 4 weapon swings within 8 sec will generate an additional attack."						
		];
i++;

//Sacred Duty - Protection
rank[i] = [
		"Increases your total Stamina by 3%, reduces the cooldown of your Divine Shield spell by 30 sec and reduces the attack speed penalty by 50%.",
		"Increases your total Stamina by 6%, reduces the cooldown of your Divine Shield spell by 60 sec and reduces the attack speed penalty by 100%."
		];
i++;

//One-Handed Weapon Specialization - Protection
rank[i]=[
"Increases all damage you deal when a one-handed melee weapon is equipped by 1%.",
"Increases all damage you deal when a one-handed melee weapon is equipped by 2%.",
"Increases all damage you deal when a one-handed melee weapon is equipped by 3%.",
"Increases all damage you deal when a one-handed melee weapon is equipped by 4%.",
"Increases all damage you deal when a one-handed melee weapon is equipped by 5%."
			];
i++;			

//Improved Holy Shield - Protection
rank[i] = [
		"Increases damage caused by your Holy Shield by 10% and increases the number of charges of your Holy Shield by 2.",
		"Increases damage caused by your Holy Shield by 20% and increases the number of charges of your Holy Shield by 4."
		];
i++;
			
//Holy Shield - Protection
rank[i] = [
		"135 Mana<br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>10 sec cooldown</span><br>Requires Shields<br>Increases chance to block by 30% for 10 sec and deals 59 Holy damage for each attack blocked while active. Damage caused by Holy Shield causes 35% additional threat. Each block expends a charge. 4 charges.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 175 Mana, 86 Holy Damage<br>\
		&nbsp;Rank 3: 215 Mana, 117 Holy Damage<br>\
		&nbsp;Rank 4: 280 Mana, 155 Holy Damage"
		];
i++;

//Ardent Defender - Protection
rank[i]=[
"When you have less than 35% health, all damage taken is reduced by 6%.",
"When you have less than 35% health, all damage taken is reduced by 12%.",
"When you have less than 35% health, all damage taken is reduced by 18%.",
"When you have less than 35% health, all damage taken is reduced by 24%.",
"When you have less than 35% health, all damage taken is reduced by 30%."
			];
i++;			
		
//Combat Expertise - Protection
rank[i]=[
"Increases your expertise by 1 and your total Stamina by 2%.",
"Increases your expertise by 2 and your total Stamina by 4%.",
"Increases your expertise by 3 and your total Stamina by 6%.",
"Increases your expertise by 4 and your total Stamina by 8%.",
"Increases your expertise by 5 and your total Stamina by 10%."
			];
i++;					
	
//Avenger's Shield - Protection
rank[i] = [
		"<span style=text-align:left;float:left;>500 Mana</span><span style=text-align:right;float:right;>8-30yd range</span><br><span style=text-align:left;float:left;>1 sec cast</span><span style=text-align:right;float:right;>30 sec cooldown</span><br>Hurls a holy shield at the enemy, dealing 270 to 330 Holy damage, dazing them and then jumping to nearby enemies. Affects 3 total targets. Lasts 6 sec.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 615 Mana, 370-452 Holy Damage<br>\
		&nbsp;Rank 3: 780 Mana, 494-602 Holy Damage"
		];
i++;	
		
//Improved Blessing of Might - Retribution
rank[i]=[
"Increases the attack power bonus of your Blessing of Might by 4%.",
"Increases the attack power bonus of your Blessing of Might by 8%.",
"Increases the attack power bonus of your Blessing of Might by 12%.",
"Increases the attack power bonus of your Blessing of Might by 16%.",
"Increases the attack power bonus of your Blessing of Might by 20%."
		];
i++;		
		
//Benediction - Retribution  
rank[i]=[
"Reduces the Mana cost of your Judgement and Seal spells by 3%.",
"Reduces the Mana cost of your Judgement and Seal spells by 6%.",
"Reduces the Mana cost of your Judgement and Seal spells by 9%.",
"Reduces the Mana cost of your Judgement and Seal spells by 12%.",
"Reduces the Mana cost of your Judgement and Seal spells by 15%."
		];
i++;		
		
//Improved Judgement - Retribution 
rank[i]=[
"Decreases the cooldown of your Judgement spell by 1 sec.",
"Decreases the cooldown of your Judgement spell by 2 sec."
		];
i++;		
		
//Improved Seal of the Crusader - Retribution  
rank[i]=[
		"In addition to the normal effect, your Judgement of the Crusader spell will also increase the critical strike chance of all attacks made against that target by an additional 1%.",
		"In addition to the normal effect, your Judgement of the Crusader spell will also increase the critical strike chance of all attacks made against that target by an additional 2%.",
		"In addition to the normal effect, your Judgement of the Crusader spell will also increase the critical strike chance of all attacks made against that target by an additional 3%."
		];
i++;		
		
//Deflection - Retribution
rank[i]=[
"Increases your Parry chance by 1%.",
"Increases your Parry chance by 2%.",
"Increases your Parry chance by 3%.",
"Increases your Parry chance by 4%.",
"Increases your Parry chance by 5%."
		];
i++;		
		
//Vindication - Retribution
rank[i]=[
"Gives the Paladin's damaging melee attacks a chance to reduce the target's attributes by 5% for 10 sec.",
"Gives the Paladin's damaging melee attacks a chance to reduce the target's attributes by 10% for 10 sec.",
"Gives the Paladin's damaging melee attacks a chance to reduce the target's attributes by 15% for 10 sec."
		];
i++;		
	
//Conviction - Retribution
rank[i]=[
		"Increases your chance to get a critical strike with melee weapons by 1%.",
		"Increases your chance to get a critical strike with melee weapons by 2%.",
		"Increases your chance to get a critical strike with melee weapons by 3%.",
		"Increases your chance to get a critical strike with melee weapons by 4%.",
		"Increases your chance to get a critical strike with melee weapons by 5%."				
		];
i++;	
		
//Seal of Command - Retribution
rank[i]=[
		"65 Mana<br>Instant cast<br>Gives the Paladin a chance to deal additional Holy damage equal to 70% of normal weapon damage. Only one Seal can be active on the Paladin at any one time. Lasts 30 sec.<br><br>Unleashing this Seal's energy will judge an enemy, instantly causing 68 to 73 Holy damage, 137 to 146 if the target is stunned or incapacitated.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 110 Mana, 97-105 / 194-209 Damage<br>\
		&nbsp;Rank 3: 140 Mana, 124-135 / 248-269 Damage<br>\
		&nbsp;Rank 4: 180 Mana, 154-168 / 309-336 Damage<br>\
		&nbsp;Rank 5: 210 Mana, 193-211 / 387-422 Damage<br>\
		&nbsp;Rank 6: 280 Mana, 228-252 / 456-504 Damage"
		];
i++;		
		
//Pursuit of Justice - Retribution
rank[i]=[
"Reduces the chance you'll be hit by spells by 1% and increases movement and mounted movement speed by 5%.  This does not stack with other movement speed increasing effects.",
"Reduces the chance you'll be hit by spells by 2% and increases movement and mounted movement speed by 10%.  This does not stack with other movement speed increasing effects.",
"Reduces the chance you'll be hit by spells by 3% and increases movement and mounted movement speed by 15%.  This does not stack with other movement speed increasing effects."
		];
i++;		
		
//Eye for an Eye - Retribution  
rank[i]=[
"All spell criticals against you cause 15% of the damage taken to the caster as well. The damage caused by Eye for an Eye will not exceed 50% of the Paladin's total health.",
"All spell criticals against you cause 30% of the damage taken to the caster as well. The damage caused by Eye for an Eye will not exceed 50% of the Paladin's total health."
		];
i++;		
		
//Improved Retribution Aura - Retribution  
rank[i]=[
"Increases the damage done by your Retribution Aura by 25%.",
"Increases the damage done by your Retribution Aura by 50%."
		];
i++;	

//Crusade - Retribution 
rank[i]=[
		"Increases all damage caused against Humanoids, Demons, Undead and Elementals by 1%.",
		"Increases all damage caused against Humanoids, Demons, Undead and Elementals by 2%.",
		"Increases all damage caused against Humanoids, Demons, Undead and Elementals by 3%."
		];
i++;

//Two-Handed Weapon Specialization - Retribution 
rank[i]=[
		"Increases the damage you deal with two-handed melee weapons by 2%.",
		"Increases the damage you deal with two-handed melee weapons by 4%.",
		"Increases the damage you deal with two-handed melee weapons by 6%."
		];
i++;	


//Sanctity Aura - Holy
rank[i] = [
		"Instant<br>Increases Holy damage done by party members within 30 yards by 10%. Players may only have one Aura on them per Paladin at any one time."
		];
i++;		

//Improved Sanctity Aura - Retribution 
rank[i]=[
		"The amount of damage caused by targets affected by Sanctity Aura is increased by 1%.",
		"The amount of damage caused by targets affected by Sanctity Aura is increased by 2%."
		];
i++;	

//Vengeance - Retribution  
rank[i]=[
"Gives you a 1% bonus to Physical and Holy damage you deal for 30 sec after dealing a critical strike from a weapon swing, spell or ability. This effect stacks up to 3 times",
"Gives you a 2% bonus to Physical and Holy damage you deal for 30 sec after dealing a critical strike from a weapon swing, spell or ability. This effect stacks up to 3 times",
"Gives you a 3% bonus to Physical and Holy damage you deal for 30 sec after dealing a critical strike from a weapon swing, spell or ability. This effect stacks up to 3 times",
"Gives you a 4% bonus to Physical and Holy damage you deal for 30 sec after dealing a critical strike from a weapon swing, spell or ability. This effect stacks up to 3 times",
"Gives you a 5% bonus to Physical and Holy damage you deal for 30 sec after dealing a critical strike from a weapon swing, spell or ability. This effect stacks up to 3 times"
		];
i++;	

//Sanctified Judgement - Retribution 
rank[i]=[
		"Gives your Judgement spell a 33% chance to return 80% of the mana cost of the judged seal.",
		"Gives your Judgement spell a 66% chance to return 80% of the mana cost of the judged seal.",
		"Gives your Judgement spell a 100% chance to return 80% of the mana cost of the judged seal."
		];
i++;	

//Sanctified Seals - Retribution 
rank[i]=[
		"Increases your chance to critically hit with all spells and melee attacks by 1% and reduces the chance your Seals will be dispelled by 33%.",
		"Increases your chance to critically hit with all spells and melee attacks by 2% and reduces the chance your Seals will be dispelled by 66%.",
		"Increases your chance to critically hit with all spells and melee attacks by 3% and reduces the chance your Seals will be dispelled by 100%."
		];
i++;

//Repentance - Protection
rank[i]=[
		"<span style=text-align:left;float:left;>60 Mana</span><span style=text-align:right;float:right;>20 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>1 min cooldown</span><br>Puts the enemy target in a state of meditation, incapacitating them for up to 6 sec. Any damage caused will awaken the target. Only works against Humanoids."
		];
i++;		

//Divine Purpose - Retribution 
rank[i]=[
		"Melee and ranged critical strikes against you cause 4% less damage.",
		"Melee and ranged critical strikes against you cause 7% less damage.",
		"Melee and ranged critical strikes against you cause 10% less damage."								
		];
i++;	

//Fanaticism - Retribution 
rank[i]=[
		"Increases the critical strike chance of all Judgements capable of a critical hit by 3% and reduces threat caused by all actions by 6% except when under the effects of Righteous Fury.",
		"Increases the critical strike chance of all Judgements capable of a critical hit by 6% and reduces threat caused by all actions by 12% except when under the effects of Righteous Fury.",
		"Increases the critical strike chance of all Judgements capable of a critical hit by 9% and reduces threat caused by all actions by 18% except when under the effects of Righteous Fury.",
		"Increases the critical strike chance of all Judgements capable of a critical hit by 12% and reduces threat caused by all actions by 24% except when under the effects of Righteous Fury.",
		"Increases the critical strike chance of all Judgements capable of a critical hit by 15% and reduces threat caused by all actions by 30% except when under the effects of Righteous Fury."								
		];
i++;	

//Crusader Strike - Retribution 
rank[i]=[
		"<span style=text-align:left;float:left;>236 Mana</span><span style=text-align:right;float:right;>5 yd range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>6 sec cooldown</span><br>Requires Melee Weapon<br>An instant strike that causes 110% weapon damage and refreshes all Judgements on the target."						
		];
i++;

//Retribution Talents End^^
jsLoaded=true;//needed for ajax script loading


