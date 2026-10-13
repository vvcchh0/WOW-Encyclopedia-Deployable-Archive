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
			selectBracket(thisObject,thisBracket-1);
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

/*
var fXXX = new RewardItem("alliance","XXX","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2FXXX.gif&reason=external-or-uncollected-resource");
fXXX.itemMoneyPrice = new Array();
fXXX.itemStats = new Array();
fXXX.itemMoneyPrice[0] = XXX;
fXXX.itemStats[0] = "Zug zug!";
RewardItems[i] = fXXX; i++;
*/

var fHealingDraught1 = new RewardItem("alliance","Superior Healing Draught","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fhealth02.gif&reason=external-or-uncollected-resource");
fHealingDraught1.itemMoneyPrice = new Array();
fHealingDraught1.itemStats = new Array();
fHealingDraught1.itemMoneyPrice[2] = 500;
fHealingDraught1.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Superior Healing Draught</b><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 health. This item may only be used in PvP Battlegrounds.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHealingDraught1; i++;

var fManaDraught1 = new RewardItem("alliance","Superior Mana Draught","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fmana02.gif&reason=external-or-uncollected-resource");
fManaDraught1.itemMoneyPrice = new Array();
fManaDraught1.itemStats = new Array();
fManaDraught1.itemMoneyPrice[2] = 500;
fManaDraught1.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Superior Mana Draught</b><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 mana. This item may only be used in PvP Battlegrounds.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fManaDraught1; i++;





var fHighlandersFieldRations = new RewardItem("alliance","Highlander's Field Ration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Ffieldration.gif&reason=external-or-uncollected-resource");
fHighlandersFieldRations.itemMoneyPrice = new Array();
fHighlandersFieldRations.itemStats = new Array();
fHighlandersFieldRations.itemMoneyPrice[1] = 1000;
fHighlandersFieldRations.itemStats[1] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Highlander's Field Ration</b><br>\
Binds when picked up<br>\
Requires Level 25<br>\
<span class='myGreen'>Use: Restores 1074 health and 2202 mana over 30 sec. Must remain seated while eating. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersFieldRations; i++;


var fHighlandersIronRations = new RewardItem("alliance","Highlander's Iron Ration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fironration.gif&reason=external-or-uncollected-resource");
fHighlandersIronRations.itemMoneyPrice = new Array();
fHighlandersIronRations.itemStats = new Array();
fHighlandersIronRations.itemMoneyPrice[2] = 1500;
fHighlandersIronRations.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Highlander's Iron Ration</b><br>\
Binds when picked up<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 1608 health and 3306 mana over 30 sec. Must remain seated while eating. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersIronRations; i++;


var fHighlandersEnrichedRations = new RewardItem("alliance","Highlander's Enriched Ration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fenrichedration.gif&reason=external-or-uncollected-resource");
fHighlandersEnrichedRations.itemMoneyPrice = new Array();
fHighlandersEnrichedRations.itemStats = new Array();
fHighlandersEnrichedRations.itemMoneyPrice[3] = 2000;
fHighlandersEnrichedRations.itemStats[3] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Highlander's Enriched Ration</b><br>\
Binds when picked up<br>\
Requires Level 45<br>\
<span class='myGreen'>Use: Restores 2148 health and 4410 mana over 30 sec. Must remain seated while eating. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersEnrichedRations; i++;





var fHighlandersSilkBandages = new RewardItem("alliance","Highlander's Silk Bandage","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fsilkbandage.gif&reason=external-or-uncollected-resource");
fHighlandersSilkBandages.itemMoneyPrice = new Array();
fHighlandersSilkBandages.itemStats = new Array();
fHighlandersSilkBandages.itemMoneyPrice[1] = 1000;
fHighlandersSilkBandages.itemStats[1] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Highlander's Silk Bandage</b><br>\
Binds when picked up<br>\
Requires Level 25<br>\
Requires First Aid (125)<br>\
<span class='myGreen'>Use: Heals 640 damage over 8 sec. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersSilkBandages; i++;

var fHighlandersMageweaveBandages = new RewardItem("alliance","Highlander's Mageweave Bandage","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fmageweavebandage.gif&reason=external-or-uncollected-resource");
fHighlandersMageweaveBandages.itemMoneyPrice = new Array();
fHighlandersMageweaveBandages.itemStats = new Array();
fHighlandersMageweaveBandages.itemMoneyPrice[2] = 1500;
fHighlandersMageweaveBandages.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Highlander's Mageweave Bandage</b><br>\
Binds when picked up<br>\
Requires Level 35<br>\
Requires First Aid (175)<br>\
<span class='myGreen'>Use: Heals 1104 damage over 8 sec. Usable only inside Arathi Basin</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersMageweaveBandages; i++;

var fHighlandersRuneclothBandages = new RewardItem("alliance","Highlander's Runecloth Bandage","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fruneclothbandage.gif&reason=external-or-uncollected-resource");
fHighlandersRuneclothBandages.itemMoneyPrice = new Array();
fHighlandersRuneclothBandages.itemStats = new Array();
fHighlandersRuneclothBandages.itemMoneyPrice[3] = 2000;
fHighlandersRuneclothBandages.itemStats[3] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Highlander's Runecloth Bandage</b><br>\
Binds when picked up<br>\
Requires Level 45<br>\
Requires First Aid (225)<br>\
<span class='myGreen'>Use: Heals 2000 damage over 8 sec. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersRuneclothBandages; i++;







var fTalismanOfArathor = new RewardItem("alliance","Talisman of Arathor","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Ftalis01.gif&reason=external-or-uncollected-resource");
//NEW - HONOR AND TOKEN PRICE
fTalismanOfArathor.itemHonorPrice = new Array();
fTalismanOfArathor.itemHonorPrice[1] = 206
fTalismanOfArathor.itemTokenPrice = new Array();
fTalismanOfArathor.itemTokenPrice[1] = new Array(0,30,0,0);
fTalismanOfArathor.itemStats = new Array();
fTalismanOfArathor.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Talisman of Arathor</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 28<br>\
<span class=\"myGreen\">Use: Absorbs 248 to 302 physical damage.  Lasts 15.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fTalismanOfArathor.itemHonorPrice[2] = 304;
fTalismanOfArathor.itemTokenPrice[2] = new Array(0,30,0,0);
fTalismanOfArathor.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myBlue'>Talisman of Arathor</span><br>\
Binds when picked up<br>\
Unique<br>\
Trinket<br>\
Requires Level 38<br>\
Requires The League of Arathor - Friendly<br>\
<span class='myGreen'>Use: Absorbs 310 to 378 physical damage. Lasts 15 sec.</span>\
</span>\
</div></td></tr></table>";
fTalismanOfArathor.itemHonorPrice[3] = 449;
fTalismanOfArathor.itemTokenPrice[3] = new Array(0,30,0,0);
fTalismanOfArathor.itemStats[3] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myBlue'>Talisman of Arathor</span><br>\
Binds when picked up<br>\
Unique<br>\
Trinket<br>\
Requires Level 48<br>\
Requires The League of Arathor - Friendly<br>\
<span class='myGreen'>Use: Absorbs 392 to 478 physical damage. Lasts 15 sec.</span>\
</span>\
</div></td></tr></table>";
fTalismanOfArathor.itemHonorPrice[4] = 3300;
fTalismanOfArathor.itemTokenPrice[4] = new Array(0,30,0,0);
fTalismanOfArathor.itemStats[4] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myBlue'>Talisman of Arathor</span><br>\
Binds when picked up<br>\
Unique<br>\
Trinket<br>\
Requires Level 58<br>\
Requires The League of Arathor - Friendly<br>\
<span class='myGreen'>Use: Absorbs 495 to 605 physical damage. Lasts 15 sec.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fTalismanOfArathor; i++;



