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
		if (goldPart > 0) outPutString += goldPart+"<img src='/shared/wow-com/images/basics/factions/gold.gif'>&nbsp;";
		if (silverPart > 0) outPutString += silverPart+"<img src='/shared/wow-com/images/basics/factions/silver.gif'>&nbsp;";
		if (copperPart > 0) outPutString += copperPart+"<img src='/shared/wow-com/images/basics/factions/copper.gif'>&nbsp;";
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

var fRuneOfPerfection = new RewardItem("alliance","Rune of Perfection","/shared/wow-com/images/basics/factions/warsong/rune01.gif");
fRuneOfPerfection.itemHonorPrice = new Array();
fRuneOfPerfection.itemHonorPrice[1] = 174
fRuneOfPerfection.itemTokenPrice = new Array();
fRuneOfPerfection.itemTokenPrice[1] = new Array(0,0,0,30);
fRuneOfPerfection.itemStats = new Array();
fRuneOfPerfection.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Rune of Perfection</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+4 Stamina<br>Classes: Priest, Shaman, Mage, Warlock, Druid<br>Requires Level 20<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 10.</span>\
</div>\
</td>\
</tr>\
</table>\
";
fRuneOfPerfection.itemHonorPrice[3] = 380
fRuneOfPerfection.itemTokenPrice[3] = new Array(0,0,0,30);
fRuneOfPerfection.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Rune of Perfection</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+7 Stamina<br>Classes: Priest, Shaman, Mage, Warlock, Druid<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRuneOfPerfection; ++i;

var fRuneOfDuty = new RewardItem("alliance","Rune of Duty","/shared/wow-com/images/basics/factions/warsong/rune02.gif");
fRuneOfDuty.itemHonorPrice = new Array();
fRuneOfDuty.itemHonorPrice[1] = 174
fRuneOfDuty.itemTokenPrice = new Array();
fRuneOfDuty.itemTokenPrice[1] = new Array(0,0,0,30);
fRuneOfDuty.itemStats = new Array();
fRuneOfDuty.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Rune of Duty</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+4 Stamina<br>Classes: Warrior, Paladin, Hunter, Rogue<br>Requires Level 20<br>\
<span class=\"myGreen\">Equip: Restores 3 health per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fRuneOfDuty.itemHonorPrice[3] = 380
fRuneOfDuty.itemTokenPrice[3] = new Array(0,0,0,30);
fRuneOfDuty.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Rune of Duty</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+7 Stamina<br>Classes: Warrior, Paladin, Hunter, Rogue<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Restores 6 health per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRuneOfDuty; ++i;


var fWarsongGulchFieldRation = new RewardItem("alliance","Warsong Gulch Field Ration","/shared/wow-com/images/basics/factions/warsong/fieldration.gif");
fWarsongGulchFieldRation.itemMoneyPrice = new Array();
fWarsongGulchFieldRation.itemMoneyPrice[1] = 1000
fWarsongGulchFieldRation.itemStats = new Array();
fWarsongGulchFieldRation.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Field Ration<br>Binds when picked up<br>Requires Level 25<br>\
<span class=\"myGreen\">Use: Restores 1074 health and 2202 mana over 30 sec.  Must remain seated while eating.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchFieldRation; ++i;


var fWarsongGulchIronRation = new RewardItem("alliance","Warsong Gulch Iron Ration","/shared/wow-com/images/basics/factions/warsong/ironration.gif");
fWarsongGulchIronRation.itemMoneyPrice = new Array();
fWarsongGulchIronRation.itemMoneyPrice[2] = 1500
fWarsongGulchIronRation.itemStats = new Array();
fWarsongGulchIronRation.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Iron Ration<br>Binds when picked up<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 1608 health and 3306 mana over 30 sec.  Must remain seated while eating.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchIronRation; ++i;


var fWarsongGulchEnrichedRation = new RewardItem("alliance","Warsong Gulch Enriched Ration","/shared/wow-com/images/basics/factions/warsong/enrichedration.gif");
fWarsongGulchEnrichedRation.itemMoneyPrice = new Array();
fWarsongGulchEnrichedRation.itemMoneyPrice[3] = 2000
fWarsongGulchEnrichedRation.itemStats = new Array();
fWarsongGulchEnrichedRation.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Enriched Ration<br>Binds when picked up<br>Requires Level 45<br>\
<span class=\"myGreen\">Use: Restores 2148 health and 4410 mana over 30 sec.  Must remain seated while eating.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchEnrichedRation; ++i;







var fWarsongGulchSilkBandage = new RewardItem("alliance","Warsong Gulch Silk Bandage","/shared/wow-com/images/basics/factions/warsong/silkbandage.gif");
fWarsongGulchSilkBandage.itemMoneyPrice = new Array();
fWarsongGulchSilkBandage.itemMoneyPrice[1] = 1000
fWarsongGulchSilkBandage.itemStats = new Array();
fWarsongGulchSilkBandage.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Silk Bandage<br>Binds when picked up<br>Requires Level 25<br>Requires First Aid (125)<br>\
<span class=\"myGreen\">Use: Heals 640 damage over 8 sec.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchSilkBandage; ++i;


var fWarsongGulchMageweaveBandage = new RewardItem("alliance","Warsong Gulch Mageweave Bandage","/shared/wow-com/images/basics/factions/warsong/mageweavebandage.gif");
fWarsongGulchMageweaveBandage.itemMoneyPrice = new Array();
fWarsongGulchMageweaveBandage.itemMoneyPrice[2] = 1500
fWarsongGulchMageweaveBandage.itemStats = new Array();
fWarsongGulchMageweaveBandage.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Mageweave Bandage<br>Binds when picked up<br>Requires Level 35<br>Requires First Aid (175)<br>\
<span class=\"myGreen\">Use: Heals 1104 damage over 8 sec.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchMageweaveBandage; ++i;


var fWarsongGulchRuneclothBandage = new RewardItem("alliance","Warsong Gulch Runecloth Bandage","/shared/wow-com/images/basics/factions/warsong/runeclothbandage.gif");
fWarsongGulchRuneclothBandage.itemMoneyPrice = new Array();
fWarsongGulchRuneclothBandage.itemMoneyPrice[3] = 2000
fWarsongGulchRuneclothBandage.itemStats = new Array();
fWarsongGulchRuneclothBandage.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Runecloth Bandage<br>Binds when picked up<br>Requires Level 45<br>Requires First Aid (225)<br>\
<span class=\"myGreen\">Use: Heals 2000 damage over 8 sec.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchRuneclothBandage; ++i;



var fSuperiorHealingDraught = new RewardItem("alliance","Superior Healing Draught","/shared/wow-com/images/basics/factions/warsong/health02.gif");
fSuperiorHealingDraught.itemMoneyPrice = new Array();
fSuperiorHealingDraught.itemMoneyPrice[2] = 500
fSuperiorHealingDraught.itemHonorPrice = new Array();
fSuperiorHealingDraught.itemHonorPrice[2] = 6
fSuperiorHealingDraught.itemStats = new Array();
fSuperiorHealingDraught.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Superior Healing Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 560 to 720 health. This item may only be used in PvP Battlegrounds.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSuperiorHealingDraught; ++i;


var fSuperiorManaDraught = new RewardItem("alliance","Superior Mana Draught","/shared/wow-com/images/basics/factions/warsong/mana02.gif");
fSuperiorManaDraught.itemMoneyPrice = new Array();
fSuperiorManaDraught.itemMoneyPrice[2] = 500
fSuperiorManaDraught.itemHonorPrice = new Array();
fSuperiorManaDraught.itemHonorPrice[2] = 6
fSuperiorManaDraught.itemStats = new Array();
fSuperiorManaDraught.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Superior Mana Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 560 to 720 mana. This item may only be used in PvP Battlegrounds.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSuperiorManaDraught; ++i;








var fCaretakersCape = new RewardItem("alliance","Caretaker's Cape","/shared/wow-com/images/basics/factions/warsong/cape_a.gif");
fCaretakersCape.itemHonorPrice = new Array();
fCaretakersCape.itemHonorPrice[0] = 95
fCaretakersCape.itemTokenPrice = new Array();
fCaretakersCape.itemTokenPrice[0] = new Array(0,0,0,10);
fCaretakersCape.itemStats = new Array();
fCaretakersCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Caretaker's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br>20 Armor<br>+4 Stamina<br>+2 Spirit<br>Requires Level 18<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 9.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fCaretakersCape.itemHonorPrice[1] = 140
fCaretakersCape.itemTokenPrice[1] = new Array(0,0,0,10);
fCaretakersCape.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Caretaker's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br>25 Armor<br>+6 Stamina<br>+4 Spirit<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 13.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fCaretakersCape.itemHonorPrice[2] = 207
fCaretakersCape.itemTokenPrice[2] = new Array(0,0,0,10);
fCaretakersCape.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Caretaker's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br>31 Armor<br>+8 Stamina<br>+5 Spirit<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fCaretakersCape.itemHonorPrice[3] = 306
fCaretakersCape.itemTokenPrice[3] = new Array(0,0,0,10);
fCaretakersCape.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Caretaker's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br>38 Armor<br>+9 Stamina<br>+6 Spirit<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 22.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fCaretakersCape.itemHonorPrice[4] = 2250
fCaretakersCape.itemTokenPrice[4] = new Array(0,0,0,10);
fCaretakersCape.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Caretaker's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br>45 Armor<br>+11 Stamina<br>+8 Spirit<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 26.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCaretakersCape; i++;






