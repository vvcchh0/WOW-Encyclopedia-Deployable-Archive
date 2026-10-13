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

var fSergeantsHeavyCloak = new RewardItem("alliance","Sergeant's Heavy Cloak","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Misc_Cape_07.gif");
fSergeantsHeavyCloak.itemHonorPrice = new Array();
fSergeantsHeavyCloak.itemHonorPrice[0] = 9435
fSergeantsHeavyCloak.itemTokenPrice = new Array();
fSergeantsHeavyCloak.itemTokenPrice[0] = new Array(0,20,0,0);
fSergeantsHeavyCloak.itemStats = new Array();
fSergeantsHeavyCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sergeant's Heavy Cloak</span>\
<br>Binds when picked up<br>Back<br>104 Armor<br>+27 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsHeavyCloak; ++i;

var fSergeantsHeavyCape = new RewardItem("alliance","Sergeant's Heavy Cape","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Misc_Cape_07.gif");
fSergeantsHeavyCape.itemHonorPrice = new Array();
fSergeantsHeavyCape.itemHonorPrice[0] = 9435
fSergeantsHeavyCape.itemTokenPrice = new Array();
fSergeantsHeavyCape.itemTokenPrice[0] = new Array(0,20,0,0);
fSergeantsHeavyCape.itemStats = new Array();
fSergeantsHeavyCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sergeant's Heavy Cape</span>\
<br>Binds when picked up<br>Back<br>104 Armor<br>+33 Stamina<br>+12 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsHeavyCape; ++i;


