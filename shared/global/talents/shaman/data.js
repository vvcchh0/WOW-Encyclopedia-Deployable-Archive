var i = 0;
var t = 0;

var className = "Shaman Talents";
var talentPath = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fglobal%2Ftalents%2Fshaman%2Fdata.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ftalents%2F&reason=external-or-uncollected-resource";

tree[i] = "Elemental"; i++;
tree[i] = "Enhancement"; i++;
tree[i] = "Restoration"; i++;

i = 0;


talent[i] = [0, "Convection", 5, 2, 1]; i++;
talent[i] = [0, "Concussion", 5, 3, 1]; i++;
talent[i] = [0, "Earth's Grasp", 2, 1, 2]; i++;
talent[i] = [0, "Elemental Warding", 3, 2, 2]; i++; 
talent[i] = [0, "Call of Flame", 3, 3, 2]; i++;
talent[i] = [0, "Elemental Focus", 1, 1, 3]; i++;
talent[i] = [0, "Reverberation", 5, 2, 3]; i++;
talent[i] = [0, "Call of Thunder", 5, 3, 3]; i++;
talent[i] = [0, "Improved Fire Nova Totem", 2, 1, 4]; i++;
talent[i] = [0, "Eye of the Storm", 3, 2, 4]; i++;
talent[i] = [0, "Elemental Devastation", 3, 4, 4]; i++;
talent[i] = [0, "Storm Reach", 2, 1, 5]; i++;
talent[i] = [0, "Elemental Fury", 1, 2, 5]; i++;
talent[i] = [0, "Unrelenting Storm", 5, 4, 5]; i++;
talent[i] = [0, "Elemental Precision", 3, 1, 6]; i++;
talent[i] = [0, "Lightning Mastery", 5, 3, 6, [getTalentID("Call of Thunder"),5]]; i++;
talent[i] = [0, "Elemental Mastery", 1, 2, 7, [getTalentID("Elemental Fury"),1]]; i++;
talent[i] = [0, "Elemental Shields", 3, 3, 7]; i++;
talent[i] = [0, "Lightning Overload", 5, 2, 8]; i++;
talent[i] = [0, "Totem of Wrath", 1, 2, 9, [getTalentID("Lightning Overload"),5]]; i++;

treeStartStop[t] = i -1;
t++;

//enhancement talents
talent[i] = [1, "Ancestral Knowledge", 5, 2, 1]; i++;
talent[i] = [1, "Shield Specialization", 5, 3, 1]; i++;
talent[i] = [1, "Guardian Totems", 2, 1, 2]; i++;
talent[i] = [1, "Thundering Strikes", 5, 2, 2]; i++;
talent[i] = [1, "Improved Ghost Wolf", 2, 3, 2]; i++;
talent[i] = [1, "Improved Lightning Shield", 3, 4, 2]; i++;
talent[i] = [1, "Enhancing Totems", 2, 1, 3]; i++;
talent[i] = [1, "Shamanistic Focus", 1, 3, 3]; i++;
talent[i] = [1, "Anticipation", 5, 4, 3]; i++;
talent[i] = [1, "Flurry", 5, 2, 4, [getTalentID("Thundering Strikes"),5]]; i++;
talent[i] = [1, "Toughness", 5, 3, 4]; i++;
talent[i] = [1, "Improved Weapon Totems", 2, 1, 5]; i++;
talent[i] = [1, "Spirit Weapons", 1, 2, 5]; i++;
talent[i] = [1, "Elemental Weapons", 3, 3, 5]; i++;
talent[i] = [1, "Mental Quickness", 3, 1, 6]; i++; 
talent[i] = [1, "Weapon Mastery", 5, 4, 6]; i++;
talent[i] = [1, "Dual Wield Specialization", 3, 1, 7, [i+1,1]]; i++;
talent[i] = [1, "Dual Wield", 1, 2, 7, [getTalentID("Spirit Weapons"),1]]; i++;
talent[i] = [1, "Stormstrike", 1, 3, 7, [getTalentID("Elemental Weapons"),3]]; i++;
talent[i] = [1, "Unleashed Rage", 5, 2, 8]; i++;  
talent[i] = [1, "Shamanistic Rage", 1, 2, 9]; i++;