var fLorekeepersRing = new RewardItem("alliance","Lorekeeper's Ring","/shared/wow-com/images/basics/factions/warsong/ring02.gif");
fLorekeepersRing.itemHonorPrice = new Array();
fLorekeepersRing.itemHonorPrice[0] = 95
fLorekeepersRing.itemTokenPrice = new Array();
fLorekeepersRing.itemTokenPrice[0] = new Array(0,0,0,20);
fLorekeepersRing.itemStats = new Array();
fLorekeepersRing.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+2 Stamina<br>Requires Level 18<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 5.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersRing.itemHonorPrice[1] = 140
fLorekeepersRing.itemTokenPrice[1] = new Array(0,0,0,20);
fLorekeepersRing.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+4 Stamina<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 7.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersRing.itemHonorPrice[2] = 207
fLorekeepersRing.itemTokenPrice[2] = new Array(0,0,0,20);
fLorekeepersRing.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+5 Stamina<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersRing.itemHonorPrice[3] = 306
fLorekeepersRing.itemTokenPrice[3] = new Array(0,0,0,20);
fLorekeepersRing.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+6 Stamina<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersRing.itemHonorPrice[4] = 2250
fLorekeepersRing.itemTokenPrice[4] = new Array(0,0,0,20);
fLorekeepersRing.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+8 Stamina<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLorekeepersRing; ++i;



var fSentinelsMedallion = new RewardItem("alliance","Sentinel's Medallion","/shared/wow-com/images/basics/factions/warsong/medallion_a.gif");
fSentinelsMedallion.itemHonorPrice = new Array();
fSentinelsMedallion.itemHonorPrice[0] = 95
fSentinelsMedallion.itemTokenPrice = new Array();
fSentinelsMedallion.itemTokenPrice[0] = new Array(0,0,0,20);
fSentinelsMedallion.itemStats = new Array();
fSentinelsMedallion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Sentinel's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+6 Agility<br>+2 Stamina<br>Requires Level 18</span>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsMedallion.itemHonorPrice[1] = 140
fSentinelsMedallion.itemTokenPrice[1] = new Array(0,0,0,20);
fSentinelsMedallion.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Sentinel's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+8 Agility<br>+5 Stamina<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsMedallion.itemHonorPrice[2] = 207
fSentinelsMedallion.itemTokenPrice[2] = new Array(0,0,0,20);
fSentinelsMedallion.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Sentinel's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+11 Agility<br>+7 Stamina<br>Requires Level 38</span>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsMedallion.itemHonorPrice[3] = 306
fSentinelsMedallion.itemTokenPrice[3] = new Array(0,0,0,20);
fSentinelsMedallion.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Sentinel's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+12 Agility<br>+8 Stamina<br>Requires Level 48</span>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsMedallion.itemHonorPrice[4] = 2250
fSentinelsMedallion.itemTokenPrice[4] = new Array(0,0,0,20);
fSentinelsMedallion.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Sentinel's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+15 Agility<br>+10 Stamina<br>Requires Level 58</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsMedallion; ++i;





var fProtectorsBand = new RewardItem("alliance","Protector's Band","/shared/wow-com/images/basics/factions/warsong/ring01.gif");
fProtectorsBand.itemHonorPrice = new Array();
fProtectorsBand.itemHonorPrice[0] = 95
fProtectorsBand.itemTokenPrice = new Array();
fProtectorsBand.itemTokenPrice[0] = new Array(0,0,0,20);
fProtectorsBand.itemStats = new Array();
fProtectorsBand.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Protector's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+4 Strength<br>+4 Agility<br>+2 Stamina<br>Requires Level 18</span>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsBand.itemHonorPrice[1] = 140
fProtectorsBand.itemTokenPrice[1] = new Array(0,0,0,20);
fProtectorsBand.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Protector's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+6 Strength<br>+6 Agility<br>+4 Stamina<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsBand.itemHonorPrice[2] = 207
fProtectorsBand.itemTokenPrice[2] = new Array(0,0,0,20);
fProtectorsBand.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Protector's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+8 Strength<br>+8 Agility<br>+5 Stamina<br>Requires Level 38</span>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsBand.itemHonorPrice[3] = 306
fProtectorsBand.itemTokenPrice[3] = new Array(0,0,0,20);
fProtectorsBand.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Protector's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+10 Strength<br>+9 Agility<br>+6 Stamina<br>Requires Level 48</span>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsBand.itemHonorPrice[4] = 2250
fProtectorsBand.itemTokenPrice[4] = new Array(0,0,0,20);
fProtectorsBand.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Protector's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+12 Strength<br>+11 Agility<br>+8 Stamina<br>Requires Level 58</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fProtectorsBand; ++i;



var fMajorHealingDraught = new RewardItem("alliance","Major Healing Draught","/shared/wow-com/images/basics/factions/warsong/health01.gif");
fMajorHealingDraught.itemMoneyPrice = new Array();
fMajorHealingDraught.itemMoneyPrice[3] = 1000
fMajorHealingDraught.itemHonorPrice = new Array();
fMajorHealingDraught.itemHonorPrice[3] = 3
fMajorHealingDraught.itemStats = new Array();
fMajorHealingDraught.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Major Healing Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 45<br>\
<span class=\"myGreen\">Use: Restores 980 to 1260 health. This item may only be used in PvP Battlegrounds.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorHealingDraught; ++i;

var fMajorManaDraught = new RewardItem("alliance","Major Mana Draught","/shared/wow-com/images/basics/factions/warsong/mana01.gif");
fMajorManaDraught.itemMoneyPrice = new Array();
fMajorManaDraught.itemMoneyPrice[3] = 1000
fMajorManaDraught.itemHonorPrice = new Array();
fMajorManaDraught.itemHonorPrice[3] = 3
fMajorManaDraught.itemStats = new Array();
fMajorManaDraught.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Mana Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 45<br>\
<span class=\"myGreen\">Use: Restores 980 to 1260 mana. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorManaDraught; ++i;













var fLorekeepersStaff = new RewardItem("alliance","Lorekeeper's Staff","/shared/wow-com/images/basics/factions/warsong/staff_a.gif");
fLorekeepersStaff.itemHonorPrice = new Array();
fLorekeepersStaff.itemHonorPrice[0] = 630
fLorekeepersStaff.itemTokenPrice = new Array();
fLorekeepersStaff.itemTokenPrice[0] = new Array(0,0,0,40);
fLorekeepersStaff.itemStats = new Array();
fLorekeepersStaff.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>45 - 69 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(19.7 damage per second)<br>+8 Stamina<br>+4 Intellect<br>Durability 80 / 80<br>Requires Level 18<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersStaff.itemHonorPrice[1] = 930
fLorekeepersStaff.itemTokenPrice[1] = new Array(0,0,0,40);
fLorekeepersStaff.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>64 - 97 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(27.8 damage per second)<br>+11 Stamina<br>+7 Intellect<br>Durability 100 / 100<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersStaff.itemHonorPrice[2] = 1380
fLorekeepersStaff.itemTokenPrice[2] = new Array(0,0,0,40);
fLorekeepersStaff.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>88 - 133 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(38.1 damage per second)<br>+14 Stamina<br>+9 Intellect<br>Durability 100 / 100<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersStaff.itemHonorPrice[3] = 2040
fLorekeepersStaff.itemTokenPrice[3] = new Array(0,0,0,40);
fLorekeepersStaff.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>106 - 160 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(45.9 damage per second)<br>+18 Stamina<br>+11 Intellect<br>Durability 100 / 100<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fLorekeepersStaff.itemHonorPrice[4] = 15000
fLorekeepersStaff.itemTokenPrice[4] = new Array(0,0,0,40);
fLorekeepersStaff.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Lorekeeper's Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>125 - 188 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(54.0 damage per second)<br>+21 Stamina<br>+13 Intellect<br>Durability 100 / 100<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLorekeepersStaff; ++i;





