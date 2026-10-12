//CONSTRUCTOR

function RewardItem(playerFaction, itemName, itemIcon, itemMoneyPrice, itemHonorPrice, itemTokenPrice, itemCost, itemStats, itemHTML)
{													//Constructor for RewardItem datatype; accepts up to 7 arguments
  this.playerFaction	 		= playerFaction;					//string variable, can be "alliance", "horde" or "both"
  this.itemName		 	 			= itemName;								//string variable, contains the name shown in the rewards list
  this.itemIcon		 	 			= itemIcon;								//string variable, contains path to item icon to be used
  this.itemMoneyPrice			=	itemMoneyPrice;
  this.itemHonorPrice		 	= itemHonorPrice;					//how much the item costs, in HONOR POINTS
  this.itemTokenPrice			= itemTokenPrice;
  this.itemCost						= itemCost;
	this.itemStats		 			= itemStats;							//Array
  this.itemHTML			 			= itemHTML;								//string variable, contains the HTML code for the item
}

tokenIcons = new Array("sporeggar","arathi","nether","warsong");
//(thisObject.itemTokenPrice) ? processPrice(thisObject.itemHonorPrice[thisBracket],thisObject.itemTokenPrice[thisBracket]) : 
function selectBracket(thisObject,thisBracket)
{
  if (thisBracket >= 0)
  {
    if (thisObject.itemStats[thisBracket])
		{
			thisObject.itemCost = generateCostString(thisObject,thisBracket);
			thisObject.itemHTML = thisObject.itemStats[thisBracket];
		}
    else
		{
			thisObject.itemHTML = "none";
			thisObject.itemCost = "none";
			//selectBracket(thisObject,thisBracket-1);
		}
  }
}

function generateCostString(thisObject,thisBracket)
{
	outPutString = "";
	if(thisObject.itemMoneyPrice && thisObject.itemMoneyPrice[thisBracket])
	{
		copperPart = thisObject.itemMoneyPrice[thisBracket];
		goldPart = Math.floor(copperPart / 10000);
		if (goldPart >= 1) copperPart -= goldPart * 10000;
		silverPart = Math.floor(copperPart / 100);
		if (silverPart >= 1) copperPart -= silverPart * 100;
		if (goldPart > 0) outPutString += goldPart+"<img src='/shared/wow-com/images/basics/factions/gold.gif'>&nbsp;";
		if (silverPart > 0) outPutString += silverPart+"<img src='/shared/wow-com/images/basics/factions/silver.gif'>&nbsp;";
		if (copperPart > 0) outPutString += copperPart+"<img src='/shared/wow-com/images/basics/factions/copper.gif'>&nbsp;";
	}
	if(thisObject.itemHonorPrice && thisObject.itemHonorPrice[thisBracket])
	{
		outPutString += thisObject.itemHonorPrice[thisBracket]+"<img src='/shared/wow-com/images/basics/factions/"+thisObject.playerFaction+"-honor.gif'>&nbsp;";
	}
	if(thisObject.itemTokenPrice && thisObject.itemTokenPrice[thisBracket])
	{
		for(carl=0; carl<thisObject.itemTokenPrice[thisBracket].length; carl++)
		{
			if (thisObject.itemTokenPrice[thisBracket][carl] > 0) outPutString += thisObject.itemTokenPrice[thisBracket][carl]+"<img src='/shared/wow-com/images/basics/factions/"+tokenIcons[carl]+".gif'>&nbsp;";
		}
	}
	return outPutString;
}

//------BEGIN REWARDS DEFINITION------
i = 0;
var RewardItems = new Array();

