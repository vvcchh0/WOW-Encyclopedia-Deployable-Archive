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

tokenIcons = new Array("alterac","arathi","nether","warsong");
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
//			selectBracket(thisObject,thisBracket-1);
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

var fDesignEnigmaticSkyfireDiamond = new RewardItem("alliance","Design: Enigmatic Skyfire Diamond","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fDesignEnigmaticSkyfireDiamond.itemMoneyPrice = new Array();
fDesignEnigmaticSkyfireDiamond.itemMoneyPrice[1] = 120000
fDesignEnigmaticSkyfireDiamond.itemStats = new Array();
fDesignEnigmaticSkyfireDiamond.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Design: Enigmatic Skyfire Diamond<br>Binds when picked up<br>Requires Jewelcrafting (365)<br>Requires Keepers of Time - Honored<br>Use: Teaches you how to cut an Enigmatic Skyfire Diamond.<br>\
<br>\
<span class=\"myBlue\">Enigmatic Skyfire Diamond</span>\
<br>+12 Critical Strike Rating & 5% Snare and Root Resist<br>\
<span class=\"myYellow\">\"Only fits in a meta gem slot.\"</span>\
<br>\
<br>Requires Skyfire Diamond</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignEnigmaticSkyfireDiamond; ++i;


var fGlyphOfFrostWarding = new RewardItem("alliance","Glyph of Frost Warding","/info/basics/factions/images/icons/Spell_Frost_FrostArmor02.gif");
fGlyphOfFrostWarding.itemMoneyPrice = new Array();
fGlyphOfFrostWarding.itemMoneyPrice[1] = 1000000
fGlyphOfFrostWarding.itemStats = new Array();
fGlyphOfFrostWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of Frost Warding</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Keepers of Time - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 20 Frost resistance to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfFrostWarding; ++i;

var fFormulaEnchantRingSpellpower = new RewardItem("alliance","Formula: Enchant Ring - Spellpower","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantRingSpellpower.itemMoneyPrice = new Array();
fFormulaEnchantRingSpellpower.itemMoneyPrice[1] = 100000
fFormulaEnchantRingSpellpower.itemStats = new Array();
fFormulaEnchantRingSpellpower.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Formula: Enchant Ring - Spellpower<br>Binds when picked up<br>Requires Enchanting (360)<br>Requires Keepers of Time - Honored<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a ring to increase spell damage and healing by up to 12.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantRingSpellpower; ++i;

var fFormulaEnchantGlovesMajorSpellpower = new RewardItem("alliance","Formula: Enchant Gloves - Major Spellpower","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantGlovesMajorSpellpower.itemMoneyPrice = new Array();
fFormulaEnchantGlovesMajorSpellpower.itemMoneyPrice[1] = 80000
fFormulaEnchantGlovesMajorSpellpower.itemStats = new Array();
fFormulaEnchantGlovesMajorSpellpower.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Gloves - Major Spellpower</span>\
<br>Binds when picked up<br>Requires Enchanting (360)<br>Requires Keepers of Time - Honored<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant gloves to increase spell damage and healing by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantGlovesMajorSpellpower; ++i;

var fDesignLivingRubySerpent = new RewardItem("alliance","Design: Living Ruby Serpent","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fDesignLivingRubySerpent.itemMoneyPrice = new Array();
fDesignLivingRubySerpent.itemMoneyPrice[2] = 120000
fDesignLivingRubySerpent.itemStats = new Array();
fDesignLivingRubySerpent.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Living Ruby Serpent</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (370)<br>Requires Keepers of Time - Revered<br>Use: Teaches you how to craft a Living Ruby Serpent.<br>\
<br>\
<span class=\"myBlue\">Figurine - Living Ruby Serpent</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+33 Stamina<br>+23 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Use: Increases damage and healing done by magical spells and effects by up to 150 for 20 sec.</span>\
<br>\
<br>Requires Felsteel Bar (2), Living Ruby (2), Primal Fire (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignLivingRubySerpent; ++i;

var fDesignPendantOfFrozenFlame = new RewardItem("alliance","Design: Pendant of Frozen Flame","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fDesignPendantOfFrozenFlame.itemMoneyPrice = new Array();
fDesignPendantOfFrozenFlame.itemMoneyPrice[2] = 120000
fDesignPendantOfFrozenFlame.itemStats = new Array();
fDesignPendantOfFrozenFlame.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Pendant of Frozen Flame</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (360)<br>Requires Keepers of Time - Revered<br>Use: Teaches you how to craft a Pendant of Frozen Flame.<br>\
<br>\
<span class=\"myBlue\">Pendant of Frozen Flame</span>\
<br>Binds when equipped<br>Neck<br>+18 Stamina<br>+30 Fire Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Use: Absorbs 900 to 2700 fire damage on all nearby party members.  Lasts 5 mins.<br>10 Charges</span>\
<br>\
<br>Requires Felsteel Bar (2), Primal Water (6), Primal Fire (4), Mercurial Adamantite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignPendantOfFrozenFlame; ++i;

var fKeyOfTime = new RewardItem("alliance","Key of Time","/info/basics/factions/images/icons/INV_Misc_Key_04.gif");
fKeyOfTime.itemMoneyPrice = new Array();
fKeyOfTime.itemMoneyPrice[1] = 100000
fKeyOfTime.itemStats = new Array();
fKeyOfTime.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Key of Time<br>Binds when picked up<br>Unique<br>Requires Keepers of Time - Honored<br>\
<span class=\"myYellow\">\"Unlocks Heroic Difficulty for Caverns of Time dungeons.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fKeyOfTime; ++i;

var fGlyphOfTheDefender = new RewardItem("alliance","Glyph of the Defender","/info/basics/factions/images/icons/Ability_Warrior_VictoryRush.gif");
fGlyphOfTheDefender.itemMoneyPrice = new Array();
fGlyphOfTheDefender.itemMoneyPrice[2] = 1000000
fGlyphOfTheDefender.itemStats = new Array();
fGlyphOfTheDefender.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of the Defender</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Keepers of Time - Revered<br>\
<span class=\"myGreen\">Use: Permanently adds 16 defense rating and 17 dodge rating to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfTheDefender; ++i;

var fTimewardensLeggings = new RewardItem("alliance","Timewarden's Leggings","/info/basics/factions/images/icons/INV_Pants_Plate_10.gif");
fTimewardensLeggings.itemMoneyPrice = new Array();
fTimewardensLeggings.itemMoneyPrice[2] = 308501
fTimewardensLeggings.itemStats = new Array();
fTimewardensLeggings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Timewarden's Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+57 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Block Value</span>\
<br>Durability 100 / 100<br>Requires Level 70<br>Requires Keepers of Time - Revered<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 18.</span>\
<br>\
<span class=\"myGreen\">Increases your dodge rating by 11.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTimewardensLeggings; ++i;

var fContinuumBlade = new RewardItem("alliance","Continuum Blade","/pvp/images/honorweapons/grandmarshalslongsword.gif");
fContinuumBlade.itemMoneyPrice = new Array();
fContinuumBlade.itemMoneyPrice[2] = 442344
fContinuumBlade.itemStats = new Array();
fContinuumBlade.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Continuum Blade</span>\
<br>Binds when picked up<br>Unique<br>Main Hand<span class=\"myRight\">Sword</span>\
<br>35 - 114 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(41.4 damage per second)<br>+30 Stamina<br>+11 Intellect<br>Durability 90 / 90<br>Requires Level 70<br>Requires Keepers of Time - Revered<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 121.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fContinuumBlade; ++i;

var fPatternDrumsOfPanic = new RewardItem("alliance","Pattern: Drums of Panic","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternDrumsOfPanic.itemMoneyPrice = new Array();
fPatternDrumsOfPanic.itemMoneyPrice[3] = 120000
fPatternDrumsOfPanic.itemStats = new Array();
fPatternDrumsOfPanic.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Drums of Panic</span>\
<br>Binds when picked up<br>Requires Leatherworking (370)<br>Requires Keepers of Time - Exalted<br>Use: Teaches you how to make Drums of Panic.<br>\
<br>\
<span class=\"myGreen\">Drums of Panic</span>\
<br>Requires Leatherworking (350)<br>\
<span class=\"myGreen\">Use: Unearthly rhythms cause 5 enemies within 5 yds to flee in terror for 2 sec.<br>30 Charges</span>\
<br>\
<br>Requires Heavy Knothide Leather (2), Primal Shadow (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternDrumsOfPanic; ++i;

var fRecipeFlaskOfSupremePower = new RewardItem("alliance","Recipe: Flask of Supreme Power","/info/basics/factions/images/icons/INV_Scroll_06.gif");
fRecipeFlaskOfSupremePower.itemMoneyPrice = new Array();
fRecipeFlaskOfSupremePower.itemMoneyPrice[3] = 40000
fRecipeFlaskOfSupremePower.itemStats = new Array();
fRecipeFlaskOfSupremePower.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Flask of Supreme Power</span>\
<br>Requires Alchemy (300)<br>Requires Keepers of Time - Exalted<br>Use: Teaches you how to make a Flask of Supreme Power.<br>\
<br>Flask of Supreme Power<br>Requires Level 50<br>\
<span class=\"myGreen\">Use: Increases damage done by magical spells and effects by up to 70 for 2 hours.  Counts as both a Battle and Guardian Elixir.  This effect persists through death.</span>\
<br>\
<br>Requires Dreamfoil (30), Mountain Silversage (10), Black Lotus, Crystal Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeFlaskOfSupremePower; ++i;

var fFormulaEnchantGlovesSuperiorAgility = new RewardItem("alliance","Formula: Enchant Gloves - Superior Agility","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantGlovesSuperiorAgility.itemMoneyPrice = new Array();
fFormulaEnchantGlovesSuperiorAgility.itemMoneyPrice[3] = 90000
fFormulaEnchantGlovesSuperiorAgility.itemStats = new Array();
fFormulaEnchantGlovesSuperiorAgility.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Gloves - Superior Agility</span>\
<br>Binds when picked up<br>Requires Enchanting (300)<br>Requires Keepers of Time - Exalted<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant gloves to increase Agility by 15.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantGlovesSuperiorAgility; ++i;

var fRiftmaker = new RewardItem("alliance","Riftmaker","/pvp/images/honorweapons/grandmarshalsdirk.gif");
fRiftmaker.itemMoneyPrice = new Array();
fRiftmaker.itemMoneyPrice[3] = 1964608
fRiftmaker.itemStats = new Array();
fRiftmaker.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Riftmaker</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>117 - 176 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(81.4 damage per second)<br>+21 Agility<br>Durability 75 / 75<br>Requires Level 70<br>Requires Keepers of Time - Exalted<br>\
<span class=\"myGreen\">Chance on hit: Encloses enemy in a temporal rift, increasing the time between their attacks by 10% for 10 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRiftmaker; ++i;

var fTimelapseShard = new RewardItem("alliance","Timelapse Shard","/info/basics/factions/images/icons/INV_DataCrystal02.gif");
fTimelapseShard.itemMoneyPrice = new Array();
fTimelapseShard.itemMoneyPrice[3] = 790112
fTimelapseShard.itemStats = new Array();
fTimelapseShard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Timelapse Shard</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+27 Stamina<br>Requires Level 70<br>Requires Keepers of Time - Exalted<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Use: Reduces your threat to enemy targets within 30 yards, making them less likely to attack you.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTimelapseShard; ++i;

var fBindingsOfTheTimewalker = new RewardItem("alliance","Bindings of the Timewalker","/info/basics/factions/images/icons/INV_Bracer_10.gif");
fBindingsOfTheTimewalker.itemMoneyPrice = new Array();
fBindingsOfTheTimewalker.itemMoneyPrice[3] = 394383
fBindingsOfTheTimewalker.itemStats = new Array();
fBindingsOfTheTimewalker.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bindings of the Timewalker</span>\
<br>Binds when picked up<br>Unique<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>78 Armor<br>+24 Stamina<br>+12 Intellect<br>Durability 35 / 35<br>Requires Level 70<br>Requires Keepers of Time - Exalted<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 64.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBindingsOfTheTimewalker; ++i;


//-------------------------------------------------------------------
//---Horde below








//------END REWARDS DEFINITION------
