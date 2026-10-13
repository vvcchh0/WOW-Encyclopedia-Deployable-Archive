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
		outPutString += thisObject.itemHonorPrice[thisBracket]+"<img src='/WOW-Encyclopedia-Deployable-Archive/pvp/arena-points.gif'>&nbsp;";
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

var fGladiatorsGreatsword = new RewardItem("alliance","Gladiator's Greatsword","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Sword_70.gif&reason=external-or-uncollected-resource");
fGladiatorsGreatsword.itemHonorPrice = new Array();
fGladiatorsGreatsword.itemHonorPrice[0] = 3750
fGladiatorsGreatsword.itemStats = new Array();
fGladiatorsGreatsword.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Greatsword</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Sword</span>\
<br>330 - 496 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(114.7 damage per second)<br>+32 Strength<br>+48 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myYellow\">\"Finely crafted to Proximo's specification.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsGreatsword; ++i;

var fGladiatorsDecapitator = new RewardItem("alliance","Gladiator's Decapitator","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Axe_68.gif&reason=external-or-uncollected-resource");
fGladiatorsDecapitator.itemHonorPrice = new Array();
fGladiatorsDecapitator.itemHonorPrice[0] = 3750
fGladiatorsDecapitator.itemStats = new Array();
fGladiatorsDecapitator.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Decapitator</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Axe</span>\
<br>330 - 496 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(114.7 damage per second)<br>+48 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 64.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsDecapitator; ++i;

var fGladiatorsBonegrinder = new RewardItem("alliance","Gladiator's Bonegrinder","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mace_52.gif&reason=external-or-uncollected-resource");
fGladiatorsBonegrinder.itemHonorPrice = new Array();
fGladiatorsBonegrinder.itemHonorPrice[0] = 3750
fGladiatorsBonegrinder.itemStats = new Array();
fGladiatorsBonegrinder.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Bonegrinder</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>330 - 496 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(114.7 damage per second)<br>+32 Strength<br>+48 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsBonegrinder; ++i;

var fGladiatorsPainsaw = new RewardItem("alliance","Gladiator's Painsaw","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Halberd15.gif&reason=external-or-uncollected-resource");
fGladiatorsPainsaw.itemHonorPrice = new Array();
fGladiatorsPainsaw.itemHonorPrice[0] = 3750
fGladiatorsPainsaw.itemStats = new Array();
fGladiatorsPainsaw.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Painsaw</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>201 - 303 Damage<span class=\"myRight\">Speed 2.20</span>\
<br>(114.5 damage per second)<br>+48 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 64.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsPainsaw; ++i;

var fGladiatorsMaul = new RewardItem("alliance","Gladiator's Maul","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mace_52.gif&reason=external-or-uncollected-resource");
fGladiatorsMaul.itemHonorPrice = new Array();
fGladiatorsMaul.itemHonorPrice[0] = 3750
fGladiatorsMaul.itemStats = new Array();
fGladiatorsMaul.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Maul</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>161 - 328 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(67.9 damage per second)<br>+32 Strength<br>+48 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 654 in Cat, Bear, Dire Bear, and Moonkin forms only.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsMaul; ++i;

var fGladiatorsHeavyCrossbow = new RewardItem("alliance","Gladiator's Heavy Crossbow","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsheavycrossbow.gif");
fGladiatorsHeavyCrossbow.itemHonorPrice = new Array();
fGladiatorsHeavyCrossbow.itemHonorPrice[0] = 3750
fGladiatorsHeavyCrossbow.itemStats = new Array();
fGladiatorsHeavyCrossbow.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Heavy Crossbow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Crossbow</span>\
<br>202 - 304 Damage<span class=\"myRight\">Speed 3.20</span>\
<br>(79.1 damage per second)<br>+15 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 24.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsHeavyCrossbow; ++i;

var fGladiatorsSlicer = new RewardItem("alliance","Gladiator's Slicer","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Sword_71.gif&reason=external-or-uncollected-resource");
fGladiatorsSlicer.itemHonorPrice = new Array();
fGladiatorsSlicer.itemHonorPrice[0] = 2625
fGladiatorsSlicer.itemStats = new Array();
fGladiatorsSlicer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Slicer</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>183 - 275 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(88.1 damage per second)<br>+21 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSlicer; ++i;

var fGladiatorsQuickblade = new RewardItem("alliance","Gladiator's Quickblade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Sword_71.gif&reason=external-or-uncollected-resource");
fGladiatorsQuickblade.itemHonorPrice = new Array();
fGladiatorsQuickblade.itemHonorPrice[0] = 1125
fGladiatorsQuickblade.itemStats = new Array();
fGladiatorsQuickblade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Quickblade</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Sword</span>\
<br>127 - 191 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(88.3 damage per second)<br>+21 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsQuickblade; ++i;

