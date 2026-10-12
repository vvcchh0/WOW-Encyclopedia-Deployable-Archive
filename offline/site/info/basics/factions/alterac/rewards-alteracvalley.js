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

var fSuperiorHealingDraught = new RewardItem("alliance","Superior Healing Draught","/shared/wow-com/images/basics/factions/alteracvalley/superiorhealingdraught.gif");
fSuperiorHealingDraught.itemMoneyPrice = new Array();
fSuperiorHealingDraught.itemMoneyPrice[0] = 500;
fSuperiorHealingDraught.itemHonorPrice = new Array();
fSuperiorHealingDraught.itemHonorPrice[0] = 5
fSuperiorHealingDraught.itemStats = new Array();
fSuperiorHealingDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Superior Healing Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 health. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fSuperiorHealingDraught; i++;



var fSuperiorManaDraught = new RewardItem("alliance","Superior Mana Draught","/shared/wow-com/images/basics/factions/alteracvalley/superiormanadraught.gif");
fSuperiorManaDraught.itemMoneyPrice = new Array();
fSuperiorManaDraught.itemMoneyPrice[0] = 500;
fSuperiorManaDraught.itemHonorPrice = new Array();
fSuperiorManaDraught.itemHonorPrice[0] = 5
fSuperiorManaDraught.itemStats = new Array();
fSuperiorManaDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Superior Mana Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 mana. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fSuperiorManaDraught; i++;



var fStormpikeBattleTabard = new RewardItem("alliance","Stormpike Battle Tabard","/shared/wow-com/images/basics/factions/alteracvalley/stormpikebattletabard.gif");
fStormpikeBattleTabard.itemTokenPrice = new Array();
fStormpikeBattleTabard.itemTokenPrice[0] = new Array(60,0,0,0);
fStormpikeBattleTabard.itemStats = new Array();
fStormpikeBattleTabard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\">Stormpike Battle Tabard<br>Binds when picked up<br>Unique<br>Tabard</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeBattleTabard; ++i;







var fAlteracHeavyRuneclothBandage = new RewardItem("alliance","Alterac Heavy Runecloth Bandage","/shared/wow-com/images/basics/factions/alteracvalley/alteracheavyruneclothbandag.gif");
fAlteracHeavyRuneclothBandage.itemMoneyPrice = new Array();
fAlteracHeavyRuneclothBandage.itemMoneyPrice[0] = 8000;
fAlteracHeavyRuneclothBandage.itemStats = new Array();
fAlteracHeavyRuneclothBandage.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Alterac Heavy Runecloth Bandage</b></span><br>\
Binds when picked up<br>\
Requires First Aid (225)<br>\
<span class='myGreen'>Use: Heals 2000 damage over 8 sec.</span><br>\
<span class='myYellow'>&quot;May only be used in Alterac Valley.&quot;</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fAlteracHeavyRuneclothBandage; i++;



var fBottledAlteracSpringWater = new RewardItem("alliance","Bottled Alterac Spring Water","/shared/wow-com/images/basics/factions/alteracvalley/bottledalteracspringwater.gif");
fBottledAlteracSpringWater.itemMoneyPrice = new Array();
fBottledAlteracSpringWater.itemMoneyPrice[0] = 5000;
fBottledAlteracSpringWater.itemStats = new Array();
fBottledAlteracSpringWater.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Bottled Alterac Spring Water</b></span><br>\
Binds when picked up<br>\
Requires Level 55<br>\
<span class='myGreen'>Use: Restores 4410 mana over 30 sec. Must remain seated while drinking. Also increases your Spirit by 10 for 10 min.</span><br>\
<span class='myYellow'>&quot;From the mountain springs of Alterac!&quot;</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fBottledAlteracSpringWater; i++;










var fMajorHealingDraught = new RewardItem("alliance","Major Healing Draught","/shared/wow-com/images/basics/factions/alteracvalley/majorhealingdraught.gif");
fMajorHealingDraught.itemMoneyPrice = new Array();
fMajorHealingDraught.itemMoneyPrice[0] = 1000;
fMajorHealingDraught.itemHonorPrice = new Array();
fMajorHealingDraught.itemHonorPrice[0] = 2
fMajorHealingDraught.itemStats = new Array();
fMajorHealingDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Major Healing Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 45<br>\
<span class='myGreen'>Use: Restores 980 to 1260 health. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fMajorHealingDraught; i++; 




var fMajorManaDraught = new RewardItem("alliance","Major Mana Draught","/shared/wow-com/images/basics/factions/alteracvalley/majormanadraught.gif");
fMajorManaDraught.itemMoneyPrice = new Array();
fMajorManaDraught.itemMoneyPrice[0] = 1000;
fMajorManaDraught.itemHonorPrice = new Array();
fMajorManaDraught.itemHonorPrice[0] = 2
fMajorManaDraught.itemStats = new Array();
fMajorManaDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Major Mana Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 45<br>\
<span class='myGreen'>Use: Restores 980 to 1260 mana. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fMajorManaDraught; i++;




var fStormpikeSoldiersCloak = new RewardItem("alliance","Stormpike Soldier's Cloak","/shared/wow-com/images/basics/factions/alteracvalley/stormpikecloak.gif");
fStormpikeSoldiersCloak.itemHonorPrice = new Array();
fStormpikeSoldiersCloak.itemHonorPrice[0] = 1800
fStormpikeSoldiersCloak.itemTokenPrice = new Array();
fStormpikeSoldiersCloak.itemTokenPrice[0] = new Array(10,0,0,0);
fStormpikeSoldiersCloak.itemStats = new Array();
fStormpikeSoldiersCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Soldier's Cloak</span>\
<br>Binds when picked up<br>Back<br>43 Armor<br>+11 Stamina<br>+5 Frost Resistance<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeSoldiersCloak; ++i;



var fStormpikeSagesCloak = new RewardItem("alliance","Stormpike Sage's Cloak","/shared/wow-com/images/basics/factions/alteracvalley/stormpikecloak.gif");
fStormpikeSagesCloak.itemHonorPrice = new Array();
fStormpikeSagesCloak.itemHonorPrice[0] = 1800
fStormpikeSagesCloak.itemTokenPrice = new Array();
fStormpikeSagesCloak.itemTokenPrice[0] = new Array(10,0,0,0);
fStormpikeSagesCloak.itemStats = new Array();
fStormpikeSagesCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Sage's Cloak</span>\
<br>Binds when picked up<br>Back<br>43 Armor<br>+11 Stamina<br>+5 Frost Resistance<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeSagesCloak; ++i;