var fRecipeDesignInsightfulEarthstormDiamond = new RewardItem("alliance","Design: Insightful Earthstorm Diamond","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fRecipeDesignInsightfulEarthstormDiamond.itemMoneyPrice = new Array();
fRecipeDesignInsightfulEarthstormDiamond.itemMoneyPrice[0] = 120000
fRecipeDesignInsightfulEarthstormDiamond.itemStats = new Array();
fRecipeDesignInsightfulEarthstormDiamond.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Design: Insightful Earthstorm Diamond<br>Binds when picked up<br>Requires Jewelcrafting (365)<br>\
Requires The Sha'tar - Friendly<br> Use: Teaches you how to cut an Insightful Earthstorm Diamond.<br>\
<br>\
<span class=\"myBlue\">Insightful Earthstorm Diamond</span><br>\
+12 Intellect & Chance to restore mana on spellcast<br>\
<span class=\"myGray\">Requires at least 5 Red gems<br>Requires at least 5 Yellow gems<br>Requires at least 5 Blue gems<br></span>\
<span class=\"myYellow\">\"Only fits in a meta gem slot.\"</span><br>\
<br>Requires Earthstorm Diamond</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeDesignInsightfulEarthstormDiamond; ++i;

var fFormulaEnchantGlovesMajorHealing = new RewardItem("alliance","Formula: Enchant Gloves - Major Healing","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantGlovesMajorHealing.itemMoneyPrice = new Array();
fFormulaEnchantGlovesMajorHealing.itemMoneyPrice[1] = 60000
fFormulaEnchantGlovesMajorHealing.itemStats = new Array();
fFormulaEnchantGlovesMajorHealing.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Gloves - Major Healing</span>\
<br>Binds when picked up<br>Requires Enchanting (350)<br>Requires The Sha'tar - Honored<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant gloves to increase Healing by 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantGlovesMajorHealing; ++i;


var fGlyphOfArcaneWarding = new RewardItem("alliance","Glyph of Arcane Warding","/info/basics/factions/images/icons/Spell_Arcane_ArcaneResilien.gif");
fGlyphOfArcaneWarding.itemMoneyPrice = new Array();
fGlyphOfArcaneWarding.itemMoneyPrice[1] = 1000000
fGlyphOfArcaneWarding.itemStats = new Array();
fGlyphOfArcaneWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of Arcane Warding</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Sha'tar - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 20 Arcane resistance to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfArcaneWarding; ++i;



var fWarpforgedKey = new RewardItem("alliance","Warpforged Key","/info/basics/factions/images/icons/INV_Misc_Key_09.gif");
fWarpforgedKey.itemMoneyPrice = new Array();
fWarpforgedKey.itemMoneyPrice[1] = 100000
fWarpforgedKey.itemStats = new Array();
fWarpforgedKey.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Warpforged Key<br>Binds when picked up<br>Unique<br>Requires The Sha'tar - Honored<br>\
<span class=\"myYellow\">\"Unlocks Heroic Difficulty for Tempest Keep dungeons.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarpforgedKey; ++i;

var fRecipeTransmutePrimalAirToFire = new RewardItem("alliance","Recipe: Transmute Primal Air to Fire","/info/basics/factions/images/icons/INV_Scroll_06.gif");
fRecipeTransmutePrimalAirToFire.itemMoneyPrice = new Array();
fRecipeTransmutePrimalAirToFire.itemMoneyPrice[2] = 80000
fRecipeTransmutePrimalAirToFire.itemStats = new Array();
fRecipeTransmutePrimalAirToFire.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Transmute Primal Air to Fire</span><br>\
<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires The Sha'tar - Revered<br>Use: Teaches you how to Transmute Primal Air into Primal Fire.<br>\
<br>\
<span class=\"myGreen\">Primal Fire</span>\
<br>Requires Primal Air</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmutePrimalAirToFire; ++i;

var fFormulaEnchantRingHealingPower = new RewardItem("alliance","Formula: Enchant Ring - Healing Power","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantRingHealingPower.itemMoneyPrice = new Array();
fFormulaEnchantRingHealingPower.itemMoneyPrice[2] = 100000
fFormulaEnchantRingHealingPower.itemStats = new Array();
fFormulaEnchantRingHealingPower.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Formula: Enchant Ring - Healing Power<br>Binds when picked up<br>Requires Enchanting (370)<br>Requires The Sha'tar - Revered<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a ring to increase healing spell effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantRingHealingPower; ++i;

var fDesignRingOfArcaneShielding = new RewardItem("alliance","Design: Ring of Arcane Shielding","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fDesignRingOfArcaneShielding.itemMoneyPrice = new Array();
fDesignRingOfArcaneShielding.itemMoneyPrice[1] = 120000
fDesignRingOfArcaneShielding.itemStats = new Array();
fDesignRingOfArcaneShielding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Ring of Arcane Shielding</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (360)<br>Requires The Sha'tar - Honored<br>Use: Teaches you how to craft a Ring of Arcane Shielding.<br>\
<br>\
<span class=\"myBlue\">Ring of Arcane Shielding</span>\
<br>Binds when equipped<br>Unique<br>Finger<br>+12 Stamina<br>+30 Arcane Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 8.</span><br>\
<br>Requires Eternium Bar (2), Primal Mana (8)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignRingOfArcaneShielding; ++i;

var fDesignTalasiteOwl = new RewardItem("alliance","Design: Talasite Owl","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fDesignTalasiteOwl.itemMoneyPrice = new Array();
fDesignTalasiteOwl.itemMoneyPrice[2] = 120000
fDesignTalasiteOwl.itemStats = new Array();
fDesignTalasiteOwl.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Talasite Owl</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (370)<br>Requires The Sha'tar - Revered<br>Use: Teaches you how to craft a Talasite Owl.<br>\
<br>\
<span class=\"myBlue\">Figurine - Talasite Owl</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Restores 14 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Use: Restores 900 mana over 12 sec.</span><br>\
<br>Requires Eternium Bar (2), Talasite (2), Primal Mana (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignTalasiteOwl; ++i;

var fBlessedScaleGirdle = new RewardItem("alliance","Blessed Scale Girdle","/info/basics/factions/images/icons/INV_Belt_08.gif");
fBlessedScaleGirdle.itemMoneyPrice = new Array();
fBlessedScaleGirdle.itemMoneyPrice[2] = 130288
fBlessedScaleGirdle.itemStats = new Array();
fBlessedScaleGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Blessed Scale Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>367 Armor<br>+20 Agility<br>+15 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>Requires The Sha'tar - Revered<br>\
<span class=\"myGreen\">Equip: Increases attack power by 70.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBlessedScaleGirdle; ++i;

var fXirisGift = new RewardItem("alliance","Xi'ri's Gift","/info/basics/factions/images/icons/INV_misc_elvencoins.gif");
fXirisGift.itemMoneyPrice = new Array();
fXirisGift.itemMoneyPrice[2] = 175952
fXirisGift.itemStats = new Array();
fXirisGift.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Xi'ri's Gift</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>Requires The Sha'tar - Revered<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Use: Increases spell damage by up to 150 and healing by up to 280 for 15 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fXirisGift; ++i;

var fFormulaEnchantWeaponMajorHealing = new RewardItem("alliance","Formula: Enchant Weapon - Major Healing","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantWeaponMajorHealing.itemMoneyPrice = new Array();
fFormulaEnchantWeaponMajorHealing.itemMoneyPrice[2] = 60000
fFormulaEnchantWeaponMajorHealing.itemStats = new Array();
fFormulaEnchantWeaponMajorHealing.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Weapon - Major Healing</span>\
<br>Binds when picked up<br>Requires Enchanting (350)<br>Requires The Sha'tar - Revered<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a melee weapon to increase healing by 81.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantWeaponMajorHealing; ++i;

var fRecipeAlchemistsStone = new RewardItem("alliance","Recipe: Alchemist's Stone","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fRecipeAlchemistsStone.itemMoneyPrice = new Array();
fRecipeAlchemistsStone.itemMoneyPrice[2] = 80000
fRecipeAlchemistsStone.itemStats = new Array();
fRecipeAlchemistsStone.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Recipe: Alchemist's Stone<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires The Sha'tar - Revered<br>Use: Teaches you how to make an Alchemist's Stone.<br>\
<br>\
<span class=\"myPurple\">Alchemist's Stone</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+15 Strength<br>+15 Agility<br>+15 Stamina<br>+15 Intellect<br>+15 Spirit<br>Requires Alchemy (350)<br>\
<span class=\"myGreen\">Equip: Increases the effect that healing and mana potions have on the wearer by 40%.</span>\
<br><br>Requires Philosopher's Stone, Earthstorm Diamond, Skyfire Diamond, Fel Lotus (2), Primal Might (5)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeAlchemistsStone; ++i;

var fGlyphOfPower = new RewardItem("alliance","Glyph of Power","/info/basics/factions/images/icons/Spell_Nature_Lightning.gif");
fGlyphOfPower.itemMoneyPrice = new Array();
fGlyphOfPower.itemMoneyPrice[2] = 1000000
fGlyphOfPower.itemStats = new Array();
fGlyphOfPower.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of Power</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Sha'tar - Revered<br>\
<span class=\"myGreen\">Use: Permanently adds up to 22 spell damage and healing and 14 spell hit rating to a head slot item. Does not stack with other\
enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfPower; ++i;

var fPatternDrumsOfBattle = new RewardItem("alliance","Pattern: Drums of Battle","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternDrumsOfBattle.itemMoneyPrice = new Array();
fPatternDrumsOfBattle.itemMoneyPrice[3] = 120000
fPatternDrumsOfBattle.itemStats = new Array();
fPatternDrumsOfBattle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Drums of Battle</span>\
<br>Binds when picked up<br>Requires Leatherworking (365)<br>Requires The Sha'tar - Exalted<br>Use: Teaches you how to make Drums of Battle.<br>\
<br>\
<span class=\"myBlue\">Drums of Battle</span>\
<br>Requires Leatherworking (350)<br>\
<span class=\"myGreen\">Use: Increases attack and casting speed rating on nearby party members by 80.  Lasts 30 sec.<br>30 Charges</span>\
<br><br>Requires Heavy Knothide Leather (2), Primal Fire, Primal Earth</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternDrumsOfBattle; ++i;

var fRecipeFlaskOfTheTitans = new RewardItem("alliance","Recipe: Flask of the Titans","/info/basics/factions/images/icons/INV_Scroll_06.gif");
fRecipeFlaskOfTheTitans.itemMoneyPrice = new Array();
fRecipeFlaskOfTheTitans.itemMoneyPrice[3] = 40000
fRecipeFlaskOfTheTitans.itemStats = new Array();
fRecipeFlaskOfTheTitans.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Flask of the Titans</span>\
<br>Requires Alchemy (300)<br>Use: Teaches you how to make a Flask of the Titans.<br>\
<br>Flask of the Titans<br>Requires Level 50<br>\
<span class=\"myGreen\">Use: Increases the player's maximum health by 400 for 2 hours.  Counts as both a Battle and Guardian elixir.  This effect persists through death.</span>\
<br><br>Requires Gromsblood (30), Stonescale Oil (10), Black Lotus, Crystal Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeFlaskOfTheTitans; ++i;

var fAdalsCommand = new RewardItem("alliance","A'dal's Command","/info/basics/factions/images/icons/INV_Jewelry_Ring_48.gif");
fAdalsCommand.itemMoneyPrice = new Array();
fAdalsCommand.itemMoneyPrice[3] = 790112
fAdalsCommand.itemStats = new Array();
fAdalsCommand.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">A'dal's Command</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+29 Strength<br>+16 Agility<br>+18 Stamina<br>Requires Level 70<br>Requires The Sha'tar - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAdalsCommand; ++i;

var fCrestOfTheShatar = new RewardItem("alliance","Crest of the Sha'tar","/info/basics/factions/images/icons/INV_Shield_30.gif");
fCrestOfTheShatar.itemMoneyPrice = new Array();
fCrestOfTheShatar.itemMoneyPrice[3] = 1229537
fCrestOfTheShatar.itemStats = new Array();
fCrestOfTheShatar.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Crest of the Sha'tar</span>\
<br>Binds when picked up<br>Unique<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>4465 Armor<br>108 Block<br>+19 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +3 Dodge Rating</span>\
<br>Durability 120 / 120<br>Requires Level 70<br>Requires The Sha'tar - Exalted<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 24.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCrestOfTheShatar; ++i;

var fGavelOfPureLight = new RewardItem("alliance","Gavel of Pure Light","/pvp/images/honorweapons/grandmarshalsbonegrinder.gif");
fGavelOfPureLight.itemMoneyPrice = new Array();
fGavelOfPureLight.itemMoneyPrice[3] = 1913844
fGavelOfPureLight.itemStats = new Array();
fGavelOfPureLight.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gavel of Pure Light</span>\
<br>Binds when picked up<br>Unique<br>Main Hand<span class=\"myRight\">Mace</span>\
<br>32 - 126 Damage<span class=\"myRight\">Speed 1.90</span>\
<br>(41.5 damage per second)<br>+12 Stamina<br>+12 Intellect<br>Durability 105 / 105<br>Requires Level 70<br>Requires The Sha'tar - Exalted<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 299.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGavelOfPureLight; ++i;

var fShatarTabard = new RewardItem("alliance","Sha'tar Tabard","/shared/wow-com/images/basics/factions/alteracvalley/stormpikebattletabard.gif");
fShatarTabard.itemMoneyPrice = new Array();
fShatarTabard.itemMoneyPrice[3] = 10000
fShatarTabard.itemStats = new Array();
fShatarTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Sha'tar Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires The Sha'tar - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fShatarTabard; ++i;



//-------------------------------------------------------------------
//---Horde below







//------END REWARDS DEFINITION------