var fHighlandersChainGirdle = new RewardItem("alliance","Highlander's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt03.gif&reason=external-or-uncollected-resource");
//NEW - HONOR AND TOKEN PRICE
fHighlandersChainGirdle.itemHonorPrice = new Array();
fHighlandersChainGirdle.itemHonorPrice[1] = 206;
fHighlandersChainGirdle.itemTokenPrice = new Array();
fHighlandersChainGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
//END - HONOR AND TOKEN PRICE
fHighlandersChainGirdle.itemStats = new Array();
fHighlandersChainGirdle.itemStats[1] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myBlue'>Highlander's Chain Girdle</span><br>\
Binds when picked up<br>\
Unique<br>\
Waist<span class='myRight'>Leather</span><br>\
61 Armor<br>\
+5 Stamina<br>\
Classes: Hunter, Shaman<br>\
Requires Level 28<br>\
<span class='myGreen'>Equip: Increases your attack power by 24.</span><br>\
</div></td></tr></table>";
fHighlandersChainGirdle.itemHonorPrice[2] = 304;
fHighlandersChainGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersChainGirdle.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myBlue'>Highlander's Chain Girdle</span><br>\
Binds when picked up<br>\
Unique<br>\
Waist<span class='myRight'>Mail</span><br>\
149 Armor<br>\
+6 Stamina<br>\
Classes: Hunter, Shaman<br>\
Requires Level 40<br>\
<span class='myGreen'>Equip: Increases your critical strike rating by 14.<br>\
Equip: Increases your attack power by 8.</span><br>\
</div></td></tr></table>";
fHighlandersChainGirdle.itemHonorPrice[3] = 449;
fHighlandersChainGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersChainGirdle.itemStats[3] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myBlue'>Highlander's Chain Girdle</span><br>\
Binds when picked up<br>\
Unique<br>\
Waist<span class='myRight'>Mail</span><br>\
178 Armor<br>\
+8 Stamina<br>\
Classes: Hunter, Shaman<br>\
Requires Level 48<br>\
<span class='myGreen'>Equip: Increases your critical strike rating by 14.<br>\
Equip: Increases your attack power by 20.</span><br>\
</div></td></tr></table>";
fHighlandersChainGirdle.itemHonorPrice[4] = 3300;
fHighlandersChainGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersChainGirdle.itemStats[4] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myBlue'>Highlander's Chain Girdle</span><br>\
Binds when picked up<br>\
Unique<br>\
Waist<span class='myRight'>Mail</span><br>\
208 Armor<br>\
+10 Stamina<br>\
Classes: Hunter, Shaman<br>\
Requires Level 58<br>\
<br>\
<span class='myGreen'>Equip: Increases your critical strike rating by 14.<br>\
Equip: Increases attack power by 34.</span><br>\
<br>\
<b class='myYellow'>The Highlander's Determination</b><br>\
<span class='myGray' style='margin-left:5px;'>Highlander's Chain Girdle</b><br>\
<span class='myGray' style='margin-left:5px;'>Highlander's Chain Greaves</b><br>\
<span class='myGray' style='margin-left:5px;'>Highlander's Chain Pauldrons</b>\
<br><br>\
<span class='myGray'>(2) Set: +5 Stamina.</span><br>\
<span class='myGray'>(3) Set: Increases your critical strike rating by 14.</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersChainGirdle; i++;





var fHighlandersClothGirdle = new RewardItem("alliance","Highlander's Cloth Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt01.gif&reason=external-or-uncollected-resource");
fHighlandersClothGirdle.itemHonorPrice = new Array();
fHighlandersClothGirdle.itemHonorPrice[1] = 206
fHighlandersClothGirdle.itemTokenPrice = new Array();
fHighlandersClothGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersClothGirdle.itemStats = new Array();
fHighlandersClothGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>88 Armor<br>+4 Stamina<br>+3 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 11.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersClothGirdle.itemHonorPrice[2] = 304
fHighlandersClothGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersClothGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>105 Armor<br>+4 Stamina<br>+4 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersClothGirdle.itemHonorPrice[3] = 449
fHighlandersClothGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersClothGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>113 Armor<br>+6 Stamina<br>+5 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersClothGirdle.itemHonorPrice[4] = 3300
fHighlandersClothGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersClothGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>150 Armor<br>+7 Stamina<br>+6 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Intent (0/3)</span>\
<br> Highlander's Cloth Boots<br> Highlander's Cloth Girdle<br> Highlander's Epaulets<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersClothGirdle; ++i;



var fHighlandersLizardhideGirdle = new RewardItem("alliance","Highlander's Lizardhide Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt01.gif&reason=external-or-uncollected-resource");
fHighlandersLizardhideGirdle.itemHonorPrice = new Array();
fHighlandersLizardhideGirdle.itemHonorPrice[1] = 206
fHighlandersLizardhideGirdle.itemTokenPrice = new Array();
fHighlandersLizardhideGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersLizardhideGirdle.itemStats = new Array();
fHighlandersLizardhideGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>91 Armor<br>+4 Stamina<br>+12 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLizardhideGirdle.itemHonorPrice[2] = 304
fHighlandersLizardhideGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersLizardhideGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>113 Armor<br>+4 Stamina<br>+15 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 38</span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLizardhideGirdle.itemHonorPrice[3] = 449
fHighlandersLizardhideGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersLizardhideGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>136 Armor<br>+6 Stamina<br>+10 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLizardhideGirdle.itemHonorPrice[4] = 3300
fHighlandersLizardhideGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersLizardhideGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>159 Armor<br>+7 Stamina<br>+17 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Will (0/3)</span>\
<br> Highlander's Lizardhide Boots<br> Highlander's Lizardhide Girdle<br> Highlander's Lizardhide Shoulders<br>\
<br>(3) Set: Increases your spell critical strike rating by 14.<br>(2) Set: +5 Stamina.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLizardhideGirdle; ++i;




var fHighlandersLeatherGirdle = new RewardItem("alliance","Highlander's Leather Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt01.gif&reason=external-or-uncollected-resource");
//NEW - HONOR AND TOKEN PRICE
fHighlandersLeatherGirdle.itemHonorPrice = new Array();
fHighlandersLeatherGirdle.itemHonorPrice[1] = 206
fHighlandersLeatherGirdle.itemTokenPrice = new Array();
fHighlandersLeatherGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersLeatherGirdle.itemStats = new Array();
fHighlandersLeatherGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>91 Armor<br>+4 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLeatherGirdle.itemHonorPrice[2] = 304
fHighlandersLeatherGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersLeatherGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>113 Armor<br>+4 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLeatherGirdle.itemHonorPrice[3] = 449
fHighlandersLeatherGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersLeatherGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>136 Armor<br>+6 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLeatherGirdle.itemHonorPrice[4] = 3300
fHighlandersLeatherGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersLeatherGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>159 Armor<br>+7 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Purpose (0/3)</span>\
<br> Highlander's Leather Boots<br> Highlander's Leather Girdle<br> Highlander's Leather Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLeatherGirdle; ++i;









var fHighlandersLamellarGirdle = new RewardItem("alliance","Highlander's Lamellar Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt02.gif&reason=external-or-uncollected-resource");
fHighlandersLamellarGirdle.itemHonorPrice = new Array();
fHighlandersLamellarGirdle.itemHonorPrice[1] = 206
fHighlandersLamellarGirdle.itemTokenPrice = new Array();
fHighlandersLamellarGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersLamellarGirdle.itemStats = new Array();
fHighlandersLamellarGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>128 Armor<br>+11 Strength<br>+4 Stamina<br>+5 Intellect<br>Durability 40 / 40<br>Classes: Paladin<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLamellarGirdle.itemHonorPrice[2] = 304
fHighlandersLamellarGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersLamellarGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>236 Armor<br>+12 Strength<br>+6 Stamina<br>+6 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLamellarGirdle.itemHonorPrice[3] = 449
fHighlandersLamellarGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersLamellarGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>313 Armor<br>+11 Strength<br>+4 Stamina<br>+8 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLamellarGirdle.itemHonorPrice[4] = 3300
fHighlandersLamellarGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersLamellarGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>369 Armor<br>+15 Strength<br>+6 Stamina<br>+10 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Resolve (0/3)</span>\
<br> Highlander's Lamellar Girdle<br> Highlander's Lamellar Greaves<br> Highlander's Lamellar Spaulders<br>\
<br>(3) Set: Increases your critical strike rating by 14.<br>(2) Set: +4 Stamina.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLamellarGirdle; i++;





var fHighlandersPlateGirdle = new RewardItem("alliance","Highlander's Plate Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt02.gif&reason=external-or-uncollected-resource");
fHighlandersPlateGirdle.itemHonorPrice = new Array();
fHighlandersPlateGirdle.itemHonorPrice[1] = 206
fHighlandersPlateGirdle.itemTokenPrice = new Array();
fHighlandersPlateGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersPlateGirdle.itemStats = new Array();
fHighlandersPlateGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>128 Armor<br>+12 Strength<br>+5 Stamina<br>Durability 40 / 40<br>Classes: Warrior, Paladin<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersPlateGirdle.itemHonorPrice[2] = 304
fHighlandersPlateGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersPlateGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>236 Armor<br>+15 Strength<br>+6 Stamina<br>Durability 45 / 45<br>Classes: Warrior, Paladin<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersPlateGirdle.itemHonorPrice[3] = 449
fHighlandersPlateGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersPlateGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>313 Armor<br>+10 Strength<br>+8 Stamina<br>Durability 45 / 45<br>Classes: Warrior, Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersPlateGirdle.itemHonorPrice[4] = 3300
fHighlandersPlateGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersPlateGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>369 Armor<br>+17 Strength<br>+10 Stamina<br>Durability 45 / 45<br>Classes: Warrior, Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Resolution (0/3)</span>\
<br> Highlander's Plate Girdle<br> Highlander's Plate Greaves<br> Highlander's Plate Spaulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersPlateGirdle; i++;