var fStormpikeSoldiersPendant = new RewardItem("alliance","Stormpike Soldier's Pendant","/shared/wow-com/images/basics/factions/alteracvalley/stormpikesoldierspendant.gif");
fStormpikeSoldiersPendant.itemHonorPrice = new Array();
fStormpikeSoldiersPendant.itemHonorPrice[0] = 1800
fStormpikeSoldiersPendant.itemTokenPrice = new Array();
fStormpikeSoldiersPendant.itemTokenPrice[0] = new Array(20,0,0,0);
fStormpikeSoldiersPendant.itemStats = new Array();
fStormpikeSoldiersPendant.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Soldier's Pendant</span>\
<br>Binds when picked up<br>Neck<br>+15 Stamina<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases attack power by 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeSoldiersPendant; ++i;


var fStormpikeSagesPendant = new RewardItem("alliance","Stormpike Sage's Pendant","/shared/wow-com/images/basics/factions/alteracvalley/stormpikesagespendant.gif");
fStormpikeSagesPendant.itemHonorPrice = new Array();
fStormpikeSagesPendant.itemHonorPrice[0] = 1800
fStormpikeSagesPendant.itemTokenPrice = new Array();
fStormpikeSagesPendant.itemTokenPrice[0] = new Array(20,0,0,0);
fStormpikeSagesPendant.itemStats = new Array();
fStormpikeSagesPendant.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Sage's Pendant</span>\
<br>Binds when picked up<br>Neck<br>+10 Stamina<br>+10 Intellect<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeSagesPendant; ++i;



var fStormpikePlateGirdle = new RewardItem("alliance","Stormpike Plate Girdle","/shared/wow-com/images/basics/factions/alteracvalley/stormpikeplategirdle.gif");
fStormpikePlateGirdle.itemHonorPrice = new Array();
fStormpikePlateGirdle.itemHonorPrice[0] = 3300
fStormpikePlateGirdle.itemTokenPrice = new Array();
fStormpikePlateGirdle.itemTokenPrice[0] = new Array(20,0,0,0);
fStormpikePlateGirdle.itemStats = new Array();
fStormpikePlateGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Plate Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>353 Armor<br>+18 Strength<br>+7 Agility<br>+8 Stamina<br>+5 Frost Resistance<br>Durability 45 / 45<br>Requires Level 55</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikePlateGirdle; ++i;






var fStormpikeMailGirdle = new RewardItem("alliance","Stormpike Mail Girdle","/shared/wow-com/images/basics/factions/alteracvalley/stormpikemailgirdle.gif");
fStormpikeMailGirdle.itemHonorPrice = new Array();
fStormpikeMailGirdle.itemHonorPrice[0] = 3300
fStormpikeMailGirdle.itemTokenPrice = new Array();
fStormpikeMailGirdle.itemTokenPrice[0] = new Array(20,0,0,0);
fStormpikeMailGirdle.itemStats = new Array();
fStormpikeMailGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Mail Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>199 Armor<br>+12 Agility<br>+12 Stamina<br>+12 Intellect<br>+5 Frost Resistance<br>Durability 40 / 40<br>Requires Level 55</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeMailGirdle; ++i;



var fStormpikeLeatherGirdle = new RewardItem("alliance","Stormpike Leather Girdle","/shared/wow-com/images/basics/factions/alteracvalley/stormpikeleathergirdle.gif");
fStormpikeLeatherGirdle.itemHonorPrice = new Array();
fStormpikeLeatherGirdle.itemHonorPrice[0] = 3300
fStormpikeLeatherGirdle.itemTokenPrice = new Array();
fStormpikeLeatherGirdle.itemTokenPrice[0] = new Array(20,0,0,0);
fStormpikeLeatherGirdle.itemStats = new Array();
fStormpikeLeatherGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Leather Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>95 Armor<br>+11 Strength<br>+10 Agility<br>+15 Stamina<br>+5 Frost Resistance<br>Durability 35 / 35<br>Requires Level 55</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeLeatherGirdle; ++i;



var fStormpikeClothGirdle = new RewardItem("alliance","Stormpike Cloth Girdle","/shared/wow-com/images/basics/factions/alteracvalley/stormpikeclothgirdle.gif");
fStormpikeClothGirdle.itemHonorPrice = new Array();
fStormpikeClothGirdle.itemHonorPrice[0] = 3300
fStormpikeClothGirdle.itemTokenPrice = new Array();
fStormpikeClothGirdle.itemTokenPrice[0] = new Array(20,0,0,0);
fStormpikeClothGirdle.itemStats = new Array();
fStormpikeClothGirdle.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Cloth Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>48 Armor<br>+11 Stamina<br>+10 Intellect<br>+5 Frost Resistance<br>Durability 30 / 30<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeClothGirdle; ++i;




var fAlteracMannaBiscuit = new RewardItem("alliance","Alterac Manna Biscuit","/shared/wow-com/images/basics/factions/alteracvalley/alteracmannabiscuit.gif");
fAlteracMannaBiscuit.itemMoneyPrice = new Array();
fAlteracMannaBiscuit.itemMoneyPrice[0] = 7000;
fAlteracMannaBiscuit.itemStats = new Array();
fAlteracMannaBiscuit.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Alterac Manna Biscuit</b></span><br>\
Binds when picked up<br>\
Requires Level 51<br>\
<span class='myGreen'>Use: Restores 4410 health and 4410 mana over 30 sec. Must remain seated while eating.</span></div>\
</td></tr></table>";
RewardItems[i] = fAlteracMannaBiscuit; i++;

var fIceThreadedArrow = new RewardItem("alliance","Ice Threaded Arrow","/shared/wow-com/images/basics/factions/alteracvalley/icethreadedarrow.gif");
fIceThreadedArrow.itemMoneyPrice = new Array();
fIceThreadedArrow.itemMoneyPrice[0] = 6000;
fIceThreadedArrow.itemHonorPrice = new Array();
fIceThreadedArrow.itemHonorPrice[0] = 1
fIceThreadedArrow.itemStats = new Array();
fIceThreadedArrow.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myGreen'><b>Ice Threaded Arrow</b></span><br>\
Binds when picked up<br>\
Projectile<span class='myRight'>Arrow</span><br>\
Adds 16.5 damage per second<br>\
Requires Level 51</div>\
</td></tr></table>";
RewardItems[i] = fIceThreadedArrow; i++;



