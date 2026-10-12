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

var fCombatHealingPotion = new RewardItem("alliance","Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_39.gif");
fCombatHealingPotion.itemMoneyPrice = new Array();
fCombatHealingPotion.itemMoneyPrice[0] = 1000
fCombatHealingPotion.itemHonorPrice = new Array();
fCombatHealingPotion.itemHonorPrice[0] = 1
fCombatHealingPotion.itemStats = new Array();
fCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 700 to 900 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCombatHealingPotion; ++i;

var fCombatManaPotion = new RewardItem("alliance","Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_81.gif");
fCombatManaPotion.itemMoneyPrice = new Array();
fCombatManaPotion.itemMoneyPrice[0] = 1000
fCombatManaPotion.itemHonorPrice = new Array();
fCombatManaPotion.itemHonorPrice[0] = 1
fCombatManaPotion.itemStats = new Array();
fCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 41<br>\
<span class=\"myGreen\">Use: Restores 900 to 1500 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("alliance","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(0,0,0,2);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("alliance","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(0,0,0,2);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("alliance","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(0,2,0,0);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("alliance","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(0,2,0,0);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("alliance","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(2,0,0,0);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("alliance","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(2,0,0,0);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("alliance","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(0,0,2,0);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("alliance","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(0,0,2,0);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fStarsLament = new RewardItem("alliance","Star's Lament","/info/basics/factions/images/icons/INV_Potion_82.gif");
fStarsLament.itemMoneyPrice = new Array();
fStarsLament.itemMoneyPrice[0] = 1200
fStarsLament.itemHonorPrice = new Array();
fStarsLament.itemHonorPrice[0] = 1
fStarsLament.itemStats = new Array();
fStarsLament.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Star's Lament<br>Binds when picked up<br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Restores 4200 mana over 30 sec. Must remain seated while drinking.<br></span>\
<span class=\myYellow\">\"Carefully extracted for warfare use.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStarsLament; ++i;

var fStarsTears = new RewardItem("alliance","Star's Tears","/info/basics/factions/images/icons/INV_Potion_82.gif");
fStarsTears.itemMoneyPrice = new Array();
fStarsTears.itemMoneyPrice[0] = 2500
fStarsTears.itemHonorPrice = new Array();
fStarsTears.itemHonorPrice[0] = 2
fStarsTears.itemStats = new Array();
fStarsTears.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Star's Tears<br>Binds when picked up<br>Requires Level 65<br>\
<span class=\"myGreen\">Use: Restores 7200 mana over 30 sec. Must remain seated while drinking.<br></span>\
<span class=\"myYellow\">\"Carefully extracted for warfare use.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStarsTears; ++i;

var fPrivatesTabard = new RewardItem("alliance","Private's Tabard","/info/basics/factions/images/icons/INV_Misc_TabardPVP_01.gif");
fPrivatesTabard.itemTokenPrice = new Array();
fPrivatesTabard.itemTokenPrice[0] = new Array(0,3,0,3);
fPrivatesTabard.itemStats = new Array();
fPrivatesTabard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Private's Tabard<br>Binds when picked up<br>Unique<br>Tabard</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPrivatesTabard; ++i;

var fKnightsColors = new RewardItem("alliance","Knight's Colors","/info/basics/factions/images/icons/INV_Misc_TabardPVP_03.gif");
fKnightsColors.itemTokenPrice = new Array();
fKnightsColors.itemTokenPrice[0] = new Array(20,20,0,20);
fKnightsColors.itemStats = new Array();
fKnightsColors.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Knight's Colors<br>Binds when picked up<br>Unique<br>Tabard</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fKnightsColors; ++i;

var fSergeantsCape = new RewardItem("alliance","Sergeant's Cape","/info/basics/factions/images/icons/INV_Misc_Cape_21.gif");
fSergeantsCape.itemHonorPrice = new Array();
fSergeantsCape.itemHonorPrice[0] = 95
fSergeantsCape.itemTokenPrice = new Array();
fSergeantsCape.itemTokenPrice[0] = new Array(0,10,0,0);
fSergeantsCape.itemStats = new Array();
fSergeantsCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Sergeant's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br><span class=\"myGreen\">66 Armor</span><br>+9 Stamina<br>Requires Level 30</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsCape; ++i;

var fSergeantsCape = new RewardItem("alliance","Sergeant's Cape","/info/basics/factions/images/icons/INV_Misc_Cape_21.gif");
fSergeantsCape.itemHonorPrice = new Array();
fSergeantsCape.itemHonorPrice[0] = 208
fSergeantsCape.itemTokenPrice = new Array();
fSergeantsCape.itemTokenPrice[0] = new Array(0,10,0,0);
fSergeantsCape.itemStats = new Array();
fSergeantsCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Sergeant's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br>96 Armor<br>+14 Stamina<br>Requires Level 45</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsCape; ++i;

var fSergeantsCape = new RewardItem("alliance","Sergeant's Cape","/info/basics/factions/images/icons/INV_Misc_Cape_21.gif");
fSergeantsCape.itemHonorPrice = new Array();
fSergeantsCape.itemHonorPrice[0] = 1530
fSergeantsCape.itemTokenPrice = new Array();
fSergeantsCape.itemTokenPrice[0] = new Array(0,10,0,0);
fSergeantsCape.itemStats = new Array();
fSergeantsCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Sergeant's Cape</span>\
<br>Binds when picked up<br>Unique<br>Back<br>115 Armor<br>+17 Stamina<br>Requires Level 58</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsCape; ++i;

var fMasterSergeantsInsignia = new RewardItem("alliance","Master Sergeant's Insignia","/info/basics/factions/images/icons/INV_Misc_MonsterScales_09.gif");
fMasterSergeantsInsignia.itemHonorPrice = new Array();
fMasterSergeantsInsignia.itemHonorPrice[0] = 95
fMasterSergeantsInsignia.itemTokenPrice = new Array();
fMasterSergeantsInsignia.itemTokenPrice[0] = new Array(0,0,0,20);
fMasterSergeantsInsignia.itemStats = new Array();
fMasterSergeantsInsignia.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Master Sergeant's Insignia</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+9 Stamina<br>+4 Spirit<br>Requires Level 30</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMasterSergeantsInsignia; ++i;

var fMasterSergeantsInsignia = new RewardItem("alliance","Master Sergeant's Insignia","/info/basics/factions/images/icons/INV_Misc_MonsterScales_09.gif");
fMasterSergeantsInsignia.itemHonorPrice = new Array();
fMasterSergeantsInsignia.itemHonorPrice[0] = 208
fMasterSergeantsInsignia.itemTokenPrice = new Array();
fMasterSergeantsInsignia.itemTokenPrice[0] = new Array(0,0,0,20);
fMasterSergeantsInsignia.itemStats = new Array();
fMasterSergeantsInsignia.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Master Sergeant's Insignia</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+14 Stamina<br>+6 Spirit<br>Requires Level 45</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMasterSergeantsInsignia; ++i;

var fMasterSergeantsInsignia = new RewardItem("alliance","Master Sergeant's Insignia","/info/basics/factions/images/icons/INV_Misc_MonsterScales_09.gif");
fMasterSergeantsInsignia.itemHonorPrice = new Array();
fMasterSergeantsInsignia.itemHonorPrice[0] = 1530
fMasterSergeantsInsignia.itemTokenPrice = new Array();
fMasterSergeantsInsignia.itemTokenPrice[0] = new Array(0,0,0,20);
fMasterSergeantsInsignia.itemStats = new Array();
fMasterSergeantsInsignia.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Master Sergeant's Insignia</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+17 Stamina<br>+7 Spirit<br>Requires Level 58</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMasterSergeantsInsignia; ++i;

var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Druid<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;

var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Hunter<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;

var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Mage<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;

var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Paladin<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;



var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Priest<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;

var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Rogue<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;

var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Shaman<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;



var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warlock<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;

var fAllianceBattleStandard = new RewardItem("alliance","Alliance Battle Standard","/info/basics/factions/images/icons/INV_BannerPVP_02.gif");
fAllianceBattleStandard.itemHonorPrice = new Array();
fAllianceBattleStandard.itemHonorPrice[0] = 15300
fAllianceBattleStandard.itemStats = new Array();
fAllianceBattleStandard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Alliance Battle Standard<br>Binds when picked up<br>\
<span class=\"myGreen\">Use: Place a Battle Standard with 1500 health that increases the maximum health of all party members that stay within 45 yards of the Battle Standard by 15%.  Lasts 2 min. The Battle Standard may only be used in PvP Battlegrounds.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAllianceBattleStandard; ++i;

var fInsigniaOfTheAlliance = new RewardItem("alliance","Insignia of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fInsigniaOfTheAlliance.itemHonorPrice = new Array();
fInsigniaOfTheAlliance.itemHonorPrice[0] = 2805
fInsigniaOfTheAlliance.itemStats = new Array();
fInsigniaOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warrior<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheAlliance; ++i;


var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;



var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;

var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;

var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;


var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;

var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;

var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;

var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;

var fMedallionOfTheAlliance = new RewardItem("alliance","Medallion of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_01.gif");
fMedallionOfTheAlliance.itemHonorPrice = new Array();
fMedallionOfTheAlliance.itemHonorPrice[0] = 16983
fMedallionOfTheAlliance.itemStats = new Array();
fMedallionOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheAlliance; ++i;

var fTalismanOfTheAlliance = new RewardItem("alliance","Talisman of the Alliance","/info/basics/factions/images/icons/INV_Jewelry_Talisman_10.gif");
fTalismanOfTheAlliance.itemHonorPrice = new Array();
fTalismanOfTheAlliance.itemHonorPrice[0] = 22950
fTalismanOfTheAlliance.itemTokenPrice = new Array();
fTalismanOfTheAlliance.itemTokenPrice[0] = new Array(0,0,10,0);
fTalismanOfTheAlliance.itemStats = new Array();
fTalismanOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Talisman of the Alliance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 34.</span>\
<br>\
<span class=\"myGreen\">Use: Heal self for 877 to 969 damage.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTalismanOfTheAlliance; ++i;

var fBandOfTriumph = new RewardItem("alliance","Band of Triumph","/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fBandOfTriumph.itemHonorPrice = new Array();
fBandOfTriumph.itemHonorPrice[0] = 11934
fBandOfTriumph.itemTokenPrice = new Array();
fBandOfTriumph.itemTokenPrice[0] = new Array(10,0,0,0);
fBandOfTriumph.itemStats = new Array();
fBandOfTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Band of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+21 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTriumph; ++i;

var fBandOfDominance = new RewardItem("alliance","Band of Dominance","/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fBandOfDominance.itemHonorPrice = new Array();
fBandOfDominance.itemHonorPrice[0] = 11934
fBandOfDominance.itemTokenPrice = new Array();
fBandOfDominance.itemTokenPrice[0] = new Array(10,0,0,0);
fBandOfDominance.itemStats = new Array();
fBandOfDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Band of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+27 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfDominance; ++i;

var fPendantOfTriumph = new RewardItem("alliance","Pendant of Triumph","/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fPendantOfTriumph.itemHonorPrice = new Array();
fPendantOfTriumph.itemHonorPrice[0] = 15300
fPendantOfTriumph.itemTokenPrice = new Array();
fPendantOfTriumph.itemTokenPrice[0] = new Array(0,0,10,0);
fPendantOfTriumph.itemStats = new Array();
fPendantOfTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pendant of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+27 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Hit Rating</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 8.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPendantOfTriumph; ++i;

var fPendantOfDominance = new RewardItem("alliance","Pendant of Dominance","/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fPendantOfDominance.itemHonorPrice = new Array();
fPendantOfDominance.itemHonorPrice[0] = 15300
fPendantOfDominance.itemTokenPrice = new Array();
fPendantOfDominance.itemTokenPrice[0] = new Array(0,0,10,0);
fPendantOfDominance.itemStats = new Array();
fPendantOfDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pendant of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+30 Stamina<br>+10 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Critical Strike Rating</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPendantOfDominance; ++i;

var fBoldOrnateRuby = new RewardItem("alliance","Bold Ornate Ruby","/info/basics/factions/images/icons/INV_Misc_Gem_Ruby_02.gif");
fBoldOrnateRuby.itemHonorPrice = new Array();
fBoldOrnateRuby.itemHonorPrice[0] = 6885
fBoldOrnateRuby.itemStats = new Array();
fBoldOrnateRuby.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bold Ornate Ruby</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+20 Attack Power<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBoldOrnateRuby; ++i;

var fRunedOrnateRuby = new RewardItem("alliance","Runed Ornate Ruby","/info/basics/factions/images/icons/INV_Misc_Gem_Bloodstone_01.gif");
fRunedOrnateRuby.itemHonorPrice = new Array();
fRunedOrnateRuby.itemHonorPrice[0] = 6885
fRunedOrnateRuby.itemStats = new Array();
fRunedOrnateRuby.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Runed Ornate Ruby</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+12 Spell Damage<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRunedOrnateRuby; ++i;

var fSmoothOrnateDawnstone = new RewardItem("alliance","Smooth Ornate Dawnstone","/info/basics/factions/images/icons/INV_Misc_Gem_Topaz_01.gif");
fSmoothOrnateDawnstone.itemHonorPrice = new Array();
fSmoothOrnateDawnstone.itemHonorPrice[0] = 6885
fSmoothOrnateDawnstone.itemStats = new Array();
fSmoothOrnateDawnstone.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Smooth Ornate Dawnstone</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+10 Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSmoothOrnateDawnstone; ++i;

var fGleamingOrnateDawnstone = new RewardItem("alliance","Gleaming Ornate Dawnstone","/info/basics/factions/images/icons/INV_Misc_Gem_Topaz_02.gif");
fGleamingOrnateDawnstone.itemHonorPrice = new Array();
fGleamingOrnateDawnstone.itemHonorPrice[0] = 6885
fGleamingOrnateDawnstone.itemStats = new Array();
fGleamingOrnateDawnstone.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gleaming Ornate Dawnstone</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+10 Spell Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGleamingOrnateDawnstone; ++i;

var fInscribedOrnateTopaz = new RewardItem("alliance","Inscribed Ornate Topaz","/info/basics/factions/images/icons/INV_Misc_Gem_Opal_01.gif");
fInscribedOrnateTopaz.itemHonorPrice = new Array();
fInscribedOrnateTopaz.itemHonorPrice[0] = 8500
fInscribedOrnateTopaz.itemStats = new Array();
fInscribedOrnateTopaz.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inscribed Ornate Topaz</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+10 Attack Power, +5 Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Red or Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscribedOrnateTopaz; ++i;

var fPotentOrnateTopaz = new RewardItem("alliance","Potent Ornate Topaz","/info/basics/factions/images/icons/INV_Misc_Gem_Opal_02.gif");
fPotentOrnateTopaz.itemHonorPrice = new Array();
fPotentOrnateTopaz.itemHonorPrice[0] = 8500
fPotentOrnateTopaz.itemStats = new Array();
fPotentOrnateTopaz.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Potent Ornate Topaz</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+6 Spell Damage, +5 Spell Crit Rating<br>\
<span class=\"myYellow\">\"Matches a Red or Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPotentOrnateTopaz; ++i;

//-------------------------------------------------------------------
//---Horde below

var fCombatHealingPotion = new RewardItem("horde","Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_39.gif");
fCombatHealingPotion.itemMoneyPrice = new Array();
fCombatHealingPotion.itemMoneyPrice[0] = 1000
fCombatHealingPotion.itemHonorPrice = new Array();
fCombatHealingPotion.itemHonorPrice[0] = 1
fCombatHealingPotion.itemStats = new Array();
fCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 35<br>\
<span class=\"myGreen\">Use: Restores 700 to 900 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCombatHealingPotion; ++i;

var fCombatManaPotion = new RewardItem("horde","Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_81.gif");
fCombatManaPotion.itemMoneyPrice = new Array();
fCombatManaPotion.itemMoneyPrice[0] = 1000
fCombatManaPotion.itemHonorPrice = new Array();
fCombatManaPotion.itemHonorPrice[0] = 1
fCombatManaPotion.itemStats = new Array();
fCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 41<br>\
<span class=\"myGreen\">Use: Restores 900 to 1500 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("horde","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(0,0,0,2);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("horde","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(0,0,0,2);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("horde","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(0,2,0,0);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("horde","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(0,2,0,0);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("horde","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(2,0,0,0);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("horde","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(2,0,0,0);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fMajorCombatHealingPotion = new RewardItem("horde","Major Combat Healing Potion","/info/basics/factions/images/icons/INV_Potion_40.gif");
fMajorCombatHealingPotion.itemTokenPrice = new Array();
fMajorCombatHealingPotion.itemTokenPrice[0] = new Array(0,0,2,0);
fMajorCombatHealingPotion.itemStats = new Array();
fMajorCombatHealingPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Healing Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1050 to 1750 health.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatHealingPotion; ++i;

var fMajorCombatManaPotion = new RewardItem("horde","Major Combat Mana Potion","/info/basics/factions/images/icons/INV_Potion_82.gif");
fMajorCombatManaPotion.itemTokenPrice = new Array();
fMajorCombatManaPotion.itemTokenPrice[0] = new Array(0,0,2,0);
fMajorCombatManaPotion.itemStats = new Array();
fMajorCombatManaPotion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Major Combat Mana Potion<br>Binds when picked up<br>Unique (10)<br>Requires Level 61<br>\
<span class=\"myGreen\">Use: Restores 1350 to 2250 mana.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMajorCombatManaPotion; ++i;

var fStarsLament = new RewardItem("horde","Star's Lament","/info/basics/factions/images/icons/INV_Potion_82.gif");
fStarsLament.itemMoneyPrice = new Array();
fStarsLament.itemMoneyPrice[0] = 1200
fStarsLament.itemHonorPrice = new Array();
fStarsLament.itemHonorPrice[0] = 1
fStarsLament.itemStats = new Array();
fStarsLament.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Star's Lament<br>Binds when picked up<br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Restores 4200 mana over 30 sec. Must remain seated while drinking.<br></span>\
<span class=\myYellow\">\"Carefully extracted for warfare use.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStarsLament; ++i;

var fStarsTears = new RewardItem("horde","Star's Tears","/info/basics/factions/images/icons/INV_Potion_82.gif");
fStarsTears.itemMoneyPrice = new Array();
fStarsTears.itemMoneyPrice[0] = 2500
fStarsTears.itemHonorPrice = new Array();
fStarsTears.itemHonorPrice[0] = 2
fStarsTears.itemStats = new Array();
fStarsTears.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Star's Tears<br>Binds when picked up<br>Requires Level 65<br>\
<span class=\"myGreen\">Use: Restores 7200 mana over 30 sec. Must remain seated while drinking.<br></span>\
<span class=\"myYellow\">\"Carefully extracted for warfare use.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStarsTears; ++i


  
var fScoutsTabard = new RewardItem("horde","Scout's Tabard","/info/basics/factions/images/icons/INV_Misc_TabardPVP_02.gif");
fScoutsTabard.itemTokenPrice = new Array();
fScoutsTabard.itemTokenPrice[0] = new Array(0,3,0,3);
fScoutsTabard.itemStats = new Array();
fScoutsTabard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Scout's Tabard<br>Binds when picked up<br>Unique<br>Tabard</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fScoutsTabard; ++i;

var fStoneGuardsHerald = new RewardItem("horde","Stone Guard's Herald","/info/basics/factions/images/icons/INV_Misc_TabardPVP_04.gif");
fStoneGuardsHerald.itemTokenPrice = new Array();
fStoneGuardsHerald.itemTokenPrice[0] = new Array(20,20,0,20);
fStoneGuardsHerald.itemStats = new Array();
fStoneGuardsHerald.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Stone Guard's Herald<br>Binds when picked up<br>Unique<br>Tabard</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStoneGuardsHerald; ++i;

var fSergeantsCape = new RewardItem("horde","Sergeant's Cloak","/info/basics/factions/images/icons/INV_Misc_Cape_21.gif");
fSergeantsCape.itemHonorPrice = new Array();
fSergeantsCape.itemHonorPrice[0] = 95
fSergeantsCape.itemTokenPrice = new Array();
fSergeantsCape.itemTokenPrice[0] = new Array(0,10,0,0);
fSergeantsCape.itemStats = new Array();
fSergeantsCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Sergeant's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br><span class=\"myGreen\">66 Armor</span><br>+9 Stamina<br>Requires Level 30</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsCape; ++i;

var fSergeantsCape = new RewardItem("horde","Sergeant's Cloak","/info/basics/factions/images/icons/INV_Misc_Cape_21.gif");
fSergeantsCape.itemHonorPrice = new Array();
fSergeantsCape.itemHonorPrice[0] = 208
fSergeantsCape.itemTokenPrice = new Array();
fSergeantsCape.itemTokenPrice[0] = new Array(0,10,0,0);
fSergeantsCape.itemStats = new Array();
fSergeantsCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Sergeant's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br>96 Armor<br>+14 Stamina<br>Requires Level 45</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsCape; ++i;

var fSergeantsCape = new RewardItem("horde","Sergeant's Cloak","/info/basics/factions/images/icons/INV_Misc_Cape_21.gif");
fSergeantsCape.itemHonorPrice = new Array();
fSergeantsCape.itemHonorPrice[0] = 1530
fSergeantsCape.itemTokenPrice = new Array();
fSergeantsCape.itemTokenPrice[0] = new Array(0,10,0,0);
fSergeantsCape.itemStats = new Array();
fSergeantsCape.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Sergeant's Cloak</span>\
<br>Binds when picked up<br>Unique<br>Back<br>115 Armor<br>+17 Stamina<br>Requires Level 58</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSergeantsCape; ++i;

var fMasterSergeantsInsignia = new RewardItem("horde","Senior Sergeant's Insignia","/info/basics/factions/images/icons/INV_Misc_MonsterScales_15.gif");
fMasterSergeantsInsignia.itemHonorPrice = new Array();
fMasterSergeantsInsignia.itemHonorPrice[0] = 95
fMasterSergeantsInsignia.itemTokenPrice = new Array();
fMasterSergeantsInsignia.itemTokenPrice[0] = new Array(0,0,0,20);
fMasterSergeantsInsignia.itemStats = new Array();
fMasterSergeantsInsignia.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Senior Sergeant's Insignia</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+9 Stamina<br>+4 Spirit<br>Requires Level 30</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMasterSergeantsInsignia; ++i;

var fMasterSergeantsInsignia = new RewardItem("horde","Senior Sergeant's Insignia","/info/basics/factions/images/icons/INV_Misc_MonsterScales_15.gif");
fMasterSergeantsInsignia.itemHonorPrice = new Array();
fMasterSergeantsInsignia.itemHonorPrice[0] = 208
fMasterSergeantsInsignia.itemTokenPrice = new Array();
fMasterSergeantsInsignia.itemTokenPrice[0] = new Array(0,0,0,20);
fMasterSergeantsInsignia.itemStats = new Array();
fMasterSergeantsInsignia.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Senior Sergeant's Insignia</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+14 Stamina<br>+6 Spirit<br>Requires Level 45</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMasterSergeantsInsignia; ++i;

var fMasterSergeantsInsignia = new RewardItem("horde","Senior Sergeant's Insignia","/info/basics/factions/images/icons/INV_Misc_MonsterScales_15.gif");
fMasterSergeantsInsignia.itemHonorPrice = new Array();
fMasterSergeantsInsignia.itemHonorPrice[0] = 1530
fMasterSergeantsInsignia.itemTokenPrice = new Array();
fMasterSergeantsInsignia.itemTokenPrice[0] = new Array(0,0,0,20);
fMasterSergeantsInsignia.itemStats = new Array();
fMasterSergeantsInsignia.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Senior Sergeant's Insignia</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+17 Stamina<br>+7 Spirit<br>Requires Level 58</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMasterSergeantsInsignia; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Druid<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Hunter<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Mage<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Paladin<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Priest<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Rogue<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character./span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Shaman<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warlock<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fInsigniaOfTheHorde = new RewardItem("horde","Insignia of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fInsigniaOfTheHorde.itemHonorPrice = new Array();
fInsigniaOfTheHorde.itemHonorPrice[0] = 2805
fInsigniaOfTheHorde.itemStats = new Array();
fInsigniaOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Insignia of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warrior<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInsigniaOfTheHorde; ++i;

var fHordeBattleStandard = new RewardItem("horde","Horde Battle Standard","/info/basics/factions/images/icons/INV_BannerPVP_01.gif");
fHordeBattleStandard.itemHonorPrice = new Array();
fHordeBattleStandard.itemHonorPrice[0] = 15300
fHordeBattleStandard.itemStats = new Array();
fHordeBattleStandard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Horde Battle Standard<br>Binds when picked up<br>\
<span class=\"myGreen\">Use: Place a Battle Standard with 1500 health that increases the maximum health of all party members that stay within 45 yards of the Battle Standard by 15%.  Lasts 2 min. The Battle Standard may only be used in PvP Battlegrounds.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHordeBattleStandard; ++i;




var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Druid<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;



var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Hunter<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;

var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Mage<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;




var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Paladin<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;



var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Priest<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;

var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Rogue<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;

var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Shaman<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;

var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warlock<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;

var fMedallionOfTheHorde = new RewardItem("horde","Medallion of the Horde","/info/basics/factions/images/icons/INV_Jewelry_TrinketPVP_02.gif");
fMedallionOfTheHorde.itemHonorPrice = new Array();
fMedallionOfTheHorde.itemHonorPrice[0] = 16983
fMedallionOfTheHorde.itemStats = new Array();
fMedallionOfTheHorde.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Medallion of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Classes: Warrior<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Use: Removes all movement impairing effects and all effects that cause loss of control of your character.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheHorde; ++i;

var fTalismanOfTheAlliance = new RewardItem("horde","Talisman of the Horde","/info/basics/factions/images/icons/INV_Jewelry_Talisman_09.gif");
fTalismanOfTheAlliance.itemHonorPrice = new Array();
fTalismanOfTheAlliance.itemHonorPrice[0] = 22950
fTalismanOfTheAlliance.itemTokenPrice = new Array();
fTalismanOfTheAlliance.itemTokenPrice[0] = new Array(0,0,10,0);
fTalismanOfTheAlliance.itemStats = new Array();
fTalismanOfTheAlliance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Talisman of the Horde</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 34.</span>\
<br>\
<span class=\"myGreen\">Use: Heal self for 877 to 969 damage.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTalismanOfTheAlliance; ++i;

var fBandOfTriumph = new RewardItem("horde","Band of Triumph","/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fBandOfTriumph.itemHonorPrice = new Array();
fBandOfTriumph.itemHonorPrice[0] = 11934
fBandOfTriumph.itemTokenPrice = new Array();
fBandOfTriumph.itemTokenPrice[0] = new Array(10,0,0,0);
fBandOfTriumph.itemStats = new Array();
fBandOfTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Band of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+21 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 32.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTriumph; ++i;


var fBandOfDominance = new RewardItem("horde","Band of Dominance","/info/basics/factions/images/icons/INV_Jewelry_Ring_60.gif");
fBandOfDominance.itemHonorPrice = new Array();
fBandOfDominance.itemHonorPrice[0] = 11934
fBandOfDominance.itemTokenPrice = new Array();
fBandOfDominance.itemTokenPrice[0] = new Array(10,0,0,0);
fBandOfDominance.itemStats = new Array();
fBandOfDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Band of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+27 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfDominance; ++i;

var fPendantOfTriumph = new RewardItem("horde","Pendant of Triumph","/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fPendantOfTriumph.itemHonorPrice = new Array();
fPendantOfTriumph.itemHonorPrice[0] = 15300
fPendantOfTriumph.itemTokenPrice = new Array();
fPendantOfTriumph.itemTokenPrice[0] = new Array(0,0,10,0);
fPendantOfTriumph.itemStats = new Array();
fPendantOfTriumph.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pendant of Triumph</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+28 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Hit Rating</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 36.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPendantOfTriumph; ++i;

var fPendantOfDominance = new RewardItem("horde","Pendant of Dominance","/info/basics/factions/images/icons/INV_Jewelry_Necklace_36.gif");
fPendantOfDominance.itemHonorPrice = new Array();
fPendantOfDominance.itemHonorPrice[0] = 15300
fPendantOfDominance.itemTokenPrice = new Array();
fPendantOfDominance.itemTokenPrice[0] = new Array(0,0,10,0);
fPendantOfDominance.itemStats = new Array();
fPendantOfDominance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pendant of Dominance</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+31 Stamina<br>+12 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Critical Strike Rating</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPendantOfDominance; ++i;

var fBoldOrnateRuby = new RewardItem("horde","Bold Ornate Ruby","/info/basics/factions/images/icons/INV_Misc_Gem_Ruby_02.gif");
fBoldOrnateRuby.itemHonorPrice = new Array();
fBoldOrnateRuby.itemHonorPrice[0] = 6885
fBoldOrnateRuby.itemStats = new Array();
fBoldOrnateRuby.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bold Ornate Ruby</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+20 Attack Power<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBoldOrnateRuby; ++i;

var fRunedOrnateRuby = new RewardItem("horde","Runed Ornate Ruby","/info/basics/factions/images/icons/INV_Misc_Gem_Bloodstone_01.gif");
fRunedOrnateRuby.itemHonorPrice = new Array();
fRunedOrnateRuby.itemHonorPrice[0] = 6885
fRunedOrnateRuby.itemStats = new Array();
fRunedOrnateRuby.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Runed Ornate Ruby</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+12 Spell Damage<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRunedOrnateRuby; ++i;

var fSmoothOrnateDawnstone = new RewardItem("horde","Smooth Ornate Dawnstone","/info/basics/factions/images/icons/INV_Misc_Gem_Topaz_01.gif");
fSmoothOrnateDawnstone.itemHonorPrice = new Array();
fSmoothOrnateDawnstone.itemHonorPrice[0] = 6885
fSmoothOrnateDawnstone.itemStats = new Array();
fSmoothOrnateDawnstone.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Smooth Ornate Dawnstone</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+10 Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSmoothOrnateDawnstone; ++i;

var fGleamingOrnateDawnstone = new RewardItem("horde","Gleaming Ornate Dawnstone","/info/basics/factions/images/icons/INV_Misc_Gem_Topaz_02.gif");
fGleamingOrnateDawnstone.itemHonorPrice = new Array();
fGleamingOrnateDawnstone.itemHonorPrice[0] = 6885
fGleamingOrnateDawnstone.itemStats = new Array();
fGleamingOrnateDawnstone.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gleaming Ornate Dawnstone</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+10 Spell Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGleamingOrnateDawnstone; ++i;

var fInscribedOrnateTopaz = new RewardItem("horde","Inscribed Ornate Topaz","/info/basics/factions/images/icons/INV_Misc_Gem_Opal_01.gif");
fInscribedOrnateTopaz.itemHonorPrice = new Array();
fInscribedOrnateTopaz.itemHonorPrice[0] = 8500
fInscribedOrnateTopaz.itemStats = new Array();
fInscribedOrnateTopaz.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inscribed Ornate Topaz</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+10 Attack Power, +5 Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Red or Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscribedOrnateTopaz; ++i;

var fPotentOrnateTopaz = new RewardItem("horde","Potent Ornate Topaz","/info/basics/factions/images/icons/INV_Misc_Gem_Opal_02.gif");
fPotentOrnateTopaz.itemHonorPrice = new Array();
fPotentOrnateTopaz.itemHonorPrice[0] = 8500
fPotentOrnateTopaz.itemStats = new Array();
fPotentOrnateTopaz.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Potent Ornate Topaz</span>\
<br>Binds when picked up<br>Unique-Equipped<br>+6 Spell Damage, +5 Spell Crit Rating<br>\
<span class=\"myYellow\">\"Matches a Red or Yellow Socket.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPotentOrnateTopaz; ++i;

//------END REWARDS DEFINITION------
