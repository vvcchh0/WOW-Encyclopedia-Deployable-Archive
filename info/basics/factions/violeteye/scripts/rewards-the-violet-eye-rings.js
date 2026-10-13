/* --------- Faction Lore ------------- */
loreTexts["alliance"] = "<h3>The Violet Eye</h3>\
Looming over Deadwind Pass, the eldritch tower of Karazhan casts its shadow on the lands below. From the outside, the ruined tower looks as if it was abandoned long ago. Yet those who have come face to face with true evil know that some horrors never truly disappear. The tower�s last master, the wizard Medivh, is gone, but the echoes of his evil deeds linger within the walls of Karazhan.\
<br/><br/>\
Although there seems little hope of ever lifting the shadows from these Light-forsaken lands, there are still people who will stand against the sinister presence that has taken up residence in Karazhan. The Violet Eye is a secret sect of the Kirin Tor, the ruling council of Dalaran. The Violet Eye was assigned to keep an eye on Karazhan and Medivh, in case things got out of hand. And things in Karazhan have indeed gotten out of hand. In recent years, several nobles of Darkshire ventured into Deadwind Pass to investigate the blight that had settled over the region. They entered the dark tower, but never emerged. The Violet Eye, too, sent agents into Karazhan to investigate, but none of them ever reported back. To make matters worse, the wizards of the Violet Eye have discovered what might very well be demonic emanations coming from the tower.\
<br/><br/>\
Whatever haunts the halls of Karazhan, it must be stopped at all costs. The tower was built at a powerful convergence of magical energies: only disaster could result if Karazhan fell into the hands of an enemy unencumbered by conscience or mercy. Members of the Violet Eye are keeping watch at the base of the tower, and they will gladly accept the aid of any adventurer willing to help.";

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

tokenIcons = new Array("sporeggar","arathi","nether","warsong");
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
			//selectBracket(thisObject,thisBracket-1);
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

var fVioletSignet = new RewardItem("alliance","Violet Signet (Mage)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+18 Stamina<br>+18 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Mage)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+18 Stamina<br>+19 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Mage)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+19 Stamina<br>+20 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignetOfTheArchmage = new RewardItem("alliance","Violet Signet of the Archmage","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignetOfTheArchmage.itemStats = new Array();
fVioletSignetOfTheArchmage.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet of the Archmage</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+21 Stamina<br>+21 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignetOfTheArchmage; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Restorer)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+18 Stamina<br>+18 Intellect<br>+12 Spirit<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Restorer)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+18 Stamina<br>+19 Intellect<br>+13 Spirit<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 44.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Restorer)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+19 Stamina<br>+20 Intellect<br>+14 Spirit<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignetOfTheGrandRestorer = new RewardItem("alliance","Violet Signet of the Grand Restorer","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignetOfTheGrandRestorer.itemStats = new Array();
fVioletSignetOfTheGrandRestorer.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet of the Grand Restorer</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+21 Stamina<br>+21 Intellect<br>+14 Spirit<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 48.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignetOfTheGrandRestorer; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Assassin)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+19 Stamina<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Assassin)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+21 Stamina<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Assassin)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+22 Stamina<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignetOfTheMasterAssassin = new RewardItem("alliance","Violet Signet of the Master Assassin","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignetOfTheMasterAssassin.itemStats = new Array();
fVioletSignetOfTheMasterAssassin.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet of the Master Assassin</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignetOfTheMasterAssassin; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Protector)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>210 Armor<br>+27 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 13.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Protector)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>230 Armor<br>+30 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 14.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignet = new RewardItem("alliance","Violet Signet (Protector)","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignet.itemStats = new Array();
fVioletSignet.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>235 Armor<br>+31 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 15.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignet; ++i;

var fVioletSignetOfTheGreatProtector = new RewardItem("alliance","Violet Signet of the Great Protector","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye-rings.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_62.gif&reason=external-or-uncollected-resource");
fVioletSignetOfTheGreatProtector.itemStats = new Array();
fVioletSignetOfTheGreatProtector.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Violet Signet of the Great Protector</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>250 Armor<br>+33 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVioletSignetOfTheGreatProtector; ++i;

//-------------------------------------------------------------------
//---Horde below







//------END REWARDS DEFINITION------
