/* --------- Faction Lore ------------- */
loreTexts["alliance"] ="<h3>The Bone Wastes</h3>\
The PvP objectives in Terokkar Forest are centered around five towers in the Bone Wastes, the blasted area around Auchindoun. The faction that is able to successfully control all 5 towers will be granted a zonewide buff called \"Blessing of Auchindoun\", which increases XP gain by +5%, damage by 5%, and allows for the capturing of Spirit Shards within Auchindoun. Spirit Shards are a 100% drop off of boss monsters within the 4 wings of Auchindoun, and each player can loot their own shard from the boss. These shards can be turned in at Spirit Sage NPCs in Allerian Stronghold and Stonebreaker Hold for PvP based rewards, including Meta Gems.\
<br /><br />\
Learn more about the PvP capture process <a href='/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/index.xml.html#terokkar'>here</a>.";

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

tokenIcons = new Array("bonewastes","arathi","nether","warsong");
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
		if (goldPart > 0) outPutString += goldPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/gold.gif'>&nbsp;";
		if (silverPart > 0) outPutString += silverPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/silver.gif'>&nbsp;";
		if (copperPart > 0) outPutString += copperPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/copper.gif'>&nbsp;";
	}
	if(thisObject.itemHonorPrice && thisObject.itemHonorPrice[thisBracket])
	{
		outPutString += thisObject.itemHonorPrice[thisBracket]+"<img src='/info/basics/factions/images/icons/"+thisObject.playerFaction+"-honor.gif'>&nbsp;";
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

var fBandOfTheExorcist = new RewardItem("alliance","Band of the Exorcist","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fBandOfTheExorcist.itemTokenPrice = new Array();
fBandOfTheExorcist.itemTokenPrice[0] = new Array(50,0,0,0);
fBandOfTheExorcist.itemStats = new Array();
fBandOfTheExorcist.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of the Exorcist</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>Requires Level 67<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheExorcist; ++i;


var fSealOfTheExorcist = new RewardItem("alliance","Seal of the Exorcist","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fSealOfTheExorcist.itemTokenPrice = new Array();
fSealOfTheExorcist.itemTokenPrice[0] = new Array(50,0,0,0);
fSealOfTheExorcist.itemStats = new Array();
fSealOfTheExorcist.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Seal of the Exorcist</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>Requires Level 67<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSealOfTheExorcist; ++i;


var fExorcistsPlateHelm = new RewardItem("alliance","Exorcist's Plate Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fExorcistsPlateHelm.itemTokenPrice = new Array();
fExorcistsPlateHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsPlateHelm.itemStats = new Array();
fExorcistsPlateHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Plate Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>827 Armor<br>+25 Strength<br>+30 Stamina<br>Durability 80 / 80<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Strength</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsPlateHelm; ++i;

var fExorcistsLamellarHelm = new RewardItem("alliance","Exorcist's Lamellar Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fExorcistsLamellarHelm.itemTokenPrice = new Array();
fExorcistsLamellarHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsLamellarHelm.itemStats = new Array();
fExorcistsLamellarHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Lamellar Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>827 Armor<br>+30 Stamina<br>+16 Intellect<br>Durability 80 / 80<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Spell Critical Rating</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsLamellarHelm; ++i;

var fExorcistsScaledHelm = new RewardItem("alliance","Exorcist's Scaled Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_22.gif");
fExorcistsScaledHelm.itemTokenPrice = new Array();
fExorcistsScaledHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsScaledHelm.itemStats = new Array();
fExorcistsScaledHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Scaled Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>827 Armor<br>+20 Strength<br>+30 Stamina<br>+15 Intellect<br>Durability 80 / 80<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Strength</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsScaledHelm; ++i;


var fExorcistsChainHelm = new RewardItem("alliance","Exorcist's Chain Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fExorcistsChainHelm.itemTokenPrice = new Array();
fExorcistsChainHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsChainHelm.itemStats = new Array();
fExorcistsChainHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Chain Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>463 Armor<br>+20 Agility<br>+35 Stamina<br>+15 Intellect<br>Durability 70 / 70<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Agility</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsChainHelm; ++i;

var fExorcistsLinkedHelm = new RewardItem("alliance","Exorcist's Linked Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fExorcistsLinkedHelm.itemTokenPrice = new Array();
fExorcistsLinkedHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsLinkedHelm.itemStats = new Array();
fExorcistsLinkedHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Linked Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>463 Armor<br>+24 Strength<br>+30 Stamina<br>+13 Intellect<br>Durability 70 / 70<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Critical Strike Rating</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsLinkedHelm; ++i;

var fExorcistsMailHelm = new RewardItem("alliance","Exorcist's Mail Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_09.gif");
fExorcistsMailHelm.itemTokenPrice = new Array();
fExorcistsMailHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsMailHelm.itemStats = new Array();
fExorcistsMailHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Mail Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>463 Armor<br>+30 Stamina<br>+16 Intellect<br>Durability 70 / 70<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Spell Critical Strike Rating</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsMailHelm; ++i;


var fExorcistsLeatherHelm = new RewardItem("alliance","Exorcist's Leather Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fExorcistsLeatherHelm.itemTokenPrice = new Array();
fExorcistsLeatherHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsLeatherHelm.itemStats = new Array();
fExorcistsLeatherHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Leather Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>208 Armor<br>+27 Agility<br>+33 Stamina<br>Durability 60 / 60<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +4 Attack Power</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsLeatherHelm; ++i;

var fExorcistsDragonhideHelm = new RewardItem("alliance","Exorcist's Dragonhide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fExorcistsDragonhideHelm.itemTokenPrice = new Array();
fExorcistsDragonhideHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsDragonhideHelm.itemStats = new Array();
fExorcistsDragonhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Dragonhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>248 Armor<br>+23 Strength<br>+17 Agility<br>+30 Stamina<br>Durability 60 / 60<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +4 Attack Power</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 37.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsDragonhideHelm; ++i;

var fExorcistsWyrmhideHelm = new RewardItem("alliance","Exorcist's Wyrmhide Helm","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fExorcistsWyrmhideHelm.itemTokenPrice = new Array();
fExorcistsWyrmhideHelm.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsWyrmhideHelm.itemStats = new Array();
fExorcistsWyrmhideHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Wyrmhide Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>248 Armor<br>+35 Stamina<br>+16 Intellect<br>Durability 60 / 60<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Healing and Spell Damage</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsWyrmhideHelm; ++i;


var fExorcistsSilkHood = new RewardItem("alliance","Exorcist's Silk Hood","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fExorcistsSilkHood.itemTokenPrice = new Array();
fExorcistsSilkHood.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsSilkHood.itemStats = new Array();
fExorcistsSilkHood.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Silk Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>111 Armor<br>+34 Stamina<br>+14 Intellect<br>Durability 50 / 50<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Spell Hit Rating</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsSilkHood; ++i;

var fExorcistsDreadweaveHood = new RewardItem("alliance","Exorcist's Dreadweave Hood","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
fExorcistsDreadweaveHood.itemTokenPrice = new Array();
fExorcistsDreadweaveHood.itemTokenPrice[0] = new Array(18,0,0,0);
fExorcistsDreadweaveHood.itemStats = new Array();
fExorcistsDreadweaveHood.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Exorcist's Dreadweave Hood</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Cloth</span>\
<br>111 Armor<br>+34 Stamina<br>+25 Intellect<br>Durability 50 / 50<br>\
<span class='myMetaGem'>Meta Socket</span>\
<span class='myGray'>Socket Bonus: +2 Spell Hit Rating</span><br>\
Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExorcistsDreadweaveHood; ++i;


var fSwiftWindfireDiamond = new RewardItem("alliance","Swift Windfire Diamond","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_gem_diamond_07.jpg");
fSwiftWindfireDiamond.itemTokenPrice = new Array();
fSwiftWindfireDiamond.itemTokenPrice[0] = new Array(8,0,0,0);
fSwiftWindfireDiamond.itemStats = new Array();
fSwiftWindfireDiamond.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Swift Windfire Diamond</span>\
<br>Binds when picked up<br>Unique<br>+20 Attack Power and Minor Run Speed Increase<br>\
Requires at least 2 Yellow gems<br>\
Requires at least 1 Red gem<br>\
<span class=\"myYellow\">\"Only fits in a meta gem slot.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSwiftWindfireDiamond; ++i;


var fSwiftStarfireDiamond = new RewardItem("alliance","Swift Starfire Diamond","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_gem_diamond_07.jpg");
fSwiftStarfireDiamond.itemTokenPrice = new Array();
fSwiftStarfireDiamond.itemTokenPrice[0] = new Array(8,0,0,0);
fSwiftStarfireDiamond.itemStats = new Array();
fSwiftStarfireDiamond.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Swift Starfire Diamond</span>\
<br>Binds when picked up<br>Unique<br>+12 Spell Damage and Minor Run Speed Increase<br>\
Requires at least 2 Yellow gems<br>\
Requires at least 1 Red gem<br>\
<span class=\"myYellow\">\"Only fits in a meta gem slot.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSwiftStarfireDiamond; ++i;



//-------------------------------------------------------------------
//---Horde below









//------END REWARDS DEFINITION------
