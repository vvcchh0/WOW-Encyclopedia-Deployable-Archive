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

var fGrandMarshalsClaymore = new RewardItem("alliance","Grand Marshal's Claymore","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalclaymore.gif");
fGrandMarshalsClaymore.itemHonorPrice = new Array();
fGrandMarshalsClaymore.itemHonorPrice[0] = 30600
fGrandMarshalsClaymore.itemTokenPrice = new Array();
fGrandMarshalsClaymore.itemTokenPrice[0] = new Array(40,0,0,0);
fGrandMarshalsClaymore.itemStats = new Array();
fGrandMarshalsClaymore.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Claymore</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Sword</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsClaymore; ++i;




var fGrandMarshalsSunderer = new RewardItem("alliance","Grand Marshal's Sunderer","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsunderer.gif");
fGrandMarshalsSunderer.itemHonorPrice = new Array();
fGrandMarshalsSunderer.itemHonorPrice[0] = 30600
fGrandMarshalsSunderer.itemTokenPrice = new Array();
fGrandMarshalsSunderer.itemTokenPrice[0] = new Array(40,0,0,0);
fGrandMarshalsSunderer.itemStats = new Array();
fGrandMarshalsSunderer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Sunderer</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Axe</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSunderer; ++i;




var fGrandMarshalsBattleHammer = new RewardItem("alliance","Grand Marshal's Battle Hammer","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalbattlehammer.gif&reason=external-or-uncollected-resource");
fGrandMarshalsBattleHammer.itemHonorPrice = new Array();
fGrandMarshalsBattleHammer.itemHonorPrice[0] = 30600
fGrandMarshalsBattleHammer.itemTokenPrice = new Array();
fGrandMarshalsBattleHammer.itemTokenPrice[0] = new Array(40,0,0,0);
fGrandMarshalsBattleHammer.itemStats = new Array();
fGrandMarshalsBattleHammer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Battle Hammer</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsBattleHammer; ++i;








var fGrandMarshalsDemolisher = new RewardItem("alliance","Grand Marshal's Demolisher","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsdemolisher.gif&reason=external-or-uncollected-resource");
fGrandMarshalsDemolisher.itemHonorPrice = new Array();
fGrandMarshalsDemolisher.itemHonorPrice[0] = 30600
fGrandMarshalsDemolisher.itemTokenPrice = new Array();
fGrandMarshalsDemolisher.itemTokenPrice[0] = new Array(40,0,0,0);
fGrandMarshalsDemolisher.itemStats = new Array();
fGrandMarshalsDemolisher.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Demolisher</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+28 Stamina<br>+27 Intellect<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDemolisher; ++i;





var fGrandMarshalsGlaive = new RewardItem("alliance","Grand Marshal's Glaive","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsglaive.gif&reason=external-or-uncollected-resource");
fGrandMarshalsGlaive.itemHonorPrice = new Array();
fGrandMarshalsGlaive.itemHonorPrice[0] = 30600
fGrandMarshalsGlaive.itemTokenPrice = new Array();
fGrandMarshalsGlaive.itemTokenPrice[0] = new Array(40,0,0,0);
fGrandMarshalsGlaive.itemStats = new Array();
fGrandMarshalsGlaive.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Glaive</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsGlaive; ++i;




var fGrandMarshalsHandaxe = new RewardItem("alliance","Grand Marshal's Handaxe","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalshandaxe.gif&reason=external-or-uncollected-resource");
fGrandMarshalsHandaxe.itemHonorPrice = new Array();
fGrandMarshalsHandaxe.itemHonorPrice[0] = 15300
fGrandMarshalsHandaxe.itemTokenPrice = new Array();
fGrandMarshalsHandaxe.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsHandaxe.itemStats = new Array();
fGrandMarshalsHandaxe.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Handaxe</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsHandaxe; ++i;

var fGrandMarshalsLongsword = new RewardItem("alliance","Grand Marshal's Longsword","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalslongsword.gif&reason=external-or-uncollected-resource");
fGrandMarshalsLongsword.itemHonorPrice = new Array();
fGrandMarshalsLongsword.itemHonorPrice[0] = 15300
fGrandMarshalsLongsword.itemTokenPrice = new Array();
fGrandMarshalsLongsword.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsLongsword.itemStats = new Array();
fGrandMarshalsLongsword.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Longsword</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLongsword; ++i;


