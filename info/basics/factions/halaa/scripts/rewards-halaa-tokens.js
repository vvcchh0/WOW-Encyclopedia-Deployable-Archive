
loreTexts["alliance"] = "<h3>Halaa Tokens</h3>\
There are two types of tokens required to purchase Halaa PvP rewards: Halaa Battle Tokens and Halaa Research \
Tokens. Players can earn Halaa Battle Tokens by defeating players of the opposite faction in the vicinity of \
the town of Halaa. You will earn a token for each enemy player you defeat. \
<br/><br/>\
Halaa Research Tokens can be earned by turning in 20 Oshu'gun Crystal Powder to your faction�s researcher NPC \
in Halaa. The crystal powder is found as a common drop from monsters in Nagrand. The researcher NPC will only \
be available to the side who currently controls Halaa. Check our <a href='/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/index.xml.html'>\
Outland World PvP Guide</a> for more information.";
/*
Halaa Tokens

There are two types of tokens required to purchase Halaa PvP rewards: Halaa Battle Tokens and Halaa Research Tokens. Players can earn Halaa Battle Tokens by defeating players of the opposite faction in the vicinity of the town of Halaa. You will earn a token for each enemy player you defeat. 

Halaa Research Tokens can be earned by turning in 20 Oshu�gun Crystal Powder to your faction�s researcher NPC in Halaa. The crystal powder is found as a common drop from monsters in Nagrand. The researcher NPC will only be available to the side who currently controls Halaa. Check our <a href>Outland World PvP Guide</a> for more information.
*/

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

tokenIcons = new Array("battletoken","researchtoken","nether","warsong");
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