var fGladiatorsCleaver = new RewardItem("alliance","Gladiator's Cleaver","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Axe_54.gif&reason=external-or-uncollected-resource");
fGladiatorsCleaver.itemHonorPrice = new Array();
fGladiatorsCleaver.itemHonorPrice[0] = 2625
fGladiatorsCleaver.itemStats = new Array();
fGladiatorsCleaver.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Cleaver</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>183 - 275 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(88.1 damage per second)<br>+21 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsCleaver; ++i;

var fGladiatorsHacker = new RewardItem("alliance","Gladiator's Hacker","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Axe_54.gif&reason=external-or-uncollected-resource");
fGladiatorsHacker.itemHonorPrice = new Array();
fGladiatorsHacker.itemHonorPrice[0] = 1125
fGladiatorsHacker.itemStats = new Array();
fGladiatorsHacker.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Hacker</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Axe</span>\
<br>127 - 191 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(88.3 damage per second)<br>+21 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsHacker; ++i;

var fGladiatorsPummeler = new RewardItem("alliance","Gladiator's Pummeler","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mace_36.gif&reason=external-or-uncollected-resource");
fGladiatorsPummeler.itemHonorPrice = new Array();
fGladiatorsPummeler.itemHonorPrice[0] = 2625
fGladiatorsPummeler.itemStats = new Array();
fGladiatorsPummeler.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Pummeler</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>183 - 275 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(88.1 damage per second)<br>+21 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsPummeler; ++i;

var fGladiatorsBonecracker = new RewardItem("alliance","Gladiator's Bonecracker","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mace_36.gif&reason=external-or-uncollected-resource");
fGladiatorsBonecracker.itemHonorPrice = new Array();
fGladiatorsBonecracker.itemHonorPrice[0] = 1125
fGladiatorsBonecracker.itemStats = new Array();
fGladiatorsBonecracker.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Bonecracker</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Mace</span>\
<br>127 - 191 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(88.3 damage per second)<br>+21 Stamina<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsBonecracker; ++i;

var fGladiatorsRightRipper = new RewardItem("alliance","Gladiator's Right Ripper","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Hand_13.gif&reason=external-or-uncollected-resource");
fGladiatorsRightRipper.itemHonorPrice = new Array();
fGladiatorsRightRipper.itemHonorPrice[0] = 2625
fGladiatorsRightRipper.itemStats = new Array();
fGladiatorsRightRipper.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Right Ripper</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Fist Weapon</span>\
<br>160 - 298 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(88.1 damage per second)<br>+21 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsRightRipper; ++i;

var fGladiatorsLeftRipper = new RewardItem("alliance","Gladiator's Left Ripper","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Hand_13.gif&reason=external-or-uncollected-resource");
fGladiatorsLeftRipper.itemHonorPrice = new Array();
fGladiatorsLeftRipper.itemHonorPrice[0] = 1125
fGladiatorsLeftRipper.itemStats = new Array();
fGladiatorsLeftRipper.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Left Ripper</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Fist Weapon</span>\
<br>111 - 206 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(88.1 damage per second)<br>+21 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsLeftRipper; ++i;


var fGladiatorsShanker = new RewardItem("alliance","Gladiator's Shanker","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Shortblade_45.gif&reason=external-or-uncollected-resource");
fGladiatorsShanker.itemHonorPrice = new Array();
fGladiatorsShanker.itemHonorPrice[0] = 2625
fGladiatorsShanker.itemStats = new Array();
fGladiatorsShanker.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Shanker</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>127 - 191 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(88.3 damage per second)<br>+21 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsShanker; ++i;

var fGladiatorsShiv = new RewardItem("alliance","Gladiator's Shiv","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Shortblade_45.gif&reason=external-or-uncollected-resource");
fGladiatorsShiv.itemHonorPrice = new Array();
fGladiatorsShiv.itemHonorPrice[0] = 1125
fGladiatorsShiv.itemStats = new Array();
fGladiatorsShiv.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Shiv</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Dagger</span>\
<br>98 - 148 Damage<span class=\"myRight\">Speed 1.40</span>\
<br>(87.9 damage per second)<br>+21 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsShiv; ++i;

var fGladiatorsShieldWall = new RewardItem("alliance","Gladiator's Shield Wall","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Shield_31.gif&reason=external-or-uncollected-resource");
fGladiatorsShieldWall.itemHonorPrice = new Array();
fGladiatorsShieldWall.itemHonorPrice[0] = 1875
fGladiatorsShieldWall.itemStats = new Array();
fGladiatorsShieldWall.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Shield Wall</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>4872 Armor<br>122 Block<br>+42 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsShieldWall; ++i;