treeStartStop[t] = i -1;
t++;

//restoration talents
talent[i] = [2, "Improved Healing Wave", 5, 2, 1]; i++;
talent[i] = [2, "Tidal Focus", 5, 3, 1]; i++;
talent[i] = [2, "Improved Reincarnation", 2, 1, 2]; i++;
talent[i] = [2, "Ancestral Healing", 3, 2, 2]; i++;
talent[i] = [2, "Totemic Focus", 5, 3, 2]; i++;
talent[i] = [2, "Nature's Guidance", 3, 1, 3]; i++;
talent[i] = [2, "Healing Focus", 5, 2, 3]; i++;
talent[i] = [2, "Totemic Mastery", 1, 3, 3]; i++;
talent[i] = [2, "Healing Grace", 3, 4, 3]; i++;
talent[i] = [2, "Restorative Totems", 5, 2, 4]; i++;
talent[i] = [2, "Tidal Mastery", 5, 3, 4]; i++;
talent[i] = [2, "Healing Way", 3, 1, 5]; i++;
talent[i] = [2, "Nature's Swiftness", 1, 3, 5]; i++;
talent[i] = [2, "Focused Mind", 3, 4, 5]; i++;
talent[i] = [2, "Purification", 5, 3, 6]; i++;
talent[i] = [2, "Mana Tide Totem", 1, 2, 7, [getTalentID("Restorative Totems"),5]]; i++;
talent[i] = [2, "Nature's Guardian", 5, 3, 7]; i++;
talent[i] = [2, "Nature's Blessing", 3, 2, 8]; i++;
talent[i] = [2, "Improved Chain Heal", 2, 3, 8]; i++;
talent[i] = [2, "Earth Shield", 1, 2, 9, [getTalentID("Nature's Blessing"),3]]; i++;

treeStartStop[t] = i -1;
t++;

i = 0;


//Elemental Talents Begin

//Convection - Elemental
rank[i] = [
"Reduces the mana cost of your Shock, Lightning Bolt and Chain Lightning spells by 2%.",
"Reduces the mana cost of your Shock, Lightning Bolt and Chain Lightning spells by 4%.",
"Reduces the mana cost of your Shock, Lightning Bolt and Chain Lightning spells by 6%.",
"Reduces the mana cost of your Shock, Lightning Bolt and Chain Lightning spells by 8%.",
"Reduces the mana cost of your Shock, Lightning Bolt and Chain Lightning spells by 10%."
		];
i++;		
		
//Concussion - Elemental
rank[i] = [
"Increases the damage done by your Lightning Bolt, Chain Lightning and Shock spells by 1%.",
"Increases the damage done by your Lightning Bolt, Chain Lightning and Shock spells by 2%.",
"Increases the damage done by your Lightning Bolt, Chain Lightning and Shock spells by 3%.",
"Increases the damage done by your Lightning Bolt, Chain Lightning and Shock spells by 4%.",
"Increases the damage done by your Lightning Bolt, Chain Lightning and Shock spells by 5%."
		];
i++;		

//Improved Stoneclaw Totem - Elemental
rank[i] = [
"Increases the health of your Stoneclaw Totem by 25% and the radius of your Earthbind Totem by 10%.",
"Increases the health of your Stoneclaw Totem by 50% and the radius of your Earthbind Totem by 20%."
		];
i++;		
		
//Elemental Warding - Elemental
rank[i] = [
"Reduces damage taken from Fire, Frost and Nature effects by 4%.",
"Reduces damage taken from Fire, Frost and Nature effects by 7%.",
"Reduces damage taken from Fire, Frost and Nature effects by 10%."
		];