var fAvengersWaistguard = new RewardItem("alliance","Avenger's Waistguard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fAvengersWaistguard.itemTokenPrice = new Array();
fAvengersWaistguard.itemTokenPrice[0] = new Array(20,1,0,0);
fAvengersWaistguard.itemStats = new Array();
fAvengersWaistguard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Avenger's Waistguard</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>573 Armor<br>+16 Strength<br>+24 Stamina<br>+11 Intellect<br>Durability 45 / 45<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAvengersWaistguard; ++i;


var fAvengersLegguards = new RewardItem("alliance","Avenger's Legguards","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fhalaa%2Fscripts%2Frewards-halaa-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Plate_15.gif&reason=external-or-uncollected-resource");
fAvengersLegguards.itemTokenPrice = new Array();
fAvengersLegguards.itemTokenPrice[0] = new Array(40,2,0,0);
fAvengersLegguards.itemStats = new Array();
fAvengersLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Avenger's Legguards</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Plate</span>\
<br>891 Armor<br>+22 Strength<br>+33 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 100 / 100<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAvengersLegguards; ++i;

var fMarksmansBelt = new RewardItem("alliance","Marksman's Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fMarksmansBelt.itemTokenPrice = new Array();
fMarksmansBelt.itemTokenPrice[0] = new Array(20,1,0,0);
fMarksmansBelt.itemStats = new Array();
fMarksmansBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Marksman's Belt</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>321 Armor<br>+19 Agility<br>+28 Stamina<br>+12 Intellect<br>Durability 40 / 40<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarksmansBelt; ++i;

var fMarksmansLegguards = new RewardItem("alliance","Marksman's Legguards","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fhalaa%2Fscripts%2Frewards-halaa-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Mail_04.gif&reason=external-or-uncollected-resource");
fMarksmansLegguards.itemTokenPrice = new Array();
fMarksmansLegguards.itemTokenPrice[0] = new Array(40,2,0,0);
fMarksmansLegguards.itemStats = new Array();
fMarksmansLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Marksman's Legguards</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Mail</span>\
<br>499 Armor<br>+25 Agility<br>+39 Stamina<br>+13 Intellect<span class='myYellowGem'>Yellow Socket</span>\<span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 90 / 90<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarksmansLegguards; ++i;

var fHierophantsSash = new RewardItem("alliance","Hierophant's Sash","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fHierophantsSash.itemTokenPrice = new Array();
fHierophantsSash.itemTokenPrice[0] = new Array(20,1,0,0);
fHierophantsSash.itemStats = new Array();
fHierophantsSash.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Hierophant's Sash</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Cloth</span>\
<br>77 Armor<br>+28 Stamina<br>+19 Intellect<br>Durability 30 / 30<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHierophantsSash; ++i;

var fHierophantsLeggings = new RewardItem("alliance","Hierophant's Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_Cloth_05.gif");
fHierophantsLeggings.itemTokenPrice = new Array();
fHierophantsLeggings.itemTokenPrice[0] = new Array(40,2,0,0);
fHierophantsLeggings.itemStats = new Array();
fHierophantsLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Hierophant's Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Cloth</span>\
<br>119 Armor<br>+39 Stamina<br>+17 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 65 / 65<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHierophantsLeggings; ++i;

var fShadowstalkersSash = new RewardItem("alliance","Shadowstalker's Sash","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fhalaa%2Fscripts%2Frewards-halaa-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Belt_15.gif&reason=external-or-uncollected-resource");
fShadowstalkersSash.itemTokenPrice = new Array();
fShadowstalkersSash.itemTokenPrice[0] = new Array(20,1,0,0);
fShadowstalkersSash.itemStats = new Array();
fShadowstalkersSash.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Shadowstalker's Sash</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>144 Armor<br>+17 Agility<br>+24 Stamina<br>Durability 35 / 35<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fShadowstalkersSash; ++i;

var fShadowstalkersLeggings = new RewardItem("alliance","Shadowstalker's Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fhalaa%2Fscripts%2Frewards-halaa-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Leather_03.gif&reason=external-or-uncollected-resource");
fShadowstalkersLeggings.itemTokenPrice = new Array();
fShadowstalkersLeggings.itemTokenPrice[0] = new Array(40,2,0,0);
fShadowstalkersLeggings.itemStats = new Array();
fShadowstalkersLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Shadowstalker's Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Leather</span>\
<br>224 Armor<br>+23 Agility<br>+33 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 75 / 75<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 30.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fShadowstalkersLeggings; ++i;

var fSlayersWaistguard = new RewardItem("alliance","Slayer's Waistguard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_14.gif");
fSlayersWaistguard.itemTokenPrice = new Array();
fSlayersWaistguard.itemTokenPrice[0] = new Array(20,1,0,0);
fSlayersWaistguard.itemStats = new Array();
fSlayersWaistguard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Slayer's Waistguard</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Plate</span>\
<br>573 Armor<br>+22 Strength<br>+24 Stamina<br>Durability 45 / 45<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves melee critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSlayersWaistguard; ++i;

var fSlayersLegguards = new RewardItem("alliance","Slayer's Legguards","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fhalaa%2Fscripts%2Frewards-halaa-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Plate_15.gif&reason=external-or-uncollected-resource");
fSlayersLegguards.itemTokenPrice = new Array();
fSlayersLegguards.itemTokenPrice[0] = new Array(40,2,0,0);
fSlayersLegguards.itemStats = new Array();
fSlayersLegguards.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Slayer's Legguards</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Plate</span>\
<br>891 Armor<br>+25 Strength<br>+39 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 100 / 100<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSlayersLegguards; ++i;

var fStormbreakersGirdle = new RewardItem("alliance","Stormbreaker's Girdle","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_20.gif");
fStormbreakersGirdle.itemTokenPrice = new Array();
fStormbreakersGirdle.itemTokenPrice[0] = new Array(20,1,0,0);
fStormbreakersGirdle.itemStats = new Array();
fStormbreakersGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Stormbreaker's Girdle</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Mail</span>\
<br>321 Armor<br>+28 Stamina<br>+19 Intellect<br>Durability 40 / 40<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormbreakersGirdle; ++i;

var fStormbreakersLeggings = new RewardItem("alliance","Stormbreaker's Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fhalaa%2Fscripts%2Frewards-halaa-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Mail_12.gif&reason=external-or-uncollected-resource");
fStormbreakersLeggings.itemTokenPrice = new Array();
fStormbreakersLeggings.itemTokenPrice[0] = new Array(40,2,0,0);
fStormbreakersLeggings.itemStats = new Array();
fStormbreakersLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Stormbreaker's Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Mail</span>\
<br>499 Armor<br>+39 Stamina<br>+16 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Resilience Rating</span>\
<br>Durability 90 / 90<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormbreakersLeggings; ++i;

var fDreamstalkerSash = new RewardItem("alliance","Dreamstalker Sash","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_17.gif");
fDreamstalkerSash.itemTokenPrice = new Array();
fDreamstalkerSash.itemTokenPrice[0] = new Array(20,1,0,0);
fDreamstalkerSash.itemStats = new Array();
fDreamstalkerSash.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Dreamstalker Sash</span>\
<br>Binds when picked up<br>Unique<br>Waist<span class=\"myRight\">Leather</span>\
<br>184 Armor<br>+15 Strength<br>+13 Agility<br>+24 Stamina<br>+15 Intellect<br>Durability 35 / 35<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDreamstalkerSash; ++i;

var fDreamstalkerLeggings = new RewardItem("alliance","Dreamstalker Leggings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Pants_07.gif");
fDreamstalkerLeggings.itemTokenPrice = new Array();
fDreamstalkerLeggings.itemTokenPrice[0] = new Array(40,2,0,0);
fDreamstalkerLeggings.itemStats = new Array();
fDreamstalkerLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Dreamstalker Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Leather</span>\
<br>284 Armor<br>+20 Strength<br>+6 Agility<br>+30 Stamina<br>+10 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Resilience Rating</span>\
<br>Durability 75 / 75<br>Requires Level 66<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDreamstalkerLeggings; ++i;

var fHalaaniBag = new RewardItem("alliance","Halaani Bag","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fhalaa%2Fscripts%2Frewards-halaa-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Bag_17.gif&reason=external-or-uncollected-resource");
fHalaaniBag.itemTokenPrice = new Array();
fHalaaniBag.itemTokenPrice[0] = new Array(0,8,0,0);
fHalaaniBag.itemStats = new Array();
fHalaaniBag.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Halaani Bag</span>\
<br>Binds when picked up<br>Unique<br>18 Slot Bag</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHalaaniBag; ++i;

var fSublimeMysticDawnstone = new RewardItem("alliance","Sublime Mystic Dawnstone","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Misc_Gem_Topaz_01.gif");
fSublimeMysticDawnstone.itemTokenPrice = new Array();
fSublimeMysticDawnstone.itemTokenPrice[0] = new Array(100,0,0,0);
fSublimeMysticDawnstone.itemStats = new Array();
fSublimeMysticDawnstone.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sublime Mystic Dawnstone</span>\
<br>Binds when picked up<br>Unique<br>+10 Resilience<br>\
<span class=\"myYellow\">\"Matches a Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSublimeMysticDawnstone; ++i;



//------END REWARDS DEFINITION------