var fHighlandersChainGreaves = new RewardItem("alliance","Highlander's Chain Greaves","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots02.gif&reason=external-or-uncollected-resource");
fHighlandersChainGreaves.itemHonorPrice = new Array();
fHighlandersChainGreaves.itemHonorPrice[1] = 206
fHighlandersChainGreaves.itemTokenPrice = new Array();
fHighlandersChainGreaves.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersChainGreaves.itemStats = new Array();
fHighlandersChainGreaves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>74 Armor<br>+8 Agility<br>+8 Stamina<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersChainGreaves.itemHonorPrice[2] = 304
fHighlandersChainGreaves.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersChainGreaves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>183 Armor<br>+7 Agility<br>+10 Stamina<br>+3 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersChainGreaves.itemHonorPrice[3] = 449
fHighlandersChainGreaves.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersChainGreaves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>218 Armor<br>+8 Agility<br>+13 Stamina<br>+6 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersChainGreaves.itemHonorPrice[4] = 3300
fHighlandersChainGreaves.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersChainGreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>255 Armor<br>+10 Agility<br>+16 Stamina<br>+8 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Determination (0/3)</span>\
<br> Highlander's Chain Girdle<br> Highlander's Chain Greaves<br> Highlander's Chain Pauldrons<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersChainGreaves; i++;










var fHighlandersClothBoots = new RewardItem("alliance","Highlander's Cloth Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots05.gif&reason=external-or-uncollected-resource");
fHighlandersClothBoots.itemHonorPrice = new Array();
fHighlandersClothBoots.itemHonorPrice[1] = 206
fHighlandersClothBoots.itemTokenPrice = new Array();
fHighlandersClothBoots.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersClothBoots.itemStats = new Array();
fHighlandersClothBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>84 Armor<br>+8 Stamina<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 7.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersClothBoots.itemHonorPrice[2] = 304
fHighlandersClothBoots.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersClothBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+10 Stamina<br>+3 Intellect<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 8.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersClothBoots.itemHonorPrice[3] = 449
fHighlandersClothBoots.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersClothBoots.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>132 Armor<br>+13 Stamina<br>+6 Intellect<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersClothBoots.itemHonorPrice[4] = 3300
fHighlandersClothBoots.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersClothBoots.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>161 Armor<br>+16 Stamina<br>+8 Intellect<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Intent (0/3)</span>\
<br> Highlander's Cloth Boots<br> Highlander's Cloth Girdle<br> Highlander's Epaulets<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersClothBoots; i++;






var fHighlandersLizardhideBoots = new RewardItem("alliance","Highlander's Lizardhide Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots04.gif&reason=external-or-uncollected-resource");
fHighlandersLizardhideBoots.itemHonorPrice = new Array();
fHighlandersLizardhideBoots.itemHonorPrice[1] = 206
fHighlandersLizardhideBoots.itemTokenPrice = new Array();
fHighlandersLizardhideBoots.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersLizardhideBoots.itemStats = new Array();
fHighlandersLizardhideBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>104 Armor<br>+5 Agility<br>+8 Stamina<br>+4 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLizardhideBoots.itemHonorPrice[2] = 304
fHighlandersLizardhideBoots.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersLizardhideBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>129 Armor<br>+6 Agility<br>+10 Stamina<br>+5 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 6.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLizardhideBoots.itemHonorPrice[3] = 449
fHighlandersLizardhideBoots.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersLizardhideBoots.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>145 Armor<br>+8 Agility<br>+13 Stamina<br>+7 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLizardhideBoots.itemHonorPrice[4] = 3300
fHighlandersLizardhideBoots.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersLizardhideBoots.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>181 Armor<br>+8 Agility<br>+16 Stamina<br>+8 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Will (0/3)</span>\
<br> Highlander's Lizardhide Boots<br> Highlander's Lizardhide Girdle<br> Highlander's Lizardhide Shoulders<br>\
<br>(3) Set: Increases your spell critical strike rating by 14.<br>(2) Set: +5 Stamina.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLizardhideBoots; i++;


var fHighlandersLeatherBoots = new RewardItem("alliance","Highlander's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots03.gif&reason=external-or-uncollected-resource");
fHighlandersLeatherBoots.itemHonorPrice = new Array();
fHighlandersLeatherBoots.itemHonorPrice[1] = 206
fHighlandersLeatherBoots.itemTokenPrice = new Array();
fHighlandersLeatherBoots.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersLeatherBoots.itemStats = new Array();
fHighlandersLeatherBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>104 Armor<br>+7 Agility<br>+8 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLeatherBoots.itemHonorPrice[2] = 304
fHighlandersLeatherBoots.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersLeatherBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>129 Armor<br>+8 Agility<br>+10 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 6.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLeatherBoots.itemHonorPrice[3] = 449
fHighlandersLeatherBoots.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersLeatherBoots.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>145 Armor<br>+11 Agility<br>+13 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLeatherBoots.itemHonorPrice[4] = 3300
fHighlandersLeatherBoots.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersLeatherBoots.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>181 Armor<br>+12 Agility<br>+16 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Purpose (0/3)</span>\
<br> Highlander's Leather Boots<br> Highlander's Leather Girdle<br> Highlander's Leather Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLeatherBoots; i++;








var fHighlandersLamellarGreaves = new RewardItem("alliance","Highlander's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots01.gif&reason=external-or-uncollected-resource");
fHighlandersLamellarGreaves.itemHonorPrice = new Array();
fHighlandersLamellarGreaves.itemHonorPrice[1] = 206
fHighlandersLamellarGreaves.itemTokenPrice = new Array();
fHighlandersLamellarGreaves.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersLamellarGreaves.itemStats = new Array();
fHighlandersLamellarGreaves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>157 Armor<br>+6 Strength<br>+6 Agility<br>+4 Stamina<br>+4 Intellect<br>Durability 60 / 60<br>Classes: Paladin<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLamellarGreaves.itemHonorPrice[2] = 304
fHighlandersLamellarGreaves.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersLamellarGreaves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>289 Armor<br>+8 Strength<br>+8 Agility<br>+6 Stamina<br>+5 Intellect<br>Durability 65 / 65<br>Classes: Paladin<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLamellarGreaves.itemHonorPrice[3] = 449
fHighlandersLamellarGreaves.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersLamellarGreaves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>383 Armor<br>+11 Strength<br>+10 Agility<br>+7 Stamina<br>+6 Intellect<br>Durability 65 / 65<br>Classes: Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersLamellarGreaves.itemHonorPrice[4] = 3300
fHighlandersLamellarGreaves.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersLamellarGreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>452 Armor<br>+14 Strength<br>+12 Agility<br>+8 Stamina<br>+8 Intellect<br>Durability 65 / 65<br>Classes: Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Resolve (0/3)</span>\
<br> Highlander's Lamellar Girdle<br> Highlander's Lamellar Greaves<br> Highlander's Lamellar Spaulders<br>\
<br>(3) Set: Increases your critical strike rating by 14.<br>(2) Set: +5 Stamina.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLamellarGreaves; i++;





















var fHighlandersPlateGreaves = new RewardItem("alliance","Highlander's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots01.gif&reason=external-or-uncollected-resource");
//NEW - HONOR AND TOKEN PRICE
fHighlandersPlateGreaves.itemHonorPrice = new Array();
fHighlandersPlateGreaves.itemHonorPrice[1] = 206
fHighlandersPlateGreaves.itemTokenPrice = new Array();
fHighlandersPlateGreaves.itemTokenPrice[1] = new Array(0,20,0,0);
fHighlandersPlateGreaves.itemStats = new Array();
fHighlandersPlateGreaves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>157 Armor<br>+6 Strength<br>+6 Agility<br>+6 Stamina<br>Durability 60 / 60<br>Classes: Warrior, Paladin<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersPlateGreaves.itemHonorPrice[2] = 304
fHighlandersPlateGreaves.itemTokenPrice[2] = new Array(0,20,0,0);
fHighlandersPlateGreaves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>289 Armor<br>+8 Strength<br>+8 Agility<br>+8 Stamina<br>Durability 65 / 65<br>Classes: Warrior, Paladin<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersPlateGreaves.itemHonorPrice[3] = 449
fHighlandersPlateGreaves.itemTokenPrice[3] = new Array(0,20,0,0);
fHighlandersPlateGreaves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>383 Armor<br>+11 Strength<br>+10 Agility<br>+10 Stamina<br>Durability 65 / 65<br>Classes: Warrior, Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fHighlandersPlateGreaves.itemHonorPrice[4] = 3300
fHighlandersPlateGreaves.itemTokenPrice[4] = new Array(0,20,0,0);
fHighlandersPlateGreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Highlander's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>452 Armor<br>+14 Strength<br>+12 Agility<br>+12 Stamina<br>Durability 65 / 65<br>Classes: Warrior, Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Resolution (0/3)</span>\
<br> Highlander's Plate Girdle<br> Highlander's Plate Greaves<br> Highlander's Plate Spaulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersPlateGreaves; i++;









