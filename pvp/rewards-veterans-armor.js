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

var fVeteransChainBracers = new RewardItem("alliance","Veteran's Chain Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransChainBracers.itemHonorPrice = new Array();
fVeteransChainBracers.itemHonorPrice[0] = 11794
fVeteransChainBracers.itemTokenPrice = new Array();
fVeteransChainBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransChainBracers.itemStats = new Array();
fVeteransChainBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Chain Bracers</span>\
<br>Binds when picked up<br>Wrist<br>388 Armor<span class=\"myRight\">Mail</span>\
<br>+20 Agility<br>+29 Stamina<br>+10 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span><br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 18.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransChainBracers; ++i;

var fVeteransChainGirdle = new RewardItem("alliance","Veteran's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransChainGirdle.itemHonorPrice = new Array();
fVeteransChainGirdle.itemHonorPrice[0] = 17850
fVeteransChainGirdle.itemTokenPrice = new Array();
fVeteransChainGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransChainGirdle.itemStats = new Array();
fVeteransChainGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Chain Girdle</span>\
<br>Binds when picked up<br>Waist<br>537 Armor<span class=\"myRight\">Mail</span>\
<br>+30 Agility<br>+45 Stamina<br>+20 Intellect<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransChainGirdle; ++i;

var fVeteransChainSabatons = new RewardItem("alliance","Veteran's Chain Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransChainSabatons.itemHonorPrice = new Array();
fVeteransChainSabatons.itemHonorPrice[0] = 17850
fVeteransChainSabatons.itemTokenPrice = new Array();
fVeteransChainSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransChainSabatons.itemStats = new Array();
fVeteransChainSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Chain Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+30 Agility<br>+45 Stamina<br>+20 Intellect<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransChainSabatons; ++i;

var fVeteransDragonhideBelt = new RewardItem("alliance","Veteran's Dragonhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransDragonhideBelt.itemHonorPrice = new Array();
fVeteransDragonhideBelt.itemHonorPrice[0] = 17850
fVeteransDragonhideBelt.itemTokenPrice = new Array();
fVeteransDragonhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransDragonhideBelt.itemStats = new Array();
fVeteransDragonhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dragonhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+27 Strength<br>+26 Agility<br>+39 Stamina<br>+17 Intellect\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDragonhideBelt; ++i;

var fVeteransDragonhideBoots = new RewardItem("alliance","Veteran's Dragonhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransDragonhideBoots.itemHonorPrice = new Array();
fVeteransDragonhideBoots.itemHonorPrice[0] = 17850
fVeteransDragonhideBoots.itemTokenPrice = new Array();
fVeteransDragonhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransDragonhideBoots.itemStats = new Array();
fVeteransDragonhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dragonhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>336 Armor<br>+27 Strength<br>+26 Agility<br>+39 Stamina<br>+17 Intellect\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDragonhideBoots; ++i;

var fVeteransDragonhideBracers = new RewardItem("alliance","Veteran's Dragonhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransDragonhideBracers.itemHonorPrice = new Array();
fVeteransDragonhideBracers.itemHonorPrice[0] = 11794
fVeteransDragonhideBracers.itemTokenPrice = new Array();
fVeteransDragonhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransDragonhideBracers.itemStats = new Array();
fVeteransDragonhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dragonhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>216 Armor<br>+19 Strength<br>+18 Agility<br>+25 Stamina<br><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDragonhideBracers; ++i;

var fVeteransDreadweaveBelt = new RewardItem("alliance","Veteran's Dreadweave Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransDreadweaveBelt.itemHonorPrice = new Array();
fVeteransDreadweaveBelt.itemHonorPrice[0] = 17850
fVeteransDreadweaveBelt.itemTokenPrice = new Array();
fVeteransDreadweaveBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransDreadweaveBelt.itemStats = new Array();
fVeteransDreadweaveBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dreadweave Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>128 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDreadweaveBelt; ++i;

var fVeteransDreadweaveCuffs = new RewardItem("alliance","Veteran's Dreadweave Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransDreadweaveCuffs.itemHonorPrice = new Array();
fVeteransDreadweaveCuffs.itemHonorPrice[0] = 11794
fVeteransDreadweaveCuffs.itemTokenPrice = new Array();
fVeteransDreadweaveCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransDreadweaveCuffs.itemStats = new Array();
fVeteransDreadweaveCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dreadweave Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>93 Armor<br>+31 Stamina<br>+16 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDreadweaveCuffs; ++i;

var fVeteransDreadweaveStalkers = new RewardItem("alliance","Veteran's Dreadweave Stalkers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVeteransDreadweaveStalkers.itemHonorPrice = new Array();
fVeteransDreadweaveStalkers.itemHonorPrice[0] = 17850
fVeteransDreadweaveStalkers.itemTokenPrice = new Array();
fVeteransDreadweaveStalkers.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransDreadweaveStalkers.itemStats = new Array();
fVeteransDreadweaveStalkers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dreadweave Stalkers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>157 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDreadweaveStalkers; ++i;

var fVeteransKodohideBelt = new RewardItem("alliance","Veteran's Kodohide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransKodohideBelt.itemHonorPrice = new Array();
fVeteransKodohideBelt.itemHonorPrice[0] = 17850
fVeteransKodohideBelt.itemTokenPrice = new Array();
fVeteransKodohideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransKodohideBelt.itemStats = new Array();
fVeteransKodohideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Kodohide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransKodohideBelt; ++i;

var fVeteransKodohideBoots = new RewardItem("alliance","Veteran's Kodohide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransKodohideBoots.itemHonorPrice = new Array();
fVeteransKodohideBoots.itemHonorPrice[0] = 17850
fVeteransKodohideBoots.itemTokenPrice = new Array();
fVeteransKodohideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransKodohideBoots.itemStats = new Array();
fVeteransKodohideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Kodohide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>336 Armor<br>+39 Stamina<br>+26 Intellect\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 70.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransKodohideBoots; ++i;

var fVeteransKodohideBracers = new RewardItem("alliance","Veteran's Kodohide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransKodohideBracers.itemHonorPrice = new Array();
fVeteransKodohideBracers.itemHonorPrice[0] = 11794
fVeteransKodohideBracers.itemTokenPrice = new Array();
fVeteransKodohideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransKodohideBracers.itemStats = new Array();
fVeteransKodohideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Kodohide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>216 Armor<br>+25 Stamina<br>+18 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransKodohideBracers; ++i;

var fVeteransLamellarBelt = new RewardItem("alliance","Veteran's Lamellar Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransLamellarBelt.itemHonorPrice = new Array();
fVeteransLamellarBelt.itemHonorPrice[0] = 17850
fVeteransLamellarBelt.itemTokenPrice = new Array();
fVeteransLamellarBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransLamellarBelt.itemStats = new Array();
fVeteransLamellarBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Lamellar Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLamellarBelt; ++i;

var fVeteransLamellarBracers = new RewardItem("alliance","Veteran's Lamellar Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransLamellarBracers.itemHonorPrice = new Array();
fVeteransLamellarBracers.itemHonorPrice[0] = 11794
fVeteransLamellarBracers.itemTokenPrice = new Array();
fVeteransLamellarBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransLamellarBracers.itemStats = new Array();
fVeteransLamellarBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Lamellar Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLamellarBracers; ++i;

var fVeteransLamellarGreaves = new RewardItem("alliance","Veteran's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransLamellarGreaves.itemHonorPrice = new Array();
fVeteransLamellarGreaves.itemHonorPrice[0] = 17850
fVeteransLamellarGreaves.itemTokenPrice = new Array();
fVeteransLamellarGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransLamellarGreaves.itemStats = new Array();
fVeteransLamellarGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Lamellar Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLamellarGreaves; ++i;

var fVeteransLeatherBelt = new RewardItem("alliance","Veteran's Leather Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransLeatherBelt.itemHonorPrice = new Array();
fVeteransLeatherBelt.itemHonorPrice[0] = 17850
fVeteransLeatherBelt.itemTokenPrice = new Array();
fVeteransLeatherBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransLeatherBelt.itemStats = new Array();
fVeteransLeatherBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Leather Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>241 Armor<br>+30 Agility<br>+45 Stamina\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLeatherBelt; ++i;

var fVeteransLeatherBoots = new RewardItem("alliance","Veteran's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransLeatherBoots.itemHonorPrice = new Array();
fVeteransLeatherBoots.itemHonorPrice[0] = 17850
fVeteransLeatherBoots.itemTokenPrice = new Array();
fVeteransLeatherBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransLeatherBoots.itemStats = new Array();
fVeteransLeatherBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Leather Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>294 Armor<br>+30 Agility<br>+45 Stamina\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLeatherBoots; ++i;

var fVeteransLeatherBracers = new RewardItem("alliance","Veteran's Leather Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransLeatherBracers.itemHonorPrice = new Array();
fVeteransLeatherBracers.itemHonorPrice[0] = 11794
fVeteransLeatherBracers.itemTokenPrice = new Array();
fVeteransLeatherBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransLeatherBracers.itemStats = new Array();
fVeteransLeatherBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Leather Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>174 Armor<br>+21 Agility<br>+29 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLeatherBracers; ++i;

var fVeteransLinkedBracers = new RewardItem("alliance","Veteran's Linked Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransLinkedBracers.itemHonorPrice = new Array();
fVeteransLinkedBracers.itemHonorPrice[0] = 11794
fVeteransLinkedBracers.itemTokenPrice = new Array();
fVeteransLinkedBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransLinkedBracers.itemStats = new Array();
fVeteransLinkedBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Linked Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>388 Armor<br>+21 Strength<br>+29 Stamina<br>+11 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLinkedBracers; ++i;

var fVeteransLinkedGirdle = new RewardItem("alliance","Veteran's Linked Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransLinkedGirdle.itemHonorPrice = new Array();
fVeteransLinkedGirdle.itemHonorPrice[0] = 17850
fVeteransLinkedGirdle.itemTokenPrice = new Array();
fVeteransLinkedGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransLinkedGirdle.itemStats = new Array();
fVeteransLinkedGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Linked Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>537 Armor<br>+31 Strength<br>+45 Stamina<br>+20 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLinkedGirdle; ++i;

var fVeteransLinkedSabatons = new RewardItem("alliance","Veteran's Linked Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransLinkedSabatons.itemHonorPrice = new Array();
fVeteransLinkedSabatons.itemHonorPrice[0] = 17850
fVeteransLinkedSabatons.itemTokenPrice = new Array();
fVeteransLinkedSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransLinkedSabatons.itemStats = new Array();
fVeteransLinkedSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Linked Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+30 Strength<br>+45 Stamina<br>+20 Intellect\
<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLinkedSabatons; ++i;

var fVeteransMailBracers = new RewardItem("alliance","Veteran's Mail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransMailBracers.itemHonorPrice = new Array();
fVeteransMailBracers.itemHonorPrice[0] = 11794
fVeteransMailBracers.itemTokenPrice = new Array();
fVeteransMailBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransMailBracers.itemStats = new Array();
fVeteransMailBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>388 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMailBracers; ++i;

var fVeteransMailGirdle = new RewardItem("alliance","Veteran's Mail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransMailGirdle.itemHonorPrice = new Array();
fVeteransMailGirdle.itemHonorPrice[0] = 17850
fVeteransMailGirdle.itemTokenPrice = new Array();
fVeteransMailGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransMailGirdle.itemStats = new Array();
fVeteransMailGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>537 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMailGirdle; ++i;

var fVeteransMailSabatons = new RewardItem("alliance","Veteran's Mail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransMailSabatons.itemHonorPrice = new Array();
fVeteransMailSabatons.itemHonorPrice[0] = 17850
fVeteransMailSabatons.itemTokenPrice = new Array();
fVeteransMailSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransMailSabatons.itemStats = new Array();
fVeteransMailSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMailSabatons; ++i;

var fVeteransPlateBelt = new RewardItem("alliance","Veteran's Plate Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransPlateBelt.itemHonorPrice = new Array();
fVeteransPlateBelt.itemHonorPrice[0] = 17850
fVeteransPlateBelt.itemTokenPrice = new Array();
fVeteransPlateBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransPlateBelt.itemStats = new Array();
fVeteransPlateBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Plate Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+31 Strength<br>+45 Stamina\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPlateBelt; ++i;

var fVeteransPlateBracers = new RewardItem("alliance","Veteran's Plate Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransPlateBracers.itemHonorPrice = new Array();
fVeteransPlateBracers.itemHonorPrice[0] = 11794
fVeteransPlateBracers.itemTokenPrice = new Array();
fVeteransPlateBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransPlateBracers.itemStats = new Array();
fVeteransPlateBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Plate Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+21 Strength<br>+30 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPlateBracers; ++i;

var fVeteransPlateGreaves = new RewardItem("alliance","Veteran's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransPlateGreaves.itemHonorPrice = new Array();
fVeteransPlateGreaves.itemHonorPrice[0] = 17850
fVeteransPlateGreaves.itemTokenPrice = new Array();
fVeteransPlateGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransPlateGreaves.itemStats = new Array();
fVeteransPlateGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Plate Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+31 Strength<br>+45 Stamina\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPlateGreaves; ++i;

var fVeteransScaledBelt = new RewardItem("alliance","Veteran's Scaled Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransScaledBelt.itemHonorPrice = new Array();
fVeteransScaledBelt.itemHonorPrice[0] = 17850
fVeteransScaledBelt.itemTokenPrice = new Array();
fVeteransScaledBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransScaledBelt.itemStats = new Array();
fVeteransScaledBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Scaled Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+27 Strength<br>+39 Stamina<br>+27 Intellect\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransScaledBelt; ++i;

var fVeteransScaledBracers = new RewardItem("alliance","Veteran's Scaled Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransScaledBracers.itemHonorPrice = new Array();
fVeteransScaledBracers.itemHonorPrice[0] = 11794
fVeteransScaledBracers.itemTokenPrice = new Array();
fVeteransScaledBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransScaledBracers.itemStats = new Array();
fVeteransScaledBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Scaled Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+19 Strength<br>+25 Stamina<br>+13 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransScaledBracers; ++i;

var fVeteransScaledGreaves = new RewardItem("alliance","Veteran's Scaled Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransScaledGreaves.itemHonorPrice = new Array();
fVeteransScaledGreaves.itemHonorPrice[0] = 17850
fVeteransScaledGreaves.itemTokenPrice = new Array();
fVeteransScaledGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransScaledGreaves.itemStats = new Array();
fVeteransScaledGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Scaled Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+27 Strength<br>+39 Stamina<br>+27 Intellect\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransScaledGreaves; ++i;

var fVeteransSilkBelt = new RewardItem("alliance","Veteran's Silk Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransSilkBelt.itemHonorPrice = new Array();
fVeteransSilkBelt.itemHonorPrice[0] = 17850
fVeteransSilkBelt.itemTokenPrice = new Array();
fVeteransSilkBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransSilkBelt.itemStats = new Array();
fVeteransSilkBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Silk Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>128 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransSilkBelt; ++i;

var fVeteransSilkCuffs = new RewardItem("alliance","Veteran's Silk Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransSilkCuffs.itemHonorPrice = new Array();
fVeteransSilkCuffs.itemHonorPrice[0] = 11794
fVeteransSilkCuffs.itemTokenPrice = new Array();
fVeteransSilkCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransSilkCuffs.itemStats = new Array();
fVeteransSilkCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Silk Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>93 Armor<br>+25 Stamina<br>+18 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransSilkCuffs; ++i;

var fVeteransSilkFootguards = new RewardItem("alliance","Veteran's Silk Footguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVeteransSilkFootguards.itemHonorPrice = new Array();
fVeteransSilkFootguards.itemHonorPrice[0] = 17850
fVeteransSilkFootguards.itemTokenPrice = new Array();
fVeteransSilkFootguards.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransSilkFootguards.itemStats = new Array();
fVeteransSilkFootguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Silk Footguards</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>157 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransSilkFootguards; ++i;

var fVeteransMoonclothBelt = new RewardItem("alliance","Veteran's Mooncloth Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransMoonclothBelt.itemHonorPrice = new Array();
fVeteransMoonclothBelt.itemHonorPrice[0] = 17850
fVeteransMoonclothBelt.itemTokenPrice = new Array();
fVeteransMoonclothBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransMoonclothBelt.itemStats = new Array();
fVeteransMoonclothBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mooncloth Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>128 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMoonclothBelt; ++i;

var fVeteransMoonclothCuffs = new RewardItem("alliance","Veteran's Mooncloth Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransMoonclothCuffs.itemHonorPrice = new Array();
fVeteransMoonclothCuffs.itemHonorPrice[0] = 11794
fVeteransMoonclothCuffs.itemTokenPrice = new Array();
fVeteransMoonclothCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransMoonclothCuffs.itemStats = new Array();
fVeteransMoonclothCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mooncloth Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>93 Armor<br>+31 Stamina<br>+16 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMoonclothCuffs; ++i;

var fVeteransMoonclothSlippers = new RewardItem("alliance","Veteran's Mooncloth Slippers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVeteransMoonclothSlippers.itemHonorPrice = new Array();
fVeteransMoonclothSlippers.itemHonorPrice[0] = 17850
fVeteransMoonclothSlippers.itemTokenPrice = new Array();
fVeteransMoonclothSlippers.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransMoonclothSlippers.itemStats = new Array();
fVeteransMoonclothSlippers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mooncloth Slippers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>157 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMoonclothSlippers; ++i;

var fVeteransWyrmhideBelt = new RewardItem("alliance","Veteran's Wyrmhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransWyrmhideBelt.itemHonorPrice = new Array();
fVeteransWyrmhideBelt.itemHonorPrice[0] = 17850
fVeteransWyrmhideBelt.itemTokenPrice = new Array();
fVeteransWyrmhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransWyrmhideBelt.itemStats = new Array();
fVeteransWyrmhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Wyrmhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransWyrmhideBelt; ++i;

var fVeteransWyrmhideBoots = new RewardItem("alliance","Veteran's Wyrmhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransWyrmhideBoots.itemHonorPrice = new Array();
fVeteransWyrmhideBoots.itemHonorPrice[0] = 17850
fVeteransWyrmhideBoots.itemTokenPrice = new Array();
fVeteransWyrmhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransWyrmhideBoots.itemStats = new Array();
fVeteransWyrmhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Wyrmhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>336 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransWyrmhideBoots; ++i;

var fVeteransWyrmhideBracers = new RewardItem("alliance","Veteran's Wyrmhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransWyrmhideBracers.itemHonorPrice = new Array();
fVeteransWyrmhideBracers.itemHonorPrice[0] = 11794
fVeteransWyrmhideBracers.itemTokenPrice = new Array();
fVeteransWyrmhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransWyrmhideBracers.itemStats = new Array();
fVeteransWyrmhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Wyrmhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>216 Armor<br>+27 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransWyrmhideBracers; ++i;

var fVeteransOrnamentedBelt = new RewardItem("alliance","Veteran's Ornamented Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransOrnamentedBelt.itemHonorPrice = new Array();
fVeteransOrnamentedBelt.itemHonorPrice[0] = 17850
fVeteransOrnamentedBelt.itemTokenPrice = new Array();
fVeteransOrnamentedBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransOrnamentedBelt.itemStats = new Array();
fVeteransOrnamentedBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ornamented Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransOrnamentedBelt; ++i;

var fVeteransOrnamentedBracers = new RewardItem("alliance","Veteran's Ornamented Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransOrnamentedBracers.itemHonorPrice = new Array();
fVeteransOrnamentedBracers.itemHonorPrice[0] = 11794
fVeteransOrnamentedBracers.itemTokenPrice = new Array();
fVeteransOrnamentedBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransOrnamentedBracers.itemStats = new Array();
fVeteransOrnamentedBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ornamented Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransOrnamentedBracers; ++i;

var fVeteransOrnamentedGreaves = new RewardItem("alliance","Veteran's Ornamented Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransOrnamentedGreaves.itemHonorPrice = new Array();
fVeteransOrnamentedGreaves.itemHonorPrice[0] = 17850
fVeteransOrnamentedGreaves.itemTokenPrice = new Array();
fVeteransOrnamentedGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransOrnamentedGreaves.itemStats = new Array();
fVeteransOrnamentedGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ornamented Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransOrnamentedGreaves; ++i;

var fVeteransRingmailBracers = new RewardItem("alliance","Veteran's Ringmail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransRingmailBracers.itemHonorPrice = new Array();
fVeteransRingmailBracers.itemHonorPrice[0] = 11794
fVeteransRingmailBracers.itemTokenPrice = new Array();
fVeteransRingmailBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransRingmailBracers.itemStats = new Array();
fVeteransRingmailBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ringmail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>388 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransRingmailBracers; ++i;

var fVeteransRingmailGirdle = new RewardItem("alliance","Veteran's Ringmail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransRingmailGirdle.itemHonorPrice = new Array();
fVeteransRingmailGirdle.itemHonorPrice[0] = 17850
fVeteransRingmailGirdle.itemTokenPrice = new Array();
fVeteransRingmailGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransRingmailGirdle.itemStats = new Array();
fVeteransRingmailGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ringmail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>537 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransRingmailGirdle; ++i;

var fVeteransRingmailSabatons = new RewardItem("alliance","Veteran's Ringmail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransRingmailSabatons.itemHonorPrice = new Array();
fVeteransRingmailSabatons.itemHonorPrice[0] = 17850
fVeteransRingmailSabatons.itemTokenPrice = new Array();
fVeteransRingmailSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransRingmailSabatons.itemStats = new Array();
fVeteransRingmailSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ringmail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransRingmailSabatons; ++i;

var fVeteransBandofDominance = new RewardItem("alliance","Veteran's Band of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVeteransBandofDominance.itemHonorPrice = new Array();
fVeteransBandofDominance.itemHonorPrice[0] = 15300
fVeteransBandofDominance.itemTokenPrice = new Array();
fVeteransBandofDominance.itemTokenPrice[0] = new Array(10,0,0,0);
fVeteransBandofDominance.itemStats = new Array();
fVeteransBandofDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Band of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Finger\
<br>+27 Stamina<br>+12 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 10.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransBandofDominance; ++i;

var fVeteransBandofSalvation = new RewardItem("alliance","Veteran's Band of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVeteransBandofSalvation.itemHonorPrice = new Array();
fVeteransBandofSalvation.itemHonorPrice[0] = 15300
fVeteransBandofSalvation.itemTokenPrice = new Array();
fVeteransBandofSalvation.itemTokenPrice[0] = new Array(10,0,0,0);
fVeteransBandofSalvation.itemStats = new Array();
fVeteransBandofSalvation.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Band of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Finger\
<br>+30 Stamina<br>+17 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransBandofSalvation; ++i;

var fVeteransBandofTriumph = new RewardItem("alliance","Veteran's Band of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVeteransBandofTriumph.itemHonorPrice = new Array();
fVeteransBandofTriumph.itemHonorPrice[0] = 15300
fVeteransBandofTriumph.itemTokenPrice = new Array();
fVeteransBandofTriumph.itemTokenPrice[0] = new Array(10,0,0,0);
fVeteransBandofTriumph.itemStats = new Array();
fVeteransBandofTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Band of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Finger\
<br>+30 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransBandofTriumph; ++i;

var fVeteransPendantofConquest = new RewardItem("alliance","Veteran's Pendant of Conquest","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofConquest.itemHonorPrice = new Array();
fVeteransPendantofConquest.itemHonorPrice[0] = 15300
fVeteransPendantofConquest.itemTokenPrice = new Array();
fVeteransPendantofConquest.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofConquest.itemStats = new Array();
fVeteransPendantofConquest.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Conquest</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+27 Stamina<br>+12 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofConquest; ++i;

var fVeteransPendantofDominance = new RewardItem("alliance","Veteran's Pendant of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofDominance.itemHonorPrice = new Array();
fVeteransPendantofDominance.itemHonorPrice[0] = 15300
fVeteransPendantofDominance.itemTokenPrice = new Array();
fVeteransPendantofDominance.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofDominance.itemStats = new Array();
fVeteransPendantofDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+31 Stamina<br>+16 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofDominance; ++i;

var fVeteransPendantofSalvation = new RewardItem("alliance","Veteran's Pendant of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofSalvation.itemHonorPrice = new Array();
fVeteransPendantofSalvation.itemHonorPrice[0] = 15300
fVeteransPendantofSalvation.itemTokenPrice = new Array();
fVeteransPendantofSalvation.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofSalvation.itemStats = new Array();
fVeteransPendantofSalvation.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+30 Stamina<br>+13 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofSalvation; ++i;

var fVeteransPendantofTriumph = new RewardItem("alliance","Veteran's Pendant of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofTriumph.itemHonorPrice = new Array();
fVeteransPendantofTriumph.itemHonorPrice[0] = 15300
fVeteransPendantofTriumph.itemTokenPrice = new Array();
fVeteransPendantofTriumph.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofTriumph.itemStats = new Array();
fVeteransPendantofTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+31 Stamina<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofTriumph; ++i;
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

var fVeteransChainBracers = new RewardItem("horde","Veteran's Chain Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransChainBracers.itemHonorPrice = new Array();
fVeteransChainBracers.itemHonorPrice[0] = 11794
fVeteransChainBracers.itemTokenPrice = new Array();
fVeteransChainBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransChainBracers.itemStats = new Array();
fVeteransChainBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Chain Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>388 Armor<br>+20 Agility<br>+29 Stamina<br>+10 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span><br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 18.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransChainBracers; ++i;

var fVeteransChainGirdle = new RewardItem("horde","Veteran's Chain Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransChainGirdle.itemHonorPrice = new Array();
fVeteransChainGirdle.itemHonorPrice[0] = 17850
fVeteransChainGirdle.itemTokenPrice = new Array();
fVeteransChainGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransChainGirdle.itemStats = new Array();
fVeteransChainGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Chain Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>537 Armor<br>+30 Agility<br>+45 Stamina<br>+20 Intellect<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransChainGirdle; ++i;

var fVeteransChainSabatons = new RewardItem("horde","Veteran's Chain Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransChainSabatons.itemHonorPrice = new Array();
fVeteransChainSabatons.itemHonorPrice[0] = 17850
fVeteransChainSabatons.itemTokenPrice = new Array();
fVeteransChainSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransChainSabatons.itemStats = new Array();
fVeteransChainSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Chain Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+30 Agility<br>+45 Stamina<br>+20 Intellect<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransChainSabatons; ++i;

var fVeteransDragonhideBelt = new RewardItem("horde","Veteran's Dragonhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransDragonhideBelt.itemHonorPrice = new Array();
fVeteransDragonhideBelt.itemHonorPrice[0] = 17850
fVeteransDragonhideBelt.itemTokenPrice = new Array();
fVeteransDragonhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransDragonhideBelt.itemStats = new Array();
fVeteransDragonhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dragonhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+27 Strength<br>+26 Agility<br>+39 Stamina<br>+17 Intellect\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDragonhideBelt; ++i;

var fVeteransDragonhideBoots = new RewardItem("horde","Veteran's Dragonhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransDragonhideBoots.itemHonorPrice = new Array();
fVeteransDragonhideBoots.itemHonorPrice[0] = 17850
fVeteransDragonhideBoots.itemTokenPrice = new Array();
fVeteransDragonhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransDragonhideBoots.itemStats = new Array();
fVeteransDragonhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dragonhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>336 Armor<br>+27 Strength<br>+26 Agility<br>+39 Stamina<br>+17 Intellect\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDragonhideBoots; ++i;

var fVeteransDragonhideBracers = new RewardItem("horde","Veteran's Dragonhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransDragonhideBracers.itemHonorPrice = new Array();
fVeteransDragonhideBracers.itemHonorPrice[0] = 11794
fVeteransDragonhideBracers.itemTokenPrice = new Array();
fVeteransDragonhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransDragonhideBracers.itemStats = new Array();
fVeteransDragonhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dragonhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>216 Armor<br>+19 Strength<br>+18 Agility<br>+25 Stamina<br><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDragonhideBracers; ++i;

var fVeteransDreadweaveBelt = new RewardItem("horde","Veteran's Dreadweave Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransDreadweaveBelt.itemHonorPrice = new Array();
fVeteransDreadweaveBelt.itemHonorPrice[0] = 17850
fVeteransDreadweaveBelt.itemTokenPrice = new Array();
fVeteransDreadweaveBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransDreadweaveBelt.itemStats = new Array();
fVeteransDreadweaveBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dreadweave Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>128 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDreadweaveBelt; ++i;

var fVeteransDreadweaveCuffs = new RewardItem("horde","Veteran's Dreadweave Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransDreadweaveCuffs.itemHonorPrice = new Array();
fVeteransDreadweaveCuffs.itemHonorPrice[0] = 11794
fVeteransDreadweaveCuffs.itemTokenPrice = new Array();
fVeteransDreadweaveCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransDreadweaveCuffs.itemStats = new Array();
fVeteransDreadweaveCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dreadweave Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>93 Armor<br>+31 Stamina<br>+16 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDreadweaveCuffs; ++i;

var fVeteransDreadweaveStalkers = new RewardItem("horde","Veteran's Dreadweave Stalkers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVeteransDreadweaveStalkers.itemHonorPrice = new Array();
fVeteransDreadweaveStalkers.itemHonorPrice[0] = 17850
fVeteransDreadweaveStalkers.itemTokenPrice = new Array();
fVeteransDreadweaveStalkers.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransDreadweaveStalkers.itemStats = new Array();
fVeteransDreadweaveStalkers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Dreadweave Stalkers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>157 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransDreadweaveStalkers; ++i;

var fVeteransKodohideBelt = new RewardItem("horde","Veteran's Kodohide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransKodohideBelt.itemHonorPrice = new Array();
fVeteransKodohideBelt.itemHonorPrice[0] = 17850
fVeteransKodohideBelt.itemTokenPrice = new Array();
fVeteransKodohideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransKodohideBelt.itemStats = new Array();
fVeteransKodohideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Kodohide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransKodohideBelt; ++i;

var fVeteransKodohideBoots = new RewardItem("horde","Veteran's Kodohide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransKodohideBoots.itemHonorPrice = new Array();
fVeteransKodohideBoots.itemHonorPrice[0] = 17850
fVeteransKodohideBoots.itemTokenPrice = new Array();
fVeteransKodohideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransKodohideBoots.itemStats = new Array();
fVeteransKodohideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Kodohide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>336 Armor<br>+39 Stamina<br>+26 Intellect\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 70.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransKodohideBoots; ++i;

var fVeteransKodohideBracers = new RewardItem("horde","Veteran's Kodohide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransKodohideBracers.itemHonorPrice = new Array();
fVeteransKodohideBracers.itemHonorPrice[0] = 11794
fVeteransKodohideBracers.itemTokenPrice = new Array();
fVeteransKodohideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransKodohideBracers.itemStats = new Array();
fVeteransKodohideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Kodohide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>216 Armor<br>+25 Stamina<br>+18 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransKodohideBracers; ++i;

var fVeteransLamellarBelt = new RewardItem("horde","Veteran's Lamellar Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransLamellarBelt.itemHonorPrice = new Array();
fVeteransLamellarBelt.itemHonorPrice[0] = 17850
fVeteransLamellarBelt.itemTokenPrice = new Array();
fVeteransLamellarBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransLamellarBelt.itemStats = new Array();
fVeteransLamellarBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Lamellar Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLamellarBelt; ++i;

var fVeteransLamellarBracers = new RewardItem("horde","Veteran's Lamellar Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransLamellarBracers.itemHonorPrice = new Array();
fVeteransLamellarBracers.itemHonorPrice[0] = 11794
fVeteransLamellarBracers.itemTokenPrice = new Array();
fVeteransLamellarBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransLamellarBracers.itemStats = new Array();
fVeteransLamellarBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Lamellar Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLamellarBracers; ++i;

var fVeteransLamellarGreaves = new RewardItem("horde","Veteran's Lamellar Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransLamellarGreaves.itemHonorPrice = new Array();
fVeteransLamellarGreaves.itemHonorPrice[0] = 17850
fVeteransLamellarGreaves.itemTokenPrice = new Array();
fVeteransLamellarGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransLamellarGreaves.itemStats = new Array();
fVeteransLamellarGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Lamellar Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLamellarGreaves; ++i;

var fVeteransLeatherBelt = new RewardItem("horde","Veteran's Leather Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransLeatherBelt.itemHonorPrice = new Array();
fVeteransLeatherBelt.itemHonorPrice[0] = 17850
fVeteransLeatherBelt.itemTokenPrice = new Array();
fVeteransLeatherBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransLeatherBelt.itemStats = new Array();
fVeteransLeatherBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Leather Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>241 Armor<br>+30 Agility<br>+45 Stamina\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLeatherBelt; ++i;

var fVeteransLeatherBoots = new RewardItem("horde","Veteran's Leather Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransLeatherBoots.itemHonorPrice = new Array();
fVeteransLeatherBoots.itemHonorPrice[0] = 17850
fVeteransLeatherBoots.itemTokenPrice = new Array();
fVeteransLeatherBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransLeatherBoots.itemStats = new Array();
fVeteransLeatherBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Leather Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>294 Armor<br>+30 Agility<br>+45 Stamina\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLeatherBoots; ++i;

var fVeteransLeatherBracers = new RewardItem("horde","Veteran's Leather Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransLeatherBracers.itemHonorPrice = new Array();
fVeteransLeatherBracers.itemHonorPrice[0] = 11794
fVeteransLeatherBracers.itemTokenPrice = new Array();
fVeteransLeatherBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransLeatherBracers.itemStats = new Array();
fVeteransLeatherBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Leather Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>174 Armor<br>+21 Agility<br>+29 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLeatherBracers; ++i;

var fVeteransLinkedBracers = new RewardItem("horde","Veteran's Linked Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransLinkedBracers.itemHonorPrice = new Array();
fVeteransLinkedBracers.itemHonorPrice[0] = 11794
fVeteransLinkedBracers.itemTokenPrice = new Array();
fVeteransLinkedBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransLinkedBracers.itemStats = new Array();
fVeteransLinkedBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Linked Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>388 Armor<br>+21 Strength<br>+29 Stamina<br>+11 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLinkedBracers; ++i;

var fVeteransLinkedGirdle = new RewardItem("horde","Veteran's Linked Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransLinkedGirdle.itemHonorPrice = new Array();
fVeteransLinkedGirdle.itemHonorPrice[0] = 17850
fVeteransLinkedGirdle.itemTokenPrice = new Array();
fVeteransLinkedGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransLinkedGirdle.itemStats = new Array();
fVeteransLinkedGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Linked Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>537 Armor<br>+31 Strength<br>+45 Stamina<br>+20 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLinkedGirdle; ++i;

var fVeteransLinkedSabatons = new RewardItem("horde","Veteran's Linked Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransLinkedSabatons.itemHonorPrice = new Array();
fVeteransLinkedSabatons.itemHonorPrice[0] = 17850
fVeteransLinkedSabatons.itemTokenPrice = new Array();
fVeteransLinkedSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransLinkedSabatons.itemStats = new Array();
fVeteransLinkedSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Linked Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+30 Strength<br>+45 Stamina<br>+20 Intellect\
<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransLinkedSabatons; ++i;

var fVeteransMailBracers = new RewardItem("horde","Veteran's Mail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransMailBracers.itemHonorPrice = new Array();
fVeteransMailBracers.itemHonorPrice[0] = 11794
fVeteransMailBracers.itemTokenPrice = new Array();
fVeteransMailBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransMailBracers.itemStats = new Array();
fVeteransMailBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>388 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMailBracers; ++i;

var fVeteransMailGirdle = new RewardItem("horde","Veteran's Mail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransMailGirdle.itemHonorPrice = new Array();
fVeteransMailGirdle.itemHonorPrice[0] = 17850
fVeteransMailGirdle.itemTokenPrice = new Array();
fVeteransMailGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransMailGirdle.itemStats = new Array();
fVeteransMailGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>537 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMailGirdle; ++i;

var fVeteransMailSabatons = new RewardItem("horde","Veteran's Mail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransMailSabatons.itemHonorPrice = new Array();
fVeteransMailSabatons.itemHonorPrice[0] = 17850
fVeteransMailSabatons.itemTokenPrice = new Array();
fVeteransMailSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransMailSabatons.itemStats = new Array();
fVeteransMailSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMailSabatons; ++i;

var fVeteransPlateBelt = new RewardItem("horde","Veteran's Plate Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransPlateBelt.itemHonorPrice = new Array();
fVeteransPlateBelt.itemHonorPrice[0] = 17850
fVeteransPlateBelt.itemTokenPrice = new Array();
fVeteransPlateBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransPlateBelt.itemStats = new Array();
fVeteransPlateBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Plate Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+31 Strength<br>+45 Stamina\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPlateBelt; ++i;

var fVeteransPlateBracers = new RewardItem("horde","Veteran's Plate Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransPlateBracers.itemHonorPrice = new Array();
fVeteransPlateBracers.itemHonorPrice[0] = 11794
fVeteransPlateBracers.itemTokenPrice = new Array();
fVeteransPlateBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransPlateBracers.itemStats = new Array();
fVeteransPlateBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Plate Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+21 Strength<br>+30 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPlateBracers; ++i;

var fVeteransPlateGreaves = new RewardItem("horde","Veteran's Plate Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransPlateGreaves.itemHonorPrice = new Array();
fVeteransPlateGreaves.itemHonorPrice[0] = 17850
fVeteransPlateGreaves.itemTokenPrice = new Array();
fVeteransPlateGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransPlateGreaves.itemStats = new Array();
fVeteransPlateGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Plate Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+31 Strength<br>+45 Stamina\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPlateGreaves; ++i;

var fVeteransScaledBelt = new RewardItem("horde","Veteran's Scaled Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransScaledBelt.itemHonorPrice = new Array();
fVeteransScaledBelt.itemHonorPrice[0] = 17850
fVeteransScaledBelt.itemTokenPrice = new Array();
fVeteransScaledBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransScaledBelt.itemStats = new Array();
fVeteransScaledBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Scaled Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+28 Strength<br>+39 Stamina<br>+26 Intellect\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransScaledBelt; ++i;

var fVeteransScaledBracers = new RewardItem("horde","Veteran's Scaled Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransScaledBracers.itemHonorPrice = new Array();
fVeteransScaledBracers.itemHonorPrice[0] = 11794
fVeteransScaledBracers.itemTokenPrice = new Array();
fVeteransScaledBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransScaledBracers.itemStats = new Array();
fVeteransScaledBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Scaled Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+19 Strength<br>+25 Stamina<br>+13 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransScaledBracers; ++i;

var fVeteransScaledGreaves = new RewardItem("horde","Veteran's Scaled Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransScaledGreaves.itemHonorPrice = new Array();
fVeteransScaledGreaves.itemHonorPrice[0] = 17850
fVeteransScaledGreaves.itemTokenPrice = new Array();
fVeteransScaledGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransScaledGreaves.itemStats = new Array();
fVeteransScaledGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Scaled Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+27 Strength<br>+39 Stamina<br>+26 Intellect\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransScaledGreaves; ++i;

var fVeteransSilkBelt = new RewardItem("horde","Veteran's Silk Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransSilkBelt.itemHonorPrice = new Array();
fVeteransSilkBelt.itemHonorPrice[0] = 17850
fVeteransSilkBelt.itemTokenPrice = new Array();
fVeteransSilkBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransSilkBelt.itemStats = new Array();
fVeteransSilkBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Silk Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>128 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransSilkBelt; ++i;

var fVeteransSilkCuffs = new RewardItem("horde","Veteran's Silk Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransSilkCuffs.itemHonorPrice = new Array();
fVeteransSilkCuffs.itemHonorPrice[0] = 11794
fVeteransSilkCuffs.itemTokenPrice = new Array();
fVeteransSilkCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransSilkCuffs.itemStats = new Array();
fVeteransSilkCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Silk Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>93 Armor<br>+25 Stamina<br>+18 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransSilkCuffs; ++i;

var fVeteransSilkFootguards = new RewardItem("horde","Veteran's Silk Footguards","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVeteransSilkFootguards.itemHonorPrice = new Array();
fVeteransSilkFootguards.itemHonorPrice[0] = 17850
fVeteransSilkFootguards.itemTokenPrice = new Array();
fVeteransSilkFootguards.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransSilkFootguards.itemStats = new Array();
fVeteransSilkFootguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Silk Footguards</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>157 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransSilkFootguards; ++i;

var fVeteransMoonclothBelt = new RewardItem("horde","Veteran's Mooncloth Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransMoonclothBelt.itemHonorPrice = new Array();
fVeteransMoonclothBelt.itemHonorPrice[0] = 17850
fVeteransMoonclothBelt.itemTokenPrice = new Array();
fVeteransMoonclothBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransMoonclothBelt.itemStats = new Array();
fVeteransMoonclothBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mooncloth Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>128 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMoonclothBelt; ++i;

var fVeteransMoonclothCuffs = new RewardItem("horde","Veteran's Mooncloth Cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransMoonclothCuffs.itemHonorPrice = new Array();
fVeteransMoonclothCuffs.itemHonorPrice[0] = 11794
fVeteransMoonclothCuffs.itemTokenPrice = new Array();
fVeteransMoonclothCuffs.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransMoonclothCuffs.itemStats = new Array();
fVeteransMoonclothCuffs.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mooncloth Cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>93 Armor<br>+31 Stamina<br>+16 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35/35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMoonclothCuffs; ++i;

var fVeteransMoonclothSlippers = new RewardItem("horde","Veteran's Mooncloth Slippers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_05.gif");
fVeteransMoonclothSlippers.itemHonorPrice = new Array();
fVeteransMoonclothSlippers.itemHonorPrice[0] = 17850
fVeteransMoonclothSlippers.itemTokenPrice = new Array();
fVeteransMoonclothSlippers.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransMoonclothSlippers.itemStats = new Array();
fVeteransMoonclothSlippers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Mooncloth Slippers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>157 Armor<br>+45 Stamina<br>+30 Intellect\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 31.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 68.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransMoonclothSlippers; ++i;

var fVeteransWyrmhideBelt = new RewardItem("horde","Veteran's Wyrmhide Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fVeteransWyrmhideBelt.itemHonorPrice = new Array();
fVeteransWyrmhideBelt.itemHonorPrice[0] = 17850
fVeteransWyrmhideBelt.itemTokenPrice = new Array();
fVeteransWyrmhideBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransWyrmhideBelt.itemStats = new Array();
fVeteransWyrmhideBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Wyrmhide Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 40/40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransWyrmhideBelt; ++i;

var fVeteransWyrmhideBoots = new RewardItem("horde","Veteran's Wyrmhide Boots","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_08.gif");
fVeteransWyrmhideBoots.itemHonorPrice = new Array();
fVeteransWyrmhideBoots.itemHonorPrice[0] = 17850
fVeteransWyrmhideBoots.itemTokenPrice = new Array();
fVeteransWyrmhideBoots.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransWyrmhideBoots.itemStats = new Array();
fVeteransWyrmhideBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Wyrmhide Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>336 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 60/60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 36.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransWyrmhideBoots; ++i;

var fVeteransWyrmhideBracers = new RewardItem("horde","Veteran's Wyrmhide Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fVeteransWyrmhideBracers.itemHonorPrice = new Array();
fVeteransWyrmhideBracers.itemHonorPrice[0] = 11794
fVeteransWyrmhideBracers.itemTokenPrice = new Array();
fVeteransWyrmhideBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransWyrmhideBracers.itemStats = new Array();
fVeteransWyrmhideBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Wyrmhide Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>216 Armor<br>+27 Stamina<br>+16 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransWyrmhideBracers; ++i;

var fVeteransOrnamentedBelt = new RewardItem("horde","Veteran's Ornamented Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fVeteransOrnamentedBelt.itemHonorPrice = new Array();
fVeteransOrnamentedBelt.itemHonorPrice[0] = 17850
fVeteransOrnamentedBelt.itemTokenPrice = new Array();
fVeteransOrnamentedBelt.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransOrnamentedBelt.itemStats = new Array();
fVeteransOrnamentedBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ornamented Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>959 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransOrnamentedBelt; ++i;

var fVeteransOrnamentedBracers = new RewardItem("horde","Veteran's Ornamented Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fVeteransOrnamentedBracers.itemHonorPrice = new Array();
fVeteransOrnamentedBracers.itemHonorPrice[0] = 11794
fVeteransOrnamentedBracers.itemTokenPrice = new Array();
fVeteransOrnamentedBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransOrnamentedBracers.itemStats = new Array();
fVeteransOrnamentedBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ornamented Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>693 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 55/55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransOrnamentedBracers; ++i;

var fVeteransOrnamentedGreaves = new RewardItem("horde","Veteran's Ornamented Greaves","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_04.gif");
fVeteransOrnamentedGreaves.itemHonorPrice = new Array();
fVeteransOrnamentedGreaves.itemHonorPrice[0] = 17850
fVeteransOrnamentedGreaves.itemTokenPrice = new Array();
fVeteransOrnamentedGreaves.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransOrnamentedGreaves.itemStats = new Array();
fVeteransOrnamentedGreaves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ornamented Greaves</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1172 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 75/75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransOrnamentedGreaves; ++i;

var fVeteransRingmailBracers = new RewardItem("horde","Veteran's Ringmail Bracers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_16.gif");
fVeteransRingmailBracers.itemHonorPrice = new Array();
fVeteransRingmailBracers.itemHonorPrice[0] = 11794
fVeteransRingmailBracers.itemTokenPrice = new Array();
fVeteransRingmailBracers.itemTokenPrice[0] = new Array(0,0,0,20);
fVeteransRingmailBracers.itemStats = new Array();
fVeteransRingmailBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ringmail Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>388 Armor<br>+25 Stamina<br>+14 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransRingmailBracers; ++i;

var fVeteransRingmailGirdle = new RewardItem("horde","Veteran's Ringmail Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fVeteransRingmailGirdle.itemHonorPrice = new Array();
fVeteransRingmailGirdle.itemHonorPrice[0] = 17850
fVeteransRingmailGirdle.itemTokenPrice = new Array();
fVeteransRingmailGirdle.itemTokenPrice[0] = new Array(0,40,0,0);
fVeteransRingmailGirdle.itemStats = new Array();
fVeteransRingmailGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ringmail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>537 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 50/50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransRingmailGirdle; ++i;

var fVeteransRingmailSabatons = new RewardItem("horde","Veteran's Ringmail Sabatons","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Plate_06.gif");
fVeteransRingmailSabatons.itemHonorPrice = new Array();
fVeteransRingmailSabatons.itemHonorPrice[0] = 17850
fVeteransRingmailSabatons.itemTokenPrice = new Array();
fVeteransRingmailSabatons.itemTokenPrice[0] = new Array(0,0,40,0);
fVeteransRingmailSabatons.itemStats = new Array();
fVeteransRingmailSabatons.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Ringmail Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>656 Armor<br>+39 Stamina<br>+27 Intellect\
<br>Durability 70/70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransRingmailSabatons; ++i;

var fVeteransBandofDominance = new RewardItem("horde","Veteran's Band of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVeteransBandofDominance.itemHonorPrice = new Array();
fVeteransBandofDominance.itemHonorPrice[0] = 15300
fVeteransBandofDominance.itemTokenPrice = new Array();
fVeteransBandofDominance.itemTokenPrice[0] = new Array(10,0,0,0);
fVeteransBandofDominance.itemStats = new Array();
fVeteransBandofDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Band of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Finger\
<br>+27 Stamina<br>+12 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 10.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransBandofDominance; ++i;

var fVeteransBandofSalvation = new RewardItem("horde","Veteran's Band of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVeteransBandofSalvation.itemHonorPrice = new Array();
fVeteransBandofSalvation.itemHonorPrice[0] = 15300
fVeteransBandofSalvation.itemTokenPrice = new Array();
fVeteransBandofSalvation.itemTokenPrice[0] = new Array(10,0,0,0);
fVeteransBandofSalvation.itemStats = new Array();
fVeteransBandofSalvation.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Band of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Finger\
<br>+30 Stamina<br>+17 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransBandofSalvation; ++i;

var fVeteransBandofTriumph = new RewardItem("horde","Veteran's Band of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fVeteransBandofTriumph.itemHonorPrice = new Array();
fVeteransBandofTriumph.itemHonorPrice[0] = 15300
fVeteransBandofTriumph.itemTokenPrice = new Array();
fVeteransBandofTriumph.itemTokenPrice[0] = new Array(10,0,0,0);
fVeteransBandofTriumph.itemStats = new Array();
fVeteransBandofTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Band of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Finger\
<br>+30 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransBandofTriumph; ++i;

var fVeteransPendantofConquest = new RewardItem("horde","Veteran's Pendant of Conquest","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofConquest.itemHonorPrice = new Array();
fVeteransPendantofConquest.itemHonorPrice[0] = 15300
fVeteransPendantofConquest.itemTokenPrice = new Array();
fVeteransPendantofConquest.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofConquest.itemStats = new Array();
fVeteransPendantofConquest.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Conquest</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+27 Stamina<br>+12 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofConquest; ++i;

var fVeteransPendantofDominance = new RewardItem("horde","Veteran's Pendant of Dominance","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofDominance.itemHonorPrice = new Array();
fVeteransPendantofDominance.itemHonorPrice[0] = 15300
fVeteransPendantofDominance.itemTokenPrice = new Array();
fVeteransPendantofDominance.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofDominance.itemStats = new Array();
fVeteransPendantofDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+31 Stamina<br>+16 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofDominance; ++i;

var fVeteransPendantofSalvation = new RewardItem("horde","Veteran's Pendant of Salvation","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofSalvation.itemHonorPrice = new Array();
fVeteransPendantofSalvation.itemHonorPrice[0] = 15300
fVeteransPendantofSalvation.itemTokenPrice = new Array();
fVeteransPendantofSalvation.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofSalvation.itemStats = new Array();
fVeteransPendantofSalvation.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Salvation</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+30 Stamina<br>+13 Intellect<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofSalvation; ++i;

var fVeteransPendantofTriumph = new RewardItem("horde","Veteran's Pendant of Triumph","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fVeteransPendantofTriumph.itemHonorPrice = new Array();
fVeteransPendantofTriumph.itemHonorPrice[0] = 15300
fVeteransPendantofTriumph.itemTokenPrice = new Array();
fVeteransPendantofTriumph.itemTokenPrice[0] = new Array(0,0,10,0);
fVeteransPendantofTriumph.itemStats = new Array();
fVeteransPendantofTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Veteran's Pendant of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Neck\
<br>+31 Stamina<br><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Stamina</span><br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVeteransPendantofTriumph; ++i;
//------END REWARDS DEFINITION------