var fIceThreadedBullet = new RewardItem("alliance","Ice Threaded Bullet","/shared/wow-com/images/basics/factions/alteracvalley/icethreadedbullet.gif");
fIceThreadedBullet.itemMoneyPrice = new Array();
fIceThreadedBullet.itemMoneyPrice[0] = 6000;
fIceThreadedBullet.itemHonorPrice = new Array();
fIceThreadedBullet.itemHonorPrice[0] = 1
fIceThreadedBullet.itemStats = new Array();
fIceThreadedBullet.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myGreen'><b>Ice Threaded Bullet</b></span><br>\
Binds when picked up<br>\
Projectile<span class='myRight'>Bullet</span><br>\
Adds 16.5 damage per second<br>\
Requires Level 51</div>\
</td></tr></table>";
RewardItems[i] = fIceThreadedBullet; i++;







var fStormpikeBattleStandard = new RewardItem("alliance","Stormpike Battle Standard","/shared/wow-com/images/basics/factions/alteracvalley/stormpikebattlestandard.gif");
fStormpikeBattleStandard.itemTokenPrice = new Array();
fStormpikeBattleStandard.itemTokenPrice[0] = new Array(30,0,0,0);
fStormpikeBattleStandard.itemStats = new Array();
fStormpikeBattleStandard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Stormpike Battle Standard</span>\
<br>Binds when picked up<br>\
<span class=\"myGreen\">Use: Place a Battle Standard with 1500 health that increases the damage of all party members that stay within 45 yards of the Battle Standard by 10%.  Lasts 2 min. May only be used in Alterac Valley.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeBattleStandard; ++i;



var fElectrifiedDagger = new RewardItem("alliance","Electrified Dagger","/shared/wow-com/images/basics/factions/alteracvalley/electrifieddagger.gif");
fElectrifiedDagger.itemHonorPrice = new Array();
fElectrifiedDagger.itemHonorPrice[0] = 2800
fElectrifiedDagger.itemTokenPrice = new Array();
fElectrifiedDagger.itemTokenPrice[0] = new Array(10,0,0,0);
fElectrifiedDagger.itemStats = new Array();
fElectrifiedDagger.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Electrified Dagger</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>53 - 100 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(42.5 damage per second)<br>+10 Agility<br>Durability 65 / 65<br>Requires Level 60<br>\
<span class=\"myGreen\">Chance on hit: Blasts a target for 45 Nature damage.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fElectrifiedDagger; ++i;


var fCracklingStaff = new RewardItem("alliance","Crackling Staff","/shared/wow-com/images/basics/factions/alteracvalley/cracklingstaff.gif");
fCracklingStaff.itemHonorPrice = new Array();
fCracklingStaff.itemHonorPrice[0] = 3200
fCracklingStaff.itemTokenPrice = new Array();
fCracklingStaff.itemTokenPrice[0] = new Array(15,0,0,0);
fCracklingStaff.itemStats = new Array();
fCracklingStaff.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Crackling Staff</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 3.10</span>\
<br>(55.6 damage per second)<br>+25 Stamina<br>+16 Intellect<br>Durability 100 / 100<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCracklingStaff; ++i;


var fStormstrikeHammer = new RewardItem("alliance","Stormstrike Hammer","/shared/wow-com/images/basics/factions/alteracvalley/stormstrikehammer.gif");
fStormstrikeHammer.itemHonorPrice = new Array();
fStormstrikeHammer.itemHonorPrice[0] = 2800
fStormstrikeHammer.itemTokenPrice = new Array();
fStormstrikeHammer.itemTokenPrice[0] = new Array(10,0,0,0);
fStormstrikeHammer.itemStats = new Array();
fStormstrikeHammer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Stormstrike Hammer</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Mace</span>\
<br>80 - 150 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(42.6 damage per second)<br>+15 Strength<br>Durability 90 / 90<br>Requires Level 60</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormstrikeHammer; ++i;



var fGnollSkinBandolier = new RewardItem("alliance","Gnoll Skin Bandolier","/shared/wow-com/images/basics/factions/alteracvalley/gnollskinbandolier.gif");
fGnollSkinBandolier.itemHonorPrice = new Array();
fGnollSkinBandolier.itemHonorPrice[0] = 1800
fGnollSkinBandolier.itemTokenPrice = new Array();
fGnollSkinBandolier.itemTokenPrice[0] = new Array(10,0,0,0);
fGnollSkinBandolier.itemStats = new Array();
fGnollSkinBandolier.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Gnoll Skin Bandolier</span>\
<br>Binds when picked up<br>Unique<br>16 Slot Ammo Pouch<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases ranged attack speed by 15%.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGnollSkinBandolier; ++i;



var fHarpyHideQuiver = new RewardItem("alliance","Harpy Hide Quiver","/shared/wow-com/images/basics/factions/alteracvalley/harpyhidequiver.gif");
fHarpyHideQuiver.itemHonorPrice = new Array();
fHarpyHideQuiver.itemHonorPrice[0] = 1800
fHarpyHideQuiver.itemTokenPrice = new Array();
fHarpyHideQuiver.itemTokenPrice[0] = new Array(10,0,0,0);
fHarpyHideQuiver.itemStats = new Array();
fHarpyHideQuiver.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Harpy Hide Quiver</span>\
<br>Binds when picked up<br>Unique<br>16 Slot Quiver<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases ranged attack speed by 15%.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHarpyHideQuiver; ++i;









var fStormpikeBattleCharger = new RewardItem("alliance","Stormpike Battle Charger","/shared/wow-com/images/basics/factions/alteracvalley/stormpikebattlecharger.gif");
fStormpikeBattleCharger.itemTokenPrice = new Array();
fStormpikeBattleCharger.itemTokenPrice[0] = new Array(50,0,0,0);
fStormpikeBattleCharger.itemStats = new Array();
fStormpikeBattleCharger.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Stormpike Battle Charger</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Stormpike Battle Charger.  This is a very fast mount.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormpikeBattleCharger; ++i;




var fLeiOfTheLifegiver = new RewardItem("alliance","Lei of the Lifegiver","/shared/wow-com/images/basics/factions/alteracvalley/leiofthelifegiver.gif");
fLeiOfTheLifegiver.itemHonorPrice = new Array();
fLeiOfTheLifegiver.itemHonorPrice[0] = 5600
fLeiOfTheLifegiver.itemTokenPrice = new Array();
fLeiOfTheLifegiver.itemTokenPrice[0] = new Array(25,0,0,0);
fLeiOfTheLifegiver.itemStats = new Array();
fLeiOfTheLifegiver.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Lei of the Lifegiver</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 53.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLeiOfTheLifegiver; ++i;