var fHighlandersChainPauldrons = new RewardItem("alliance","Highlander's Chain Pauldrons","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders02.gif&reason=external-or-uncollected-resource");
fHighlandersChainPauldrons.itemHonorPrice = new Array();
fHighlandersChainPauldrons.itemHonorPrice[5] = 9900
fHighlandersChainPauldrons.itemTokenPrice = new Array();
fHighlandersChainPauldrons.itemTokenPrice[5] = new Array(0,40,0,0);
fHighlandersChainPauldrons.itemStats = new Array();
fHighlandersChainPauldrons.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Highlander's Chain Pauldrons</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>356 Armor<br>+14 Agility<br>+18 Stamina<br>+17 Intellect<br>Durability 85 / 85<br>Classes: Hunter, Shaman<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Determination (0/3)</span>\
<br> Highlander's Chain Girdle<br> Highlander's Chain Greaves<br> Highlander's Chain Pauldrons<br>\
<br>(2) Set: +$s1 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersChainPauldrons; ++i;







var fHighlandersEpaulets = new RewardItem("alliance","Highlander's Epaulets","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders01.gif&reason=external-or-uncollected-resource");
fHighlandersEpaulets.itemHonorPrice = new Array();
fHighlandersEpaulets.itemHonorPrice[5] = 9900
fHighlandersEpaulets.itemTokenPrice = new Array();
fHighlandersEpaulets.itemTokenPrice[5] = new Array(0,40,0,0);
fHighlandersEpaulets.itemStats = new Array();
fHighlandersEpaulets.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Highlander's Epaulets</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>196 Armor<br>+18 Stamina<br>+17 Intellect<br>Durability 60 / 60<br>Classes: Priest, Mage, Warlock<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Intent (0/3)</span>\
<br> Highlander's Cloth Boots<br> Highlander's Cloth Girdle<br> Highlander's Epaulets<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersEpaulets; ++i;




var fHighlandersLizardhideShoulders = new RewardItem("alliance","Highlander's Lizardhide Shoulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders01.gif&reason=external-or-uncollected-resource");
fHighlandersLizardhideShoulders.itemHonorPrice = new Array();
fHighlandersLizardhideShoulders.itemHonorPrice[5] = 9900
fHighlandersLizardhideShoulders.itemTokenPrice = new Array();
fHighlandersLizardhideShoulders.itemTokenPrice[5] = new Array(0,40,0,0);
fHighlandersLizardhideShoulders.itemStats = new Array();
fHighlandersLizardhideShoulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Highlander's Lizardhide Shoulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>279 Armor<br>+12 Agility<br>+17 Stamina<br>+12 Intellect<br>Durability 70 / 70<br>Classes: Rogue, Druid<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Will (0/3)</span>\
<br> Highlander's Lizardhide Boots<br> Highlander's Lizardhide Girdle<br> Highlander's Lizardhide Shoulders<br>\
<br>(3) Set: Increases your spell critical strike rating by 14.<br>(2) Set: +5 Stamina.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLizardhideShoulders; ++i;





var fHighlandersLeatherShoulders = new RewardItem("alliance","Highlander's Leather Shoulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders01.gif&reason=external-or-uncollected-resource");
fHighlandersLeatherShoulders.itemHonorPrice = new Array();
fHighlandersLeatherShoulders.itemHonorPrice[5] = 9900
fHighlandersLeatherShoulders.itemTokenPrice = new Array();
fHighlandersLeatherShoulders.itemTokenPrice[5] = new Array(0,40,0,0);
fHighlandersLeatherShoulders.itemStats = new Array();
fHighlandersLeatherShoulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Highlander's Leather Shoulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>279 Armor<br>+18 Agility<br>+17 Stamina<br>Durability 70 / 70<br>Classes: Rogue, Druid<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Highlander's Purpose (0/3)</span>\
<br> Highlander's Leather Boots<br> Highlander's Leather Girdle<br> Highlander's Leather Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLeatherShoulders; ++i;




var fHighlandersLamellarSpaulders = new RewardItem("alliance","Highlander's Lamellar Spaulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders02.gif&reason=external-or-uncollected-resource");
fHighlandersLamellarSpaulders.itemHonorPrice = new Array();
fHighlandersLamellarSpaulders.itemHonorPrice[5] = 9900
fHighlandersLamellarSpaulders.itemTokenPrice = new Array();
fHighlandersLamellarSpaulders.itemTokenPrice[5] = new Array(0,40,0,0);
fHighlandersLamellarSpaulders.itemStats = new Array();
fHighlandersLamellarSpaulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Highlander's Lamellar Spaulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>632 Armor<br>+18 Strength<br>+17 Agility<br>+15 Stamina<br>+10 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 60<br>\
<br>\
<span class=\"myYellow\">The Highlander's Resolve (0/3)</span>\
<br> Highlander's Lamellar Girdle<br> Highlander's Lamellar Greaves<br> Highlander's Lamellar Spaulders<br>\
<br>(3) Set: Increases your critical strike rating by 14.<br>(2) Set: +5 Stamina.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersLamellarSpaulders; ++i;











var fHighlandersPlateSpaulders = new RewardItem("alliance","Highlander's Plate Spaulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders02.gif&reason=external-or-uncollected-resource");
fHighlandersPlateSpaulders.itemHonorPrice = new Array();
fHighlandersPlateSpaulders.itemHonorPrice[5] = 9900
fHighlandersPlateSpaulders.itemTokenPrice = new Array();
fHighlandersPlateSpaulders.itemTokenPrice[5] = new Array(0,40,0,0);
fHighlandersPlateSpaulders.itemStats = new Array();
fHighlandersPlateSpaulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Highlander's Plate Spaulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>632 Armor<br>+18 Strength<br>+17 Agility<br>+20 Stamina<br>Durability 100 / 100<br>Classes: Warrior, Paladin<br>Requires Level 60<br>\
<br>\
<span class=\"myYellow\">The Highlander's Resolution (0/3)</span>\
<br> Highlander's Plate Girdle<br> Highlander's Plate Greaves<br> Highlander's Plate Spaulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighlandersPlateSpaulders; ++i;













var fCloakOfTheHonorGuard = new RewardItem("alliance","Cloak of the Honor Guard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fcape01.gif&reason=external-or-uncollected-resource");
fCloakOfTheHonorGuard.itemHonorPrice = new Array();
fCloakOfTheHonorGuard.itemHonorPrice[5] = 5400
fCloakOfTheHonorGuard.itemTokenPrice = new Array();
fCloakOfTheHonorGuard.itemTokenPrice[5] = new Array(0,20,0,0);
fCloakOfTheHonorGuard.itemStats = new Array();
fCloakOfTheHonorGuard.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Cloak of the Honor Guard</span>\
<br>Binds when picked up<br>Back<br>57 Armor<br>+5 Agility<br>+11 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCloakOfTheHonorGuard; ++i;



var fIronbarkStaff = new RewardItem("alliance","Ironbark Staff","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fstaff01.gif&reason=external-or-uncollected-resource");
fIronbarkStaff.itemHonorPrice = new Array();
fIronbarkStaff.itemHonorPrice[5] = 18000
fIronbarkStaff.itemTokenPrice = new Array();
fIronbarkStaff.itemTokenPrice[5] = new Array(0,40,0,0);
fIronbarkStaff.itemStats = new Array();
fIronbarkStaff.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Ironbark Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>136 - 243 Damage<span class=\"myRight\">Speed 3.40</span>\
<br>(55.8 damage per second)<br>100 Armor<br>+19 Stamina<br>+10 Intellect<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 41.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIronbarkStaff; ++i;


var fSageclaw = new RewardItem("alliance","Sageclaw","/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/arathi/dagger01.gif");
fSageclaw.itemHonorPrice = new Array();
fSageclaw.itemHonorPrice[5] = 9600
fSageclaw.itemTokenPrice = new Array();
fSageclaw.itemTokenPrice[5] = new Array(0,40,0,0);
fSageclaw.itemStats = new Array();
fSageclaw.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Sageclaw</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Dagger</span>\
<br>46 - 96 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(41.7 damage per second)<br>40 Armor<br>+8 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSageclaw; ++i;













