i++;				
		
//Call of Flame - Elemental
rank[i] = [
"Increases the damage done by your Fire Totems by 5%.",
"Increases the damage done by your Fire Totems by 10%.",
"Increases the damage done by your Fire Totems by 15%."
		];
i++;		

//Elemental Focus - Elemental
rank[i] = [
"After landing a critical strike with a Fire, Frost, or Nature damage spell, you enter a Clearcasting state.  The Clearcasting state reduces the mana cost of your next 2 damage spells by 40%."
		];		
i++;		

//Reverberation - Elemental
rank[i] = [
"Reduces the cooldown of your Shock spells by 0.2 sec.",
"Reduces the cooldown of your Shock spells by 0.4 sec.",
"Reduces the cooldown of your Shock spells by 0.6 sec.",
"Reduces the cooldown of your Shock spells by 0.8 sec.",
"Reduces the cooldown of your Shock spells by 1 sec."
		];
i++;		

//Call of Thunder - Elemental
rank[i] = [ 
"Increases the critical strike chance of your Lightning Bolt and Chain Lightning spells by an additional 1%.",
"Increases the critical strike chance of your Lightning Bolt and Chain Lightning spells by an additional 2%.",
"Increases the critical strike chance of your Lightning Bolt and Chain Lightning spells by an additional 3%.",
"Increases the critical strike chance of your Lightning Bolt and Chain Lightning spells by an additional 4%.",
"Increases the critical strike chance of your Lightning Bolt and Chain Lightning spells by an additional 6%."
		];
i++;		

//Improved Fire Nova Totem - Elemental
rank[i] = [
"Reduces the delay before your Fire Nova Totem activates by 1 sec. and decreases the threat generated by your Magma Totem by 25%.",
"Reduces the delay before your Fire Nova Totem activates by 2 sec. and decreases the threat generated by your Magma Totem by 50%."
		];
i++;		

//Eye of the Storm - Elemental
rank[i] = [
"Gives you a 33% chance to gain the Focused Casting effect that lasts for 6 sec after being the victim of a melee or ranged critical strike. The Focused Casting effect prevents you from losing casting time on Shaman spells when taking damage.",
"Gives your a 66% chance to gain the Focused Casting effect that lasts for 6 sec after being the victim of a melee or ranged critical strike. The Focused Casting effect prevents you from losing casting time on Shaman spells when taking damage.",
"Gives your a 100% chance to gain the Focused Casting effect that lasts for 6 sec after being the victim of a melee or ranged critical strike. The Focused Casting effect prevents you from losing casting time on Shaman spells when taking damage."
		];
i++;		

//Elemental Fury - Elemental 
rank[i] = [
"Your offensive spell crits will increase your chance to get a critical strike with melee attacks by 3% for 10 sec.",
"Your offensive spell crits will increase your chance to get a critical strike with melee attacks by 6% for 10 sec.",
"Your offensive spell crits will increase your chance to get a critical strike with melee attacks by 9% for 10 sec."
		];
i++;		

//Elemental Fury - Elemental 
rank[i] = [
"Increases the range of your Lightning Bolt and Chain Lightning spells by 3 yards.",
"Increases the range of your Lightning Bolt and Chain Lightning spells by 6 yards."
		];
i++;		

//Elemental Fury - Elemental 
rank[i] = [
"Increases the critical strike damage bonus of your Searing, Magma, and Fire Nova Totems and your Fire, Frost, and Nature spells by 100%."
		];
i++;		

//Unrelenting Storm - Elemental 
rank[i] = [
"Regenerate mana equal to 2% of your Intellect every 5 sec, even while casting.",
"Regenerate mana equal to 4% of your Intellect every 5 sec, even while casting.",
"Regenerate mana equal to 6% of your Intellect every 5 sec, even while casting.",
"Regenerate mana equal to 8% of your Intellect every 5 sec, even while casting.",
"Regenerate mana equal to 10% of your Intellect every 5 sec, even while casting."
		];