var fTherazanesTouch = new RewardItem("alliance","Therazane's Touch","/shared/wow-com/images/basics/factions/alteracvalley/therazanestouch.gif");
fTherazanesTouch.itemHonorPrice = new Array();
fTherazanesTouch.itemHonorPrice[0] = 5600
fTherazanesTouch.itemTokenPrice = new Array();
fTherazanesTouch.itemTokenPrice[0] = new Array(25,0,0,0);
fTherazanesTouch.itemStats = new Array();
fTherazanesTouch.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Therazane's Touch</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTherazanesTouch; ++i;


var fTomeOfArcaneDomination = new RewardItem("alliance","Tome of Arcane Domination","/shared/wow-com/images/basics/factions/alteracvalley/tomeofarcanedomination.gif");
fTomeOfArcaneDomination.itemHonorPrice = new Array();
fTomeOfArcaneDomination.itemHonorPrice[0] = 5600
fTomeOfArcaneDomination.itemTokenPrice = new Array();
fTomeOfArcaneDomination.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfArcaneDomination.itemStats = new Array();
fTomeOfArcaneDomination.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of Arcane Domination</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Arcane spells and effects by up to 34.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfArcaneDomination; ++i;




var fTomeOfFieryArcana = new RewardItem("alliance","Tome of Fiery Arcana","/shared/wow-com/images/basics/factions/alteracvalley/tomeoffieryarcana.gif");
fTomeOfFieryArcana.itemHonorPrice = new Array();
fTomeOfFieryArcana.itemHonorPrice[0] = 5600
fTomeOfFieryArcana.itemTokenPrice = new Array();
fTomeOfFieryArcana.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfFieryArcana.itemStats = new Array();
fTomeOfFieryArcana.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of Fiery Arcana</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Fire spells and effects by up to 40.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfFieryArcana; ++i;



var fTomeOfShadowForce = new RewardItem("alliance","Tome of Shadow Force","/shared/wow-com/images/basics/factions/alteracvalley/tomeofshadowforce.gif");
fTomeOfShadowForce.itemHonorPrice = new Array();
fTomeOfShadowForce.itemHonorPrice[0] = 5600
fTomeOfShadowForce.itemTokenPrice = new Array();
fTomeOfShadowForce.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfShadowForce.itemStats = new Array();
fTomeOfShadowForce.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of Shadow Force</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>+8 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Shadow spells and effects by up to 34.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfShadowForce; ++i;


var fTomeOfTheIceLord = new RewardItem("alliance","Tome of the Ice Lord","/shared/wow-com/images/basics/factions/alteracvalley/tomeoftheicelord.gif");
fTomeOfTheIceLord.itemHonorPrice = new Array();
fTomeOfTheIceLord.itemHonorPrice[0] = 5600
fTomeOfTheIceLord.itemTokenPrice = new Array();
fTomeOfTheIceLord.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfTheIceLord.itemStats = new Array();
fTomeOfTheIceLord.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of the Ice Lord</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>+9 Intellect<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Frost spells and effects by up to 34.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfTheIceLord; ++i;



var fTheUnstoppableForce = new RewardItem("alliance","The Unstoppable Force","/shared/wow-com/images/basics/factions/alteracvalley/theunstoppableforce.gif");
fTheUnstoppableForce.itemHonorPrice = new Array();
fTheUnstoppableForce.itemHonorPrice[0] = 5600
fTheUnstoppableForce.itemTokenPrice = new Array();
fTheUnstoppableForce.itemTokenPrice[0] = new Array(25,0,0,0);
fTheUnstoppableForce.itemStats = new Array();
fTheUnstoppableForce.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">The Unstoppable Force</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>175 - 292 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(61.4 damage per second)<br>+19 Strength<br>+15 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Chance on hit: Stuns target for 1 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTheUnstoppableForce; ++i;


var fTheImmovableObject = new RewardItem("alliance","The Immovable Object","/shared/wow-com/images/basics/factions/alteracvalley/theimmovableobject.gif");
fTheImmovableObject.itemHonorPrice = new Array();
fTheImmovableObject.itemHonorPrice[0] = 5600
fTheImmovableObject.itemTokenPrice = new Array();
fTheImmovableObject.itemTokenPrice[0] = new Array(25,0,0,0);
fTheImmovableObject.itemStats = new Array();
fTheImmovableObject.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">The Immovable Object</span>\
<br>Binds when picked up<br>Unique<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>2836 Armor<br>58 Block<br>+15 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 27.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTheImmovableObject; ++i;


var fDonJuliosBand = new RewardItem("alliance","Don Julio's Band","/shared/wow-com/images/basics/factions/alteracvalley/donjuliosband.gif");
fDonJuliosBand.itemHonorPrice = new Array();
fDonJuliosBand.itemHonorPrice[0] = 5400
fDonJuliosBand.itemTokenPrice = new Array();
fDonJuliosBand.itemTokenPrice[0] = new Array(25,0,0,0);
fDonJuliosBand.itemStats = new Array();
fDonJuliosBand.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Don Julio's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+11 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDonJuliosBand; ++i;

var fTheLobotomizer = new RewardItem("alliance","The Lobotomizer","/shared/wow-com/images/basics/factions/alteracvalley/thelobotomizer.gif");
fTheLobotomizer.itemHonorPrice = new Array();
fTheLobotomizer.itemHonorPrice[0] = 5600
fTheLobotomizer.itemTokenPrice = new Array();
fTheLobotomizer.itemTokenPrice[0] = new Array(25,0,0,0);
fTheLobotomizer.itemStats = new Array();
fTheLobotomizer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">The Lobotomizer</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>59 - 111 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(47.2 damage per second)<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Chance on hit: Wounds the target for 200 to 300 damage and lowers Intellect of target by 25 for 30 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTheLobotomizer; ++i;

var fDonRodrigosBand = new RewardItem("alliance","Don Rodrigo's Band","/shared/wow-com/images/basics/factions/alteracvalley/donrodrigosband.gif");
fDonRodrigosBand.itemHonorPrice = new Array();
fDonRodrigosBand.itemHonorPrice[0] = 5400
fDonRodrigosBand.itemTokenPrice = new Array();
fDonRodrigosBand.itemTokenPrice[0] = new Array(25,0,0,0);
fDonRodrigosBand.itemStats = new Array();
fDonRodrigosBand.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Don Rodrigo's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+7 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDonRodrigosBand; ++i;










//---Horde below

var fSuperiorHealingDraught = new RewardItem("horde","Superior Healing Draught","/shared/wow-com/images/basics/factions/alteracvalley/superiorhealingdraught.gif");
fSuperiorHealingDraught.itemMoneyPrice = new Array();
fSuperiorHealingDraught.itemMoneyPrice[0] = 500;
fSuperiorHealingDraught.itemStats = new Array();
fSuperiorHealingDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Superior Healing Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 health. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fSuperiorHealingDraught; i++;