//---Horde 1362

var fHealingDraught1 = new RewardItem("horde","Superior Healing Draught","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fhealth02.gif&reason=external-or-uncollected-resource");
fHealingDraught1.itemMoneyPrice = new Array();
fHealingDraught1.itemStats = new Array();
fHealingDraught1.itemMoneyPrice[2] = 500;
fHealingDraught1.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Superior Healing Draught</b><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 health. This item may only be used in PvP Battlegrounds.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHealingDraught1; i++;

var fManaDraught1 = new RewardItem("horde","Superior Mana Draught","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fmana02.gif&reason=external-or-uncollected-resource");
fManaDraught1.itemMoneyPrice = new Array();
fManaDraught1.itemStats = new Array();
fManaDraught1.itemMoneyPrice[2] = 500;
fManaDraught1.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Superior Mana Draught</b><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 mana. This item may only be used in PvP Battlegrounds.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fManaDraught1; i++;





var fHighlandersFieldRations = new RewardItem("horde","Defiler's Field Ration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Ffieldration.gif&reason=external-or-uncollected-resource");
fHighlandersFieldRations.itemMoneyPrice = new Array();
fHighlandersFieldRations.itemStats = new Array();
fHighlandersFieldRations.itemMoneyPrice[1] = 1000;
fHighlandersFieldRations.itemStats[1] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Defiler's Field Ration</b><br>\
Binds when picked up<br>\
Requires Level 25<br>\
<span class='myGreen'>Use: Restores 1074 health and 2202 mana over over 30 sec. Must remain seated while eating. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersFieldRations; i++;


var fHighlandersIronRations = new RewardItem("horde","Defiler's Iron Ration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fironration.gif&reason=external-or-uncollected-resource");
fHighlandersIronRations.itemMoneyPrice = new Array();
fHighlandersIronRations.itemStats = new Array();
fHighlandersIronRations.itemMoneyPrice[2] = 1500;
fHighlandersIronRations.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Defiler's Iron Ration</b><br>\
Binds when picked up<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 1608 health and 3306 mana over 30 sec. Must remain seated while eating. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersIronRations; i++;


var fHighlandersEnrichedRations = new RewardItem("horde","Defiler's Enriched Ration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fenrichedration.gif&reason=external-or-uncollected-resource");
fHighlandersEnrichedRations.itemMoneyPrice = new Array();
fHighlandersEnrichedRations.itemStats = new Array();
fHighlandersEnrichedRations.itemMoneyPrice[3] = 2000;
fHighlandersEnrichedRations.itemStats[3] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Defiler's Enriched Ration</b><br>\
Binds when picked up<br>\
Requires Level 45<br>\
<span class='myGreen'>Use: Restores 2148 health and 4410 mana over 30 sec. Must remain seated while eating. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersEnrichedRations; i++;





var fHighlandersSilkBandages = new RewardItem("horde","Defiler's Silk Bandage","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fsilkbandage.gif&reason=external-or-uncollected-resource");
fHighlandersSilkBandages.itemMoneyPrice = new Array();
fHighlandersSilkBandages.itemStats = new Array();
fHighlandersSilkBandages.itemMoneyPrice[1] = 1000;
fHighlandersSilkBandages.itemStats[1] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Defiler's Silk Bandage</b><br>\
Binds when picked up<br>\
Requires Level 25<br>\
Requires First Aid (125)<br>\
<span class='myGreen'>Use: Heals 640 damage over 8 sec. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersSilkBandages; i++;

var fHighlandersMageweaveBandages = new RewardItem("horde","Defiler's Mageweave Bandage","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fmageweavebandage.gif&reason=external-or-uncollected-resource");
fHighlandersMageweaveBandages.itemMoneyPrice = new Array();
fHighlandersMageweaveBandages.itemStats = new Array();
fHighlandersMageweaveBandages.itemMoneyPrice[2] = 1500;
fHighlandersMageweaveBandages.itemStats[2] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Defiler's Mageweave Bandage</b><br>\
Binds when picked up<br>\
Requires Level 35<br>\
Requires First Aid (175)<br>\
<span class='myGreen'>Use: Heals 1104 damage over 8 sec. Usable only inside Arathi Basin</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersMageweaveBandages; i++;

var fHighlandersRuneclothBandages = new RewardItem("horde","Defiler's Runecloth Bandage","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Fwarsong%2Fruneclothbandage.gif&reason=external-or-uncollected-resource");
fHighlandersRuneclothBandages.itemMoneyPrice = new Array();
fHighlandersRuneclothBandages.itemStats = new Array();
fHighlandersRuneclothBandages.itemMoneyPrice[3] = 2000;
fHighlandersRuneclothBandages.itemStats[3] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<b>Defiler's Runecloth Bandage</b><br>\
Binds when picked up<br>\
Requires Level 45<br>\
Requires First Aid (225)<br>\
<span class='myGreen'>Use: Heals 2000 damage over 8 sec. Usable only inside Arathi Basin.</span>\
</span>\
</div></td></tr></table>";
RewardItems[i] = fHighlandersRuneclothBandages; i++;







var fDefilersTalisman = new RewardItem("horde","Defiler's Talisman","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Ftalis01.gif&reason=external-or-uncollected-resource");
fDefilersTalisman.itemHonorPrice = new Array();
fDefilersTalisman.itemHonorPrice[1] = 206
fDefilersTalisman.itemTokenPrice = new Array();
fDefilersTalisman.itemTokenPrice[1] = new Array(0,30,0,0);
fDefilersTalisman.itemStats = new Array();
fDefilersTalisman.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Talisman</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 28<br>\
<span class=\"myGreen\">Use: Absorbs 248 to 302 physical damage.  Lasts 15 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersTalisman.itemHonorPrice[2] = 304
fDefilersTalisman.itemTokenPrice[2] = new Array(0,30,0,0);
fDefilersTalisman.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Talisman</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 38<br>\
<span class=\"myGreen\">Use: Absorbs 310 to 378 physical damage.  Lasts 15 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersTalisman.itemHonorPrice[3] = 449
fDefilersTalisman.itemTokenPrice[3] = new Array(0,30,0,0);
fDefilersTalisman.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Talisman</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 48<br>\
<span class=\"myGreen\">Use: Absorbs 392 to 478 physical damage.  Lasts 15 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersTalisman.itemHonorPrice[4] = 3300
fDefilersTalisman.itemTokenPrice[4] = new Array(0,30,0,0);
fDefilersTalisman.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Talisman</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 58<br>\
<span class=\"myGreen\">Use: Absorbs 495 to 605 physical damage.  Lasts 15 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersTalisman; ++i;










var fDefilersChainGirdle = new RewardItem("horde","Defiler's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt03.gif&reason=external-or-uncollected-resource");
fDefilersChainGirdle.itemHonorPrice = new Array();
fDefilersChainGirdle.itemHonorPrice[1] = 206
fDefilersChainGirdle.itemTokenPrice = new Array();
fDefilersChainGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersChainGirdle.itemStats = new Array();
fDefilersChainGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>61 Armor<br>+5 Stamina<br>Durability 35 / 35<br>Classes: Hunter, Shaman<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersChainGirdle.itemHonorPrice[2] = 304
fDefilersChainGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersChainGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>149 Armor<br>+6 Stamina<br>Durability 40 / 40<br>Classes: Hunter, Shaman<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 8.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersChainGirdle.itemHonorPrice[3] = 449
fDefilersChainGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersChainGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>178 Armor<br>+8 Stamina<br>Durability 40 / 40<br>Classes: Hunter, Shaman<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersChainGirdle.itemHonorPrice[4] = 3300
fDefilersChainGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersChainGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>208 Armor<br>+10 Stamina<br>Durability 40 / 40<br>Classes: Hunter, Shaman<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Determination (0/3)</span>\
<br> Defiler's Chain Pauldrons<br> Defiler's Chain Greaves<br> Defiler's Chain Girdle<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersChainGirdle; ++i;











var fDefilersClothGirdle = new RewardItem("horde","Defiler's Cloth Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt01.gif&reason=external-or-uncollected-resource");
fDefilersClothGirdle.itemHonorPrice = new Array();
fDefilersClothGirdle.itemHonorPrice[1] = 206
fDefilersClothGirdle.itemTokenPrice = new Array();
fDefilersClothGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersClothGirdle.itemStats = new Array();
fDefilersClothGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>88 Armor<br>+4 Stamina<br>+3 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 11.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersClothGirdle.itemHonorPrice[2] = 304
fDefilersClothGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersClothGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>105 Armor<br>+4 Stamina<br>+4 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersClothGirdle.itemHonorPrice[3] = 449
fDefilersClothGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersClothGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>113 Armor<br>+6 Stamina<br>+5 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersClothGirdle.itemHonorPrice[4] = 3300
fDefilersClothGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersClothGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>150 Armor<br>+7 Stamina<br>+6 Intellect<br>Durability 30 / 30<br>Classes: Priest, Mage, Warlock<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Intent (0/3)</span>\
<br> Defiler's Epaulets<br> Defiler's Cloth Boots<br> Defiler's Cloth Girdle<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersClothGirdle; i++;