i++;		

//Elemental Precision - Elemental 
rank[i] = [
"Increases your chance to hit with Fire, Frost, and Nature spells by 2% and reduces the threat caused by Fire, Frost, and Nature spells by 4%.",
"Increases your chance to hit with Fire, Frost, and Nature spells by 4% and reduces the threat caused by Fire, Frost, and Nature spells by 7%.",
"Increases your chance to hit with Fire, Frost, and Nature spells by 6% and reduces the threat caused by Fire, Frost, and Nature spells by 10%."
		];
i++;		

//Lightning Mastery - Elemental  
rank[i] = [
"Reduces the cast time of your Lightning Bolt and Chain Lightning spells by 0.1 sec.",
"Reduces the cast time of your Lightning Bolt and Chain Lightning spells by 0.2 sec.",
"Reduces the cast time of your Lightning Bolt and Chain Lightning spells by 0.3 sec.",
"Reduces the cast time of your Lightning Bolt and Chain Lightning spells by 0.4 sec.",
"Reduces the cast time of your Lightning Bolt and Chain Lightning spells by 0.5 sec."
		];
i++;		

//Elemental Mastery - Elemental				
rank[i] = [
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, this spell gives your next Fire, Frost, or Nature damage spell a 100% critical strike chance and reduces the mana cost by 100%."
		];
i++;		

//Elemental Shards - Elemental  
rank[i] = [
"Reduces the chance you will be critically hit by melee and ranged attacks by 2%.",
"Reduces the chance you will be critically hit by melee and ranged attacks by 4%.",
"Reduces the chance you will be critically hit by melee and ranged attacks by 6%."
		];
i++;		

//Lightning Overload - Elemental
rank[i] = [
"Gives your Lightning Bolt and Chain Lightning spells a 4% chance to cast a second, similar spell on the same target at no additional cost that causes half damage and no threat.",
"Gives your Lightning Bolt and Chain Lightning spells a 8% chance to cast a second, similar spell on the same target at no additional cost that causes half damage and no threat.",
"Gives your Lightning Bolt and Chain Lightning spells a 12% chance to cast a second, similar spell on the same target at no additional cost that causes half damage and no threat.",
"Gives your Lightning Bolt and Chain Lightning spells a 16% chance to cast a second, similar spell on the same target at no additional cost that causes half damage and no threat.",
"Gives your Lightning Bolt and Chain Lightning spells a 20% chance to cast a second, similar spell on the same target at no additional cost that causes half damage and no threat."
		];
i++;	

//Totem of Wrath - Elemental
rank[i] = [
	"147 Mana<br>Instant cast<br>Tools: Fire Totem<br>Summons a Totem of Wrath with 5 health at the feet of the caster. The totem increases the chance to hit and critically hit with spells by 3% to all party members if they are within 20 yards. Lasts 2 min."
		];
i++;	

//Ancestral Knowledge - Enhancement
rank[i] = [
"Increases your maximum Mana by 1%.",
"Increases your maximum Mana by 2%.",
"Increases your maximum Mana by 3%.",
"Increases your maximum Mana by 4%.",
"Increases your maximum Mana by 5%."
		];
i++;		

//Shield Specialization - Enhancement 
rank[i] = [
"Increases your chance to block attacks with a shield by 1% and increases the amount blocked by 5%.",
"Increases your chance to block attacks with a shield by 2% and increases the amount blocked by 10%.",
"Increases your chance to block attacks with a shield by 3% and increases the amount blocked by 15%.",
"Increases your chance to block attacks with a shield by 4% and increases the amount blocked by 20%.",
"Increases your chance to block attacks with a shield by 5% and increases the amount blocked by 25%."
		];
i++;