var fSuperiorManaDraught = new RewardItem("horde","Superior Mana Draught","/shared/wow-com/images/basics/factions/alteracvalley/superiormanadraught.gif");
fSuperiorManaDraught.itemMoneyPrice = new Array();
fSuperiorManaDraught.itemMoneyPrice[0] = 500;
fSuperiorManaDraught.itemStats = new Array();
fSuperiorManaDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Superior Mana Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 35<br>\
<span class='myGreen'>Use: Restores 560 to 720 mana. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fSuperiorManaDraught; i++;



var fFrostwolfBattleTabard = new RewardItem("horde","Frostwolf Battle Tabard","/shared/wow-com/images/basics/factions/alteracvalley/stormpikebattletabard.gif");
fFrostwolfBattleTabard.itemTokenPrice = new Array();
fFrostwolfBattleTabard.itemTokenPrice[0] = new Array(60,0,0,0);
fFrostwolfBattleTabard.itemStats = new Array();
fFrostwolfBattleTabard.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Frostwolf Battle Tabard</b></span><br>\
Binds when picked up<br>\
Unique<br>\
Tabard</div>\
</td></tr></table>";
RewardItems[i] = fFrostwolfBattleTabard; i++;





var fAlteracHeavyRuneclothBandage = new RewardItem("horde","Alterac Heavy Runecloth Bandage","/shared/wow-com/images/basics/factions/alteracvalley/alteracheavyruneclothbandag.gif");
fAlteracHeavyRuneclothBandage.itemMoneyPrice = new Array();
fAlteracHeavyRuneclothBandage.itemMoneyPrice[0] = 8000;
fAlteracHeavyRuneclothBandage.itemStats = new Array();
fAlteracHeavyRuneclothBandage.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Alterac Heavy Runecloth Bandage</b></span><br>\
Binds when picked up<br>\
Requires First Aid (225)<br>\
<span class='myGreen'>Use: Heals 2000 damage over 8 sec.</span><br>\
<span class='myYellow'>&quot;May only be used in Alterac Valley.&quot;</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fAlteracHeavyRuneclothBandage; i++;



var fBottledAlteracSpringWater = new RewardItem("horde","Bottled Alterac Spring Water","/shared/wow-com/images/basics/factions/alteracvalley/bottledalteracspringwater.gif");
fBottledAlteracSpringWater.itemMoneyPrice = new Array();
fBottledAlteracSpringWater.itemMoneyPrice[0] = 5000;
fBottledAlteracSpringWater.itemStats = new Array();
fBottledAlteracSpringWater.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Bottled Alterac Spring Water</b></span><br>\
Binds when picked up<br>\
Requires Level 55<br>\
<span class='myGreen'>Use: Restores 4410 mana over 30 sec. Must remain seated while drinking. Also increases your Spirit by 10 for 10 min.</span><br>\
<span class='myYellow'>&quot;From the mountain springs of Alterac!&quot;</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fBottledAlteracSpringWater; i++;










var fMajorHealingDraught = new RewardItem("horde","Major Healing Draught","/shared/wow-com/images/basics/factions/alteracvalley/majorhealingdraught.gif");
fMajorHealingDraught.itemMoneyPrice = new Array();
fMajorHealingDraught.itemMoneyPrice[0] = 900;
fMajorHealingDraught.itemStats = new Array();
fMajorHealingDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Major Healing Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 45<br>\
<span class='myGreen'>Use: Restores 980 to 1260 health. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fMajorHealingDraught; i++;




var fMajorManaDraught = new RewardItem("horde","Major Mana Draught","/shared/wow-com/images/basics/factions/alteracvalley/majormanadraught.gif");
fMajorManaDraught.itemMoneyPrice = new Array();
fMajorManaDraught.itemMoneyPrice[0] = 900;
fMajorManaDraught.itemStats = new Array();
fMajorManaDraught.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Major Mana Draught</b></span><br>\
Binds when picked up<br>\
Unique (10)<br>\
Requires Level 45<br>\
<span class='myGreen'>Use: Restores 980 to 1260 mana. This item may only be used in PvP Battlegrounds.</span>\
</div>\
</td></tr></table>";
RewardItems[i] = fMajorManaDraught; i++;




var fFrostwolfLegionnairesCloak = new RewardItem("horde","Frostwolf Legionnaire's Cloak","/shared/wow-com/images/basics/factions/alteracvalley/frostwolfcloak.gif");
fFrostwolfLegionnairesCloak.itemHonorPrice = new Array();
fFrostwolfLegionnairesCloak.itemHonorPrice[0] = 1800
fFrostwolfLegionnairesCloak.itemTokenPrice = new Array();
fFrostwolfLegionnairesCloak.itemTokenPrice[0] = new Array(10,0,0,0);
fFrostwolfLegionnairesCloak.itemStats = new Array();
fFrostwolfLegionnairesCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Legionnaire's Cloak</span>\
<br>Binds when picked up<br>Back<br>43 Armor<br>+11 Stamina<br>+5 Frost Resistance<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases attack power by 24.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfLegionnairesCloak; ++i;




var fFrostwolfAdvisorsCloak = new RewardItem("horde","Frostwolf Advisor's Cloak","/shared/wow-com/images/basics/factions/alteracvalley/frostwolfcloak.gif");
fFrostwolfAdvisorsCloak.itemHonorPrice = new Array();
fFrostwolfAdvisorsCloak.itemHonorPrice[0] = 1800
fFrostwolfAdvisorsCloak.itemTokenPrice = new Array();
fFrostwolfAdvisorsCloak.itemTokenPrice[0] = new Array(10,0,0,0);
fFrostwolfAdvisorsCloak.itemStats = new Array();
fFrostwolfAdvisorsCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Advisor's Cloak</span>\
<br>Binds when picked up<br>Back<br>43 Armor<br>+11 Stamina<br>+5 Frost Resistance<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 14.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfAdvisorsCloak; ++i;



var fFrostwolfLegionnairesPendant = new RewardItem("horde","Frostwolf Legionnaire's Pendant","/shared/wow-com/images/basics/factions/alteracvalley/frostwolflegpendant.gif");
fFrostwolfLegionnairesPendant.itemHonorPrice = new Array();
fFrostwolfLegionnairesPendant.itemHonorPrice[0] = 1800
fFrostwolfLegionnairesPendant.itemTokenPrice = new Array();
fFrostwolfLegionnairesPendant.itemTokenPrice[0] = new Array(20,0,0,0);
fFrostwolfLegionnairesPendant.itemStats = new Array();
fFrostwolfLegionnairesPendant.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Legionnaire's Pendant</span>\
<br>Binds when picked up<br>Neck<br>+15 Stamina<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases attack power by 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfLegionnairesPendant; ++i;