var fDefilersLizardhideGirdle = new RewardItem("horde","Defiler's Lizardhide Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt01.gif&reason=external-or-uncollected-resource");
fDefilersLizardhideGirdle.itemHonorPrice = new Array();
fDefilersLizardhideGirdle.itemHonorPrice[1] = 206
fDefilersLizardhideGirdle.itemTokenPrice = new Array();
fDefilersLizardhideGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersLizardhideGirdle.itemStats = new Array();
fDefilersLizardhideGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>91 Armor<br>+4 Stamina<br>+12 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLizardhideGirdle.itemHonorPrice[2] = 304
fDefilersLizardhideGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersLizardhideGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>113 Armor<br>+4 Stamina<br>+15 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 38</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLizardhideGirdle.itemHonorPrice[3] = 449
fDefilersLizardhideGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersLizardhideGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>136 Armor<br>+6 Stamina<br>+10 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLizardhideGirdle.itemHonorPrice[4] = 3300
fDefilersLizardhideGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersLizardhideGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>159 Armor<br>+7 Stamina<br>+17 Intellect<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Will (0/3)</span>\
<br> Defiler's Lizardhide Boots<br> Defiler's Lizardhide Girdle<br> Defiler's Lizardhide Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLizardhideGirdle; ++i;






var fDefilersLeatherGirdle = new RewardItem("horde","Defiler's Leather Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt01.gif&reason=external-or-uncollected-resource");
fDefilersLeatherGirdle.itemHonorPrice = new Array();
fDefilersLeatherGirdle.itemHonorPrice[1] = 206
fDefilersLeatherGirdle.itemTokenPrice = new Array();
fDefilersLeatherGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersLeatherGirdle.itemStats = new Array();
fDefilersLeatherGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>91 Armor<br>+4 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLeatherGirdle.itemHonorPrice[2] = 304
fDefilersLeatherGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersLeatherGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>113 Armor<br>+4 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLeatherGirdle.itemHonorPrice[3] = 449
fDefilersLeatherGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersLeatherGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>136 Armor<br>+6 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLeatherGirdle.itemHonorPrice[4] = 3300
fDefilersLeatherGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersLeatherGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>159 Armor<br>+7 Stamina<br>Durability 35 / 35<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Purpose (0/3)</span>\
<br> Defiler's Leather Boots<br> Defiler's Leather Girdle<br> Defiler's Leather Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLeatherGirdle; ++i;








var fDefilersMailGirdle = new RewardItem("horde","Defiler's Mail Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt03.gif&reason=external-or-uncollected-resource");
fDefilersMailGirdle.itemHonorPrice = new Array();
fDefilersMailGirdle.itemHonorPrice[1] = 206
fDefilersMailGirdle.itemTokenPrice = new Array();
fDefilersMailGirdle.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersMailGirdle.itemStats = new Array();
fDefilersMailGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>61 Armor<br>+5 Stamina<br>+12 Intellect<br>Durability 35 / 35<br>Classes: Hunter, Shaman<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersMailGirdle.itemHonorPrice[2] = 304
fDefilersMailGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersMailGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>149 Armor<br>+6 Stamina<br>+15 Intellect<br>Durability 40 / 40<br>Classes: Hunter, Shaman<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersMailGirdle.itemHonorPrice[3] = 449
fDefilersMailGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersMailGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>178 Armor<br>+8 Stamina<br>+10 Intellect<br>Durability 40 / 40<br>Classes: Hunter, Shaman<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersMailGirdle.itemHonorPrice[4] = 3300
fDefilersMailGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersMailGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>208 Armor<br>+10 Stamina<br>+17 Intellect<br>Durability 40 / 40<br>Classes: Hunter, Shaman<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Fortitude (0/3)</span>\
<br> Defiler's Mail Girdle<br> Defiler's Mail Greaves<br> Defiler's Mail Pauldrons<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersMailGirdle; ++i;





var fDefilersPlateGirdle = new RewardItem("horde","Defiler's Plate Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt02.gif&reason=external-or-uncollected-resource");
fDefilersPlateGirdle.itemHonorPrice = new Array();
fDefilersPlateGirdle.itemHonorPrice[1] = 206
fDefilersPlateGirdle.itemStats = new Array(0,20,0,0);
fDefilersPlateGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>128 Armor<br>+12 Strength<br>+5 Stamina<br>Durability 40 / 40<br>Classes: Warrior, Paladin<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersPlateGirdle.itemHonorPrice[2] = 304
fDefilersPlateGirdle.itemTokenPrice = new Array();
fDefilersPlateGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersPlateGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>236 Armor<br>+15 Strength<br>+6 Stamina<br>Durability 45 / 45<br>Classes: Warrior, Paladin<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersPlateGirdle.itemHonorPrice[3] = 449
fDefilersPlateGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersPlateGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>313 Armor<br>+10 Strength<br>+8 Stamina<br>Durability 45 / 45<br>Classes: Warrior, Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersPlateGirdle.itemHonorPrice[4] = 3300
fDefilersPlateGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersPlateGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>369 Armor<br>+17 Strength<br>+10 Stamina<br>Durability 45 / 45<br>Classes: Warrior, Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Resolution (0/3)</span>\
<br> Defiler's Plate Girdle<br> Defiler's Plate Greaves<br> Defiler's Plate Spaulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersPlateGirdle; ++i;



var fDefilersLamellarGirdle = new RewardItem("horde","Defiler's Lamellar Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fbelt02.gif&reason=external-or-uncollected-resource");
fDefilersLamellarGirdle.itemHonorPrice = new Array();
fDefilersLamellarGirdle.itemHonorPrice[1] = 206
fDefilersLamellarGirdle.itemStats = new Array(0,20,0,0);
fDefilersLamellarGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>128 Armor<br>+11 Strength<br>+4 Stamina<br>+5 Intellect<br>Durability 40 / 40<br>Classes: Paladin<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLamellarGirdle.itemHonorPrice[2] = 304
fDefilersLamellarGirdle.itemTokenPrice = new Array();
fDefilersLamellarGirdle.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersLamellarGirdle.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>236 Armor<br>+12 Strength<br>+6 Stamina<br>+6 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLamellarGirdle.itemHonorPrice[3] = 449
fDefilersLamellarGirdle.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersLamellarGirdle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>313 Armor<br>+11 Strength<br>+4 Stamina<br>+8 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLamellarGirdle.itemHonorPrice[4] = 3300
fDefilersLamellarGirdle.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersLamellarGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>369 Armor<br>+15 Strength<br>+6 Stamina<br>+10 Intellect<br>Durability 45 / 45<br>Classes:Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLamellarGirdle; ++i;









var fDefilersChainGreaves = new RewardItem("horde","Defiler's Chain Greaves","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots02.gif&reason=external-or-uncollected-resource");
fDefilersChainGreaves.itemHonorPrice = new Array();
fDefilersChainGreaves.itemHonorPrice[1] = 206
fDefilersChainGreaves.itemTokenPrice = new Array();
fDefilersChainGreaves.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersChainGreaves.itemStats = new Array();
fDefilersChainGreaves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>74 Armor<br>+8 Agility<br>+8 Stamina<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersChainGreaves.itemHonorPrice[2] = 304
fDefilersChainGreaves.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersChainGreaves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>183 Armor<br>+7 Agility<br>+10 Stamina<br>+3 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersChainGreaves.itemHonorPrice[3] = 449
fDefilersChainGreaves.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersChainGreaves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>218 Armor<br>+8 Agility<br>+13 Stamina<br>+6 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersChainGreaves.itemHonorPrice[4] = 3300
fDefilersChainGreaves.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersChainGreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Chain Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>255 Armor<br>+10 Agility<br>+16 Stamina<br>+8 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Determination (0/3)</span>\
<br> Defiler's Chain Pauldrons<br> Defiler's Chain Greaves<br> Defiler's Chain Girdle<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersChainGreaves; i++;













