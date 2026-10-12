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

var fDesignEnduringDeepPeridot = new RewardItem("alliance","Design: Enduring Deep Peridot","/info/basics/factions/images/icons/INV_Scroll_06.gif");
fDesignEnduringDeepPeridot.itemMoneyPrice = new Array();
fDesignEnduringDeepPeridot.itemMoneyPrice[0] = 60000
fDesignEnduringDeepPeridot.itemStats = new Array();
fDesignEnduringDeepPeridot.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myGreen\">Design: Enduring Deep Peridot</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (315)<br>Requires Honor Hold - Friendly<br>Use: Teaches you how to cut an Enduring Deep Peridot.<br>\
<br>\
<span class=\"myGreen\">Enduring Deep Peridot</span>\
<br>+3 Defense Rating and +4 Stamina<br>\
<span class=\"myYellow\">\"Matches a Yellow or Blue Socket.\"</span></span>\
<br><br>Requires Deep Peridot</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignEnduringDeepPeridot; ++i;

var fPatternFelstalkerBelt = new RewardItem("alliance","Pattern: Felstalker Belt","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternFelstalkerBelt.itemMoneyPrice = new Array();
fPatternFelstalkerBelt.itemMoneyPrice[0] = 120000
fPatternFelstalkerBelt.itemStats = new Array();
fPatternFelstalkerBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Pattern: Felstalker Belt</span>\
<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires Honor Hold - Friendly<br>Use: Teaches you how to make a Felstalker Belt.<br>\
<br>\
<span class=\"myBlue\">Felstalker Belt</span>\
<br>Binds when equipped<br>Waist<span class=\"myRight\">Mail</span>\
<br>357 Armor<br>+18 Agility<br>+17 Intellect<br>\
<span class=\"myRedGem\">Red Socket</span>\
<span class=\"myBlueGem\">Blue Socket</span>\
<span class=\"myGray\">Socket Bonus: +4 Stamina<br></span>\
Durability 40 / 40<br>Requires Level 69<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span><br>\
<br>\
<span class=\"myYellow\">Felstalker Armor (0/3)</span>\
<br>Requires Leatherworking (350)<br> <br> <span class=\"myGray\">Felstalker Belt<br> Felstalker Bracers<br> Felstalker Breastplate</span><br>\
<br><span class=\"myGray\">(3) Set: Increases your hit rating by 20.</span><br>\
<br>Requires Heavy Knothide Leather (6), Fel Hide (4), Crystal Infused Leather (8), Primal Air (6), Rune Thread (2)</span>\
</div></div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelstalkerBelt; ++i;


var fFootmansWaterskin = new RewardItem("alliance","Footman's Waterskin","/info/basics/factions/images/icons/INV_Drink_Waterskin_05.gif");
fFootmansWaterskin.itemMoneyPrice = new Array();
fFootmansWaterskin.itemMoneyPrice[0] = 2000
fFootmansWaterskin.itemStats = new Array();
fFootmansWaterskin.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Footman's Waterskin<br>Binds when picked up<br>Unique (20)<br>Requires Level 55<br>Requires Honor Hold - Friendly<br>\
<span class=\"myGreen\">Use: Restores 4200 mana over 30 sec.  Must remain seated while drinking.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFootmansWaterskin; ++i;

var fDriedMushroomRations = new RewardItem("alliance","Dried Mushroom Rations","/info/basics/factions/images/icons/INV_Mushroom_01.gif");
fDriedMushroomRations.itemMoneyPrice = new Array();
fDriedMushroomRations.itemMoneyPrice[0] = 4500
fDriedMushroomRations.itemStats = new Array();
fDriedMushroomRations.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Dried Mushroom Rations<br>Binds when picked up<br>Unique (20)<br>Requires Level 55<br>Requires Honor Hold - Friendly<br>\
<span class=\"myGreen\">Use: Restores 4320 health over 30 sec.   Must remain seated while eating.   Also increases your Stamina by 10 for 10 min. </span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDriedMushroomRations; ++i;

var fFormulaEnchantBracerSuperiorHealing= new RewardItem("alliance","Formula: Enchant - Superior Healing","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantBracerSuperiorHealing.itemMoneyPrice = new Array();
fFormulaEnchantBracerSuperiorHealing.itemMoneyPrice[0] = 60000
fFormulaEnchantBracerSuperiorHealing.itemStats = new Array();
fFormulaEnchantBracerSuperiorHealing.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Formula: Enchant Bracer - Superior Healing<br>Requires Enchanting (325)<br>Requires Honor Hold - Friendly<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a bracer to increase the effect of healing spells by up to 30.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantBracerSuperiorHealing; ++i;

var fRecipeElixirOfMajorAgility = new RewardItem("alliance","Recipe: Elixir of Agility","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fRecipeElixirOfMajorAgility.itemMoneyPrice = new Array();
fRecipeElixirOfMajorAgility.itemMoneyPrice[1] = 50000
fRecipeElixirOfMajorAgility.itemStats = new Array();
fRecipeElixirOfMajorAgility.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
Recipe: Elixir of Agility<br>Requires Alchemy (330)<br>Requires Honor Hold - Honored<br>Use: Teaches you how to make an Elixir of Agility.<br>\
<br>\
<b>Elixir of Agility</b><br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Increases your Agility by 35 and your critical strike rating by 20 for 1 Hour. Battle Elixir.</span></span>\
<br>Requires Terocone, Felweed (2), Imbued Vial\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeElixirOfMajorAgility; ++i;


var fFormulaEnchantChestExceptionalStats = new RewardItem("alliance","Formula: Enchant - Exceptional Stats","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantChestExceptionalStats.itemMoneyPrice = new Array();
fFormulaEnchantChestExceptionalStats.itemMoneyPrice[2] = 60000
fFormulaEnchantChestExceptionalStats.itemStats = new Array();
fFormulaEnchantChestExceptionalStats.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Formula: Enchant Chest - Exceptional Stats<br>Binds when picked up<br>Requires Enchanting (345)<br>Requires Honor Hold - Revered<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant chest armor to increase all stats by 6.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantChestExceptionalStats; ++i;

var fPlansFelsteelShieldSpike = new RewardItem("alliance","Plans: Felsteel Shield Spike","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fPlansFelsteelShieldSpike.itemMoneyPrice = new Array();
fPlansFelsteelShieldSpike.itemMoneyPrice[3] = 60000
fPlansFelsteelShieldSpike.itemStats = new Array();
fPlansFelsteelShieldSpike.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\">Plans: Felsteel Shield Spike<br>Binds when picked up<br>Requires Blacksmithing (360)<br>Requires Honor Hold - Exalted<br>Use: Teaches you how to make a Felsteel Shield Spike.<br>\
<br>\
<span class=\"myGreen\"><b>Felsteel Shield Spike</b></span>\
<br>Requires Blacksmithing (350)<br>\
<span class=\"myGreen\">Use: Attaches a Felsteel Spike to your shield that deals 26-38 damage every time you block with it.</span>\
<br>Requires Felsteel Bar (4), Primal Fire (4), Primal Earth (4)</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansFelsteelShieldSpike; ++i;



var fPatternFelstalkerBracers = new RewardItem("alliance","Pattern: Felstalker Bracers","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternFelstalkerBracers.itemMoneyPrice = new Array();
fPatternFelstalkerBracers.itemMoneyPrice[1] = 160000
fPatternFelstalkerBracers.itemStats = new Array();
fPatternFelstalkerBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
	<tr>\
		<td>\
			<div class=\"myTable\">\
				<span class=\"myBlue\">Pattern: Felstalker Bracers</span>\
				<br>Binds when picked up<br>\
				Requires Leatherworking (360)<br>\
				Requires Honor Hold - Honored<br>\
				Use: Teaches you how to make Felstalker Bracers.<br>\
				<br>\
				<span class=\"myBlue\">Felstalker Bracers</span>\
				<br>Binds when equipped<br>\
				Wrist<span class=\"myRight\">Mail</span>\
				<br>283 Armor<br>\
				+18 Agility<br>\
				+11 Intellect<br>\
				<span class='myBlueGem'>Blue Socket</span>\
				<span class='myGray'>Socket Bonus: +3 Stamina</span><br>\
				<br>Durability 40 / 40<br>\
				Requires Level 70<br>\
				<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
				<br>\
				<br>\
<span class=\"myYellow\">Felstalker Armor (0/3)</span>\
<br>Requires Leatherworking (350)<br> <br> <span class=\"myGray\">Felstalker Belt<br> Felstalker Bracers<br> Felstalker Breastplate</span><br>\
<br><span class=\"myGray\">(3) Set: Increases your hit rating by 20.</span><br>\
				<br>Requires Heavy Knothide Leather (6), Fel Hide (6), Crystal Infused Leather (6), Primal Air (4), Rune Thread (2)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelstalkerBracers; ++i;

var fPatternCobrahideLegArmor = new RewardItem("alliance","Pattern: Cobrahide Leg Armor","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fPatternCobrahideLegArmor.itemMoneyPrice = new Array();
fPatternCobrahideLegArmor.itemMoneyPrice[1] = 60000
fPatternCobrahideLegArmor.itemStats = new Array();
fPatternCobrahideLegArmor.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\">Pattern: Cobrahide Leg Armor<br>Binds when picked up<br>Requires Leatherworking (335)<br>Requires Honor Hold - Honored<br>Use: Teaches you how to make Cobrahide Leg Armor.<br>\
<br>\
<span class=\"myTable\"><span class=\"myBlue\">Cobrahide Leg Armor</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently attach cobrahide armor onto pants to increase attack power by 40 and critical strike rating by 10.</span></span>\
<br><br>Requires Heavy Knothide Leather (4), Cobra Scales (2), Primal Air (4)</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternCobrahideLegArmor; ++i;

var fFootmansLongsword = new RewardItem("alliance","Footman's Longsword","/info/basics/factions/images/icons/INV_Sword_20.gif");
fFootmansLongsword.itemMoneyPrice = new Array();
fFootmansLongsword.itemMoneyPrice[1] = 349801
fFootmansLongsword.itemStats = new Array();
fFootmansLongsword.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Footman's Longsword</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>77 - 145 Damage<span class=\"myRight\">Speed 2.10</span>\
<br>(52.9 damage per second)<br>+16 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>Requires Honor Hold - Honored<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFootmansLongsword; ++i;

var fSagesBand = new RewardItem("alliance","Sage's Band","/info/basics/factions/images/icons/INV_Jewelry_Ring_11.gif");
fSagesBand.itemMoneyPrice = new Array();
fSagesBand.itemMoneyPrice[1] = 114780
fSagesBand.itemStats = new Array();
fSagesBand.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Sage's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+15 Intellect<br>Requires Level 60<br>Requires Honor Hold - Honored<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSagesBand; ++i;




var fGlyphOfFireWarding = new RewardItem("alliance","Glyph of Fire Warding","/info/basics/factions/images/icons/Spell_Fire_SealOfFire.gif");
fGlyphOfFireWarding.itemMoneyPrice = new Array();
fGlyphOfFireWarding.itemMoneyPrice[1] = 1000000
fGlyphOfFireWarding.itemStats = new Array();
fGlyphOfFireWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myGreen\">Glyph of Fire Warding</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Honor Hold - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 20 Fire resistance to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfFireWarding; ++i;


var fDesignDawnstoneCrab = new RewardItem("alliance","Design: Dawnstone Crab","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fDesignDawnstoneCrab.itemMoneyPrice = new Array();
fDesignDawnstoneCrab.itemMoneyPrice[2] = 120000
fDesignDawnstoneCrab.itemStats = new Array();
fDesignDawnstoneCrab.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Design: Dawnstone Crab</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (370)<br>Requires Honor Hold - Revered<br>Use: Teaches you how to craft a Dawnstone Crab.<br>\
<br>\
<span class=\"myBlue\">Figurine - Dawnstone Crab</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 32.</span><br>\
<span class=\"myGreen\">Use: Increases dodge rating by 125 for 20 sec.</span>\
<br><br>Requires Khorium Bar (4), Dawnstone (2), Golden Draenite (4)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignDawnstoneCrab; ++i;

var fFlamewroughtKey = new RewardItem("alliance","Flamewrought Key","/info/basics/factions/images/icons/INV_Misc_Key_13.gif");
fFlamewroughtKey.itemMoneyPrice = new Array();
fFlamewroughtKey.itemMoneyPrice[1] = 100000
fFlamewroughtKey.itemStats = new Array();
fFlamewroughtKey.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Flamewrought Key<br>Binds when picked up<br>Unique<br>Requires Honor Hold - Honored<br>\
<span class=\"myYellow\">\"Unlocks Heroic Difficulty for Hellfire Citadel dungeons.\"</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFlamewroughtKey; ++i;

var fRecipeTransmuteSkyfireDiamond = new RewardItem("alliance","Recipe: Transmute Skyfire Diamond","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fRecipeTransmuteSkyfireDiamond.itemMoneyPrice = new Array();
fRecipeTransmuteSkyfireDiamond.itemMoneyPrice[1] = 80000
fRecipeTransmuteSkyfireDiamond.itemStats = new Array();
fRecipeTransmuteSkyfireDiamond.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
Recipe: Transmute Skyfire Diamond<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires Honor Hold - Honored<br>Use: Teaches you how to Transmute a Skyfire Diamond.<br>\
<br>\
<span class=\"myBlue\">Skyfire Diamond</span>\
<br>Requires Blood Garnet (3), Flame Spessarite (3), Azure Moonstone (3), Primal Fire (2), Primal Air (2)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmuteSkyfireDiamond; ++i;


var fPatternFelstalkerBreastplate = new RewardItem("alliance","Pattern: Felstalker Breastplate","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternFelstalkerBreastplate.itemMoneyPrice = new Array();
fPatternFelstalkerBreastplate.itemMoneyPrice[1] = 160000
fPatternFelstalkerBreastplate.itemStats = new Array();
fPatternFelstalkerBreastplate.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Felstalker Breastplate</span>\
<br>Binds when picked up<br>Requires Leatherworking (360)<br>Requires Honor Hold - Honored<br>Use: Teaches you how to make a Felstalker Breastplate.<br>\
<br>\
<span class=\"myBlue\">Felstalker Breastplate</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Mail</span>\
<br>646 Armor<br>+26 Agility<br>+26 Intellect<br>\
<span class='myRedGem'>Red Socket</span>\
<span class='myRedGem'>Red Socket</span>\
<span class='myBlueGem'>Blue Socket</span>\
<span class='myGray'>Socket Bonus: +6 Stamina</span><br>\
Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 52.</span>\
<br>\
<span class=\"myYellow\">Felstalker Armor (0/3)</span>\
<br>Requires Leatherworking (350)<br> <br> <span class=\"myGray\">Felstalker Belt<br> Felstalker Bracers<br> Felstalker Breastplate</span><br>\
<br><span class=\"myGray\">(3) Set: Increases your hit rating by 20.</span><br>\
<br>Requires Heavy Knothide Leather (10), Fel Hide (4), Crystal Infused Leather (8), Primal Air (8), Rune Thread (2)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelstalkerBreastplate; ++i;


var fGlyphOfRenewal = new RewardItem("alliance","Glyph of Renewal","/info/basics/factions/images/icons/Spell_Holy_HealingAura.gif");
fGlyphOfRenewal.itemMoneyPrice = new Array();
fGlyphOfRenewal.itemMoneyPrice[2] = 1000000
fGlyphOfRenewal.itemStats = new Array();
fGlyphOfRenewal.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myGreen\">Glyph of Renewal</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Honor Hold - Revered<br>\
<span class=\"myGreen\">Use: Permanently adds up to 35 healing, and 7 mana per 5 sec. to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfRenewal; ++i;

var fRingOfConvalescence = new RewardItem("alliance","Ring of Convalescence","/info/basics/factions/images/icons/INV_Jewelry_Ring_43.gif");
fRingOfConvalescence.itemMoneyPrice = new Array();
fRingOfConvalescence.itemMoneyPrice[2] = 175952
fRingOfConvalescence.itemStats = new Array();
fRingOfConvalescence.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Ring of Convalescence</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+15 Intellect<br>Requires Level 70<br>Requires Honor Hold - Revered<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 57.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRingOfConvalescence; ++i;

var fHellforgedHalberd = new RewardItem("alliance","Hellforged Halberd","/info/basics/factions/images/icons/INV_Weapon_Halberd_12.gif");
fHellforgedHalberd.itemMoneyPrice = new Array();
fHellforgedHalberd.itemMoneyPrice[2] = 555019
fHellforgedHalberd.itemStats = new Array();
fHellforgedHalberd.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Hellforged Halberd</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>261 - 392 Damage<span class=\"myRight\">Speed 3.50</span>\
<br>(93.3 damage per second)<br>+26 Agility<br>Durability 100 / 100<br>Requires Level 70<br>Requires Honor Hold - Revered<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 92.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHellforgedHalberd; ++i;

var fFelbaneSlugs = new RewardItem("alliance","Felbane Slugs","/info/basics/factions/images/icons/INV_Misc_Ammo_Bullet_02.gif");
fFelbaneSlugs.itemMoneyPrice = new Array();
fFelbaneSlugs.itemMoneyPrice[2] = 5000
fFelbaneSlugs.itemStats = new Array();
fFelbaneSlugs.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Felbane Slugs</span>\
<br>Projectile<span class=\"myRight\">Bullet</span>\
<br>Adds 37 damage per second<br>Requires Level 68<br>Requires Honor Hold - Revered<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFelbaneSlugs; ++i;

var fPatternNethercobraLegArmor = new RewardItem("alliance","Pattern: Nethercobra Leg Armor","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fPatternNethercobraLegArmor.itemMoneyPrice = new Array();
fPatternNethercobraLegArmor.itemMoneyPrice[3] = 120000
fPatternNethercobraLegArmor.itemStats = new Array();
fPatternNethercobraLegArmor.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
Pattern: Nethercobra Leg Armor<br>Binds when picked up<br>Requires Leatherworking (365)<br>Requires Honor Hold - Exalted<br>Use: Teaches you how to make Nethercobra Leg Armor.<br>\
<br>\
<span class=\"myTable\"><span class=\"myBlue\">Nethercobra Leg Armor</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently attach nethercobra armor onto pants to increase attack power by 50 and critical strike rating by 12.</span>\
<br>Requires Heavy Knothide Leather (4), Cobra Scales (4), Primal Air (8), Primal Nether\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNethercobraLegArmor; ++i;

var fFormulaEnchantCloakSubtlety = new RewardItem("alliance","Formula: Enchant Cloak - Subtlety","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantCloakSubtlety.itemMoneyPrice = new Array();
fFormulaEnchantCloakSubtlety.itemMoneyPrice[3] = 90000
fFormulaEnchantCloakSubtlety.itemStats = new Array();
fFormulaEnchantCloakSubtlety.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Cloak - Subtlety</span>\
<br>Binds when picked up<br>Requires Enchanting (300)<br>Requires Honor Hold - Exalted<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a cloak to reduce how threatening the wearer is to monsters by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantCloakSubtlety; ++i;

var fVeteransMusket = new RewardItem("alliance","Veteran's Musket","/info/basics/factions/images/icons/INV_Weapon_Rifle_02.gif");
fVeteransMusket.itemMoneyPrice = new Array();
fVeteransMusket.itemMoneyPrice[3] = 1522789
fVeteransMusket.itemStats = new Array();
fVeteransMusket.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Veteran's Musket</span>\
<br>Binds when picked up<br>Unique<br>Ranged<span class=\"myRight\">Gun</span>\
<br>139 - 259 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(73.7 damage per second)<br>+12 Agility<br>Durability 90 / 90<br>Requires Level 70<br>Requires Honor Hold - Exalted<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMusket; ++i;

var fBladeOfTheArchmage = new RewardItem("alliance","Blade of the Archmage","/info/basics/factions/images/icons/INV_Weapon_Shortblade_37_.gif");
fBladeOfTheArchmage.itemMoneyPrice = new Array();
fBladeOfTheArchmage.itemMoneyPrice[3] = 2045002
fBladeOfTheArchmage.itemStats = new Array();
fBladeOfTheArchmage.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Blade of the Archmage</span>\
<br>Binds when picked up<br>Unique<br>Main Hand<span class=\"myRight\">Sword</span>\
<br>30 - 119 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(41.3 damage per second)<br>+13 Stamina<br>+11 Intellect<br>Durability 105 / 105<br>Requires Level 70<br>Requires Honor Hold - Exalted<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 159.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBladeOfTheArchmage; ++i;

var fHonorsCall = new RewardItem("alliance","Honor's Call","/pvp/images/honorweapons/grandmarshalslongsword.gif");
fHonorsCall.itemMoneyPrice = new Array();
fHonorsCall.itemMoneyPrice[3] = 1921350
fHonorsCall.itemStats = new Array();
fHonorsCall.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Honor's Call</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>102 - 190 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(81.1 damage per second)<br>+13 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>Requires Honor Hold - Exalted<br>\
<span class=\"myGreen\">Increases defense rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHonorsCall; ++i;

var fHonorHoldTabard = new RewardItem("alliance","Honor Hold Tabard","/shared/wow-com/images/basics/factions/alteracvalley/stormpikebattletabard.gif");
fHonorHoldTabard.itemMoneyPrice = new Array();
fHonorHoldTabard.itemMoneyPrice[3] = 10000
fHonorHoldTabard.itemStats = new Array();
fHonorHoldTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Honor Hold Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires Honor Hold - Exalted</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHonorHoldTabard; ++i;

//-------------------------------------------------------------------
//---Horde below

var fDesignEnduringDeepPeridot = new RewardItem("horde","Design: Enduring Deep Peridot","/info/basics/factions/images/icons/INV_Scroll_06.gif");
fDesignEnduringDeepPeridot.itemMoneyPrice = new Array();
fDesignEnduringDeepPeridot.itemMoneyPrice[0] = 60000
fDesignEnduringDeepPeridot.itemStats = new Array();
fDesignEnduringDeepPeridot.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myGreen\">Design: Enduring Deep Peridot</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (315)<br>Requires Thrallmar - Friendly<br>Use: Teaches you how to cut an Enduring Deep Peridot.<br>\
<br>\
<span class=\"myGreen\">Enduring Deep Peridot</span>\
<br>+3 Defense Rating and +4 Stamina<br>\
<span class=\"myYellow\">\"Matches a Yellow or Blue Socket.\"</span></span>\
<br><br>Requires Deep Peridot</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignEnduringDeepPeridot; ++i;

var fPatternFelstalkerBelt = new RewardItem("horde","Pattern: Felstalker Belt ","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternFelstalkerBelt.itemMoneyPrice = new Array();
fPatternFelstalkerBelt.itemMoneyPrice[0] = 120000
fPatternFelstalkerBelt.itemStats = new Array();
fPatternFelstalkerBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Pattern: Felstalker Belt</span>\
<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires Honor Hold - Friendly<br>Use: Teaches you how to make a Felstalker Belt.<br>\
<br>\
<span class=\"myBlue\">Felstalker Belt</span>\
<br>Binds when equipped<br>Waist<span class=\"myRight\">Mail</span>\
<br>357 Armor<br>+18 Agility<br>+17 Intellect<br>\
<span class=\"myRedGem\">Red Socket</span>\
<span class=\"myBlueGem\">Blue Socket</span>\
<span class=\"myGray\">Socket Bonus: +4 Stamina<br></span>\
Durability 40 / 40<br>Requires Level 69<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span><br>\
<br>\
<span class=\"myYellow\">Felstalker Armor (0/3)</span>\
<br>Requires Leatherworking (350)<br> <br> <span class=\"myGray\">Felstalker Belt<br> Felstalker Bracers<br> Felstalker Breastplate</span><br>\
<br><span class=\"myGray\">(3) Set: Increases your hit rating by 20.</span><br>\
<br>Requires Heavy Knothide Leather (6), Fel Hide (4), Crystal Infused Leather (8), Primal Air (6), Rune Thread (2)</span>\
</div></div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelstalkerBelt; ++i;

var fFootmansWaterskin = new RewardItem("horde","Grunt's Waterskin","/info/basics/factions/images/icons/INV_Drink_Waterskin_05.gif");
fFootmansWaterskin.itemMoneyPrice = new Array();
fFootmansWaterskin.itemMoneyPrice[0] = 2000
fFootmansWaterskin.itemStats = new Array();
fFootmansWaterskin.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Footman's Waterskin<br>Binds when picked up<br>Unique (20)<br>Requires Level 55<br>Requires Thrallmar - Friendly<br>\
<span class=\"myGreen\">Use: Restores 4200 mana over 30 sec.  Must remain seated while drinking.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFootmansWaterskin; ++i;

var fDriedFruitRations = new RewardItem("horde","Dried Fruit Rations","/info/basics/factions/images/icons/INV_Misc_Food_42.gif");
fDriedFruitRations.itemMoneyPrice = new Array();
fDriedFruitRations.itemMoneyPrice[0] = 4500
fDriedFruitRations.itemStats = new Array();
fDriedFruitRations.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Dried Fruit Rations<br>Binds when picked up<br>Unique (20)<br>Requires Level 55<br>Requires Thrallmar - Friendly<br>\
<span class=\"myGreen\">Use: Restores 4320 health over 30 sec.   Must remain seated while eating.   Also increases your Stamina by 10 for 10 min. </span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDriedFruitRations; ++i;

var fFormulaEnchantBracerSuperiorHealing= new RewardItem("horde","Formula: Enchant - Superior Healing","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantBracerSuperiorHealing.itemMoneyPrice = new Array();
fFormulaEnchantBracerSuperiorHealing.itemMoneyPrice[0] = 60000
fFormulaEnchantBracerSuperiorHealing.itemStats = new Array();
fFormulaEnchantBracerSuperiorHealing.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Formula: Enchant Bracer - Superior Healing<br>Requires Enchanting (325)<br>Requires Thrallmar - Friendly<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a bracer to increase the effect of healing spells by up to 30.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantBracerSuperiorHealing; ++i;

var fRecipeElixirOfMajorAgility = new RewardItem("horde","Recipe: Elixir of Agility","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fRecipeElixirOfMajorAgility.itemMoneyPrice = new Array();
fRecipeElixirOfMajorAgility.itemMoneyPrice[1] = 50000
fRecipeElixirOfMajorAgility.itemStats = new Array();
fRecipeElixirOfMajorAgility.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
Recipe: Elixir of Agility<br>Requires Alchemy (330)<br>Requires Thrallmar - Honored<br>Use: Teaches you how to make an Elixir of Agility.<br>\
<br>\
<b>Elixir of Agility</b><br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Increases your Agility by 35 and your critical strike rating by 20 for 1 Hour. Battle Elixir.</span></span>\
<br>Requires Terocone, Felweed (2), Imbued Vial\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeElixirOfMajorAgility; ++i;

var fFormulaEnchantChestExceptionalStats = new RewardItem("horde","Formula: Enchant - Exceptional Stats","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantChestExceptionalStats.itemMoneyPrice = new Array();
fFormulaEnchantChestExceptionalStats.itemMoneyPrice[2] = 60000
fFormulaEnchantChestExceptionalStats.itemStats = new Array();
fFormulaEnchantChestExceptionalStats.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Formula: Enchant Chest - Exceptional Stats<br>Binds when picked up<br>Requires Enchanting (345)<br>Requires Thrallmar - Revered<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant chest armor to increase all stats by 6.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantChestExceptionalStats; ++i;

var fPatternFelstalkerBracers = new RewardItem("horde","Pattern: Felstalker Bracers","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternFelstalkerBracers.itemMoneyPrice = new Array();
fPatternFelstalkerBracers.itemMoneyPrice[1] = 160000
fPatternFelstalkerBracers.itemStats = new Array();
fPatternFelstalkerBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
	<tr>\
		<td>\
			<div class=\"myTable\">\
				<span class=\"myBlue\">Pattern: Felstalker Bracers</span>\
				<br>Binds when picked up<br>\
				Requires Leatherworking (360)<br>\
				Requires Thrallmar - Honored<br>\
				Use: Teaches you how to make Felstalker Bracers.<br>\
				<br>\
				<span class=\"myBlue\">Felstalker Bracers</span>\
				<br>Binds when equipped<br>\
				Wrist<span class=\"myRight\">Mail</span>\
				<br>283 Armor<br>\
				+18 Agility<br>\
				+11 Intellect<br>\
				<span class='myBlueGem'>Blue Socket</span>\
				<span class='myGray'>Socket Bonus: +3 Stamina</span><br>\
				<br>Durability 40 / 40<br>\
				Requires Level 70<br>\
				<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
				<br>\
				<br>\
<span class=\"myYellow\">Felstalker Armor (0/3)</span>\
<br>Requires Leatherworking (350)<br> <br> <span class=\"myGray\">Felstalker Belt<br> Felstalker Bracers<br> Felstalker Breastplate</span><br>\
<br><span class=\"myGray\">(3) Set: Increases your hit rating by 20.</span><br>\
				<br>Requires Heavy Knothide Leather (6), Fel Hide (6), Crystal Infused Leather (6), Primal Air (4), Rune Thread (2)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelstalkerBracers; ++i;

var fPatternCobrahideLegArmor = new RewardItem("horde","Pattern: Cobrahide Leg Armor","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fPatternCobrahideLegArmor.itemMoneyPrice = new Array();
fPatternCobrahideLegArmor.itemMoneyPrice[1] = 60000
fPatternCobrahideLegArmor.itemStats = new Array();
fPatternCobrahideLegArmor.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\">Pattern: Cobrahide Leg Armor<br>Binds when picked up<br>Requires Leatherworking (335)<br>Requires Thrallmar - Honored<br>Use: Teaches you how to make Cobrahide Leg Armor.<br>\
<br>\
<span class=\"myTable\"><span class=\"myBlue\">Cobrahide Leg Armor</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently attach cobrahide armor onto pants to increase attack power by 40 and critical strike rating by 10.</span></span>\
<br><br>Requires Heavy Knothide Leather (4), Cobra Scales (2), Primal Air (4)</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternCobrahideLegArmor; ++i;












var fGruntsWaraxe = new RewardItem("horde","Grunt's Waraxe","/info/basics/factions/images/icons/INV_Axe_11.gif");
fGruntsWaraxe.itemMoneyPrice = new Array();
fGruntsWaraxe.itemMoneyPrice[1] = 347318
fGruntsWaraxe.itemStats = new Array();
fGruntsWaraxe.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grunt's Waraxe</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>70 - 131 Damage<span class=\"myRight\">Speed 1.90</span>\
<br>(52.9 damage per second)<br>+16 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>Requires Thrallmar - Honored<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGruntsWaraxe; ++i;

var fFarseersBand = new RewardItem("horde","Farseer's Band","/info/basics/factions/images/icons/INV_Jewelry_Ring_17.gif");
fFarseersBand.itemMoneyPrice = new Array();
fFarseersBand.itemMoneyPrice[1] = 114780
fFarseersBand.itemStats = new Array();
fFarseersBand.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Farseer's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+15 Intellect<br>Requires Level 60<br>Requires Thrallmar - Honored<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFarseersBand; ++i;






var fGlyphOfFireWarding = new RewardItem("horde","Glyph of Fire Warding","/info/basics/factions/images/icons/Spell_Fire_SealOfFire.gif");
fGlyphOfFireWarding.itemMoneyPrice = new Array();
fGlyphOfFireWarding.itemMoneyPrice[1] = 1000000
fGlyphOfFireWarding.itemStats = new Array();
fGlyphOfFireWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myGreen\">Glyph of Fire Warding</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Thrallmar - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 20 Fire resistance to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfFireWarding; ++i;


var fDesignDawnstoneCrab = new RewardItem("horde","Design: Dawnstone Crab","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fDesignDawnstoneCrab.itemMoneyPrice = new Array();
fDesignDawnstoneCrab.itemMoneyPrice[2] = 120000
fDesignDawnstoneCrab.itemStats = new Array();
fDesignDawnstoneCrab.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Design: Dawnstone Crab</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (370)<br>Requires Thrallmar - Revered<br>Use: Teaches you how to craft a Dawnstone Crab.<br>\
<br>\
<span class=\"myBlue\">Figurine - Dawnstone Crab</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 32.</span><br>\
<span class=\"myGreen\">Use: Increases dodge rating by 125 for 20 sec.</span>\
<br><br>Requires Khorium Bar (4), Dawnstone (2), Golden Draenite (4)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignDawnstoneCrab; ++i;

var fFlamewroughtKey = new RewardItem("horde","Flamewrought Key","/info/basics/factions/images/icons/INV_Misc_Key_13.gif");
fFlamewroughtKey.itemMoneyPrice = new Array();
fFlamewroughtKey.itemMoneyPrice[1] = 100000
fFlamewroughtKey.itemStats = new Array();
fFlamewroughtKey.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Flamewrought Key<br>Binds when picked up<br>Unique<br>Requires Thrallmar - Honored<br>\
<span class=\"myYellow\">\"Unlocks Heroic Difficulty for Hellfire Citadel dungeons.\"</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFlamewroughtKey; ++i;

var fRecipeTransmuteSkyfireDiamond = new RewardItem("horde","Recipe: Transmute Skyfire Diamond","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fRecipeTransmuteSkyfireDiamond.itemMoneyPrice = new Array();
fRecipeTransmuteSkyfireDiamond.itemMoneyPrice[1] = 80000
fRecipeTransmuteSkyfireDiamond.itemStats = new Array();
fRecipeTransmuteSkyfireDiamond.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
Recipe: Transmute Skyfire Diamond<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires Thrallmar - Honored<br>Use: Teaches you how to Transmute a Skyfire Diamond.<br>\
<br>\
<span class=\"myBlue\">Skyfire Diamond</span>\
<br>Requires Blood Garnet (3), Flame Spessarite (3), Azure Moonstone (3), Primal Fire (2), Primal Air (2)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmuteSkyfireDiamond; ++i;

var fPatternFelstalkerBreastplate = new RewardItem("horde","Pattern: Felstalker Breastplate","/info/basics/factions/images/icons/INV_Scroll_05.gif");
fPatternFelstalkerBreastplate.itemMoneyPrice = new Array();
fPatternFelstalkerBreastplate.itemMoneyPrice[1] = 160000
fPatternFelstalkerBreastplate.itemStats = new Array();
fPatternFelstalkerBreastplate.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Felstalker Breastplate</span>\
<br>Binds when picked up<br>Requires Leatherworking (360)<br>Requires Honor Hold - Honored<br>Use: Teaches you how to make a Felstalker Breastplate.<br>\
<br>\
<span class=\"myBlue\">Felstalker Breastplate</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Mail</span>\
<br>646 Armor<br>+26 Agility<br>+26 Intellect<br>\
<span class='myRedGem'>Red Socket</span>\
<span class='myRedGem'>Red Socket</span>\
<span class='myBlueGem'>Blue Socket</span>\
<span class='myGray'>Socket Bonus: +6 Stamina</span><br>\
Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 52.</span>\
<br>\
<span class=\"myYellow\">Felstalker Armor (0/3)</span>\
<br>Requires Leatherworking (350)<br> <br> <span class=\"myGray\">Felstalker Belt<br> Felstalker Bracers<br> Felstalker Breastplate</span><br>\
<br><span class=\"myGray\">(3) Set: Increases your hit rating by 20.</span><br>\
<br>Requires Heavy Knothide Leather (10), Fel Hide (4), Crystal Infused Leather (8), Primal Air (8), Rune Thread (2)\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelstalkerBreastplate; ++i;





var fGlyphOfRenewal = new RewardItem("horde","Glyph of Renewal","/info/basics/factions/images/icons/Spell_Holy_HealingAura.gif");
fGlyphOfRenewal.itemMoneyPrice = new Array();
fGlyphOfRenewal.itemMoneyPrice[2] = 1000000
fGlyphOfRenewal.itemStats = new Array();
fGlyphOfRenewal.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myGreen\">Glyph of Renewal</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Thrallmar - Revered<br>\
<span class=\"myGreen\">Use: Permanently adds up to 35 healing, and 7 mana per 5 sec. to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfRenewal; ++i;

var fAncestralBand = new RewardItem("horde","Ancestral Band","/info/basics/factions/images/icons/INV_Jewelry_Ring_22.gif");
fAncestralBand.itemMoneyPrice = new Array();
fAncestralBand.itemMoneyPrice[2] = 175952
fAncestralBand.itemStats = new Array();
fAncestralBand.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Ancestral Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+15 Intellect<br>Requires Level 70<br>Requires Thrallmar - Revered<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 57.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAncestralBand; ++i;

var fBlackenedSpear = new RewardItem("horde","Blackened Spear","/info/basics/factions/images/icons/INV_Spear_03.gif");
fBlackenedSpear.itemMoneyPrice = new Array();
fBlackenedSpear.itemMoneyPrice[2] = 557054
fBlackenedSpear.itemStats = new Array();
fBlackenedSpear.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Blackened Spear</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>261 - 392 Damage<span class=\"myRight\">Speed 3.50</span>\
<br>(93.3 damage per second)<br>+26 Agility<br>Durability 100 / 100<br>Requires Level 70<br>Requires Thrallmar - Revered<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 92.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBlackenedSpear; ++i;

var fHellfireShot = new RewardItem("horde","Hellfire Shot","/info/basics/factions/images/icons/INV_Misc_Ammo_Bullet_02.gif");
fHellfireShot.itemMoneyPrice = new Array();
fHellfireShot.itemMoneyPrice[2] = 5000
fHellfireShot.itemStats = new Array();
fHellfireShot.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Hellfire Shot</span>\
<br>Projectile<span class=\"myRight\">Bullet</span>\
<br>Adds 37 damage per second<br>Requires Level 68<br>Requires Thrallmar - Revered<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHellfireShot; ++i;

var fPlansFelsteelShieldSpike = new RewardItem("horde","Plans: Felsteel Shield Spike","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fPlansFelsteelShieldSpike.itemMoneyPrice = new Array();
fPlansFelsteelShieldSpike.itemMoneyPrice[3] = 60000
fPlansFelsteelShieldSpike.itemStats = new Array();
fPlansFelsteelShieldSpike.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\">Plans: Felsteel Shield Spike<br>Binds when picked up<br>Requires Blacksmithing (360)<br>Requires Thrallmar - Exalted<br>Use: Teaches you how to make a Felsteel Shield Spike.<br>\
<br>\
<span class=\"myGreen\"><b>Felsteel Shield Spike</b></span>\
<br>Requires Blacksmithing (350)<br>\
<span class=\"myGreen\">Use: Attaches a Felsteel Spike to your shield that deals 26-38 damage every time you block with it.</span>\
<br>Requires Felsteel Bar (4), Primal Fire (4), Primal Earth (4)</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansFelsteelShieldSpike; ++i;

var fPatternNethercobraLegArmor = new RewardItem("horde","Pattern: Nethercobra Leg Armor","/info/basics/factions/images/icons/INV_Scroll_03.gif");
fPatternNethercobraLegArmor.itemMoneyPrice = new Array();
fPatternNethercobraLegArmor.itemMoneyPrice[3] = 120000
fPatternNethercobraLegArmor.itemStats = new Array();
fPatternNethercobraLegArmor.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\">Pattern: Nethercobra Leg Armor<br>Binds when picked up<br>Requires Leatherworking (365)<br>Requires Thrallmar - Exalted<br>Use: Teaches you how to make Nethercobra Leg Armor.<br>\
<br>\
<span class=\"myBlue\">Nethercobra Leg Armor</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently attach nethercobra armor onto pants to increase attack power by 50 and critical strike rating by 12.</span>\
<br>Requires Heavy Knothide Leather (4), Cobra Scales (4), Primal Air (8), Primal Nether</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNethercobraLegArmor; ++i;

var fFormulaEnchantCloakSubtlety = new RewardItem("horde","Formula: Enchant Cloak - Subtlety","/info/basics/factions/images/icons/recipe.gif");
fFormulaEnchantCloakSubtlety.itemMoneyPrice = new Array();
fFormulaEnchantCloakSubtlety.itemMoneyPrice[3] = 90000
fFormulaEnchantCloakSubtlety.itemStats = new Array();
fFormulaEnchantCloakSubtlety.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Cloak - Subtlety</span>\
<br>Binds when picked up<br>Requires Enchanting (300)<br>Requires Thrallmar - Exalted<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a cloak to reduce how threatening the wearer is to monsters by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantCloakSubtlety; ++i;




var fMarksmansBow = new RewardItem("horde","Marksman's Bow","/info/basics/factions/images/icons/INV_Weapon_Bow_08.gif");
fMarksmansBow.itemMoneyPrice = new Array();
fMarksmansBow.itemMoneyPrice[3] = 1599984
fMarksmansBow.itemStats = new Array();
fMarksmansBow.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Marksman's Bow</span>\
<br>Binds when picked up<br>Unique<br>Ranged<span class=\"myRight\">Bow</span>\
<br>144 - 269 Damage<span class=\"myRight\">Speed 2.80</span>\
<br>(73.8 damage per second)<br>+12 Agility<br>Durability 90 / 90<br>Requires Level 70<br>Requires Thrallmar - Exalted<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarksmansBow; ++i;

var fStormcaller = new RewardItem("horde","Stormcaller","/pvp/images/honorweapons/highwarlordsslicer.gif");
fStormcaller.itemMoneyPrice = new Array();
fStormcaller.itemMoneyPrice[3] = 2059422
fStormcaller.itemStats = new Array();
fStormcaller.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Stormcaller</span>\
<br>Binds when picked up<br>Unique<br>Main Hand<span class=\"myRight\">Sword</span>\
<br>30 - 119 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(41.3 damage per second)<br>+12 Stamina<br>+12 Intellect<br>Durability 105 / 105<br>Requires Level 70<br>Requires Thrallmar - Exalted<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 159.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormcaller; ++i;

var fWarbringer = new RewardItem("horde","Warbringer","/pvp/images/honorweapons/grandmarshalsunderer.gif");
fWarbringer.itemMoneyPrice = new Array();
fWarbringer.itemMoneyPrice[3] = 1986731
fWarbringer.itemStats = new Array();
fWarbringer.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Warbringer</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>102 - 190 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(81.1 damage per second)<br>+12 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>Requires Thrallmar - Exalted<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 7.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarbringer; ++i;



var fHonorHoldTabard = new RewardItem("horde","Thrallmar Tabard","/shared/wow-com/images/basics/factions/alteracvalley/stormpikebattletabard.gif");
fHonorHoldTabard.itemMoneyPrice = new Array();
fHonorHoldTabard.itemMoneyPrice[3] = 10000
fHonorHoldTabard.itemStats = new Array();
fHonorHoldTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Thrallmar Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires Thrallmar - Exalted</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHonorHoldTabard; ++i;

//-------------------------------------------------------------------
//---Horde below




//------END REWARDS DEFINITION------