var fFrostwolfAdvisorsPendant = new RewardItem("horde","Frostwolf Advisor's Pendant","/shared/wow-com/images/basics/factions/alteracvalley/frostwolfadvisorspendant.gif");
fFrostwolfAdvisorsPendant.itemHonorPrice = new Array();
fFrostwolfAdvisorsPendant.itemHonorPrice[0] = 1800
fFrostwolfAdvisorsPendant.itemTokenPrice = new Array();
fFrostwolfAdvisorsPendant.itemTokenPrice[0] = new Array(20,0,0,0);
fFrostwolfAdvisorsPendant.itemStats = new Array();
fFrostwolfAdvisorsPendant.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Advisor's Pendant</span>\
<br>Binds when picked up<br>Neck<br>+10 Stamina<br>+10 Intellect<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfAdvisorsPendant; ++i;



var fFrostwolfPlateBelt = new RewardItem("horde","Frostwolf Plate Belt","/shared/wow-com/images/basics/factions/alteracvalley/stormpikeplategirdle.gif");
fFrostwolfPlateBelt.itemHonorPrice = new Array();
fFrostwolfPlateBelt.itemHonorPrice[0] = 3300
fFrostwolfPlateBelt.itemTokenPrice = new Array();
fFrostwolfPlateBelt.itemTokenPrice[0] = new Array(20,0,0,0);
fFrostwolfPlateBelt.itemStats = new Array();
fFrostwolfPlateBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Plate Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>353 Armor<br>+18 Strength<br>+7 Agility<br>+8 Stamina<br>+5 Frost Resistance<br>Durability 45 / 45<br>Requires Level 55</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfPlateBelt; ++i;





var fFrostwolfMailBelt = new RewardItem("horde","Frostwolf Mail Belt","/shared/wow-com/images/basics/factions/alteracvalley/stormpikemailgirdle.gif");
fFrostwolfMailBelt.itemHonorPrice = new Array();
fFrostwolfMailBelt.itemHonorPrice[0] = 3300
fFrostwolfMailBelt.itemTokenPrice = new Array();
fFrostwolfMailBelt.itemTokenPrice[0] = new Array(20,0,0,0);
fFrostwolfMailBelt.itemStats = new Array();
fFrostwolfMailBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Mail Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>199 Armor<br>+12 Agility<br>+12 Stamina<br>+12 Intellect<br>+5 Frost Resistance<br>Durability 40 / 40<br>Requires Level 55</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfMailBelt; ++i;



var fFrostwolfLeatherBelt = new RewardItem("horde","Frostwolf Leather Belt","/shared/wow-com/images/basics/factions/alteracvalley/stormpikeleathergirdle.gif");
fFrostwolfLeatherBelt.itemHonorPrice = new Array();
fFrostwolfLeatherBelt.itemHonorPrice[0] = 3300
fFrostwolfLeatherBelt.itemTokenPrice = new Array();
fFrostwolfLeatherBelt.itemTokenPrice[0] = new Array(20,0,0,0);
fFrostwolfLeatherBelt.itemStats = new Array();
fFrostwolfLeatherBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Leather Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>95 Armor<br>+11 Strength<br>+10 Agility<br>+15 Stamina<br>+5 Frost Resistance<br>Durability 35 / 35<br>Requires Level 55</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfLeatherBelt; ++i;


var fFrostwolfClothBelt = new RewardItem("horde","Frostwolf Cloth Belt","/shared/wow-com/images/basics/factions/alteracvalley/stormpikeclothgirdle.gif");
fFrostwolfClothBelt.itemHonorPrice = new Array();
fFrostwolfClothBelt.itemHonorPrice[0] = 3300
fFrostwolfClothBelt.itemTokenPrice = new Array();
fFrostwolfClothBelt.itemTokenPrice[0] = new Array(20,0,0,0);
fFrostwolfClothBelt.itemStats = new Array();
fFrostwolfClothBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Cloth Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>48 Armor<br>+11 Stamina<br>+10 Intellect<br>+5 Frost Resistance<br>Durability 30 / 30<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 18.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfClothBelt; ++i;


var fAlteracMannaBiscuit = new RewardItem("horde","Alterac Mana Biscuit","/shared/wow-com/images/basics/factions/alteracvalley/alteracmannabiscuit.gif");
fAlteracMannaBiscuit.itemMoneyPrice = new Array();
fAlteracMannaBiscuit.itemMoneyPrice[0] = 7000;
fAlteracMannaBiscuit.itemStats = new Array();
fAlteracMannaBiscuit.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myTable'><b>Alterac Mana Biscuit</b></span><br>\
Binds when picked up<br>\
Requires Level 51<br>\
<span class='myGreen'>Use: Restores 4410 health and 4410 mana over 30 sec. Must remain seated while eating.</span></div>\
</td></tr></table>";
RewardItems[i] = fAlteracMannaBiscuit; i++;

var fIceThreadedArrow = new RewardItem("horde","Ice Threaded Arrow","/shared/wow-com/images/basics/factions/alteracvalley/icethreadedarrow.gif");
fIceThreadedArrow.itemMoneyPrice = new Array();
fIceThreadedArrow.itemMoneyPrice[0] = 6000;
fIceThreadedArrow.itemHonorPrice = new Array();
fIceThreadedArrow.itemHonorPrice[0] = 1
fIceThreadedArrow.itemStats = new Array();
fIceThreadedArrow.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myGreen'><b>Ice Threaded Arrow</b></span><br>\
Binds when picked up<br>\
Projectile<span class='myRight'>Arrow</span><br>\
Adds 16.5 damage per second<br>\
Requires Level 51</div>\
</td></tr></table>";
RewardItems[i] = fIceThreadedArrow; i++;



var fIceThreadedBullet = new RewardItem("horde","Ice Threaded Bullet","/shared/wow-com/images/basics/factions/alteracvalley/icethreadedbullet.gif");
fIceThreadedBullet.itemMoneyPrice = new Array();
fIceThreadedBullet.itemMoneyPrice[0] = 6000;
fIceThreadedBullet.itemHonorPrice = new Array();
fIceThreadedBullet.itemHonorPrice[0] = 1
fIceThreadedBullet.itemStats = new Array();
fIceThreadedBullet.itemStats[0] = "\
<table border='0' cellpadding='0' cellspacing='0' width='275'><tr><td>\
<div class='myTable'>\
<span class='myGreen'><b>Ice Threaded Bullet</b></span><br>\
Binds when picked up<br>\
Projectile<span class='myRight'>Bullet</span><br>\
Adds 16.5 damage per second<br>\
Requires Level 51</div>\
</td></tr></table>";
RewardItems[i] = fIceThreadedBullet; i++;