var fOutrunnersBow = new RewardItem("alliance","Outrunner's Bow","/shared/wow-com/images/basics/factions/warsong/bow_a.gif");
fOutrunnersBow.itemHonorPrice = new Array();
fOutrunnersBow.itemHonorPrice[0] = 315
fOutrunnersBow.itemTokenPrice = new Array();
fOutrunnersBow.itemTokenPrice[0] = new Array(0,0,0,30);
fOutrunnersBow.itemStats = new Array();
fOutrunnersBow.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>25 - 48 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(15.2 damage per second)<br>Durability 65 / 65<br>Requires Level 18</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[1] = 465
fOutrunnersBow.itemTokenPrice[1] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>35 - 67 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(21.2 damage per second)<br>Durability 75 / 75<br>Requires Level 28</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[2] = 690
fOutrunnersBow.itemTokenPrice[2] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>48 - 90 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(28.7 damage per second)<br>+3 Agility<br>+6 Stamina<br>Durability 75 / 75<br>Requires Level 38</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[3] = 1020
fOutrunnersBow.itemTokenPrice[3] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>58 - 109 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(34.8 damage per second)<br>+3 Agility<br>+8 Stamina<br>Durability 75 / 75<br>Requires Level 48</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[4] = 7500
fOutrunnersBow.itemTokenPrice[4] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>68 - 128 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(40.8 damage per second)<br>+4 Agility<br>+10 Stamina<br>Durability 75 / 75<br>Requires Level 58</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutrunnersBow; ++i;





var fProtectorsSword = new RewardItem("alliance","Protector's Sword","/shared/wow-com/images/basics/factions/warsong/sword_a.gif");
fProtectorsSword.itemHonorPrice = new Array();
fProtectorsSword.itemHonorPrice[0] = 315
fProtectorsSword.itemTokenPrice = new Array();
fProtectorsSword.itemTokenPrice[0] = new Array(0,0,0,30);
fProtectorsSword.itemStats = new Array();
fProtectorsSword.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Protector's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>28 - 53 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(15.0 damage per second)<br>+4 Strength<br>+2 Stamina<br>Durability 75 / 75<br>Requires Level 18</div>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsSword.itemHonorPrice[1] = 465
fProtectorsSword.itemTokenPrice[1] = new Array(0,0,0,30);
fProtectorsSword.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Protector's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>40 - 75 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(21.3 damage per second)<br>+7 Strength<br>+3 Stamina<br>Durability 90 / 90<br>Requires Level 28</div>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsSword.itemHonorPrice[2] = 690
fProtectorsSword.itemTokenPrice[2] = new Array(0,0,0,30);
fProtectorsSword.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Protector's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>55 - 103 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(29.3 damage per second)<br>+8 Strength<br>+3 Stamina<br>Durability 90 / 90<br>Requires Level 38</div>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsSword.itemHonorPrice[3] = 1020
fProtectorsSword.itemTokenPrice[3] = new Array(0,0,0,30);
fProtectorsSword.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Protector's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>66 - 124 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(35.2 damage per second)<br>+11 Strength<br>+5 Stamina<br>Durability 90 / 90<br>Requires Level 48</div>\
</div>\
</td>\
</tr>\
</table>\
";
fProtectorsSword.itemHonorPrice[4] = 7500
fProtectorsSword.itemTokenPrice[4] = new Array(0,0,0,30);
fProtectorsSword.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Protector's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>78 - 146 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(41.5 damage per second)<br>+13 Strength<br>+5 Stamina<br>Durability 90 / 90<br>Requires Level 58</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fProtectorsSword; ++i;




var fSentinelsBlade = new RewardItem("alliance","Sentinel's Blade","/shared/wow-com/images/basics/factions/warsong/dagger_a.gif");
fSentinelsBlade.itemHonorPrice = new Array();
fSentinelsBlade.itemHonorPrice[0] = 315
fSentinelsBlade.itemTokenPrice = new Array();
fSentinelsBlade.itemTokenPrice[0] = new Array(0,0,0,30);
fSentinelsBlade.itemStats = new Array();
fSentinelsBlade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Sentinel's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>18 - 34 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(15.3 damage per second)<br>+4 Agility<br>+2 Stamina<br>Durability 50 / 50<br>Requires Level 18</div>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsBlade.itemHonorPrice[1] = 465
fSentinelsBlade.itemTokenPrice[1] = new Array(0,0,0,30);
fSentinelsBlade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Sentinel's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>25 - 47 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(21.2 damage per second)<br>+7 Agility<br>+3 Stamina<br>Durability 65 / 65<br>Requires Level 28</div>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsBlade.itemHonorPrice[2] = 690
fSentinelsBlade.itemTokenPrice[2] = new Array(0,0,0,30);
fSentinelsBlade.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Sentinel's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>34 - 65 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(29.1 damage per second)<br>+8 Agility<br>+3 Stamina<br>Durability 65 / 65<br>Requires Level 38</div>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsBlade.itemHonorPrice[3] = 1020
fSentinelsBlade.itemTokenPrice[3] = new Array(0,0,0,30);
fSentinelsBlade.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Sentinel's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>41 - 78 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(35.0 damage per second)<br>+11 Agility<br>+5 Stamina<br>Durability 65 / 65<br>Requires Level 48</div>\
</div>\
</td>\
</tr>\
</table>\
";
fSentinelsBlade.itemHonorPrice[4] = 7500
fSentinelsBlade.itemTokenPrice[4] = new Array(0,0,0,30);
fSentinelsBlade.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Sentinel's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>49 - 92 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(41.5 damage per second)<br>+13 Agility<br>+5 Stamina<br>Durability 65 / 65<br>Requires Level 58</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsBlade; ++i;







var fSilverwingBattleTabard = new RewardItem("alliance","Silverwing Battle Tabard","/shared/wow-com/images/basics/factions/warsong/tabard.gif");
fSilverwingBattleTabard.itemTokenPrice = new Array();
fSilverwingBattleTabard.itemTokenPrice[0] = new Array(0,0,0,60);
fSilverwingBattleTabard.itemStats = new Array();
fSilverwingBattleTabard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Silverwing Battle Tabard<br>Binds when picked up<br>Unique<br>Tabard</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSilverwingBattleTabard; ++i;




var fBerserkerBracers = new RewardItem("alliance","Berserker Bracers","/shared/wow-com/images/basics/factions/warsong/bracers02.gif");
fBerserkerBracers.itemHonorPrice = new Array();
fBerserkerBracers.itemHonorPrice[3] = 621
fBerserkerBracers.itemTokenPrice = new Array();
fBerserkerBracers.itemTokenPrice[3] = new Array(0,0,0,20);
fBerserkerBracers.itemStats = new Array();
fBerserkerBracers.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Berserker Bracers</span>\
<br>Binds when picked up<br>Unique<br>Wrist<span class=\"myRight\">Plate</span>\
<br>262 Armor<br>+14 Strength<br>+6 Agility<br>+8 Stamina<br>Durability 55 / 55<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fBerserkerBracers.itemHonorPrice[4] = 918
fBerserkerBracers.itemTokenPrice[4] = new Array(0,0,0,20);
fBerserkerBracers.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Berserker Bracers</span>\
<br>Binds when picked up<br>Unique<br>Wrist<span class=\"myRight\">Plate</span>\
<br>314 Armor<br>+17 Strength<br>+7 Agility<br>+9 Stamina<br>Durability 55 / 55<br>Requires Level 50</span>\
</div>\
</td>\
</tr>\
</table>\
";
fBerserkerBracers.itemHonorPrice[5] = 6750
fBerserkerBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fBerserkerBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Berserker Bracers</span>\
<br>Binds when picked up<br>Unique<br>Wrist<span class=\"myRight\">Plate</span>\
<br>368 Armor<br>+19 Strength<br>+8 Agility<br>+11 Stamina<br>Durability 55 / 55<br>Requires Level 60</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBerserkerBracers; ++i;





var fDryadsWristBindings = new RewardItem("alliance","Dryad's Wrist Bindings","/shared/wow-com/images/basics/factions/warsong/bracers03.gif");
fDryadsWristBindings.itemHonorPrice = new Array();
fDryadsWristBindings.itemHonorPrice[3] = 621
fDryadsWristBindings.itemTokenPrice = new Array();
fDryadsWristBindings.itemTokenPrice[3] = new Array(0,0,0,20);
fDryadsWristBindings.itemStats = new Array();
fDryadsWristBindings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Dryad's Wrist Bindings</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>35 Armor<br>+6 Stamina<br>+6 Intellect<br>+5 Spirit<br>Durability 35 / 35<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 16.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";

fDryadsWristBindings.itemHonorPrice[4] = 918
fDryadsWristBindings.itemTokenPrice[4] = new Array(0,0,0,20);
fDryadsWristBindings.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Dryad's Wrist Bindings</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>43 Armor<br>+7 Stamina<br>+6 Intellect<br>+6 Spirit<br>Durability 35 / 35<br>Requires Level 50<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDryadsWristBindings.itemHonorPrice[5] = 6750
fDryadsWristBindings.itemTokenPrice[5] = new Array(0,0,0,20);
fDryadsWristBindings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Dryad's Wrist Bindings</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>50 Armor<br>+8 Stamina<br>+8 Intellect<br>+7 Spirit<br>Durability 35 / 35<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDryadsWristBindings; ++i;