var fMarshalsSilkCuffs = new RewardItem("alliance","Marshal's Silk Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsSilkCuffs.itemHonorPrice = new Array();
fMarshalsSilkCuffs.itemHonorPrice[0] = 9435
fMarshalsSilkCuffs.itemTokenPrice = new Array();
fMarshalsSilkCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsSilkCuffs.itemStats = new Array();
fMarshalsSilkCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Silk Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>84 Armor<br>+22 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsSilkCuffs; ++i;


var fMarshalsDreadweaveCuffs = new RewardItem("alliance","Marshal's Dreadweave Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsDreadweaveCuffs.itemHonorPrice = new Array();
fMarshalsDreadweaveCuffs.itemHonorPrice[0] = 9435
fMarshalsDreadweaveCuffs.itemTokenPrice = new Array();
fMarshalsDreadweaveCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsDreadweaveCuffs.itemStats = new Array();
fMarshalsDreadweaveCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Dreadweave Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>84 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDreadweaveCuffs; ++i;

var fMarshalsSilkBelt = new RewardItem("alliance","Marshal's Silk Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsSilkBelt.itemHonorPrice = new Array();
fMarshalsSilkBelt.itemHonorPrice[0] = 14280
fMarshalsSilkBelt.itemTokenPrice = new Array();
fMarshalsSilkBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsSilkBelt.itemStats = new Array();
fMarshalsSilkBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Silk Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+33 Stamina<br>+23 Intellect<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsSilkBelt; ++i;

var fMarshalsDreadweaveBelt = new RewardItem("alliance","Marshal's Dreadweave Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsDreadweaveBelt.itemHonorPrice = new Array();
fMarshalsDreadweaveBelt.itemHonorPrice[0] = 14280
fMarshalsDreadweaveBelt.itemTokenPrice = new Array();
fMarshalsDreadweaveBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsDreadweaveBelt.itemStats = new Array();
fMarshalsDreadweaveBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Dreadweave Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+39 Stamina<br>+27 Intellect<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDreadweaveBelt; ++i;

var fMarshalsSilkFootguards = new RewardItem("alliance","Marshal's Silk Footguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fMarshalsSilkFootguards.itemHonorPrice = new Array();
fMarshalsSilkFootguards.itemHonorPrice[0] = 14280
fMarshalsSilkFootguards.itemTokenPrice = new Array();
fMarshalsSilkFootguards.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsSilkFootguards.itemStats = new Array();
fMarshalsSilkFootguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Silk Footguards</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>142 Armor<br>+33 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsSilkFootguards; ++i;

var fMarshalsDreadweaveStalkers = new RewardItem("alliance","Marshal's Dreadweave Stalkers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fMarshalsDreadweaveStalkers.itemHonorPrice = new Array();
fMarshalsDreadweaveStalkers.itemHonorPrice[0] = 14280
fMarshalsDreadweaveStalkers.itemTokenPrice = new Array();
fMarshalsDreadweaveStalkers.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsDreadweaveStalkers.itemStats = new Array();
fMarshalsDreadweaveStalkers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Dreadweave Stalkers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>142 Armor<br>+40 Stamina<br>+27 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDreadweaveStalkers; ++i;

var fMarshalsLeatherBracers = new RewardItem("alliance","Marshal's Leather Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsLeatherBracers.itemHonorPrice = new Array();
fMarshalsLeatherBracers.itemHonorPrice[0] = 9435
fMarshalsLeatherBracers.itemTokenPrice = new Array();
fMarshalsLeatherBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsLeatherBracers.itemStats = new Array();
fMarshalsLeatherBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Leather Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>157 Armor<br>+19 Agility<br>+25 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 7.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLeatherBracers; ++i;

var fMarshalsDragonhideBracers = new RewardItem("alliance","Marshal's Dragonhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsDragonhideBracers.itemHonorPrice = new Array();
fMarshalsDragonhideBracers.itemHonorPrice[0] = 9435
fMarshalsDragonhideBracers.itemTokenPrice = new Array();
fMarshalsDragonhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsDragonhideBracers.itemStats = new Array();
fMarshalsDragonhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Dragonhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+16 Strength<br>+13 Agility<br>+22 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 13.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDragonhideBracers; ++i;

var fMarshalsWyrmhideBracers = new RewardItem("alliance","Marshal's Wyrmhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsWyrmhideBracers.itemHonorPrice = new Array();
fMarshalsWyrmhideBracers.itemHonorPrice[0] = 9435
fMarshalsWyrmhideBracers.itemTokenPrice = new Array();
fMarshalsWyrmhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsWyrmhideBracers.itemStats = new Array();
fMarshalsWyrmhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Wyrmhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>187 Armor<br>+22 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsWyrmhideBracers; ++i;

var fMarshalsKodohideBracers = new RewardItem("alliance","Marshal's Kodohide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsKodohideBracers.itemHonorPrice = new Array();
fMarshalsKodohideBracers.itemHonorPrice[0] = 9435
fMarshalsKodohideBracers.itemTokenPrice = new Array();
fMarshalsKodohideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsKodohideBracers.itemStats = new Array();
fMarshalsKodohideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Kodohide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>187 Armor<br>+22 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsKodohideBracers; ++i;

var fMarshalsLeatherBelt = new RewardItem("alliance","Marshal's Leather Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsLeatherBelt.itemHonorPrice = new Array();
fMarshalsLeatherBelt.itemHonorPrice[0] = 14280
fMarshalsLeatherBelt.itemTokenPrice = new Array();
fMarshalsLeatherBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsLeatherBelt.itemStats = new Array();
fMarshalsLeatherBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Leather Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>219 Armor<br>+27 Agility<br>+39 Stamina<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLeatherBelt; ++i;

var fMarshalsDragonhideBelt = new RewardItem("alliance","Marshal's Dragonhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsDragonhideBelt.itemHonorPrice = new Array();
fMarshalsDragonhideBelt.itemHonorPrice[0] = 14280
fMarshalsDragonhideBelt.itemTokenPrice = new Array();
fMarshalsDragonhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsDragonhideBelt.itemStats = new Array();
fMarshalsDragonhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Dragonhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>259 Armor<br>+24 Strength<br>+24 Agility<br>+33 Stamina<br>+15 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 37.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDragonhideBelt; ++i;

var fMarshalsWyrmhideBelt = new RewardItem("alliance","Marshal's Wyrmhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsWyrmhideBelt.itemHonorPrice = new Array();
fMarshalsWyrmhideBelt.itemHonorPrice[0] = 14280
fMarshalsWyrmhideBelt.itemTokenPrice = new Array();
fMarshalsWyrmhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsWyrmhideBelt.itemStats = new Array();
fMarshalsWyrmhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Wyrmhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>259 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsWyrmhideBelt; ++i;

var fMarshalsKodohideBelt = new RewardItem("alliance","Marshal's Kodohide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsKodohideBelt.itemHonorPrice = new Array();
fMarshalsKodohideBelt.itemHonorPrice[0] = 14280
fMarshalsKodohideBelt.itemTokenPrice = new Array();
fMarshalsKodohideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsKodohideBelt.itemStats = new Array();
fMarshalsKodohideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Kodohide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>259 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 62.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsKodohideBelt; ++i;

var fMarshalsLeatherBoots = new RewardItem("alliance","Marshal's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsLeatherBoots.itemHonorPrice = new Array();
fMarshalsLeatherBoots.itemHonorPrice[0] = 14280
fMarshalsLeatherBoots.itemTokenPrice = new Array();
fMarshalsLeatherBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsLeatherBoots.itemStats = new Array();
fMarshalsLeatherBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Leather Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+27 Agility<br>+39 Stamina<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLeatherBoots; ++i;

var fMarshalsDragonhideBoots = new RewardItem("alliance","Marshal's Dragonhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsDragonhideBoots.itemHonorPrice = new Array();
fMarshalsDragonhideBoots.itemHonorPrice[0] = 14280
fMarshalsDragonhideBoots.itemTokenPrice = new Array();
fMarshalsDragonhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsDragonhideBoots.itemStats = new Array();
fMarshalsDragonhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Dragonhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>309 Armor<br>+24 Strength<br>+24 Agility<br>+33 Stamina<br>+15 Intellect<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 37.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDragonhideBoots; ++i;

var fMarshalsWyrmhideBoots = new RewardItem("alliance","Marshal's Wyrmhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsWyrmhideBoots.itemHonorPrice = new Array();
fMarshalsWyrmhideBoots.itemHonorPrice[0] = 14280
fMarshalsWyrmhideBoots.itemTokenPrice = new Array();
fMarshalsWyrmhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsWyrmhideBoots.itemStats = new Array();
fMarshalsWyrmhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Wyrmhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>307 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsWyrmhideBoots; ++i;

var fMarshalsKodohideBoots = new RewardItem("alliance","Marshal's Kodohide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsKodohideBoots.itemHonorPrice = new Array();
fMarshalsKodohideBoots.itemHonorPrice[0] = 14280
fMarshalsKodohideBoots.itemTokenPrice = new Array();
fMarshalsKodohideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsKodohideBoots.itemStats = new Array();
fMarshalsKodohideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Kodohide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>307 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 62.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsKodohideBoots; ++i;


var fMarshalsChainBracers = new RewardItem("alliance","Marshal's Chain Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fMarshalsChainBracers.itemHonorPrice = new Array();
fMarshalsChainBracers.itemHonorPrice[0] = 9435
fMarshalsChainBracers.itemTokenPrice = new Array();
fMarshalsChainBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsChainBracers.itemStats = new Array();
fMarshalsChainBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Chain Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>349 Armor<br>+18 Agility<br>+25 Stamina<br>+9 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 7.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsChainBracers; ++i;

var fMarshalsLinkedBracers = new RewardItem("alliance","Marshal's Linked Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fMarshalsLinkedBracers.itemHonorPrice = new Array();
fMarshalsLinkedBracers.itemHonorPrice[0] = 9435
fMarshalsLinkedBracers.itemTokenPrice = new Array();
fMarshalsLinkedBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsLinkedBracers.itemStats = new Array();
fMarshalsLinkedBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Linked Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>349 Armor<br>+19 Strength<br>+25 Stamina<br>+9 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 10.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLinkedBracers; ++i;

var fMarshalsMailBracers = new RewardItem("alliance","Marshal's Mail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fMarshalsMailBracers.itemHonorPrice = new Array();
fMarshalsMailBracers.itemHonorPrice[0] = 9435
fMarshalsMailBracers.itemTokenPrice = new Array();
fMarshalsMailBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsMailBracers.itemStats = new Array();
fMarshalsMailBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Mail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>349 Armor<br>+22 Stamina<br>+12 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsMailBracers; ++i;

var fMarshalsChainGirdle = new RewardItem("alliance","Marshal's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fMarshalsChainGirdle.itemHonorPrice = new Array();
fMarshalsChainGirdle.itemHonorPrice[0] = 14280
fMarshalsChainGirdle.itemTokenPrice = new Array();
fMarshalsChainGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsChainGirdle.itemStats = new Array();
fMarshalsChainGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Chain Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>487 Armor<br>+27 Agility<br>+39 Stamina<br>+18 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsChainGirdle; ++i;

var fMarshalsLinkedGirdle = new RewardItem("alliance","Marshal's Linked Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fMarshalsLinkedGirdle.itemHonorPrice = new Array();
fMarshalsLinkedGirdle.itemHonorPrice[0] = 14280
fMarshalsLinkedGirdle.itemTokenPrice = new Array();
fMarshalsLinkedGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsLinkedGirdle.itemStats = new Array();
fMarshalsLinkedGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Linked Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>487 Armor<br>+27 Strength<br>+39 Stamina<br>+18 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLinkedGirdle; ++i;

var fMarshalsMailGirdle = new RewardItem("alliance","Marshal's Mail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fMarshalsMailGirdle.itemHonorPrice = new Array();
fMarshalsMailGirdle.itemHonorPrice[0] = 14280
fMarshalsMailGirdle.itemTokenPrice = new Array();
fMarshalsMailGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsMailGirdle.itemStats = new Array();
fMarshalsMailGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Mail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>487 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsMailGirdle; ++i;

var fMarshalsChainSabatons = new RewardItem("alliance","Marshal's Chain Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fMarshalsChainSabatons.itemHonorPrice = new Array();
fMarshalsChainSabatons.itemHonorPrice[0] = 14280
fMarshalsChainSabatons.itemTokenPrice = new Array();
fMarshalsChainSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsChainSabatons.itemStats = new Array();
fMarshalsChainSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Chain Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>595 Armor<br>+27 Agility<br>+39 Stamina<br>+18 Intellect<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsChainSabatons; ++i;

var fMarshalsLinkedSabatons = new RewardItem("alliance","Marshal's Linked Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fMarshalsLinkedSabatons.itemHonorPrice = new Array();
fMarshalsLinkedSabatons.itemHonorPrice[0] = 14280
fMarshalsLinkedSabatons.itemTokenPrice = new Array();
fMarshalsLinkedSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsLinkedSabatons.itemStats = new Array();
fMarshalsLinkedSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Linked Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>595 Armor<br>+27 Agility<br>+39 Stamina<br>+18 Intellect<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLinkedSabatons; ++i;

var fMarshalsMailSabatons = new RewardItem("alliance","Marshal's Mail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fMarshalsMailSabatons.itemHonorPrice = new Array();
fMarshalsMailSabatons.itemHonorPrice[0] = 14280
fMarshalsMailSabatons.itemTokenPrice = new Array();
fMarshalsMailSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsMailSabatons.itemStats = new Array();
fMarshalsMailSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Mail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>595 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsMailSabatons; ++i;

var fMarshalsPlateBracers = new RewardItem("alliance","Marshal's Plate Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fMarshalsPlateBracers.itemHonorPrice = new Array();
fMarshalsPlateBracers.itemHonorPrice[0] = 9435
fMarshalsPlateBracers.itemTokenPrice = new Array();
fMarshalsPlateBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsPlateBracers.itemStats = new Array();
fMarshalsPlateBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Plate Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>624 Armor<br>+19 Strength<br>+25 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsPlateBracers; ++i;

var fMarshalsLamellarBracers = new RewardItem("alliance","Marshal's Lamellar Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fMarshalsLamellarBracers.itemHonorPrice = new Array();
fMarshalsLamellarBracers.itemHonorPrice[0] = 9435
fMarshalsLamellarBracers.itemTokenPrice = new Array();
fMarshalsLamellarBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsLamellarBracers.itemStats = new Array();
fMarshalsLamellarBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Lamellar Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>624 Armor<br>+22 Stamina<br>+12 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLamellarBracers; ++i;

var fMarshalsScaledBracers = new RewardItem("alliance","Marshal's Scaled Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fMarshalsScaledBracers.itemHonorPrice = new Array();
fMarshalsScaledBracers.itemHonorPrice[0] = 9435
fMarshalsScaledBracers.itemTokenPrice = new Array();
fMarshalsScaledBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsScaledBracers.itemStats = new Array();
fMarshalsScaledBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Scaled Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>624 Armor<br>+17 Strength<br>+22 Stamina<br>+11 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsScaledBracers; ++i;

var fMarshalsPlateBelt = new RewardItem("alliance","Marshal's Plate Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fMarshalsPlateBelt.itemHonorPrice = new Array();
fMarshalsPlateBelt.itemHonorPrice[0] = 14280
fMarshalsPlateBelt.itemTokenPrice = new Array();
fMarshalsPlateBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsPlateBelt.itemStats = new Array();
fMarshalsPlateBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Plate Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>870 Armor<br>+27 Strength<br>+40 Stamina<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsPlateBelt; ++i;

var fMarshalsLamellarBelt = new RewardItem("alliance","Marshal's Lamellar Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fMarshalsLamellarBelt.itemHonorPrice = new Array();
fMarshalsLamellarBelt.itemHonorPrice[0] = 14280
fMarshalsLamellarBelt.itemTokenPrice = new Array();
fMarshalsLamellarBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsLamellarBelt.itemStats = new Array();
fMarshalsLamellarBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Lamellar Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>870 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLamellarBelt; ++i;

var fMarshalsScaledBelt = new RewardItem("alliance","Marshal's Scaled Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fMarshalsScaledBelt.itemHonorPrice = new Array();
fMarshalsScaledBelt.itemHonorPrice[0] = 14280
fMarshalsScaledBelt.itemTokenPrice = new Array();
fMarshalsScaledBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsScaledBelt.itemStats = new Array();
fMarshalsScaledBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Scaled Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>870 Armor<br>+24 Strength<br>+33 Stamina<br>+23 Intellect<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsScaledBelt; ++i;

var fMarshalsPlateGreaves = new RewardItem("alliance","Marshal's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fMarshalsPlateGreaves.itemHonorPrice = new Array();
fMarshalsPlateGreaves.itemHonorPrice[0] = 14280
fMarshalsPlateGreaves.itemTokenPrice = new Array();
fMarshalsPlateGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsPlateGreaves.itemStats = new Array();
fMarshalsPlateGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Plate Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1063 Armor<br>+27 Strength<br>+40 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsPlateGreaves; ++i;

var fMarshalsLamellarGreaves = new RewardItem("alliance","Marshal's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fMarshalsLamellarGreaves.itemHonorPrice = new Array();
fMarshalsLamellarGreaves.itemHonorPrice[0] = 14280
fMarshalsLamellarGreaves.itemTokenPrice = new Array();
fMarshalsLamellarGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsLamellarGreaves.itemStats = new Array();
fMarshalsLamellarGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Lamellar Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1063 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLamellarGreaves; ++i;

var fMarshalsScaledGreaves = new RewardItem("alliance","Marshal's Scaled Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fMarshalsScaledGreaves.itemHonorPrice = new Array();
fMarshalsScaledGreaves.itemHonorPrice[0] = 14280
fMarshalsScaledGreaves.itemTokenPrice = new Array();
fMarshalsScaledGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsScaledGreaves.itemStats = new Array();
fMarshalsScaledGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Marshal's Scaled Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1063 Armor<br>+24 Strength<br>+33 Stamina<br>+23 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsScaledGreaves; ++i;



//-------------------------------------------------------------------
//---Horde below

var fSergeantsHeavyCloak = new RewardItem("horde","Sergeant's Heavy Cloak","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Misc_Cape_07.gif");
fSergeantsHeavyCloak.itemHonorPrice = new Array();
fSergeantsHeavyCloak.itemHonorPrice[0] = 9435
fSergeantsHeavyCloak.itemTokenPrice = new Array();
fSergeantsHeavyCloak.itemTokenPrice[0] = new Array(0,20,0,0);
fSergeantsHeavyCloak.itemStats = new Array();
fSergeantsHeavyCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sergeant's Heavy Cloak</span>\
<br>Binds when picked up<br>Back<br>104 Armor<br>+27 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsHeavyCloak; ++i;

var fSergeantsHeavyCape = new RewardItem("horde","Sergeant's Heavy Cape","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Misc_Cape_07.gif");
fSergeantsHeavyCape.itemHonorPrice = new Array();
fSergeantsHeavyCape.itemHonorPrice[0] = 9435
fSergeantsHeavyCape.itemTokenPrice = new Array();
fSergeantsHeavyCape.itemTokenPrice[0] = new Array(0,20,0,0);
fSergeantsHeavyCape.itemStats = new Array();
fSergeantsHeavyCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sergeant's Heavy Cape</span>\
<br>Binds when picked up<br>Back<br>104 Armor<br>+33 Stamina<br>+12 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsHeavyCape; ++i;


var fMarshalsSilkCuffs = new RewardItem("horde","General's Silk Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsSilkCuffs.itemHonorPrice = new Array();
fMarshalsSilkCuffs.itemHonorPrice[0] = 9435
fMarshalsSilkCuffs.itemTokenPrice = new Array();
fMarshalsSilkCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsSilkCuffs.itemStats = new Array();
fMarshalsSilkCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Silk Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>84 Armor<br>+22 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsSilkCuffs; ++i;


var fMarshalsDreadweaveCuffs = new RewardItem("horde","General's Dreadweave Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsDreadweaveCuffs.itemHonorPrice = new Array();
fMarshalsDreadweaveCuffs.itemHonorPrice[0] = 9435
fMarshalsDreadweaveCuffs.itemTokenPrice = new Array();
fMarshalsDreadweaveCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsDreadweaveCuffs.itemStats = new Array();
fMarshalsDreadweaveCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Dreadweave Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>84 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDreadweaveCuffs; ++i;

var fMarshalsSilkBelt = new RewardItem("horde","General's Silk Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsSilkBelt.itemHonorPrice = new Array();
fMarshalsSilkBelt.itemHonorPrice[0] = 14280
fMarshalsSilkBelt.itemTokenPrice = new Array();
fMarshalsSilkBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsSilkBelt.itemStats = new Array();
fMarshalsSilkBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Silk Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+33 Stamina<br>+23 Intellect<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsSilkBelt; ++i;

var fMarshalsDreadweaveBelt = new RewardItem("horde","General's Dreadweave Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsDreadweaveBelt.itemHonorPrice = new Array();
fMarshalsDreadweaveBelt.itemHonorPrice[0] = 14280
fMarshalsDreadweaveBelt.itemTokenPrice = new Array();
fMarshalsDreadweaveBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsDreadweaveBelt.itemStats = new Array();
fMarshalsDreadweaveBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Dreadweave Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>117 Armor<br>+39 Stamina<br>+27 Intellect<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDreadweaveBelt; ++i;

var fMarshalsSilkFootguards = new RewardItem("horde","General's Silk Footguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fMarshalsSilkFootguards.itemHonorPrice = new Array();
fMarshalsSilkFootguards.itemHonorPrice[0] = 14280
fMarshalsSilkFootguards.itemTokenPrice = new Array();
fMarshalsSilkFootguards.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsSilkFootguards.itemStats = new Array();
fMarshalsSilkFootguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Silk Footguards</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>142 Armor<br>+33 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsSilkFootguards; ++i;

var fMarshalsDreadweaveStalkers = new RewardItem("horde","General's Dreadweave Stalkers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fMarshalsDreadweaveStalkers.itemHonorPrice = new Array();
fMarshalsDreadweaveStalkers.itemHonorPrice[0] = 14280
fMarshalsDreadweaveStalkers.itemTokenPrice = new Array();
fMarshalsDreadweaveStalkers.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsDreadweaveStalkers.itemStats = new Array();
fMarshalsDreadweaveStalkers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Dreadweave Stalkers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>142 Armor<br>+40 Stamina<br>+27 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDreadweaveStalkers; ++i;

var fMarshalsLeatherBracers = new RewardItem("horde","General's Leather Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsLeatherBracers.itemHonorPrice = new Array();
fMarshalsLeatherBracers.itemHonorPrice[0] = 9435
fMarshalsLeatherBracers.itemTokenPrice = new Array();
fMarshalsLeatherBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsLeatherBracers.itemStats = new Array();
fMarshalsLeatherBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Leather Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>157 Armor<br>+19 Agility<br>+25 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 7.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLeatherBracers; ++i;

var fMarshalsDragonhideBracers = new RewardItem("horde","General's Dragonhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsDragonhideBracers.itemHonorPrice = new Array();
fMarshalsDragonhideBracers.itemHonorPrice[0] = 9435
fMarshalsDragonhideBracers.itemTokenPrice = new Array();
fMarshalsDragonhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsDragonhideBracers.itemStats = new Array();
fMarshalsDragonhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Dragonhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>213 Armor<br>+16 Strength<br>+13 Agility<br>+22 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 13.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDragonhideBracers; ++i;

var fMarshalsWyrmhideBracers = new RewardItem("horde","General's Wyrmhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsWyrmhideBracers.itemHonorPrice = new Array();
fMarshalsWyrmhideBracers.itemHonorPrice[0] = 9435
fMarshalsWyrmhideBracers.itemTokenPrice = new Array();
fMarshalsWyrmhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsWyrmhideBracers.itemStats = new Array();
fMarshalsWyrmhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Wyrmhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>187 Armor<br>+22 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsWyrmhideBracers; ++i;

var fMarshalsKodohideBracers = new RewardItem("horde","General's Kodohide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-general-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fMarshalsKodohideBracers.itemHonorPrice = new Array();
fMarshalsKodohideBracers.itemHonorPrice[0] = 9435
fMarshalsKodohideBracers.itemTokenPrice = new Array();
fMarshalsKodohideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsKodohideBracers.itemStats = new Array();
fMarshalsKodohideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Kodohide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>187 Armor<br>+22 Stamina<br>+14 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsKodohideBracers; ++i;

var fMarshalsLeatherBelt = new RewardItem("horde","General's Leather Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsLeatherBelt.itemHonorPrice = new Array();
fMarshalsLeatherBelt.itemHonorPrice[0] = 14280
fMarshalsLeatherBelt.itemTokenPrice = new Array();
fMarshalsLeatherBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsLeatherBelt.itemStats = new Array();
fMarshalsLeatherBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Leather Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>219 Armor<br>+27 Agility<br>+39 Stamina<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLeatherBelt; ++i;

var fMarshalsDragonhideBelt = new RewardItem("horde","General's Dragonhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsDragonhideBelt.itemHonorPrice = new Array();
fMarshalsDragonhideBelt.itemHonorPrice[0] = 14280
fMarshalsDragonhideBelt.itemTokenPrice = new Array();
fMarshalsDragonhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsDragonhideBelt.itemStats = new Array();
fMarshalsDragonhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Dragonhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>259 Armor<br>+24 Strength<br>+24 Agility<br>+33 Stamina<br>+15 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 37.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDragonhideBelt; ++i;

var fMarshalsWyrmhideBelt = new RewardItem("horde","General's Wyrmhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsWyrmhideBelt.itemHonorPrice = new Array();
fMarshalsWyrmhideBelt.itemHonorPrice[0] = 14280
fMarshalsWyrmhideBelt.itemTokenPrice = new Array();
fMarshalsWyrmhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsWyrmhideBelt.itemStats = new Array();
fMarshalsWyrmhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Wyrmhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>259 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsWyrmhideBelt; ++i;

var fMarshalsKodohideBelt = new RewardItem("horde","General's Kodohide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fMarshalsKodohideBelt.itemHonorPrice = new Array();
fMarshalsKodohideBelt.itemHonorPrice[0] = 14280
fMarshalsKodohideBelt.itemTokenPrice = new Array();
fMarshalsKodohideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsKodohideBelt.itemStats = new Array();
fMarshalsKodohideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Kodohide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>259 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 62.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsKodohideBelt; ++i;

var fMarshalsLeatherBoots = new RewardItem("horde","General's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsLeatherBoots.itemHonorPrice = new Array();
fMarshalsLeatherBoots.itemHonorPrice[0] = 14280
fMarshalsLeatherBoots.itemTokenPrice = new Array();
fMarshalsLeatherBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsLeatherBoots.itemStats = new Array();
fMarshalsLeatherBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Leather Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>267 Armor<br>+27 Agility<br>+39 Stamina<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLeatherBoots; ++i;

var fMarshalsDragonhideBoots = new RewardItem("horde","General's Dragonhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsDragonhideBoots.itemHonorPrice = new Array();
fMarshalsDragonhideBoots.itemHonorPrice[0] = 14280
fMarshalsDragonhideBoots.itemTokenPrice = new Array();
fMarshalsDragonhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsDragonhideBoots.itemStats = new Array();
fMarshalsDragonhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Dragonhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>309 Armor<br>+24 Strength<br>+24 Agility<br>+33 Stamina<br>+15 Intellect<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 37.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsDragonhideBoots; ++i;

var fMarshalsWyrmhideBoots = new RewardItem("horde","General's Wyrmhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsWyrmhideBoots.itemHonorPrice = new Array();
fMarshalsWyrmhideBoots.itemHonorPrice[0] = 14280
fMarshalsWyrmhideBoots.itemTokenPrice = new Array();
fMarshalsWyrmhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsWyrmhideBoots.itemStats = new Array();
fMarshalsWyrmhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Wyrmhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>307 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsWyrmhideBoots; ++i;

var fMarshalsKodohideBoots = new RewardItem("horde","General's Kodohide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fMarshalsKodohideBoots.itemHonorPrice = new Array();
fMarshalsKodohideBoots.itemHonorPrice[0] = 14280
fMarshalsKodohideBoots.itemTokenPrice = new Array();
fMarshalsKodohideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsKodohideBoots.itemStats = new Array();
fMarshalsKodohideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Kodohide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>307 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 62.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsKodohideBoots; ++i;


var fMarshalsChainBracers = new RewardItem("horde","General's Chain Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fMarshalsChainBracers.itemHonorPrice = new Array();
fMarshalsChainBracers.itemHonorPrice[0] = 9435
fMarshalsChainBracers.itemTokenPrice = new Array();
fMarshalsChainBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsChainBracers.itemStats = new Array();
fMarshalsChainBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Chain Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>349 Armor<br>+18 Agility<br>+25 Stamina<br>+9 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 7.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsChainBracers; ++i;

var fMarshalsLinkedBracers = new RewardItem("horde","General's Linked Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fMarshalsLinkedBracers.itemHonorPrice = new Array();
fMarshalsLinkedBracers.itemHonorPrice[0] = 9435
fMarshalsLinkedBracers.itemTokenPrice = new Array();
fMarshalsLinkedBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsLinkedBracers.itemStats = new Array();
fMarshalsLinkedBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Linked Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>349 Armor<br>+19 Strength<br>+25 Stamina<br>+9 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 10.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLinkedBracers; ++i;

var fMarshalsMailBracers = new RewardItem("horde","General's Mail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fMarshalsMailBracers.itemHonorPrice = new Array();
fMarshalsMailBracers.itemHonorPrice[0] = 9435
fMarshalsMailBracers.itemTokenPrice = new Array();
fMarshalsMailBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsMailBracers.itemStats = new Array();
fMarshalsMailBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Mail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>349 Armor<br>+22 Stamina<br>+12 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsMailBracers; ++i;

var fMarshalsChainGirdle = new RewardItem("horde","General's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fMarshalsChainGirdle.itemHonorPrice = new Array();
fMarshalsChainGirdle.itemHonorPrice[0] = 14280
fMarshalsChainGirdle.itemTokenPrice = new Array();
fMarshalsChainGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsChainGirdle.itemStats = new Array();
fMarshalsChainGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Chain Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>487 Armor<br>+27 Agility<br>+39 Stamina<br>+18 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsChainGirdle; ++i;

var fMarshalsLinkedGirdle = new RewardItem("horde","General's Linked Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fMarshalsLinkedGirdle.itemHonorPrice = new Array();
fMarshalsLinkedGirdle.itemHonorPrice[0] = 14280
fMarshalsLinkedGirdle.itemTokenPrice = new Array();
fMarshalsLinkedGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsLinkedGirdle.itemStats = new Array();
fMarshalsLinkedGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Linked Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>487 Armor<br>+27 Strength<br>+39 Stamina<br>+18 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLinkedGirdle; ++i;

var fMarshalsMailGirdle = new RewardItem("horde","General's Mail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fMarshalsMailGirdle.itemHonorPrice = new Array();
fMarshalsMailGirdle.itemHonorPrice[0] = 14280
fMarshalsMailGirdle.itemTokenPrice = new Array();
fMarshalsMailGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsMailGirdle.itemStats = new Array();
fMarshalsMailGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Mail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>487 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsMailGirdle; ++i;

var fMarshalsChainSabatons = new RewardItem("horde","General's Chain Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fMarshalsChainSabatons.itemHonorPrice = new Array();
fMarshalsChainSabatons.itemHonorPrice[0] = 14280
fMarshalsChainSabatons.itemTokenPrice = new Array();
fMarshalsChainSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsChainSabatons.itemStats = new Array();
fMarshalsChainSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Chain Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>595 Armor<br>+27 Agility<br>+39 Stamina<br>+18 Intellect<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsChainSabatons; ++i;

var fMarshalsLinkedSabatons = new RewardItem("horde","General's Linked Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fMarshalsLinkedSabatons.itemHonorPrice = new Array();
fMarshalsLinkedSabatons.itemHonorPrice[0] = 14280
fMarshalsLinkedSabatons.itemTokenPrice = new Array();
fMarshalsLinkedSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsLinkedSabatons.itemStats = new Array();
fMarshalsLinkedSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Linked Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>595 Armor<br>+27 Agility<br>+39 Stamina<br>+18 Intellect<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLinkedSabatons; ++i;

var fMarshalsMailSabatons = new RewardItem("horde","General's Mail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fMarshalsMailSabatons.itemHonorPrice = new Array();
fMarshalsMailSabatons.itemHonorPrice[0] = 14280
fMarshalsMailSabatons.itemTokenPrice = new Array();
fMarshalsMailSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsMailSabatons.itemStats = new Array();
fMarshalsMailSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Mail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>595 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsMailSabatons; ++i;

var fMarshalsPlateBracers = new RewardItem("horde","General's Plate Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fMarshalsPlateBracers.itemHonorPrice = new Array();
fMarshalsPlateBracers.itemHonorPrice[0] = 9435
fMarshalsPlateBracers.itemTokenPrice = new Array();
fMarshalsPlateBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsPlateBracers.itemStats = new Array();
fMarshalsPlateBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Plate Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>624 Armor<br>+19 Strength<br>+25 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsPlateBracers; ++i;

var fMarshalsLamellarBracers = new RewardItem("horde","General's Lamellar Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fMarshalsLamellarBracers.itemHonorPrice = new Array();
fMarshalsLamellarBracers.itemHonorPrice[0] = 9435
fMarshalsLamellarBracers.itemTokenPrice = new Array();
fMarshalsLamellarBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsLamellarBracers.itemStats = new Array();
fMarshalsLamellarBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Lamellar Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>624 Armor<br>+22 Stamina<br>+12 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLamellarBracers; ++i;

var fMarshalsScaledBracers = new RewardItem("horde","General's Scaled Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fMarshalsScaledBracers.itemHonorPrice = new Array();
fMarshalsScaledBracers.itemHonorPrice[0] = 9435
fMarshalsScaledBracers.itemTokenPrice = new Array();
fMarshalsScaledBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fMarshalsScaledBracers.itemStats = new Array();
fMarshalsScaledBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Scaled Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>624 Armor<br>+17 Strength<br>+22 Stamina<br>+11 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsScaledBracers; ++i;

var fMarshalsPlateBelt = new RewardItem("horde","General's Plate Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fMarshalsPlateBelt.itemHonorPrice = new Array();
fMarshalsPlateBelt.itemHonorPrice[0] = 14280
fMarshalsPlateBelt.itemTokenPrice = new Array();
fMarshalsPlateBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsPlateBelt.itemStats = new Array();
fMarshalsPlateBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Plate Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>870 Armor<br>+27 Strength<br>+40 Stamina<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsPlateBelt; ++i;

var fMarshalsLamellarBelt = new RewardItem("horde","General's Lamellar Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fMarshalsLamellarBelt.itemHonorPrice = new Array();
fMarshalsLamellarBelt.itemHonorPrice[0] = 14280
fMarshalsLamellarBelt.itemTokenPrice = new Array();
fMarshalsLamellarBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsLamellarBelt.itemStats = new Array();
fMarshalsLamellarBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Lamellar Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>870 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLamellarBelt; ++i;

var fMarshalsScaledBelt = new RewardItem("horde","General's Scaled Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fMarshalsScaledBelt.itemHonorPrice = new Array();
fMarshalsScaledBelt.itemHonorPrice[0] = 14280
fMarshalsScaledBelt.itemTokenPrice = new Array();
fMarshalsScaledBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fMarshalsScaledBelt.itemStats = new Array();
fMarshalsScaledBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Scaled Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>870 Armor<br>+24 Strength<br>+33 Stamina<br>+23 Intellect<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsScaledBelt; ++i;

var fMarshalsPlateGreaves = new RewardItem("horde","General's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fMarshalsPlateGreaves.itemHonorPrice = new Array();
fMarshalsPlateGreaves.itemHonorPrice[0] = 14280
fMarshalsPlateGreaves.itemTokenPrice = new Array();
fMarshalsPlateGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsPlateGreaves.itemStats = new Array();
fMarshalsPlateGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Plate Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1063 Armor<br>+27 Strength<br>+40 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsPlateGreaves; ++i;

var fMarshalsLamellarGreaves = new RewardItem("horde","General's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fMarshalsLamellarGreaves.itemHonorPrice = new Array();
fMarshalsLamellarGreaves.itemHonorPrice[0] = 14280
fMarshalsLamellarGreaves.itemTokenPrice = new Array();
fMarshalsLamellarGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsLamellarGreaves.itemStats = new Array();
fMarshalsLamellarGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Lamellar Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1063 Armor<br>+34 Stamina<br>+23 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsLamellarGreaves; ++i;

var fMarshalsScaledGreaves = new RewardItem("horde","General's Scaled Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fMarshalsScaledGreaves.itemHonorPrice = new Array();
fMarshalsScaledGreaves.itemHonorPrice[0] = 14280
fMarshalsScaledGreaves.itemTokenPrice = new Array();
fMarshalsScaledGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fMarshalsScaledGreaves.itemStats = new Array();
fMarshalsScaledGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">General's Scaled Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1063 Armor<br>+24 Strength<br>+33 Stamina<br>+23 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshalsScaledGreaves; ++i;

//------END REWARDS DEFINITION------
