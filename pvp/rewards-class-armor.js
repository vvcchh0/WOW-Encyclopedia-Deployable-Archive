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

//DRUID----------------------------------------------------
var fGrandMarshalsDragonhideGloves = new RewardItem("alliance","Grand Marshal's Dragonhide Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsDragonhideGloves.itemHonorPrice = new Array();
fGrandMarshalsDragonhideGloves.itemHonorPrice[0] = 10098
fGrandMarshalsDragonhideGloves.itemTokenPrice = new Array();
fGrandMarshalsDragonhideGloves.itemTokenPrice[0] = new Array(20,0,0,0);
fGrandMarshalsDragonhideGloves.itemStats = new Array();
fGrandMarshalsDragonhideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dragonhide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+17 Strength<br>+17 Agility<br>+24 Stamina<br>+11 Intellect<br>Durability 35 / 35<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 35.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Sanctuary (0/5)</span>\
<br> Grand Marshal's Dragonhide Gloves<br> Grand Marshal's Dragonhide Helm<br> Grand Marshal's Dragonhide Legguards<br> Grand Marshal's Dragonhide Spaulders<br> Grand Marshal's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideGloves; ++i;

var fGrandMarshalsDragonhideSpaulders = new RewardItem("alliance","Grand Marshal's Dragonhide Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsDragonhideSpaulders.itemHonorPrice = new Array();
fGrandMarshalsDragonhideSpaulders.itemHonorPrice[0] = 10098
fGrandMarshalsDragonhideSpaulders.itemTokenPrice = new Array();
fGrandMarshalsDragonhideSpaulders.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsDragonhideSpaulders.itemStats = new Array();
fGrandMarshalsDragonhideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dragonhide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+17 Strength<br>+17 Agility<br>+24 Stamina<br>+13 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 18.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Sanctuary (0/5)</span>\
<br> Grand Marshal's Dragonhide Gloves<br> Grand Marshal's Dragonhide Helm<br> Grand Marshal's Dragonhide Legguards<br> Grand Marshal's Dragonhide Spaulders<br> Grand Marshal's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideSpaulders; ++i;

var fGrandMarshalsDragonhideLegguards = new RewardItem("alliance","Grand Marshal's Dragonhide Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsDragonhideLegguards.itemHonorPrice = new Array();
fGrandMarshalsDragonhideLegguards.itemHonorPrice[0] = 16065
fGrandMarshalsDragonhideLegguards.itemTokenPrice = new Array();
fGrandMarshalsDragonhideLegguards.itemTokenPrice[0] = new Array(0,0,0,30);
fGrandMarshalsDragonhideLegguards.itemStats = new Array();
fGrandMarshalsDragonhideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dragonhide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>306 Armor<br>+23 Strength<br>+22 Agility<br>+30 Stamina<br>+22 Intellect<br>Durability 75 / 75<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 48.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Sanctuary (0/5)</span>\
<br> Grand Marshal's Dragonhide Gloves<br> Grand Marshal's Dragonhide Helm<br> Grand Marshal's Dragonhide Legguards<br> Grand Marshal's Dragonhide Spaulders<br> Grand Marshal's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideLegguards; ++i;

var fGrandMarshalsDragonhideHelm = new RewardItem("alliance","Grand Marshal's Dragonhide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsDragonhideHelm.itemHonorPrice = new Array();
fGrandMarshalsDragonhideHelm.itemHonorPrice[0] = 16065
fGrandMarshalsDragonhideHelm.itemTokenPrice = new Array();
fGrandMarshalsDragonhideHelm.itemTokenPrice[0] = new Array(30,0,0,0);
fGrandMarshalsDragonhideHelm.itemStats = new Array();
fGrandMarshalsDragonhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dragonhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+22 Strength<br>+22 Agility<br>+21 Stamina<br>+14 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Sanctuary (0/5)</span>\
<br> Grand Marshal's Dragonhide Gloves<br> Grand Marshal's Dragonhide Helm<br> Grand Marshal's Dragonhide Legguards<br> Grand Marshal's Dragonhide Spaulders<br> Grand Marshal's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideHelm; ++i;

var fGrandMarshalsDragonhideTunic = new RewardItem("alliance","Grand Marshal's Dragonhide Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsDragonhideTunic.itemHonorPrice = new Array();
fGrandMarshalsDragonhideTunic.itemHonorPrice[0] = 16524
fGrandMarshalsDragonhideTunic.itemTokenPrice = new Array();
fGrandMarshalsDragonhideTunic.itemTokenPrice[0] = new Array(0,30,0,0);
fGrandMarshalsDragonhideTunic.itemStats = new Array();
fGrandMarshalsDragonhideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dragonhide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>322 Armor<br>+18 Strength<br>+18 Agility<br>+31 Stamina<br>+18 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 100 / 100<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Sanctuary (0/5)</span>\
<br> Grand Marshal's Dragonhide Gloves<br> Grand Marshal's Dragonhide Helm<br> Grand Marshal's Dragonhide Legguards<br> Grand Marshal's Dragonhide Spaulders<br> Grand Marshal's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideTunic; ++i;

//DRUID SET 2 ---------------------------
var fGrandMarshalsWyrmhideGloves = new RewardItem("alliance","Grand Marshal's Wyrmhide Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsWyrmhideGloves.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideGloves.itemHonorPrice[0] = 10098
fGrandMarshalsWyrmhideGloves.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideGloves.itemTokenPrice[0] = new Array(20,0,0,0);
fGrandMarshalsWyrmhideGloves.itemStats = new Array();
fGrandMarshalsWyrmhideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Wyrmhide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+22 Stamina<br>+15 Intellect<br>Durability 35 / 35<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wildhide (0/5)</span>\
<br> Grand Marshal's Wyrmhide Gloves<br> Grand Marshal's Wyrmhide Helm<br> Grand Marshal's Wyrmhide Legguards<br> Grand Marshal's Wyrmhide Spaulders<br> Grand Marshal's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideGloves; ++i;

var fGrandMarshalsWyrmhideSpaulders = new RewardItem("alliance","Grand Marshal's Wyrmhide Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsWyrmhideSpaulders.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideSpaulders.itemHonorPrice[0] = 10098
fGrandMarshalsWyrmhideSpaulders.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideSpaulders.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsWyrmhideSpaulders.itemStats = new Array();
fGrandMarshalsWyrmhideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Wyrmhide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+33 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wildhide (0/5)</span>\
<br> Grand Marshal's Wyrmhide Gloves<br> Grand Marshal's Wyrmhide Helm<br> Grand Marshal's Wyrmhide Legguards<br> Grand Marshal's Wyrmhide Spaulders<br> Grand Marshal's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideSpaulders; ++i;


var fGrandMarshalsWyrmhideLegguards = new RewardItem("alliance","Grand Marshal's Wyrmhide Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsWyrmhideLegguards.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideLegguards.itemHonorPrice[0] = 16065
fGrandMarshalsWyrmhideLegguards.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideLegguards.itemTokenPrice[0] = new Array(0,0,0,30);
fGrandMarshalsWyrmhideLegguards.itemStats = new Array();
fGrandMarshalsWyrmhideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Wyrmhide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>306 Armor<br>+33 Stamina<br>+22 Intellect<br>Durability 75 / 75<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wildhide (0/5)</span>\
<br> Grand Marshal's Wyrmhide Gloves<br> Grand Marshal's Wyrmhide Helm<br> Grand Marshal's Wyrmhide Legguards<br> Grand Marshal's Wyrmhide Spaulders<br> Grand Marshal's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideLegguards; ++i;

var fGrandMarshalsWyrmhideHelm = new RewardItem("alliance","Grand Marshal's Wyrmhide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsWyrmhideHelm.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideHelm.itemHonorPrice[0] = 16065
fGrandMarshalsWyrmhideHelm.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideHelm.itemTokenPrice[0] = new Array(30,0,0,0);
fGrandMarshalsWyrmhideHelm.itemStats = new Array();
fGrandMarshalsWyrmhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Wyrmhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+21 Stamina<br>+18 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wildhide (0/5)</span>\
<br> Grand Marshal's Wyrmhide Gloves<br> Grand Marshal's Wyrmhide Helm<br> Grand Marshal's Wyrmhide Legguards<br> Grand Marshal's Wyrmhide Spaulders<br> Grand Marshal's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideHelm; ++i;

var fGrandMarshalsWyrmhideTunic = new RewardItem("alliance","Grand Marshal's Wyrmhide Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsWyrmhideTunic.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideTunic.itemHonorPrice[0] = 16524
fGrandMarshalsWyrmhideTunic.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideTunic.itemTokenPrice[0] = new Array(0,30,0,0);
fGrandMarshalsWyrmhideTunic.itemStats = new Array();
fGrandMarshalsWyrmhideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Wyrmhide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>322 Armor<br>+33 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 100 / 100<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wildhide (0/5)</span>\
<br> Grand Marshal's Wyrmhide Gloves<br> Grand Marshal's Wyrmhide Helm<br> Grand Marshal's Wyrmhide Legguards<br> Grand Marshal's Wyrmhide Spaulders<br> Grand Marshal's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideTunic; ++i;

//DRUID SET 3-------------------------------------------
var fGrandMarshalsKodohideGloves = new RewardItem("alliance","Grand Marshal's Kodohide Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsKodohideGloves.itemHonorPrice = new Array();
fGrandMarshalsKodohideGloves.itemHonorPrice[0] = 10098
fGrandMarshalsKodohideGloves.itemTokenPrice = new Array();
fGrandMarshalsKodohideGloves.itemTokenPrice[0] = new Array(20,0,0,0);
fGrandMarshalsKodohideGloves.itemStats = new Array();
fGrandMarshalsKodohideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Kodohide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+22 Stamina<br>+22 Intellect<br>Durability 35 / 35<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 51.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Refuge (0/5)</span>\
<br> Grand Marshal's Kodohide Gloves<br> Grand Marshal's Kodohide Helm<br> Grand Marshal's Kodohide Legguards<br> Grand Marshal's Kodohide Spaulders<br> Grand Marshal's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideGloves; ++i;

var fGrandMarshalsKodohideSpaulders = new RewardItem("alliance","Grand Marshal's Kodohide Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsKodohideSpaulders.itemHonorPrice = new Array();
fGrandMarshalsKodohideSpaulders.itemHonorPrice[0] = 10098
fGrandMarshalsKodohideSpaulders.itemTokenPrice = new Array();
fGrandMarshalsKodohideSpaulders.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsKodohideSpaulders.itemStats = new Array();
fGrandMarshalsKodohideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Kodohide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+33 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Refuge (0/5)</span>\
<br> Grand Marshal's Kodohide Gloves<br> Grand Marshal's Kodohide Helm<br> Grand Marshal's Kodohide Legguards<br> Grand Marshal's Kodohide Spaulders<br> Grand Marshal's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideSpaulders; ++i;

var fGrandMarshalsKodohideLegguards = new RewardItem("alliance","Grand Marshal's Kodohide Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsKodohideLegguards.itemHonorPrice = new Array();
fGrandMarshalsKodohideLegguards.itemHonorPrice[0] = 16065
fGrandMarshalsKodohideLegguards.itemTokenPrice = new Array();
fGrandMarshalsKodohideLegguards.itemTokenPrice[0] = new Array(0,0,0,30);
fGrandMarshalsKodohideLegguards.itemStats = new Array();
fGrandMarshalsKodohideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Kodohide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>306 Armor<br>+33 Stamina<br>+28 Intellect<br>Durability 75 / 75<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 64.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Refuge (0/5)</span>\
<br> Grand Marshal's Kodohide Gloves<br> Grand Marshal's Kodohide Helm<br> Grand Marshal's Kodohide Legguards<br> Grand Marshal's Kodohide Spaulders<br> Grand Marshal's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideLegguards; ++i;

var fGrandMarshalsKodohideHelm = new RewardItem("alliance","Grand Marshal's Kodohide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsKodohideHelm.itemHonorPrice = new Array();
fGrandMarshalsKodohideHelm.itemHonorPrice[0] = 16065
fGrandMarshalsKodohideHelm.itemTokenPrice = new Array();
fGrandMarshalsKodohideHelm.itemTokenPrice[0] = new Array(30,0,0,0);
fGrandMarshalsKodohideHelm.itemStats = new Array();
fGrandMarshalsKodohideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Kodohide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+30 Stamina<br>+18 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Refuge (0/5)</span>\
<br> Grand Marshal's Kodohide Gloves<br> Grand Marshal's Kodohide Helm<br> Grand Marshal's Kodohide Legguards<br> Grand Marshal's Kodohide Spaulders<br> Grand Marshal's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideHelm; ++i;

var fGrandMarshalsKodohideTunic = new RewardItem("alliance","Grand Marshal's Kodohide Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsKodohideTunic.itemHonorPrice = new Array();
fGrandMarshalsKodohideTunic.itemHonorPrice[0] = 16524
fGrandMarshalsKodohideTunic.itemTokenPrice = new Array();
fGrandMarshalsKodohideTunic.itemTokenPrice[0] = new Array(0,30,0,0);
fGrandMarshalsKodohideTunic.itemStats = new Array();
fGrandMarshalsKodohideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Kodohide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>322 Armor<br>+33 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 100 / 100<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Refuge (0/5)</span>\
<br> Grand Marshal's Kodohide Gloves<br> Grand Marshal's Kodohide Helm<br> Grand Marshal's Kodohide Legguards<br> Grand Marshal's Kodohide Spaulders<br> Grand Marshal's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideTunic; ++i;

//HUNTER-----------------------------------------------------------------------------

var fGrandMarshalsChainGauntlets = new RewardItem("alliance","Grand Marshal's Chain Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsChainGauntlets.itemHonorPrice = new Array();
fGrandMarshalsChainGauntlets.itemHonorPrice[1] = 10098
fGrandMarshalsChainGauntlets.itemTokenPrice = new Array();
fGrandMarshalsChainGauntlets.itemTokenPrice[1] = new Array(20,0,0,0);
fGrandMarshalsChainGauntlets.itemStats = new Array();
fGrandMarshalsChainGauntlets.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Chain Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+21 Agility<br>+31 Stamina<br>+6 Intellect<br>Durability 40 / 40<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the damage done by your Multi-Shot by 4%.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Pursuit (0/5)</span>\
<br> Grand Marshal's Chain Armor<br> Grand Marshal's Chain Gauntlets<br> Grand Marshal's Chain Helm<br> Grand Marshal's Chain Leggings<br> Grand Marshal's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainGauntlets; ++i;

var fGrandMarshalsChainSpaulders = new RewardItem("alliance","Grand Marshal's Chain Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsChainSpaulders.itemHonorPrice = new Array();
fGrandMarshalsChainSpaulders.itemHonorPrice[1] = 10098
fGrandMarshalsChainSpaulders.itemTokenPrice = new Array();
fGrandMarshalsChainSpaulders.itemTokenPrice[1] = new Array(0,20,0,0);
fGrandMarshalsChainSpaulders.itemStats = new Array();
fGrandMarshalsChainSpaulders.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Chain Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+14 Agility<br>+31 Stamina<br>+4 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Pursuit (0/5)</span>\
<br> Grand Marshal's Chain Armor<br> Grand Marshal's Chain Gauntlets<br> Grand Marshal's Chain Helm<br> Grand Marshal's Chain Leggings<br> Grand Marshal's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainSpaulders; ++i;

var fGrandMarshalsChainLeggings = new RewardItem("alliance","Grand Marshal's Chain Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsChainLeggings.itemHonorPrice = new Array();
fGrandMarshalsChainLeggings.itemHonorPrice[1] = 16065
fGrandMarshalsChainLeggings.itemTokenPrice = new Array();
fGrandMarshalsChainLeggings.itemTokenPrice[1] = new Array(0,0,0,30);
fGrandMarshalsChainLeggings.itemStats = new Array();
fGrandMarshalsChainLeggings.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Chain Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+28 Agility<br>+42 Stamina<br>+8 Intellect<br>Durability 90 / 90<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Pursuit (0/5)</span>\
<br> Grand Marshal's Chain Armor<br> Grand Marshal's Chain Gauntlets<br> Grand Marshal's Chain Helm<br> Grand Marshal's Chain Leggings<br> Grand Marshal's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainLeggings; ++i;

var fGrandMarshalsChainHelm = new RewardItem("alliance","Grand Marshal's Chain Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsChainHelm.itemHonorPrice = new Array();
fGrandMarshalsChainHelm.itemHonorPrice[1] = 16065
fGrandMarshalsChainHelm.itemTokenPrice = new Array();
fGrandMarshalsChainHelm.itemTokenPrice[1] = new Array(30,0,0,0);
fGrandMarshalsChainHelm.itemStats = new Array();
fGrandMarshalsChainHelm.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Chain Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+20 Agility<br>+30 Stamina<br>+14 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Pursuit (0/5)</span>\
<br> Grand Marshal's Chain Armor<br> Grand Marshal's Chain Gauntlets<br> Grand Marshal's Chain Helm<br> Grand Marshal's Chain Leggings<br> Grand Marshal's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainHelm; ++i;

var fGrandMarshalsChainArmor = new RewardItem("alliance","Grand Marshal's Chain Armor","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_11.gif");
fGrandMarshalsChainArmor.itemHonorPrice = new Array();
fGrandMarshalsChainArmor.itemHonorPrice[1] = 16524
fGrandMarshalsChainArmor.itemTokenPrice = new Array();
fGrandMarshalsChainArmor.itemTokenPrice[1] = new Array(0,30,0,0);
fGrandMarshalsChainArmor.itemStats = new Array();
fGrandMarshalsChainArmor.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Chain Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+20 Agility<br>+42 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Pursuit (0/5)</span>\
<br> Grand Marshal's Chain Armor<br> Grand Marshal's Chain Gauntlets<br> Grand Marshal's Chain Helm<br> Grand Marshal's Chain Leggings<br> Grand Marshal's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainArmor; ++i;

//MAGE---------------------------------------------------------------------
var fGrandMarshalsSilkHandguards = new RewardItem("alliance","Grand Marshal's Silk Handguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_19.gif");
fGrandMarshalsSilkHandguards.itemHonorPrice = new Array();
fGrandMarshalsSilkHandguards.itemHonorPrice[2] = 10098
fGrandMarshalsSilkHandguards.itemTokenPrice = new Array();
fGrandMarshalsSilkHandguards.itemTokenPrice[2] = new Array(20,0,0,0);
fGrandMarshalsSilkHandguards.itemStats = new Array();
fGrandMarshalsSilkHandguards.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Silk Handguards</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+33 Stamina<br>+12 Intellect<br>Durability 30 / 30<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of your Fire Blast spell by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Regalia (0/5)</span>\
<br> Grand Marshal's Silk Amice<br> Grand Marshal's Silk Cowl<br> Grand Marshal's Silk Handguards<br> Grand Marshal's Silk Raiment<br> Grand Marshal's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkHandguards; ++i;

var fGrandMarshalsSilkAmice = new RewardItem("alliance","Grand Marshal's Silk Amice","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_19.gif");
fGrandMarshalsSilkAmice.itemHonorPrice = new Array();
fGrandMarshalsSilkAmice.itemHonorPrice[2] = 10098
fGrandMarshalsSilkAmice.itemTokenPrice = new Array();
fGrandMarshalsSilkAmice.itemTokenPrice[2] = new Array(0,20,0,0);
fGrandMarshalsSilkAmice.itemStats = new Array();
fGrandMarshalsSilkAmice.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Silk Amice</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+21 Stamina<br>+16 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Regalia (0/5)</span>\
<br> Grand Marshal's Silk Amice<br> Grand Marshal's Silk Cowl<br> Grand Marshal's Silk Handguards<br> Grand Marshal's Silk Raiment<br> Grand Marshal's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkAmice; ++i;

var fGrandMarshalsSilkTrousers = new RewardItem("alliance","Grand Marshal's Silk Trousers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_07.gif");
fGrandMarshalsSilkTrousers.itemHonorPrice = new Array();
fGrandMarshalsSilkTrousers.itemHonorPrice[2] = 16065
fGrandMarshalsSilkTrousers.itemTokenPrice = new Array();
fGrandMarshalsSilkTrousers.itemTokenPrice[2] = new Array(0,0,0,30);
fGrandMarshalsSilkTrousers.itemStats = new Array();
fGrandMarshalsSilkTrousers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Silk Trousers</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+42 Stamina<br>+22 Intellect<br>Durability 65 / 65<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Regalia (0/5)</span>\
<br> Grand Marshal's Silk Amice<br> Grand Marshal's Silk Cowl<br> Grand Marshal's Silk Handguards<br> Grand Marshal's Silk Raiment<br> Grand Marshal's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkTrousers; ++i;

var fGrandMarshalsSilkCowl = new RewardItem("alliance","Grand Marshal's Silk Cowl","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_08.gif");
fGrandMarshalsSilkCowl.itemHonorPrice = new Array();
fGrandMarshalsSilkCowl.itemHonorPrice[2] = 16065
fGrandMarshalsSilkCowl.itemTokenPrice = new Array();
fGrandMarshalsSilkCowl.itemTokenPrice[2] = new Array(30,0,0,0);
fGrandMarshalsSilkCowl.itemStats = new Array();
fGrandMarshalsSilkCowl.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Silk Cowl</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+39 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Regalia (0/5)</span>\
<br> Grand Marshal's Silk Amice<br> Grand Marshal's Silk Cowl<br> Grand Marshal's Silk Handguards<br> Grand Marshal's Silk Raiment<br> Grand Marshal's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkCowl; ++i;

var fGrandMarshalsSilkRaiment = new RewardItem("alliance","Grand Marshal's Silk Raiment","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Leather_01.gif&reason=external-or-uncollected-resource");
fGrandMarshalsSilkRaiment.itemHonorPrice = new Array();
fGrandMarshalsSilkRaiment.itemHonorPrice[2] = 16524
fGrandMarshalsSilkRaiment.itemTokenPrice = new Array();
fGrandMarshalsSilkRaiment.itemTokenPrice[2] = new Array(0,30,0,0);
fGrandMarshalsSilkRaiment.itemStats = new Array();
fGrandMarshalsSilkRaiment.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Silk Raiment</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+42 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 80 / 80<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Regalia (0/5)</span>\
<br> Grand Marshal's Silk Amice<br> Grand Marshal's Silk Cowl<br> Grand Marshal's Silk Handguards<br> Grand Marshal's Silk Raiment<br> Grand Marshal's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkRaiment; ++i;


//PALADIN-----------------------------------------------------
var fGrandMarshalsLamellarGauntlets = new RewardItem("alliance","Grand Marshal's Lamellar Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsLamellarGauntlets.itemHonorPrice = new Array();
fGrandMarshalsLamellarGauntlets.itemHonorPrice[3] = 10098
fGrandMarshalsLamellarGauntlets.itemTokenPrice = new Array();
fGrandMarshalsLamellarGauntlets.itemTokenPrice[3] = new Array(20,0,0,0);
fGrandMarshalsLamellarGauntlets.itemStats = new Array();
fGrandMarshalsLamellarGauntlets.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Lamellar Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+36 Stamina<br>+13 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the Holy damage bonus of your Judgement of the Crusader by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Aegis (0/5)</span>\
<br> Grand Marshal's Lamellar Chestpiece<br> Grand Marshal's Lamellar Gauntlets<br> Grand Marshal's Lamellar Helm<br> Grand Marshal's Lamellar Legguards<br> Grand Marshal's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarGauntlets; ++i;

var fGrandMarshalsLamellarShoulders = new RewardItem("alliance","Grand Marshal's Lamellar Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsLamellarShoulders.itemHonorPrice = new Array();
fGrandMarshalsLamellarShoulders.itemHonorPrice[3] = 10098
fGrandMarshalsLamellarShoulders.itemTokenPrice = new Array();
fGrandMarshalsLamellarShoulders.itemTokenPrice[3] = new Array(0,20,0,0);
fGrandMarshalsLamellarShoulders.itemStats = new Array();
fGrandMarshalsLamellarShoulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Lamellar Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+36 Stamina<br>+12 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Aegis (0/5)</span>\
<br> Grand Marshal's Lamellar Chestpiece<br> Grand Marshal's Lamellar Gauntlets<br> Grand Marshal's Lamellar Helm<br> Grand Marshal's Lamellar Legguards<br> Grand Marshal's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarShoulders; ++i;

var fGrandMarshalsLamellarLegguards = new RewardItem("alliance","Grand Marshal's Lamellar Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsLamellarLegguards.itemHonorPrice = new Array();
fGrandMarshalsLamellarLegguards.itemHonorPrice[3] = 16065
fGrandMarshalsLamellarLegguards.itemTokenPrice = new Array();
fGrandMarshalsLamellarLegguards.itemTokenPrice[3] = new Array(0,0,0,30);
fGrandMarshalsLamellarLegguards.itemStats = new Array();
fGrandMarshalsLamellarLegguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Lamellar Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+48 Stamina<br>+15 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Aegis (0/5)</span>\
<br> Grand Marshal's Lamellar Chestpiece<br> Grand Marshal's Lamellar Gauntlets<br> Grand Marshal's Lamellar Helm<br> Grand Marshal's Lamellar Legguards<br> Grand Marshal's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarLegguards; ++i;

var fGrandMarshalsLamellarHelm = new RewardItem("alliance","Grand Marshal's Lamellar Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsLamellarHelm.itemHonorPrice = new Array();
fGrandMarshalsLamellarHelm.itemHonorPrice[3] = 16065
fGrandMarshalsLamellarHelm.itemTokenPrice = new Array();
fGrandMarshalsLamellarHelm.itemTokenPrice[3] = new Array(30,0,0,0);
fGrandMarshalsLamellarHelm.itemStats = new Array();
fGrandMarshalsLamellarHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Lamellar Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+44 Stamina<br>+11 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Aegis (0/5)</span>\
<br> Grand Marshal's Lamellar Chestpiece<br> Grand Marshal's Lamellar Gauntlets<br> Grand Marshal's Lamellar Helm<br> Grand Marshal's Lamellar Legguards<br> Grand Marshal's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarHelm; ++i;

var fGrandMarshalsLamellarChestpiece = new RewardItem("alliance","Grand Marshal's Lamellar Chestpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGrandMarshalsLamellarChestpiece.itemHonorPrice = new Array();
fGrandMarshalsLamellarChestpiece.itemHonorPrice[3] = 16524
fGrandMarshalsLamellarChestpiece.itemTokenPrice = new Array();
fGrandMarshalsLamellarChestpiece.itemTokenPrice[3] = new Array(0,30,0,0);
fGrandMarshalsLamellarChestpiece.itemStats = new Array();
fGrandMarshalsLamellarChestpiece.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Lamellar Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+48 Stamina<br>+12 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Aegis (0/5)</span>\
<br> Grand Marshal's Lamellar Chestpiece<br> Grand Marshal's Lamellar Gauntlets<br> Grand Marshal's Lamellar Helm<br> Grand Marshal's Lamellar Legguards<br> Grand Marshal's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarChestpiece; ++i;

var fGrandMarshalsScaledGauntlets = new RewardItem("alliance","Grand Marshal's Scaled Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsScaledGauntlets.itemHonorPrice = new Array();
fGrandMarshalsScaledGauntlets.itemHonorPrice[3] = 10098
fGrandMarshalsScaledGauntlets.itemTokenPrice = new Array();
fGrandMarshalsScaledGauntlets.itemTokenPrice[3] = new Array(20,0,0,0);
fGrandMarshalsScaledGauntlets.itemStats = new Array();
fGrandMarshalsScaledGauntlets.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Scaled Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+19 Strength<br>+25 Stamina<br>+12 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the Holy damage bonus of your Judgement of the Crusader by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vindication (0/5)</span>\
<br> Grand Marshal's Scaled Chestpiece<br> Grand Marshal's Scaled Gauntlets<br> Grand Marshal's Scaled Helm<br> Grand Marshal's Scaled Legguards<br> Grand Marshal's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledGauntlets; ++i;

var fGrandMarshalsScaledShoulders = new RewardItem("alliance","Grand Marshal's Scaled Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsScaledShoulders.itemHonorPrice = new Array();
fGrandMarshalsScaledShoulders.itemHonorPrice[3] = 10098
fGrandMarshalsScaledShoulders.itemTokenPrice = new Array();
fGrandMarshalsScaledShoulders.itemTokenPrice[3] = new Array(0,20,0,0);
fGrandMarshalsScaledShoulders.itemStats = new Array();
fGrandMarshalsScaledShoulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Scaled Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+19 Strength<br>+33 Stamina<br>+8 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vindication (0/5)</span>\
<br> Grand Marshal's Scaled Chestpiece<br> Grand Marshal's Scaled Gauntlets<br> Grand Marshal's Scaled Helm<br> Grand Marshal's Scaled Legguards<br> Grand Marshal's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledShoulders; ++i;

var fGrandMarshalsScaledLegguards = new RewardItem("alliance","Grand Marshal's Scaled Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsScaledLegguards.itemHonorPrice = new Array();
fGrandMarshalsScaledLegguards.itemHonorPrice[3] = 16065
fGrandMarshalsScaledLegguards.itemTokenPrice = new Array();
fGrandMarshalsScaledLegguards.itemTokenPrice[3] = new Array(0,0,0,30);
fGrandMarshalsScaledLegguards.itemStats = new Array();
fGrandMarshalsScaledLegguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Scaled Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+24 Strength<br>+42 Stamina<br>+16 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vindication (0/5)</span>\
<br> Grand Marshal's Scaled Chestpiece<br> Grand Marshal's Scaled Gauntlets<br> Grand Marshal's Scaled Helm<br> Grand Marshal's Scaled Legguards<br> Grand Marshal's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledLegguards; ++i;

var fGrandMarshalsScaledHelm = new RewardItem("alliance","Grand Marshal's Scaled Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsScaledHelm.itemHonorPrice = new Array();
fGrandMarshalsScaledHelm.itemHonorPrice[3] = 16065
fGrandMarshalsScaledHelm.itemTokenPrice = new Array();
fGrandMarshalsScaledHelm.itemTokenPrice[3] = new Array(30,0,0,0);
fGrandMarshalsScaledHelm.itemStats = new Array();
fGrandMarshalsScaledHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Scaled Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+20 Strength<br>+30 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vindication (0/5)</span>\
<br> Grand Marshal's Scaled Chestpiece<br> Grand Marshal's Scaled Gauntlets<br> Grand Marshal's Scaled Helm<br> Grand Marshal's Scaled Legguards<br> Grand Marshal's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledHelm; ++i;

var fGrandMarshalsScaledChestpiece = new RewardItem("alliance","Grand Marshal's Scaled Chestpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGrandMarshalsScaledChestpiece.itemHonorPrice = new Array();
fGrandMarshalsScaledChestpiece.itemHonorPrice[3] = 16524
fGrandMarshalsScaledChestpiece.itemTokenPrice = new Array();
fGrandMarshalsScaledChestpiece.itemTokenPrice[3] = new Array(0,30,0,0);
fGrandMarshalsScaledChestpiece.itemStats = new Array();
fGrandMarshalsScaledChestpiece.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Scaled Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+24 Strength<br>+42 Stamina<br>+12 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vindication (0/5)</span>\
<br> Grand Marshal's Scaled Chestpiece<br> Grand Marshal's Scaled Gauntlets<br> Grand Marshal's Scaled Helm<br> Grand Marshal's Scaled Legguards<br> Grand Marshal's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledChestpiece; ++i;

var fGrandMarshalsOrnamentedChestplate = new RewardItem("alliance","Grand Marshal's Ornamented Chestplate","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGrandMarshalsOrnamentedChestplate.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedChestplate.itemHonorPrice[3] = 16524
fGrandMarshalsOrnamentedChestplate.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedChestplate.itemTokenPrice[3] = new Array(0,30,0,0);
fGrandMarshalsOrnamentedChestplate.itemStats = new Array();
fGrandMarshalsOrnamentedChestplate.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ornamented Chestplate</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+37 Stamina<br>+24 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 18.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Redemption (0/5)</span>\
<br> Grand Marshal's Ornamented Chestplate<br> Grand Marshal's Ornamented Gloves<br> Grand Marshal's Ornamented Headguard<br> Grand Marshal's Ornamented Leggings<br> Grand Marshal's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedChestplate; ++i;

var fGrandMarshalsOrnamentedGloves = new RewardItem("alliance","Grand Marshal's Ornamented Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsOrnamentedGloves.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedGloves.itemHonorPrice[3] = 10098
fGrandMarshalsOrnamentedGloves.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedGloves.itemTokenPrice[3] = new Array(20,0,0,0);
fGrandMarshalsOrnamentedGloves.itemStats = new Array();
fGrandMarshalsOrnamentedGloves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ornamented Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+30 Stamina<br>+20 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the Holy damage bonus of your Judgement of the Crusader by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Redemption (0/5)</span>\
<br> Grand Marshal's Ornamented Chestplate<br> Grand Marshal's Ornamented Gloves<br> Grand Marshal's Ornamented Headguard<br>\
Grand Marshal's Ornamented Leggings<br> Grand Marshal's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedGloves; ++i;

var fGrandMarshalsOrnamentedHeadguard = new RewardItem("alliance","Grand Marshal's Ornamented Headguard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsOrnamentedHeadguard.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedHeadguard.itemHonorPrice[3] = 16065
fGrandMarshalsOrnamentedHeadguard.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedHeadguard.itemTokenPrice[3] = new Array(30,0,0,0);
fGrandMarshalsOrnamentedHeadguard.itemStats = new Array();
fGrandMarshalsOrnamentedHeadguard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ornamented Headguard</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+34 Stamina<br>+22 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 35.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Redemption (0/5)</span>\
<br> Grand Marshal's Ornamented Chestplate<br> Grand Marshal's Ornamented Gloves<br> Grand Marshal's Ornamented Headguard<br> Grand Marshal's Ornamented Leggings<br> Grand Marshal's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedHeadguard; ++i;


var fGrandMarshalsOrnamentedLeggings = new RewardItem("alliance","Grand Marshal's Ornamented Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsOrnamentedLeggings.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedLeggings.itemHonorPrice[3] = 16065
fGrandMarshalsOrnamentedLeggings.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedLeggings.itemTokenPrice[3] = new Array(0,0,0,30);
fGrandMarshalsOrnamentedLeggings.itemStats = new Array();
fGrandMarshalsOrnamentedLeggings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ornamented Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+39 Stamina<br>+26 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 53.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Redemption (0/5)</span>\
<br> Grand Marshal's Ornamented Chestplate<br> Grand Marshal's Ornamented Gloves<br> Grand Marshal's Ornamented Headguard<br> Grand Marshal's Ornamented Leggings<br> Grand Marshal's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedLeggings; ++i;

var fGrandMarshalsOrnamentedSpaulders = new RewardItem("alliance","Grand Marshal's Ornamented Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsOrnamentedSpaulders.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedSpaulders.itemHonorPrice[3] = 10098
fGrandMarshalsOrnamentedSpaulders.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedSpaulders.itemTokenPrice[3] = new Array(0,20,0,0);
fGrandMarshalsOrnamentedSpaulders.itemStats = new Array();
fGrandMarshalsOrnamentedSpaulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ornamented Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+30 Stamina<br>+19 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Redemption (0/5)</span>\
<br> Grand Marshal's Ornamented Chestplate<br> Grand Marshal's Ornamented Gloves<br> Grand Marshal's Ornamented Headguard<br> Grand Marshal's Ornamented Leggings<br> Grand Marshal's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedSpaulders; ++i;

//PRIEST---------------------------------------------------------------------------------------

//PRIEST SET 1-----
var fGrandMarshalsSatinGloves = new RewardItem("alliance","Grand Marshal's Satin Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fGrandMarshalsSatinGloves.itemHonorPrice = new Array();
fGrandMarshalsSatinGloves.itemHonorPrice[4] = 10098
fGrandMarshalsSatinGloves.itemTokenPrice = new Array();
fGrandMarshalsSatinGloves.itemTokenPrice[4] = new Array(20,0,0,0);
fGrandMarshalsSatinGloves.itemStats = new Array();
fGrandMarshalsSatinGloves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Satin Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+33 Stamina<br>+15 Intellect<br>Durability 30 / 30<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the duration of your Psychic Scream spell by 1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Raiment (0/5)</span>\
<br> Grand Marshal's Satin Gloves<br> Grand Marshal's Satin Hood<br> Grand Marshal's Satin Leggings<br> Grand Marshal's Satin Mantle<br> Grand Marshal's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinGloves; ++i;

var fGrandMarshalsSatinMantle = new RewardItem("alliance","Grand Marshal's Satin Mantle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fGrandMarshalsSatinMantle.itemHonorPrice = new Array();
fGrandMarshalsSatinMantle.itemHonorPrice[4] = 10098
fGrandMarshalsSatinMantle.itemTokenPrice = new Array();
fGrandMarshalsSatinMantle.itemTokenPrice[4] = new Array(0,20,0,0);
fGrandMarshalsSatinMantle.itemStats = new Array();
fGrandMarshalsSatinMantle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Satin Mantle</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+33 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Raiment (0/5)</span>\
<br> Grand Marshal's Satin Gloves<br> Grand Marshal's Satin Hood<br> Grand Marshal's Satin Leggings<br> Grand Marshal's Satin Mantle<br> Grand Marshal's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinMantle; ++i;

var fGrandMarshalsSatinLeggings = new RewardItem("alliance","Grand Marshal's Satin Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsSatinLeggings.itemHonorPrice = new Array();
fGrandMarshalsSatinLeggings.itemHonorPrice[4] = 16065
fGrandMarshalsSatinLeggings.itemTokenPrice = new Array();
fGrandMarshalsSatinLeggings.itemTokenPrice[4] = new Array(0,0,0,30);
fGrandMarshalsSatinLeggings.itemStats = new Array();
fGrandMarshalsSatinLeggings.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Satin Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+46 Stamina<br>+23 Intellect<br>Durability 65 / 65<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Raiment (0/5)</span>\
<br> Grand Marshal's Satin Gloves<br> Grand Marshal's Satin Hood<br> Grand Marshal's Satin Leggings<br> Grand Marshal's Satin Mantle<br> Grand Marshal's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinLeggings; ++i;

var fGrandMarshalsSatinHood = new RewardItem("alliance","Grand Marshal's Satin Hood ","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsSatinHood.itemHonorPrice = new Array();
fGrandMarshalsSatinHood.itemHonorPrice[4] = 16065
fGrandMarshalsSatinHood.itemTokenPrice = new Array();
fGrandMarshalsSatinHood.itemTokenPrice[4] = new Array(30,0,0,0);
fGrandMarshalsSatinHood.itemStats = new Array();
fGrandMarshalsSatinHood.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Satin Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+46 Stamina<br>+19 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 18.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Raiment (0/5)</span>\
<br> Grand Marshal's Satin Gloves<br> Grand Marshal's Satin Hood<br> Grand Marshal's Satin Leggings<br> Grand Marshal's Satin Mantle<br> Grand Marshal's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinHood; ++i;

var fGrandMarshalsSatinRobe = new RewardItem("alliance","Grand Marshal's Satin Robe","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Cloth_43.gif&reason=external-or-uncollected-resource");
fGrandMarshalsSatinRobe.itemHonorPrice = new Array();
fGrandMarshalsSatinRobe.itemHonorPrice[4] = 16524
fGrandMarshalsSatinRobe.itemTokenPrice = new Array();
fGrandMarshalsSatinRobe.itemTokenPrice[4] = new Array(0,30,0,0);
fGrandMarshalsSatinRobe.itemStats = new Array();
fGrandMarshalsSatinRobe.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Satin Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+46 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 80 / 80<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Raiment (0/5)</span>\
<br> Grand Marshal's Satin Gloves<br> Grand Marshal's Satin Hood<br> Grand Marshal's Satin Leggings<br> Grand Marshal's Satin Mantle<br> Grand Marshal's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinRobe; ++i;

//PRIEST SET 2 ------------
var fGrandMarshalsMoonclothCowl = new RewardItem("alliance","Grand Marshal's Mooncloth Cowl","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsMoonclothCowl.itemHonorPrice = new Array();
fGrandMarshalsMoonclothCowl.itemHonorPrice[4] = 16065
fGrandMarshalsMoonclothCowl.itemTokenPrice = new Array();
fGrandMarshalsMoonclothCowl.itemTokenPrice[4] = new Array(30,0,0,0);
fGrandMarshalsMoonclothCowl.itemStats = new Array();
fGrandMarshalsMoonclothCowl.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mooncloth Cowl</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+40 Stamina<br>+26 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Investiture (0/5)</span>\
<br> Grand Marshal's Mooncloth Cowl<br> Grand Marshal's Mooncloth Legguards<br> Grand Marshal's Mooncloth Mitts<br> Grand Marshal's Mooncloth Shoulderpads<br> Grand Marshal's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothCowl; ++i;

var fGrandMarshalsMoonclothLegguards = new RewardItem("alliance","Grand Marshal's Mooncloth Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsMoonclothLegguards.itemHonorPrice = new Array();
fGrandMarshalsMoonclothLegguards.itemHonorPrice[4] = 16065
fGrandMarshalsMoonclothLegguards.itemTokenPrice = new Array();
fGrandMarshalsMoonclothLegguards.itemTokenPrice[4] = new Array(0,0,0,30);
fGrandMarshalsMoonclothLegguards.itemStats = new Array();
fGrandMarshalsMoonclothLegguards.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mooncloth Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+42 Stamina<br>+28 Intellect<br>Durability 65 / 65<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Investiture (0/5)</span>\
<br> Grand Marshal's Mooncloth Cowl<br> Grand Marshal's Mooncloth Legguards<br> Grand Marshal's Mooncloth Mitts<br> Grand Marshal's Mooncloth Shoulderpads<br> Grand Marshal's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothLegguards; ++i;

var fGrandMarshalsMoonclothMitts = new RewardItem("alliance","Grand Marshal's Mooncloth Mitts","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fGrandMarshalsMoonclothMitts.itemHonorPrice = new Array();
fGrandMarshalsMoonclothMitts.itemHonorPrice[4] = 10098
fGrandMarshalsMoonclothMitts.itemTokenPrice = new Array();
fGrandMarshalsMoonclothMitts.itemTokenPrice[4] = new Array(20,0,0,0);
fGrandMarshalsMoonclothMitts.itemStats = new Array();
fGrandMarshalsMoonclothMitts.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mooncloth Mitts</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+33 Stamina<br>+15 Intellect<br>Durability 30 / 30<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the duration of your Psychic Scream spell by 1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Investiture (0/5)</span>\
<br> Grand Marshal's Mooncloth Cowl<br> Grand Marshal's Mooncloth Legguards<br> Grand Marshal's Mooncloth Mitts<br> Grand Marshal's Mooncloth Shoulderpads<br> Grand Marshal's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothMitts; ++i;

var fGrandMarshalsMoonclothShoulderpads = new RewardItem("alliance","Grand Marshal's Mooncloth Shoulderpads","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fGrandMarshalsMoonclothShoulderpads.itemHonorPrice = new Array();
fGrandMarshalsMoonclothShoulderpads.itemHonorPrice[4] = 10098
fGrandMarshalsMoonclothShoulderpads.itemTokenPrice = new Array();
fGrandMarshalsMoonclothShoulderpads.itemTokenPrice[4] = new Array(0,20,0,0);
fGrandMarshalsMoonclothShoulderpads.itemStats = new Array();
fGrandMarshalsMoonclothShoulderpads.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mooncloth Shoulderpads</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+30 Stamina<br>+20 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Investiture (0/5)</span>\
<br> Grand Marshal's Mooncloth Cowl<br> Grand Marshal's Mooncloth Legguards<br> Grand Marshal's Mooncloth Mitts<br> Grand Marshal's Mooncloth Shoulderpads<br> Grand Marshal's Mooncloth Vestments<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothShoulderpads; ++i;

var fGrandMarshalsMoonclothVestments = new RewardItem("alliance","Grand Marshal's Mooncloth Vestments","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Cloth_43.gif&reason=external-or-uncollected-resource");
fGrandMarshalsMoonclothVestments.itemHonorPrice = new Array();
fGrandMarshalsMoonclothVestments.itemHonorPrice[4] = 16524
fGrandMarshalsMoonclothVestments.itemTokenPrice = new Array();
fGrandMarshalsMoonclothVestments.itemTokenPrice[4] = new Array(0,30,0,0);
fGrandMarshalsMoonclothVestments.itemStats = new Array();
fGrandMarshalsMoonclothVestments.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mooncloth Vestments</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+39 Stamina<br>+25 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 80 / 80<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 51.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Investiture (0/5)</span>\
<br> Grand Marshal's Mooncloth Cowl<br> Grand Marshal's Mooncloth Legguards<br> Grand Marshal's Mooncloth Mitts<br> Grand Marshal's Mooncloth Shoulderpads<br> Grand Marshal's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothVestments; ++i;

//ROGUE-----------------------------------------------
var fGrandMarshalsLeatherGloves = new RewardItem("alliance","Grand Marshal's Leather Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsLeatherGloves.itemHonorPrice = new Array();
fGrandMarshalsLeatherGloves.itemHonorPrice[5] = 10098
fGrandMarshalsLeatherGloves.itemTokenPrice = new Array();
fGrandMarshalsLeatherGloves.itemTokenPrice[5] = new Array(20,0,0,0);
fGrandMarshalsLeatherGloves.itemStats = new Array();
fGrandMarshalsLeatherGloves.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Leather Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>183 Armor<br>+21 Agility<br>+31 Stamina<br>Durability 35 / 35<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Causes your Deadly Throw ability to interrupt spellcasting and prevent any spell in that school from being cast for 3 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vestments (0/5)</span>\
<br> Grand Marshal's Leather Gloves<br> Grand Marshal's Leather Helm<br> Grand Marshal's Leather Legguards<br> Grand Marshal's Leather Spaulders<br> Grand Marshal's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherGloves; ++i;

var fGrandMarshalsLeatherSpaulders = new RewardItem("alliance","Grand Marshal's Leather Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsLeatherSpaulders.itemHonorPrice = new Array();
fGrandMarshalsLeatherSpaulders.itemHonorPrice[5] = 10098
fGrandMarshalsLeatherSpaulders.itemTokenPrice = new Array();
fGrandMarshalsLeatherSpaulders.itemTokenPrice[5] = new Array(0,20,0,0);
fGrandMarshalsLeatherSpaulders.itemStats = new Array();
fGrandMarshalsLeatherSpaulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Leather Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>219 Armor<br>+13 Agility<br>+31 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vestments (0/5)</span>\
<br> Grand Marshal's Leather Gloves<br> Grand Marshal's Leather Helm<br> Grand Marshal's Leather Legguards<br> Grand Marshal's Leather Spaulders<br> Grand Marshal's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherSpaulders; ++i;

var fGrandMarshalsLeatherLegguards = new RewardItem("alliance","Grand Marshal's Leather Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsLeatherLegguards.itemHonorPrice = new Array();
fGrandMarshalsLeatherLegguards.itemHonorPrice[5] = 16065
fGrandMarshalsLeatherLegguards.itemTokenPrice = new Array();
fGrandMarshalsLeatherLegguards.itemTokenPrice[5] = new Array(0,0,0,30);
fGrandMarshalsLeatherLegguards.itemStats = new Array();
fGrandMarshalsLeatherLegguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Leather Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>256 Armor<br>+28 Agility<br>+42 Stamina<br>Durability 75 / 75<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vestments (0/5)</span>\
<br> Grand Marshal's Leather Gloves<br> Grand Marshal's Leather Helm<br> Grand Marshal's Leather Legguards<br> Grand Marshal's Leather Spaulders<br> Grand Marshal's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherLegguards; ++i;

var fGrandMarshalsLeatherHelm = new RewardItem("alliance","Grand Marshal's Leather Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsLeatherHelm.itemHonorPrice = new Array();
fGrandMarshalsLeatherHelm.itemHonorPrice[5] = 16065
fGrandMarshalsLeatherHelm.itemTokenPrice = new Array();
fGrandMarshalsLeatherHelm.itemTokenPrice[5] = new Array(30,0,0,0);
fGrandMarshalsLeatherHelm.itemStats = new Array();
fGrandMarshalsLeatherHelm.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Leather Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>237 Armor<br>+20 Agility<br>+36 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vestments (0/5)</span>\
<br> Grand Marshal's Leather Gloves<br> Grand Marshal's Leather Helm<br> Grand Marshal's Leather Legguards<br> Grand Marshal's Leather Spaulders<br> Grand Marshal's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherHelm; ++i;

var fGrandMarshalsLeatherTunic = new RewardItem("alliance","Grand Marshal's Leather Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsLeatherTunic.itemHonorPrice = new Array();
fGrandMarshalsLeatherTunic.itemHonorPrice[5] = 16524
fGrandMarshalsLeatherTunic.itemTokenPrice = new Array();
fGrandMarshalsLeatherTunic.itemTokenPrice[5] = new Array(0,30,0,0);
fGrandMarshalsLeatherTunic.itemStats = new Array();
fGrandMarshalsLeatherTunic.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Leather Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>292 Armor<br>+20 Agility<br>+42 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 100 / 100<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Vestments (0/5)</span>\
<br> Grand Marshal's Leather Gloves<br> Grand Marshal's Leather Helm<br> Grand Marshal's Leather Legguards<br> Grand Marshal's Leather Spaulders<br> Grand Marshal's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherTunic; ++i;

//SHAMAN---------------------------------------------------------------------------------------------

var fGrandMarshalsLinkedGauntlets = new RewardItem("alliance","Grand Marshal's Linked Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsLinkedGauntlets.itemHonorPrice = new Array();
fGrandMarshalsLinkedGauntlets.itemHonorPrice[6] = 10098
fGrandMarshalsLinkedGauntlets.itemTokenPrice = new Array();
fGrandMarshalsLinkedGauntlets.itemTokenPrice[6] = new Array(20,0,0,0);
fGrandMarshalsLinkedGauntlets.itemStats = new Array();
fGrandMarshalsLinkedGauntlets.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Linked Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+21 Strength<br>+33 Stamina<br>Durability 40 / 40<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the damage done by your Lightning Shield by 8%.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Earthshaker (0/5)</span>\
<br> Grand Marshal's Linked Armor<br> Grand Marshal's Linked Gauntlets<br> Grand Marshal's Linked Helm<br> Grand Marshal's Linked Leggings<br> Grand Marshal's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedGauntlets; ++i;

var fGrandMarshalsLinkedSpaulders = new RewardItem("alliance","Grand Marshal's Linked Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsLinkedSpaulders.itemHonorPrice = new Array();
fGrandMarshalsLinkedSpaulders.itemHonorPrice[6] = 10098
fGrandMarshalsLinkedSpaulders.itemTokenPrice = new Array();
fGrandMarshalsLinkedSpaulders.itemTokenPrice[6] = new Array(0,20,0,0);
fGrandMarshalsLinkedSpaulders.itemStats = new Array();
fGrandMarshalsLinkedSpaulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Linked Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+13 Strength<br>+33 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Earthshaker (0/5)</span>\
<br> Grand Marshal's Linked Armor<br> Grand Marshal's Linked Gauntlets<br> Grand Marshal's Linked Helm<br> Grand Marshal's Linked Leggings<br> Grand Marshal's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedSpaulders; ++i;


var fGrandMarshalsLinkedLeggings = new RewardItem("alliance","Grand Marshal's Linked Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsLinkedLeggings.itemHonorPrice = new Array();
fGrandMarshalsLinkedLeggings.itemHonorPrice[6] = 16065
fGrandMarshalsLinkedLeggings.itemTokenPrice = new Array();
fGrandMarshalsLinkedLeggings.itemTokenPrice[6] = new Array(0,0,0,30);
fGrandMarshalsLinkedLeggings.itemStats = new Array();
fGrandMarshalsLinkedLeggings.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Linked Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+22 Strength<br>+42 Stamina<br>+22 Intellect<br>Durability 90 / 90<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Earthshaker (0/5)</span>\
<br> Grand Marshal's Linked Armor<br> Grand Marshal's Linked Gauntlets<br> Grand Marshal's Linked Helm<br> Grand Marshal's Linked Leggings<br> Grand Marshal's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedLeggings; ++i;

var fGrandMarshalsLinkedHelm = new RewardItem("alliance","Grand Marshal's Linked Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsLinkedHelm.itemHonorPrice = new Array();
fGrandMarshalsLinkedHelm.itemHonorPrice[6] = 16065
fGrandMarshalsLinkedHelm.itemTokenPrice = new Array();
fGrandMarshalsLinkedHelm.itemTokenPrice[6] = new Array(30,0,0,0);
fGrandMarshalsLinkedHelm.itemStats = new Array();
fGrandMarshalsLinkedHelm.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Linked Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+20 Strength<br>+30 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Earthshaker (0/5)</span>\
<br> Grand Marshal's Linked Armor<br> Grand Marshal's Linked Gauntlets<br> Grand Marshal's Linked Helm<br> Grand Marshal's Linked Leggings<br> Grand Marshal's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedHelm; ++i;

var fGrandMarshalsLinkedArmor = new RewardItem("alliance","Grand Marshal's Linked Armor","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGrandMarshalsLinkedArmor.itemHonorPrice = new Array();
fGrandMarshalsLinkedArmor.itemHonorPrice[6] = 16524
fGrandMarshalsLinkedArmor.itemTokenPrice = new Array();
fGrandMarshalsLinkedArmor.itemTokenPrice[6] = new Array(0,30,0,0);
fGrandMarshalsLinkedArmor.itemStats = new Array();
fGrandMarshalsLinkedArmor.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Linked Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+12 Strength<br>+42 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Earthshaker (0/5)</span>\
<br> Grand Marshal's Linked Armor<br> Grand Marshal's Linked Gauntlets<br> Grand Marshal's Linked Helm<br> Grand Marshal's Linked Leggings<br> Grand Marshal's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedArmor; ++i;


//SHAMAN SET 2---------------
var fGrandMarshalsMailGauntlets = new RewardItem("alliance","Grand Marshal's Mail Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsMailGauntlets.itemHonorPrice = new Array();
fGrandMarshalsMailGauntlets.itemHonorPrice[6] = 10098
fGrandMarshalsMailGauntlets.itemTokenPrice = new Array();
fGrandMarshalsMailGauntlets.itemTokenPrice[6] = new Array(20,0,0,0);
fGrandMarshalsMailGauntlets.itemStats = new Array();
fGrandMarshalsMailGauntlets.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mail Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+33 Stamina<br>+13 Intellect<br>Durability 40 / 40<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of all Shock spells by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Thunderfist (0/5)</span>\
<br> Grand Marshal's Mail Armor<br> Grand Marshal's Mail Gauntlets<br> Grand Marshal's Mail Helm<br> Grand Marshal's Mail Leggings<br> Grand Marshal's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailGauntlets; ++i;

var fGrandMarshalsMailSpaulders = new RewardItem("alliance","Grand Marshal's Mail Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsMailSpaulders.itemHonorPrice = new Array();
fGrandMarshalsMailSpaulders.itemHonorPrice[6] = 10098
fGrandMarshalsMailSpaulders.itemTokenPrice = new Array();
fGrandMarshalsMailSpaulders.itemTokenPrice[6] = new Array(0,20,0,0);
fGrandMarshalsMailSpaulders.itemStats = new Array();
fGrandMarshalsMailSpaulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mail Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+33 Stamina<br>+13 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Thunderfist (0/5)</span>\
<br> Grand Marshal's Mail Armor<br> Grand Marshal's Mail Gauntlets<br> Grand Marshal's Mail Helm<br> Grand Marshal's Mail Leggings<br> Grand Marshal's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailSpaulders; ++i;

var fGrandMarshalsMailLeggings = new RewardItem("alliance","Grand Marshal's Mail Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsMailLeggings.itemHonorPrice = new Array();
fGrandMarshalsMailLeggings.itemHonorPrice[6] = 16065
fGrandMarshalsMailLeggings.itemTokenPrice = new Array();
fGrandMarshalsMailLeggings.itemTokenPrice[6] = new Array(0,0,0,30);
fGrandMarshalsMailLeggings.itemStats = new Array();
fGrandMarshalsMailLeggings.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mail Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+42 Stamina<br>+18 Intellect<br>Durability 90 / 90<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Thunderfist (0/5)</span>\
<br> Grand Marshal's Mail Armor<br> Grand Marshal's Mail Gauntlets<br> Grand Marshal's Mail Helm<br> Grand Marshal's Mail Leggings<br> Grand Marshal's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailLeggings; ++i;

var fGrandMarshalsMailHelm = new RewardItem("alliance","Grand Marshal's Mail Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsMailHelm.itemHonorPrice = new Array();
fGrandMarshalsMailHelm.itemHonorPrice[6] = 16065
fGrandMarshalsMailHelm.itemTokenPrice = new Array();
fGrandMarshalsMailHelm.itemTokenPrice[6] = new Array(30,0,0,0);
fGrandMarshalsMailHelm.itemStats = new Array();
fGrandMarshalsMailHelm.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mail Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+36 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Thunderfist (0/5)</span>\
<br> Grand Marshal's Mail Armor<br> Grand Marshal's Mail Gauntlets<br> Grand Marshal's Mail Helm<br> Grand Marshal's Mail Leggings<br> Grand Marshal's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailHelm; ++i;


var fGrandMarshalsMailArmor = new RewardItem("alliance","Grand Marshal's Mail Armor","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGrandMarshalsMailArmor.itemHonorPrice = new Array();
fGrandMarshalsMailArmor.itemHonorPrice[6] = 16524
fGrandMarshalsMailArmor.itemTokenPrice = new Array();
fGrandMarshalsMailArmor.itemTokenPrice[6] = new Array(0,30,0,0);
fGrandMarshalsMailArmor.itemStats = new Array();
fGrandMarshalsMailArmor.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Mail Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+42 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Thunderfist (0/5)</span>\
<br> Grand Marshal's Mail Armor<br> Grand Marshal's Mail Gauntlets<br> Grand Marshal's Mail Helm<br> Grand Marshal's Mail Leggings<br> Grand Marshal's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailArmor; ++i;

//SHAMAN SET 3-------------------------
var fGrandMarshalsRingmailChestguard = new RewardItem("alliance","Grand Marshal's Ringmail Chestguard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGrandMarshalsRingmailChestguard.itemHonorPrice = new Array();
fGrandMarshalsRingmailChestguard.itemHonorPrice[6] = 16524
fGrandMarshalsRingmailChestguard.itemTokenPrice = new Array();
fGrandMarshalsRingmailChestguard.itemTokenPrice[6] = new Array(0,30,0,0);
fGrandMarshalsRingmailChestguard.itemStats = new Array();
fGrandMarshalsRingmailChestguard.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ringmail Chestguard</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+34 Stamina<br>+22 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wartide (0/5)</span>\
<br> Grand Marshal's Ringmail Chestguard<br> Grand Marshal's Ringmail Gloves<br> Grand Marshal's Ringmail Headpiece<br> Grand Marshal's Ringmail Legguards<br> Grand Marshal's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailChestguard; ++i;

var fGrandMarshalsRingmailGloves = new RewardItem("alliance","Grand Marshal's Ringmail Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsRingmailGloves.itemHonorPrice = new Array();
fGrandMarshalsRingmailGloves.itemHonorPrice[6] = 10098
fGrandMarshalsRingmailGloves.itemTokenPrice = new Array();
fGrandMarshalsRingmailGloves.itemTokenPrice[6] = new Array(20,0,0,0);
fGrandMarshalsRingmailGloves.itemStats = new Array();
fGrandMarshalsRingmailGloves.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ringmail Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+28 Stamina<br>+18 Intellect<br>Durability 40 / 40<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of all Shock spells by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wartide (0/5)</span>\
<br> Grand Marshal's Ringmail Chestguard<br> Grand Marshal's Ringmail Gloves<br> Grand Marshal's Ringmail Headpiece<br> Grand Marshal's Ringmail Legguards<br> Grand Marshal's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailGloves; ++i;

var fGrandMarshalsRingmailHeadpiece = new RewardItem("alliance","Grand Marshal's Ringmail Headpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsRingmailHeadpiece.itemHonorPrice = new Array();
fGrandMarshalsRingmailHeadpiece.itemHonorPrice[6] = 16065
fGrandMarshalsRingmailHeadpiece.itemTokenPrice = new Array();
fGrandMarshalsRingmailHeadpiece.itemTokenPrice[6] = new Array(30,0,0,0);
fGrandMarshalsRingmailHeadpiece.itemStats = new Array();
fGrandMarshalsRingmailHeadpiece.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ringmail Headpiece</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+33 Stamina<br>+21 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wartide (0/5)</span>\
<br> Grand Marshal's Ringmail Chestguard<br> Grand Marshal's Ringmail Gloves<br> Grand Marshal's Ringmail Headpiece<br> Grand Marshal's Ringmail Legguards<br> Grand Marshal's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailHeadpiece; ++i;

var fGrandMarshalsRingmailLegguards = new RewardItem("alliance","Grand Marshal's Ringmail Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsRingmailLegguards.itemHonorPrice = new Array();
fGrandMarshalsRingmailLegguards.itemHonorPrice[6] = 16065
fGrandMarshalsRingmailLegguards.itemTokenPrice = new Array();
fGrandMarshalsRingmailLegguards.itemTokenPrice[6] = new Array(0,0,0,30);
fGrandMarshalsRingmailLegguards.itemStats = new Array();
fGrandMarshalsRingmailLegguards.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ringmail Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+36 Stamina<br>+24 Intellect<br>Durability 90 / 90<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 62.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wartide (0/5)</span>\
<br> Grand Marshal's Ringmail Chestguard<br> Grand Marshal's Ringmail Gloves<br> Grand Marshal's Ringmail Headpiece<br> Grand Marshal's Ringmail Legguards<br> Grand Marshal's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailLegguards; ++i;

var fGrandMarshalsRingmailShoulders = new RewardItem("alliance","Grand Marshal's Ringmail Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsRingmailShoulders.itemHonorPrice = new Array();
fGrandMarshalsRingmailShoulders.itemHonorPrice[6] = 10098
fGrandMarshalsRingmailShoulders.itemTokenPrice = new Array();
fGrandMarshalsRingmailShoulders.itemTokenPrice[6] = new Array(0,20,0,0);
fGrandMarshalsRingmailShoulders.itemStats = new Array();
fGrandMarshalsRingmailShoulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Ringmail Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+28 Stamina<br>+18 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Wartide (0/5)</span>\
<br> Grand Marshal's Ringmail Chestguard<br> Grand Marshal's Ringmail Gloves<br> Grand Marshal's Ringmail Headpiece<br> Grand Marshal's Ringmail Legguards<br> Grand Marshal's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailShoulders; ++i;



//WARLOCK---------------------------------
var fHighWarlordsDreadweaveGloves = new RewardItem("alliance","Grand Marshal's Dreadweave Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fHighWarlordsDreadweaveGloves.itemHonorPrice = new Array();
fHighWarlordsDreadweaveGloves.itemHonorPrice[7] = 10098
fHighWarlordsDreadweaveGloves.itemTokenPrice = new Array() ;
fHighWarlordsDreadweaveGloves.itemTokenPrice[7] = new Array(20,0,0,0);
fHighWarlordsDreadweaveGloves.itemStats = new Array();
fHighWarlordsDreadweaveGloves.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dreadweave Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+31 Stamina<br>+21 Intellect<br>Durability 30 / 30<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Gives you a 50% chance to avoid interruption caused by damage while casting Fear.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Dreadgear (0/5)</span>\
<br> Grand Marshal's Dreadweave Gloves<br> Grand Marshal's Dreadweave Hood<br>Grand Marshal's Dreadweave Leggings<br> Grand Marshal's Dreadweave Mantle<br> Grand Marshal's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveGloves; ++i;

var fHighWarlordsDreadweaveMantle = new RewardItem("alliance","Grand Marshal's Dreadweave Mantle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fHighWarlordsDreadweaveMantle.itemHonorPrice = new Array();
fHighWarlordsDreadweaveMantle.itemHonorPrice[7] = 10098
fHighWarlordsDreadweaveMantle.itemTokenPrice = new Array();
fHighWarlordsDreadweaveMantle.itemTokenPrice[7] = new Array(0,20,0,0);
fHighWarlordsDreadweaveMantle.itemStats = new Array();
fHighWarlordsDreadweaveMantle.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dreadweave Mantle</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+19 Stamina<br>+15 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 6.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Dreadgear (0/5)</span>\
<br> Grand Marshal's Dreadweave Gloves<br> Grand Marshal's Dreadweave Hood<br> Grand Marshal's Dreadweave Leggings<br> Grand Marshal's Dreadweave Mantle<br> Grand Marshal's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveMantle; ++i;

var fHighWarlordsDreadweaveLeggings = new RewardItem("alliance","Grand Marshal's Dreadweave Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fHighWarlordsDreadweaveLeggings.itemHonorPrice = new Array();
fHighWarlordsDreadweaveLeggings.itemHonorPrice[7] = 16065
fHighWarlordsDreadweaveLeggings.itemTokenPrice = new Array();
fHighWarlordsDreadweaveLeggings.itemTokenPrice[7] = new Array(0,0,0,30);
fHighWarlordsDreadweaveLeggings.itemStats = new Array();
fHighWarlordsDreadweaveLeggings.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dreadweave Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+49 Stamina<br>+22 Intellect<br>Durability 65 / 65<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Dreadgear (0/5)</span>\
<br> Grand Marshal's Dreadweave Gloves<br> Grand Marshal's Dreadweave Hood<br>Grand Marshal's Dreadweave Leggings<br> Grand Marshal's Dreadweave Mantle<br> Grand Marshal's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveLeggings; ++i;

var fHighWarlordsDreadweaveHood = new RewardItem("alliance","Grand Marshal's Dreadweave Hood","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fHighWarlordsDreadweaveHood.itemHonorPrice = new Array();
fHighWarlordsDreadweaveHood.itemHonorPrice[7] = 16065
fHighWarlordsDreadweaveHood.itemTokenPrice = new Array();
fHighWarlordsDreadweaveHood.itemTokenPrice[7] = new Array(30,0,0,0);
fHighWarlordsDreadweaveHood.itemStats = new Array();
fHighWarlordsDreadweaveHood.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dreadweave Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+49 Stamina<br>+14 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Dreadgear (0/5)</span>\
<br> Grand Marshal's Dreadweave Gloves<br> Grand Marshal's Dreadweave Hood<br> Grand Marshal's Dreadweave Leggings<br> Grand Marshal's Dreadweave Mantle<br> Grand Marshal's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveHood; ++i;

var fHighWarlordsDreadweaveRobe = new RewardItem("alliance","Grand Marshal's Dreadweave Robe","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Cloth_43.gif&reason=external-or-uncollected-resource");
fHighWarlordsDreadweaveRobe.itemHonorPrice = new Array();
fHighWarlordsDreadweaveRobe.itemHonorPrice[7] = 16524
fHighWarlordsDreadweaveRobe.itemTokenPrice = new Array();
fHighWarlordsDreadweaveRobe.itemTokenPrice[7] = new Array(0,30,0,0);
fHighWarlordsDreadweaveRobe.itemStats = new Array();
fHighWarlordsDreadweaveRobe.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Dreadweave Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+49 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 80 / 80<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Dreadgear (0/5)</span>\
<br> Grand Marshal's Dreadweave Gloves<br> Grand Marshal's Dreadweave Hood<br> Grand Marshal's Dreadweave Leggings<br> Grand Marshal's Dreadweave Mantle<br> Grand Marshal's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveRobe; ++i;

//WARRIOR----------------------------------------
var fGrandMarshalsPlateGauntlets = new RewardItem("alliance","Grand Marshal's Plate Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsPlateGauntlets.itemHonorPrice = new Array();
fGrandMarshalsPlateGauntlets.itemHonorPrice[8] = 10098
fGrandMarshalsPlateGauntlets.itemTokenPrice = new Array();
fGrandMarshalsPlateGauntlets.itemTokenPrice[8] = new Array(20,0,0,0);
fGrandMarshalsPlateGauntlets.itemStats = new Array();
fGrandMarshalsPlateGauntlets.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Plate Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+22 Strength<br>+30 Stamina<br>Durability 45 / 45<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Hamstring Rage cost reduced by 3.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Battlegear (0/5)</span>\
<br> Grand Marshal's Plate Chestpiece<br> Grand Marshal's Plate Gauntlets<br> Grand Marshal's Plate Helm<br> Grand Marshal's Plate Legguards<br> Grand Marshal's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateGauntlets; ++i;

var fGrandMarshalsPlateShoulders = new RewardItem("alliance","Grand Marshal's Plate Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsPlateShoulders.itemHonorPrice = new Array();
fGrandMarshalsPlateShoulders.itemHonorPrice[8] = 10098
fGrandMarshalsPlateShoulders.itemTokenPrice = new Array();
fGrandMarshalsPlateShoulders.itemTokenPrice[8] = new Array(0,20,0,0);
fGrandMarshalsPlateShoulders.itemStats = new Array();
fGrandMarshalsPlateShoulders.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Plate Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+14 Strength<br>+36 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Battlegear (0/5)</span>\
<br> Grand Marshal's Plate Chestpiece<br> Grand Marshal's Plate Gauntlets<br> Grand Marshal's Plate Helm<br> Grand Marshal's Plate Legguards<br> Grand Marshal's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateShoulders; ++i;


var fGrandMarshalsPlateLegguards = new RewardItem("alliance","Grand Marshal's Plate Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsPlateLegguards.itemHonorPrice = new Array();
fGrandMarshalsPlateLegguards.itemHonorPrice[8] = 16065
fGrandMarshalsPlateLegguards.itemTokenPrice = new Array();
fGrandMarshalsPlateLegguards.itemTokenPrice[8] = new Array(0,0,0,30);
fGrandMarshalsPlateLegguards.itemStats = new Array();
fGrandMarshalsPlateLegguards.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Plate Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+28 Strength<br>+46 Stamina<br>Durability 100 / 100<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Battlegear (0/5)</span>\
<br> Grand Marshal's Plate Chestpiece<br> Grand Marshal's Plate Gauntlets<br> Grand Marshal's Plate Helm<br> Grand Marshal's Plate Legguards<br> Grand Marshal's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateLegguards; ++i;

var fGrandMarshalsPlateHelm = new RewardItem("alliance","Grand Marshal's Plate Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsPlateHelm.itemHonorPrice = new Array();
fGrandMarshalsPlateHelm.itemHonorPrice[8] = 16065
fGrandMarshalsPlateHelm.itemTokenPrice = new Array();
fGrandMarshalsPlateHelm.itemTokenPrice[8] = new Array(30,0,0,0);
fGrandMarshalsPlateHelm.itemStats = new Array();
fGrandMarshalsPlateHelm.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Plate Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+20 Strength<br>+34 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Battlegear (0/5)</span>\
<br> Grand Marshal's Plate Chestpiece<br> Grand Marshal's Plate Gauntlets<br> Grand Marshal's Plate Helm<br> Grand Marshal's Plate Legguards<br> Grand Marshal's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateHelm; ++i;

var fGrandMarshalsPlateChestpiece = new RewardItem("alliance","Grand Marshal's Plate Chestpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate05.gif");
fGrandMarshalsPlateChestpiece.itemHonorPrice = new Array();
fGrandMarshalsPlateChestpiece.itemHonorPrice[8] = 16524
fGrandMarshalsPlateChestpiece.itemTokenPrice = new Array();
fGrandMarshalsPlateChestpiece.itemTokenPrice[8] = new Array(0,30,0,0);
fGrandMarshalsPlateChestpiece.itemStats = new Array();
fGrandMarshalsPlateChestpiece.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Grand Marshal's Plate Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+12 Strength<br>+46 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">Grand Marshal's Battlegear (0/5)</span>\
<br> Grand Marshal's Plate Chestpiece<br> Grand Marshal's Plate Gauntlets<br> Grand Marshal's Plate Helm<br> Grand Marshal's Plate Legguards<br> Grand Marshal's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateChestpiece; ++i;

//-------------------------------------------------------------------
//---Horde below

//DRUID----------------------------------------------------
var fGrandMarshalsDragonhideGloves = new RewardItem("horde","High Warlord's Dragonhide Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsDragonhideGloves.itemHonorPrice = new Array();
fGrandMarshalsDragonhideGloves.itemHonorPrice[0] = 10098
fGrandMarshalsDragonhideGloves.itemTokenPrice = new Array();
fGrandMarshalsDragonhideGloves.itemTokenPrice[0] = new Array(20,0,0,0);
fGrandMarshalsDragonhideGloves.itemStats = new Array();
fGrandMarshalsDragonhideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dragonhide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+17 Strength<br>+17 Agility<br>+24 Stamina<br>+11 Intellect<br>Durability 35 / 35<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 35.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Sanctuary (0/5)</span>\
<br> High Warlord's Dragonhide Gloves<br> High Warlord's Dragonhide Helm<br> High Warlord's Dragonhide Legguards<br> High Warlord's Dragonhide Spaulders<br> High Warlord's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideGloves; ++i;

var fGrandMarshalsDragonhideSpaulders = new RewardItem("horde","High Warlord's Dragonhide Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsDragonhideSpaulders.itemHonorPrice = new Array();
fGrandMarshalsDragonhideSpaulders.itemHonorPrice[0] = 10098
fGrandMarshalsDragonhideSpaulders.itemTokenPrice = new Array();
fGrandMarshalsDragonhideSpaulders.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsDragonhideSpaulders.itemStats = new Array();
fGrandMarshalsDragonhideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dragonhide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+17 Strength<br>+17 Agility<br>+24 Stamina<br>+13 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 18.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Sanctuary (0/5)</span>\
<br> High Warlord's Dragonhide Gloves<br> High Warlord's Dragonhide Helm<br> High Warlord's Dragonhide Legguards<br> High Warlord's Dragonhide Spaulders<br> High Warlord's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideSpaulders; ++i;

var fGrandMarshalsDragonhideLegguards = new RewardItem("horde","High Warlord's Dragonhide Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsDragonhideLegguards.itemHonorPrice = new Array();
fGrandMarshalsDragonhideLegguards.itemHonorPrice[0] = 16065
fGrandMarshalsDragonhideLegguards.itemTokenPrice = new Array();
fGrandMarshalsDragonhideLegguards.itemTokenPrice[0] = new Array(0,0,0,30);
fGrandMarshalsDragonhideLegguards.itemStats = new Array();
fGrandMarshalsDragonhideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dragonhide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>306 Armor<br>+22 Strength<br>+22 Agility<br>+30 Stamina<br>+22 Intellect<br>Durability 75 / 75<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 48.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Sanctuary (0/5)</span>\
<br> High Warlord's Dragonhide Gloves<br> High Warlord's Dragonhide Helm<br> High Warlord's Dragonhide Legguards<br> High Warlord's Dragonhide Spaulders<br> High Warlord's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideLegguards; ++i;

var fGrandMarshalsDragonhideHelm = new RewardItem("horde","High Warlord's Dragonhide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsDragonhideHelm.itemHonorPrice = new Array();
fGrandMarshalsDragonhideHelm.itemHonorPrice[0] = 16065
fGrandMarshalsDragonhideHelm.itemTokenPrice = new Array();
fGrandMarshalsDragonhideHelm.itemTokenPrice[0] = new Array(30,0,0,0);
fGrandMarshalsDragonhideHelm.itemStats = new Array();
fGrandMarshalsDragonhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dragonhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+22 Strength<br>+22 Agility<br>+21 Stamina<br>+14 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Sanctuary (0/5)</span>\
<br> High Warlord's Dragonhide Gloves<br> High Warlord's Dragonhide Helm<br> High Warlord's Dragonhide Legguards<br> High Warlord's Dragonhide Spaulders<br> High Warlord's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideHelm; ++i;

var fGrandMarshalsDragonhideTunic = new RewardItem("horde","High Warlord's Dragonhide Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsDragonhideTunic.itemHonorPrice = new Array();
fGrandMarshalsDragonhideTunic.itemHonorPrice[0] = 16524
fGrandMarshalsDragonhideTunic.itemTokenPrice = new Array();
fGrandMarshalsDragonhideTunic.itemTokenPrice[0] = new Array(0,30,0,0);
fGrandMarshalsDragonhideTunic.itemStats = new Array();
fGrandMarshalsDragonhideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dragonhide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>322 Armor<br>+18 Strength<br>+18 Agility<br>+31 Stamina<br>+18 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 100 / 100<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Sanctuary (0/5)</span>\
<br> High Warlord's Dragonhide Gloves<br> High Warlord's Dragonhide Helm<br> High Warlord's Dragonhide Legguards<br> High Warlord's Dragonhide Spaulders<br> High Warlord's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDragonhideTunic; ++i;

//DRUID SET 2 ---------------------------
var fGrandMarshalsWyrmhideGloves = new RewardItem("horde","High Warlord's Wyrmhide Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsWyrmhideGloves.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideGloves.itemHonorPrice[0] = 10098
fGrandMarshalsWyrmhideGloves.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideGloves.itemTokenPrice[0] = new Array(20,0,0,0);
fGrandMarshalsWyrmhideGloves.itemStats = new Array();
fGrandMarshalsWyrmhideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Wyrmhide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+22 Stamina<br>+15 Intellect<br>Durability 35 / 35<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wildhide (0/5)</span>\
<br> High Warlord's Wyrmhide Gloves<br> High Warlord's Wyrmhide Helm<br> High Warlord's Wyrmhide Legguards<br> High Warlord's Wyrmhide Spaulders<br> High Warlord's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideGloves; ++i;

var fGrandMarshalsWyrmhideSpaulders = new RewardItem("horde","High Warlord's Wyrmhide Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsWyrmhideSpaulders.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideSpaulders.itemHonorPrice[0] = 10098
fGrandMarshalsWyrmhideSpaulders.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideSpaulders.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsWyrmhideSpaulders.itemStats = new Array();
fGrandMarshalsWyrmhideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Wyrmhide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+33 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wildhide (0/5)</span>\
<br> High Warlord's Wyrmhide Gloves<br> High Warlord's Wyrmhide Helm<br> High Warlord's Wyrmhide Legguards<br> High Warlord's Wyrmhide Spaulders<br> High Warlord's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideSpaulders; ++i;


var fGrandMarshalsWyrmhideLegguards = new RewardItem("horde","High Warlord's Wyrmhide Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsWyrmhideLegguards.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideLegguards.itemHonorPrice[0] = 16065
fGrandMarshalsWyrmhideLegguards.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideLegguards.itemTokenPrice[0] = new Array(0,0,0,30);
fGrandMarshalsWyrmhideLegguards.itemStats = new Array();
fGrandMarshalsWyrmhideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Wyrmhide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>306 Armor<br>+33 Stamina<br>+22 Intellect<br>Durability 75 / 75<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wildhide (0/5)</span>\
<br> High Warlord's Wyrmhide Gloves<br> High Warlord's Wyrmhide Helm<br> High Warlord's Wyrmhide Legguards<br> High Warlord's Wyrmhide Spaulders<br> High Warlord's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideLegguards; ++i;

var fGrandMarshalsWyrmhideHelm = new RewardItem("horde","High Warlord's Wyrmhide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsWyrmhideHelm.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideHelm.itemHonorPrice[0] = 16065
fGrandMarshalsWyrmhideHelm.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideHelm.itemTokenPrice[0] = new Array(30,0,0,0);
fGrandMarshalsWyrmhideHelm.itemStats = new Array();
fGrandMarshalsWyrmhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Wyrmhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+21 Stamina<br>+18 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wildhide (0/5)</span>\
<br> High Warlord's Wyrmhide Gloves<br> High Warlord's Wyrmhide Helm<br> High Warlord's Wyrmhide Legguards<br> High Warlord's Wyrmhide Spaulders<br> High Warlord's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideHelm; ++i;

var fGrandMarshalsWyrmhideTunic = new RewardItem("horde","High Warlord's Wyrmhide Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsWyrmhideTunic.itemHonorPrice = new Array();
fGrandMarshalsWyrmhideTunic.itemHonorPrice[0] = 16524
fGrandMarshalsWyrmhideTunic.itemTokenPrice = new Array();
fGrandMarshalsWyrmhideTunic.itemTokenPrice[0] = new Array(0,30,0,0);
fGrandMarshalsWyrmhideTunic.itemStats = new Array();
fGrandMarshalsWyrmhideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Wyrmhide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>322 Armor<br>+33 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 100 / 100<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wildhide (0/5)</span>\
<br> High Warlord's Wyrmhide Gloves<br> High Warlord's Wyrmhide Helm<br> High Warlord's Wyrmhide Legguards<br> High Warlord's Wyrmhide Spaulders<br> High Warlord's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWyrmhideTunic; ++i;

//DRUID SET 3-------------------------------------------
var fGrandMarshalsKodohideGloves = new RewardItem("horde","High Warlord's Kodohide Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsKodohideGloves.itemHonorPrice = new Array();
fGrandMarshalsKodohideGloves.itemHonorPrice[0] = 10098
fGrandMarshalsKodohideGloves.itemTokenPrice = new Array();
fGrandMarshalsKodohideGloves.itemTokenPrice[0] = new Array(20,0,0,0);
fGrandMarshalsKodohideGloves.itemStats = new Array();
fGrandMarshalsKodohideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Kodohide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+22 Stamina<br>+22 Intellect<br>Durability 35 / 35<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 51.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Refuge (0/5)</span>\
<br> High Warlord's Kodohide Gloves<br> High Warlord's Kodohide Helm<br> High Warlord's Kodohide Legguards<br> High Warlord's Kodohide Spaulders<br> High Warlord's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideGloves; ++i;

var fGrandMarshalsKodohideSpaulders = new RewardItem("horde","High Warlord's Kodohide Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsKodohideSpaulders.itemHonorPrice = new Array();
fGrandMarshalsKodohideSpaulders.itemHonorPrice[0] = 10098
fGrandMarshalsKodohideSpaulders.itemTokenPrice = new Array();
fGrandMarshalsKodohideSpaulders.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsKodohideSpaulders.itemStats = new Array();
fGrandMarshalsKodohideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Kodohide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+33 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Refuge (0/5)</span>\
<br> High Warlord's Kodohide Gloves<br> High Warlord's Kodohide Helm<br> High Warlord's Kodohide Legguards<br> High Warlord's Kodohide Spaulders<br> High Warlord's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideSpaulders; ++i;

var fGrandMarshalsKodohideLegguards = new RewardItem("horde","High Warlord's Kodohide Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsKodohideLegguards.itemHonorPrice = new Array();
fGrandMarshalsKodohideLegguards.itemHonorPrice[0] = 16065
fGrandMarshalsKodohideLegguards.itemTokenPrice = new Array();
fGrandMarshalsKodohideLegguards.itemTokenPrice[0] = new Array(0,0,0,30);
fGrandMarshalsKodohideLegguards.itemStats = new Array();
fGrandMarshalsKodohideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Kodohide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>306 Armor<br>+33 Stamina<br>+28 Intellect<br>Durability 75 / 75<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 64.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Refuge (0/5)</span>\
<br> High Warlord's Kodohide Gloves<br> High Warlord's Kodohide Helm<br> High Warlord's Kodohide Legguards<br> High Warlord's Kodohide Spaulders<br> High Warlord's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideLegguards; ++i;

var fGrandMarshalsKodohideHelm = new RewardItem("horde","High Warlord's Kodohide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsKodohideHelm.itemHonorPrice = new Array();
fGrandMarshalsKodohideHelm.itemHonorPrice[0] = 16065
fGrandMarshalsKodohideHelm.itemTokenPrice = new Array();
fGrandMarshalsKodohideHelm.itemTokenPrice[0] = new Array(30,0,0,0);
fGrandMarshalsKodohideHelm.itemStats = new Array();
fGrandMarshalsKodohideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Kodohide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+30 Stamina<br>+18 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Refuge (0/5)</span>\
<br> High Warlord's Kodohide Gloves<br> High Warlord's Kodohide Helm<br> High Warlord's Kodohide Legguards<br> High Warlord's Kodohide Spaulders<br> High Warlord's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideHelm; ++i;

var fGrandMarshalsKodohideTunic = new RewardItem("horde","High Warlord's Kodohide Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsKodohideTunic.itemHonorPrice = new Array();
fGrandMarshalsKodohideTunic.itemHonorPrice[0] = 16524
fGrandMarshalsKodohideTunic.itemTokenPrice = new Array();
fGrandMarshalsKodohideTunic.itemTokenPrice[0] = new Array(0,30,0,0);
fGrandMarshalsKodohideTunic.itemStats = new Array();
fGrandMarshalsKodohideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Kodohide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>322 Armor<br>+33 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 100 / 100<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Refuge (0/5)</span>\
<br> High Warlord's Kodohide Gloves<br> High Warlord's Kodohide Helm<br> High Warlord's Kodohide Legguards<br> High Warlord's Kodohide Spaulders<br> High Warlord's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsKodohideTunic; ++i;

//HUNTER-----------------------------------------------------------------------------

var fGrandMarshalsChainGauntlets = new RewardItem("horde","High Warlord's Chain Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsChainGauntlets.itemHonorPrice = new Array();
fGrandMarshalsChainGauntlets.itemHonorPrice[1] = 10098
fGrandMarshalsChainGauntlets.itemTokenPrice = new Array();
fGrandMarshalsChainGauntlets.itemTokenPrice[1] = new Array(20,0,0,0);
fGrandMarshalsChainGauntlets.itemStats = new Array();
fGrandMarshalsChainGauntlets.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Chain Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+21 Agility<br>+31 Stamina<br>+6 Intellect<br>Durability 40 / 40<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the damage done by your Multi-Shot by 4%.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Pursuit (0/5)</span>\
<br> High Warlord's Chain Armor<br> High Warlord's Chain Gauntlets<br> High Warlord's Chain Helm<br> High Warlord's Chain Leggings<br> High Warlord's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainGauntlets; ++i;

var fGrandMarshalsChainSpaulders = new RewardItem("horde","High Warlord's Chain Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsChainSpaulders.itemHonorPrice = new Array();
fGrandMarshalsChainSpaulders.itemHonorPrice[1] = 10098
fGrandMarshalsChainSpaulders.itemTokenPrice = new Array();
fGrandMarshalsChainSpaulders.itemTokenPrice[1] = new Array(0,20,0,0);
fGrandMarshalsChainSpaulders.itemStats = new Array();
fGrandMarshalsChainSpaulders.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Chain Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+14 Agility<br>+31 Stamina<br>+4 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Pursuit (0/5)</span>\
<br> High Warlord's Chain Armor<br> High Warlord's Chain Gauntlets<br> High Warlord's Chain Helm<br> High Warlord's Chain Leggings<br> High Warlord's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainSpaulders; ++i;

var fGrandMarshalsChainLeggings = new RewardItem("horde","High Warlord's Chain Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsChainLeggings.itemHonorPrice = new Array();
fGrandMarshalsChainLeggings.itemHonorPrice[1] = 16065
fGrandMarshalsChainLeggings.itemTokenPrice = new Array();
fGrandMarshalsChainLeggings.itemTokenPrice[1] = new Array(0,0,0,30);
fGrandMarshalsChainLeggings.itemStats = new Array();
fGrandMarshalsChainLeggings.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Chain Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+28 Agility<br>+42 Stamina<br>+8 Intellect<br>Durability 90 / 90<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Pursuit (0/5)</span>\
<br> High Warlord's Chain Armor<br> High Warlord's Chain Gauntlets<br> High Warlord's Chain Helm<br> High Warlord's Chain Leggings<br> High Warlord's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainLeggings; ++i;

var fGrandMarshalsChainHelm = new RewardItem("horde","High Warlord's Chain Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsChainHelm.itemHonorPrice = new Array();
fGrandMarshalsChainHelm.itemHonorPrice[1] = 16065
fGrandMarshalsChainHelm.itemTokenPrice = new Array();
fGrandMarshalsChainHelm.itemTokenPrice[1] = new Array(30,0,0,0);
fGrandMarshalsChainHelm.itemStats = new Array();
fGrandMarshalsChainHelm.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Chain Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+20 Agility<br>+30 Stamina<br>+14 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Pursuit (0/5)</span>\
<br> High Warlord's Chain Armor<br> High Warlord's Chain Gauntlets<br> High Warlord's Chain Helm<br> High Warlord's Chain Leggings<br> High Warlord's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainHelm; ++i;

var fGrandMarshalsChainArmor = new RewardItem("horde","High Warlord's Chain Armor","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_11.gif");
fGrandMarshalsChainArmor.itemHonorPrice = new Array();
fGrandMarshalsChainArmor.itemHonorPrice[1] = 16524
fGrandMarshalsChainArmor.itemTokenPrice = new Array();
fGrandMarshalsChainArmor.itemTokenPrice[1] = new Array(0,30,0,0);
fGrandMarshalsChainArmor.itemStats = new Array();
fGrandMarshalsChainArmor.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Chain Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+20 Agility<br>+42 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Pursuit (0/5)</span>\
<br> High Warlord's Chain Armor<br> High Warlord's Chain Gauntlets<br> High Warlord's Chain Helm<br> High Warlord's Chain Leggings<br> High Warlord's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsChainArmor; ++i;

//MAGE---------------------------------------------------------------------
var fGrandMarshalsSilkHandguards = new RewardItem("horde","High Warlord's Silk Handguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_19.gif");
fGrandMarshalsSilkHandguards.itemHonorPrice = new Array();
fGrandMarshalsSilkHandguards.itemHonorPrice[2] = 10098
fGrandMarshalsSilkHandguards.itemTokenPrice = new Array();
fGrandMarshalsSilkHandguards.itemTokenPrice[2] = new Array(20,0,0,0);
fGrandMarshalsSilkHandguards.itemStats = new Array();
fGrandMarshalsSilkHandguards.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Silk Handguards</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+33 Stamina<br>+12 Intellect<br>Durability 30 / 30<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of your Fire Blast spell by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Regalia (0/5)</span>\
<br> High Warlord's Silk Amice<br> High Warlord's Silk Cowl<br> High Warlord's Silk Handguards<br> High Warlord's Silk Raiment<br> High Warlord's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkHandguards; ++i;

var fGrandMarshalsSilkAmice = new RewardItem("horde","High Warlord's Silk Amice","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_19.gif");
fGrandMarshalsSilkAmice.itemHonorPrice = new Array();
fGrandMarshalsSilkAmice.itemHonorPrice[2] = 10098
fGrandMarshalsSilkAmice.itemTokenPrice = new Array();
fGrandMarshalsSilkAmice.itemTokenPrice[2] = new Array(0,20,0,0);
fGrandMarshalsSilkAmice.itemStats = new Array();
fGrandMarshalsSilkAmice.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Silk Amice</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+21 Stamina<br>+16 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Regalia (0/5)</span>\
<br> High Warlord's Silk Amice<br> High Warlord's Silk Cowl<br> High Warlord's Silk Handguards<br> High Warlord's Silk Raiment<br> High Warlord's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkAmice; ++i;

var fGrandMarshalsSilkTrousers = new RewardItem("horde","High Warlord's Silk Trousers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_07.gif");
fGrandMarshalsSilkTrousers.itemHonorPrice = new Array();
fGrandMarshalsSilkTrousers.itemHonorPrice[2] = 16065
fGrandMarshalsSilkTrousers.itemTokenPrice = new Array();
fGrandMarshalsSilkTrousers.itemTokenPrice[2] = new Array(0,0,0,30);
fGrandMarshalsSilkTrousers.itemStats = new Array();
fGrandMarshalsSilkTrousers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Silk Trousers</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+42 Stamina<br>+22 Intellect<br>Durability 65 / 65<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Regalia (0/5)</span>\
<br> High Warlord's Silk Amice<br> High Warlord's Silk Cowl<br> High Warlord's Silk Handguards<br> High Warlord's Silk Raiment<br> High Warlord's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkTrousers; ++i;

var fGrandMarshalsSilkCowl = new RewardItem("horde","High Warlord's Silk Cowl","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_08.gif");
fGrandMarshalsSilkCowl.itemHonorPrice = new Array();
fGrandMarshalsSilkCowl.itemHonorPrice[2] = 16065
fGrandMarshalsSilkCowl.itemTokenPrice = new Array();
fGrandMarshalsSilkCowl.itemTokenPrice[2] = new Array(30,0,0,0);
fGrandMarshalsSilkCowl.itemStats = new Array();
fGrandMarshalsSilkCowl.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Silk Cowl</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+39 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Regalia (0/5)</span>\
<br> High Warlord's Silk Amice<br> High Warlord's Silk Cowl<br> High Warlord's Silk Handguards<br> High Warlord's Silk Raiment<br> High Warlord's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkCowl; ++i;

var fGrandMarshalsSilkRaiment = new RewardItem("horde","High Warlord's Silk Raiment","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Leather_01.gif&reason=external-or-uncollected-resource");
fGrandMarshalsSilkRaiment.itemHonorPrice = new Array();
fGrandMarshalsSilkRaiment.itemHonorPrice[2] = 16524
fGrandMarshalsSilkRaiment.itemTokenPrice = new Array();
fGrandMarshalsSilkRaiment.itemTokenPrice[2] = new Array(0,30,0,0);
fGrandMarshalsSilkRaiment.itemStats = new Array();
fGrandMarshalsSilkRaiment.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Silk Raiment</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+42 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 80 / 80<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Regalia (0/5)</span>\
<br> High Warlord's Silk Amice<br> High Warlord's Silk Cowl<br> High Warlord's Silk Handguards<br> High Warlord's Silk Raiment<br> High Warlord's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSilkRaiment; ++i;

//PALADIN-----------------------------------------------------
var fGrandMarshalsLamellarGauntlets = new RewardItem("horde","High Warlord's Lamellar Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsLamellarGauntlets.itemHonorPrice = new Array();
fGrandMarshalsLamellarGauntlets.itemHonorPrice[3] = 10098
fGrandMarshalsLamellarGauntlets.itemTokenPrice = new Array();
fGrandMarshalsLamellarGauntlets.itemTokenPrice[3] = new Array(20,0,0,0);
fGrandMarshalsLamellarGauntlets.itemStats = new Array();
fGrandMarshalsLamellarGauntlets.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Lamellar Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+36 Stamina<br>+13 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the Holy damage bonus of your Judgement of the Crusader by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Aegis (0/5)</span>\
<br> High Warlord's Lamellar Chestpiece<br> High Warlord's Lamellar Gauntlets<br> High Warlord's Lamellar Helm<br> High Warlord's Lamellar Legguards<br> High Warlord's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarGauntlets; ++i;

var fGrandMarshalsLamellarShoulders = new RewardItem("horde","High Warlord's Lamellar Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsLamellarShoulders.itemHonorPrice = new Array();
fGrandMarshalsLamellarShoulders.itemHonorPrice[3] = 10098
fGrandMarshalsLamellarShoulders.itemTokenPrice = new Array();
fGrandMarshalsLamellarShoulders.itemTokenPrice[3] = new Array(0,20,0,0);
fGrandMarshalsLamellarShoulders.itemStats = new Array();
fGrandMarshalsLamellarShoulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Lamellar Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+36 Stamina<br>+12 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Aegis (0/5)</span>\
<br> High Warlord's Lamellar Chestpiece<br> High Warlord's Lamellar Gauntlets<br> High Warlord's Lamellar Helm<br> High Warlord's Lamellar Legguards<br> High Warlord's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarShoulders; ++i;

var fGrandMarshalsLamellarLegguards = new RewardItem("horde","High Warlord's Lamellar Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsLamellarLegguards.itemHonorPrice = new Array();
fGrandMarshalsLamellarLegguards.itemHonorPrice[3] = 16065
fGrandMarshalsLamellarLegguards.itemTokenPrice = new Array();
fGrandMarshalsLamellarLegguards.itemTokenPrice[3] = new Array(0,0,0,30);
fGrandMarshalsLamellarLegguards.itemStats = new Array();
fGrandMarshalsLamellarLegguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Lamellar Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+48 Stamina<br>+15 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Aegis (0/5)</span>\
<br> High Warlord's Lamellar Chestpiece<br> High Warlord's Lamellar Gauntlets<br> High Warlord's Lamellar Helm<br> High Warlord's Lamellar Legguards<br> High Warlord's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarLegguards; ++i;

var fGrandMarshalsLamellarHelm = new RewardItem("horde","High Warlord's Lamellar Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsLamellarHelm.itemHonorPrice = new Array();
fGrandMarshalsLamellarHelm.itemHonorPrice[3] = 16065
fGrandMarshalsLamellarHelm.itemTokenPrice = new Array();
fGrandMarshalsLamellarHelm.itemTokenPrice[3] = new Array(30,0,0,0);
fGrandMarshalsLamellarHelm.itemStats = new Array();
fGrandMarshalsLamellarHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Lamellar Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+44 Stamina<br>+11 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Aegis (0/5)</span>\
<br> High Warlord's Lamellar Chestpiece<br> High Warlord's Lamellar Gauntlets<br> High Warlord's Lamellar Helm<br> High Warlord's Lamellar Legguards<br> High Warlord's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarHelm; ++i;

var fGrandMarshalsLamellarChestpiece = new RewardItem("horde","High Warlord's Lamellar Chestpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGrandMarshalsLamellarChestpiece.itemHonorPrice = new Array();
fGrandMarshalsLamellarChestpiece.itemHonorPrice[3] = 16524
fGrandMarshalsLamellarChestpiece.itemTokenPrice = new Array();
fGrandMarshalsLamellarChestpiece.itemTokenPrice[3] = new Array(0,30,0,0);
fGrandMarshalsLamellarChestpiece.itemStats = new Array();
fGrandMarshalsLamellarChestpiece.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Lamellar Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+48 Stamina<br>+12 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Aegis (0/5)</span>\
<br> High Warlord's Lamellar Chestpiece<br> High Warlord's Lamellar Gauntlets<br> High Warlord's Lamellar Helm<br> High Warlord's Lamellar Legguards<br> High Warlord's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLamellarChestpiece; ++i;

var fGrandMarshalsScaledGauntlets = new RewardItem("horde","High Warlord's Scaled Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsScaledGauntlets.itemHonorPrice = new Array();
fGrandMarshalsScaledGauntlets.itemHonorPrice[3] = 10098
fGrandMarshalsScaledGauntlets.itemTokenPrice = new Array();
fGrandMarshalsScaledGauntlets.itemTokenPrice[3] = new Array(20,0,0,0);
fGrandMarshalsScaledGauntlets.itemStats = new Array();
fGrandMarshalsScaledGauntlets.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Scaled Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+19 Strength<br>+25 Stamina<br>+12 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the Holy damage bonus of your Judgement of the Crusader by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vindication (0/5)</span>\
<br> High Warlord's Scaled Chestpiece<br> High Warlord's Scaled Gauntlets<br> High Warlord's Scaled Helm<br> High Warlord's Scaled Legguards<br> High Warlord's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledGauntlets; ++i;

var fGrandMarshalsScaledShoulders = new RewardItem("horde","High Warlord's Scaled Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsScaledShoulders.itemHonorPrice = new Array();
fGrandMarshalsScaledShoulders.itemHonorPrice[3] = 10098
fGrandMarshalsScaledShoulders.itemTokenPrice = new Array();
fGrandMarshalsScaledShoulders.itemTokenPrice[3] = new Array(0,20,0,0);
fGrandMarshalsScaledShoulders.itemStats = new Array();
fGrandMarshalsScaledShoulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Scaled Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+19 Strength<br>+33 Stamina<br>+8 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vindication (0/5)</span>\
<br> High Warlord's Scaled Chestpiece<br> High Warlord's Scaled Gauntlets<br> High Warlord's Scaled Helm<br> High Warlord's Scaled Legguards<br> High Warlord's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledShoulders; ++i;

var fGrandMarshalsScaledLegguards = new RewardItem("horde","High Warlord's Scaled Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsScaledLegguards.itemHonorPrice = new Array();
fGrandMarshalsScaledLegguards.itemHonorPrice[3] = 16065
fGrandMarshalsScaledLegguards.itemTokenPrice = new Array();
fGrandMarshalsScaledLegguards.itemTokenPrice[3] = new Array(0,0,0,30);
fGrandMarshalsScaledLegguards.itemStats = new Array();
fGrandMarshalsScaledLegguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Scaled Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+24 Strength<br>+42 Stamina<br>+16 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vindication (0/5)</span>\
<br> High Warlord's Scaled Chestpiece<br> High Warlord's Scaled Gauntlets<br> High Warlord's Scaled Helm<br> High Warlord's Scaled Legguards<br> High Warlord's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledLegguards; ++i;

var fGrandMarshalsScaledHelm = new RewardItem("horde","High Warlord's Scaled Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsScaledHelm.itemHonorPrice = new Array();
fGrandMarshalsScaledHelm.itemHonorPrice[3] = 16065
fGrandMarshalsScaledHelm.itemTokenPrice = new Array();
fGrandMarshalsScaledHelm.itemTokenPrice[3] = new Array(30,0,0,0);
fGrandMarshalsScaledHelm.itemStats = new Array();
fGrandMarshalsScaledHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Scaled Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+20 Strength<br>+30 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vindication (0/5)</span>\
<br> High Warlord's Scaled Chestpiece<br> High Warlord's Scaled Gauntlets<br> High Warlord's Scaled Helm<br> High Warlord's Scaled Legguards<br> High Warlord's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledHelm; ++i;

var fGrandMarshalsScaledChestpiece = new RewardItem("horde","High Warlord's Scaled Chestpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGrandMarshalsScaledChestpiece.itemHonorPrice = new Array();
fGrandMarshalsScaledChestpiece.itemHonorPrice[3] = 16524
fGrandMarshalsScaledChestpiece.itemTokenPrice = new Array();
fGrandMarshalsScaledChestpiece.itemTokenPrice[3] = new Array(0,30,0,0);
fGrandMarshalsScaledChestpiece.itemStats = new Array();
fGrandMarshalsScaledChestpiece.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Scaled Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+24 Strength<br>+42 Stamina<br>+12 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vindication (0/5)</span>\
<br> High Warlord's Scaled Chestpiece<br> High Warlord's Scaled Gauntlets<br> High Warlord's Scaled Helm<br> High Warlord's Scaled Legguards<br> High Warlord's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsScaledChestpiece; ++i;

var fGrandMarshalsOrnamentedChestplate = new RewardItem("horde","High Warlord's Ornamented Chestplate","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGrandMarshalsOrnamentedChestplate.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedChestplate.itemHonorPrice[3] = 16524
fGrandMarshalsOrnamentedChestplate.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedChestplate.itemTokenPrice[3] = new Array(0,30,0,0);
fGrandMarshalsOrnamentedChestplate.itemStats = new Array();
fGrandMarshalsOrnamentedChestplate.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ornamented Chestplate</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+37 Stamina<br>+24 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 18.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Redemption (0/5)</span>\
<br> High Warlord's Ornamented Chestplate<br> High Warlord's Ornamented Gloves<br> High Warlord's Ornamented Headguard<br> High Warlord's Ornamented Leggings<br> High Warlord's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedChestplate; ++i;

var fGrandMarshalsOrnamentedGloves = new RewardItem("horde","High Warlord's Ornamented Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsOrnamentedGloves.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedGloves.itemHonorPrice[3] = 10098
fGrandMarshalsOrnamentedGloves.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedGloves.itemTokenPrice[3] = new Array(20,0,0,0);
fGrandMarshalsOrnamentedGloves.itemStats = new Array();
fGrandMarshalsOrnamentedGloves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ornamented Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+30 Stamina<br>+20 Intellect<br>Durability 45 / 45<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the Holy damage bonus of your Judgement of the Crusader by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Redemption (0/5)</span>\
<br> High Warlord's Ornamented Chestplate<br> High Warlord's Ornamented Gloves<br> High Warlord's Ornamented Headguard<br>\
High Warlord's Ornamented Leggings<br> High Warlord's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedGloves; ++i;

var fGrandMarshalsOrnamentedHeadguard = new RewardItem("horde","High Warlord's Ornamented Headguard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsOrnamentedHeadguard.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedHeadguard.itemHonorPrice[3] = 16065
fGrandMarshalsOrnamentedHeadguard.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedHeadguard.itemTokenPrice[3] = new Array(30,0,0,0);
fGrandMarshalsOrnamentedHeadguard.itemStats = new Array();
fGrandMarshalsOrnamentedHeadguard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ornamented Headguard</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+34 Stamina<br>+22 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 35.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Redemption (0/5)</span>\
<br> High Warlord's Ornamented Chestplate<br> High Warlord's Ornamented Gloves<br> High Warlord's Ornamented Headguard<br> High Warlord's Ornamented Leggings<br> High Warlord's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedHeadguard; ++i;


var fGrandMarshalsOrnamentedLeggings = new RewardItem("horde","High Warlord's Ornamented Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsOrnamentedLeggings.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedLeggings.itemHonorPrice[3] = 16065
fGrandMarshalsOrnamentedLeggings.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedLeggings.itemTokenPrice[3] = new Array(0,0,0,30);
fGrandMarshalsOrnamentedLeggings.itemStats = new Array();
fGrandMarshalsOrnamentedLeggings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ornamented Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+39 Stamina<br>+26 Intellect<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 53.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Redemption (0/5)</span>\
<br> High Warlord's Ornamented Chestplate<br> High Warlord's Ornamented Gloves<br> High Warlord's Ornamented Headguard<br> High Warlord's Ornamented Leggings<br> High Warlord's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedLeggings; ++i;

var fGrandMarshalsOrnamentedSpaulders = new RewardItem("horde","High Warlord's Ornamented Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsOrnamentedSpaulders.itemHonorPrice = new Array();
fGrandMarshalsOrnamentedSpaulders.itemHonorPrice[3] = 10098
fGrandMarshalsOrnamentedSpaulders.itemTokenPrice = new Array();
fGrandMarshalsOrnamentedSpaulders.itemTokenPrice[3] = new Array(0,20,0,0);
fGrandMarshalsOrnamentedSpaulders.itemStats = new Array();
fGrandMarshalsOrnamentedSpaulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ornamented Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+30 Stamina<br>+19 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Redemption (0/5)</span>\
<br> High Warlord's Ornamented Chestplate<br> High Warlord's Ornamented Gloves<br> High Warlord's Ornamented Headguard<br> High Warlord's Ornamented Leggings<br> High Warlord's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsOrnamentedSpaulders; ++i;

//PRIEST---------------------------------------------------------------------------------------

//PRIEST SET 1-----
var fGrandMarshalsSatinGloves = new RewardItem("horde","High Warlord's Satin Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fGrandMarshalsSatinGloves.itemHonorPrice = new Array();
fGrandMarshalsSatinGloves.itemHonorPrice[4] = 10098
fGrandMarshalsSatinGloves.itemTokenPrice = new Array();
fGrandMarshalsSatinGloves.itemTokenPrice[4] = new Array(20,0,0,0);
fGrandMarshalsSatinGloves.itemStats = new Array();
fGrandMarshalsSatinGloves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Satin Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+33 Stamina<br>+15 Intellect<br>Durability 30 / 30<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the duration of your Psychic Scream spell by 1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Raiment (0/5)</span>\
<br> High Warlord's Satin Gloves<br> High Warlord's Satin Hood<br> High Warlord's Satin Leggings<br> High Warlord's Satin Mantle<br> High Warlord's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinGloves; ++i;

var fGrandMarshalsSatinMantle = new RewardItem("horde","High Warlord's Satin Mantle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fGrandMarshalsSatinMantle.itemHonorPrice = new Array();
fGrandMarshalsSatinMantle.itemHonorPrice[4] = 10098
fGrandMarshalsSatinMantle.itemTokenPrice = new Array();
fGrandMarshalsSatinMantle.itemTokenPrice[4] = new Array(0,20,0,0);
fGrandMarshalsSatinMantle.itemStats = new Array();
fGrandMarshalsSatinMantle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Satin Mantle</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+33 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Raiment (0/5)</span>\
<br> High Warlord's Satin Gloves<br> High Warlord's Satin Hood<br> High Warlord's Satin Leggings<br> High Warlord's Satin Mantle<br> High Warlord's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinMantle; ++i;

var fGrandMarshalsSatinLeggings = new RewardItem("horde","High Warlord's Satin Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsSatinLeggings.itemHonorPrice = new Array();
fGrandMarshalsSatinLeggings.itemHonorPrice[4] = 16065
fGrandMarshalsSatinLeggings.itemTokenPrice = new Array();
fGrandMarshalsSatinLeggings.itemTokenPrice[4] = new Array(0,0,0,30);
fGrandMarshalsSatinLeggings.itemStats = new Array();
fGrandMarshalsSatinLeggings.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Satin Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+46 Stamina<br>+23 Intellect<br>Durability 65 / 65<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Raiment (0/5)</span>\
<br> High Warlord's Satin Gloves<br> High Warlord's Satin Hood<br> High Warlord's Satin Leggings<br> High Warlord's Satin Mantle<br> High Warlord's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinLeggings; ++i;

var fGrandMarshalsSatinHood = new RewardItem("horde","High Warlord's Satin Hood ","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsSatinHood.itemHonorPrice = new Array();
fGrandMarshalsSatinHood.itemHonorPrice[4] = 16065
fGrandMarshalsSatinHood.itemTokenPrice = new Array();
fGrandMarshalsSatinHood.itemTokenPrice[4] = new Array(30,0,0,0);
fGrandMarshalsSatinHood.itemStats = new Array();
fGrandMarshalsSatinHood.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Satin Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+46 Stamina<br>+19 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 18.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Raiment (0/5)</span>\
<br> High Warlord's Satin Gloves<br> High Warlord's Satin Hood<br> High Warlord's Satin Leggings<br> High Warlord's Satin Mantle<br> High Warlord's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinHood; ++i;

var fGrandMarshalsSatinRobe = new RewardItem("horde","High Warlord's Satin Robe","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Cloth_43.gif&reason=external-or-uncollected-resource");
fGrandMarshalsSatinRobe.itemHonorPrice = new Array();
fGrandMarshalsSatinRobe.itemHonorPrice[4] = 16524
fGrandMarshalsSatinRobe.itemTokenPrice = new Array();
fGrandMarshalsSatinRobe.itemTokenPrice[4] = new Array(0,30,0,0);
fGrandMarshalsSatinRobe.itemStats = new Array();
fGrandMarshalsSatinRobe.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Satin Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+46 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 80 / 80<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Raiment (0/5)</span>\
<br> High Warlord's Satin Gloves<br> High Warlord's Satin Hood<br> High Warlord's Satin Leggings<br> High Warlord's Satin Mantle<br> High Warlord's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSatinRobe; ++i;

//PRIEST SET 2 ------------
var fGrandMarshalsMoonclothCowl = new RewardItem("horde","High Warlord's Mooncloth Cowl","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsMoonclothCowl.itemHonorPrice = new Array();
fGrandMarshalsMoonclothCowl.itemHonorPrice[4] = 16065
fGrandMarshalsMoonclothCowl.itemTokenPrice = new Array();
fGrandMarshalsMoonclothCowl.itemTokenPrice[4] = new Array(30,0,0,0);
fGrandMarshalsMoonclothCowl.itemStats = new Array();
fGrandMarshalsMoonclothCowl.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mooncloth Cowl</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+40 Stamina<br>+26 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Investiture (0/5)</span>\
<br> High Warlord's Mooncloth Cowl<br> High Warlord's Mooncloth Legguards<br> High Warlord's Mooncloth Mitts<br> High Warlord's Mooncloth Shoulderpads<br> High Warlord's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothCowl; ++i;

var fGrandMarshalsMoonclothLegguards = new RewardItem("horde","High Warlord's Mooncloth Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsMoonclothLegguards.itemHonorPrice = new Array();
fGrandMarshalsMoonclothLegguards.itemHonorPrice[4] = 16065
fGrandMarshalsMoonclothLegguards.itemTokenPrice = new Array();
fGrandMarshalsMoonclothLegguards.itemTokenPrice[4] = new Array(0,0,0,30);
fGrandMarshalsMoonclothLegguards.itemStats = new Array();
fGrandMarshalsMoonclothLegguards.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mooncloth Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+42 Stamina<br>+28 Intellect<br>Durability 65 / 65<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Investiture (0/5)</span>\
<br> High Warlord's Mooncloth Cowl<br> High Warlord's Mooncloth Legguards<br> High Warlord's Mooncloth Mitts<br> High Warlord's Mooncloth Shoulderpads<br> High Warlord's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothLegguards; ++i;

var fGrandMarshalsMoonclothMitts = new RewardItem("horde","High Warlord's Mooncloth Mitts","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fGrandMarshalsMoonclothMitts.itemHonorPrice = new Array();
fGrandMarshalsMoonclothMitts.itemHonorPrice[4] = 10098
fGrandMarshalsMoonclothMitts.itemTokenPrice = new Array();
fGrandMarshalsMoonclothMitts.itemTokenPrice[4] = new Array(20,0,0,0);
fGrandMarshalsMoonclothMitts.itemStats = new Array();
fGrandMarshalsMoonclothMitts.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mooncloth Mitts</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+33 Stamina<br>+15 Intellect<br>Durability 30 / 30<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the duration of your Psychic Scream spell by 1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Investiture (0/5)</span>\
<br> High Warlord's Mooncloth Cowl<br> High Warlord's Mooncloth Legguards<br> High Warlord's Mooncloth Mitts<br> High Warlord's Mooncloth Shoulderpads<br> High Warlord's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothMitts; ++i;

var fGrandMarshalsMoonclothShoulderpads = new RewardItem("horde","High Warlord's Mooncloth Shoulderpads","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fGrandMarshalsMoonclothShoulderpads.itemHonorPrice = new Array();
fGrandMarshalsMoonclothShoulderpads.itemHonorPrice[4] = 10098
fGrandMarshalsMoonclothShoulderpads.itemTokenPrice = new Array();
fGrandMarshalsMoonclothShoulderpads.itemTokenPrice[4] = new Array(0,20,0,0);
fGrandMarshalsMoonclothShoulderpads.itemStats = new Array();
fGrandMarshalsMoonclothShoulderpads.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mooncloth Shoulderpads</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+30 Stamina<br>+20 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Investiture (0/5)</span>\
<br> High Warlord's Mooncloth Cowl<br> High Warlord's Mooncloth Legguards<br> High Warlord's Mooncloth Mitts<br> High Warlord's Mooncloth Shoulderpads<br> High Warlord's Mooncloth Vestments<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothShoulderpads; ++i;

var fGrandMarshalsMoonclothVestments = new RewardItem("horde","High Warlord's Mooncloth Vestments","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Cloth_43.gif&reason=external-or-uncollected-resource");
fGrandMarshalsMoonclothVestments.itemHonorPrice = new Array();
fGrandMarshalsMoonclothVestments.itemHonorPrice[4] = 16524
fGrandMarshalsMoonclothVestments.itemTokenPrice = new Array();
fGrandMarshalsMoonclothVestments.itemTokenPrice[4] = new Array(0,30,0,0);
fGrandMarshalsMoonclothVestments.itemStats = new Array();
fGrandMarshalsMoonclothVestments.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mooncloth Vestments</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+39 Stamina<br>+25 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 80 / 80<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 51.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Investiture (0/5)</span>\
<br> High Warlord's Mooncloth Cowl<br> High Warlord's Mooncloth Legguards<br> High Warlord's Mooncloth Mitts<br> High Warlord's Mooncloth Shoulderpads<br> High Warlord's Mooncloth Vestments<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span><br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMoonclothVestments; ++i;

//ROGUE-----------------------------------------------
var fGrandMarshalsLeatherGloves = new RewardItem("horde","High Warlord's Leather Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGrandMarshalsLeatherGloves.itemHonorPrice = new Array();
fGrandMarshalsLeatherGloves.itemHonorPrice[5] = 10098
fGrandMarshalsLeatherGloves.itemTokenPrice = new Array();
fGrandMarshalsLeatherGloves.itemTokenPrice[5] = new Array(20,0,0,0);
fGrandMarshalsLeatherGloves.itemStats = new Array();
fGrandMarshalsLeatherGloves.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Leather Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>183 Armor<br>+21 Agility<br>+31 Stamina<br>Durability 35 / 35<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Causes your Deadly Throw ability to interrupt spellcasting and prevent any spell in that school from being cast for 3 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vestments (0/5)</span>\
<br> High Warlord's Leather Gloves<br> High Warlord's Leather Helm<br> High Warlord's Leather Legguards<br> High Warlord's Leather Spaulders<br> High Warlord's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherGloves; ++i;

var fGrandMarshalsLeatherSpaulders = new RewardItem("horde","High Warlord's Leather Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGrandMarshalsLeatherSpaulders.itemHonorPrice = new Array();
fGrandMarshalsLeatherSpaulders.itemHonorPrice[5] = 10098
fGrandMarshalsLeatherSpaulders.itemTokenPrice = new Array();
fGrandMarshalsLeatherSpaulders.itemTokenPrice[5] = new Array(0,20,0,0);
fGrandMarshalsLeatherSpaulders.itemStats = new Array();
fGrandMarshalsLeatherSpaulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Leather Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>219 Armor<br>+13 Agility<br>+31 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vestments (0/5)</span>\
<br> High Warlord's Leather Gloves<br> High Warlord's Leather Helm<br> High Warlord's Leather Legguards<br> High Warlord's Leather Spaulders<br> High Warlord's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherSpaulders; ++i;

var fGrandMarshalsLeatherLegguards = new RewardItem("horde","High Warlord's Leather Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGrandMarshalsLeatherLegguards.itemHonorPrice = new Array();
fGrandMarshalsLeatherLegguards.itemHonorPrice[5] = 16065
fGrandMarshalsLeatherLegguards.itemTokenPrice = new Array();
fGrandMarshalsLeatherLegguards.itemTokenPrice[5] = new Array(0,0,0,30);
fGrandMarshalsLeatherLegguards.itemStats = new Array();
fGrandMarshalsLeatherLegguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Leather Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>256 Armor<br>+28 Agility<br>+42 Stamina<br>Durability 75 / 75<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vestments (0/5)</span>\
<br> High Warlord's Leather Gloves<br> High Warlord's Leather Helm<br> High Warlord's Leather Legguards<br> High Warlord's Leather Spaulders<br> High Warlord's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherLegguards; ++i;

var fGrandMarshalsLeatherHelm = new RewardItem("horde","High Warlord's Leather Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGrandMarshalsLeatherHelm.itemHonorPrice = new Array();
fGrandMarshalsLeatherHelm.itemHonorPrice[5] = 16065
fGrandMarshalsLeatherHelm.itemTokenPrice = new Array();
fGrandMarshalsLeatherHelm.itemTokenPrice[5] = new Array(30,0,0,0);
fGrandMarshalsLeatherHelm.itemStats = new Array();
fGrandMarshalsLeatherHelm.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Leather Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>237 Armor<br>+20 Agility<br>+36 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vestments (0/5)</span>\
<br> High Warlord's Leather Gloves<br> High Warlord's Leather Helm<br> High Warlord's Leather Legguards<br> High Warlord's Leather Spaulders<br> High Warlord's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherHelm; ++i;

var fGrandMarshalsLeatherTunic = new RewardItem("horde","High Warlord's Leather Tunic","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGrandMarshalsLeatherTunic.itemHonorPrice = new Array();
fGrandMarshalsLeatherTunic.itemHonorPrice[5] = 16524
fGrandMarshalsLeatherTunic.itemTokenPrice = new Array();
fGrandMarshalsLeatherTunic.itemTokenPrice[5] = new Array(0,30,0,0);
fGrandMarshalsLeatherTunic.itemStats = new Array();
fGrandMarshalsLeatherTunic.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Leather Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>292 Armor<br>+20 Agility<br>+42 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 100 / 100<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Vestments (0/5)</span>\
<br> High Warlord's Leather Gloves<br> High Warlord's Leather Helm<br> High Warlord's Leather Legguards<br> High Warlord's Leather Spaulders<br> High Warlord's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeatherTunic; ++i;

//SHAMAN---------------------------------------------------------------------------------------------

var fGrandMarshalsLinkedGauntlets = new RewardItem("horde","High Warlord's Linked Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsLinkedGauntlets.itemHonorPrice = new Array();
fGrandMarshalsLinkedGauntlets.itemHonorPrice[6] = 10098
fGrandMarshalsLinkedGauntlets.itemTokenPrice = new Array();
fGrandMarshalsLinkedGauntlets.itemTokenPrice[6] = new Array(20,0,0,0);
fGrandMarshalsLinkedGauntlets.itemStats = new Array();
fGrandMarshalsLinkedGauntlets.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Linked Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+21 Strength<br>+33 Stamina<br>Durability 40 / 40<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the damage done by your Lightning Shield by 8%.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Earthshaker (0/5)</span>\
<br> High Warlord's Linked Armor<br> High Warlord's Linked Gauntlets<br> High Warlord's Linked Helm<br> High Warlord's Linked Leggings<br> High Warlord's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedGauntlets; ++i;

var fGrandMarshalsLinkedSpaulders = new RewardItem("horde","High Warlord's Linked Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsLinkedSpaulders.itemHonorPrice = new Array();
fGrandMarshalsLinkedSpaulders.itemHonorPrice[6] = 10098
fGrandMarshalsLinkedSpaulders.itemTokenPrice = new Array();
fGrandMarshalsLinkedSpaulders.itemTokenPrice[6] = new Array(0,20,0,0);
fGrandMarshalsLinkedSpaulders.itemStats = new Array();
fGrandMarshalsLinkedSpaulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Linked Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+13 Strength<br>+33 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Earthshaker (0/5)</span>\
<br> High Warlord's Linked Armor<br> High Warlord's Linked Gauntlets<br> High Warlord's Linked Helm<br> High Warlord's Linked Leggings<br> High Warlord's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedSpaulders; ++i;


var fGrandMarshalsLinkedLeggings = new RewardItem("horde","High Warlord's Linked Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsLinkedLeggings.itemHonorPrice = new Array();
fGrandMarshalsLinkedLeggings.itemHonorPrice[6] = 16065
fGrandMarshalsLinkedLeggings.itemTokenPrice = new Array();
fGrandMarshalsLinkedLeggings.itemTokenPrice[6] = new Array(0,0,0,30);
fGrandMarshalsLinkedLeggings.itemStats = new Array();
fGrandMarshalsLinkedLeggings.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Linked Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+22 Strength<br>+42 Stamina<br>+22 Intellect<br>Durability 90 / 90<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Earthshaker (0/5)</span>\
<br> High Warlord's Linked Armor<br> High Warlord's Linked Gauntlets<br> High Warlord's Linked Helm<br> High Warlord's Linked Leggings<br> High Warlord's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedLeggings; ++i;

var fGrandMarshalsLinkedHelm = new RewardItem("horde","High Warlord's Linked Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsLinkedHelm.itemHonorPrice = new Array();
fGrandMarshalsLinkedHelm.itemHonorPrice[6] = 16065
fGrandMarshalsLinkedHelm.itemTokenPrice = new Array();
fGrandMarshalsLinkedHelm.itemTokenPrice[6] = new Array(30,0,0,0);
fGrandMarshalsLinkedHelm.itemStats = new Array();
fGrandMarshalsLinkedHelm.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Linked Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+20 Strength<br>+30 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Earthshaker (0/5)</span>\
<br> High Warlord's Linked Armor<br> High Warlord's Linked Gauntlets<br> High Warlord's Linked Helm<br> High Warlord's Linked Leggings<br> High Warlord's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedHelm; ++i;

var fGrandMarshalsLinkedArmor = new RewardItem("horde","High Warlord's Linked Armor","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGrandMarshalsLinkedArmor.itemHonorPrice = new Array();
fGrandMarshalsLinkedArmor.itemHonorPrice[6] = 16524
fGrandMarshalsLinkedArmor.itemTokenPrice = new Array();
fGrandMarshalsLinkedArmor.itemTokenPrice[6] = new Array(0,30,0,0);
fGrandMarshalsLinkedArmor.itemStats = new Array();
fGrandMarshalsLinkedArmor.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Linked Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+12 Strength<br>+42 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Earthshaker (0/5)</span>\
<br> High Warlord's Linked Armor<br> High Warlord's Linked Gauntlets<br> High Warlord's Linked Helm<br> High Warlord's Linked Leggings<br> High Warlord's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLinkedArmor; ++i;


//SHAMAN SET 2---------------
var fGrandMarshalsMailGauntlets = new RewardItem("horde","High Warlord's Mail Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsMailGauntlets.itemHonorPrice = new Array();
fGrandMarshalsMailGauntlets.itemHonorPrice[6] = 10098
fGrandMarshalsMailGauntlets.itemTokenPrice = new Array();
fGrandMarshalsMailGauntlets.itemTokenPrice[6] = new Array(20,0,0,0);
fGrandMarshalsMailGauntlets.itemStats = new Array();
fGrandMarshalsMailGauntlets.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mail Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+33 Stamina<br>+13 Intellect<br>Durability 40 / 40<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of all Shock spells by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Thunderfist (0/5)</span>\
<br> High Warlord's Mail Armor<br> High Warlord's Mail Gauntlets<br> High Warlord's Mail Helm<br> High Warlord's Mail Leggings<br> High Warlord's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailGauntlets; ++i;

var fGrandMarshalsMailSpaulders = new RewardItem("horde","High Warlord's Mail Spaulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsMailSpaulders.itemHonorPrice = new Array();
fGrandMarshalsMailSpaulders.itemHonorPrice[6] = 10098
fGrandMarshalsMailSpaulders.itemTokenPrice = new Array();
fGrandMarshalsMailSpaulders.itemTokenPrice[6] = new Array(0,20,0,0);
fGrandMarshalsMailSpaulders.itemStats = new Array();
fGrandMarshalsMailSpaulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mail Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+33 Stamina<br>+13 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Thunderfist (0/5)</span>\
<br> High Warlord's Mail Armor<br> High Warlord's Mail Gauntlets<br> High Warlord's Mail Helm<br> High Warlord's Mail Leggings<br> High Warlord's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailSpaulders; ++i;

var fGrandMarshalsMailLeggings = new RewardItem("horde","High Warlord's Mail Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsMailLeggings.itemHonorPrice = new Array();
fGrandMarshalsMailLeggings.itemHonorPrice[6] = 16065
fGrandMarshalsMailLeggings.itemTokenPrice = new Array();
fGrandMarshalsMailLeggings.itemTokenPrice[6] = new Array(0,0,0,30);
fGrandMarshalsMailLeggings.itemStats = new Array();
fGrandMarshalsMailLeggings.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mail Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+42 Stamina<br>+18 Intellect<br>Durability 90 / 90<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Thunderfist (0/5)</span>\
<br> High Warlord's Mail Armor<br> High Warlord's Mail Gauntlets<br> High Warlord's Mail Helm<br> High Warlord's Mail Leggings<br> High Warlord's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailLeggings; ++i;

var fGrandMarshalsMailHelm = new RewardItem("horde","High Warlord's Mail Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsMailHelm.itemHonorPrice = new Array();
fGrandMarshalsMailHelm.itemHonorPrice[6] = 16065
fGrandMarshalsMailHelm.itemTokenPrice = new Array();
fGrandMarshalsMailHelm.itemTokenPrice[6] = new Array(30,0,0,0);
fGrandMarshalsMailHelm.itemStats = new Array();
fGrandMarshalsMailHelm.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mail Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+36 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Thunderfist (0/5)</span>\
<br> High Warlord's Mail Armor<br> High Warlord's Mail Gauntlets<br> High Warlord's Mail Helm<br> High Warlord's Mail Leggings<br> High Warlord's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailHelm; ++i;


var fGrandMarshalsMailArmor = new RewardItem("horde","High Warlord's Mail Armor","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGrandMarshalsMailArmor.itemHonorPrice = new Array();
fGrandMarshalsMailArmor.itemHonorPrice[6] = 16524
fGrandMarshalsMailArmor.itemTokenPrice = new Array();
fGrandMarshalsMailArmor.itemTokenPrice[6] = new Array(0,30,0,0);
fGrandMarshalsMailArmor.itemStats = new Array();
fGrandMarshalsMailArmor.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Mail Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+42 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Thunderfist (0/5)</span>\
<br> High Warlord's Mail Armor<br> High Warlord's Mail Gauntlets<br> High Warlord's Mail Helm<br> High Warlord's Mail Leggings<br> High Warlord's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMailArmor; ++i;

//SHAMAN SET 3-------------------------
var fGrandMarshalsRingmailChestguard = new RewardItem("horde","High Warlord's Ringmail Chestguard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGrandMarshalsRingmailChestguard.itemHonorPrice = new Array();
fGrandMarshalsRingmailChestguard.itemHonorPrice[6] = 16524
fGrandMarshalsRingmailChestguard.itemTokenPrice = new Array();
fGrandMarshalsRingmailChestguard.itemTokenPrice[6] = new Array(0,30,0,0);
fGrandMarshalsRingmailChestguard.itemStats = new Array();
fGrandMarshalsRingmailChestguard.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ringmail Chestguard</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+34 Stamina<br>+22 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wartide (0/5)</span>\
<br> High Warlord's Ringmail Chestguard<br> High Warlord's Ringmail Gloves<br> High Warlord's Ringmail Headpiece<br> High Warlord's Ringmail Legguards<br> High Warlord's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailChestguard; ++i;

var fGrandMarshalsRingmailGloves = new RewardItem("horde","High Warlord's Ringmail Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGrandMarshalsRingmailGloves.itemHonorPrice = new Array();
fGrandMarshalsRingmailGloves.itemHonorPrice[6] = 10098
fGrandMarshalsRingmailGloves.itemTokenPrice = new Array();
fGrandMarshalsRingmailGloves.itemTokenPrice[6] = new Array(20,0,0,0);
fGrandMarshalsRingmailGloves.itemStats = new Array();
fGrandMarshalsRingmailGloves.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ringmail Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>407 Armor<br>+28 Stamina<br>+18 Intellect<br>Durability 40 / 40<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of all Shock spells by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wartide (0/5)</span>\
<br> High Warlord's Ringmail Chestguard<br> High Warlord's Ringmail Gloves<br> High Warlord's Ringmail Headpiece<br> High Warlord's Ringmail Legguards<br> High Warlord's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailGloves; ++i;

var fGrandMarshalsRingmailHeadpiece = new RewardItem("horde","High Warlord's Ringmail Headpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGrandMarshalsRingmailHeadpiece.itemHonorPrice = new Array();
fGrandMarshalsRingmailHeadpiece.itemHonorPrice[6] = 16065
fGrandMarshalsRingmailHeadpiece.itemTokenPrice = new Array();
fGrandMarshalsRingmailHeadpiece.itemTokenPrice[6] = new Array(30,0,0,0);
fGrandMarshalsRingmailHeadpiece.itemStats = new Array();
fGrandMarshalsRingmailHeadpiece.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ringmail Headpiece</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+33 Stamina<br>+21 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wartide (0/5)</span>\
<br> High Warlord's Ringmail Chestguard<br> High Warlord's Ringmail Gloves<br> High Warlord's Ringmail Headpiece<br> High Warlord's Ringmail Legguards<br> High Warlord's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailHeadpiece; ++i;

var fGrandMarshalsRingmailLegguards = new RewardItem("horde","High Warlord's Ringmail Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGrandMarshalsRingmailLegguards.itemHonorPrice = new Array();
fGrandMarshalsRingmailLegguards.itemHonorPrice[6] = 16065
fGrandMarshalsRingmailLegguards.itemTokenPrice = new Array();
fGrandMarshalsRingmailLegguards.itemTokenPrice[6] = new Array(0,0,0,30);
fGrandMarshalsRingmailLegguards.itemStats = new Array();
fGrandMarshalsRingmailLegguards.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ringmail Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>570 Armor<br>+36 Stamina<br>+24 Intellect<br>Durability 90 / 90<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 62.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wartide (0/5)</span>\
<br> High Warlord's Ringmail Chestguard<br> High Warlord's Ringmail Gloves<br> High Warlord's Ringmail Headpiece<br> High Warlord's Ringmail Legguards<br> High Warlord's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailLegguards; ++i;

var fGrandMarshalsRingmailShoulders = new RewardItem("horde","High Warlord's Ringmail Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGrandMarshalsRingmailShoulders.itemHonorPrice = new Array();
fGrandMarshalsRingmailShoulders.itemHonorPrice[6] = 10098
fGrandMarshalsRingmailShoulders.itemTokenPrice = new Array();
fGrandMarshalsRingmailShoulders.itemTokenPrice[6] = new Array(0,20,0,0);
fGrandMarshalsRingmailShoulders.itemStats = new Array();
fGrandMarshalsRingmailShoulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Ringmail Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>489 Armor<br>+28 Stamina<br>+18 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Wartide (0/5)</span>\
<br> High Warlord's Ringmail Chestguard<br> High Warlord's Ringmail Gloves<br> High Warlord's Ringmail Headpiece<br> High Warlord's Ringmail Legguards<br> High Warlord's Ringmail Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRingmailShoulders; ++i;

//WARLOCK-----------------------------------------------------------------------
var fHighWarlordsDreadweaveGloves = new RewardItem("horde","High Warlord's Dreadweave Gloves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fHighWarlordsDreadweaveGloves.itemHonorPrice = new Array();
fHighWarlordsDreadweaveGloves.itemHonorPrice[7] = 10098
fHighWarlordsDreadweaveGloves.itemTokenPrice = new Array() ;
fHighWarlordsDreadweaveGloves.itemTokenPrice[7] = new Array(20,0,0,0);
fHighWarlordsDreadweaveGloves.itemStats = new Array();
fHighWarlordsDreadweaveGloves.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dreadweave Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+31 Stamina<br>+21 Intellect<br>Durability 30 / 30<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Gives you a 50% chance to avoid interruption caused by damage while casting Fear.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Dreadgear (0/5)</span>\
<br> High Warlord's Dreadweave Gloves<br> High Warlord's Dreadweave Hood<br> High Warlord's Dreadweave Leggings<br> High Warlord's Dreadweave Mantle<br> High Warlord's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveGloves; ++i;

var fHighWarlordsDreadweaveMantle = new RewardItem("horde","High Warlord's Dreadweave Mantle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fHighWarlordsDreadweaveMantle.itemHonorPrice = new Array();
fHighWarlordsDreadweaveMantle.itemHonorPrice[7] = 10098
fHighWarlordsDreadweaveMantle.itemTokenPrice = new Array();
fHighWarlordsDreadweaveMantle.itemTokenPrice[7] = new Array(0,20,0,0);
fHighWarlordsDreadweaveMantle.itemStats = new Array();
fHighWarlordsDreadweaveMantle.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dreadweave Mantle</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+19 Stamina<br>+15 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 6.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Dreadgear (0/5)</span>\
<br> High Warlord's Dreadweave Gloves<br> High Warlord's Dreadweave Hood<br> High Warlord's Dreadweave Leggings<br> High Warlord's Dreadweave Mantle<br> High Warlord's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveMantle; ++i;

var fHighWarlordsDreadweaveLeggings = new RewardItem("horde","High Warlord's Dreadweave Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fHighWarlordsDreadweaveLeggings.itemHonorPrice = new Array();
fHighWarlordsDreadweaveLeggings.itemHonorPrice[7] = 16065
fHighWarlordsDreadweaveLeggings.itemTokenPrice = new Array();
fHighWarlordsDreadweaveLeggings.itemTokenPrice[7] = new Array(0,0,0,30);
fHighWarlordsDreadweaveLeggings.itemStats = new Array();
fHighWarlordsDreadweaveLeggings.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dreadweave Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+49 Stamina<br>+22 Intellect<br>Durability 65 / 65<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Dreadgear (0/5)</span>\
<br> High Warlord's Dreadweave Gloves<br> High Warlord's Dreadweave Hood<br> High Warlord's Dreadweave Leggings<br> High Warlord's Dreadweave Mantle<br> High Warlord's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveLeggings; ++i;

var fHighWarlordsDreadweaveHood = new RewardItem("horde","High Warlord's Dreadweave Hood","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fHighWarlordsDreadweaveHood.itemHonorPrice = new Array();
fHighWarlordsDreadweaveHood.itemHonorPrice[7] = 16065
fHighWarlordsDreadweaveHood.itemTokenPrice = new Array();
fHighWarlordsDreadweaveHood.itemTokenPrice[7] = new Array(30,0,0,0);
fHighWarlordsDreadweaveHood.itemStats = new Array();
fHighWarlordsDreadweaveHood.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dreadweave Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+49 Stamina<br>+14 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Dreadgear (0/5)</span>\
<br> High Warlord's Dreadweave Gloves<br> High Warlord's Dreadweave Hood<br> High Warlord's Dreadweave Leggings<br> High Warlord's Dreadweave Mantle<br> High Warlord's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveHood; ++i;

var fHighWarlordsDreadweaveRobe = new RewardItem("horde","High Warlord's Dreadweave Robe","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-class-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Cloth_43.gif&reason=external-or-uncollected-resource");
fHighWarlordsDreadweaveRobe.itemHonorPrice = new Array();
fHighWarlordsDreadweaveRobe.itemHonorPrice[7] = 16524
fHighWarlordsDreadweaveRobe.itemTokenPrice = new Array();
fHighWarlordsDreadweaveRobe.itemTokenPrice[7] = new Array(0,30,0,0);
fHighWarlordsDreadweaveRobe.itemStats = new Array();
fHighWarlordsDreadweaveRobe.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Dreadweave Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+49 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 80 / 80<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Dreadgear (0/5)</span>\
<br> High Warlord's Dreadweave Gloves<br> High Warlord's Dreadweave Hood<br> High Warlord's Dreadweave Leggings<br> High Warlord's Dreadweave Mantle<br> High Warlord's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDreadweaveRobe; ++i;

//WARRIOR----------------------------------------
var fGrandMarshalsPlateGauntlets = new RewardItem("horde","High Warlord's Plate Gauntlets","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGrandMarshalsPlateGauntlets.itemHonorPrice = new Array();
fGrandMarshalsPlateGauntlets.itemHonorPrice[8] = 10098
fGrandMarshalsPlateGauntlets.itemTokenPrice = new Array();
fGrandMarshalsPlateGauntlets.itemTokenPrice[8] = new Array(20,0,0,0);
fGrandMarshalsPlateGauntlets.itemStats = new Array();
fGrandMarshalsPlateGauntlets.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Plate Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+22 Strength<br>+30 Stamina<br>Durability 45 / 45<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Hamstring Rage cost reduced by 3.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Battlegear (0/5)</span>\
<br> High Warlord's Plate Chestpiece<br> High Warlord's Plate Gauntlets<br> High Warlord's Plate Helm<br> High Warlord's Plate Legguards<br> High Warlord's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateGauntlets; ++i;

var fGrandMarshalsPlateShoulders = new RewardItem("horde","High Warlord's Plate Shoulders","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGrandMarshalsPlateShoulders.itemHonorPrice = new Array();
fGrandMarshalsPlateShoulders.itemHonorPrice[8] = 10098
fGrandMarshalsPlateShoulders.itemTokenPrice = new Array();
fGrandMarshalsPlateShoulders.itemTokenPrice[8] = new Array(0,20,0,0);
fGrandMarshalsPlateShoulders.itemStats = new Array();
fGrandMarshalsPlateShoulders.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Plate Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>873 Armor<br>+14 Strength<br>+36 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Battlegear (0/5)</span>\
<br> High Warlord's Plate Chestpiece<br> High Warlord's Plate Gauntlets<br> High Warlord's Plate Helm<br> High Warlord's Plate Legguards<br> High Warlord's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateShoulders; ++i;


var fGrandMarshalsPlateLegguards = new RewardItem("horde","High Warlord's Plate Legguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGrandMarshalsPlateLegguards.itemHonorPrice = new Array();
fGrandMarshalsPlateLegguards.itemHonorPrice[8] = 16065
fGrandMarshalsPlateLegguards.itemTokenPrice = new Array();
fGrandMarshalsPlateLegguards.itemTokenPrice[8] = new Array(0,0,0,30);
fGrandMarshalsPlateLegguards.itemStats = new Array();
fGrandMarshalsPlateLegguards.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Plate Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+28 Strength<br>+46 Stamina<br>Durability 100 / 100<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Battlegear (0/5)</span>\
<br> High Warlord's Plate Chestpiece<br> High Warlord's Plate Gauntlets<br> High Warlord's Plate Helm<br> High Warlord's Plate Legguards<br> High Warlord's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateLegguards; ++i;

var fGrandMarshalsPlateHelm = new RewardItem("horde","High Warlord's Plate Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGrandMarshalsPlateHelm.itemHonorPrice = new Array();
fGrandMarshalsPlateHelm.itemHonorPrice[8] = 16065
fGrandMarshalsPlateHelm.itemTokenPrice = new Array();
fGrandMarshalsPlateHelm.itemTokenPrice[8] = new Array(30,0,0,0);
fGrandMarshalsPlateHelm.itemStats = new Array();
fGrandMarshalsPlateHelm.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Plate Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>946 Armor<br>+20 Strength<br>+34 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 80 / 80<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Battlegear (0/5)</span>\
<br> High Warlord's Plate Chestpiece<br> High Warlord's Plate Gauntlets<br> High Warlord's Plate Helm<br> High Warlord's Plate Legguards<br> High Warlord's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateHelm; ++i;

var fGrandMarshalsPlateChestpiece = new RewardItem("horde","High Warlord's Plate Chestpiece","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Chest_Plate05.gif");
fGrandMarshalsPlateChestpiece.itemHonorPrice = new Array();
fGrandMarshalsPlateChestpiece.itemHonorPrice[8] = 16524
fGrandMarshalsPlateChestpiece.itemTokenPrice = new Array();
fGrandMarshalsPlateChestpiece.itemTokenPrice[8] = new Array(0,30,0,0);
fGrandMarshalsPlateChestpiece.itemStats = new Array();
fGrandMarshalsPlateChestpiece.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">High Warlord's Plate Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+12 Strength<br>+46 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 135 / 135<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">High Warlord's Battlegear (0/5)</span>\
<br> High Warlord's Plate Chestpiece<br> High Warlord's Plate Gauntlets<br> High Warlord's Plate Helm<br> High Warlord's Plate Legguards<br> High Warlord's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPlateChestpiece; ++i;

//------END REWARDS DEFINITION------