var fDefilersClothBoots = new RewardItem("horde","Defiler's Cloth Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots05.gif&reason=external-or-uncollected-resource");
fDefilersClothBoots.itemHonorPrice = new Array();
fDefilersClothBoots.itemHonorPrice[1] = 206
fDefilersClothBoots.itemTokenPrice = new Array();
fDefilersClothBoots.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersClothBoots.itemStats = new Array();
fDefilersClothBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>84 Armor<br>+8 Stamina<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 7.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersClothBoots.itemHonorPrice[2] = 304
fDefilersClothBoots.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersClothBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+10 Stamina<br>+3 Intellect<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 8.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersClothBoots.itemHonorPrice[3] = 449
fDefilersClothBoots.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersClothBoots.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>132 Armor<br>+13 Stamina<br>+6 Intellect<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 6.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersClothBoots.itemHonorPrice[4] = 3300
fDefilersClothBoots.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersClothBoots.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Cloth Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Cloth</span>\
<br>161 Armor<br>+16 Stamina<br>+8 Intellect<br>Durability 40 / 40<br>Classes: Priest, Mage, Warlock<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Intent (0/3)</span>\
<br> Defiler's Epaulets<br> Defiler's Cloth Boots<br> Defiler's Cloth Girdle<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersClothBoots; ++i;





var fDefilersLizardhideBoots = new RewardItem("horde","Defiler's Lizardhide Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots04.gif&reason=external-or-uncollected-resource");
fDefilersLizardhideBoots.itemHonorPrice = new Array();
fDefilersLizardhideBoots.itemHonorPrice[1] = 206
fDefilersLizardhideBoots.itemTokenPrice = new Array();
fDefilersLizardhideBoots.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersLizardhideBoots.itemStats = new Array();
fDefilersLizardhideBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>104 Armor<br>+5 Agility<br>+8 Stamina<br>+4 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLizardhideBoots.itemHonorPrice[2] = 304
fDefilersLizardhideBoots.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersLizardhideBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>129 Armor<br>+6 Agility<br>+10 Stamina<br>+5 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 6.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLizardhideBoots.itemHonorPrice[3] = 449
fDefilersLizardhideBoots.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersLizardhideBoots.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>145 Armor<br>+8 Agility<br>+13 Stamina<br>+7 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLizardhideBoots.itemHonorPrice[4] = 3300
fDefilersLizardhideBoots.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersLizardhideBoots.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lizardhide Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>181 Armor<br>+8 Agility<br>+16 Stamina<br>+8 Intellect<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Will (0/3)</span>\
<br> Defiler's Lizardhide Boots<br> Defiler's Lizardhide Girdle<br> Defiler's Lizardhide Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLizardhideBoots; ++i;







var fDefilersLeatherBoots = new RewardItem("horde","Defiler's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots03.gif&reason=external-or-uncollected-resource");
fDefilersLeatherBoots.itemHonorPrice = new Array();
fDefilersLeatherBoots.itemHonorPrice[1] = 206
fDefilersLeatherBoots.itemTokenPrice = new Array();
fDefilersLeatherBoots.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersLeatherBoots.itemStats = new Array();
fDefilersLeatherBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>104 Armor<br>+7 Agility<br>+8 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLeatherBoots.itemHonorPrice[2] = 304
fDefilersLeatherBoots.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersLeatherBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>129 Armor<br>+8 Agility<br>+10 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 6.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLeatherBoots.itemHonorPrice[3] = 449
fDefilersLeatherBoots.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersLeatherBoots.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>145 Armor<br>+11 Agility<br>+13 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLeatherBoots.itemHonorPrice[4] = 3300
fDefilersLeatherBoots.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersLeatherBoots.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Leather Boots</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>181 Armor<br>+12 Agility<br>+16 Stamina<br>Durability 50 / 50<br>Classes: Rogue, Druid<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Purpose (0/3)</span>\
<br> Defiler's Leather Boots<br> Defiler's Leather Girdle<br> Defiler's Leather Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLeatherBoots; ++i;




var fDefilersMailGreaves = new RewardItem("horde","Defiler's Mail Greaves","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots02.gif&reason=external-or-uncollected-resource");
fDefilersMailGreaves.itemHonorPrice = new Array();
fDefilersMailGreaves.itemHonorPrice[1] = 206
fDefilersMailGreaves.itemTokenPrice = new Array();
fDefilersMailGreaves.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersMailGreaves.itemStats = new Array();
fDefilersMailGreaves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Leather</span>\
<br>74 Armor<br>+8 Agility<br>+8 Stamina<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersMailGreaves.itemHonorPrice[2] = 304
fDefilersMailGreaves.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersMailGreaves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>183 Armor<br>+7 Agility<br>+10 Stamina<br>+3 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersMailGreaves.itemHonorPrice[3] = 449
fDefilersMailGreaves.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersMailGreaves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>218 Armor<br>+8 Agility<br>+13 Stamina<br>+6 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersMailGreaves.itemHonorPrice[4] = 3300
fDefilersMailGreaves.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersMailGreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Mail Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>255 Armor<br>+10 Agility<br>+16 Stamina<br>+8 Intellect<br>Durability 60 / 60<br>Classes: Hunter, Shaman<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Fortitude (0/3)</span>\
<br> Defiler's Mail Girdle<br> Defiler's Mail Greaves<br> Defiler's Mail Pauldrons<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersMailGreaves; ++i;






var fDefilersPlateGreaves = new RewardItem("horde","Defiler's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots01.gif&reason=external-or-uncollected-resource");
fDefilersPlateGreaves.itemHonorPrice = new Array();
fDefilersPlateGreaves.itemHonorPrice[1] = 206
fDefilersPlateGreaves.itemTokenPrice = new Array();
fDefilersPlateGreaves.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersPlateGreaves.itemStats = new Array();
fDefilersPlateGreaves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>157 Armor<br>+6 Strength<br>+6 Agility<br>+6 Stamina<br>Durability 60 / 60<br>Classes: Warrior, Paladin<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersPlateGreaves.itemHonorPrice[2] = 304
fDefilersPlateGreaves.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersPlateGreaves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>289 Armor<br>+8 Strength<br>+8 Agility<br>+8 Stamina<br>Durability 65 / 65<br>Classes: Warrior, Paladin<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersPlateGreaves.itemHonorPrice[3] = 449
fDefilersPlateGreaves.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersPlateGreaves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>383 Armor<br>+11 Strength<br>+10 Agility<br>+10 Stamina<br>Durability 65 / 65<br>Classes: Warrior, Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersPlateGreaves.itemHonorPrice[4] = 3300
fDefilersPlateGreaves.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersPlateGreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Plate Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>452 Armor<br>+14 Strength<br>+12 Agility<br>+12 Stamina<br>Durability 65 / 65<br>Classes: Warrior, Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Resolution (0/3)</span>\
<br> Defiler's Plate Girdle<br> Defiler's Plate Greaves<br> Defiler's Plate Spaulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersPlateGreaves; ++i;




var fDefilersLamellarGreaves = new RewardItem("horde","Defiler's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fboots01.gif&reason=external-or-uncollected-resource");
fDefilersLamellarGreaves.itemHonorPrice = new Array();
fDefilersLamellarGreaves.itemHonorPrice[1] = 206
fDefilersLamellarGreaves.itemTokenPrice = new Array();
fDefilersLamellarGreaves.itemTokenPrice[1] = new Array(0,20,0,0);
fDefilersLamellarGreaves.itemStats = new Array();
fDefilersLamellarGreaves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Mail</span>\
<br>157 Armor<br>+6 Strength<br>+6 Agility<br>+4 Stamina<br>+4 Intellect<br>Durability 60/60<br>Classes: Paladin<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLamellarGreaves.itemHonorPrice[2] = 304
fDefilersLamellarGreaves.itemTokenPrice[2] = new Array(0,20,0,0);
fDefilersLamellarGreaves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>289 Armor<br>+8 Strength<br>+8 Agility<br>+6 Stamina<br>+5 Intellect<br>Durability 65/65<br>Classes: Paladin<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLamellarGreaves.itemHonorPrice[3] = 449
fDefilersLamellarGreaves.itemTokenPrice[3] = new Array(0,20,0,0);
fDefilersLamellarGreaves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>383 Armor<br>+11 Strength<br>+10 Agility<br>+7 Stamina<br>+6 Intellect<br>Durability 65 / 65<br>Classes: Paladin<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDefilersLamellarGreaves.itemHonorPrice[4] = 3300
fDefilersLamellarGreaves.itemTokenPrice[4] = new Array(0,20,0,0);
fDefilersLamellarGreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Defiler's Lamellar Greaves</span>\
<br>Binds when picked up<br>Unique<br>Feet<span class=\"myRight\">Plate</span>\
<br>452 Armor<br>+14 Strength<br>+12 Agility<br>+8 Stamina<br>+8 Intellect<br>Durability 65 / 65<br>Classes: Paladin<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLamellarGreaves; ++i;