//Improved Stoneskin Totem - Enhancement
rank[i] = [
"Increases the amount of damage reduced by your Stoneskin Totem and Windwall Totem by 10% and reduces the cooldown of your Grounding Totem by 1 sec.",
"Increases the amount of damage reduced by your Stoneskin Totem and Windwall Totem by 20% and reduces the cooldown of your Grounding Totem by 2 sec."
		];
i++;		

//Thundering Strikes - Enhancement 
rank[i] = [
"Improves your chance to get a critical strike with your weapon attacks by 1%.",
"Improves your chance to get a critical strike with your weapon attacks by 2%.",
"Improves your chance to get a critical strike with your weapon attacks by 3%.",
"Improves your chance to get a critical strike with your weapon attacks by 4%.",
"Improves your chance to get a critical strike with your weapon attacks by 5%."
		];		
i++;		

//Improved Ghost Wolf - Enhancement 
rank[i] = [

"Reduces the cast time of your Ghost Wolf spell by 1 sec.",
"Reduces the cast time of your Ghost Wolf spell by 2 sec."
		];
i++;		

//Improved Lightning Shield - Enhancement
rank[i] = [
"Increases the damage done by your Lightning Shield orbs by 5%.",
"Increases the damage done by your Lightning Shield orbs by 10%.",
"Increases the damage done by your Lightning Shield orbs by 15%."
		];
i++;		

//Improved Strength of Earth Totem - Enhancement	
rank[i] = [

"Increases the effect of your Strength of Earth and Grace of Air Totems by 8%.",
"Increases the effect of your Strength of Earth and Grace of Air Totems by 15%."
		];
i++;		

//Shamanistic Focus - Enhancement  
rank[i] = [
"After landing a melee critical strike, you enter a Focused state. The Focused state reduces the mana cost of your next Shock spell by 60%."
		];
i++;		

//Anticipation - Enhancement 
rank[i] = [
"Increases your chance to dodge by an additional 1%.",
"Increases your chance to dodge by an additional 2%",
"Increases your chance to dodge by an additional 3%",
"Increases your chance to dodge by an additional 4%",
"Increases your chance to dodge by an additional 5%"
		];i++;		

//Flurry - Enhancement
rank[i] = [
"Increases your attack speed by 10% for your next 3 swings after dealing a critical strike.",
"Increases your attack speed by 15% for your next 3 swings after dealing a critical strike.",
"Increases your attack speed by 20% for your next 3 swings after dealing a critical strike.",
"Increases your attack speed by 25% for your next 3 swings after dealing a critical strike.",
"Increases your attack speed by 30% for your next 3 swings after dealing a critical strike."
		];
i++;		

//Toughness - Enhancement 
rank[i]=[
"Increases your armor value from items by 2%, and reduces the duration of movement slowing effects on you by 10%.",
"Increases your armor value from items by 4%, and reduces the duration of movement slowing effects on you by 20%.",
"Increases your armor value from items by 6%, and reduces the duration of movement slowing effects on you by 30%.",
"Increases your armor value from items by 8%, and reduces the duration of movement slowing effects on you by 40%.",
"Increases your armor value from items by 10%, and reduces the duration of movement slowing effects on you by 50%."
		];
i++;		

//Improved Rockbiter Weapon - Enhancement  
rank[i] = [
"Increases the melee attack power bonus of your Windfury Totem by 15% and increases the damage caused by your Flametongue Totem by 6%",
"Increases the melee attack power bonus of your Windfury Totem by 30% and increases the damage caused by your Flametongue Totem by 12%"
		];
i++;

//Spirit Weapons - Enhancement
rank[i]=[
"Gives a chance to parry enemy melee attacks and reduces the threat generated by your melee attacks by 30%."
			];
i++;			

//Elemental Weapons - Enhancement 