var fGladiatorsWarEdge = new RewardItem("alliance","Gladiator's War Edge","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalscleaver.gif");
fGladiatorsWarEdge.itemHonorPrice = new Array();
fGladiatorsWarEdge.itemHonorPrice[0] = 1000
fGladiatorsWarEdge.itemStats = new Array();
fGladiatorsWarEdge.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's War Edge</span>\
<br>Binds when picked up<br>Thrown<span class=\"myRight\">Thrown</span>\
<br>82 - 124 Damage<span class=\"myRight\">Speed 1.9</span>\
<br>(79.2 damage per second)<br>+15 Stamina<br>Durability 285 / 285<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsWarEdge; ++i;

var fGladiatorsWarStaff = new RewardItem("alliance","Gladiator's War Staff","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Staff_53.gif&reason=external-or-uncollected-resource");
fGladiatorsWarStaff.itemHonorPrice = new Array();
fGladiatorsWarStaff.itemHonorPrice[0] = 3750
fGladiatorsWarStaff.itemStats = new Array();
fGladiatorsWarStaff.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's War Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>134 - 273 Damage<span class=\"myRight\">Speed 3.00</span>\
<br>(67.9 damage per second)<br>+48 Stamina<br>+32 Intellect<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 187.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsWarStaff; ++i;

var fGladiatorsSpellblade = new RewardItem("alliance","Gladiator's Spellblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdirk.gif");
fGladiatorsSpellblade.itemHonorPrice = new Array();
fGladiatorsSpellblade.itemHonorPrice[0] = 3150
fGladiatorsSpellblade.itemStats = new Array();
fGladiatorsSpellblade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Spellblade</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Dagger</span>\
<br>23 - 109 Damage<span class=\"myRight\">Speed 1.60</span>\
<br>(41.3 damage per second)<br>+24 Stamina<br>+16 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 187.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsSpellblade; ++i;

var fTouchOfDefeat = new RewardItem("alliance","Touch of Defeat","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Wand_09.gif&reason=external-or-uncollected-resource");
fTouchOfDefeat.itemHonorPrice = new Array();
fTouchOfDefeat.itemHonorPrice[0] = 1000
fTouchOfDefeat.itemStats = new Array();
fTouchOfDefeat.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Touch of Defeat</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Wand</span>\
<br>215 - 400 Fire Damage<span class=\"myRight\">Speed 1.90</span>\
<br>(161.8 damage per second)<br>+15 Stamina<br>+10 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 13.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTouchOfDefeat; ++i;

var fGladiatorsEndgame = new RewardItem("alliance","Gladiator's Endgame","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsbattletome.gif");
fGladiatorsEndgame.itemHonorPrice = new Array();
fGladiatorsEndgame.itemHonorPrice[0] = 1125
fGladiatorsEndgame.itemStats = new Array();
fGladiatorsEndgame.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gladiator's Endgame</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+21 Stamina<br>+13 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 16.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGladiatorsEndgame; ++i;

var fIdolOfTenacity = new RewardItem("alliance","Idol of Tenacity","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_IdolofHealth.gif&reason=external-or-uncollected-resource");
fIdolOfTenacity.itemHonorPrice = new Array();
fIdolOfTenacity.itemHonorPrice[0] = 1000
fIdolOfTenacity.itemStats = new Array();
fIdolOfTenacity.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Idol of Tenacity</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Idol</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases the final healing value of your Lifebloom by 80.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIdolOfTenacity; ++i;


var fLibramOfJustice = new RewardItem("alliance","Libram of Justice","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_LibramofHope.gif&reason=external-or-uncollected-resource");
fLibramOfJustice.itemHonorPrice = new Array();
fLibramOfJustice.itemHonorPrice[0] = 1000
fLibramOfJustice.itemStats = new Array();
fLibramOfJustice.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Libram of Justice</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Libram</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Causes your Flash of Light to increase the target's Resilience rating by 24 for 6 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLibramOfJustice; ++i;

var fTotemOfTheThirdWind = new RewardItem("alliance","Totem of the Third Wind","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-arena-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Nature_SlowingTotem.gif&reason=external-or-uncollected-resource");
fTotemOfTheThirdWind.itemHonorPrice = new Array();
fTotemOfTheThirdWind.itemHonorPrice[0] = 1000
fTotemOfTheThirdWind.itemStats = new Array();
fTotemOfTheThirdWind.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Totem of the Third Wind</span>\
<br>Binds when picked up<br>Relic<span class=\"myRight\">Totem</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Causes your Lesser Healing Wave to increase the target's Resilience rating by 24 for 6 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTotemOfTheThirdWind; ++i;




//-------------------------------------------------------------------
//---Horde below






//------END REWARDS DEFINITION------