var fDefilersChainPauldrons = new RewardItem("horde","Defiler's Chain Pauldrons","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders02.gif&reason=external-or-uncollected-resource");
fDefilersChainPauldrons.itemHonorPrice = new Array();
fDefilersChainPauldrons.itemHonorPrice[5] = 9900
fDefilersChainPauldrons.itemTokenPrice = new Array();
fDefilersChainPauldrons.itemTokenPrice[5] = new Array(0,40,0,0);
fDefilersChainPauldrons.itemStats = new Array();
fDefilersChainPauldrons.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Defiler's Chain Pauldrons</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>356 Armor<br>+14 Agility<br>+18 Stamina<br>+17 Intellect<br>Durability 85 / 85<br>Classes: Hunter, Shaman<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Determination (0/3)</span>\
<br> Defiler's Chain Pauldrons<br> Defiler's Chain Greaves<br> Defiler's Chain Girdle<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersChainPauldrons; ++i;







var fDefilersEpaulets = new RewardItem("horde","Defiler's Epaulets","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders01.gif&reason=external-or-uncollected-resource");
fDefilersEpaulets.itemHonorPrice = new Array();
fDefilersEpaulets.itemHonorPrice[5] = 9900
fDefilersEpaulets.itemTokenPrice = new Array();
fDefilersEpaulets.itemTokenPrice[5] = new Array(0,40,0,0);
fDefilersEpaulets.itemStats = new Array();
fDefilersEpaulets.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Defiler's Epaulets</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>196 Armor<br>+18 Stamina<br>+17 Intellect<br>Durability 60 / 60<br>Classes: Priest, Mage, Warlock<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Intent (0/3)</span>\
<br> Defiler's Epaulets<br> Defiler's Cloth Boots<br> Defiler's Cloth Girdle<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersEpaulets; ++i;





var fDefilersLizardhideShoulders = new RewardItem("horde","Defiler's Lizardhide Shoulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders01.gif&reason=external-or-uncollected-resource");
fDefilersLizardhideShoulders.itemHonorPrice = new Array();
fDefilersLizardhideShoulders.itemHonorPrice[5] = 9900
fDefilersLizardhideShoulders.itemTokenPrice = new Array();
fDefilersLizardhideShoulders.itemTokenPrice[5] = new Array(0,40,0,0);
fDefilersLizardhideShoulders.itemStats = new Array();
fDefilersLizardhideShoulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Defiler's Lizardhide Shoulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>279 Armor<br>+12 Agility<br>+17 Stamina<br>+12 Intellect<br>Durability 70 / 70<br>Classes: Rogue, Druid<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Will (0/3)</span>\
<br> Defiler's Lizardhide Boots<br> Defiler's Lizardhide Girdle<br> Defiler's Lizardhide Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your spell critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLizardhideShoulders; ++i;





var fDefilersLeatherShoulders = new RewardItem("horde","Defiler's Leather Shoulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders01.gif&reason=external-or-uncollected-resource");
fDefilersLeatherShoulders.itemHonorPrice = new Array();
fDefilersLeatherShoulders.itemHonorPrice[5] = 9900
fDefilersLeatherShoulders.itemTokenPrice = new Array();
fDefilersLeatherShoulders.itemTokenPrice[5] = new Array(0,40,0,0);
fDefilersLeatherShoulders.itemStats = new Array();
fDefilersLeatherShoulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Defiler's Leather Shoulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>279 Armor<br>+18 Agility<br>+17 Stamina<br>Durability 70 / 70<br>Classes: Rogue, Druid<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Purpose (0/3)</span>\
<br> Defiler's Leather Boots<br> Defiler's Leather Girdle<br> Defiler's Leather Shoulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLeatherShoulders; ++i;






var fDefilersMailPauldrons = new RewardItem("horde","Defiler's Mail Pauldrons","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders02.gif&reason=external-or-uncollected-resource");
fDefilersMailPauldrons.itemHonorPrice = new Array();
fDefilersMailPauldrons.itemHonorPrice[5] = 9900
fDefilersMailPauldrons.itemTokenPrice = new Array();
fDefilersMailPauldrons.itemTokenPrice[5] = new Array(0,40,0,0);
fDefilersMailPauldrons.itemStats = new Array();
fDefilersMailPauldrons.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Defiler's Mail Pauldrons</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>356 Armor<br>+11 Strength<br>+10 Agility<br>+18 Stamina<br>+17 Intellect<br>Durability 85 / 85<br>Classes: Hunter, Shaman<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">The Defiler's Fortitude (0/3)</span>\
<br> Defiler's Mail Girdle<br> Defiler's Mail Greaves<br> Defiler's Mail Pauldrons<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersMailPauldrons; ++i;








var fDefilersPlateSpaulders = new RewardItem("horde","Defiler's Plate Spaulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders02.gif&reason=external-or-uncollected-resource");
fDefilersPlateSpaulders.itemHonorPrice = new Array();
fDefilersPlateSpaulders.itemHonorPrice[5] = 6188
fDefilersPlateSpaulders.itemTokenPrice = new Array();
fDefilersPlateSpaulders.itemTokenPrice[5] = new Array(0,40,0,0);
fDefilersPlateSpaulders.itemStats = new Array();
fDefilersPlateSpaulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Defiler's Plate Spaulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>632 Armor<br>+18 Strength<br>+17 Agility<br>+20 Stamina<br>Durability 100 / 100<br>Classes: Warrior<br>Requires Level 60<br>\
<br>\
<span class=\"myYellow\">The Defiler's Resolution (0/3)</span>\
<br> Defiler's Plate Girdle<br> Defiler's Plate Greaves<br> Defiler's Plate Spaulders<br>\
<br>(2) Set: +5 Stamina.<br>(3) Set: Increases your critical strike rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersPlateSpaulders; ++i;

var fDefilersLamellarSpaulders = new RewardItem("horde","Defiler's Lamellar Spaulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fshoulders02.gif&reason=external-or-uncollected-resource");
fDefilersLamellarSpaulders.itemHonorPrice = new Array();
fDefilersLamellarSpaulders.itemHonorPrice[5] = 9900
fDefilersLamellarSpaulders.itemTokenPrice = new Array();
fDefilersLamellarSpaulders.itemTokenPrice[5] = new Array(0,40,0,0);
fDefilersLamellarSpaulders.itemStats = new Array();
fDefilersLamellarSpaulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Defiler's Lamellar Spaulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>632 Armor<br>+18 Strength<br>+17 Agility<br>+15 Stamina<br>+10 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 60<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDefilersLamellarSpaulders; ++i;










var fCloakOfTheHonorGuard = new RewardItem("horde","Deathguard's Cloak","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fcape01.gif&reason=external-or-uncollected-resource");
fCloakOfTheHonorGuard.itemHonorPrice = new Array();
fCloakOfTheHonorGuard.itemHonorPrice[5] = 5400
fCloakOfTheHonorGuard.itemTokenPrice = new Array();
fCloakOfTheHonorGuard.itemTokenPrice[5] = new Array(0,20,0,0);
fCloakOfTheHonorGuard.itemStats = new Array();
fCloakOfTheHonorGuard.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Deathguard's Cloak</span>\
<br>Binds when picked up<br>Back<br>57 Armor<br>+5 Agility<br>+11 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCloakOfTheHonorGuard; ++i;


var fIronbarkStaff = new RewardItem("horde","Ironbark Staff","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Farathi%2Frewards-arathi.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Farathi%2Fstaff01.gif&reason=external-or-uncollected-resource");
fIronbarkStaff.itemHonorPrice = new Array();
fIronbarkStaff.itemHonorPrice[5] = 18000
fIronbarkStaff.itemTokenPrice = new Array();
fIronbarkStaff.itemTokenPrice[5] = new Array(0,40,0,0);
fIronbarkStaff.itemStats = new Array();
fIronbarkStaff.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Ironbark Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>136 - 243 Damage<span class=\"myRight\">Speed 3.40</span>\
<br>(55.8 damage per second)<br>100 Armor<br>+19 Stamina<br>+10 Intellect<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 41.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIronbarkStaff; ++i;



var fMindfang = new RewardItem("horde","Mindfang","/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/arathi/dagger01.gif");
fMindfang.itemHonorPrice = new Array();
fMindfang.itemHonorPrice[5] = 9600
fMindfang.itemTokenPrice = new Array();
fMindfang.itemTokenPrice[5] = new Array(0,40,0,0);
fMindfang.itemStats = new Array();
fMindfang.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Mindfang</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Dagger</span>\
<br>46 - 96 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(41.7 damage per second)<br>40 Armor<br>+8 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMindfang; ++i;

//------END REWARDS DEFINITION------