var fFrostwolfBattleStandard = new RewardItem("horde","Frostwolf Battle Standard","/shared/wow-com/images/basics/factions/alteracvalley/frostwolfbattlestandard.gif");
fFrostwolfBattleStandard.itemTokenPrice = new Array();
fFrostwolfBattleStandard.itemTokenPrice[0] = new Array(30,0,0,0);
fFrostwolfBattleStandard.itemStats = new Array();
fFrostwolfBattleStandard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Frostwolf Battle Standard</span>\
<br>Binds when picked up<br>\
<span class=\"myGreen\">Use: Place a Battle Standard with 1500 health that increases the maximum damage of all party members that stay within 45 yards of the Battle Standard by 10%.  Lasts 2 min. May only be used in Alterac Valley.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostwolfBattleStandard; ++i;



var fGlacialBlade = new RewardItem("horde","Glacial Blade","/shared/wow-com/images/basics/factions/alteracvalley/glacialblade.gif");
fGlacialBlade.itemHonorPrice = new Array();
fGlacialBlade.itemHonorPrice[0] = 2800
fGlacialBlade.itemTokenPrice = new Array();
fGlacialBlade.itemTokenPrice[0] = new Array(10,0,0,0);
fGlacialBlade.itemStats = new Array();
fGlacialBlade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Glacial Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>53 - 100 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(42.5 damage per second)<br>+10 Agility<br>Durability 65 / 65<br>Requires Level 60<br>\
<span class=\"myGreen\">Chance on hit: Blasts a target for 45 Frost damage.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlacialBlade; ++i;




var fWhiteoutStaff = new RewardItem("horde","Whiteout Staff","/shared/wow-com/images/basics/factions/alteracvalley/whiteoutstaff.gif");
fWhiteoutStaff.itemHonorPrice = new Array();
fWhiteoutStaff.itemHonorPrice[0] = 3200
fWhiteoutStaff.itemTokenPrice = new Array();
fWhiteoutStaff.itemTokenPrice[0] = new Array(15,0,0,0);
fWhiteoutStaff.itemStats = new Array();
fWhiteoutStaff.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Whiteout Staff</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>138 - 207 Damage<span class=\"myRight\">Speed 3.10</span>\
<br>(55.6 damage per second)<br>+25 Stamina<br>+16 Intellect<br>Durability 100 / 100<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 15.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWhiteoutStaff; ++i;





var fFrostbite = new RewardItem("horde","Frostbite","/shared/wow-com/images/basics/factions/alteracvalley/frostbite.gif");
fFrostbite.itemHonorPrice = new Array();
fFrostbite.itemHonorPrice[0] = 2800
fFrostbite.itemTokenPrice = new Array();
fFrostbite.itemTokenPrice[0] = new Array(10,0,0,0);
fFrostbite.itemStats = new Array();
fFrostbite.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Frostbite</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Axe</span>\
<br>80 - 150 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(42.6 damage per second)<br>+15 Strength<br>Durability 90 / 90<br>Requires Level 60</div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFrostbite; ++i;










var fGnollSkinBandolier = new RewardItem("horde","Gnoll Skin Bandolier","/shared/wow-com/images/basics/factions/alteracvalley/gnollskinbandolier.gif");
fGnollSkinBandolier.itemHonorPrice = new Array();
fGnollSkinBandolier.itemHonorPrice[0] = 1800
fGnollSkinBandolier.itemTokenPrice = new Array();
fGnollSkinBandolier.itemTokenPrice[0] = new Array(10,0,0,0);
fGnollSkinBandolier.itemStats = new Array();
fGnollSkinBandolier.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Gnoll Skin Bandolier</span>\
<br>Binds when picked up<br>Unique<br>16 Slot Ammo Pouch<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases ranged attack speed by 15%.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGnollSkinBandolier; ++i;

var fHarpyHideQuiver = new RewardItem("horde","Harpy Hide Quiver","/shared/wow-com/images/basics/factions/alteracvalley/harpyhidequiver.gif");
fHarpyHideQuiver.itemHonorPrice = new Array();
fHarpyHideQuiver.itemHonorPrice[0] = 1800
fHarpyHideQuiver.itemTokenPrice = new Array();
fHarpyHideQuiver.itemTokenPrice[0] = new Array(10,0,0,0);
fHarpyHideQuiver.itemStats = new Array();
fHarpyHideQuiver.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myBlue\">Harpy Hide Quiver</span>\
<br>Binds when picked up<br>Unique<br>16 Slot Quiver<br>Requires Level 55<br>\
<span class=\"myGreen\">Equip: Increases ranged attack speed by 15%.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHarpyHideQuiver; ++i;







var fHornOfTheFrostwolfHowler = new RewardItem("horde","Horn of the Frostwolf Howler","/shared/wow-com/images/basics/factions/alteracvalley/frostwolfhowler.gif");
fHornOfTheFrostwolfHowler.itemTokenPrice = new Array();
fHornOfTheFrostwolfHowler.itemTokenPrice[0] = new Array(50,0,0,0);
fHornOfTheFrostwolfHowler.itemStats = new Array();
fHornOfTheFrostwolfHowler.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Horn of the Frostwolf Howler</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Frostwolf Howler.  This is a very fast mount.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHornOfTheFrostwolfHowler; ++i;



var fLeiOfTheLifegiver = new RewardItem("horde","Lei of the Lifegiver","/shared/wow-com/images/basics/factions/alteracvalley/leiofthelifegiver.gif");
fLeiOfTheLifegiver.itemHonorPrice = new Array();
fLeiOfTheLifegiver.itemHonorPrice[0] = 5600
fLeiOfTheLifegiver.itemTokenPrice = new Array();
fLeiOfTheLifegiver.itemTokenPrice[0] = new Array(25,0,0,0);
fLeiOfTheLifegiver.itemStats = new Array();
fLeiOfTheLifegiver.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Lei of the Lifegiver</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 53.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLeiOfTheLifegiver; ++i;



var fTherazanesTouch = new RewardItem("horde","Therazane's Touch","/shared/wow-com/images/basics/factions/alteracvalley/therazanestouch.gif");
fTherazanesTouch.itemHonorPrice = new Array();
fTherazanesTouch.itemHonorPrice[0] = 5600
fTherazanesTouch.itemTokenPrice = new Array();
fTherazanesTouch.itemTokenPrice[0] = new Array(25,0,0,0);
fTherazanesTouch.itemStats = new Array();
fTherazanesTouch.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Therazane's Touch</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 33.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTherazanesTouch; ++i;


