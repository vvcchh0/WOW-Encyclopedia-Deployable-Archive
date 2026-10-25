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
		if (goldPart > 0) outPutString += goldPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/gold.gif'>&nbsp;";
		if (silverPart > 0) outPutString += silverPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/silver.gif'>&nbsp;";
		if (copperPart > 0) outPutString += copperPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/copper.gif'>&nbsp;";
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

var fFormulaEnchantCloakSpellPenetration = new RewardItem("alliance","Formula: Spell Penetration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fconsortium%2Fscripts%2Frewards-consortium.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Frecipe.gif&reason=external-or-uncollected-resource");
fFormulaEnchantCloakSpellPenetration.itemMoneyPrice = new Array();
fFormulaEnchantCloakSpellPenetration.itemMoneyPrice[0] = 40000
fFormulaEnchantCloakSpellPenetration.itemStats = new Array();
fFormulaEnchantCloakSpellPenetration.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Cloak - Spell Penetration</span>\
<br>Binds when picked up<br>Requires Enchanting (325)<br>Requires The Consortium - Friendly<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a cloak to give 20 Spell Penetration.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantCloakSpellPenetration; ++i;

var fDesignShiftingShadowDraenite = new RewardItem("alliance","Design: Shifting Shadow Draenite","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignShiftingShadowDraenite.itemMoneyPrice = new Array();
fDesignShiftingShadowDraenite.itemMoneyPrice[0] = 60000
fDesignShiftingShadowDraenite.itemStats = new Array();
fDesignShiftingShadowDraenite.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Shifting Shadow Draenite</span>\
<br>Requires Jewelcrafting (315)<br>Requires The Consortium - Friendly<br>Use: Teaches you how to cut a Shifting Shadow Draenite.<br>\
<br>\
<span class=\"myGreen\"><b>Shifting Shadow Draenite</b></span>\
<br>+3 Agility and +4 Stamina<br>\
<span class=\"myYellow\">\"Matches a Red or Blue Socket.\"</span>\
<br>Requires Shadow Draenite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignShiftingShadowDraenite; ++i;

var fDesignLuminousFlameSpessarite = new RewardItem("alliance","Design: Luminous Flame Spessarite","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignLuminousFlameSpessarite.itemMoneyPrice = new Array();
fDesignLuminousFlameSpessarite.itemMoneyPrice[0] = 50000
fDesignLuminousFlameSpessarite.itemStats = new Array();
fDesignLuminousFlameSpessarite.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Luminous Flame Spessarite</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (305)<br>Requires The Consortium - Friendly<br>Use: Teaches you how to cut a Luminous Flame Spessarite.<br>\
<br>\
<span class=\"myGreen\"><b>Luminous Flame Spessarite</b></span>\
<br>+7 Healing Spells and +3 Intellect<br>\
<span class=\"myYellow\">\"Matches a Yellow or Red Socket.\"</span>\
<br>Requires Flame Spessarite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignLuminousFlameSpessarite; ++i;


var fPatternFelLeatherGloves = new RewardItem("alliance","Pattern: Fel Leather Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternFelLeatherGloves.itemMoneyPrice = new Array();
fPatternFelLeatherGloves.itemMoneyPrice[0] = 120000
fPatternFelLeatherGloves.itemStats = new Array();
fPatternFelLeatherGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Fel Leather Gloves</span>\
<br>Binds when picked up<br>Requires Leatherworking (340)<br>Requires The Consortium - Friendly<br>Use: Teaches you how to make Fel Leather Gloves.<br>\
<br>\
<span class=\"myBlue\">Fel Leather Gloves</span>\
<br>Binds when equipped<br>Hand<span class=\"myRight\">Leather</span>\
<br>169 Armor<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 67<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 36.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fel Skin (0/3)</span>\
<br>Requires Leatherworking (350)<br> Fel Leather Gloves<br> Fel Leather Boots<br> Fel Leather Leggings<br>\
<br>\
<span class=\"myGray\">(3) Set: Increases your dodge rating by 20.</span>\
<br>\
<br>Requires Heavy Knothide Leather (6), Fel Hide (6), Primal Shadow (6), Rune Thread (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelLeatherGloves; ++i;


var fDesignThickGoldenDraenite = new RewardItem("alliance","Design: Thick Golden Draenite","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignThickGoldenDraenite.itemMoneyPrice = new Array();
fDesignThickGoldenDraenite.itemMoneyPrice[1] = 60000
fDesignThickGoldenDraenite.itemStats = new Array();
fDesignThickGoldenDraenite.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Thick Golden Draenite</span>\
<br>Requires Jewelcrafting (315)<br>Requires The Consortium - Honored<br>Use: Teaches you how to cut a Thick Golden Draenite.<br>\
<br>\
<span class=\"myGreen\"><b>Thick Golden Draenite</b></span>\
<br>+6 Defense Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow Socket.\"</span>\
<br>Requires Golden Draenite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignThickGoldenDraenite; ++i;

var fDesignDelicateBloodGarnet = new RewardItem("alliance","Design: Delicate Blood Garnet","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignDelicateBloodGarnet.itemMoneyPrice = new Array();
fDesignDelicateBloodGarnet.itemMoneyPrice[1] = 60000
fDesignDelicateBloodGarnet.itemStats = new Array();
fDesignDelicateBloodGarnet.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Delicate Blood Garnet</span>\
<br>Requires Jewelcrafting (325)<br>Requires The Consortium - Honored<br>Use: Teaches you how to cut a Delicate Blood Garnet.<br>\
<br>\
<span class=\"myGreen\"><b>Delicate Blood Garnet</b></span>\
<br>+6 Agility<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span>\
<br>Requires Blood Garnet</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignDelicateBloodGarnet; ++i;

var fDesignLustrousAzureMoonstone = new RewardItem("alliance","Design: Lustrous Azure Moonstone","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignLustrousAzureMoonstone.itemMoneyPrice = new Array();
fDesignLustrousAzureMoonstone.itemMoneyPrice[1] = 60000
fDesignLustrousAzureMoonstone.itemStats = new Array();
fDesignLustrousAzureMoonstone.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Lustrous Azure Moonstone</span>\
<br>Requires Jewelcrafting (325)<br>Requires The Consortium - Honored<br>Use: Teaches you how to cut a Lustrous Azure Moonstone.<br>\
<br>\
<span class=\"myGreen\"><b>Lustrous Azure Moonstone</b></span>\
<br>+2 Mana every 5 seconds<br>\
<span class=\"myYellow\">\"Matches a Blue Socket.\"</span>\
<br>Requires Azure Moonstone</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignLustrousAzureMoonstone; ++i;

var fDesignSwiftSkyfireDiamond = new RewardItem("alliance","Design: Swift Skyfire Diamond","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fDesignSwiftSkyfireDiamond.itemMoneyPrice = new Array();
fDesignSwiftSkyfireDiamond.itemMoneyPrice[1] = 120000
fDesignSwiftSkyfireDiamond.itemStats = new Array();
fDesignSwiftSkyfireDiamond.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Design: Swift Skyfire Diamond<br>Binds when picked up<br>Requires Jewelcrafting (365)<br>Requires The Consortium - Honored<br>Use: Teaches you how to cut a Swift Skyfire Diamond.<br>\
<br>\
<span class=\"myBlue\">Swift Skyfire Diamond</span>\
<br>+24 Attack Power and Minor Run Speed Increase<br>\
Requires at least 2 Yellow gems<br>\
Requires at least 1 Red gem<br>\
<span class=\"myYellow\">\"Only fits in a meta gem slot.\"</span>\
<br>Requires Skyfire Diamond</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignSwiftSkyfireDiamond; ++i;

var fSmugglersAmmoPouch = new RewardItem("alliance","Smuggler's Ammo Pouch","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fconsortium%2Fscripts%2Frewards-consortium.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Bag_10_Black.gif&reason=external-or-uncollected-resource");
fSmugglersAmmoPouch.itemMoneyPrice = new Array();
fSmugglersAmmoPouch.itemMoneyPrice[1] = 100000
fSmugglersAmmoPouch.itemStats = new Array();
fSmugglersAmmoPouch.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Smuggler's Ammo Pouch</span>\
<br>Binds when picked up<br>Unique<br>18 Slot Ammo Pouch<br>Classes: Hunter<br>Requires Level 68<br>Requires The Consortium - Honored<br>\
<span class=\"myGreen\">Equip: Increases ranged attack speed by 15%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSmugglersAmmoPouch; ++i;

var fNethershard = new RewardItem("alliance","Nethershard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Weapon_ShortBlade_08.gif");
fNethershard.itemMoneyPrice = new Array();
fNethershard.itemMoneyPrice[1] = 349938
fNethershard.itemStats = new Array();
fNethershard.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Nethershard</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>40 - 99 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(41.2 damage per second)<br>+15 Stamina<br>+18 Intellect<br>Durability 65 / 65<br>Requires Level 63<br>Requires The Consortium - Honored<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 6.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 61.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNethershard; ++i;

var fGiftOfTheEthereal = new RewardItem("alliance","Gift of the Ethereal","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_sword_draenei_01.jpg");
fGiftOfTheEthereal.itemMoneyPrice = new Array();
fGiftOfTheEthereal.itemMoneyPrice[1] = 348580
fGiftOfTheEthereal.itemStats = new Array();
fGiftOfTheEthereal.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Gift of the Ethereal</span>\
<br>Binds when picked up<br>Unique<br>Main Hand<span class=\"myRight\">Sword</span>\
<br>79 - 147 Damage<span class=\"myRight\">Speed 2.00</span>\
<br>(56.5 damage per second)<br>+12 Agility<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 63<br>Requires The Consortium - Honored<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGiftOfTheEthereal; ++i;

var fDesignPendantOfTheNullRune = new RewardItem("alliance","Design: Pendant of the Null Rune","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fDesignPendantOfTheNullRune.itemMoneyPrice = new Array();
fDesignPendantOfTheNullRune.itemMoneyPrice[2] = 120000
fDesignPendantOfTheNullRune.itemStats = new Array();
fDesignPendantOfTheNullRune.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Pendant of the Null Rune</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (360)<br>Requires The Consortium - Revered<br>Use: Teaches you how to craft a Pendant of the Null Rune.<br>\
<br>\
<span class=\"myBlue\">Pendant of the Null Rune</span>\
<br>Binds when equipped<br>Neck<br>+18 Stamina<br>+30 Arcane Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Use: Absorbs 900 to 2700 arcane damage on all nearby party members.  Lasts 5 mins.<br>10 Charges</span>\
<br>Requires Felsteel Bar (2), Primal Mana (8), Mercurial Adamantite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignPendantOfTheNullRune; ++i;

var fPatternBagOfJewels = new RewardItem("alliance","Pattern: Bag of Jewels","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternBagOfJewels.itemMoneyPrice = new Array();
fPatternBagOfJewels.itemMoneyPrice[1] = 40000
fPatternBagOfJewels.itemStats = new Array();
fPatternBagOfJewels.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Bag of Jewels<br>Binds when picked up<br>Requires Tailoring (340)<br>Requires The Consortium - Honored<br>Use: Teaches you how to sew a Bag of Jewels.<br>\
<br>\
<span class=\"myGreen\"><b>Bag of Jewels</b></span>\
<br>Binds when equipped<br>24 Slot Gem Bag\
<br>Requires Bolt of Imbued Netherweave (6), Knothide Leather (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternBagOfJewels; ++i;

var fPatternFelLeatherBoots = new RewardItem("alliance","Pattern: Fel Leather Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternFelLeatherBoots.itemMoneyPrice = new Array();
fPatternFelLeatherBoots.itemMoneyPrice[1] = 140000
fPatternFelLeatherBoots.itemStats = new Array();
fPatternFelLeatherBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Fel Leather Boots</span>\
<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Consortium - Honored<br>Use: Teaches you how to make Fel Leather Boots.<br>\
<br>\
<span class=\"myBlue\">Fel Leather Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Leather</span>\
<br>196 Armor<br>Durability 50 / 50<br>\
<span class='myYellowGem'>Yellow Socket</span>\
<span class='myRedGem'>Red Socket</span>\
<span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 69<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 36.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fel Skin (0/3)</span>\
<br>Requires Leatherworking (350)<br> Fel Leather Gloves<br> Fel Leather Boots<br> Fel Leather Leggings<br>\
<br>(3) Set: Increases your dodge rating by 20.\
<br>Requires Heavy Knothide Leather (10), Fel Hide (8), Primal Shadow (8), Rune Thread (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelLeatherBoots; ++i;

var fPatternFelLeatherLeggings = new RewardItem("alliance","Pattern: Fel Leather Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternFelLeatherLeggings.itemMoneyPrice = new Array();
fPatternFelLeatherLeggings.itemMoneyPrice[2] = 140000
fPatternFelLeatherLeggings.itemStats = new Array();
fPatternFelLeatherLeggings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Fel Leather Leggings</span>\
<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Consortium - Revered<br>Use: Teaches you how to make Fel Leather Leggings.<br>\
<br>\
<span class=\"myBlue\">Fel Leather Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Leather</span>\
<br>249 Armor<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +8 Attack Power</span>\
<br>Requires Level 69<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 52.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fel Skin (0/3)</span>\
<br>Requires Leatherworking (350)<br> Fel Leather Gloves<br> Fel Leather Boots<br> Fel Leather Leggings<br>\
<br>\
<span class=\"myGray\">(3) Set: Increases your dodge rating by 20.</span>\
<br>\
<br>Requires Heavy Knothide Leather (10), Fel Hide (10), Primal Shadow (10), Rune Thread (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFelLeatherLeggings; ++i;



var fConsortiumBlaster = new RewardItem("alliance","Consortium Blaster","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fconsortium%2Fscripts%2Frewards-consortium.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Rifle_01.gif&reason=external-or-uncollected-resource");
fConsortiumBlaster.itemMoneyPrice = new Array();
fConsortiumBlaster.itemMoneyPrice[2] = 344063
fConsortiumBlaster.itemStats = new Array();
fConsortiumBlaster.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Consortium Blaster</span>\
<br>Binds when picked up<br>Unique<br>Ranged<span class=\"myRight\">Gun</span>\
<br>111 - 207 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(66.2 damage per second)<br>+15 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>Requires The Consortium - Revered<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 7.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fConsortiumBlaster; ++i;

var fNomadsLeggings = new RewardItem("alliance","Nomad's Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fconsortium%2Fscripts%2Frewards-consortium.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_02.gif&reason=external-or-uncollected-resource");
fNomadsLeggings.itemMoneyPrice = new Array();
fNomadsLeggings.itemMoneyPrice[2] = 230189
fNomadsLeggings.itemStats = new Array();
fNomadsLeggings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Nomad's Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Leather</span>\
<br>256 Armor<br>+33 Agility<br>+49 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>Requires The Consortium - Revered<br>\
<span class=\"myGreen\">Equip: Increases attack power by 66.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNomadsLeggings; ++i;

var fStormspireVest = new RewardItem("alliance","Stormspire Vest","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_cloth_08.jpg");
fStormspireVest.itemMoneyPrice = new Array();
fStormspireVest.itemMoneyPrice[2] = 167172
fStormspireVest.itemStats = new Array();
fStormspireVest.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Stormspire Vest</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+49 Stamina<br>Durability 80 / 80<br>Requires Level 70<br>Requires The Consortium - Revered<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 13 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormspireVest; ++i;


var fHaramadsBargain = new RewardItem("alliance","Haramad's Bargain","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_necklace_29.jpg");
fHaramadsBargain.itemMoneyPrice = new Array();
fHaramadsBargain.itemMoneyPrice[3] = 790112
fHaramadsBargain.itemStats = new Array();
fHaramadsBargain.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Haramad's Bargain</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+26 Strength<br>+25 Agility<br>Requires Level 70<br>Requires The Consortium - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHaramadsBargain; ++i;

var fGuileOfKhoraazi = new RewardItem("alliance","Guile of Khoraazi","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fconsortium%2Fscripts%2Frewards-consortium.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Sword_53.gif&reason=external-or-uncollected-resource");
fGuileOfKhoraazi.itemMoneyPrice = new Array();
fGuileOfKhoraazi.itemMoneyPrice[3] = 1905745
fGuileOfKhoraazi.itemStats = new Array();
fGuileOfKhoraazi.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Guile of Khoraazi</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>104 - 156 Damage<span class=\"myRight\">Speed 1.60</span>\
<br>(81.3 damage per second)<br>+19 Agility<br>Durability 75 / 75<br>Requires Level 70<br>Requires The Consortium - Exalted<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGuileOfKhoraazi; ++i;

var fNetherRunnersCowl = new RewardItem("alliance","Nether Runner's Cowl","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fNetherRunnersCowl.itemMoneyPrice = new Array();
fNetherRunnersCowl.itemMoneyPrice[3] = 573916
fNetherRunnersCowl.itemStats = new Array();
fNetherRunnersCowl.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Nether Runner's Cowl</span>\
<br>Binds when picked up<br>Unique<br>Head<span class=\"myRight\">Cloth</span>\
<br>145 Armor<br>+45 Stamina<br>+39 Intellect<br>Durability 60 / 60<br>\
<span class='myYellowGem'>Yellow Socket</span>\
<span class='myMetaGem'>Meta Socket</span>\
Socket Bonus: +4 Spell Damage<br>\
Requires Level 70<br>Requires The Consortium - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNetherRunnersCowl; ++i;

var fConsortiumTabard = new RewardItem("alliance","Consortium Tabard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fconsortium%2Fscripts%2Frewards-consortium.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Falteracvalley%2Fstormpikebattletabard.gif&reason=external-or-uncollected-resource");
fConsortiumTabard.itemMoneyPrice = new Array();
fConsortiumTabard.itemMoneyPrice[3] = 10000
fConsortiumTabard.itemStats = new Array();
fConsortiumTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Consortium Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires The Consortium - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fConsortiumTabard; ++i;




//-------------------------------------------------------------------
//---Horde below


var fNethershard = new RewardItem("horde","Nethershard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Weapon_ShortBlade_08.gif");
fNethershard.itemHonorPrice = new Array();
fNethershard.itemHonorPrice[1] = 465
fNethershard.itemStats = new Array();
fNethershard.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Nethershard</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>40 - 99 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(41.2 damage per second)<br>+15 Stamina<br>+18 Intellect<br>Durability 65 / 65<br>Requires Level 63<br>Requires The Consortium - Honored<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 6.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 61.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNethershard; ++i;






//------END REWARDS DEFINITION------
