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

var fVindicatorsChainBracers = new RewardItem("alliance","Vindicator's Chain Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsChainBracers.itemHonorPrice = new Array();
fVindicatorsChainBracers.itemHonorPrice[1] = 11794
fVindicatorsChainBracers.itemTokenPrice = new Array();
fVindicatorsChainBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsChainBracers.itemStats = new Array();
fVindicatorsChainBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Chain Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+23 Agility<br>+33 Stamina<br>+13 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsChainBracers; ++i;



var fVindicatorsChainGirdle = new RewardItem("alliance","Vindicator's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsChainGirdle.itemHonorPrice = new Array();
fVindicatorsChainGirdle.itemHonorPrice[1] = 17850
fVindicatorsChainGirdle.itemTokenPrice = new Array();
fVindicatorsChainGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsChainGirdle.itemStats = new Array();
fVindicatorsChainGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Chain Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+33 Agility<br>+48 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsChainGirdle; ++i;



var fVindicatorsChainSabatons = new RewardItem("alliance","Vindicator's Chain Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsChainSabatons.itemHonorPrice = new Array();
fVindicatorsChainSabatons.itemHonorPrice[1] = 17850
fVindicatorsChainSabatons.itemTokenPrice = new Array();
fVindicatorsChainSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsChainSabatons.itemStats = new Array();
fVindicatorsChainSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Chain Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+33 Agility<br>+48 Stamina<br>+23 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsChainSabatons; ++i;

var fVindicatorsDragonhideBelt = new RewardItem("alliance","Vindicator's Dragonhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsDragonhideBelt.itemHonorPrice = new Array();
fVindicatorsDragonhideBelt.itemHonorPrice[5] = 17850
fVindicatorsDragonhideBelt.itemTokenPrice = new Array();
fVindicatorsDragonhideBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsDragonhideBelt.itemStats = new Array();
fVindicatorsDragonhideBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dragonhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>300 Armor<br>+30 Strength<br>+29 Agility<br>+42 Stamina<br>+20 Intellect<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDragonhideBelt; ++i;


var fVindicatorsDragonhideBoots = new RewardItem("alliance","Vindicator's Dragonhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsDragonhideBoots.itemHonorPrice = new Array();
fVindicatorsDragonhideBoots.itemHonorPrice[5] = 17850
fVindicatorsDragonhideBoots.itemTokenPrice = new Array();
fVindicatorsDragonhideBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsDragonhideBoots.itemStats = new Array();
fVindicatorsDragonhideBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dragonhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>357 Armor<br>+30 Strength<br>+29 Agility<br>+42 Stamina<br>+20 Intellect<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDragonhideBoots; ++i;

var fVindicatorsDragonhideBracers = new RewardItem("alliance","Vindicator's Dragonhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsDragonhideBracers.itemHonorPrice = new Array();
fVindicatorsDragonhideBracers.itemHonorPrice[5] = 11794
fVindicatorsDragonhideBracers.itemTokenPrice = new Array();
fVindicatorsDragonhideBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsDragonhideBracers.itemStats = new Array();
fVindicatorsDragonhideBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dragonhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>236 Armor<br>+22 Strength<br>+22 Agility<br>+29 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDragonhideBracers; ++i;

var fVindicatorsDreadweaveBelt = new RewardItem("alliance","Vindicator's Dreadweave Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsDreadweaveBelt.itemHonorPrice = new Array();
fVindicatorsDreadweaveBelt.itemHonorPrice[2] = 17850
fVindicatorsDreadweaveBelt.itemTokenPrice = new Array();
fVindicatorsDreadweaveBelt.itemTokenPrice[2] = new Array(0,40,0,0);
fVindicatorsDreadweaveBelt.itemStats = new Array();
fVindicatorsDreadweaveBelt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dreadweave Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>138 Armor<br>+49 Stamina<br>+34 Intellect<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 41.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDreadweaveBelt; ++i;

var fVindicatorsDreadweaveCuffs = new RewardItem("alliance","Vindicator's Dreadweave Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsDreadweaveCuffs.itemHonorPrice = new Array();
fVindicatorsDreadweaveCuffs.itemHonorPrice[2] = 11794
fVindicatorsDreadweaveCuffs.itemTokenPrice = new Array();
fVindicatorsDreadweaveCuffs.itemTokenPrice[2] = new Array(0,0,0,20);
fVindicatorsDreadweaveCuffs.itemStats = new Array();
fVindicatorsDreadweaveCuffs.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dreadweave Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+37 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDreadweaveCuffs; ++i;


var fVindicatorsDreadweaveStalkers = new RewardItem("alliance","Vindicator's Dreadweave Stalkers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVindicatorsDreadweaveStalkers.itemHonorPrice = new Array();
fVindicatorsDreadweaveStalkers.itemHonorPrice[2] = 17850
fVindicatorsDreadweaveStalkers.itemTokenPrice = new Array();
fVindicatorsDreadweaveStalkers.itemTokenPrice[2] = new Array(0,0,40,0);
fVindicatorsDreadweaveStalkers.itemStats = new Array();
fVindicatorsDreadweaveStalkers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dreadweave Stalkers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>168 Armor<br>+49 Stamina<br>+34 Intellect<br>Durability 50 / 50<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 41.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDreadweaveStalkers; ++i;


var fVindicatorsKodohideBelt = new RewardItem("alliance","Vindicator's Kodohide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsKodohideBelt.itemHonorPrice = new Array();
fVindicatorsKodohideBelt.itemHonorPrice[5] = 17850
fVindicatorsKodohideBelt.itemTokenPrice = new Array();
fVindicatorsKodohideBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsKodohideBelt.itemStats = new Array();
fVindicatorsKodohideBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Kodohide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>300 Armor<br>+43 Stamina<br>+30 Intellect<br>+23 Spirit<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBelt; ++i;

var fVindicatorsKodohideBoots = new RewardItem("alliance","Vindicator's Kodohide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsKodohideBoots.itemHonorPrice = new Array();
fVindicatorsKodohideBoots.itemHonorPrice[5] = 17850
fVindicatorsKodohideBoots.itemTokenPrice = new Array();
fVindicatorsKodohideBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsKodohideBoots.itemStats = new Array();
fVindicatorsKodohideBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Kodohide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>357 Armor<br>+43 Stamina<br>+30 Intellect<br>+23 Spirit<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBoots; ++i;


var fVindicatorsKodohideBracers = new RewardItem("alliance","Vindicator's Kodohide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsKodohideBracers.itemHonorPrice = new Array();
fVindicatorsKodohideBracers.itemHonorPrice[5] = 11794
fVindicatorsKodohideBracers.itemTokenPrice = new Array();
fVindicatorsKodohideBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsKodohideBracers.itemStats = new Array();
fVindicatorsKodohideBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Kodohide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>236 Armor<br>+29 Stamina<br>+22 Intellect<br>+17 Spirit<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 40 and damage done by up to 14 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBracers; ++i;


var fVindicatorsLamellarBelt = new RewardItem("alliance","Vindicator's Lamellar Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsLamellarBelt.itemHonorPrice = new Array();
fVindicatorsLamellarBelt.itemHonorPrice[8] = 17850
fVindicatorsLamellarBelt.itemTokenPrice = new Array();
fVindicatorsLamellarBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsLamellarBelt.itemStats = new Array();
fVindicatorsLamellarBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Lamellar Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLamellarBelt; ++i;



var fVindicatorsLamellarBracers = new RewardItem("alliance","Vindicator's Lamellar Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsLamellarBracers.itemHonorPrice = new Array();
fVindicatorsLamellarBracers.itemHonorPrice[8] = 11794
fVindicatorsLamellarBracers.itemTokenPrice = new Array();
fVindicatorsLamellarBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsLamellarBracers.itemStats = new Array();
fVindicatorsLamellarBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Lamellar Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLamellarBracers; ++i;



var fVindicatorsLamellarGreaves = new RewardItem("alliance","Vindicator's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsLamellarGreaves.itemHonorPrice = new Array();
fVindicatorsLamellarGreaves.itemHonorPrice[8] = 17850
fVindicatorsLamellarGreaves.itemTokenPrice = new Array();
fVindicatorsLamellarGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsLamellarGreaves.itemStats = new Array();
fVindicatorsLamellarGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Lamellar Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLamellarGreaves; ++i;



var fVindicatorsLeatherBelt = new RewardItem("alliance","Vindicator's Leather Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsLeatherBelt.itemHonorPrice = new Array();
fVindicatorsLeatherBelt.itemHonorPrice[5] = 17850
fVindicatorsLeatherBelt.itemTokenPrice = new Array();
fVindicatorsLeatherBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsLeatherBelt.itemStats = new Array();
fVindicatorsLeatherBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Leather Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>258 Armor<br>+33 Agility<br>+49 Stamina<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLeatherBelt; ++i;


var fVindicatorsLeatherBoots = new RewardItem("alliance","Vindicator's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsLeatherBoots.itemHonorPrice = new Array();
fVindicatorsLeatherBoots.itemHonorPrice[5] = 17850
fVindicatorsLeatherBoots.itemTokenPrice = new Array();
fVindicatorsLeatherBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsLeatherBoots.itemStats = new Array();
fVindicatorsLeatherBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Leather Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>315 Armor<br>+33 Agility<br>+49 Stamina<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLeatherBoots; ++i;


var fVindicatorsLeatherBracers = new RewardItem("alliance","Vindicator's Leather Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsLeatherBracers.itemHonorPrice = new Array();
fVindicatorsLeatherBracers.itemHonorPrice[5] = 11794
fVindicatorsLeatherBracers.itemTokenPrice = new Array();
fVindicatorsLeatherBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsLeatherBracers.itemStats = new Array();
fVindicatorsLeatherBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Leather Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>194 Armor<br>+25 Agility<br>+33 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLeatherBracers; ++i;



var fVindicatorsLinkedBracers = new RewardItem("alliance","Vindicator's Linked Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsLinkedBracers.itemHonorPrice = new Array();
fVindicatorsLinkedBracers.itemHonorPrice[1] = 11794
fVindicatorsLinkedBracers.itemTokenPrice = new Array();
fVindicatorsLinkedBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsLinkedBracers.itemStats = new Array();
fVindicatorsLinkedBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Linked Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+25 Strength<br>+33 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLinkedBracers; ++i;


var fVindicatorsLinkedGirdle = new RewardItem("alliance","Vindicator's Linked Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsLinkedGirdle.itemHonorPrice = new Array();
fVindicatorsLinkedGirdle.itemHonorPrice[1] = 17850
fVindicatorsLinkedGirdle.itemTokenPrice = new Array();
fVindicatorsLinkedGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsLinkedGirdle.itemStats = new Array();
fVindicatorsLinkedGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Linked Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+34 Strength<br>+49 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLinkedGirdle; ++i;

var fVindicatorsLinkedSabatons = new RewardItem("alliance","Vindicator's Linked Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsLinkedSabatons.itemHonorPrice = new Array();
fVindicatorsLinkedSabatons.itemHonorPrice[1] = 17850
fVindicatorsLinkedSabatons.itemTokenPrice = new Array();
fVindicatorsLinkedSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsLinkedSabatons.itemStats = new Array();
fVindicatorsLinkedSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Linked Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+33 Strength<br>+49 Stamina<br>+23 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 34.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLinkedSabatons; ++i;



var fVindicatorsMailBracers = new RewardItem("alliance","Vindicator's Mail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsMailBracers.itemHonorPrice = new Array();
fVindicatorsMailBracers.itemHonorPrice[1] = 11794
fVindicatorsMailBracers.itemTokenPrice = new Array();
fVindicatorsMailBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsMailBracers.itemStats = new Array();
fVindicatorsMailBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMailBracers; ++i;



var fVindicatorsMailGirdle = new RewardItem("alliance","Vindicator's Mail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsMailGirdle.itemHonorPrice = new Array();
fVindicatorsMailGirdle.itemHonorPrice[1] = 17850
fVindicatorsMailGirdle.itemTokenPrice = new Array();
fVindicatorsMailGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsMailGirdle.itemStats = new Array();
fVindicatorsMailGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMailGirdle; ++i;

var fVindicatorsMailSabatons = new RewardItem("alliance","Vindicator's Mail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsMailSabatons.itemHonorPrice = new Array();
fVindicatorsMailSabatons.itemHonorPrice[1] = 17850
fVindicatorsMailSabatons.itemTokenPrice = new Array();
fVindicatorsMailSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsMailSabatons.itemStats = new Array();
fVindicatorsMailSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMailSabatons; ++i;



var fVindicatorsPlateBelt = new RewardItem("alliance","Vindicator's Plate Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsPlateBelt.itemHonorPrice = new Array();
fVindicatorsPlateBelt.itemHonorPrice[8] = 17850
fVindicatorsPlateBelt.itemTokenPrice = new Array();
fVindicatorsPlateBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsPlateBelt.itemStats = new Array();
fVindicatorsPlateBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Plate Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+35 Strength<br>+49 Stamina<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 35.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPlateBelt; ++i;



var fVindicatorsPlateBracers = new RewardItem("alliance","Vindicator's Plate Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsPlateBracers.itemHonorPrice = new Array();
fVindicatorsPlateBracers.itemHonorPrice[8] = 11794
fVindicatorsPlateBracers.itemTokenPrice = new Array();
fVindicatorsPlateBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsPlateBracers.itemStats = new Array();
fVindicatorsPlateBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Plate Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+25 Strength<br>+36 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Strength</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPlateBracers; ++i;


var fVindicatorsPlateGreaves = new RewardItem("alliance","Vindicator's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsPlateGreaves.itemHonorPrice = new Array();
fVindicatorsPlateGreaves.itemHonorPrice[8] = 17850
fVindicatorsPlateGreaves.itemTokenPrice = new Array();
fVindicatorsPlateGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsPlateGreaves.itemStats = new Array();
fVindicatorsPlateGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Plate Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+35 Strength<br>+49 Stamina<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 35.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPlateGreaves; ++i;


var fVindicatorsScaledBelt = new RewardItem("alliance","Vindicator's Scaled Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsScaledBelt.itemHonorPrice = new Array();
fVindicatorsScaledBelt.itemHonorPrice[8] = 17850
fVindicatorsScaledBelt.itemTokenPrice = new Array();
fVindicatorsScaledBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsScaledBelt.itemStats = new Array();
fVindicatorsScaledBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Scaled Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+27 Strength<br>+39 Stamina<br>+26 Intellect<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsScaledBelt; ++i;



var fVindicatorsScaledBracers = new RewardItem("alliance","Vindicator's Scaled Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsScaledBracers.itemHonorPrice = new Array();
fVindicatorsScaledBracers.itemHonorPrice[8] = 11794
fVindicatorsScaledBracers.itemTokenPrice = new Array();
fVindicatorsScaledBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsScaledBracers.itemStats = new Array();
fVindicatorsScaledBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Scaled Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+19 Strength<br>+28 Stamina<br>+15 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsScaledBracers; ++i;

var fVindicatorsScaledGreaves = new RewardItem("alliance","Vindicator's Scaled Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsScaledGreaves.itemHonorPrice = new Array();
fVindicatorsScaledGreaves.itemHonorPrice[8] = 17850
fVindicatorsScaledGreaves.itemTokenPrice = new Array();
fVindicatorsScaledGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsScaledGreaves.itemStats = new Array();
fVindicatorsScaledGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Scaled Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+27 Strength<br>+39 Stamina<br>+26 Intellect<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsScaledGreaves; ++i;



var fVindicatorsSilkBelt = new RewardItem("alliance","Vindicator's Silk Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsSilkBelt.itemHonorPrice = new Array();
fVindicatorsSilkBelt.itemHonorPrice[2] = 17850
fVindicatorsSilkBelt.itemTokenPrice = new Array();
fVindicatorsSilkBelt.itemTokenPrice[2] = new Array(0,40,0,0);
fVindicatorsSilkBelt.itemStats = new Array();
fVindicatorsSilkBelt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Silk Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>138 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsSilkBelt; ++i;


var fVindicatorsSilkCuffs = new RewardItem("alliance","Vindicator's Silk Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsSilkCuffs.itemHonorPrice = new Array();
fVindicatorsSilkCuffs.itemHonorPrice[2] = 11794
fVindicatorsSilkCuffs.itemTokenPrice = new Array();
fVindicatorsSilkCuffs.itemTokenPrice[2] = new Array(0,0,0,20);
fVindicatorsSilkCuffs.itemStats = new Array();
fVindicatorsSilkCuffs.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Silk Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+29 Stamina<br>+22 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsSilkCuffs; ++i;

var fVindicatorsSilkFootguards = new RewardItem("alliance","Vindicator's Silk Footguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVindicatorsSilkFootguards.itemHonorPrice = new Array();
fVindicatorsSilkFootguards.itemHonorPrice[2] = 17850
fVindicatorsSilkFootguards.itemTokenPrice = new Array();
fVindicatorsSilkFootguards.itemTokenPrice[2] = new Array(0,0,40,0);
fVindicatorsSilkFootguards.itemStats = new Array();
fVindicatorsSilkFootguards.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Silk Footguards</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>168 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 50 / 50<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsSilkFootguards; ++i;


var fVindicatorsMoonclothBelt = new RewardItem("alliance","Vindicator's Mooncloth Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsMoonclothBelt.itemHonorPrice = new Array();
fVindicatorsMoonclothBelt.itemHonorPrice[2] = 17850
fVindicatorsMoonclothBelt.itemTokenPrice = new Array();
fVindicatorsMoonclothBelt.itemTokenPrice[2] = new Array(0,40,0,0);
fVindicatorsMoonclothBelt.itemStats = new Array();
fVindicatorsMoonclothBelt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mooncloth Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>138 Armor<br>+49 Stamina<br>+33 Intellect<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 77 and damage done by up to 26 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMoonclothBelt; ++i;

var fVindicatorsMoonclothCuffs = new RewardItem("alliance","Vindicator's Mooncloth Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsMoonclothCuffs.itemHonorPrice = new Array();
fVindicatorsMoonclothCuffs.itemHonorPrice[2] = 11794
fVindicatorsMoonclothCuffs.itemTokenPrice = new Array();
fVindicatorsMoonclothCuffs.itemTokenPrice[2] = new Array(0,0,0,20);
fVindicatorsMoonclothCuffs.itemStats = new Array();
fVindicatorsMoonclothCuffs.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mooncloth Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+37 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 55 and damage done by up to 19 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMoonclothCuffs; ++i;

var fVindicatorsMoonclothSlippers = new RewardItem("alliance","Vindicator's Mooncloth Slippers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVindicatorsMoonclothSlippers.itemHonorPrice = new Array();
fVindicatorsMoonclothSlippers.itemHonorPrice[2] = 17850
fVindicatorsMoonclothSlippers.itemTokenPrice = new Array();
fVindicatorsMoonclothSlippers.itemTokenPrice[2] = new Array(0,0,40,0);
fVindicatorsMoonclothSlippers.itemStats = new Array();
fVindicatorsMoonclothSlippers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mooncloth Slippers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>168 Armor<br>+49 Stamina<br>+33 Intellect<br>Durability 50 / 50<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 77 and damage done by up to 26 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMoonclothSlippers; ++i;

var fVindicatorsKodohideBelt = new RewardItem("alliance","Vindicator's Wyrmhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsKodohideBelt.itemHonorPrice = new Array();
fVindicatorsKodohideBelt.itemHonorPrice[5] = 17850
fVindicatorsKodohideBelt.itemTokenPrice = new Array();
fVindicatorsKodohideBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsKodohideBelt.itemStats = new Array();
fVindicatorsKodohideBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Wyrmhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>300 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBelt; ++i;

var fVindicatorsKodohideBoots = new RewardItem("alliance","Vindicator's Wyrmhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsKodohideBoots.itemHonorPrice = new Array();
fVindicatorsKodohideBoots.itemHonorPrice[5] = 17850
fVindicatorsKodohideBoots.itemTokenPrice = new Array();
fVindicatorsKodohideBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsKodohideBoots.itemStats = new Array();
fVindicatorsKodohideBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Wyrmhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>357 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBoots; ++i;

var fVindicatorsKodohideBracers = new RewardItem("alliance","Vindicator's Wyrmhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsKodohideBracers.itemHonorPrice = new Array();
fVindicatorsKodohideBracers.itemHonorPrice[5] = 11794
fVindicatorsKodohideBracers.itemTokenPrice = new Array();
fVindicatorsKodohideBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsKodohideBracers.itemStats = new Array();
fVindicatorsKodohideBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Wyrmhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>236 Armor<br>+31 Stamina<br>+20 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBracers; ++i;

var fVindicatorsOrnamentedBelt = new RewardItem("alliance","Vindicator's Ornamented Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsOrnamentedBelt.itemHonorPrice = new Array();
fVindicatorsOrnamentedBelt.itemHonorPrice[8] = 17850
fVindicatorsOrnamentedBelt.itemTokenPrice = new Array();
fVindicatorsOrnamentedBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsOrnamentedBelt.itemStats = new Array();
fVindicatorsOrnamentedBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ornamented Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsOrnamentedBelt; ++i;



var fVindicatorsOrnamentedBracers = new RewardItem("alliance","Vindicator's Ornamented Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsOrnamentedBracers.itemHonorPrice = new Array();
fVindicatorsOrnamentedBracers.itemHonorPrice[8] = 11794
fVindicatorsOrnamentedBracers.itemTokenPrice = new Array();
fVindicatorsOrnamentedBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsOrnamentedBracers.itemStats = new Array();
fVindicatorsOrnamentedBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ornamented Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsOrnamentedBracers; ++i;

var fVindicatorsOrnamentedGreaves = new RewardItem("alliance","Vindicator's Ornamented Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsOrnamentedGreaves.itemHonorPrice = new Array();
fVindicatorsOrnamentedGreaves.itemHonorPrice[8] = 17850
fVindicatorsOrnamentedGreaves.itemTokenPrice = new Array();
fVindicatorsOrnamentedGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsOrnamentedGreaves.itemStats = new Array();
fVindicatorsOrnamentedGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ornamented Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsOrnamentedGreaves; ++i;

var fVindicatorsRingmailBracers = new RewardItem("alliance","Vindicator's Ringmail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsRingmailBracers.itemHonorPrice = new Array();
fVindicatorsRingmailBracers.itemHonorPrice[1] = 11794
fVindicatorsRingmailBracers.itemTokenPrice = new Array();
fVindicatorsRingmailBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsRingmailBracers.itemStats = new Array();
fVindicatorsRingmailBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ringmail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsRingmailBracers; ++i;



var fVindicatorsRingmailGirdle = new RewardItem("alliance","Vindicator's Ringmail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsRingmailGirdle.itemHonorPrice = new Array();
fVindicatorsRingmailGirdle.itemHonorPrice[1] = 17850
fVindicatorsRingmailGirdle.itemTokenPrice = new Array();
fVindicatorsRingmailGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsRingmailGirdle.itemStats = new Array();
fVindicatorsRingmailGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ringmail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsRingmailGirdle; ++i;


var fVindicatorsRingmailSabatons = new RewardItem("alliance","Vindicator's Ringmail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsRingmailSabatons.itemHonorPrice = new Array();
fVindicatorsRingmailSabatons.itemHonorPrice[1] = 17850
fVindicatorsRingmailSabatons.itemTokenPrice = new Array();
fVindicatorsRingmailSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsRingmailSabatons.itemStats = new Array();
fVindicatorsRingmailSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ringmail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsRingmailSabatons; ++i;





var fVindicatorsBandOfDominance = new RewardItem("alliance","Vindicator's Band of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVindicatorsBandOfDominance.itemHonorPrice = new Array();
fVindicatorsBandOfDominance.itemHonorPrice[9] = 15300
fVindicatorsBandOfDominance.itemTokenPrice = new Array();
fVindicatorsBandOfDominance.itemTokenPrice[9] = new Array(10,0,0,0);
fVindicatorsBandOfDominance.itemStats = new Array();
fVindicatorsBandOfDominance.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Band of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+31 Stamina<br>+15 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsBandOfDominance; ++i;



var fVindicatorsBandOfSalvation = new RewardItem("alliance","Vindicator's Band of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVindicatorsBandOfSalvation.itemHonorPrice = new Array();
fVindicatorsBandOfSalvation.itemHonorPrice[9] = 15300
fVindicatorsBandOfSalvation.itemTokenPrice = new Array();
fVindicatorsBandOfSalvation.itemTokenPrice[9] = new Array(10,0,0,0);
fVindicatorsBandOfSalvation.itemStats = new Array();
fVindicatorsBandOfSalvation.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Band of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+34 Stamina<br>+20 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsBandOfSalvation; ++i;



var fVindicatorsBandOfTriumph = new RewardItem("alliance","Vindicator's Band of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVindicatorsBandOfTriumph.itemHonorPrice = new Array();
fVindicatorsBandOfTriumph.itemHonorPrice[9] = 15300
fVindicatorsBandOfTriumph.itemTokenPrice = new Array();
fVindicatorsBandOfTriumph.itemTokenPrice[9] = new Array(10,0,0,0);
fVindicatorsBandOfTriumph.itemStats = new Array();
fVindicatorsBandOfTriumph.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Band of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+34 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 56 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsBandOfTriumph; ++i;



var fVindicatorsPendantOfConquest = new RewardItem("alliance","Vindicator's Pendant of Conquest","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfConquest.itemHonorPrice = new Array();
fVindicatorsPendantOfConquest.itemHonorPrice[9] = 15300
fVindicatorsPendantOfConquest.itemTokenPrice = new Array();
fVindicatorsPendantOfConquest.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfConquest.itemStats = new Array();
fVindicatorsPendantOfConquest.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Conquest</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+31 Stamina<br>+15 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfConquest; ++i;


var fVindicatorsPendantOfDominance = new RewardItem("alliance","Vindicator's Pendant of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfDominance.itemHonorPrice = new Array();
fVindicatorsPendantOfDominance.itemHonorPrice[9] = 15300
fVindicatorsPendantOfDominance.itemTokenPrice = new Array();
fVindicatorsPendantOfDominance.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfDominance.itemStats = new Array();
fVindicatorsPendantOfDominance.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+35 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfDominance; ++i;


var fVindicatorsPendantOfSalvation = new RewardItem("alliance","Vindicator's Pendant of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfSalvation.itemHonorPrice = new Array();
fVindicatorsPendantOfSalvation.itemHonorPrice[9] = 15300
fVindicatorsPendantOfSalvation.itemTokenPrice = new Array();
fVindicatorsPendantOfSalvation.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfSalvation.itemStats = new Array();
fVindicatorsPendantOfSalvation.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+34 Stamina<br>+16 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfSalvation; ++i;


var fVindicatorsPendantOfTriumph = new RewardItem("alliance","Vindicator's Pendant of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfTriumph.itemHonorPrice = new Array();
fVindicatorsPendantOfTriumph.itemHonorPrice[9] = 15300
fVindicatorsPendantOfTriumph.itemTokenPrice = new Array();
fVindicatorsPendantOfTriumph.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfTriumph.itemStats = new Array();
fVindicatorsPendantOfTriumph.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+35 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfTriumph; ++i;




//-------------------------------------------------------------------
//---Horde below


var fVindicatorsChainBracers = new RewardItem("horde","Vindicator's Chain Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsChainBracers.itemHonorPrice = new Array();
fVindicatorsChainBracers.itemHonorPrice[1] = 11794
fVindicatorsChainBracers.itemTokenPrice = new Array();
fVindicatorsChainBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsChainBracers.itemStats = new Array();
fVindicatorsChainBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Chain Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+23 Agility<br>+33 Stamina<br>+13 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsChainBracers; ++i;



var fVindicatorsChainGirdle = new RewardItem("horde","Vindicator's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsChainGirdle.itemHonorPrice = new Array();
fVindicatorsChainGirdle.itemHonorPrice[1] = 17850
fVindicatorsChainGirdle.itemTokenPrice = new Array();
fVindicatorsChainGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsChainGirdle.itemStats = new Array();
fVindicatorsChainGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Chain Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+33 Agility<br>+48 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsChainGirdle; ++i;



var fVindicatorsChainSabatons = new RewardItem("horde","Vindicator's Chain Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsChainSabatons.itemHonorPrice = new Array();
fVindicatorsChainSabatons.itemHonorPrice[1] = 17850
fVindicatorsChainSabatons.itemTokenPrice = new Array();
fVindicatorsChainSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsChainSabatons.itemStats = new Array();
fVindicatorsChainSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Chain Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+33 Agility<br>+48 Stamina<br>+23 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsChainSabatons; ++i;

var fVindicatorsDragonhideBelt = new RewardItem("horde","Vindicator's Dragonhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsDragonhideBelt.itemHonorPrice = new Array();
fVindicatorsDragonhideBelt.itemHonorPrice[5] = 17850
fVindicatorsDragonhideBelt.itemTokenPrice = new Array();
fVindicatorsDragonhideBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsDragonhideBelt.itemStats = new Array();
fVindicatorsDragonhideBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dragonhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>300 Armor<br>+30 Strength<br>+29 Agility<br>+42 Stamina<br>+20 Intellect<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDragonhideBelt; ++i;


var fVindicatorsDragonhideBoots = new RewardItem("horde","Vindicator's Dragonhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsDragonhideBoots.itemHonorPrice = new Array();
fVindicatorsDragonhideBoots.itemHonorPrice[5] = 17850
fVindicatorsDragonhideBoots.itemTokenPrice = new Array();
fVindicatorsDragonhideBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsDragonhideBoots.itemStats = new Array();
fVindicatorsDragonhideBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dragonhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>357 Armor<br>+30 Strength<br>+29 Agility<br>+42 Stamina<br>+20 Intellect<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDragonhideBoots; ++i;

var fVindicatorsDragonhideBracers = new RewardItem("horde","Vindicator's Dragonhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsDragonhideBracers.itemHonorPrice = new Array();
fVindicatorsDragonhideBracers.itemHonorPrice[5] = 11794
fVindicatorsDragonhideBracers.itemTokenPrice = new Array();
fVindicatorsDragonhideBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsDragonhideBracers.itemStats = new Array();
fVindicatorsDragonhideBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dragonhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>236 Armor<br>+22 Strength<br>+22 Agility<br>+29 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDragonhideBracers; ++i;

var fVindicatorsDreadweaveBelt = new RewardItem("horde","Vindicator's Dreadweave Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsDreadweaveBelt.itemHonorPrice = new Array();
fVindicatorsDreadweaveBelt.itemHonorPrice[2] = 17850
fVindicatorsDreadweaveBelt.itemTokenPrice = new Array();
fVindicatorsDreadweaveBelt.itemTokenPrice[2] = new Array(0,40,0,0);
fVindicatorsDreadweaveBelt.itemStats = new Array();
fVindicatorsDreadweaveBelt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dreadweave Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>138 Armor<br>+49 Stamina<br>+34 Intellect<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 41.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDreadweaveBelt; ++i;

var fVindicatorsDreadweaveCuffs = new RewardItem("horde","Vindicator's Dreadweave Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsDreadweaveCuffs.itemHonorPrice = new Array();
fVindicatorsDreadweaveCuffs.itemHonorPrice[2] = 11794
fVindicatorsDreadweaveCuffs.itemTokenPrice = new Array();
fVindicatorsDreadweaveCuffs.itemTokenPrice[2] = new Array(0,0,0,20);
fVindicatorsDreadweaveCuffs.itemStats = new Array();
fVindicatorsDreadweaveCuffs.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dreadweave Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+37 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDreadweaveCuffs; ++i;


var fVindicatorsDreadweaveStalkers = new RewardItem("horde","Vindicator's Dreadweave Stalkers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVindicatorsDreadweaveStalkers.itemHonorPrice = new Array();
fVindicatorsDreadweaveStalkers.itemHonorPrice[2] = 17850
fVindicatorsDreadweaveStalkers.itemTokenPrice = new Array();
fVindicatorsDreadweaveStalkers.itemTokenPrice[2] = new Array(0,0,40,0);
fVindicatorsDreadweaveStalkers.itemStats = new Array();
fVindicatorsDreadweaveStalkers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Dreadweave Stalkers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>168 Armor<br>+49 Stamina<br>+34 Intellect<br>Durability 50 / 50<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 41.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsDreadweaveStalkers; ++i;


var fVindicatorsKodohideBelt = new RewardItem("horde","Vindicator's Kodohide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsKodohideBelt.itemHonorPrice = new Array();
fVindicatorsKodohideBelt.itemHonorPrice[5] = 17850
fVindicatorsKodohideBelt.itemTokenPrice = new Array();
fVindicatorsKodohideBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsKodohideBelt.itemStats = new Array();
fVindicatorsKodohideBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Kodohide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>300 Armor<br>+43 Stamina<br>+30 Intellect<br>+23 Spirit<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBelt; ++i;

var fVindicatorsKodohideBoots = new RewardItem("horde","Vindicator's Kodohide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsKodohideBoots.itemHonorPrice = new Array();
fVindicatorsKodohideBoots.itemHonorPrice[5] = 17850
fVindicatorsKodohideBoots.itemTokenPrice = new Array();
fVindicatorsKodohideBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsKodohideBoots.itemStats = new Array();
fVindicatorsKodohideBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Kodohide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>357 Armor<br>+43 Stamina<br>+30 Intellect<br>+23 Spirit<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBoots; ++i;


var fVindicatorsKodohideBracers = new RewardItem("horde","Vindicator's Kodohide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsKodohideBracers.itemHonorPrice = new Array();
fVindicatorsKodohideBracers.itemHonorPrice[5] = 11794
fVindicatorsKodohideBracers.itemTokenPrice = new Array();
fVindicatorsKodohideBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsKodohideBracers.itemStats = new Array();
fVindicatorsKodohideBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Kodohide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>236 Armor<br>+29 Stamina<br>+22 Intellect<br>+17 Spirit<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 40 and damage done by up to 14 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBracers; ++i;


var fVindicatorsLamellarBelt = new RewardItem("horde","Vindicator's Lamellar Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsLamellarBelt.itemHonorPrice = new Array();
fVindicatorsLamellarBelt.itemHonorPrice[8] = 17850
fVindicatorsLamellarBelt.itemTokenPrice = new Array();
fVindicatorsLamellarBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsLamellarBelt.itemStats = new Array();
fVindicatorsLamellarBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Lamellar Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLamellarBelt; ++i;



var fVindicatorsLamellarBracers = new RewardItem("horde","Vindicator's Lamellar Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsLamellarBracers.itemHonorPrice = new Array();
fVindicatorsLamellarBracers.itemHonorPrice[8] = 11794
fVindicatorsLamellarBracers.itemTokenPrice = new Array();
fVindicatorsLamellarBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsLamellarBracers.itemStats = new Array();
fVindicatorsLamellarBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Lamellar Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLamellarBracers; ++i;



var fVindicatorsLamellarGreaves = new RewardItem("horde","Vindicator's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsLamellarGreaves.itemHonorPrice = new Array();
fVindicatorsLamellarGreaves.itemHonorPrice[8] = 17850
fVindicatorsLamellarGreaves.itemTokenPrice = new Array();
fVindicatorsLamellarGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsLamellarGreaves.itemStats = new Array();
fVindicatorsLamellarGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Lamellar Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLamellarGreaves; ++i;



var fVindicatorsLeatherBelt = new RewardItem("horde","Vindicator's Leather Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsLeatherBelt.itemHonorPrice = new Array();
fVindicatorsLeatherBelt.itemHonorPrice[5] = 17850
fVindicatorsLeatherBelt.itemTokenPrice = new Array();
fVindicatorsLeatherBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsLeatherBelt.itemStats = new Array();
fVindicatorsLeatherBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Leather Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>258 Armor<br>+33 Agility<br>+49 Stamina<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLeatherBelt; ++i;


var fVindicatorsLeatherBoots = new RewardItem("horde","Vindicator's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsLeatherBoots.itemHonorPrice = new Array();
fVindicatorsLeatherBoots.itemHonorPrice[5] = 17850
fVindicatorsLeatherBoots.itemTokenPrice = new Array();
fVindicatorsLeatherBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsLeatherBoots.itemStats = new Array();
fVindicatorsLeatherBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Leather Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>315 Armor<br>+33 Agility<br>+49 Stamina<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLeatherBoots; ++i;


var fVindicatorsLeatherBracers = new RewardItem("horde","Vindicator's Leather Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsLeatherBracers.itemHonorPrice = new Array();
fVindicatorsLeatherBracers.itemHonorPrice[5] = 11794
fVindicatorsLeatherBracers.itemTokenPrice = new Array();
fVindicatorsLeatherBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsLeatherBracers.itemStats = new Array();
fVindicatorsLeatherBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Leather Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>194 Armor<br>+25 Agility<br>+33 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLeatherBracers; ++i;



var fVindicatorsLinkedBracers = new RewardItem("horde","Vindicator's Linked Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsLinkedBracers.itemHonorPrice = new Array();
fVindicatorsLinkedBracers.itemHonorPrice[1] = 11794
fVindicatorsLinkedBracers.itemTokenPrice = new Array();
fVindicatorsLinkedBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsLinkedBracers.itemStats = new Array();
fVindicatorsLinkedBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Linked Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+25 Strength<br>+33 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLinkedBracers; ++i;


var fVindicatorsLinkedGirdle = new RewardItem("horde","Vindicator's Linked Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsLinkedGirdle.itemHonorPrice = new Array();
fVindicatorsLinkedGirdle.itemHonorPrice[1] = 17850
fVindicatorsLinkedGirdle.itemTokenPrice = new Array();
fVindicatorsLinkedGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsLinkedGirdle.itemStats = new Array();
fVindicatorsLinkedGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Linked Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+34 Strength<br>+49 Stamina<br>+23 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLinkedGirdle; ++i;

var fVindicatorsLinkedSabatons = new RewardItem("horde","Vindicator's Linked Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsLinkedSabatons.itemHonorPrice = new Array();
fVindicatorsLinkedSabatons.itemHonorPrice[1] = 17850
fVindicatorsLinkedSabatons.itemTokenPrice = new Array();
fVindicatorsLinkedSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsLinkedSabatons.itemStats = new Array();
fVindicatorsLinkedSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Linked Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+33 Strength<br>+49 Stamina<br>+23 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 34.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsLinkedSabatons; ++i;



var fVindicatorsMailBracers = new RewardItem("horde","Vindicator's Mail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsMailBracers.itemHonorPrice = new Array();
fVindicatorsMailBracers.itemHonorPrice[1] = 11794
fVindicatorsMailBracers.itemTokenPrice = new Array();
fVindicatorsMailBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsMailBracers.itemStats = new Array();
fVindicatorsMailBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMailBracers; ++i;



var fVindicatorsMailGirdle = new RewardItem("horde","Vindicator's Mail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsMailGirdle.itemHonorPrice = new Array();
fVindicatorsMailGirdle.itemHonorPrice[1] = 17850
fVindicatorsMailGirdle.itemTokenPrice = new Array();
fVindicatorsMailGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsMailGirdle.itemStats = new Array();
fVindicatorsMailGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMailGirdle; ++i;

var fVindicatorsMailSabatons = new RewardItem("horde","Vindicator's Mail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsMailSabatons.itemHonorPrice = new Array();
fVindicatorsMailSabatons.itemHonorPrice[1] = 17850
fVindicatorsMailSabatons.itemTokenPrice = new Array();
fVindicatorsMailSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsMailSabatons.itemStats = new Array();
fVindicatorsMailSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMailSabatons; ++i;



var fVindicatorsPlateBelt = new RewardItem("horde","Vindicator's Plate Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsPlateBelt.itemHonorPrice = new Array();
fVindicatorsPlateBelt.itemHonorPrice[8] = 17850
fVindicatorsPlateBelt.itemTokenPrice = new Array();
fVindicatorsPlateBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsPlateBelt.itemStats = new Array();
fVindicatorsPlateBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Plate Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+35 Strength<br>+49 Stamina<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 35.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPlateBelt; ++i;



var fVindicatorsPlateBracers = new RewardItem("horde","Vindicator's Plate Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsPlateBracers.itemHonorPrice = new Array();
fVindicatorsPlateBracers.itemHonorPrice[8] = 11794
fVindicatorsPlateBracers.itemTokenPrice = new Array();
fVindicatorsPlateBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsPlateBracers.itemStats = new Array();
fVindicatorsPlateBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Plate Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+25 Strength<br>+36 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Strength</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPlateBracers; ++i;


var fVindicatorsPlateGreaves = new RewardItem("horde","Vindicator's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsPlateGreaves.itemHonorPrice = new Array();
fVindicatorsPlateGreaves.itemHonorPrice[8] = 17850
fVindicatorsPlateGreaves.itemTokenPrice = new Array();
fVindicatorsPlateGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsPlateGreaves.itemStats = new Array();
fVindicatorsPlateGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Plate Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+35 Strength<br>+49 Stamina<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 35.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPlateGreaves; ++i;


var fVindicatorsScaledBelt = new RewardItem("horde","Vindicator's Scaled Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsScaledBelt.itemHonorPrice = new Array();
fVindicatorsScaledBelt.itemHonorPrice[8] = 17850
fVindicatorsScaledBelt.itemTokenPrice = new Array();
fVindicatorsScaledBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsScaledBelt.itemStats = new Array();
fVindicatorsScaledBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Scaled Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+27 Strength<br>+39 Stamina<br>+26 Intellect<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsScaledBelt; ++i;



var fVindicatorsScaledBracers = new RewardItem("horde","Vindicator's Scaled Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsScaledBracers.itemHonorPrice = new Array();
fVindicatorsScaledBracers.itemHonorPrice[8] = 11794
fVindicatorsScaledBracers.itemTokenPrice = new Array();
fVindicatorsScaledBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsScaledBracers.itemStats = new Array();
fVindicatorsScaledBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Scaled Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+19 Strength<br>+28 Stamina<br>+15 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsScaledBracers; ++i;

var fVindicatorsScaledGreaves = new RewardItem("horde","Vindicator's Scaled Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsScaledGreaves.itemHonorPrice = new Array();
fVindicatorsScaledGreaves.itemHonorPrice[8] = 17850
fVindicatorsScaledGreaves.itemTokenPrice = new Array();
fVindicatorsScaledGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsScaledGreaves.itemStats = new Array();
fVindicatorsScaledGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Scaled Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+27 Strength<br>+39 Stamina<br>+26 Intellect<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsScaledGreaves; ++i;



var fVindicatorsSilkBelt = new RewardItem("horde","Vindicator's Silk Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsSilkBelt.itemHonorPrice = new Array();
fVindicatorsSilkBelt.itemHonorPrice[2] = 17850
fVindicatorsSilkBelt.itemTokenPrice = new Array();
fVindicatorsSilkBelt.itemTokenPrice[2] = new Array(0,40,0,0);
fVindicatorsSilkBelt.itemStats = new Array();
fVindicatorsSilkBelt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Silk Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>138 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsSilkBelt; ++i;


var fVindicatorsSilkCuffs = new RewardItem("horde","Vindicator's Silk Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsSilkCuffs.itemHonorPrice = new Array();
fVindicatorsSilkCuffs.itemHonorPrice[2] = 11794
fVindicatorsSilkCuffs.itemTokenPrice = new Array();
fVindicatorsSilkCuffs.itemTokenPrice[2] = new Array(0,0,0,20);
fVindicatorsSilkCuffs.itemStats = new Array();
fVindicatorsSilkCuffs.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Silk Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+29 Stamina<br>+22 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsSilkCuffs; ++i;

var fVindicatorsSilkFootguards = new RewardItem("horde","Vindicator's Silk Footguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVindicatorsSilkFootguards.itemHonorPrice = new Array();
fVindicatorsSilkFootguards.itemHonorPrice[2] = 17850
fVindicatorsSilkFootguards.itemTokenPrice = new Array();
fVindicatorsSilkFootguards.itemTokenPrice[2] = new Array(0,0,40,0);
fVindicatorsSilkFootguards.itemStats = new Array();
fVindicatorsSilkFootguards.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Silk Footguards</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>168 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 50 / 50<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsSilkFootguards; ++i;


var fVindicatorsMoonclothBelt = new RewardItem("horde","Vindicator's Mooncloth Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsMoonclothBelt.itemHonorPrice = new Array();
fVindicatorsMoonclothBelt.itemHonorPrice[2] = 17850
fVindicatorsMoonclothBelt.itemTokenPrice = new Array();
fVindicatorsMoonclothBelt.itemTokenPrice[2] = new Array(0,40,0,0);
fVindicatorsMoonclothBelt.itemStats = new Array();
fVindicatorsMoonclothBelt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mooncloth Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>138 Armor<br>+49 Stamina<br>+33 Intellect<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 77 and damage done by up to 26 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMoonclothBelt; ++i;

var fVindicatorsMoonclothCuffs = new RewardItem("horde","Vindicator's Mooncloth Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsMoonclothCuffs.itemHonorPrice = new Array();
fVindicatorsMoonclothCuffs.itemHonorPrice[2] = 11794
fVindicatorsMoonclothCuffs.itemTokenPrice = new Array();
fVindicatorsMoonclothCuffs.itemTokenPrice[2] = new Array(0,0,0,20);
fVindicatorsMoonclothCuffs.itemStats = new Array();
fVindicatorsMoonclothCuffs.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mooncloth Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>103 Armor<br>+37 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Durability 35 / 35<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 55 and damage done by up to 19 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMoonclothCuffs; ++i;

var fVindicatorsMoonclothSlippers = new RewardItem("horde","Vindicator's Mooncloth Slippers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVindicatorsMoonclothSlippers.itemHonorPrice = new Array();
fVindicatorsMoonclothSlippers.itemHonorPrice[2] = 17850
fVindicatorsMoonclothSlippers.itemTokenPrice = new Array();
fVindicatorsMoonclothSlippers.itemTokenPrice[2] = new Array(0,0,40,0);
fVindicatorsMoonclothSlippers.itemStats = new Array();
fVindicatorsMoonclothSlippers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Mooncloth Slippers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>168 Armor<br>+49 Stamina<br>+33 Intellect<br>Durability 50 / 50<br>Classes: Priest, Mage, Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 77 and damage done by up to 26 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsMoonclothSlippers; ++i;

var fVindicatorsKodohideBelt = new RewardItem("horde","Vindicator's Wyrmhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVindicatorsKodohideBelt.itemHonorPrice = new Array();
fVindicatorsKodohideBelt.itemHonorPrice[5] = 17850
fVindicatorsKodohideBelt.itemTokenPrice = new Array();
fVindicatorsKodohideBelt.itemTokenPrice[5] = new Array(0,40,0,0);
fVindicatorsKodohideBelt.itemStats = new Array();
fVindicatorsKodohideBelt.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Wyrmhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>300 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBelt; ++i;

var fVindicatorsKodohideBoots = new RewardItem("horde","Vindicator's Wyrmhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVindicatorsKodohideBoots.itemHonorPrice = new Array();
fVindicatorsKodohideBoots.itemHonorPrice[5] = 17850
fVindicatorsKodohideBoots.itemTokenPrice = new Array();
fVindicatorsKodohideBoots.itemTokenPrice[5] = new Array(0,0,40,0);
fVindicatorsKodohideBoots.itemStats = new Array();
fVindicatorsKodohideBoots.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Wyrmhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>357 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 60 / 60<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBoots; ++i;

var fVindicatorsKodohideBracers = new RewardItem("horde","Vindicator's Wyrmhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-vindicators-armor.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Bracer_07.gif&reason=external-or-uncollected-resource");
fVindicatorsKodohideBracers.itemHonorPrice = new Array();
fVindicatorsKodohideBracers.itemHonorPrice[5] = 11794
fVindicatorsKodohideBracers.itemTokenPrice = new Array();
fVindicatorsKodohideBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fVindicatorsKodohideBracers.itemStats = new Array();
fVindicatorsKodohideBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Wyrmhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>236 Armor<br>+31 Stamina<br>+20 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40 / 40<br>Classes: Rogue, Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsKodohideBracers; ++i;

var fVindicatorsOrnamentedBelt = new RewardItem("horde","Vindicator's Ornamented Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVindicatorsOrnamentedBelt.itemHonorPrice = new Array();
fVindicatorsOrnamentedBelt.itemHonorPrice[8] = 17850
fVindicatorsOrnamentedBelt.itemTokenPrice = new Array();
fVindicatorsOrnamentedBelt.itemTokenPrice[8] = new Array(0,40,0,0);
fVindicatorsOrnamentedBelt.itemStats = new Array();
fVindicatorsOrnamentedBelt.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ornamented Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>1027 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsOrnamentedBelt; ++i;



var fVindicatorsOrnamentedBracers = new RewardItem("horde","Vindicator's Ornamented Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVindicatorsOrnamentedBracers.itemHonorPrice = new Array();
fVindicatorsOrnamentedBracers.itemHonorPrice[8] = 11794
fVindicatorsOrnamentedBracers.itemTokenPrice = new Array();
fVindicatorsOrnamentedBracers.itemTokenPrice[8] = new Array(0,0,0,20);
fVindicatorsOrnamentedBracers.itemStats = new Array();
fVindicatorsOrnamentedBracers.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ornamented Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>772 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55 / 55<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsOrnamentedBracers; ++i;

var fVindicatorsOrnamentedGreaves = new RewardItem("horde","Vindicator's Ornamented Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVindicatorsOrnamentedGreaves.itemHonorPrice = new Array();
fVindicatorsOrnamentedGreaves.itemHonorPrice[8] = 17850
fVindicatorsOrnamentedGreaves.itemTokenPrice = new Array();
fVindicatorsOrnamentedGreaves.itemTokenPrice[8] = new Array(0,0,40,0);
fVindicatorsOrnamentedGreaves.itemStats = new Array();
fVindicatorsOrnamentedGreaves.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ornamented Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1255 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 75 / 75<br>Classes: Warrior, Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsOrnamentedGreaves; ++i;

var fVindicatorsRingmailBracers = new RewardItem("horde","Vindicator's Ringmail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVindicatorsRingmailBracers.itemHonorPrice = new Array();
fVindicatorsRingmailBracers.itemHonorPrice[1] = 11794
fVindicatorsRingmailBracers.itemTokenPrice = new Array();
fVindicatorsRingmailBracers.itemTokenPrice[1] = new Array(0,0,0,20);
fVindicatorsRingmailBracers.itemStats = new Array();
fVindicatorsRingmailBracers.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ringmail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>432 Armor<br>+29 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsRingmailBracers; ++i;



var fVindicatorsRingmailGirdle = new RewardItem("horde","Vindicator's Ringmail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVindicatorsRingmailGirdle.itemHonorPrice = new Array();
fVindicatorsRingmailGirdle.itemHonorPrice[1] = 17850
fVindicatorsRingmailGirdle.itemTokenPrice = new Array();
fVindicatorsRingmailGirdle.itemTokenPrice[1] = new Array(0,40,0,0);
fVindicatorsRingmailGirdle.itemStats = new Array();
fVindicatorsRingmailGirdle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ringmail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>575 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 50 / 50<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsRingmailGirdle; ++i;


var fVindicatorsRingmailSabatons = new RewardItem("horde","Vindicator's Ringmail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVindicatorsRingmailSabatons.itemHonorPrice = new Array();
fVindicatorsRingmailSabatons.itemHonorPrice[1] = 17850
fVindicatorsRingmailSabatons.itemTokenPrice = new Array();
fVindicatorsRingmailSabatons.itemTokenPrice[1] = new Array(0,0,40,0);
fVindicatorsRingmailSabatons.itemStats = new Array();
fVindicatorsRingmailSabatons.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Ringmail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>702 Armor<br>+43 Stamina<br>+30 Intellect<br>Durability 70 / 70<br>Classes: Hunter, Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 66 and damage done by up to 22 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsRingmailSabatons; ++i;





var fVindicatorsBandOfDominance = new RewardItem("horde","Vindicator's Band of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVindicatorsBandOfDominance.itemHonorPrice = new Array();
fVindicatorsBandOfDominance.itemHonorPrice[9] = 15300
fVindicatorsBandOfDominance.itemTokenPrice = new Array();
fVindicatorsBandOfDominance.itemTokenPrice[9] = new Array(10,0,0,0);
fVindicatorsBandOfDominance.itemStats = new Array();
fVindicatorsBandOfDominance.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Band of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+31 Stamina<br>+15 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsBandOfDominance; ++i;



var fVindicatorsBandOfSalvation = new RewardItem("horde","Vindicator's Band of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVindicatorsBandOfSalvation.itemHonorPrice = new Array();
fVindicatorsBandOfSalvation.itemHonorPrice[9] = 15300
fVindicatorsBandOfSalvation.itemTokenPrice = new Array();
fVindicatorsBandOfSalvation.itemTokenPrice[9] = new Array(10,0,0,0);
fVindicatorsBandOfSalvation.itemStats = new Array();
fVindicatorsBandOfSalvation.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Band of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+34 Stamina<br>+20 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsBandOfSalvation; ++i;



var fVindicatorsBandOfTriumph = new RewardItem("horde","Vindicator's Band of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVindicatorsBandOfTriumph.itemHonorPrice = new Array();
fVindicatorsBandOfTriumph.itemHonorPrice[9] = 15300
fVindicatorsBandOfTriumph.itemTokenPrice = new Array();
fVindicatorsBandOfTriumph.itemTokenPrice[9] = new Array(10,0,0,0);
fVindicatorsBandOfTriumph.itemStats = new Array();
fVindicatorsBandOfTriumph.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Band of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+34 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 56 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsBandOfTriumph; ++i;



var fVindicatorsPendantOfConquest = new RewardItem("horde","Vindicator's Pendant of Conquest","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfConquest.itemHonorPrice = new Array();
fVindicatorsPendantOfConquest.itemHonorPrice[9] = 15300
fVindicatorsPendantOfConquest.itemTokenPrice = new Array();
fVindicatorsPendantOfConquest.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfConquest.itemStats = new Array();
fVindicatorsPendantOfConquest.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Conquest</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+31 Stamina<br>+15 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfConquest; ++i;


var fVindicatorsPendantOfDominance = new RewardItem("horde","Vindicator's Pendant of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfDominance.itemHonorPrice = new Array();
fVindicatorsPendantOfDominance.itemHonorPrice[9] = 15300
fVindicatorsPendantOfDominance.itemTokenPrice = new Array();
fVindicatorsPendantOfDominance.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfDominance.itemStats = new Array();
fVindicatorsPendantOfDominance.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+35 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfDominance; ++i;


var fVindicatorsPendantOfSalvation = new RewardItem("horde","Vindicator's Pendant of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfSalvation.itemHonorPrice = new Array();
fVindicatorsPendantOfSalvation.itemHonorPrice[9] = 15300
fVindicatorsPendantOfSalvation.itemTokenPrice = new Array();
fVindicatorsPendantOfSalvation.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfSalvation.itemStats = new Array();
fVindicatorsPendantOfSalvation.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+34 Stamina<br>+16 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfSalvation; ++i;


var fVindicatorsPendantOfTriumph = new RewardItem("horde","Vindicator's Pendant of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVindicatorsPendantOfTriumph.itemHonorPrice = new Array();
fVindicatorsPendantOfTriumph.itemHonorPrice[9] = 15300
fVindicatorsPendantOfTriumph.itemTokenPrice = new Array();
fVindicatorsPendantOfTriumph.itemTokenPrice[9] = new Array(0,0,10,0);
fVindicatorsPendantOfTriumph.itemStats = new Array();
fVindicatorsPendantOfTriumph.itemStats[9] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Pendant of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+35 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsPendantOfTriumph; ++i;


//------END REWARDS DEFINITION------