rank[i] = [
"Increases the damage caused by your Rockbiter Weapon by 7%, your Windfury Weapon effect by 13% and increases the damage caused by your Flametongue Weapon and Frostbrand Weapon by 5%.",
"Increases the damage caused by your Rockbiter Weapon by 14%, your Windfury Weapon effect by 27% and increases the damage caused by your Flametongue Weapon and Frostbrand Weapon by 10%.",
"Increases the damage caused by your Rockbiter Weapon by 20%, your Windfury Weapon effect by 40% and increases the damage caused by your Flametongue Weapon and Frostbrand Weapon by 15%."
		];
i++;
	
//Mental Quickness - Enhancement
rank[i]=[
"Reduces the mana cost of your instant cast spells by 2% and increases your spell damage and healing by an amount equal to 10% of your attack power.",
"Reduces the mana cost of your instant cast spells by 4% and increases your spell damage and healing by an amount equal to 20% of your attack power..",
"Reduces the mana cost of your instant cast spells by 6% and increases your spell damage and healing by an amount equal to 30% of your attack power.."
		];
i++;		
			
//Weapon Mastery - Enhancement
rank[i]=[
"Increases the damage you deal with all weapons by 2%.",
"Increases the damage you deal with all weapons by 4%.",
"Increases the damage you deal with all weapons by 6%.",
"Increases the damage you deal with all weapons by 8%.",
"Increases the damage you deal with all weapons by 10%."
		];
i++;		

//Dual Wield Specialization - Enhancement
rank[i]=[
"Increases your chance to hit while dual wielding by an additional 2%.",
"Increases your chance to hit while dual wielding by an additional 4%.",
"Increases your chance to hit while dual wielding by an additional 6%."
		];
i++;		

//Dual Wield - Enhancement
rank[i]=[
"Allows one-hand and off-hand weapons to be equipped in the off-hand."
		];
i++;		

//Stormstrike - Enhancement 
rank[i]=[
		"<span style=text-align:left;float:left;>236 Mana</span><span style=text-align:right;float:right;>Melee Range</span><br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>10 sec cooldown</span><br><span style=text-align:left;float:left;>Requires Melee Weapon</span><BR>Instantly attack with both weapons. In addition, the next 2 sources of Nature damage dealt to the target are increased by 20%. Lasts 12 sec."
		];
i++;		
			
//Unleashed Rage - Enhancement 

rank[i] = [
"Causes your critical hits with melee attacks to increase all party members' attack power by 2% if within 20 yards of the Shaman. Lasts 10 sec.",
"Causes your critical hits with melee attacks to increase all party members' attack power by 4% if within 20 yards of the Shaman. Lasts 10 sec.",
"Causes your critical hits with melee attacks to increase all party members' attack power by 6% if within 20 yards of the Shaman. Lasts 10 sec.",
"Causes your critical hits with melee attacks to increase all party members' attack power by 8% if within 20 yards of the Shaman. Lasts 10 sec.",
"Causes your critical hits with melee attacks to increase all party members' attack power by 10% if within 20 yards of the Shaman. Lasts 10 sec."

		];
i++;						

//Shamanistic Rage - Enhancement 
rank[i]=[
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>2 min cooldown</span><br>Reduces all damage taken by 30% and gives your successful melee attacks a chance to regenerate mana equal to 15% of your attack power.  Lasts 30 sec."
		];
i++;		

//Improved Healing Wave - Restoration 
rank[i]=[
"Reduces the casting time of your Healing Wave spell by 0.1 sec.",
"Reduces the casting time of your Healing Wave spell by 0.2 sec.",
"Reduces the casting time of your Healing Wave spell by 0.3 sec.",
"Reduces the casting time of your Healing Wave spell by 0.4 sec.",
"Reduces the casting time of your Healing Wave spell by 0.5 sec."
		];
i++;		
		
//Tidal Focus - Restoration 
rank[i]=[
"Reduces the Mana cost of your healing spells by 1%.",
"Reduces the Mana cost of your healing spells by 2%.",
"Reduces the Mana cost of your healing spells by 3%.",
"Reduces the Mana cost of your healing spells by 4%.",
"Reduces the Mana cost of your healing spells by 5%."
		];