var fForestStalkersBracers = new RewardItem("alliance","Forest Stalker's Bracers","/shared/wow-com/images/basics/factions/warsong/bracers01.gif");
fForestStalkersBracers.itemHonorPrice = new Array();
fForestStalkersBracers.itemHonorPrice[3] = 621
fForestStalkersBracers.itemTokenPrice = new Array();
fForestStalkersBracers.itemTokenPrice[3] = new Array(0,0,0,20);
fForestStalkersBracers.itemStats = new Array();
fForestStalkersBracers.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Forest Stalker's Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>73 Armor<br>+8 Strength<br>+14 Agility<br>+6 Stamina<br>Durability 40 / 40<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fForestStalkersBracers.itemHonorPrice[4] = 918
fForestStalkersBracers.itemTokenPrice[4] = new Array(0,0,0,20);
fForestStalkersBracers.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Forest Stalker's Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>86 Armor<br>+9 Strength<br>+17 Agility<br>+7 Stamina<br>Durability 40 / 40<br>Requires Level 50</span>\
</div>\
</td>\
</tr>\
</table>\
";
fForestStalkersBracers.itemHonorPrice[5] = 6750
fForestStalkersBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fForestStalkersBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Forest Stalker's Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>99 Armor<br>+11 Strength<br>+19 Agility<br>+8 Stamina<br>Durability 40 / 40<br>Requires Level 60</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fForestStalkersBracers; ++i;



var fWindtalkersWristguards = new RewardItem("alliance","Windtalker's Wristguards","/shared/wow-com/images/basics/factions/warsong/bracers04.gif");
fWindtalkersWristguards.itemHonorPrice = new Array();
fWindtalkersWristguards.itemHonorPrice[3] = 621
fWindtalkersWristguards.itemTokenPrice = new Array();
fWindtalkersWristguards.itemTokenPrice[3] = new Array(0,0,0,20);
fWindtalkersWristguards.itemStats = new Array();
fWindtalkersWristguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Windtalker's Wristguards</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>149 Armor<br>+6 Stamina<br>+6 Intellect<br>+5 Spirit<br>Durability 50 / 50<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
fWindtalkersWristguards.itemHonorPrice[4] = 918
fWindtalkersWristguards.itemTokenPrice[4] = new Array(0,0,0,20);
fWindtalkersWristguards.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Windtalker's Wristguards</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>178 Armor<br>+7 Stamina<br>+6 Intellect<br>+6 Spirit<br>Durability 50 / 50<br>Requires Level 50<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
fWindtalkersWristguards.itemHonorPrice[5] = 6750
fWindtalkersWristguards.itemTokenPrice[5] = new Array(0,0,0,20);
fWindtalkersWristguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Windtalker's Wristguards</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>208 Armor<br>+8 Stamina<br>+8 Intellect<br>+7 Spirit<br>Durability 50 / 50<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWindtalkersWristguards; ++i;




var fSentinelsSilkLeggings = new RewardItem("alliance","Sentinel's Silk Leggings","/shared/wow-com/images/basics/factions/warsong/silk_leggings.gif");
fSentinelsSilkLeggings.itemHonorPrice = new Array();
fSentinelsSilkLeggings.itemHonorPrice[5] = 13125
fSentinelsSilkLeggings.itemTokenPrice = new Array();
fSentinelsSilkLeggings.itemTokenPrice[5] = new Array(0,0,0,40);
fSentinelsSilkLeggings.itemStats = new Array();
fSentinelsSilkLeggings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Sentinel's Silk Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Cloth</span>\
<br>200 Armor<br>+23 Stamina<br>+19 Intellect<br>+10 Spirit<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsSilkLeggings; ++i;


var fSentinelsLizardhidePants = new RewardItem("alliance","Sentinel's Lizardhide Pants","/shared/wow-com/images/basics/factions/warsong/lizardhide_pants.gif");
fSentinelsLizardhidePants.itemHonorPrice = new Array();
fSentinelsLizardhidePants.itemHonorPrice[5] = 13125
fSentinelsLizardhidePants.itemTokenPrice = new Array();
fSentinelsLizardhidePants.itemTokenPrice[5] = new Array(0,0,0,40);
fSentinelsLizardhidePants.itemStats = new Array();
fSentinelsLizardhidePants.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Sentinel's Lizardhide Pants</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>287 Armor<br>+22 Strength<br>+10 Agility<br>+22 Stamina<br>+22 Intellect<br>+9 Spirit<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 11.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsLizardhidePants; ++i;


var fSentinelsLeatherPants = new RewardItem("alliance","Sentinel's Leather Pants","/shared/wow-com/images/basics/factions/warsong/leather_pants.gif");
fSentinelsLeatherPants.itemHonorPrice = new Array();
fSentinelsLeatherPants.itemHonorPrice[5] = 13125
fSentinelsLeatherPants.itemTokenPrice = new Array();
fSentinelsLeatherPants.itemTokenPrice[5] = new Array(0,0,0,40);
fSentinelsLeatherPants.itemStats = new Array();
fSentinelsLeatherPants.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Sentinel's Leather Pants</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>257 Armor<br>+28 Agility<br>+27 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsLeatherPants; ++i;


var fSentinelsChainLeggings = new RewardItem("alliance","Sentinel's Chain Leggings","/shared/wow-com/images/basics/factions/warsong/chain_leggings.gif");
fSentinelsChainLeggings.itemHonorPrice = new Array();
fSentinelsChainLeggings.itemHonorPrice[5] = 13125
fSentinelsChainLeggings.itemTokenPrice = new Array();
fSentinelsChainLeggings.itemTokenPrice[5] = new Array(0,0,0,40);
fSentinelsChainLeggings.itemStats = new Array();
fSentinelsChainLeggings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Sentinel's Chain Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>415 Armor<br>+35 Agility<br>+15 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsChainLeggings; ++i;


var fSentinelsLamellarLegguards = new RewardItem("alliance","Sentinel's Lamellar Legguards","/shared/wow-com/images/basics/factions/warsong/lamellar_legguards.gif");
fSentinelsLamellarLegguards.itemHonorPrice = new Array();
fSentinelsLamellarLegguards.itemHonorPrice[5] = 13125
fSentinelsLamellarLegguards.itemTokenPrice = new Array();
fSentinelsLamellarLegguards.itemTokenPrice[5] = new Array(0,0,0,40);
fSentinelsLamellarLegguards.itemStats = new Array();
fSentinelsLamellarLegguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Sentinel's Lamellar Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>737 Armor<br>+21 Strength<br>+21 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsLamellarLegguards; ++i;


var fSentinelsPlateLegguards = new RewardItem("alliance","Sentinel's Plate Legguards","/shared/wow-com/images/basics/factions/warsong/plate_legguards.gif");
fSentinelsPlateLegguards.itemHonorPrice = new Array();
fSentinelsPlateLegguards.itemHonorPrice[5] = 13125
fSentinelsPlateLegguards.itemTokenPrice = new Array();
fSentinelsPlateLegguards.itemTokenPrice[5] = new Array(0,0,0,40);
fSentinelsPlateLegguards.itemStats = new Array();
fSentinelsPlateLegguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Sentinel's Plate Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>737 Armor<br>+28 Strength<br>+27 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsPlateLegguards; ++i;

var fSentinelsMailLeggings = new RewardItem("alliance","Sentinel's Mail Leggings","/shared/wow-com/images/basics/factions/warsong/plate_legguards.gif");
fSentinelsMailLeggings.itemHonorPrice = new Array();
fSentinelsMailLeggings.itemHonorPrice[5] = 11625
fSentinelsMailLeggings.itemTokenPrice = new Array();
fSentinelsMailLeggings.itemTokenPrice[5] = new Array(0,0,0,60);
fSentinelsMailLeggings.itemStats = new Array();
fSentinelsMailLeggings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sentinel's Mail Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>415 Armor<br>+14 Strength<br>+22 Stamina<br>+22 Intellect<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsMailLeggings; ++i;




//----------------------------------------------------------------
//-------------------------------------------------------------------
//---Horde below
var fRuneOfPerfection = new RewardItem("horde","Rune of Perfection","/shared/wow-com/images/basics/factions/warsong/rune01.gif");
fRuneOfPerfection.itemHonorPrice = new Array();
fRuneOfPerfection.itemHonorPrice[1] = 174
fRuneOfPerfection.itemTokenPrice = new Array();
fRuneOfPerfection.itemTokenPrice[1] = new Array(0,0,0,30);
fRuneOfPerfection.itemStats = new Array();
fRuneOfPerfection.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Rune of Perfection</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+4 Stamina<br>Classes: Priest, Shaman, Mage, Warlock, Druid<br>Requires Level 20<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 10.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fRuneOfPerfection.itemHonorPrice[3] = 380
fRuneOfPerfection.itemTokenPrice[3] = new Array(0,0,0,30);
fRuneOfPerfection.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Rune of Perfection</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+7 Stamina<br>Classes: Priest, Shaman, Mage, Warlock, Druid<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 20.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRuneOfPerfection; ++i;





