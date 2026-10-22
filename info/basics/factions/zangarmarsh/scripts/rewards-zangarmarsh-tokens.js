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

tokenIcons = new Array("honorholdtoken","arathi","nether","warsong");
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
			if (thisObject.itemTokenPrice[thisBracket][carl] > 0) outPutString += thisObject.itemTokenPrice[thisBracket][carl]+"<img src='/info/basics/factions/images/icons/"+tokenIcons[carl]+".gif'>&nbsp;";
		}
	}
	return outPutString;
}

//------BEGIN REWARDS DEFINITION------
i = 0;
var RewardItems = new Array();

var fTerminalEdge = new RewardItem("alliance","Terminal Edge","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalscleaver.gif");
fTerminalEdge.itemTokenPrice = new Array();
fTerminalEdge.itemTokenPrice[0] = new Array(15,0,0,0);
fTerminalEdge.itemStats = new Array();
fTerminalEdge.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Terminal Edge</span>\
<br>Binds when picked up<br>Thrown<span class=\"myRight\">Thrown</span>\
<br>63 - 96 Damage<span class=\"myRight\">Speed 1.60</span>\
<br>(49.7 damage per second)<br>+7 Stamina<br>Durability 240 / 240<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTerminalEdge; ++i;

var fSplintermark = new RewardItem("alliance","Splintermark","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Weapon_Bow_04.gif");
fSplintermark.itemTokenPrice = new Array();
fSplintermark.itemTokenPrice[0] = new Array(15,0,0,0);
fSplintermark.itemStats = new Array();
fSplintermark.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Splintermark</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>93 - 174 Damage<span class=\"myRight\">Speed 2.50</span>\
<br>(53.4 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSplintermark; ++i;

var fIncendicRod = new RewardItem("alliance","Incendic Rod","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Wand_11.jpg");
fIncendicRod.itemTokenPrice = new Array();
fIncendicRod.itemTokenPrice[0] = new Array(15,0,0,0);
fIncendicRod.itemStats = new Array();
fIncendicRod.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Incendic Rod</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Wand</span>\
<br>129 - 240 Fire Damage<span class=\"myRight\">Speed 1.90</span>\
<br>(97.1 damage per second)<br>+8 Stamina<br>Durability 65 / 65<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIncendicRod; ++i;

var fLibramOfZeal = new RewardItem("alliance","Libram of Zeal","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_LibramofTruth.gif&reason=external-or-uncollected-resource");
fLibramOfZeal.itemTokenPrice = new Array();
fLibramOfZeal.itemTokenPrice[0] = new Array(15,0,0,0);
fLibramOfZeal.itemStats = new Array();
fLibramOfZeal.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Libram of Zeal</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Libram</span>\
<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases the melee attack power bonus of your Seal of the Crusader by 68 and the Holy damage increase of your Judgement of the Crusader by 47.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLibramOfZeal; ++i;

var fTotemOfImpact = new RewardItem("alliance","Totem of Impact","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Ftotemofimpact.gif&reason=external-or-uncollected-resource");
fTotemOfImpact.itemTokenPrice = new Array();
fTotemOfImpact.itemTokenPrice[0] = new Array(15,0,0,0);
fTotemOfImpact.itemStats = new Array();
fTotemOfImpact.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Totem of Impact</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Totem</span>\
<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases damage done by Earth Shock, Flame Shock, and Frost Shock by up to 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTotemOfImpact; ++i;

var fIdolOfSavagery = new RewardItem("alliance","Idol of Savagery","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fidolofsavagery.gif&reason=external-or-uncollected-resource");
fIdolOfSavagery.itemTokenPrice = new Array();
fIdolOfSavagery.itemTokenPrice[0] = new Array(15,0,0,0);
fIdolOfSavagery.itemStats = new Array();
fIdolOfSavagery.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Idol of Savagery</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Idol</span>\
<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases the damage of your Claw and Rake abilites by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIdolOfSavagery; ++i;

var fMarkOfDefiance = new RewardItem("alliance","Mark of Defiance","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Necklace_16.gif&reason=external-or-uncollected-resource");
fMarkOfDefiance.itemTokenPrice = new Array();
fMarkOfDefiance.itemTokenPrice[0] = new Array(30,0,0,0);
fMarkOfDefiance.itemStats = new Array();
fMarkOfDefiance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Mark of Defiance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Priest, Mage, Warlock<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Chance on spell hit to restore 128 to 172 mana to the bearer.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarkOfDefiance; ++i;

var fMarkOfConquest = new RewardItem("alliance","Mark of Conquest","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_ArmorKit_12.gif&reason=external-or-uncollected-resource");
fMarkOfConquest.itemTokenPrice = new Array();
fMarkOfConquest.itemTokenPrice[0] = new Array(30,0,0,0);
fMarkOfConquest.itemStats = new Array();
fMarkOfConquest.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Mark of Conquest</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warrior, Hunter, Rogue, Druid<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases attack power by 54.</span>\
<br>\
<span class=\"myGreen\">Equip: Sometimes heals the bearer of 90 to 120 damage when damaging an enemy in melee and chance on ranged hit to restore 128 to 172 mana to the bearer.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarkOfConquest; ++i;

var fMarkOfVindication = new RewardItem("alliance","Mark of Vindication","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_QirajiIdol_Sun.gif&reason=external-or-uncollected-resource");
fMarkOfVindication.itemTokenPrice = new Array();
fMarkOfVindication.itemTokenPrice[0] = new Array(30,0,0,0);
fMarkOfVindication.itemStats = new Array();
fMarkOfVindication.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Mark of Vindication</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Paladin, Shaman<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases attack power by 54.</span>\
<br>\
<span class=\"myGreen\">Equip: Chance on spell hit to restore 128 to 172 mana to the bearer.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarkOfVindication; ++i;

