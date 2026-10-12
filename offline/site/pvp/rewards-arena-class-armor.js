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
		outPutString += thisObject.itemHonorPrice[thisBracket]+"<img src='/pvp/arena-points.gif'>&nbsp;";
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
var fGladiatorsDragonhideGloves = new RewardItem("alliance","Gladiator's Dragonhide Gloves","/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGladiatorsDragonhideGloves.itemHonorPrice = new Array();
fGladiatorsDragonhideGloves.itemHonorPrice[0] = 1125
fGladiatorsDragonhideGloves.itemStats = new Array();
fGladiatorsDragonhideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dragonhide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>258 Armor<br>+28 Strength<br>+16 Agility<br>+30 Stamina<br>+16 Intellect<br>Durability 40 / 40<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Sanctuary (0/5)</span>\
<br> Gladiator's Dragonhide Gloves<br> Gladiator's Dragonhide Helm<br> Gladiator's Dragonhide Legguards<br> Gladiator's Dragonhide Spaulders<br> Gladiator's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDragonhideGloves; ++i;

var fGladiatorsDragonhideSpaulders = new RewardItem("alliance","Gladiator's Dragonhide Spaulders","/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGladiatorsDragonhideSpaulders.itemHonorPrice = new Array();
fGladiatorsDragonhideSpaulders.itemHonorPrice[0] = 1500
fGladiatorsDragonhideSpaulders.itemStats = new Array();
fGladiatorsDragonhideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dragonhide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>302 Armor<br>+25 Strength<br>+15 Agility<br>+30 Stamina<br>+10 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Sanctuary (0/5)</span>\
<br> Gladiator's Dragonhide Gloves<br> Gladiator's Dragonhide Helm<br> Gladiator's Dragonhide Legguards<br> Gladiator's Dragonhide Spaulders<br> Gladiator's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDragonhideSpaulders; ++i;


var fGladiatorsDragonhideLegguards = new RewardItem("alliance","Gladiator's Dragonhide Legguards","/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGladiatorsDragonhideLegguards.itemHonorPrice = new Array();
fGladiatorsDragonhideLegguards.itemHonorPrice[0] = 1875
fGladiatorsDragonhideLegguards.itemStats = new Array();
fGladiatorsDragonhideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dragonhide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>365 Armor<br>+36 Strength<br>+25 Agility<br>+39 Stamina<br>+22 Intellect<br>Durability 90 / 90<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 13.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Sanctuary (0/5)</span>\
<br> Gladiator's Dragonhide Gloves<br> Gladiator's Dragonhide Helm<br> Gladiator's Dragonhide Legguards<br> Gladiator's Dragonhide Spaulders<br> Gladiator's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDragonhideLegguards; ++i;

var fGladiatorsDragonhideHelm = new RewardItem("alliance","Gladiator's Dragonhide Helm","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGladiatorsDragonhideHelm.itemHonorPrice = new Array();
fGladiatorsDragonhideHelm.itemHonorPrice[0] = 1875
fGladiatorsDragonhideHelm.itemStats = new Array();
fGladiatorsDragonhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dragonhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>323 Armor<br>+29 Strength<br>+17 Agility<br>+39 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 37.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Sanctuary (0/5)</span>\
<br> Gladiator's Dragonhide Gloves<br> Gladiator's Dragonhide Helm<br> Gladiator's Dragonhide Legguards<br> Gladiator's Dragonhide Spaulders<br> Gladiator's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDragonhideHelm; ++i;


var fGladiatorsDragonhideTunic = new RewardItem("alliance","Gladiator's Dragonhide Tunic","/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGladiatorsDragonhideTunic.itemHonorPrice = new Array();
fGladiatorsDragonhideTunic.itemHonorPrice[0] = 1875
fGladiatorsDragonhideTunic.itemStats = new Array();
fGladiatorsDragonhideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dragonhide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>404 Armor<br>+30 Strength<br>+18 Agility<br>+39 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 24.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Sanctuary (0/5)</span>\
<br> Gladiator's Dragonhide Gloves<br> Gladiator's Dragonhide Helm<br> Gladiator's Dragonhide Legguards<br> Gladiator's Dragonhide Spaulders<br> Gladiator's Dragonhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDragonhideTunic; ++i;





//DRUID SET 2 ---------------------------
var fGladiatorsWyrmhideGloves = new RewardItem("alliance","Gladiator's Wyrmhide Gloves","/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGladiatorsWyrmhideGloves.itemHonorPrice = new Array();
fGladiatorsWyrmhideGloves.itemHonorPrice[0] = 1125
fGladiatorsWyrmhideGloves.itemStats = new Array();
fGladiatorsWyrmhideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Wyrmhide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>258 Armor<br>+30 Stamina<br>+18 Intellect<br>Durability 40 / 40<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wildhide (0/5)</span>\
<br> Gladiator's Wyrmhide Gloves<br> Gladiator's Wyrmhide Helm<br> Gladiator's Wyrmhide Legguards<br> Gladiator's Wyrmhide Spaulders<br> Gladiator's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsWyrmhideGloves; ++i;



var fGladiatorsWyrmhideSpaulders = new RewardItem("alliance","Gladiator's Wyrmhide Spaulders","/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGladiatorsWyrmhideSpaulders.itemHonorPrice = new Array();
fGladiatorsWyrmhideSpaulders.itemHonorPrice[0] = 1500
fGladiatorsWyrmhideSpaulders.itemStats = new Array();
fGladiatorsWyrmhideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Wyrmhide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>302 Armor<br>+30 Stamina<br>+12 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wildhide (0/5)</span>\
<br> Gladiator's Wyrmhide Gloves<br> Gladiator's Wyrmhide Helm<br> Gladiator's Wyrmhide Legguards<br> Gladiator's Wyrmhide Spaulders<br> Gladiator's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsWyrmhideSpaulders; ++i;



var fGladiatorsWyrmhideLegguards = new RewardItem("alliance","Gladiator's Wyrmhide Legguards","/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGladiatorsWyrmhideLegguards.itemHonorPrice = new Array();
fGladiatorsWyrmhideLegguards.itemHonorPrice[0] = 1875
fGladiatorsWyrmhideLegguards.itemStats = new Array();
fGladiatorsWyrmhideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Wyrmhide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>365 Armor<br>+39 Stamina<br>+25 Intellect<br>Durability 90 / 90<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wildhide (0/5)</span>\
<br> Gladiator's Wyrmhide Gloves<br> Gladiator's Wyrmhide Helm<br> Gladiator's Wyrmhide Legguards<br> Gladiator's Wyrmhide Spaulders<br> Gladiator's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsWyrmhideLegguards; ++i;

var fGladiatorsWyrmhideHelm = new RewardItem("alliance","Gladiator's Wyrmhide Helm","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGladiatorsWyrmhideHelm.itemHonorPrice = new Array();
fGladiatorsWyrmhideHelm.itemHonorPrice[0] = 1875
fGladiatorsWyrmhideHelm.itemStats = new Array();
fGladiatorsWyrmhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Wyrmhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>323 Armor<br>+39 Stamina<br>+21 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wildhide (0/5)</span>\
<br> Gladiator's Wyrmhide Gloves<br> Gladiator's Wyrmhide Helm<br> Gladiator's Wyrmhide Legguards<br> Gladiator's Wyrmhide Spaulders<br> Gladiator's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsWyrmhideHelm; ++i;

var fGladiatorsWyrmhideTunic = new RewardItem("alliance","Gladiator's Wyrmhide Tunic","/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGladiatorsWyrmhideTunic.itemHonorPrice = new Array();
fGladiatorsWyrmhideTunic.itemHonorPrice[0] = 1875
fGladiatorsWyrmhideTunic.itemStats = new Array();
fGladiatorsWyrmhideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Wyrmhide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>404 Armor<br>+39 Stamina<br>+20 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 120 / 120<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 42.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wildhide (0/5)</span>\
<br> Gladiator's Wyrmhide Gloves<br> Gladiator's Wyrmhide Helm<br> Gladiator's Wyrmhide Legguards<br> Gladiator's Wyrmhide Spaulders<br> Gladiator's Wyrmhide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the mana cost of your Moonfire spell by 10%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsWyrmhideTunic; ++i;


//DRUID SET 3-------------------------------------------
var fGladiatorsKodohideGloves = new RewardItem("alliance","Gladiator's Kodohide Gloves","/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGladiatorsKodohideGloves.itemHonorPrice = new Array();
fGladiatorsKodohideGloves.itemHonorPrice[0] = 1125
fGladiatorsKodohideGloves.itemStats = new Array();
fGladiatorsKodohideGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Kodohide Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>258 Armor<br>+30 Stamina<br>+24 Intellect<br>Durability 40 / 40<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 55.</span>\
<br>\
<span class=\"myGreen\">Equip: Reduces the cast time of your Cyclone spell by 0.1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Refuge (0/5)</span>\
<br> Gladiator's Kodohide Gloves<br> Gladiator's Kodohide Helm<br> Gladiator's Kodohide Legguards<br> Gladiator's Kodohide Spaulders<br> Gladiator's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsKodohideGloves; ++i;

var fGladiatorsKodohideSpaulders = new RewardItem("alliance","Gladiator's Kodohide Spaulders","/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGladiatorsKodohideSpaulders.itemHonorPrice = new Array();
fGladiatorsKodohideSpaulders.itemHonorPrice[0] = 1500
fGladiatorsKodohideSpaulders.itemStats = new Array();
fGladiatorsKodohideSpaulders.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Kodohide Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>302 Armor<br>+30 Stamina<br>+18 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Refuge (0/5)</span>\
<br> Gladiator's Kodohide Gloves<br> Gladiator's Kodohide Helm<br> Gladiator's Kodohide Legguards<br> Gladiator's Kodohide Spaulders<br> Gladiator's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsKodohideSpaulders; ++i;

var fGladiatorsKodohideLegguards = new RewardItem("alliance","Gladiator's Kodohide Legguards","/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGladiatorsKodohideLegguards.itemHonorPrice = new Array();
fGladiatorsKodohideLegguards.itemHonorPrice[0] = 1875
fGladiatorsKodohideLegguards.itemStats = new Array();
fGladiatorsKodohideLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Kodohide Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>365 Armor<br>+39 Stamina<br>+33 Intellect<br>Durability 90 / 90<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 75.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Refuge (0/5)</span>\
<br> Gladiator's Kodohide Gloves<br> Gladiator's Kodohide Helm<br> Gladiator's Kodohide Legguards<br> Gladiator's Kodohide Spaulders<br> Gladiator's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsKodohideLegguards; ++i;


var fGladiatorsKodohideHelm = new RewardItem("alliance","Gladiator's Kodohide Helm","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGladiatorsKodohideHelm.itemHonorPrice = new Array();
fGladiatorsKodohideHelm.itemHonorPrice[0] = 1875
fGladiatorsKodohideHelm.itemStats = new Array();
fGladiatorsKodohideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Kodohide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>323 Armor<br>+40 Stamina<br>+29 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 66.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Refuge (0/5)</span>\
<br> Gladiator's Kodohide Gloves<br> Gladiator's Kodohide Helm<br> Gladiator's Kodohide Legguards<br> Gladiator's Kodohide Spaulders<br> Gladiator's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsKodohideHelm; ++i;



var fGladiatorsKodohideTunic = new RewardItem("alliance","Gladiator's Kodohide Tunic","/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGladiatorsKodohideTunic.itemHonorPrice = new Array();
fGladiatorsKodohideTunic.itemHonorPrice[0] = 1875
fGladiatorsKodohideTunic.itemStats = new Array();
fGladiatorsKodohideTunic.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Kodohide Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>404 Armor<br>+39 Stamina<br>+28 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 120 / 120<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Refuge (0/5)</span>\
<br> Gladiator's Kodohide Gloves<br> Gladiator's Kodohide Helm<br> Gladiator's Kodohide Legguards<br> Gladiator's Kodohide Spaulders<br> Gladiator's Kodohide Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Increases your movement speed by 15% while in Bear, Cat, or Travel Form.  Only active outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsKodohideTunic; ++i;




//HUNTER-----------------------------------------------------------------------------

var fGladiatorsChainGauntlets = new RewardItem("alliance","Gladiator's Chain Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGladiatorsChainGauntlets.itemHonorPrice = new Array();
fGladiatorsChainGauntlets.itemHonorPrice[1] = 1125
fGladiatorsChainGauntlets.itemStats = new Array();
fGladiatorsChainGauntlets.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Chain Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>486 Armor<br>+24 Agility<br>+36 Stamina<br>+8 Intellect<br>Durability 50 / 50<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the damage done by your Multi-Shot by 4%.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Pursuit (0/5)</span>\
<br> Gladiator's Chain Armor<br> Gladiator's Chain Gauntlets<br> Gladiator's Chain Helm<br> Gladiator's Chain Leggings<br> Gladiator's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsChainGauntlets; ++i;

var fGladiatorsChainSpaulders = new RewardItem("alliance","Gladiator's Chain Spaulders","/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGladiatorsChainSpaulders.itemHonorPrice = new Array();
fGladiatorsChainSpaulders.itemHonorPrice[1] = 1500
fGladiatorsChainSpaulders.itemStats = new Array();
fGladiatorsChainSpaulders.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Chain Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>583 Armor<br>+25 Agility<br>+36 Stamina<br>+6 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Pursuit (0/5)</span>\
<br> Gladiator's Chain Armor<br> Gladiator's Chain Gauntlets<br> Gladiator's Chain Helm<br> Gladiator's Chain Leggings<br> Gladiator's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsChainSpaulders; ++i;





var fGladiatorsChainLeggings = new RewardItem("alliance","Gladiator's Chain Leggings","/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGladiatorsChainLeggings.itemHonorPrice = new Array();
fGladiatorsChainLeggings.itemHonorPrice[1] = 1875
fGladiatorsChainLeggings.itemStats = new Array();
fGladiatorsChainLeggings.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Chain Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>681 Armor<br>+32 Agility<br>+48 Stamina<br>+10 Intellect<br>Durability 105 / 105<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Pursuit (0/5)</span>\
<br> Gladiator's Chain Armor<br> Gladiator's Chain Gauntlets<br> Gladiator's Chain Helm<br> Gladiator's Chain Leggings<br> Gladiator's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsChainLeggings; ++i;

var fGladiatorsChainHelm = new RewardItem("alliance","Gladiator's Chain Helm","/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGladiatorsChainHelm.itemHonorPrice = new Array();
fGladiatorsChainHelm.itemHonorPrice[1] = 1875
fGladiatorsChainHelm.itemStats = new Array();
fGladiatorsChainHelm.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Chain Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>632 Armor<br>+31 Agility<br>+44 Stamina<br>+15 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Pursuit (0/5)</span>\
<br> Gladiator's Chain Armor<br> Gladiator's Chain Gauntlets<br> Gladiator's Chain Helm<br> Gladiator's Chain Leggings<br> Gladiator's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsChainHelm; ++i;





var fGladiatorsChainArmor = new RewardItem("alliance","Gladiator's Chain Armor","/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGladiatorsChainArmor.itemHonorPrice = new Array();
fGladiatorsChainArmor.itemHonorPrice[1] = 1875
fGladiatorsChainArmor.itemStats = new Array();
fGladiatorsChainArmor.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Chain Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>812 Armor<br>+25 Agility<br>+48 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 140 / 140<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Pursuit (0/5)</span>\
<br> Gladiator's Chain Armor<br> Gladiator's Chain Gauntlets<br> Gladiator's Chain Helm<br> Gladiator's Chain Leggings<br> Gladiator's Chain Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Concussive Shot by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsChainArmor; ++i;

//MAGE---------------------------------------------------------------------
var fGladiatorsSilkHandguards = new RewardItem("alliance","Gladiator's Silk Handguards","/info/basics/factions/images/icons/INV_Gauntlets_19.gif");
fGladiatorsSilkHandguards.itemHonorPrice = new Array();
fGladiatorsSilkHandguards.itemHonorPrice[2] = 1125
fGladiatorsSilkHandguards.itemStats = new Array();
fGladiatorsSilkHandguards.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Silk Handguards</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>116 Armor<br>+36 Stamina<br>+12 Intellect<br>Durability 35 / 35<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of your Fire Blast spell by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Regalia (0/5)</span>\
<br> Gladiator's Silk Amice<br> Gladiator's Silk Cowl<br> Gladiator's Silk Handguards<br> Gladiator's Silk Raiment<br> Gladiator's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSilkHandguards; ++i;


var fGladiatorsSilkAmice = new RewardItem("alliance","Gladiator's Silk Amice","/info/basics/factions/images/icons/INV_Shoulder_19.gif");
fGladiatorsSilkAmice.itemHonorPrice = new Array();
fGladiatorsSilkAmice.itemHonorPrice[2] = 1500
fGladiatorsSilkAmice.itemStats = new Array();
fGladiatorsSilkAmice.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Silk Amice</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>140 Armor<br>+39 Stamina<br>+11 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Regalia (0/5)</span>\
<br> Gladiator's Silk Amice<br> Gladiator's Silk Cowl<br> Gladiator's Silk Handguards<br> Gladiator's Silk Raiment<br> Gladiator's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSilkAmice; ++i;


var fGladiatorsSilkTrousers = new RewardItem("alliance","Gladiator's Silk Trousers","/info/basics/factions/images/icons/INV_Pants_07.gif");
fGladiatorsSilkTrousers.itemHonorPrice = new Array();
fGladiatorsSilkTrousers.itemHonorPrice[2] = 1875
fGladiatorsSilkTrousers.itemStats = new Array();
fGladiatorsSilkTrousers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Silk Trousers</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>163 Armor<br>+48 Stamina<br>+22 Intellect<br>Durability 75 / 75<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 37.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Regalia (0/5)</span>\
<br> Gladiator's Silk Amice<br> Gladiator's Silk Cowl<br> Gladiator's Silk Handguards<br> Gladiator's Silk Raiment<br> Gladiator's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSilkTrousers; ++i;


var fGladiatorsSilkCowl = new RewardItem("alliance","Gladiator's Silk Cowl","/info/basics/factions/images/icons/INV_Helmet_08.gif");
fGladiatorsSilkCowl.itemHonorPrice = new Array();
fGladiatorsSilkCowl.itemHonorPrice[2] = 1875
fGladiatorsSilkCowl.itemStats = new Array();
fGladiatorsSilkCowl.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Silk Cowl</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>151 Armor<br>+48 Stamina<br>+12 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Regalia (0/5)</span>\
<br> Gladiator's Silk Amice<br> Gladiator's Silk Cowl<br> Gladiator's Silk Handguards<br> Gladiator's Silk Raiment<br> Gladiator's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSilkCowl; ++i;


var fGladiatorsSilkRaiment = new RewardItem("alliance","Gladiator's Silk Raiment","/info/basics/factions/images/icons/INV_Chest_Leather_01.gif");
fGladiatorsSilkRaiment.itemHonorPrice = new Array();
fGladiatorsSilkRaiment.itemHonorPrice[2] = 1875
fGladiatorsSilkRaiment.itemStats = new Array();
fGladiatorsSilkRaiment.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Silk Raiment</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>194 Armor<br>+48 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 100 / 100<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Regalia (0/5)</span>\
<br> Gladiator's Silk Amice<br> Gladiator's Silk Cowl<br> Gladiator's Silk Handguards<br> Gladiator's Silk Raiment<br> Gladiator's Silk Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Blink spell by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSilkRaiment; ++i;


//PALADIN-----------------------------------------------------
var fGladiatorsLamellarGauntlets = new RewardItem("alliance","Gladiator's Lamellar Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGladiatorsLamellarGauntlets.itemHonorPrice = new Array();
fGladiatorsLamellarGauntlets.itemHonorPrice[3] = 1125
fGladiatorsLamellarGauntlets.itemStats = new Array();
fGladiatorsLamellarGauntlets.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Lamellar Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>868 Armor<br>+31 Stamina<br>+21 Intellect<br>Durability 55 / 55<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the critical effect chance of your Flash of Light by 2%.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Aegis (0/5)</span>\
<br> Gladiator's Lamellar Chestpiece<br> Gladiator's Lamellar Gauntlets<br> Gladiator's Lamellar Helm<br> Gladiator's Lamellar Legguards<br> Gladiator's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLamellarGauntlets; ++i;

var fGladiatorsLamellarShoulders = new RewardItem("alliance","Gladiator's Lamellar Shoulders","/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGladiatorsLamellarShoulders.itemHonorPrice = new Array();
fGladiatorsLamellarShoulders.itemHonorPrice[3] = 1500
fGladiatorsLamellarShoulders.itemStats = new Array();
fGladiatorsLamellarShoulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Lamellar Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>1042 Armor<br>+31 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Aegis (0/5)</span>\
<br> Gladiator's Lamellar Chestpiece<br> Gladiator's Lamellar Gauntlets<br> Gladiator's Lamellar Helm<br> Gladiator's Lamellar Legguards<br> Gladiator's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLamellarShoulders; ++i;



var fGladiatorsLamellarLegguards = new RewardItem("alliance","Gladiator's Lamellar Legguards","/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGladiatorsLamellarLegguards.itemHonorPrice = new Array();
fGladiatorsLamellarLegguards.itemHonorPrice[3] = 1875
fGladiatorsLamellarLegguards.itemStats = new Array();
fGladiatorsLamellarLegguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Lamellar Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1216 Armor<br>+51 Stamina<br>+18 Intellect<br>Durability 120 / 120<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Aegis (0/5)</span>\
<br> Gladiator's Lamellar Chestpiece<br> Gladiator's Lamellar Gauntlets<br> Gladiator's Lamellar Helm<br> Gladiator's Lamellar Legguards<br> Gladiator's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLamellarLegguards; ++i;



var fGladiatorsLamellarHelm = new RewardItem("alliance","Gladiator's Lamellar Helm","/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGladiatorsLamellarHelm.itemHonorPrice = new Array();
fGladiatorsLamellarHelm.itemHonorPrice[3] = 1875
fGladiatorsLamellarHelm.itemStats = new Array();
fGladiatorsLamellarHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Lamellar Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>1129 Armor<br>+51 Stamina<br>+18 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Aegis (0/5)</span>\
<br> Gladiator's Lamellar Chestpiece<br> Gladiator's Lamellar Gauntlets<br> Gladiator's Lamellar Helm<br> Gladiator's Lamellar Legguards<br> Gladiator's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLamellarHelm; ++i;



var fGladiatorsLamellarChestpiece = new RewardItem("alliance","Gladiator's Lamellar Chestpiece","/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGladiatorsLamellarChestpiece.itemHonorPrice = new Array();
fGladiatorsLamellarChestpiece.itemHonorPrice[3] = 1875
fGladiatorsLamellarChestpiece.itemStats = new Array();
fGladiatorsLamellarChestpiece.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Lamellar Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1450 Armor<br>+48 Stamina<br>+23 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 165 / 165<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Aegis (0/5)</span>\
<br> Gladiator's Lamellar Chestpiece<br> Gladiator's Lamellar Gauntlets<br> Gladiator's Lamellar Helm<br> Gladiator's Lamellar Legguards<br> Gladiator's Lamellar Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLamellarChestpiece; ++i;




//PALADIN SET 2
var fGladiatorsScaledGauntlets = new RewardItem("alliance","Gladiator's Scaled Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGladiatorsScaledGauntlets.itemHonorPrice = new Array();
fGladiatorsScaledGauntlets.itemHonorPrice[3] = 1125
fGladiatorsScaledGauntlets.itemStats = new Array();
fGladiatorsScaledGauntlets.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Scaled Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>868 Armor<br>+21 Strength<br>+31 Stamina<br>+12 Intellect<br>Durability 55 / 55<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the Holy damage bonus of your Judgement of the Crusader by 20.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vindication (0/5)</span>\
<br> Gladiator's Scaled Chestpiece<br> Gladiator's Scaled Gauntlets<br> Gladiator's Scaled Helm<br> Gladiator's Scaled Legguards<br> Gladiator's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsScaledGauntlets; ++i;

var fGladiatorsScaledShoulders = new RewardItem("alliance","Gladiator's Scaled Shoulders","/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGladiatorsScaledShoulders.itemHonorPrice = new Array();
fGladiatorsScaledShoulders.itemHonorPrice[3] = 1500
fGladiatorsScaledShoulders.itemStats = new Array();
fGladiatorsScaledShoulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Scaled Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>1042 Armor<br>+21 Strength<br>+31 Stamina<br>+13 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vindication (0/5)</span>\
<br> Gladiator's Scaled Chestpiece<br> Gladiator's Scaled Gauntlets<br> Gladiator's Scaled Helm<br> Gladiator's Scaled Legguards<br> Gladiator's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsScaledShoulders; ++i;



var fGladiatorsScaledLegguards = new RewardItem("alliance","Gladiator's Scaled Legguards","/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGladiatorsScaledLegguards.itemHonorPrice = new Array();
fGladiatorsScaledLegguards.itemHonorPrice[3] = 1875
fGladiatorsScaledLegguards.itemStats = new Array();
fGladiatorsScaledLegguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Scaled Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1216 Armor<br>+28 Strength<br>+48 Stamina<br>+18 Intellect<br>Durability 120 / 120<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vindication (0/5)</span>\
<br> Gladiator's Scaled Chestpiece<br> Gladiator's Scaled Gauntlets<br> Gladiator's Scaled Helm<br> Gladiator's Scaled Legguards<br> Gladiator's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsScaledLegguards; ++i;



var fGladiatorsScaledHelm = new RewardItem("alliance","Gladiator's Scaled Helm","/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGladiatorsScaledHelm.itemHonorPrice = new Array();
fGladiatorsScaledHelm.itemHonorPrice[3] = 1875
fGladiatorsScaledHelm.itemStats = new Array();
fGladiatorsScaledHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Scaled Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>1129 Armor<br>+30 Strength<br>+42 Stamina<br>+18 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vindication (0/5)</span>\
<br> Gladiator's Scaled Chestpiece<br> Gladiator's Scaled Gauntlets<br> Gladiator's Scaled Helm<br> Gladiator's Scaled Legguards<br> Gladiator's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsScaledHelm; ++i;



var fGladiatorsScaledChestpiece = new RewardItem("alliance","Gladiator's Scaled Chestpiece","/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGladiatorsScaledChestpiece.itemHonorPrice = new Array();
fGladiatorsScaledChestpiece.itemHonorPrice[3] = 1875
fGladiatorsScaledChestpiece.itemStats = new Array();
fGladiatorsScaledChestpiece.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Scaled Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1450 Armor<br>+29 Strength<br>+42 Stamina<br>+21 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 165 / 165<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vindication (0/5)</span>\
<br> Gladiator's Scaled Chestpiece<br> Gladiator's Scaled Gauntlets<br> Gladiator's Scaled Helm<br> Gladiator's Scaled Legguards<br> Gladiator's Scaled Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsScaledChestpiece; ++i;

var fGladiatorsOrnamentedChestguard = new RewardItem("alliance","Gladiator's Ornamented Chestguard","/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGladiatorsOrnamentedChestguard.itemHonorPrice = new Array();
fGladiatorsOrnamentedChestguard.itemHonorPrice[3] = 1875
fGladiatorsOrnamentedChestguard.itemStats = new Array();
fGladiatorsOrnamentedChestguard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ornamented Chestguard</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1450 Armor<br>+42 Stamina<br>+29 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 165 / 165<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 35.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Redemption (0/5)</span>\
<br> Gladiator's Ornamented Chestguard<br> Gladiator's Ornamented Gloves<br> Gladiator's Ornamented Headcover<br> Gladiator's Ornamented Legplates<br> Gladiator's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsOrnamentedChestguard; ++i;








var fGladiatorsOrnamentedGloves = new RewardItem("alliance","Gladiator's Ornamented Gloves","/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGladiatorsOrnamentedGloves.itemHonorPrice = new Array();
fGladiatorsOrnamentedGloves.itemHonorPrice[3] = 1125
fGladiatorsOrnamentedGloves.itemStats = new Array();
fGladiatorsOrnamentedGloves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ornamented Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>868 Armor<br>+31 Stamina<br>+21 Intellect<br>Durability 55 / 55<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the critical effect chance of your Flash of Light by 2%.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Redemption (0/5)</span>\
<br> Gladiator's Ornamented Chestguard<br> Gladiator's Ornamented Gloves<br> Gladiator's Ornamented Headcover<br> Gladiator's Ornamented Legplates<br> Gladiator's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsOrnamentedGloves; ++i;



var fGladiatorsOrnamentedHeadcover = new RewardItem("alliance","Gladiator's Ornamented Headcover","/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGladiatorsOrnamentedHeadcover.itemHonorPrice = new Array();
fGladiatorsOrnamentedHeadcover.itemHonorPrice[3] = 1875
fGladiatorsOrnamentedHeadcover.itemStats = new Array();
fGladiatorsOrnamentedHeadcover.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ornamented Headcover</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>1129 Armor<br>+46 Stamina<br>+26 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 48.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Redemption (0/5)</span>\
<br> Gladiator's Ornamented Chestguard<br> Gladiator's Ornamented Gloves<br> Gladiator's Ornamented Headcover<br> Gladiator's Ornamented Legplates<br> Gladiator's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsOrnamentedHeadcover; ++i;




var fGladiatorsOrnamentedLegplates = new RewardItem("alliance","Gladiator's Ornamented Legplates","/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGladiatorsOrnamentedLegplates.itemHonorPrice = new Array();
fGladiatorsOrnamentedLegplates.itemHonorPrice[3] = 1875
fGladiatorsOrnamentedLegplates.itemStats = new Array();
fGladiatorsOrnamentedLegplates.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ornamented Legplates</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1216 Armor<br>+42 Stamina<br>+28 Intellect<br>Durability 120 / 120<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 62.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Redemption (0/5)</span>\
<br> Gladiator's Ornamented Chestguard<br> Gladiator's Ornamented Gloves<br> Gladiator's Ornamented Headcover<br> Gladiator's Ornamented Legplates<br> Gladiator's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsOrnamentedLegplates; ++i;



var fGladiatorsOrnamentedSpaulders = new RewardItem("alliance","Gladiator's Ornamented Spaulders","/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGladiatorsOrnamentedSpaulders.itemHonorPrice = new Array();
fGladiatorsOrnamentedSpaulders.itemHonorPrice[3] = 1500
fGladiatorsOrnamentedSpaulders.itemStats = new Array();
fGladiatorsOrnamentedSpaulders.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ornamented Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>1042 Armor<br>+27 Stamina<br>+21 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Redemption (0/5)</span>\
<br> Gladiator's Ornamented Chestguard<br> Gladiator's Ornamented Gloves<br> Gladiator's Ornamented Headcover<br> Gladiator's Ornamented Legplates<br> Gladiator's Ornamented Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Hammer of Justice by 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsOrnamentedSpaulders; ++i;





//PRIEST---------------------------------------------------------------------------------------

//PRIEST SET 1-----
var fGladiatorsSatinGloves = new RewardItem("alliance","Gladiator's Satin Gloves","/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fGladiatorsSatinGloves.itemHonorPrice = new Array();
fGladiatorsSatinGloves.itemHonorPrice[4] = 1125
fGladiatorsSatinGloves.itemStats = new Array();
fGladiatorsSatinGloves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Satin Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>116 Armor<br>+36 Stamina<br>+17 Intellect<br>Durability 35 / 35<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the duration of your Psychic Scream spell by 1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Raiment (0/5)</span>\
<br> Gladiator's Satin Gloves<br> Gladiator's Satin Hood<br> Gladiator's Satin Leggings<br> Gladiator's Satin Mantle<br> Gladiator's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSatinGloves; ++i;



var fGladiatorsSatinMantle = new RewardItem("alliance","Gladiator's Satin Mantle","/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fGladiatorsSatinMantle.itemHonorPrice = new Array();
fGladiatorsSatinMantle.itemHonorPrice[4] = 1500
fGladiatorsSatinMantle.itemStats = new Array();
fGladiatorsSatinMantle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Satin Mantle</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>140 Armor<br>+36 Stamina<br>+19 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 16.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Raiment (0/5)</span>\
<br> Gladiator's Satin Gloves<br> Gladiator's Satin Hood<br> Gladiator's Satin Leggings<br> Gladiator's Satin Mantle<br> Gladiator's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSatinMantle; ++i;



var fGladiatorsSatinLeggings = new RewardItem("alliance","Gladiator's Satin Leggings","/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGladiatorsSatinLeggings.itemHonorPrice = new Array();
fGladiatorsSatinLeggings.itemHonorPrice[4] = 1875
fGladiatorsSatinLeggings.itemStats = new Array();
fGladiatorsSatinLeggings.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Satin Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>163 Armor<br>+54 Stamina<br>+26 Intellect<br>Durability 75 / 75<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 42.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Raiment (0/5)</span>\
<br> Gladiator's Satin Gloves<br> Gladiator's Satin Hood<br> Gladiator's Satin Leggings<br> Gladiator's Satin Mantle<br> Gladiator's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSatinLeggings; ++i;

var fGladiatorsSatinHood = new RewardItem("alliance","Gladiator's Satin Hood","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGladiatorsSatinHood.itemHonorPrice = new Array();
fGladiatorsSatinHood.itemHonorPrice[4] = 1875
fGladiatorsSatinHood.itemStats = new Array();
fGladiatorsSatinHood.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Satin Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>151 Armor<br>+54 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Raiment (0/5)</span>\
<br> Gladiator's Satin Gloves<br> Gladiator's Satin Hood<br> Gladiator's Satin Leggings<br> Gladiator's Satin Mantle<br> Gladiator's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSatinHood; ++i;




var fGladiatorsSatinRobe = new RewardItem("alliance","Gladiator's Satin Robe","/info/basics/factions/images/icons/INV_Chest_Cloth_43.gif");
fGladiatorsSatinRobe.itemHonorPrice = new Array();
fGladiatorsSatinRobe.itemHonorPrice[4] = 1875
fGladiatorsSatinRobe.itemStats = new Array();
fGladiatorsSatinRobe.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Satin Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>194 Armor<br>+48 Stamina<br>+24 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 100 / 100<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Raiment (0/5)</span>\
<br> Gladiator's Satin Gloves<br> Gladiator's Satin Hood<br> Gladiator's Satin Leggings<br> Gladiator's Satin Mantle<br> Gladiator's Satin Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSatinRobe; ++i;

//PRIEST SET 2 ------------

var fGladiatorsMoonclothGloves = new RewardItem("alliance","Gladiator's Mooncloth Gloves","/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fGladiatorsMoonclothGloves.itemHonorPrice = new Array();
fGladiatorsMoonclothGloves.itemHonorPrice[4] = 1125
fGladiatorsMoonclothGloves.itemStats = new Array();
fGladiatorsMoonclothGloves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mooncloth Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>116 Armor<br>+36 Stamina<br>+17 Intellect<br>Durability 35 / 35<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the duration of your Psychic Scream spell by 1 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Investiture (0/5)</span>\
<br> Gladiator's Mooncloth Gloves<br> Gladiator's Mooncloth Hood<br> Gladiator's Mooncloth Leggings<br> Gladiator's Mooncloth Mantle<br> Gladiator's Mooncloth Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br><span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMoonclothGloves; ++i;

var fGladiatorsMoonclothMantle = new RewardItem("alliance","Gladiator's Mooncloth Mantle","/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fGladiatorsMoonclothMantle.itemHonorPrice = new Array();
fGladiatorsMoonclothMantle.itemHonorPrice[4] = 1500
fGladiatorsMoonclothMantle.itemStats = new Array();
fGladiatorsMoonclothMantle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mooncloth Mantle</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>140 Armor<br>+36 Stamina<br>+19 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 35.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Investiture (0/5)</span>\
<br> Gladiator's Mooncloth Gloves<br> Gladiator's Mooncloth Hood<br> Gladiator's Mooncloth Leggings<br> Gladiator's Mooncloth Mantle<br> Gladiator's Mooncloth Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMoonclothMantle; ++i;



var fGladiatorsMoonclothLeggings = new RewardItem("alliance","Gladiator's Mooncloth Leggings","/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGladiatorsMoonclothLeggings.itemHonorPrice = new Array();
fGladiatorsMoonclothLeggings.itemHonorPrice[4] = 1875
fGladiatorsMoonclothLeggings.itemStats = new Array();
fGladiatorsMoonclothLeggings.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mooncloth Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>163 Armor<br>+54 Stamina<br>+26 Intellect<br>Durability 75 / 75<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 53.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 10 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Investiture (0/5)</span>\
<br> Gladiator's Mooncloth Gloves<br> Gladiator's Mooncloth Hood<br> Gladiator's Mooncloth Leggings<br> Gladiator's Mooncloth Mantle<br> Gladiator's Mooncloth Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br><span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMoonclothLeggings; ++i;

var fGladiatorsMoonclothHood = new RewardItem("alliance","Gladiator's Mooncloth Hood","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGladiatorsMoonclothHood.itemHonorPrice = new Array();
fGladiatorsMoonclothHood.itemHonorPrice[4] = 1875
fGladiatorsMoonclothHood.itemStats = new Array();
fGladiatorsMoonclothHood.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mooncloth Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>151 Armor<br>+54 Stamina<br>+18 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Investiture (0/5)</span>\
<br> Gladiator's Mooncloth Gloves<br> Gladiator's Mooncloth Hood<br> Gladiator's Mooncloth Leggings<br> Gladiator's Mooncloth Mantle<br> Gladiator's Mooncloth Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMoonclothHood; ++i;



var fGladiatorsMoonclothRobe = new RewardItem("alliance","Gladiator's Mooncloth Robe","/info/basics/factions/images/icons/INV_Chest_Cloth_43.gif");
fGladiatorsMoonclothRobe.itemHonorPrice = new Array();
fGladiatorsMoonclothRobe.itemHonorPrice[4] = 1875
fGladiatorsMoonclothRobe.itemStats = new Array();
fGladiatorsMoonclothRobe.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mooncloth Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>194 Armor<br>+48 Stamina<br>+26 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 100 / 100<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Investiture (0/5)</span>\
<br> Gladiator's Mooncloth Gloves<br> Gladiator's Mooncloth Hood<br> Gladiator's Mooncloth Leggings<br> Gladiator's Mooncloth Mantle<br> Gladiator's Mooncloth Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the duration of the Weakened Soul effect caused by your Power Word: Shield by 2 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMoonclothRobe; ++i;




//ROGUE-----------------------------------------------
var fGladiatorsLeatherGloves = new RewardItem("alliance","Gladiator's Leather Gloves","/info/basics/factions/images/icons/INV_Gauntlets_28.gif");
fGladiatorsLeatherGloves.itemHonorPrice = new Array();
fGladiatorsLeatherGloves.itemHonorPrice[5] = 1125
fGladiatorsLeatherGloves.itemStats = new Array();
fGladiatorsLeatherGloves.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Leather Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>218 Armor<br>+24 Agility<br>+36 Stamina<br>Durability 40 / 40<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Causes your Deadly Throw ability to interrupt spellcasting and prevent any spell in that school from being cast for 3 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vestments (0/5)</span>\
<br> Gladiator's Leather Gloves<br> Gladiator's Leather Legguards<br> Gladiator's Leather Helm<br> Gladiator's Leather Spaulders<br> Gladiator's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLeatherGloves; ++i;



var fGladiatorsLeatherSpaulders = new RewardItem("alliance","Gladiator's Leather Spaulders","/info/basics/factions/images/icons/INV_Shoulder_12.gif");
fGladiatorsLeatherSpaulders.itemHonorPrice = new Array();
fGladiatorsLeatherSpaulders.itemHonorPrice[5] = 1500
fGladiatorsLeatherSpaulders.itemStats = new Array();
fGladiatorsLeatherSpaulders.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Leather Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>262 Armor<br>+26 Agility<br>+36 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 12.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vestments (0/5)</span>\
<br> Gladiator's Leather Gloves<br> Gladiator's Leather Legguards<br> Gladiator's Leather Helm<br> Gladiator's Leather Spaulders<br> Gladiator's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLeatherSpaulders; ++i;





var fGladiatorsLeatherLegguards = new RewardItem("alliance","Gladiator's Leather Legguards","/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGladiatorsLeatherLegguards.itemHonorPrice = new Array();
fGladiatorsLeatherLegguards.itemHonorPrice[5] = 1875
fGladiatorsLeatherLegguards.itemStats = new Array();
fGladiatorsLeatherLegguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Leather Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>305 Armor<br>+32 Agility<br>+48 Stamina<br>Durability 90 / 90<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vestments (0/5)</span>\
<br> Gladiator's Leather Gloves<br> Gladiator's Leather Legguards<br> Gladiator's Leather Helm<br> Gladiator's Leather Spaulders<br> Gladiator's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLeatherLegguards; ++i;










var fGladiatorsLeatherHelm = new RewardItem("alliance","Gladiator's Leather Helm","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGladiatorsLeatherHelm.itemHonorPrice = new Array();
fGladiatorsLeatherHelm.itemHonorPrice[5] = 1875
fGladiatorsLeatherHelm.itemStats = new Array();
fGladiatorsLeatherHelm.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Leather Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+30 Agility<br>+47 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 70 / 70<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vestments (0/5)</span>\
<br> Gladiator's Leather Gloves<br> Gladiator's Leather Legguards<br> Gladiator's Leather Helm<br> Gladiator's Leather Spaulders<br> Gladiator's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLeatherHelm; ++i;




var fGladiatorsLeatherTunic = new RewardItem("alliance","Gladiator's Leather Tunic","/info/basics/factions/images/icons/INV_Chest_Leather_03.gif");
fGladiatorsLeatherTunic.itemHonorPrice = new Array();
fGladiatorsLeatherTunic.itemHonorPrice[5] = 1875
fGladiatorsLeatherTunic.itemStats = new Array();
fGladiatorsLeatherTunic.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Leather Tunic</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>364 Armor<br>+31 Agility<br>+47 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 120 / 120<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Vestments (0/5)</span>\
<br> Gladiator's Leather Gloves<br> Gladiator's Leather Legguards<br> Gladiator's Leather Helm<br> Gladiator's Leather Spaulders<br> Gladiator's Leather Tunic<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Gouge ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLeatherTunic; ++i;





//SHAMAN---------------------------------------------------------------------------------------------

var fGladiatorsLinkedGauntlets = new RewardItem("alliance","Gladiator's Linked Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGladiatorsLinkedGauntlets.itemHonorPrice = new Array();
fGladiatorsLinkedGauntlets.itemHonorPrice[6] = 1125
fGladiatorsLinkedGauntlets.itemStats = new Array();
fGladiatorsLinkedGauntlets.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Linked Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>486 Armor<br>+22 Strength<br>+36 Stamina<br>Durability 50 / 50<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the damage done by your Lightning Shield by 8%.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Earthshaker (0/5)</span>\
<br> Gladiator's Linked Armor<br> Gladiator's Linked Gauntlets<br> Gladiator's Linked Helm<br> Gladiator's Linked Leggings<br> Gladiator's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLinkedGauntlets; ++i;





var fGladiatorsLinkedSpaulders = new RewardItem("alliance","Gladiator's Linked Spaulders","/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGladiatorsLinkedSpaulders.itemHonorPrice = new Array();
fGladiatorsLinkedSpaulders.itemHonorPrice[6] = 1500
fGladiatorsLinkedSpaulders.itemStats = new Array();
fGladiatorsLinkedSpaulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Linked Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>583 Armor<br>+16 Strength<br>+39 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Earthshaker (0/5)</span>\
<br> Gladiator's Linked Armor<br> Gladiator's Linked Gauntlets<br> Gladiator's Linked Helm<br> Gladiator's Linked Leggings<br> Gladiator's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLinkedSpaulders; ++i;






var fGladiatorsLinkedLeggings = new RewardItem("alliance","Gladiator's Linked Leggings","/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGladiatorsLinkedLeggings.itemHonorPrice = new Array();
fGladiatorsLinkedLeggings.itemHonorPrice[6] = 1875
fGladiatorsLinkedLeggings.itemStats = new Array();
fGladiatorsLinkedLeggings.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Linked Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>681 Armor<br>+26 Strength<br>+48 Stamina<br>+22 Intellect<br>Durability 105 / 105<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Earthshaker (0/5)</span>\
<br> Gladiator's Linked Armor<br> Gladiator's Linked Gauntlets<br> Gladiator's Linked Helm<br> Gladiator's Linked Leggings<br> Gladiator's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLinkedLeggings; ++i;


var fGladiatorsLinkedHelm = new RewardItem("alliance","Gladiator's Linked Helm","/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGladiatorsLinkedHelm.itemHonorPrice = new Array();
fGladiatorsLinkedHelm.itemHonorPrice[6] = 1875
fGladiatorsLinkedHelm.itemStats = new Array();
fGladiatorsLinkedHelm.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Linked Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>632 Armor<br>+29 Strength<br>+45 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Earthshaker (0/5)</span>\
<br> Gladiator's Linked Armor<br> Gladiator's Linked Gauntlets<br> Gladiator's Linked Helm<br> Gladiator's Linked Leggings<br> Gladiator's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLinkedHelm; ++i;



var fGladiatorsLinkedArmor = new RewardItem("alliance","Gladiator's Linked Armor","/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGladiatorsLinkedArmor.itemHonorPrice = new Array();
fGladiatorsLinkedArmor.itemHonorPrice[6] = 1875
fGladiatorsLinkedArmor.itemStats = new Array();
fGladiatorsLinkedArmor.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Linked Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>812 Armor<br>+26 Strength<br>+48 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 140 / 140<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Earthshaker (0/5)</span>\
<br> Gladiator's Linked Armor<br> Gladiator's Linked Gauntlets<br> Gladiator's Linked Helm<br> Gladiator's Linked Leggings<br> Gladiator's Linked Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Stormstrike ability by 1 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLinkedArmor; ++i;



//SHAMAN SET 2---------------
var fGladiatorsMailGauntlets = new RewardItem("alliance","Gladiator's Mail Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGladiatorsMailGauntlets.itemHonorPrice = new Array();
fGladiatorsMailGauntlets.itemHonorPrice[6] = 1125
fGladiatorsMailGauntlets.itemStats = new Array();
fGladiatorsMailGauntlets.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mail Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>486 Armor<br>+33 Stamina<br>+16 Intellect<br>Durability 50 / 50<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves the range of all Shock spells by 5 yards.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Thunderfist (0/5)</span>\
<br> Gladiator's Mail Armor<br> Gladiator's Mail Gauntlets<br> Gladiator's Mail Helm<br> Gladiator's Mail Leggings<br> Gladiator's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMailGauntlets; ++i;



var fGladiatorsMailSpaulders = new RewardItem("alliance","Gladiator's Mail Spaulders","/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGladiatorsMailSpaulders.itemHonorPrice = new Array();
fGladiatorsMailSpaulders.itemHonorPrice[6] = 1500
fGladiatorsMailSpaulders.itemStats = new Array();
fGladiatorsMailSpaulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mail Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>583 Armor<br>+30 Stamina<br>+15 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Thunderfist (0/5)</span>\
<br> Gladiator's Mail Armor<br> Gladiator's Mail Gauntlets<br> Gladiator's Mail Helm<br> Gladiator's Mail Leggings<br> Gladiator's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMailSpaulders; ++i;


var fGladiatorsMailLeggings = new RewardItem("alliance","Gladiator's Mail Leggings","/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGladiatorsMailLeggings.itemHonorPrice = new Array();
fGladiatorsMailLeggings.itemHonorPrice[6] = 1875
fGladiatorsMailLeggings.itemStats = new Array();
fGladiatorsMailLeggings.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mail Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>681 Armor<br>+48 Stamina<br>+22 Intellect<br>Durability 105 / 105<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 37.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Thunderfist (0/5)</span>\
<br> Gladiator's Mail Armor<br> Gladiator's Mail Gauntlets<br> Gladiator's Mail Helm<br> Gladiator's Mail Leggings<br> Gladiator's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMailLeggings; ++i;



var fGladiatorsMailHelm = new RewardItem("alliance","Gladiator's Mail Helm","/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGladiatorsMailHelm.itemHonorPrice = new Array();
fGladiatorsMailHelm.itemHonorPrice[6] = 1875
fGladiatorsMailHelm.itemStats = new Array();
fGladiatorsMailHelm.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mail Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>632 Armor<br>+48 Stamina<br>+12 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Thunderfist (0/5)</span>\
<br> Gladiator's Mail Armor<br> Gladiator's Mail Gauntlets<br> Gladiator's Mail Helm<br> Gladiator's Mail Leggings<br> Gladiator's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMailHelm; ++i;



var fGladiatorsMailArmor = new RewardItem("alliance","Gladiator's Mail Armor","/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGladiatorsMailArmor.itemHonorPrice = new Array();
fGladiatorsMailArmor.itemHonorPrice[6] = 1875
fGladiatorsMailArmor.itemStats = new Array();
fGladiatorsMailArmor.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Mail Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>812 Armor<br>+39 Stamina<br>+21 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 140 / 140<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Thunderfist (0/5)</span>\
<br> Gladiator's Mail Armor<br> Gladiator's Mail Gauntlets<br> Gladiator's Mail Helm<br> Gladiator's Mail Leggings<br> Gladiator's Mail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Improves your chance to get a critical strike with all Shock spells by 2%.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMailArmor; ++i;



//SHAMAN SET 3-------------------------

var fGladiatorsRingmailGauntlets = new RewardItem("alliance","Gladiator's Ringmail Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_11.gif");
fGladiatorsRingmailGauntlets.itemHonorPrice = new Array();
fGladiatorsRingmailGauntlets.itemHonorPrice[6] = 1125
fGladiatorsRingmailGauntlets.itemStats = new Array();
fGladiatorsRingmailGauntlets.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ringmail Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>486 Armor<br>+33 Stamina<br>+16 Intellect<br>Durability 50 / 50<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the critical effect chance of your Lesser Healing Wave by 2%.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 53.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wartide (0/5)</span>\
<br> Gladiator's Ringmail Armor<br> Gladiator's Ringmail Gauntlets<br> Gladiator's Ringmail Helm<br> Gladiator's Ringmail Leggings<br> Gladiator's Ringmail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsRingmailGauntlets; ++i;


var fGladiatorsRingmailSpaulders = new RewardItem("alliance","Gladiator's Ringmail Spaulders","/info/basics/factions/images/icons/INV_Shoulder_29.gif");
fGladiatorsRingmailSpaulders.itemHonorPrice = new Array();
fGladiatorsRingmailSpaulders.itemHonorPrice[6] = 1500
fGladiatorsRingmailSpaulders.itemStats = new Array();
fGladiatorsRingmailSpaulders.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ringmail Spaulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>583 Armor<br>+30 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 35.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wartide (0/5)</span>\
<br> Gladiator's Ringmail Armor<br> Gladiator's Ringmail Gauntlets<br> Gladiator's Ringmail Helm<br> Gladiator's Ringmail Leggings<br> Gladiator's Ringmail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsRingmailSpaulders; ++i;

var fGladiatorsRingmailLeggings = new RewardItem("alliance","Gladiator's Ringmail Leggings","/info/basics/factions/images/icons/INV_Pants_Mail_15.gif");
fGladiatorsRingmailLeggings.itemHonorPrice = new Array();
fGladiatorsRingmailLeggings.itemHonorPrice[6] = 1875
fGladiatorsRingmailLeggings.itemStats = new Array();
fGladiatorsRingmailLeggings.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ringmail Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>681 Armor<br>+48 Stamina<br>+22 Intellect<br>Durability 105 / 105<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 70.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wartide (0/5)</span>\
<br> Gladiator's Ringmail Armor<br> Gladiator's Ringmail Gauntlets<br> Gladiator's Ringmail Helm<br> Gladiator's Ringmail Leggings<br> Gladiator's Ringmail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsRingmailLeggings; ++i;

var fGladiatorsRingmailHelm = new RewardItem("alliance","Gladiator's Ringmail Helm","/info/basics/factions/images/icons/INV_Helmet_09.gif");
fGladiatorsRingmailHelm.itemHonorPrice = new Array();
fGladiatorsRingmailHelm.itemHonorPrice[6] = 1875
fGladiatorsRingmailHelm.itemStats = new Array();
fGladiatorsRingmailHelm.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ringmail Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>632 Armor<br>+48 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 85 / 85<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 53.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wartide (0/5)</span>\
<br> Gladiator's Ringmail Armor<br> Gladiator's Ringmail Gauntlets<br> Gladiator's Ringmail Helm<br> Gladiator's Ringmail Leggings<br> Gladiator's Ringmail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsRingmailHelm; ++i;




var fGladiatorsRingmailArmor = new RewardItem("alliance","Gladiator's Ringmail Armor","/info/basics/factions/images/icons/INV_Chest_Chain_12.gif");
fGladiatorsRingmailArmor.itemHonorPrice = new Array();
fGladiatorsRingmailArmor.itemHonorPrice[6] = 1875
fGladiatorsRingmailArmor.itemStats = new Array();
fGladiatorsRingmailArmor.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Ringmail Armor</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>812 Armor<br>+39 Stamina<br>+21 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 140 / 140<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 55.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Wartide (0/5)</span>\
<br> Gladiator's Ringmail Armor<br> Gladiator's Ringmail Gauntlets<br> Gladiator's Ringmail Helm<br> Gladiator's Ringmail Leggings<br> Gladiator's Ringmail Spaulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown on your Nature's Swiftness ability by 24 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsRingmailArmor; ++i;



//WARLOCK---------------------------------
//WARLOCK SET 1

var fGladiatorsDreadweaveGloves = new RewardItem("alliance","Gladiator's Dreadweave Gloves","/info/basics/factions/images/icons/INV_Gauntlets_15.gif");
fGladiatorsDreadweaveGloves.itemHonorPrice = new Array();
fGladiatorsDreadweaveGloves.itemHonorPrice[7] = 1125
fGladiatorsDreadweaveGloves.itemStats = new Array();
fGladiatorsDreadweaveGloves.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dreadweave Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>116 Armor<br>+36 Stamina<br>+22 Intellect<br>Durability 35 / 35<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Gives you a 50% chance to avoid interruption caused by damage while casting Fear.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Dreadgear (0/5)</span>\
<br> Gladiator's Dreadweave Gloves<br> Gladiator's Dreadweave Hood<br> Gladiator's Dreadweave Leggings<br> Gladiator's Dreadweave Mantle<br> Gladiator's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDreadweaveGloves; ++i;

var fGladiatorsDreadweaveMantle = new RewardItem("alliance","Gladiator's Dreadweave Mantle","/info/basics/factions/images/icons/INV_Shoulder_02.gif");
fGladiatorsDreadweaveMantle.itemHonorPrice = new Array();
fGladiatorsDreadweaveMantle.itemHonorPrice[7] = 1500
fGladiatorsDreadweaveMantle.itemStats = new Array();
fGladiatorsDreadweaveMantle.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dreadweave Mantle</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>140 Armor<br>+39 Stamina<br>+11 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Dreadgear (0/5)</span>\
<br> Gladiator's Dreadweave Gloves<br> Gladiator's Dreadweave Hood<br> Gladiator's Dreadweave Leggings<br> Gladiator's Dreadweave Mantle<br> Gladiator's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDreadweaveMantle; ++i;


var fGladiatorsDreadweaveLeggings = new RewardItem("alliance","Gladiator's Dreadweave Leggings","/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fGladiatorsDreadweaveLeggings.itemHonorPrice = new Array();
fGladiatorsDreadweaveLeggings.itemHonorPrice[7] = 1875
fGladiatorsDreadweaveLeggings.itemStats = new Array();
fGladiatorsDreadweaveLeggings.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dreadweave Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>163 Armor<br>+54 Stamina<br>+26 Intellect<br>Durability 75 / 75<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 42.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Dreadgear (0/5)</span>\
<br> Gladiator's Dreadweave Gloves<br> Gladiator's Dreadweave Hood<br> Gladiator's Dreadweave Leggings<br> Gladiator's Dreadweave Mantle<br> Gladiator's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDreadweaveLeggings; ++i;




var fGladiatorsDreadweaveHood = new RewardItem("alliance","Gladiator's Dreadweave Hood","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fGladiatorsDreadweaveHood.itemHonorPrice = new Array();
fGladiatorsDreadweaveHood.itemHonorPrice[7] = 1875
fGladiatorsDreadweaveHood.itemStats = new Array();
fGladiatorsDreadweaveHood.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dreadweave Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>151 Armor<br>+54 Stamina<br>+16 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Dreadgear (0/5)</span>\
<br> Gladiator's Dreadweave Gloves<br> Gladiator's Dreadweave Hood<br> Gladiator's Dreadweave Leggings<br> Gladiator's Dreadweave Mantle<br> Gladiator's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDreadweaveHood; ++i;





var fGladiatorsDreadweaveRobe = new RewardItem("alliance","Gladiator's Dreadweave Robe","/info/basics/factions/images/icons/INV_Chest_Cloth_43.gif");
fGladiatorsDreadweaveRobe.itemHonorPrice = new Array();
fGladiatorsDreadweaveRobe.itemHonorPrice[7] = 1875
fGladiatorsDreadweaveRobe.itemStats = new Array();
fGladiatorsDreadweaveRobe.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Dreadweave Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>194 Armor<br>+54 Stamina<br>+17 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Resilience</span>\
<br>Durability 100 / 100<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Dreadgear (0/5)</span>\
<br> Gladiator's Dreadweave Gloves<br> Gladiator's Dreadweave Hood<br> Gladiator's Dreadweave Leggings<br> Gladiator's Dreadweave Mantle<br> Gladiator's Dreadweave Robe<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDreadweaveRobe; ++i;




//WARLOCK SET 2
var fGladiatorsFelweaveHandguards = new RewardItem("alliance","Gladiator's Felweave Handguards","/info/basics/factions/images/icons/INV_Gauntlets_19.gif");
fGladiatorsFelweaveHandguards.itemHonorPrice = new Array();
fGladiatorsFelweaveHandguards.itemHonorPrice[7] = 1125
fGladiatorsFelweaveHandguards.itemStats = new Array();
fGladiatorsFelweaveHandguards.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Felweave Handguards</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>116 Armor<br>+36 Stamina<br>+12 Intellect<br>Durability 35 / 35<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Gives you a 50% chance to avoid interruption caused by damage while casting Searing Pain.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Felshroud (0/5)</span>\
<br> Gladiator's Felweave Amice<br> Gladiator's Felweave Cowl<br> Gladiator's Felweave Handguards<br> Gladiator's Felweave Raiment<br> Gladiator's Felweave Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsFelweaveHandguards; ++i;

var fGladiatorsFelweaveAmice = new RewardItem("alliance","Gladiator's Felweave Amice","/info/basics/factions/images/icons/INV_Shoulder_19.gif");
fGladiatorsFelweaveAmice.itemHonorPrice = new Array();
fGladiatorsFelweaveAmice.itemHonorPrice[7] = 1500
fGladiatorsFelweaveAmice.itemStats = new Array();
fGladiatorsFelweaveAmice.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Felweave Amice</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Cloth</span>\
<br>140 Armor<br>+36 Stamina<br>+11 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Felshroud (0/5)</span>\
<br> Gladiator's Felweave Amice<br> Gladiator's Felweave Cowl<br> Gladiator's Felweave Handguards<br> Gladiator's Felweave Raiment<br> Gladiator's Felweave Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsFelweaveAmice; ++i;


var fGladiatorsFelweaveTrousers = new RewardItem("alliance","Gladiator's Felweave Trousers","/info/basics/factions/images/icons/INV_Pants_07.gif");
fGladiatorsFelweaveTrousers.itemHonorPrice = new Array();
fGladiatorsFelweaveTrousers.itemHonorPrice[7] = 1875
fGladiatorsFelweaveTrousers.itemStats = new Array();
fGladiatorsFelweaveTrousers.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Felweave Trousers</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>163 Armor<br>+48 Stamina<br>+22 Intellect<br>Durability 75 / 75<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 37.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Felshroud (0/5)</span>\
<br> Gladiator's Felweave Amice<br> Gladiator's Felweave Cowl<br> Gladiator's Felweave Handguards<br> Gladiator's Felweave Raiment<br> Gladiator's Felweave Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsFelweaveTrousers; ++i;



var fGladiatorsFelweaveCowl = new RewardItem("alliance","Gladiator's Felweave Cowl","/info/basics/factions/images/icons/INV_Helmet_08.gif");
fGladiatorsFelweaveCowl.itemHonorPrice = new Array();
fGladiatorsFelweaveCowl.itemHonorPrice[7] = 1875
fGladiatorsFelweaveCowl.itemStats = new Array();
fGladiatorsFelweaveCowl.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Felweave Cowl</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>151 Armor<br>+48 Stamina<br>+12 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 60 / 60<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Felshroud (0/5)</span>\
<br> Gladiator's Felweave Amice<br> Gladiator's Felweave Cowl<br> Gladiator's Felweave Handguards<br> Gladiator's Felweave Raiment<br> Gladiator's Felweave Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsFelweaveCowl; ++i;



var fGladiatorsFelweaveRaiment = new RewardItem("alliance","Gladiator's Felweave Raiment","/info/basics/factions/images/icons/INV_Chest_Leather_01.gif");
fGladiatorsFelweaveRaiment.itemHonorPrice = new Array();
fGladiatorsFelweaveRaiment.itemHonorPrice[7] = 1875
fGladiatorsFelweaveRaiment.itemStats = new Array();
fGladiatorsFelweaveRaiment.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Felweave Raiment</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>194 Armor<br>+48 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Critical Strike Rating</span>\
<br>Durability 100 / 100<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Felshroud (0/5)</span>\
<br> Gladiator's Felweave Amice<br> Gladiator's Felweave Cowl<br> Gladiator's Felweave Handguards<br> Gladiator's Felweave Raiment<br> Gladiator's Felweave Trousers<br>\
<br>\
<span class=\"myGray\">(2) Set: +35  Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the casting time of your Immolate spell by 0.2  sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsFelweaveRaiment; ++i;


//WARRIOR----------------------------------------
var fGladiatorsPlateGauntlets = new RewardItem("alliance","Gladiator's Plate Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_29.gif");
fGladiatorsPlateGauntlets.itemHonorPrice = new Array();
fGladiatorsPlateGauntlets.itemHonorPrice[8] = 1125
fGladiatorsPlateGauntlets.itemStats = new Array();
fGladiatorsPlateGauntlets.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Plate Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>868 Armor<br>+24 Strength<br>+36 Stamina<br>Durability 55 / 55<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Hamstring Rage cost reduced by 3.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Battlegear (0/5)</span>\
<br> Gladiator's Plate Chestpiece<br> Gladiator's Plate Gauntlets<br> Gladiator's Plate Helm<br> Gladiator's Plate Legguards<br> Gladiator's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsPlateGauntlets; ++i;

var fGladiatorsPlateShoulders = new RewardItem("alliance","Gladiator's Plate Shoulders","/info/basics/factions/images/icons/INV_Shoulder_22.gif");
fGladiatorsPlateShoulders.itemHonorPrice = new Array();
fGladiatorsPlateShoulders.itemHonorPrice[8] = 1500
fGladiatorsPlateShoulders.itemStats = new Array();
fGladiatorsPlateShoulders.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Plate Shoulders</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>1042 Armor<br>+16 Strength<br>+39 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Battlegear (0/5)</span>\
<br> Gladiator's Plate Chestpiece<br> Gladiator's Plate Gauntlets<br> Gladiator's Plate Helm<br> Gladiator's Plate Legguards<br> Gladiator's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsPlateShoulders; ++i;


var fGladiatorsPlateLegguards = new RewardItem("alliance","Gladiator's Plate Legguards","/info/basics/factions/images/icons/INV_Pants_Plate_17.gif");
fGladiatorsPlateLegguards.itemHonorPrice = new Array();
fGladiatorsPlateLegguards.itemHonorPrice[8] = 1875
fGladiatorsPlateLegguards.itemStats = new Array();
fGladiatorsPlateLegguards.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Plate Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1216 Armor<br>+32 Strength<br>+54 Stamina<br>Durability 120 / 120<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Battlegear (0/5)</span>\
<br> Gladiator's Plate Chestpiece<br> Gladiator's Plate Gauntlets<br> Gladiator's Plate Helm<br> Gladiator's Plate Legguards<br> Gladiator's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsPlateLegguards; ++i;

var fGladiatorsPlateHelm = new RewardItem("alliance","Gladiator's Plate Helm","/info/basics/factions/images/icons/INV_Helmet_22.gif");
fGladiatorsPlateHelm.itemHonorPrice = new Array();
fGladiatorsPlateHelm.itemHonorPrice[8] = 1875
fGladiatorsPlateHelm.itemStats = new Array();
fGladiatorsPlateHelm.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Plate Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>1129 Armor<br>+26 Strength<br>+48 Stamina<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 100 / 100<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Battlegear (0/5)</span>\
<br> Gladiator's Plate Chestpiece<br> Gladiator's Plate Gauntlets<br> Gladiator's Plate Helm<br> Gladiator's Plate Legguards<br> Gladiator's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
<br>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsPlateHelm; ++i;

var fGladiatorsPlateChestpiece = new RewardItem("alliance","Gladiator's Plate Chestpiece","/info/basics/factions/images/icons/INV_Chest_Plate06.gif");
fGladiatorsPlateChestpiece.itemHonorPrice = new Array();
fGladiatorsPlateChestpiece.itemHonorPrice[8] = 1875
fGladiatorsPlateChestpiece.itemStats = new Array();
fGladiatorsPlateChestpiece.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Plate Chestpiece</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1450 Armor<br>+21 Strength<br>+48 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 165 / 165<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<br>\
<span class=\"myYellow\">Gladiator's Battlegear (0/5)</span>\
<br>Gladiator's Plate Chestpiece<br> Gladiator's Plate Gauntlets<br> Gladiator's Plate Helm<br>\
Gladiator's Plate Legguards<br> Gladiator's Plate Shoulders<br>\
<br>\
<span class=\"myGray\">(2) Set: +35 Resilience.</span>\
<br>\
<span class=\"myGray\">(4) Set: Reduces the cooldown of your Intercept ability by 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsPlateChestpiece; ++i;


//-------------------------------------------------------------------
//---Horde below



//------END REWARDS DEFINITION------