var fRuneOfDuty = new RewardItem("horde","Rune of Duty","/shared/wow-com/images/basics/factions/warsong/rune02.gif");
fRuneOfDuty.itemHonorPrice = new Array();
fRuneOfDuty.itemHonorPrice[1] = 174
fRuneOfDuty.itemTokenPrice = new Array();
fRuneOfDuty.itemTokenPrice[1] = new Array(0,0,0,30);
fRuneOfDuty.itemStats = new Array();
fRuneOfDuty.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Rune of Duty</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+4 Stamina<br>Classes: Warrior, Paladin, Hunter, Rogue<br>Requires Level 20<br>\
<span class=\"myGreen\">Equip: Restores 3 health per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fRuneOfDuty.itemHonorPrice[3] = 380
fRuneOfDuty.itemTokenPrice[3] = new Array(0,0,0,30);
fRuneOfDuty.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Rune of Duty</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>+7 Stamina<br>Classes: Warrior, Paladin, Hunter, Rogue<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Restores 6 health per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRuneOfDuty; ++i;

var fWarsongGulchFieldRation = new RewardItem("horde","Warsong Gulch Field Ration","/shared/wow-com/images/basics/factions/warsong/fieldration.gif");
fWarsongGulchFieldRation.itemMoneyPrice = new Array();
fWarsongGulchFieldRation.itemMoneyPrice[1] = 1000
fWarsongGulchFieldRation.itemStats = new Array();
fWarsongGulchFieldRation.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Field Ration<br>Binds when picked up<br>Requires Level 25<br>\
<span class=\"myGreen\">Use: Restores 1074 health and 2202 mana over 30 sec.  Must remain seated while eating.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchFieldRation; ++i;



var fWarsongGulchIronRation = new RewardItem("horde","Warsong Gulch Iron Ration","/shared/wow-com/images/basics/factions/warsong/ironration.gif");
fWarsongGulchIronRation.itemMoneyPrice = new Array();
fWarsongGulchIronRation.itemMoneyPrice[2] = 1500
fWarsongGulchIronRation.itemStats = new Array();
fWarsongGulchIronRation.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Iron Ration<br>Binds when picked up<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 1608 health and 3306 mana over 30 sec.  Must remain seated while eating.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchIronRation; ++i;



var fWarsongGulchEnrichedRation = new RewardItem("horde","Warsong Gulch Enriched Ration","/shared/wow-com/images/basics/factions/warsong/enrichedration.gif");
fWarsongGulchEnrichedRation.itemMoneyPrice = new Array();
fWarsongGulchEnrichedRation.itemMoneyPrice[3] = 2000
fWarsongGulchEnrichedRation.itemStats = new Array();
fWarsongGulchEnrichedRation.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Enriched Ration<br>Binds when picked up<br>Requires Level 45<br>\
<span class=\"myGreen\">Use: Restores 2148 health and 4410 mana over 30 sec.  Must remain seated while eating.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchEnrichedRation; ++i;






var fWarsongGulchSilkBandage = new RewardItem("horde","Warsong Gulch Silk Bandage","/shared/wow-com/images/basics/factions/warsong/silkbandage.gif");
fWarsongGulchSilkBandage.itemMoneyPrice = new Array();
fWarsongGulchSilkBandage.itemMoneyPrice[1] = 1000
fWarsongGulchSilkBandage.itemStats = new Array();
fWarsongGulchSilkBandage.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Silk Bandage<br>Binds when picked up<br>Requires Level 25<br>Requires First Aid (125)<br>\
<span class=\"myGreen\">Use: Heals 640 damage over 8 sec.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchSilkBandage; ++i;

var fWarsongGulchMageweaveBandage = new RewardItem("horde","Warsong Gulch Mageweave Bandage","/shared/wow-com/images/basics/factions/warsong/mageweavebandage.gif");
fWarsongGulchMageweaveBandage.itemMoneyPrice = new Array();
fWarsongGulchMageweaveBandage.itemMoneyPrice[2] = 1500
fWarsongGulchMageweaveBandage.itemStats = new Array();
fWarsongGulchMageweaveBandage.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Mageweave Bandage<br>Binds when picked up<br>Requires Level 35<br>Requires First Aid (175)<br>\
<span class=\"myGreen\">Use: Heals 1104 damage over 8 sec.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchMageweaveBandage; ++i;

var fWarsongGulchRuneclothBandage = new RewardItem("horde","Warsong Gulch Runecloth Bandage","/shared/wow-com/images/basics/factions/warsong/runeclothbandage.gif");
fWarsongGulchRuneclothBandage.itemMoneyPrice = new Array();
fWarsongGulchRuneclothBandage.itemMoneyPrice[3] = 2000
fWarsongGulchRuneclothBandage.itemStats = new Array();
fWarsongGulchRuneclothBandage.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Gulch Runecloth Bandage<br>Binds when picked up<br>Requires Level 45<br>Requires First Aid (225)<br>\
<span class=\"myGreen\">Use: Heals 2000 damage over 8 sec.  Usable only inside Warsong Gulch.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongGulchRuneclothBandage; ++i;






var fSuperiorHealingDraught = new RewardItem("horde","Superior Healing Draught","/shared/wow-com/images/basics/factions/warsong/health02.gif");
fSuperiorHealingDraught.itemMoneyPrice = new Array();
fSuperiorHealingDraught.itemMoneyPrice[2] = 500
fSuperiorHealingDraught.itemHonorPrice = new Array();
fSuperiorHealingDraught.itemHonorPrice[2] = 6
fSuperiorHealingDraught.itemStats = new Array();
fSuperiorHealingDraught.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Superior Healing Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 560 to 720 health. This item may only be used in PvP Battlegrounds.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSuperiorHealingDraught; ++i;


var fSuperiorManaDraught = new RewardItem("horde","Superior Mana Draught","/shared/wow-com/images/basics/factions/warsong/mana02.gif");
fSuperiorManaDraught.itemMoneyPrice = new Array();
fSuperiorManaDraught.itemMoneyPrice[2] = 500
fSuperiorManaDraught.itemHonorPrice = new Array();
fSuperiorManaDraught.itemHonorPrice[2] = 6
fSuperiorManaDraught.itemStats = new Array();
fSuperiorManaDraught.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Superior Mana Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 560 to 720 mana. This item may only be used in PvP Battlegrounds.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSuperiorManaDraught; ++i;















var fBattleHealersCloak = new RewardItem("horde","Battle Healer's Cloak","/shared/wow-com/images/basics/factions/warsong/cape_h.gif");
fBattleHealersCloak.itemHonorPrice = new Array();
fBattleHealersCloak.itemHonorPrice[0] = 95
fBattleHealersCloak.itemTokenPrice = new Array();
fBattleHealersCloak.itemTokenPrice[0] = new Array(0,0,0,10);
fBattleHealersCloak.itemStats = new Array();
fBattleHealersCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Battle Healer's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br>20 Armor<br>+4 Stamina<br>+2 Spirit<br>Requires Level 18<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 9.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fBattleHealersCloak.itemHonorPrice[1] = 140
fBattleHealersCloak.itemTokenPrice[1] = new Array(0,0,0,10);
fBattleHealersCloak.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Battle Healer's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br>25 Armor<br>+6 Stamina<br>+4 Spirit<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 13.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fBattleHealersCloak.itemHonorPrice[2] = 207
fBattleHealersCloak.itemTokenPrice[2] = new Array(0,0,0,10);
fBattleHealersCloak.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Battle Healer's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br>31 Armor<br>+8 Stamina<br>+5 Spirit<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fBattleHealersCloak.itemHonorPrice[3] = 306
fBattleHealersCloak.itemTokenPrice[3] = new Array(0,0,0,10);
fBattleHealersCloak.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Battle Healer's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br>38 Armor<br>+9 Stamina<br>+6 Spirit<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 22.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fBattleHealersCloak.itemHonorPrice[4] = 2250
fBattleHealersCloak.itemTokenPrice[4] = new Array(0,0,0,10);
fBattleHealersCloak.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Battle Healer's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br>45 Armor<br>+11 Stamina<br>+8 Spirit<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 26.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBattleHealersCloak; ++i;