//-------------------------------------------------------------------
//---Horde below

var fTerminalEdge = new RewardItem("horde","Terminal Edge","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalscleaver.gif");
fTerminalEdge.itemTokenPrice = new Array();
fTerminalEdge.itemTokenPrice[0] = new Array(15,0,0,0);
fTerminalEdge.itemStats = new Array();
fTerminalEdge.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Terminal Edge</span>\
<br>Binds when picked up<br>Thrown<span class=\"myRight\">Thrown</span>\
<br>63 - 96 Damage<span class=\"myRight\">Speed 1.60</span>\
<br>(49.7 damage per second)<br>+7 Stamina<br>Durability 240 / 240<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTerminalEdge; ++i;

var fSplintermark = new RewardItem("horde","Splintermark","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Weapon_Bow_04.gif");
fSplintermark.itemTokenPrice = new Array();
fSplintermark.itemTokenPrice[0] = new Array(15,0,0,0);
fSplintermark.itemStats = new Array();
fSplintermark.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Splintermark</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>93 - 174 Damage<span class=\"myRight\">Speed 2.50</span>\
<br>(53.4 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSplintermark; ++i;

var fIncendicRod = new RewardItem("horde","Incendic Rod","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Wand_11.jpg");
fIncendicRod.itemTokenPrice = new Array();
fIncendicRod.itemTokenPrice[0] = new Array(15,0,0,0);
fIncendicRod.itemStats = new Array();
fIncendicRod.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Incendic Rod</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Wand</span>\
<br>129 - 240 Fire Damage<span class=\"myRight\">Speed 1.90</span>\
<br>(97.1 damage per second)<br>+8 Stamina<br>Durability 65 / 65<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIncendicRod; ++i;

var fLibramOfZeal = new RewardItem("horde","Libram of Zeal","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_LibramofTruth.gif&reason=external-or-uncollected-resource");
fLibramOfZeal.itemTokenPrice = new Array();
fLibramOfZeal.itemTokenPrice[0] = new Array(15,0,0,0);
fLibramOfZeal.itemStats = new Array();
fLibramOfZeal.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Libram of Zeal</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Libram</span>\
<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases the melee attack power bonus of your Seal of the Crusader by 68 and the Holy damage increase of your Judgement of the Crusader by 47.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLibramOfZeal; ++i;

var fTotemOfImpact = new RewardItem("horde","Totem of Impact","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Ftotemofimpact.gif&reason=external-or-uncollected-resource");
fTotemOfImpact.itemTokenPrice = new Array();
fTotemOfImpact.itemTokenPrice[0] = new Array(15,0,0,0);
fTotemOfImpact.itemStats = new Array();
fTotemOfImpact.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Totem of Impact</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Totem</span>\
<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases damage done by Earth Shock, Flame Shock, and Frost Shock by up to 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTotemOfImpact; ++i;

var fIdolOfSavagery = new RewardItem("horde","Idol of Savagery","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fidolofsavagery.gif&reason=external-or-uncollected-resource");
fIdolOfSavagery.itemTokenPrice = new Array();
fIdolOfSavagery.itemTokenPrice[0] = new Array(15,0,0,0);
fIdolOfSavagery.itemStats = new Array();
fIdolOfSavagery.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Idol of Savagery</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Idol</span>\
<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases the damage of your Claw and Rake abilites by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIdolOfSavagery; ++i;

var fMarkOfDefiance = new RewardItem("horde","Mark of Defiance","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Necklace_16.gif&reason=external-or-uncollected-resource");
fMarkOfDefiance.itemTokenPrice = new Array();
fMarkOfDefiance.itemTokenPrice[0] = new Array(30,0,0,0);
fMarkOfDefiance.itemStats = new Array();
fMarkOfDefiance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Mark of Defiance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Priest, Mage, Warlock<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Chance on spell hit to restore 128 to 172 mana to the bearer.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarkOfDefiance; ++i;


var fMarkOfConquest = new RewardItem("horde","Mark of Conquest","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_ArmorKit_12.gif&reason=external-or-uncollected-resource");
fMarkOfConquest.itemTokenPrice = new Array();
fMarkOfConquest.itemTokenPrice[0] = new Array(30,0,0,0);
fMarkOfConquest.itemStats = new Array();
fMarkOfConquest.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Mark of Conquest</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warrior, Hunter, Rogue, Druid<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases attack power by 54.</span>\
<br>\
<span class=\"myGreen\">Equip: Sometimes heals the bearer of 90 to 120 damage when damaging an enemy in melee and chance on ranged hit to restore 128 to 172 mana to the bearer.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarkOfConquest; ++i;

var fMarkOfVindication = new RewardItem("horde","Mark of Vindication","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzangarmarsh%2Fscripts%2Frewards-zangarmarsh-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_QirajiIdol_Sun.gif&reason=external-or-uncollected-resource");
fMarkOfVindication.itemTokenPrice = new Array();
fMarkOfVindication.itemTokenPrice[0] = new Array(30,0,0,0);
fMarkOfVindication.itemStats = new Array();
fMarkOfVindication.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Mark of Vindication</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Paladin, Shaman<br>Requires Level 62<br>\
<span class=\"myGreen\">Equip: Increases attack power by 54.</span>\
<br>\
<span class=\"myGreen\">Equip: Chance on spell hit to restore 128 to 172 mana to the bearer.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarkOfVindication; ++i;




//------END REWARDS DEFINITION------