i++;		
		
//Improved Reincarnation - Restoration 
rank[i]=[
"Reduces the cooldown of your Reincarnation spell by 10 min and increases the amount of health and mana you reincarnate with by an additional 10%.",
"Reduces the cooldown of your Reincarnation spell by 20 min and increases the amount of health and mana you reincarnate with by an additional 20%."
		];
i++;		
		
//Ancestral Healing - Restoration 
rank[i]=[
"Increases your target's armor value by 8% for 15 sec after getting a critical effect from one of your healing spells.",
"Increases your target's armor value by 16% for 15 sec after getting a critical effect from one of your healing spells.",
"Increases your target's armor value by 25% for 15 sec after getting a critical effect from one of your healing spells."
		];
i++;		
		
//Totemic Focus - Restoration
rank[i]=[
"Reduces the Mana cost of your totems by 5%.",
"Reduces the Mana cost of your totems by 10%.",
"Reduces the Mana cost of your totems by 15%.",
"Reduces the Mana cost of your totems by 20%.",
"Reduces the Mana cost of your totems by 25%."
		];
i++;		
		
//Nature's Guidance - Restoration      
rank[i]=[
"Increases your chance to hit with melee attacks and spells by 1%",
"Increases your chance to hit with melee attacks and spells by 2%",
"Increases your chance to hit with melee attacks and spells by 3%"
		];
i++;		
	
//Healing Focus - Restoration  
rank[i]=[
"Gives you a 14% chance to avoid interruption caused by damage while casting any Shaman healing spell.",
"Gives you a 28% chance to avoid interruption caused by damage while casting any Shaman healing spell.",
"Gives you a 42% chance to avoid interruption caused by damage while casting any Shaman healing spell.",
"Gives you a 56% chance to avoid interruption caused by damage while casting any Shaman healing spell.",
"Gives you a 70% chance to avoid interruption caused by damage while casting any Shaman healing spell."
		];
i++;		
		
//Improved Healing Stream Totem - Restoration 
rank[i]=[
"The radius of your totems that affect friendly targets is increased to 30 yd."
		];
i++;		

//Healing Grace - Restoration 
rank[i]=[
"Reduces the threat generated by your healing spells by 5% and reduces the chance your spells will be dispelled by 10%.",
"Reduces the threat generated by your healing spells by 10% and reduces the chance your spells will be dispelled by 20%.",
"Reduces the threat generated by your healing spells by 15% and reduces the chance your spells will be dispelled by 30%."
		];
i++;	

//Improved Mana Spring Totem - Restoration  
rank[i]=[
"Increases the effect of your Mana Spring and Healing Stream Totems by 5%.",
"Increases the effect of your Mana Spring and Healing Stream Totems by 10%.",
"Increases the effect of your Mana Spring and Healing Stream Totems by 15%.",
"Increases the effect of your Mana Spring and Healing Stream Totems by 20%.",
"Increases the effect of your Mana Spring and Healing Stream Totems by 25%."
		];
i++;	

		
//Tidal Mastery - Restoration 
rank[i]=[
"Increases the critical effect chance of your healing and lightning spells by 1%.",
"Increases the critical effect chance of your healing and lightning spells by 2%.",
"Increases the critical effect chance of your healing and lightning spells by 3%.",
"Increases the critical effect chance of your healing and lightning spells by 4%.",
"Increases the critical effect chance of your healing and lightning spells by 5%."
		];
i++;	
		
//Purification - Restoration  
rank[i]=[
"Your Healing Wave spells have a 33% chance to increase the effect of subsequent Healing Wave spells on that target by 6% for 15 sec. This effect will stack up to 3 times.",
"Your Healing Wave spells have a 66% chance to increase the effect of subsequent Healing Wave spells on that target by 6% for 15 sec. This effect will stack up to 3 times.",
"Your Healing Wave spells have a 100% chance to increase the effect of subsequent Healing Wave spells on that target by 6% for 15 sec. This effect will stack up to 3 times."
		];