var fAdvisorsRing = new RewardItem("horde","Advisor's Ring","/shared/wow-com/images/basics/factions/warsong/ring03.gif");
fAdvisorsRing.itemHonorPrice = new Array();
fAdvisorsRing.itemHonorPrice[0] = 95
fAdvisorsRing.itemTokenPrice = new Array();
fAdvisorsRing.itemTokenPrice[0] = new Array(0,0,0,20);
fAdvisorsRing.itemStats = new Array();
fAdvisorsRing.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Advisor's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+2 Stamina<br>Requires Level 18<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 5.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsRing.itemHonorPrice[1] = 140
fAdvisorsRing.itemTokenPrice[1] = new Array(0,0,0,20);
fAdvisorsRing.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Advisor's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+4 Stamina<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 7.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 2 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsRing.itemHonorPrice[2] = 207
fAdvisorsRing.itemTokenPrice[2] = new Array(0,0,0,20);
fAdvisorsRing.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Advisor's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+5 Stamina<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 9.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsRing.itemHonorPrice[3] = 306
fAdvisorsRing.itemTokenPrice[3] = new Array(0,0,0,20);
fAdvisorsRing.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Advisor's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+6 Stamina<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsRing.itemHonorPrice[4] = 2250
fAdvisorsRing.itemTokenPrice[4] = new Array(0,0,0,20);
fAdvisorsRing.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Advisor's Ring</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+8 Stamina<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAdvisorsRing; ++i;





var fScoutsMedallion = new RewardItem("horde","Scout's Medallion","/shared/wow-com/images/basics/factions/warsong/medallion_h.gif");
fScoutsMedallion.itemHonorPrice = new Array();
fScoutsMedallion.itemHonorPrice[0] = 95
fScoutsMedallion.itemTokenPrice = new Array();
fScoutsMedallion.itemTokenPrice[0] = new Array(0,0,0,20);
fScoutsMedallion.itemStats = new Array();
fScoutsMedallion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Scout's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+6 Agility<br>+2 Stamina<br>Requires Level 18</span>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsMedallion.itemHonorPrice[1] = 140
fScoutsMedallion.itemTokenPrice[1] = new Array(0,0,0,20);
fScoutsMedallion.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Scout's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+8 Agility<br>+5 Stamina<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsMedallion.itemHonorPrice[2] = 207
fScoutsMedallion.itemTokenPrice[2] = new Array(0,0,0,20);
fScoutsMedallion.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Scout's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+11 Agility<br>+7 Stamina<br>Requires Level 38</span>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsMedallion.itemHonorPrice[3] = 306
fScoutsMedallion.itemTokenPrice[3] = new Array(0,0,0,20);
fScoutsMedallion.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Scout's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+12 Agility<br>+8 Stamina<br>Requires Level 48</span>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsMedallion.itemHonorPrice[4] = 2250
fScoutsMedallion.itemTokenPrice[4] = new Array(0,0,0,20);
fScoutsMedallion.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Scout's Medallion</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+15 Agility<br>+10 Stamina<br>Requires Level 58</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fScoutsMedallion; ++i;






var fLegionnairesBand = new RewardItem("horde","Legionnaire's Band","/shared/wow-com/images/basics/factions/warsong/ring04.gif");
fLegionnairesBand.itemHonorPrice = new Array();
fLegionnairesBand.itemHonorPrice[0] = 95
fLegionnairesBand.itemTokenPrice = new Array();
fLegionnairesBand.itemTokenPrice[0] = new Array(0,0,0,20);
fLegionnairesBand.itemStats = new Array();
fLegionnairesBand.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Legionnaire's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+4 Strength<br>+4 Agility<br>+2 Stamina<br>Requires Level 18</span>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesBand.itemHonorPrice[1] = 140
fLegionnairesBand.itemTokenPrice[1] = new Array(0,0,0,20);
fLegionnairesBand.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Legionnaire's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+6 Strength<br>+6 Agility<br>+4 Stamina<br>Requires Level 28</span>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesBand.itemHonorPrice[2] = 207
fLegionnairesBand.itemTokenPrice[2] = new Array(0,0,0,20);
fLegionnairesBand.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Legionnaire's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+8 Strength<br>+8 Agility<br>+5 Stamina<br>Requires Level 38</span>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesBand.itemHonorPrice[3] = 306
fLegionnairesBand.itemTokenPrice[3] = new Array(0,0,0,20);
fLegionnairesBand.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Legionnaire's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+10 Strength<br>+9 Agility<br>+6 Stamina<br>Requires Level 48</span>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesBand.itemHonorPrice[4] = 2250
fLegionnairesBand.itemTokenPrice[4] = new Array(0,0,0,20);
fLegionnairesBand.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Legionnaire's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+12 Strength<br>+11 Agility<br>+8 Stamina<br>Requires Level 58</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLegionnairesBand; ++i;












var fMajorHealingDraught = new RewardItem("horde","Major Healing Draught","/shared/wow-com/images/basics/factions/warsong/health01.gif");
fMajorHealingDraught.itemMoneyPrice = new Array();
fMajorHealingDraught.itemMoneyPrice[3] = 1000
fMajorHealingDraught.itemHonorPrice = new Array();
fMajorHealingDraught.itemHonorPrice[3] = 3
fMajorHealingDraught.itemStats = new Array();
fMajorHealingDraught.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Major Healing Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 45<br>\
<span class=\"myGreen\">Use: Restores 980 to 1260 health. This item may only be used in PvP Battlegrounds.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorHealingDraught; ++i;


var fMajorManaDraught = new RewardItem("horde","Major Mana Draught","/shared/wow-com/images/basics/factions/warsong/mana01.gif");
fMajorManaDraught.itemMoneyPrice = new Array();
fMajorManaDraught.itemMoneyPrice[3] = 1000
fMajorManaDraught.itemHonorPrice = new Array();
fMajorManaDraught.itemHonorPrice[3] = 3
fMajorManaDraught.itemStats = new Array();
fMajorManaDraught.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Mana Draught<br>Binds when picked up<br>Unique (10)<br>Requires Level 45<br>\
<span class=\"myGreen\">Use: Restores 980 to 1260 mana. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorManaDraught; ++i;













var fAdvisorsGnarledStaff = new RewardItem("horde","Advisor's Gnarled Staff","/shared/wow-com/images/basics/factions/warsong/staff_h.gif");
fAdvisorsGnarledStaff.itemHonorPrice = new Array();
fAdvisorsGnarledStaff.itemHonorPrice[0] = 630
fAdvisorsGnarledStaff.itemTokenPrice = new Array();
fAdvisorsGnarledStaff.itemTokenPrice[0] = new Array(0,0,0,40);
fAdvisorsGnarledStaff.itemStats = new Array();
fAdvisorsGnarledStaff.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Advisor's Gnarled Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>45 - 69 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(19.7 damage per second)<br>+8 Stamina<br>+4 Intellect<br>Durability 80 / 80<br>Requires Level 18<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsGnarledStaff.itemHonorPrice[1] = 930
fAdvisorsGnarledStaff.itemTokenPrice[1] = new Array(0,0,0,40);
fAdvisorsGnarledStaff.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Advisor's Gnarled Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>64 - 97 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(27.8 damage per second)<br>+11 Stamina<br>+7 Intellect<br>Durability 100 / 100<br>Requires Level 28<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsGnarledStaff.itemHonorPrice[2] = 1380
fAdvisorsGnarledStaff.itemTokenPrice[2] = new Array(0,0,0,40);
fAdvisorsGnarledStaff.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Advisor's Gnarled Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>88 - 133 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(38.1 damage per second)<br>+14 Stamina<br>+9 Intellect<br>Durability 100 / 100<br>Requires Level 38<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsGnarledStaff.itemHonorPrice[3] = 2040
fAdvisorsGnarledStaff.itemTokenPrice[3] = new Array(0,0,0,40);
fAdvisorsGnarledStaff.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Advisor's Gnarled Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>106 - 160 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(45.9 damage per second)<br>+18 Stamina<br>+11 Intellect<br>Durability 100 / 100<br>Requires Level 48<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
fAdvisorsGnarledStaff.itemHonorPrice[4] = 15000
fAdvisorsGnarledStaff.itemTokenPrice[4] = new Array(0,0,0,40);
fAdvisorsGnarledStaff.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Advisor's Gnarled Staff</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>125 - 188 Damage<span class=\"myRight\">Speed 2.90</span>\
<br>(54.0 damage per second)<br>+21 Stamina<br>+13 Intellect<br>Durability 100 / 100<br>Requires Level 58<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAdvisorsGnarledStaff; ++i;



var fOutrunnersBow = new RewardItem("horde","Outrunner's Bow","/shared/wow-com/images/basics/factions/warsong/bow_h.gif");
fOutrunnersBow.itemHonorPrice = new Array();
fOutrunnersBow.itemHonorPrice[0] = 315
fOutrunnersBow.itemTokenPrice = new Array();
fOutrunnersBow.itemTokenPrice[0] = new Array(0,0,0,30);
fOutrunnersBow.itemStats = new Array();
fOutrunnersBow.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>25 - 48 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(15.2 damage per second)<br>Durability 65 / 65<br>Requires Level 18</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[1] = 465
fOutrunnersBow.itemTokenPrice[1] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>35 - 67 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(21.2 damage per second)<br>Durability 75 / 75<br>Requires Level 28</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[2] = 690
fOutrunnersBow.itemTokenPrice[2] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>48 - 90 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(28.7 damage per second)<br>+3 Agility<br>+6 Stamina<br>Durability 75 / 75<br>Requires Level 38</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[3] = 1020
fOutrunnersBow.itemTokenPrice[3] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>58 - 109 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(34.8 damage per second)<br>+3 Agility<br>+8 Stamina<br>Durability 75 / 75<br>Requires Level 48</div>\
</div>\
</td>\
</tr>\
</table>\
";
fOutrunnersBow.itemHonorPrice[4] = 7500
fOutrunnersBow.itemTokenPrice[4] = new Array(0,0,0,30);
fOutrunnersBow.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Outrunner's Bow</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Bow</span>\
<br>68 - 128 Damage<span class=\"myRight\">Speed 2.40</span>\
<br>(40.8 damage per second)<br>+4 Agility<br>+10 Stamina<br>Durability 75 / 75<br>Requires Level 58</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutrunnersBow; ++i;




var fLegionnairesSword = new RewardItem("horde","Legionnaire's Sword","/shared/wow-com/images/basics/factions/warsong/sword_h.gif");
fLegionnairesSword.itemHonorPrice = new Array();
fLegionnairesSword.itemHonorPrice[0] = 315
fLegionnairesSword.itemTokenPrice = new Array();
fLegionnairesSword.itemTokenPrice[0] = new Array(0,0,0,30);
fLegionnairesSword.itemStats = new Array();
fLegionnairesSword.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Legionnaire's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>28 - 53 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(15.0 damage per second)<br>+4 Strength<br>+2 Stamina<br>Durability 75 / 75<br>Requires Level 18</div>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesSword.itemHonorPrice[1] = 465
fLegionnairesSword.itemTokenPrice[1] = new Array(0,0,0,30);
fLegionnairesSword.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Legionnaire's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>40 - 75 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(21.3 damage per second)<br>+7 Strength<br>+3 Stamina<br>Durability 90 / 90<br>Requires Level 28</div>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesSword.itemHonorPrice[2] = 690
fLegionnairesSword.itemTokenPrice[2] = new Array(0,0,0,30);
fLegionnairesSword.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Legionnaire's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>55 - 103 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(29.3 damage per second)<br>+8 Strength<br>+3 Stamina<br>Durability 90 / 90<br>Requires Level 38</div>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesSword.itemHonorPrice[3] = 1020
fLegionnairesSword.itemTokenPrice[3] = new Array(0,0,0,30);
fLegionnairesSword.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Legionnaire's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>66 - 124 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(35.2 damage per second)<br>+11 Strength<br>+5 Stamina<br>Durability 90 / 90<br>Requires Level 48</div>\
</div>\
</td>\
</tr>\
</table>\
";
fLegionnairesSword.itemHonorPrice[4] = 15000
fLegionnairesSword.itemTokenPrice[4] = new Array(0,0,0,30);
fLegionnairesSword.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Legionnaire's Sword</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>78 - 146 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(41.5 damage per second)<br>+13 Strength<br>+5 Stamina<br>Durability 90 / 90<br>Requires Level 58</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLegionnairesSword; ++i;










var fScoutsBlade = new RewardItem("horde","Scout's Blade","/shared/wow-com/images/basics/factions/warsong/dagger_h.gif");
fScoutsBlade.itemHonorPrice = new Array();
fScoutsBlade.itemHonorPrice[0] = 315
fScoutsBlade.itemTokenPrice = new Array();
fScoutsBlade.itemTokenPrice[0] = new Array(0,0,0,30);
fScoutsBlade.itemStats = new Array();
fScoutsBlade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Scout's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>18 - 34 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(15.3 damage per second)<br>+4 Agility<br>+2 Stamina<br>Durability 50 / 50<br>Requires Level 18</div>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsBlade.itemHonorPrice[1] = 465
fScoutsBlade.itemTokenPrice[1] = new Array(0,0,0,30);
fScoutsBlade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Scout's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>25 - 47 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(21.2 damage per second)<br>+7 Agility<br>+3 Stamina<br>Durability 65 / 65<br>Requires Level 28</div>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsBlade.itemHonorPrice[2] = 690
fScoutsBlade.itemTokenPrice[2] = new Array(0,0,0,30);
fScoutsBlade.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Scout's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>34 - 65 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(29.1 damage per second)<br>+8 Agility<br>+3 Stamina<br>Durability 65 / 65<br>Requires Level 38</div>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsBlade.itemHonorPrice[3] = 1020
fScoutsBlade.itemTokenPrice[3] = new Array(0,0,0,30);
fScoutsBlade.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Scout's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>41 - 78 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(35.0 damage per second)<br>+11 Agility<br>+5 Stamina<br>Durability 65 / 65<br>Requires Level 48</div>\
</div>\
</td>\
</tr>\
</table>\
";
fScoutsBlade.itemHonorPrice[4] = 7500
fScoutsBlade.itemTokenPrice[4] = new Array(0,0,0,30);
fScoutsBlade.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Scout's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>49 - 92 Damage<span class=\"myRight\">Speed 1.70</span>\
<br>(41.5 damage per second)<br>+13 Agility<br>+5 Stamina<br>Durability 65 / 65<br>Requires Level 58</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fScoutsBlade; ++i;





var fWarsongBattleTabard = new RewardItem("horde","Warsong Battle Tabard","/shared/wow-com/images/basics/factions/warsong/tabard.gif");
fWarsongBattleTabard.itemTokenPrice = new Array();
fWarsongBattleTabard.itemTokenPrice[0] = new Array(0,0,0,60);
fWarsongBattleTabard.itemStats = new Array();
fWarsongBattleTabard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Warsong Battle Tabard<br>Binds when picked up<br>Unique<br>Tabard</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarsongBattleTabard; ++i;





var fBerserkerBracers = new RewardItem("horde","Berserker Bracers","/shared/wow-com/images/basics/factions/warsong/bracers02.gif");
fBerserkerBracers.itemHonorPrice = new Array();
fBerserkerBracers.itemHonorPrice[3] = 621
fBerserkerBracers.itemTokenPrice = new Array();
fBerserkerBracers.itemTokenPrice[3] = new Array(0,0,0,20);
fBerserkerBracers.itemStats = new Array();
fBerserkerBracers.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Berserker Bracers</span>\
<br>Binds when picked up<br>Unique<br>Wrist<span class=\"myRight\">Plate</span>\
<br>262 Armor<br>+14 Strength<br>+6 Agility<br>+8 Stamina<br>Durability 55 / 55<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fBerserkerBracers.itemHonorPrice[4] = 918
fBerserkerBracers.itemTokenPrice[4] = new Array(0,0,0,20);
fBerserkerBracers.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Berserker Bracers</span>\
<br>Binds when picked up<br>Unique<br>Wrist<span class=\"myRight\">Plate</span>\
<br>314 Armor<br>+17 Strength<br>+7 Agility<br>+9 Stamina<br>Durability 55 / 55<br>Requires Level 50</span>\
</div>\
</td>\
</tr>\
</table>\
";
fBerserkerBracers.itemHonorPrice[5] = 6750
fBerserkerBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fBerserkerBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Berserker Bracers</span>\
<br>Binds when picked up<br>Unique<br>Wrist<span class=\"myRight\">Plate</span>\
<br>368 Armor<br>+19 Strength<br>+8 Agility<br>+11 Stamina<br>Durability 55 / 55<br>Requires Level 60</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBerserkerBracers; ++i;





var fDryadsWristBindings = new RewardItem("horde","Dryad's Wrist Bindings","/shared/wow-com/images/basics/factions/warsong/bracers03.gif");
fDryadsWristBindings.itemHonorPrice = new Array();
fDryadsWristBindings.itemHonorPrice[3] = 621
fDryadsWristBindings.itemTokenPrice = new Array();
fDryadsWristBindings.itemTokenPrice[3] = new Array(0,0,0,20);
fDryadsWristBindings.itemStats = new Array();
fDryadsWristBindings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Dryad's Wrist Bindings</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>35 Armor<br>+6 Stamina<br>+6 Intellect<br>+5 Spirit<br>Durability 35 / 35<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 16.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDryadsWristBindings.itemHonorPrice[4] = 918
fDryadsWristBindings.itemTokenPrice[4] = new Array(0,0,0,20);
fDryadsWristBindings.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Dryad's Wrist Bindings</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>43 Armor<br>+7 Stamina<br>+6 Intellect<br>+6 Spirit<br>Durability 35 / 35<br>Requires Level 50<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 20.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fDryadsWristBindings.itemHonorPrice[5] = 6750
fDryadsWristBindings.itemTokenPrice[5] = new Array(0,0,0,20);
fDryadsWristBindings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Dryad's Wrist Bindings</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>50 Armor<br>+8 Stamina<br>+8 Intellect<br>+7 Spirit<br>Durability 35 / 35<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 22.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDryadsWristBindings; ++i;