var fTomeOfArcaneDomination = new RewardItem("horde","Tome of Arcane Domination","/shared/wow-com/images/basics/factions/alteracvalley/tomeofarcanedomination.gif");
fTomeOfArcaneDomination.itemHonorPrice = new Array();
fTomeOfArcaneDomination.itemHonorPrice[0] = 5600
fTomeOfArcaneDomination.itemTokenPrice = new Array();
fTomeOfArcaneDomination.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfArcaneDomination.itemStats = new Array();
fTomeOfArcaneDomination.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of Arcane Domination</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Arcane spells and effects by up to 34.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 3 mana per 5 sec.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfArcaneDomination; ++i;



var fTomeOfFieryArcana = new RewardItem("horde","Tome of Fiery Arcana","/shared/wow-com/images/basics/factions/alteracvalley/tomeoffieryarcana.gif");
fTomeOfFieryArcana.itemHonorPrice = new Array();
fTomeOfFieryArcana.itemHonorPrice[0] = 5600
fTomeOfFieryArcana.itemTokenPrice = new Array();
fTomeOfFieryArcana.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfFieryArcana.itemStats = new Array();
fTomeOfFieryArcana.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of Fiery Arcana</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Fire spells and effects by up to 40.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfFieryArcana; ++i;


var fTomeOfShadowForce = new RewardItem("horde","Tome of Shadow Force","/shared/wow-com/images/basics/factions/alteracvalley/tomeofshadowforce.gif");
fTomeOfShadowForce.itemHonorPrice = new Array();
fTomeOfShadowForce.itemHonorPrice[0] = 5600
fTomeOfShadowForce.itemTokenPrice = new Array();
fTomeOfShadowForce.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfShadowForce.itemStats = new Array();
fTomeOfShadowForce.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of Shadow Force</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>+8 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Shadow spells and effects by up to 34.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfShadowForce; ++i;


var fTomeOfTheIceLord = new RewardItem("horde","Tome of the Ice Lord","/shared/wow-com/images/basics/factions/alteracvalley/tomeoftheicelord.gif");
fTomeOfTheIceLord.itemHonorPrice = new Array();
fTomeOfTheIceLord.itemHonorPrice[0] = 5600
fTomeOfTheIceLord.itemTokenPrice = new Array();
fTomeOfTheIceLord.itemTokenPrice[0] = new Array(25,0,0,0);
fTomeOfTheIceLord.itemStats = new Array();
fTomeOfTheIceLord.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Tome of the Ice Lord</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>+9 Intellect<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases damage done by Frost spells and effects by up to 34.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTomeOfTheIceLord; ++i;



var fTheUnstoppableForce = new RewardItem("horde","The Unstoppable Force","/shared/wow-com/images/basics/factions/alteracvalley/theunstoppableforce.gif");
fTheUnstoppableForce.itemHonorPrice = new Array();
fTheUnstoppableForce.itemHonorPrice[0] = 5600
fTheUnstoppableForce.itemTokenPrice = new Array();
fTheUnstoppableForce.itemTokenPrice[0] = new Array(25,0,0,0);
fTheUnstoppableForce.itemStats = new Array();
fTheUnstoppableForce.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">The Unstoppable Force</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>175 - 292 Damage<span class=\"myRight\">Speed 3.80</span>\
<br>(61.4 damage per second)<br>+19 Strength<br>+15 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 28.</span>\
<br>\
<span class=\"myGreen\">Chance on hit: Stuns target for 1 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTheUnstoppableForce; ++i;


var fTheImmovableObject = new RewardItem("horde","The Immovable Object","/shared/wow-com/images/basics/factions/alteracvalley/theimmovableobject.gif");
fTheImmovableObject.itemHonorPrice = new Array();
fTheImmovableObject.itemHonorPrice[0] = 5600
fTheImmovableObject.itemTokenPrice = new Array();
fTheImmovableObject.itemTokenPrice[0] = new Array(25,0,0,0);
fTheImmovableObject.itemStats = new Array();
fTheImmovableObject.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">The Immovable Object</span>\
<br>Binds when picked up<br>Unique<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>2836 Armor<br>58 Block<br>+15 Stamina<br>Durability 120 / 120<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 27.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTheImmovableObject; ++i;


var fDonJuliosBand = new RewardItem("horde","Don Julio's Band","/shared/wow-com/images/basics/factions/alteracvalley/donjuliosband.gif");
fDonJuliosBand.itemHonorPrice = new Array();
fDonJuliosBand.itemHonorPrice[0] = 5400
fDonJuliosBand.itemTokenPrice = new Array();
fDonJuliosBand.itemTokenPrice[0] = new Array(25,0,0,0);
fDonJuliosBand.itemStats = new Array();
fDonJuliosBand.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<span class=\"myTable\"><span class=\"myPurple\">Don Julio's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+11 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your hit rating by 10.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 16.</span></span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDonJuliosBand; ++i;



var fTheLobotomizer = new RewardItem("horde","The Lobotomizer","/shared/wow-com/images/basics/factions/alteracvalley/thelobotomizer.gif");
fTheLobotomizer.itemHonorPrice = new Array();
fTheLobotomizer.itemHonorPrice[0] = 5600
fTheLobotomizer.itemTokenPrice = new Array();
fTheLobotomizer.itemTokenPrice[0] = new Array(25,0,0,0);
fTheLobotomizer.itemStats = new Array();
fTheLobotomizer.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myPurple\">The Lobotomizer</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>59 - 111 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(47.2 damage per second)<br>Durability 75 / 75<br>Requires Level 60<br>\
<span class=\"myGreen\">Chance on hit: Wounds the target for 200 to 300 damage and lowers Intellect of target by 25 for 30 sec.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTheLobotomizer; ++i;

var fDonRodrigosBand = new RewardItem("horde","Don Rodrigo's Band","/shared/wow-com/images/basics/factions/alteracvalley/donrodrigosband.gif");
fDonRodrigosBand.itemHonorPrice = new Array();
fDonRodrigosBand.itemHonorPrice[0] = 5400
fDonRodrigosBand.itemTokenPrice = new Array();
fDonRodrigosBand.itemTokenPrice[0] = new Array(25,0,0,0);
fDonRodrigosBand.itemStats = new Array();
fDonRodrigosBand.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Don Rodrigo's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+7 Stamina<br>Requires Level 60<br>\
<span class=\"myGreen\">Equip: Increases your spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your spell penetration by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDonRodrigosBand; ++i;

//------END REWARDS DEFINITION------