i++;

//Nature's Swiftness - Restoration
rank[i]=[
		"<span style=text-align:left;float:left;>Instant</span><span style=text-align:right;float:right;>3 min cooldown</span><br>When activated, your next Nature spell with a casting time less then 10 sec becomes an instant cast spell."
		];
i++;	

//Focused Mind - Restoration  
rank[i]=[
"Reduces the duration of any Silence or Interrupt effects used against the Shaman by 10%. This effect does not stack with other similar effects.",
"Reduces the duration of any Silence or Interrupt effects used against the Shaman by 20%. This effect does not stack with other similar effects.",
"Reduces the duration of any Silence or Interrupt effects used against the Shaman by 30%. This effect does not stack with other similar effects."
		];
i++;	

//Purification - Restoration  
rank[i]=[
"Increases the effectiveness of your healing spells by 2%.",
"Increases the effectiveness of your healing spells by 4%.",
"Increases the effectiveness of your healing spells by 6%.",
"Increases the effectiveness of your healing spells by 8%.",
"Increases the effectiveness of your healing spells by 10%."
		];
i++;	


//Mana Tide Totem - Restoration 
rank[i]=[
		"88 Mana<br><span style=text-align:left;float:left;>Instant cast</span><span style=text-align:right;float:right;>5 min cooldown</span><br>Tools: Water Totem<br>Summons a Mana Tide Totem with 5 health at the feet of the caster for 12 sec that restores 6% of total mana every 3 seconds to group members within 20 yards."
		];
i++;	


//Nature's Guardian - Restoration  
rank[i]=[
"Whenever a damaging attack is taken that reduces you below 30% health, you have a 10% chance to heal 10% of your total health and reduce your threat level on that target. 5 second cooldown.",
"Whenever a damaging attack is taken that reduces you below 30% health, you have a 20% chance to heal 10% of your total health and reduce your threat level on that target. 5 second cooldown.",
"Whenever a damaging attack is taken that reduces you below 30% health, you have a 30% chance to heal 10% of your total health and reduce your threat level on that target. 5 second cooldown.",
"Whenever a damaging attack is taken that reduces you below 30% health, you have a 40% chance to heal 10% of your total health and reduce your threat level on that target. 5 second cooldown.",
"Whenever a damaging attack is taken that reduces you below 30% health, you have a 50% chance to heal 10% of your total health and reduce your threat level on that target. 5 second cooldown."
		];
i++;	
		
//Nature's Blessing - Restoration  
rank[i]=[
"Increases your spell damage and healing by an amount equal to 10% of your Intellect.",
"Increases your spell damage and healing by an amount equal to 20% of your Intellect.",
"Increases your spell damage and healing by an amount equal to 30% of your Intellect."
		];
i++;			
		
//Improved Chain Heal - Restoration  
rank[i]=[
"Increases the amount healed by your Chain Heal spell by 10%.",
"Increases the amount healed by your Chain Heal spell by 20%."
		];
i++;					
		
//Earth Shield - Restoration 
rank[i]=[
		"<span style=text-align:left;float:left;>600 Mana</span><span style=text-align:right;float:right;>40 yd range</span><br>Instant Cast<br>Protects the target with an earthen shield, giving a 30% chance of ignoring spell interruption when damaged and causing melee attacks to heal the shielded target for 150. This effect can only occur once every few seconds. 10 charges. Lasts 10 min. Earth Shield can only be placed on one target at a time and only one Elemental Shield can be active on a target at a time.<br><br>\
		&nbsp;Trainable Ranks Listed Below:<br>\
		&nbsp;Rank 2: 745 Mana, Heals for 205<br>\
		&nbsp;Rank 3: 900 Mana, Heals for 270"
				];
i++;			
		
//Restoration Talents End^^