var fForestStalkersBracers = new RewardItem("horde","Forest Stalker's Bracers","/shared/wow-com/images/basics/factions/warsong/bracers01.gif");
fForestStalkersBracers.itemHonorPrice = new Array();
fForestStalkersBracers.itemHonorPrice[3] = 621
fForestStalkersBracers.itemTokenPrice = new Array();
fForestStalkersBracers.itemTokenPrice[3] = new Array(0,0,0,20);
fForestStalkersBracers.itemStats = new Array();
fForestStalkersBracers.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Forest Stalker's Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>73 Armor<br>+8 Strength<br>+14 Agility<br>+6 Stamina<br>Durability 40 / 40<br>Requires Level 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
fForestStalkersBracers.itemHonorPrice[4] = 918
fForestStalkersBracers.itemTokenPrice[4] = new Array(0,0,0,20);
fForestStalkersBracers.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Forest Stalker's Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>86 Armor<br>+9 Strength<br>+17 Agility<br>+7 Stamina<br>Durability 40 / 40<br>Requires Level 50</span>\
</div>\
</td>\
</tr>\
</table>\
";
fForestStalkersBracers.itemHonorPrice[5] = 6750
fForestStalkersBracers.itemTokenPrice[5] = new Array(0,0,0,20);
fForestStalkersBracers.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Forest Stalker's Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>99 Armor<br>+11 Strength<br>+19 Agility<br>+8 Stamina<br>Durability 40 / 40<br>Requires Level 60</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fForestStalkersBracers; ++i;






var fWindtalkersWristguards = new RewardItem("horde","Windtalker's Wristguards","/shared/wow-com/images/basics/factions/warsong/bracers04.gif");
fWindtalkersWristguards.itemHonorPrice = new Array();
fWindtalkersWristguards.itemHonorPrice[3] = 621
fWindtalkersWristguards.itemTokenPrice = new Array();
fWindtalkersWristguards.itemTokenPrice[3] = new Array(0,0,0,20);
fWindtalkersWristguards.itemStats = new Array();
fWindtalkersWristguards.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Windtalker's Wristguards</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>149 Armor<br>+6 Stamina<br>+6 Intellect<br>+5 Spirit<br>Durability 50 / 50<br>Requires Level 40<br>\
<span class=\"myGreen\">Equip: Increases attack power by 28.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fWindtalkersWristguards.itemHonorPrice[4] = 918
fWindtalkersWristguards.itemTokenPrice[4] = new Array(0,0,0,20);
fWindtalkersWristguards.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Windtalker's Wristguards</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>178 Armor<br>+7 Stamina<br>+6 Intellect<br>+6 Spirit<br>Durability 50 / 50<br>Requires Level 50<br>\
<span class=\"myGreen\">Equip: Increases attack power by 34.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
fWindtalkersWristguards.itemHonorPrice[5] = 6750
fWindtalkersWristguards.itemTokenPrice[5] = new Array(0,0,0,20);
fWindtalkersWristguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Windtalker's Wristguards</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>208 Armor<br>+8 Stamina<br>+8 Intellect<br>+7 Spirit<br>Durability 50 / 50<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWindtalkersWristguards; ++i;

var fOutridersSilkLeggings = new RewardItem("horde","Outrider's Silk Leggings","/shared/wow-com/images/basics/factions/warsong/silk_leggings.gif");
fOutridersSilkLeggings.itemHonorPrice = new Array();
fOutridersSilkLeggings.itemHonorPrice[5] = 13125
fOutridersSilkLeggings.itemTokenPrice = new Array();
fOutridersSilkLeggings.itemTokenPrice[5] = new Array(0,0,0,40);
fOutridersSilkLeggings.itemStats = new Array();
fOutridersSilkLeggings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Outrider's Silk Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Cloth</span>\
<br>200 Armor<br>+23 Stamina<br>+19 Intellect<br>+10 Spirit<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutridersSilkLeggings; ++i;

var fOutridersLizardhidePants = new RewardItem("horde","Outrider's Lizardhide Pants","/shared/wow-com/images/basics/factions/warsong/lizardhide_pants.gif");
fOutridersLizardhidePants.itemHonorPrice = new Array();
fOutridersLizardhidePants.itemHonorPrice[5] = 13125
fOutridersLizardhidePants.itemTokenPrice = new Array();
fOutridersLizardhidePants.itemTokenPrice[5] = new Array(0,0,0,40);
fOutridersLizardhidePants.itemStats = new Array();
fOutridersLizardhidePants.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Outrider's Lizardhide Pants</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>287 Armor<br>+22 Strength<br>+10 Agility<br>+22 Stamina<br>+22 Intellect<br>+9 Spirit<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 11.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutridersLizardhidePants; ++i;


var fOutridersLeatherPants = new RewardItem("horde","Outrider's Leather Pants","/shared/wow-com/images/basics/factions/warsong/leather_pants.gif");
fOutridersLeatherPants.itemHonorPrice = new Array();
fOutridersLeatherPants.itemHonorPrice[5] = 13125
fOutridersLeatherPants.itemTokenPrice = new Array();
fOutridersLeatherPants.itemTokenPrice[5] = new Array(0,0,0,40);
fOutridersLeatherPants.itemStats = new Array();
fOutridersLeatherPants.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Outrider's Leather Pants</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>257 Armor<br>+28 Agility<br>+27 Stamina<br>Durability 90 / 90<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutridersLeatherPants; ++i;



var fOutridersChainLeggings = new RewardItem("horde","Outrider's Chain Leggings","/shared/wow-com/images/basics/factions/warsong/chain_leggings.gif");
fOutridersChainLeggings.itemHonorPrice = new Array();
fOutridersChainLeggings.itemHonorPrice[5] = 13125
fOutridersChainLeggings.itemTokenPrice = new Array();
fOutridersChainLeggings.itemTokenPrice[5] = new Array(0,0,0,40);
fOutridersChainLeggings.itemStats = new Array();
fOutridersChainLeggings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Outrider's Chain Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>415 Armor<br>+35 Agility<br>+15 Stamina<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutridersChainLeggings; ++i;

var fOutridersMailLeggings = new RewardItem("horde","Outrider's Mail Leggings","/shared/wow-com/images/basics/factions/warsong/chain_leggings.gif");
fOutridersMailLeggings.itemHonorPrice = new Array();
fOutridersMailLeggings.itemHonorPrice[5] = 13125
fOutridersMailLeggings.itemTokenPrice = new Array();
fOutridersMailLeggings.itemTokenPrice[5] = new Array(0,0,0,40);
fOutridersMailLeggings.itemStats = new Array();
fOutridersMailLeggings.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Outrider's Mail Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>415 Armor<br>+14 Strength<br>+22 Stamina<br>+22 Intellect<br>Durability 105 / 105<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutridersMailLeggings; ++i;


var fOutridersPlateLegguards = new RewardItem("horde","Outrider's Plate Legguards","/shared/wow-com/images/basics/factions/warsong/plate_legguards.gif");
fOutridersPlateLegguards.itemHonorPrice = new Array();
fOutridersPlateLegguards.itemHonorPrice[5] = 13125
fOutridersPlateLegguards.itemTokenPrice = new Array();
fOutridersPlateLegguards.itemTokenPrice[5] = new Array(0,0,0,40);
fOutridersPlateLegguards.itemStats = new Array();
fOutridersPlateLegguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Outrider's Plate Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>737 Armor<br>+28 Strength<br>+27 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOutridersPlateLegguards; ++i;

var fSentinelsLamellarLegguards = new RewardItem("horde","Outrider's Lamellar Legguards","/shared/wow-com/images/basics/factions/warsong/lamellar_legguards.gif");
fSentinelsLamellarLegguards.itemHonorPrice = new Array();
fSentinelsLamellarLegguards.itemHonorPrice[5] = 11625
fSentinelsLamellarLegguards.itemTokenPrice = new Array();
fSentinelsLamellarLegguards.itemTokenPrice[5] = new Array(0,0,0,60);
fSentinelsLamellarLegguards.itemStats = new Array();
fSentinelsLamellarLegguards.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Outrider's Lamellar Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>737 Armor<br>+21 Strength<br>+21 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSentinelsLamellarLegguards; ++i;

//------END REWARDS DEFINITION------