var fGrandMarshalsSwiftblade = new RewardItem("alliance","Grand Marshal's Swiftblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsswiftblade.gif");
fGrandMarshalsSwiftblade.itemHonorPrice = new Array();
fGrandMarshalsSwiftblade.itemHonorPrice[0] = 15300
fGrandMarshalsSwiftblade.itemTokenPrice = new Array();
fGrandMarshalsSwiftblade.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsSwiftblade.itemStats = new Array();
fGrandMarshalsSwiftblade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Swiftblade</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>85 - 129 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(59.4 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSwiftblade; ++i;

var fGrandMarshalsPunisher = new RewardItem("alliance","Grand Marshal's Punisher","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalspunisher.gif&reason=external-or-uncollected-resource");
fGrandMarshalsPunisher.itemHonorPrice = new Array();
fGrandMarshalsPunisher.itemHonorPrice[0] = 15300
fGrandMarshalsPunisher.itemTokenPrice = new Array();
fGrandMarshalsPunisher.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsPunisher.itemStats = new Array();
fGrandMarshalsPunisher.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Punisher</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPunisher; ++i;




var fGrandMarshalsWarhammer = new RewardItem("alliance","Grand Marshal's Warhammer","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalswarhammer.gif&reason=external-or-uncollected-resource");
fGrandMarshalsWarhammer.itemHonorPrice = new Array();
fGrandMarshalsWarhammer.itemHonorPrice[0] = 15300
fGrandMarshalsWarhammer.itemTokenPrice = new Array();
fGrandMarshalsWarhammer.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsWarhammer.itemStats = new Array();
fGrandMarshalsWarhammer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Warhammer</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Mace</span>\
<br>68 - 173 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(41.7 damage per second)<br>+14 Stamina<br>+8 Intellect<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 134.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWarhammer; ++i;


var fGrandMarshalsRightHandBlade = new RewardItem("alliance","Grand Marshal's Right Hand Blade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsrighthandblade.gif&reason=external-or-uncollected-resource");
fGrandMarshalsRightHandBlade.itemHonorPrice = new Array();
fGrandMarshalsRightHandBlade.itemHonorPrice[0] = 15300
fGrandMarshalsRightHandBlade.itemTokenPrice = new Array();
fGrandMarshalsRightHandBlade.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsRightHandBlade.itemStats = new Array();
fGrandMarshalsRightHandBlade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Right Hand Blade</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Fist Weapon</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRightHandBlade; ++i;


var fGrandMarshalsLeftHandBlade = new RewardItem("alliance","Grand Marshal's Left Hand Blade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalslefthandblade.gif&reason=external-or-uncollected-resource");
fGrandMarshalsLeftHandBlade.itemHonorPrice = new Array();
fGrandMarshalsLeftHandBlade.itemHonorPrice[0] = 15300
fGrandMarshalsLeftHandBlade.itemTokenPrice = new Array();
fGrandMarshalsLeftHandBlade.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsLeftHandBlade.itemStats = new Array();
fGrandMarshalsLeftHandBlade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Left Hand Blade</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Fist Weapon</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeftHandBlade; ++i;

var fGrandMarshalsDirk = new RewardItem("alliance","Grand Marshal's Dirk","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdirk.gif");
fGrandMarshalsDirk.itemHonorPrice = new Array();
fGrandMarshalsDirk.itemHonorPrice[0] = 15300
fGrandMarshalsDirk.itemTokenPrice = new Array();
fGrandMarshalsDirk.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsDirk.itemStats = new Array();
fGrandMarshalsDirk.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Dirk</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>95 - 143 Damage<span class=\"myRight\">Speed 2.00</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDirk; ++i;

var fGrandMarshalsAegis = new RewardItem("alliance","Grand Marshal's Aegis","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsaegis.gif&reason=external-or-uncollected-resource");
fGrandMarshalsAegis.itemHonorPrice = new Array();
fGrandMarshalsAegis.itemHonorPrice[0] = 15300
fGrandMarshalsAegis.itemTokenPrice = new Array();
fGrandMarshalsAegis.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsAegis.itemStats = new Array();
fGrandMarshalsAegis.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Aegis</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>3366 Armor<br>73 Block<br>+10 Strength<br>+23 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: When struck in combat has a 5% chance of inflicting 35 to 65 Nature damage to the attacker.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsAegis; ++i;

var fGrandMarshalsBullseye = new RewardItem("alliance","Grand Marshal's Bullseye","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsbullseye.gif&reason=external-or-uncollected-resource");
fGrandMarshalsBullseye.itemHonorPrice = new Array();
fGrandMarshalsBullseye.itemHonorPrice[0] = 15300
fGrandMarshalsBullseye.itemTokenPrice = new Array();
fGrandMarshalsBullseye.itemTokenPrice[0] = new Array(0,40,0,0);
fGrandMarshalsBullseye.itemStats = new Array();
fGrandMarshalsBullseye.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Bullseye</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>80 - 121 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(55.8 damage per second)<br>+7 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 36.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsBullseye; ++i;

var fGrandMarshalsRepeater = new RewardItem("alliance","Grand Marshal's Repeater","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsrepeater.gif&reason=external-or-uncollected-resource");
fGrandMarshalsRepeater.itemHonorPrice = new Array();
fGrandMarshalsRepeater.itemHonorPrice[0] = 15300
fGrandMarshalsRepeater.itemTokenPrice = new Array();
fGrandMarshalsRepeater.itemTokenPrice[0] = new Array(0,40,0,0);
fGrandMarshalsRepeater.itemStats = new Array();
fGrandMarshalsRepeater.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Repeater</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Crossbow</span>\
<br>129 - 195 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(55.9 damage per second)<br>+7 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 36.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRepeater; ++i;


var fGrandMarshalsHandCannon = new RewardItem("alliance","Grand Marshal's Hand Cannon","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalshandcannon.gif&reason=external-or-uncollected-resource");
fGrandMarshalsHandCannon.itemHonorPrice = new Array();
fGrandMarshalsHandCannon.itemHonorPrice[0] = 15300
fGrandMarshalsHandCannon.itemTokenPrice = new Array();
fGrandMarshalsHandCannon.itemTokenPrice[0] = new Array(0,40,0,0);
fGrandMarshalsHandCannon.itemStats = new Array();
fGrandMarshalsHandCannon.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Hand Cannon</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Gun</span>\
<br>129 - 195 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(55.9 damage per second)<br>+7 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 36.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsHandCannon; ++i;

var fGrandMarshalsStave = new RewardItem("alliance","Grand Marshal's Stave","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsstave.gif&reason=external-or-uncollected-resource");
fGrandMarshalsStave.itemHonorPrice = new Array();
fGrandMarshalsStave.itemHonorPrice[0] = 30600
fGrandMarshalsStave.itemTokenPrice = new Array();
fGrandMarshalsStave.itemTokenPrice[0] = new Array(40,0,0,0);
fGrandMarshalsStave.itemStats = new Array();
fGrandMarshalsStave.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Stave</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>131 - 225 Damage<span class=\"myRight\">Speed 3.00</span>\
<br>(59.3 damage per second)<br>+41 Stamina<br>+23 Intellect<br>+17 Spirit<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 71.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsStave; ++i;

var fGrandMarshalsMageblade = new RewardItem("alliance","Grand Marshal's Mageblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdirk.gif");
fGrandMarshalsMageblade.itemHonorPrice = new Array();
fGrandMarshalsMageblade.itemHonorPrice[0] = 15300
fGrandMarshalsMageblade.itemTokenPrice = new Array();
fGrandMarshalsMageblade.itemTokenPrice[0] = new Array(0,20,0,0);
fGrandMarshalsMageblade.itemStats = new Array();
fGrandMarshalsMageblade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Mageblade</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Dagger</span>\
<br>47 - 119 Damage<span class=\"myRight\">Speed 2.00</span>\
<br>(41.5 damage per second)<br>+14 Stamina<br>+8 Intellect<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 72.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMageblade; ++i;

var fGrandMarshalsTomeOfPower = new RewardItem("alliance","Grand Marshal's Tome of Power","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalstomeofpower.gif");
fGrandMarshalsTomeOfPower.itemHonorPrice = new Array();
fGrandMarshalsTomeOfPower.itemHonorPrice[0] = 15300
fGrandMarshalsTomeOfPower.itemTokenPrice = new Array();
fGrandMarshalsTomeOfPower.itemTokenPrice[0] = new Array(0,40,0,0);
fGrandMarshalsTomeOfPower.itemStats = new Array();
fGrandMarshalsTomeOfPower.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Tome of Power</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+17 Stamina<br>+16 Intellect<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsTomeOfPower; ++i;

var fGrandMarshalsTomeOfRestoration = new RewardItem("alliance","Grand Marshal's Tome of Restoration","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalstomeofrestore.gif&reason=external-or-uncollected-resource");
fGrandMarshalsTomeOfRestoration.itemHonorPrice = new Array();
fGrandMarshalsTomeOfRestoration.itemHonorPrice[0] = 15300
fGrandMarshalsTomeOfRestoration.itemTokenPrice = new Array();
fGrandMarshalsTomeOfRestoration.itemTokenPrice[0] = new Array(0,40,0,0);
fGrandMarshalsTomeOfRestoration.itemStats = new Array();
fGrandMarshalsTomeOfRestoration.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">Grand Marshal's Tome of Restoration</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+14 Stamina<br>+14 Intellect<br>+14 Spirit<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsTomeOfRestoration; ++i;

var fGrandMarshalsWarblade = new RewardItem("alliance","Grand Marshal's Warblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalclaymore.gif");
fGrandMarshalsWarblade.itemHonorPrice = new Array();
fGrandMarshalsWarblade.itemHonorPrice[1] = 30600
fGrandMarshalsWarblade.itemTokenPrice = new Array();
fGrandMarshalsWarblade.itemTokenPrice[1] = new Array(40,0,0,0);
fGrandMarshalsWarblade.itemStats = new Array();
fGrandMarshalsWarblade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Warblade</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Sword</span>\
<br>268 - 403 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(93.2 damage per second)<br>+28 Strength<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70</span>\
<br><span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br><span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWarblade; ++i;

var fGrandMarshalsDecapitator = new RewardItem("alliance","Grand Marshal's Decapitator","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdecapitator.gif");
fGrandMarshalsDecapitator.itemHonorPrice = new Array();
fGrandMarshalsDecapitator.itemHonorPrice[1] = 30600
fGrandMarshalsDecapitator.itemTokenPrice = new Array();
fGrandMarshalsDecapitator.itemTokenPrice[1] = new Array(40,0,0,0);
fGrandMarshalsDecapitator.itemStats = new Array();
fGrandMarshalsDecapitator.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Decapitator</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Axe</span>\
<br>268 - 403 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(93.2 damage per second)<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br><span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br><span class=\"myGreen\">Equip: Increases attack power by 56.</span>\
</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsDecapitator; ++i;

var fGrandMarshalsBonegrinder = new RewardItem("alliance","Grand Marshal's Bonegrinder","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsbonegrinder.gif");
fGrandMarshalsBonegrinder.itemHonorPrice = new Array();
fGrandMarshalsBonegrinder.itemHonorPrice[1] = 30600
fGrandMarshalsBonegrinder.itemTokenPrice = new Array();
fGrandMarshalsBonegrinder.itemTokenPrice[1] = new Array(40,0,0,0);
fGrandMarshalsBonegrinder.itemStats = new Array();
fGrandMarshalsBonegrinder.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Bonegrinder</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>268 - 403 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(93.2 damage per second)<br>+28 Strength<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70</span>\
<br><span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br><span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsBonegrinder; ++i;

var fGrandMarshalsPainsaw = new RewardItem("alliance","Grand Marshal's Painsaw","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalspainsaw.gif");
fGrandMarshalsPainsaw.itemHonorPrice = new Array();
fGrandMarshalsPainsaw.itemHonorPrice[1] = 30600
fGrandMarshalsPainsaw.itemTokenPrice = new Array();
fGrandMarshalsPainsaw.itemTokenPrice[1] = new Array(40,0,0,0);
fGrandMarshalsPainsaw.itemStats = new Array();
fGrandMarshalsPainsaw.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Painsaw</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>164 - 246 Damage<span class=\"myRight\">Speed 2.20</span>\
<br>(93.2 damage per second)<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br><span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br><span class=\"myGreen\">Equip: Increases attack power by 56.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPainsaw; ++i;


var fGrandMarshalsMaul = new RewardItem("alliance","Grand Marshal's Maul","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsbonegrinder.gif");
fGrandMarshalsMaul.itemHonorPrice = new Array();
fGrandMarshalsMaul.itemHonorPrice[1] = 30600
fGrandMarshalsMaul.itemTokenPrice = new Array();
fGrandMarshalsMaul.itemTokenPrice[1] = new Array(40,0,0,0);
fGrandMarshalsMaul.itemStats = new Array();
fGrandMarshalsMaul.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Maul</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>158 - 294 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(62.9 damage per second)<br>+28 Strength<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br><span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br><span class=\"myGreen\">Equip: Increases attack power by 423 in Cat, Bear, Dire Bear, and Moonkin forms only.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsMaul; ++i;

var fGrandMarshalsHeavyCrossbow = new RewardItem("alliance","Grand Marshal's Heavy Crossbow","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsheavycrossbow.gif");
fGrandMarshalsHeavyCrossbow.itemHonorPrice = new Array();
fGrandMarshalsHeavyCrossbow.itemHonorPrice[1] = 20400
fGrandMarshalsHeavyCrossbow.itemTokenPrice = new Array();
fGrandMarshalsHeavyCrossbow.itemTokenPrice[1] = new Array(40,0,0,0);
fGrandMarshalsHeavyCrossbow.itemStats = new Array();
fGrandMarshalsHeavyCrossbow.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Heavy Crossbow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Crossbow</span>\
<br>170 - 255 Damage<span class=\"myRight\">Speed 3.20</span>\
<br>(66.4 damage per second)<br>+12 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 9.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br><span class=\"myGreen\">Equip: Increases ranged attack power by 22.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsHeavyCrossbow; ++i;

var fGrandMarshalsSlicer = new RewardItem("alliance","Grand Marshal's Slicer","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsswiftblade.gif");
fGrandMarshalsSlicer.itemHonorPrice = new Array();
fGrandMarshalsSlicer.itemHonorPrice[1] = 15300
fGrandMarshalsSlicer.itemTokenPrice = new Array();
fGrandMarshalsSlicer.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsSlicer.itemStats = new Array();
fGrandMarshalsSlicer.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Slicer</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>149 - 224 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br><span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br><span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSlicer; ++i;

var fGrandMarshalsQuickblade = new RewardItem("alliance","Grand Marshal's Quickblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsswiftblade.gif");
fGrandMarshalsQuickblade.itemHonorPrice = new Array();
fGrandMarshalsQuickblade.itemHonorPrice[1] = 15300
fGrandMarshalsQuickblade.itemTokenPrice = new Array();
fGrandMarshalsQuickblade.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsQuickblade.itemStats = new Array();
fGrandMarshalsQuickblade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Quickblade</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br><span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br><span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br><span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsQuickblade; ++i;

var fGrandMarshalsCleaver = new RewardItem("alliance","Grand Marshal's Cleaver","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalscleaver.gif");
fGrandMarshalsCleaver.itemHonorPrice = new Array();
fGrandMarshalsCleaver.itemHonorPrice[1] = 15300
fGrandMarshalsCleaver.itemTokenPrice = new Array();
fGrandMarshalsCleaver.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsCleaver.itemStats = new Array();
fGrandMarshalsCleaver.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Cleaver</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>149 - 224 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsCleaver; ++i;


var fGrandMarshalsHacker = new RewardItem("alliance","Grand Marshal's Hacker","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalscleaver.gif");
fGrandMarshalsHacker.itemHonorPrice = new Array();
fGrandMarshalsHacker.itemHonorPrice[1] = 15300
fGrandMarshalsHacker.itemTokenPrice = new Array();
fGrandMarshalsHacker.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsHacker.itemStats = new Array();
fGrandMarshalsHacker.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Hacker</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsHacker; ++i;

var fGrandMarshalsPummeler = new RewardItem("alliance","Grand Marshal's Pummeler","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalspummeler.gif");
fGrandMarshalsPummeler.itemHonorPrice = new Array();
fGrandMarshalsPummeler.itemHonorPrice[1] = 15300
fGrandMarshalsPummeler.itemTokenPrice = new Array();
fGrandMarshalsPummeler.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsPummeler.itemStats = new Array();
fGrandMarshalsPummeler.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Pummeler</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>149 - 224 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsPummeler; ++i;

var fGrandMarshalsBonecracker = new RewardItem("alliance","Grand Marshal's Bonecracker","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalspummeler.gif");
fGrandMarshalsBonecracker.itemHonorPrice = new Array();
fGrandMarshalsBonecracker.itemHonorPrice[1] = 15300
fGrandMarshalsBonecracker.itemTokenPrice = new Array();
fGrandMarshalsBonecracker.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsBonecracker.itemStats = new Array();
fGrandMarshalsBonecracker.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Bonecracker</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsBonecracker; ++i;

var fGrandMarshalsRightRipper = new RewardItem("alliance","Grand Marshal's Right Ripper","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsrightripper.gif");
fGrandMarshalsRightRipper.itemHonorPrice = new Array();
fGrandMarshalsRightRipper.itemHonorPrice[1] = 15300
fGrandMarshalsRightRipper.itemTokenPrice = new Array();
fGrandMarshalsRightRipper.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsRightRipper.itemStats = new Array();
fGrandMarshalsRightRipper.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Right Ripper</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Fist Weapon</span>\
<br>130 - 243 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsRightRipper; ++i;

var fGrandMarshalsLeftRipper = new RewardItem("alliance","Grand Marshal's Left Ripper","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsrightripper.gif");
fGrandMarshalsLeftRipper.itemHonorPrice = new Array();
fGrandMarshalsLeftRipper.itemHonorPrice[1] = 15300
fGrandMarshalsLeftRipper.itemTokenPrice = new Array();
fGrandMarshalsLeftRipper.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsLeftRipper.itemStats = new Array();
fGrandMarshalsLeftRipper.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Left Ripper</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Fist Weapon</span>\
<br>90 - 168 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsLeftRipper; ++i;

var fGrandMarshalsShanker = new RewardItem("alliance","Grand Marshal's Shanker","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsshanker.gif");
fGrandMarshalsShanker.itemHonorPrice = new Array();
fGrandMarshalsShanker.itemHonorPrice[1] = 15300
fGrandMarshalsShanker.itemTokenPrice = new Array();
fGrandMarshalsShanker.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsShanker.itemStats = new Array();
fGrandMarshalsShanker.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Shanker</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsShanker; ++i;

var fGrandMarshalsShiv = new RewardItem("alliance","Grand Marshal's Shiv","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsshanker.gif");
fGrandMarshalsShiv.itemHonorPrice = new Array();
fGrandMarshalsShiv.itemHonorPrice[1] = 15300
fGrandMarshalsShiv.itemTokenPrice = new Array();
fGrandMarshalsShiv.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsShiv.itemStats = new Array();
fGrandMarshalsShiv.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Shiv</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>80 - 121 Damage<span class=\"myRight\">Speed 1.40</span>\
<br>(71.8 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves hit rating by 8.</span><span class=\"myGreen\">\
<br>Equip: Improves critical strike rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsShiv; ++i;

var fGrandMarshalsWarStaff = new RewardItem("alliance","Grand Marshal's War Staff","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalswarstaff.gif");
fGrandMarshalsWarStaff.itemHonorPrice = new Array();
fGrandMarshalsWarStaff.itemHonorPrice[1] = 30600
fGrandMarshalsWarStaff.itemTokenPrice = new Array();
fGrandMarshalsWarStaff.itemTokenPrice[1] = new Array(40,0,0,0);
fGrandMarshalsWarStaff.itemStats = new Array();
fGrandMarshalsWarStaff.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's War Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>133 - 245 Damage<span class=\"myRight\">Speed 3.00</span>\
<br>(63.0 damage per second)<br>+40 Stamina<br>+30 Intellect<br>Durability 100 / 100<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves spell hit rating by 20.</span>\
<span class=\"myGreen\"><br>Equip: Improves spell critical strike rating by 30.</span>\
<span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 121.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsWarStaff; ++i;

var fGrandMarshalsSpellblade = new RewardItem("alliance","Grand Marshal's Spellblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdirk.gif");
fGrandMarshalsSpellblade.itemHonorPrice = new Array();
fGrandMarshalsSpellblade.itemHonorPrice[1] = 15300
fGrandMarshalsSpellblade.itemTokenPrice = new Array();
fGrandMarshalsSpellblade.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsSpellblade.itemStats = new Array();
fGrandMarshalsSpellblade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Spellblade</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Dagger</span>\
<br>31 - 101 Damage<span class=\"myRight\">Speed 1.60</span>\
<br>(41.3 damage per second)<br>+18 Stamina<br>+13 Intellect<br>Durability 65 / 65<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves Spell hit rating by 13.</span><span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 121.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsSpellblade; ++i;

var fGrandMarshalsBattletome = new RewardItem("alliance","Grand Marshal's Battletome","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalstomeofpower.gif");
fGrandMarshalsBattletome.itemHonorPrice = new Array();
fGrandMarshalsBattletome.itemHonorPrice[1] = 15300
fGrandMarshalsBattletome.itemTokenPrice = new Array();
fGrandMarshalsBattletome.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsBattletome.itemStats = new Array();
fGrandMarshalsBattletome.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Battletome</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+18 Stamina<br>+12 Intellect<br>Requires Level 70<span class=\"myGreen\">\
<br>Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsBattletome; ++i;

var fGrandMarshalsBarricade = new RewardItem("alliance","Grand Marshal's Barricade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsbarricade.gif");
fGrandMarshalsBarricade.itemHonorPrice = new Array();
fGrandMarshalsBarricade.itemHonorPrice[1] = 15300
fGrandMarshalsBarricade.itemTokenPrice = new Array();
fGrandMarshalsBarricade.itemTokenPrice[1] = new Array(0,0,20,0);
fGrandMarshalsBarricade.itemStats = new Array();
fGrandMarshalsBarricade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Grand Marshal's Barricade</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>3806 Armor<br>86 Block<br>+36 Stamina<br>Durability 100 / 100<br>Requires Level 70</span>\
<span class=\"myGreen\"><br>Equip: Improves your resilience rating by 23.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGrandMarshalsBarricade; ++i;



//-------------------------------------------------------------------
//---Horde below

var fHighWarlordsGreatsword = new RewardItem("horde","High Warlord's Greatsword","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsgreatsword.gif");
fHighWarlordsGreatsword.itemHonorPrice = new Array();
fHighWarlordsGreatsword.itemHonorPrice[0] = 30600
fHighWarlordsGreatsword.itemTokenPrice = new Array();
fHighWarlordsGreatsword.itemTokenPrice[0] = new Array(40,0,0,0);
fHighWarlordsGreatsword.itemStats = new Array();
fHighWarlordsGreatsword.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Greatsword</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Sword</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsGreatsword; ++i;

var fHighWarlordsBattleAxe = new RewardItem("horde","High Warlord's Battle Axe","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsbattleaxe.gif&reason=external-or-uncollected-resource");
fHighWarlordsBattleAxe.itemHonorPrice = new Array();
fHighWarlordsBattleAxe.itemHonorPrice[0] = 30600
fHighWarlordsBattleAxe.itemTokenPrice = new Array();
fHighWarlordsBattleAxe.itemTokenPrice[0] = new Array(40,0,0,0);
fHighWarlordsBattleAxe.itemStats = new Array();
fHighWarlordsBattleAxe.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Battle Axe</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Axe</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBattleAxe; ++i;

var fHighWarlordsPulverizer = new RewardItem("horde","High Warlord's Pulverizer","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordspulverizer.gif&reason=external-or-uncollected-resource");
fHighWarlordsPulverizer.itemHonorPrice = new Array();
fHighWarlordsPulverizer.itemHonorPrice[0] = 30600
fHighWarlordsPulverizer.itemTokenPrice = new Array();
fHighWarlordsPulverizer.itemTokenPrice[0] = new Array(40,0,0,0);
fHighWarlordsPulverizer.itemStats = new Array();
fHighWarlordsPulverizer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Pulverizer</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsPulverizer; ++i;

var fHighWarlordsDestroyer = new RewardItem("horde","High Warlord's Destroyer","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsdestroyer.gif&reason=external-or-uncollected-resource");
fHighWarlordsDestroyer.itemHonorPrice = new Array();
fHighWarlordsDestroyer.itemHonorPrice[0] = 30600
fHighWarlordsDestroyer.itemTokenPrice = new Array();
fHighWarlordsDestroyer.itemTokenPrice[0] = new Array(40,0,0,0);
fHighWarlordsDestroyer.itemStats = new Array();
fHighWarlordsDestroyer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Destroyer</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+28 Stamina<br>+27 Intellect<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDestroyer; ++i;


var fHighWarlordsPigSticker = new RewardItem("horde","High Warlord's Pig Sticker","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordspigsticker.gif&reason=external-or-uncollected-resource");
fHighWarlordsPigSticker.itemHonorPrice = new Array();
fHighWarlordsPigSticker.itemHonorPrice[0] = 30600
fHighWarlordsPigSticker.itemTokenPrice = new Array();
fHighWarlordsPigSticker.itemTokenPrice[0] = new Array(40,0,0,0);
fHighWarlordsPigSticker.itemStats = new Array();
fHighWarlordsPigSticker.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Pig Sticker</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>235 - 353 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(77.4 damage per second)<br>+26 Strength<br>+41 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsPigSticker; ++i;

var fHighWarlordsCleaver = new RewardItem("horde","High Warlord's Cleaver","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordscleaver.gif");
fHighWarlordsCleaver.itemHonorPrice = new Array();
fHighWarlordsCleaver.itemHonorPrice[0] = 15300
fHighWarlordsCleaver.itemTokenPrice = new Array();
fHighWarlordsCleaver.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsCleaver.itemStats = new Array();
fHighWarlordsCleaver.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Cleaver</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsCleaver; ++i;


var fHighWarlordsBlade = new RewardItem("horde","High Warlord's Blade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalslongsword.gif&reason=external-or-uncollected-resource");
fHighWarlordsBlade.itemHonorPrice = new Array();
fHighWarlordsBlade.itemHonorPrice[0] = 15300
fHighWarlordsBlade.itemTokenPrice = new Array();
fHighWarlordsBlade.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsBlade.itemStats = new Array();
fHighWarlordsBlade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Blade</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBlade; ++i;

var fHighWarlordsQuickblade = new RewardItem("horde","High Warlord's Quickblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsswiftblade.gif");
fHighWarlordsQuickblade.itemHonorPrice = new Array();
fHighWarlordsQuickblade.itemHonorPrice[0] = 15300
fHighWarlordsQuickblade.itemTokenPrice = new Array();
fHighWarlordsQuickblade.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsQuickblade.itemStats = new Array();
fHighWarlordsQuickblade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Quickblade</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>85 - 129 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(59.4 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsQuickblade; ++i;


var fHighWarlordsBludgeon = new RewardItem("horde","High Warlord's Bludgeon","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsbludgeon.gif&reason=external-or-uncollected-resource");
fHighWarlordsBludgeon.itemHonorPrice = new Array();
fHighWarlordsBludgeon.itemHonorPrice[0] = 15300
fHighWarlordsBludgeon.itemTokenPrice = new Array();
fHighWarlordsBludgeon.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsBludgeon.itemStats = new Array();
fHighWarlordsBludgeon.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Bludgeon</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBludgeon; ++i;

var fHighWarlordsBattleMace = new RewardItem("horde","High Warlord's Battle Mace","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalswarhammer.gif&reason=external-or-uncollected-resource");
fHighWarlordsBattleMace.itemHonorPrice = new Array();
fHighWarlordsBattleMace.itemHonorPrice[0] = 15300
fHighWarlordsBattleMace.itemTokenPrice = new Array();
fHighWarlordsBattleMace.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsBattleMace.itemStats = new Array();
fHighWarlordsBattleMace.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Battle Mace</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Mace</span>\
<br>68 - 173 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(41.7 damage per second)<br>+14 Stamina<br>+8 Intellect<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 134.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBattleMace; ++i;

var fHighWarlordsRightClaw = new RewardItem("horde","High Warlord's Right Claw","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsrightclaw.gif&reason=external-or-uncollected-resource");
fHighWarlordsRightClaw.itemHonorPrice = new Array();
fHighWarlordsRightClaw.itemHonorPrice[0] = 15300
fHighWarlordsRightClaw.itemTokenPrice = new Array();
fHighWarlordsRightClaw.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsRightClaw.itemStats = new Array();
fHighWarlordsRightClaw.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Right Claw</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Fist Weapon</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsRightClaw; ++i;

var fHighWarlordsLeftClaw = new RewardItem("horde","High Warlord's Left Claw","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsleftclaw.gif&reason=external-or-uncollected-resource");
fHighWarlordsLeftClaw.itemHonorPrice = new Array();
fHighWarlordsLeftClaw.itemHonorPrice[0] = 15300
fHighWarlordsLeftClaw.itemTokenPrice = new Array();
fHighWarlordsLeftClaw.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsLeftClaw.itemStats = new Array();
fHighWarlordsLeftClaw.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Left Claw</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Fist Weapon</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsLeftClaw; ++i;


var fHighWarlordsRazor = new RewardItem("horde","High Warlord's Razor","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsrazor.gif&reason=external-or-uncollected-resource");
fHighWarlordsRazor.itemHonorPrice = new Array();
fHighWarlordsRazor.itemHonorPrice[0] = 15300
fHighWarlordsRazor.itemTokenPrice = new Array();
fHighWarlordsRazor.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsRazor.itemStats = new Array();
fHighWarlordsRazor.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Razor</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>95 - 143 Damage<span class=\"myRight\">Speed 2.00</span>\
<br>(59.5 damage per second)<br>+7 Stamina<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsRazor; ++i;

var fHighWarlordsShieldWall = new RewardItem("horde","High Warlord's Shield Wall","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsbarricade.gif");
fHighWarlordsShieldWall.itemHonorPrice = new Array();
fHighWarlordsShieldWall.itemHonorPrice[0] = 15300
fHighWarlordsShieldWall.itemTokenPrice = new Array();
fHighWarlordsShieldWall.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsShieldWall.itemStats = new Array();
fHighWarlordsShieldWall.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Shield Wall</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>3366 Armor<br>73 Block<br>+10 Strength<br>+23 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: When struck in combat has a 5% chance of inflicting 35 to 65 Nature damage to the attacker.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsShieldWall; ++i;

var fHighWarlordsRecurve = new RewardItem("horde","High Warlord's Recurve","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsrecurve.gif&reason=external-or-uncollected-resource");
fHighWarlordsRecurve.itemHonorPrice = new Array();
fHighWarlordsRecurve.itemHonorPrice[0] = 15300
fHighWarlordsRecurve.itemTokenPrice = new Array();
fHighWarlordsRecurve.itemTokenPrice[0] = new Array(0,40,0,0);
fHighWarlordsRecurve.itemStats = new Array();
fHighWarlordsRecurve.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Recurve</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>80 - 121 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(55.8 damage per second)<br>+7 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 36.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsRecurve; ++i;

var fHighWarlordsCrossbow = new RewardItem("horde","High Warlord's Crossbow","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsheavycrossbow.gif");
fHighWarlordsCrossbow.itemHonorPrice = new Array();
fHighWarlordsCrossbow.itemHonorPrice[0] = 15300
fHighWarlordsCrossbow.itemTokenPrice = new Array();
fHighWarlordsCrossbow.itemTokenPrice[0] = new Array(0,40,0,0);
fHighWarlordsCrossbow.itemStats = new Array();
fHighWarlordsCrossbow.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Crossbow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Crossbow</span>\
<br>129 - 195 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(55.9 damage per second)<br>+7 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 36.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsCrossbow; ++i;

var fHighWarlordsStreetSweeper = new RewardItem("horde","High Warlord's Street Sweeper","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordsstreetsweeper.gif&reason=external-or-uncollected-resource");
fHighWarlordsStreetSweeper.itemHonorPrice = new Array();
fHighWarlordsStreetSweeper.itemHonorPrice[0] = 15300
fHighWarlordsStreetSweeper.itemTokenPrice = new Array();
fHighWarlordsStreetSweeper.itemTokenPrice[0] = new Array(0,40,0,0);
fHighWarlordsStreetSweeper.itemStats = new Array();
fHighWarlordsStreetSweeper.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Street Sweeper</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Gun</span>\
<br>129 - 195 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(55.9 damage per second)<br>+7 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 36.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsStreetSweeper; ++i;

var fHighWarlordsWarStaff = new RewardItem("horde","High Warlord's War Staff","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordswarstaff.gif");
fHighWarlordsWarStaff.itemHonorPrice = new Array();
fHighWarlordsWarStaff.itemHonorPrice[0] = 30600
fHighWarlordsWarStaff.itemTokenPrice = new Array();
fHighWarlordsWarStaff.itemTokenPrice[0] = new Array(40,0,0,0);
fHighWarlordsWarStaff.itemStats = new Array();
fHighWarlordsWarStaff.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's War Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>131 - 225 Damage<span class=\"myRight\">Speed 3.00</span>\
<br>(59.3 damage per second)<br>+41 Stamina<br>+23 Intellect<br>+17 Spirit<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 71.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsWarStaff; ++i;

var fHighWarlordsSpellblade = new RewardItem("horde","High Warlord's Spellblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdirk.gif");
fHighWarlordsSpellblade.itemHonorPrice = new Array();
fHighWarlordsSpellblade.itemHonorPrice[0] = 15300
fHighWarlordsSpellblade.itemTokenPrice = new Array();
fHighWarlordsSpellblade.itemTokenPrice[0] = new Array(0,20,0,0);
fHighWarlordsSpellblade.itemStats = new Array();
fHighWarlordsSpellblade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Spellblade</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Dagger</span>\
<br>47 - 119 Damage<span class=\"myRight\">Speed 2.00</span>\
<br>(41.5 damage per second)<br>+14 Stamina<br>+8 Intellect<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 72.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsSpellblade; ++i;

var fHighWarlordsTomeOfDestruction = new RewardItem("horde","High Warlord's Tome of Destruction","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordstomeofd.gif&reason=external-or-uncollected-resource");
fHighWarlordsTomeOfDestruction.itemHonorPrice = new Array();
fHighWarlordsTomeOfDestruction.itemHonorPrice[0] = 15300
fHighWarlordsTomeOfDestruction.itemTokenPrice = new Array();
fHighWarlordsTomeOfDestruction.itemTokenPrice[0] = new Array(0,40,0,0);
fHighWarlordsTomeOfDestruction.itemStats = new Array();
fHighWarlordsTomeOfDestruction.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Tome of Destruction</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+17 Stamina<br>+16 Intellect<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsTomeOfDestruction; ++i;

var fHighWarlordsTomeOfMending = new RewardItem("horde","High Warlord's Tome of Mending","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Frewards-weapons.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fhighwarlordstomeofmending.gif&reason=external-or-uncollected-resource");
fHighWarlordsTomeOfMending.itemHonorPrice = new Array();
fHighWarlordsTomeOfMending.itemHonorPrice[0] = 15300
fHighWarlordsTomeOfMending.itemTokenPrice = new Array();
fHighWarlordsTomeOfMending.itemTokenPrice[0] = new Array(0,40,0,0);
fHighWarlordsTomeOfMending.itemStats = new Array();
fHighWarlordsTomeOfMending.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">High Warlord's Tome of Mending</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+14 Stamina<br>+14 Intellect<br>+14 Spirit<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 31.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsTomeOfMending; ++i;

var fHighWarlordsClaymore = new RewardItem("horde","High Warlord's Claymore","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsgreatsword.gif");
fHighWarlordsClaymore.itemHonorPrice = new Array();
fHighWarlordsClaymore.itemHonorPrice[1] = 30600
fHighWarlordsClaymore.itemTokenPrice = new Array();
fHighWarlordsClaymore.itemTokenPrice[1] = new Array(40,0,0,0);
fHighWarlordsClaymore.itemStats = new Array();
fHighWarlordsClaymore.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Claymore</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Sword</span>\
<br>268 - 403 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(93.2 damage per second)<br>+28 Strength<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsClaymore; ++i;

var fHighWarlordsDecapitator = new RewardItem("horde","High Warlord's Decapitator","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdecapitator.gif");
fHighWarlordsDecapitator.itemHonorPrice = new Array();
fHighWarlordsDecapitator.itemHonorPrice[1] = 30600
fHighWarlordsDecapitator.itemTokenPrice = new Array();
fHighWarlordsDecapitator.itemTokenPrice[1] = new Array(40,0,0,0);
fHighWarlordsDecapitator.itemStats = new Array();
fHighWarlordsDecapitator.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Decapitator</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Axe</span>\
<br>268 - 403 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(93.2 damage per second)<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 56.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsDecapitator; ++i;

var fHighWarlordsBonegrinder = new RewardItem("horde","High Warlord's Bonegrinder","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsbonegrinder.gif");
fHighWarlordsBonegrinder.itemHonorPrice = new Array();
fHighWarlordsBonegrinder.itemHonorPrice[1] = 30600
fHighWarlordsBonegrinder.itemTokenPrice = new Array();
fHighWarlordsBonegrinder.itemTokenPrice[1] = new Array(40,0,0,0);
fHighWarlordsBonegrinder.itemStats = new Array();
fHighWarlordsBonegrinder.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Bonegrinder</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>268 - 403 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(93.2 damage per second)<br>+28 Strength<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBonegrinder; ++i;

var fHighWarlordsPainsaw = new RewardItem("horde","High Warlord's Painsaw","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalspainsaw.gif");
fHighWarlordsPainsaw.itemHonorPrice = new Array();
fHighWarlordsPainsaw.itemHonorPrice[1] = 30600
fHighWarlordsPainsaw.itemTokenPrice = new Array();
fHighWarlordsPainsaw.itemTokenPrice[1] = new Array(40,0,0,0);
fHighWarlordsPainsaw.itemStats = new Array();
fHighWarlordsPainsaw.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Painsaw</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>164 - 246 Damage<span class=\"myRight\">Speed 2.20</span>\
<br>(93.2 damage per second)<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 56.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsPainsaw; ++i;

var fHighWarlordsMaul = new RewardItem("horde","High Warlord's Maul","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsbonegrinder.gif");
fHighWarlordsMaul.itemHonorPrice = new Array();
fHighWarlordsMaul.itemHonorPrice[1] = 30600
fHighWarlordsMaul.itemTokenPrice = new Array();
fHighWarlordsMaul.itemTokenPrice[1] = new Array(40,0,0,0);
fHighWarlordsMaul.itemStats = new Array();
fHighWarlordsMaul.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Maul</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>158 - 294 Damage<span class=\"myRight\">Speed 3.60</span>\
<br>(62.9 damage per second)<br>+28 Strength<br>+42 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 423 in Cat, Bear, Dire Bear, and Moonkin forms only.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsMaul; ++i;

var fHighWarlordsHeavyCrossbow = new RewardItem("horde","High Warlord's Heavy Crossbow","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsheavycrossbow.gif");
fHighWarlordsHeavyCrossbow.itemHonorPrice = new Array();
fHighWarlordsHeavyCrossbow.itemHonorPrice[1] = 20400
fHighWarlordsHeavyCrossbow.itemTokenPrice = new Array();
fHighWarlordsHeavyCrossbow.itemTokenPrice[1] = new Array(40,0,0,0);
fHighWarlordsHeavyCrossbow.itemStats = new Array();
fHighWarlordsHeavyCrossbow.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Heavy Crossbow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Crossbow</span>\
<br>170 - 255 Damage<span class=\"myRight\">Speed 3.20</span>\
<br>(66.4 damage per second)<br>+12 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases ranged attack power by 22.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsHeavyCrossbow; ++i;

var fHighWarlordsSlicer = new RewardItem("horde","High Warlord's Slicer","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsslicer.gif");
fHighWarlordsSlicer.itemHonorPrice = new Array();
fHighWarlordsSlicer.itemHonorPrice[1] = 15300
fHighWarlordsSlicer.itemTokenPrice = new Array();
fHighWarlordsSlicer.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsSlicer.itemStats = new Array();
fHighWarlordsSlicer.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Slicer</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>149 - 224 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsSlicer; ++i;

var fHighWarlordsQuickblade = new RewardItem("horde","High Warlord's Quickblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsslicer.gif");
fHighWarlordsQuickblade.itemHonorPrice = new Array();
fHighWarlordsQuickblade.itemHonorPrice[1] = 15300
fHighWarlordsQuickblade.itemTokenPrice = new Array();
fHighWarlordsQuickblade.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsQuickblade.itemStats = new Array();
fHighWarlordsQuickblade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Quickblade</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsQuickblade; ++i;

var fHighWarlordsCleaver = new RewardItem("horde","High Warlord's Cleaver","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordscleaver.gif");
fHighWarlordsCleaver.itemHonorPrice = new Array();
fHighWarlordsCleaver.itemHonorPrice[1] = 15300
fHighWarlordsCleaver.itemTokenPrice = new Array();
fHighWarlordsCleaver.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsCleaver.itemStats = new Array();
fHighWarlordsCleaver.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Cleaver</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>149 - 224 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsCleaver; ++i;

var fHighWarlordsHacker = new RewardItem("horde","High Warlord's Hacker","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordscleaver.gif");
fHighWarlordsHacker.itemHonorPrice = new Array();
fHighWarlordsHacker.itemHonorPrice[1] = 15300
fHighWarlordsHacker.itemTokenPrice = new Array();
fHighWarlordsHacker.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsHacker.itemStats = new Array();
fHighWarlordsHacker.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Hacker</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsHacker; ++i;

var fHighWarlordsPummeler = new RewardItem("horde","High Warlord's Pummeler","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalspummeler.gif");
fHighWarlordsPummeler.itemHonorPrice = new Array();
fHighWarlordsPummeler.itemHonorPrice[1] = 15300
fHighWarlordsPummeler.itemTokenPrice = new Array();
fHighWarlordsPummeler.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsPummeler.itemStats = new Array();
fHighWarlordsPummeler.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Pummeler</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>149 - 224 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsPummeler; ++i;

var fHighWarlordsBonecracker = new RewardItem("horde","High Warlord's Bonecracker","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalspummeler.gif");
fHighWarlordsBonecracker.itemHonorPrice = new Array();
fHighWarlordsBonecracker.itemHonorPrice[1] = 15300
fHighWarlordsBonecracker.itemTokenPrice = new Array();
fHighWarlordsBonecracker.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsBonecracker.itemStats = new Array();
fHighWarlordsBonecracker.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Bonecracker</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBonecracker; ++i;

var fHighWarlordsRightRipper = new RewardItem("horde","High Warlord's Right Ripper","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsrightripper.gif");
fHighWarlordsRightRipper.itemHonorPrice = new Array();
fHighWarlordsRightRipper.itemHonorPrice[1] = 15300
fHighWarlordsRightRipper.itemTokenPrice = new Array();
fHighWarlordsRightRipper.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsRightRipper.itemStats = new Array();
fHighWarlordsRightRipper.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Right Ripper</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Fist Weapon</span>\
<br>130 - 243 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsRightRipper; ++i;

var fHighWarlordsLeftRipper = new RewardItem("horde","High Warlord's Left Ripper","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsrightripper.gif");
fHighWarlordsLeftRipper.itemHonorPrice = new Array();
fHighWarlordsLeftRipper.itemHonorPrice[1] = 15300
fHighWarlordsLeftRipper.itemTokenPrice = new Array();
fHighWarlordsLeftRipper.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsLeftRipper.itemStats = new Array();
fHighWarlordsLeftRipper.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Left Ripper</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Fist Weapon</span>\
<br>90 - 168 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsLeftRipper; ++i;

var fHighWarlordsShanker = new RewardItem("horde","High Warlord's Shanker","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsshanker.gif");
fHighWarlordsShanker.itemHonorPrice = new Array();
fHighWarlordsShanker.itemHonorPrice[1] = 15300
fHighWarlordsShanker.itemTokenPrice = new Array();
fHighWarlordsShanker.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsShanker.itemStats = new Array();
fHighWarlordsShanker.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Shanker</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>103 - 155 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(71.7 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsShanker; ++i;

var fHighWarlordsShiv = new RewardItem("horde","High Warlord's Shiv","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsshanker.gif");
fHighWarlordsShiv.itemHonorPrice = new Array();
fHighWarlordsShiv.itemHonorPrice[1] = 15300
fHighWarlordsShiv.itemTokenPrice = new Array();
fHighWarlordsShiv.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsShiv.itemStats = new Array();
fHighWarlordsShiv.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Shiv</span>\
<br>Binds when picked up<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>80 - 121 Damage<span class=\"myRight\">Speed 1.40</span>\
<br>(71.8 damage per second)<br>+18 Stamina<br>Durability 65 / 65<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 26.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsShiv; ++i;


var fHighWarlordsWarStaff = new RewardItem("horde","High Warlord's War Staff","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordswarstaff.gif");
fHighWarlordsWarStaff.itemHonorPrice = new Array();
fHighWarlordsWarStaff.itemHonorPrice[1] = 30600
fHighWarlordsWarStaff.itemTokenPrice = new Array();
fHighWarlordsWarStaff.itemTokenPrice[1] = new Array(40,0,0,0);
fHighWarlordsWarStaff.itemStats = new Array();
fHighWarlordsWarStaff.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's War Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>133 - 245 Damage<span class=\"myRight\">Speed 3.00</span>\
<br>(63.0 damage per second)<br>+40 Stamina<br>+30 Intellect<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 121.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsWarStaff; ++i;

var fHighWarlordsSpellblade = new RewardItem("horde","High Warlord's Spellblade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsdirk.gif");
fHighWarlordsSpellblade.itemHonorPrice = new Array();
fHighWarlordsSpellblade.itemHonorPrice[1] = 15300
fHighWarlordsSpellblade.itemTokenPrice = new Array();
fHighWarlordsSpellblade.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsSpellblade.itemStats = new Array();
fHighWarlordsSpellblade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Spellblade</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Dagger</span>\
<br>31 - 101 Damage<span class=\"myRight\">Speed 1.60</span>\
<br>(41.3 damage per second)<br>+18 Stamina<br>+13 Intellect<br>Durability 65 / 65<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 121.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsSpellblade; ++i;


var fHighWarlordsBattletome = new RewardItem("horde","High Warlord's Battletome","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/highwarlordsbattletome.gif");
fHighWarlordsBattletome.itemHonorPrice = new Array();
fHighWarlordsBattletome.itemHonorPrice[1] = 15300
fHighWarlordsBattletome.itemTokenPrice = new Array();
fHighWarlordsBattletome.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsBattletome.itemStats = new Array();
fHighWarlordsBattletome.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Battletome</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+18 Stamina<br>+12 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBattletome; ++i;

var fHighWarlordsBarricade = new RewardItem("horde","High Warlord's Barricade","/WOW-Encyclopedia-Deployable-Archive/pvp/images/honorweapons/grandmarshalsbarricade.gif");
fHighWarlordsBarricade.itemHonorPrice = new Array();
fHighWarlordsBarricade.itemHonorPrice[1] = 15300
fHighWarlordsBarricade.itemTokenPrice = new Array();
fHighWarlordsBarricade.itemTokenPrice[1] = new Array(0,0,20,0);
fHighWarlordsBarricade.itemStats = new Array();
fHighWarlordsBarricade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">High Warlord's Barricade</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>3806 Armor<br>86 Block<br>+36 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighWarlordsBarricade; ++i;


//------END REWARDS DEFINITION------
