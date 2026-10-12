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

tokenIcons = new Array("honorholdtoken","thrallmartoken","nether","warsong");
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
		if (goldPart > 0) outPutString += goldPart+"<img src='/info/basics/factions/images/icons/gold.gif'>&nbsp;";
		if (silverPart > 0) outPutString += silverPart+"<img src='/info/basics/factions/images/icons/silver.gif'>&nbsp;";
		if (copperPart > 0) outPutString += copperPart+"<img src='/info/basics/factions/images/icons/copper.gif'>&nbsp;";
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

var fMightyBloodGarnet = new RewardItem("alliance","Mighty Blood Garnet","/info/basics/factions/images/icons/INV_Misc_Gem_Bloodstone_02.gif");
fMightyBloodGarnet.itemTokenPrice = new Array();
fMightyBloodGarnet.itemTokenPrice[0] = new Array(10,0,0,0);
fMightyBloodGarnet.itemStats = new Array();
fMightyBloodGarnet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Mighty Blood Garnet</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+14 Attack Power<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMightyBloodGarnet; ++i;

var fStarkBloodGarnet = new RewardItem("alliance","Stark Blood Garnet","/info/basics/factions/images/icons/INV_Misc_Gem_Ruby_01.gif");
fStarkBloodGarnet.itemTokenPrice = new Array();
fStarkBloodGarnet.itemTokenPrice[0] = new Array(10,0,0,0);
fStarkBloodGarnet.itemStats = new Array();
fStarkBloodGarnet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Stark Blood Garnet</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+8 Spell Damage<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStarkBloodGarnet; ++i;


var fBarbedDeepPeridot = new RewardItem("alliance","Barbed Deep Peridot","/info/basics/factions/images/icons/INV_Misc_Gem_EmeraldRough_0.gif");
fBarbedDeepPeridot.itemTokenPrice = new Array();
fBarbedDeepPeridot.itemTokenPrice[0] = new Array(10,0,0,0);
fBarbedDeepPeridot.itemStats = new Array();
fBarbedDeepPeridot.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Barbed Deep Peridot</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+3 Stamina, +4 Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow or Blue Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBarbedDeepPeridot; ++i;

var fNotchedDeepPeridot = new RewardItem("alliance","Notched Deep Peridot","/info/basics/factions/images/icons/INV_Misc_Gem_DeepPeridot_03.gif");
fNotchedDeepPeridot.itemTokenPrice = new Array();
fNotchedDeepPeridot.itemTokenPrice[0] = new Array(10,0,0,0);
fNotchedDeepPeridot.itemStats = new Array();
fNotchedDeepPeridot.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Notched Deep Peridot</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+3 Stamina, +4 Spell Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow or Blue Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNotchedDeepPeridot; ++i;

var fBandOfTheVictor = new RewardItem("alliance","Band of the Victor","/info/basics/factions/images/icons/INV_jewelry_ring_36_aee84_8.gif");
fBandOfTheVictor.itemTokenPrice = new Array();
fBandOfTheVictor.itemTokenPrice[0] = new Array(15,0,0,0);
fBandOfTheVictor.itemStats = new Array();
fBandOfTheVictor.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Band of the Victor</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+25 Stamina<br>Requires Level 60<br>\
Red Socket<br>\
Socket Bonus: +4 Attack Power<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheVictor; ++i;

var fCircletOfTheVictor = new RewardItem("alliance","Circlet of the Victor","/info/basics/factions/images/icons/INV_jewelry_ring_36_aee84_8.gif");
fCircletOfTheVictor.itemTokenPrice = new Array();
fCircletOfTheVictor.itemTokenPrice[0] = new Array(15,0,0,0);
fCircletOfTheVictor.itemStats = new Array();
fCircletOfTheVictor.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Circlet of the Victor</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+25 Stamina<br>Requires Level 60<br>\
Red Socket<br>\
Socket Bonus: +2 Spell Damage<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 13.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCircletOfTheVictor; ++i;

var fHonorHoldFavor = new RewardItem("alliance","Honor Hold Favor","/info/basics/factions/images/icons/INV_Banner_02.gif");
fHonorHoldFavor.itemTokenPrice = new Array();
fHonorHoldFavor.itemTokenPrice[0] = new Array(5,0,0,0);
fHonorHoldFavor.itemStats = new Array();
fHonorHoldFavor.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span>Honor Hold Favor<br>Binds when picked up<br>\
<span class=\"myGreen\">Use: In Hellfire Peninsula and Hellfire Citadel, increases Honor Hold reputation gained from killing monsters by 25% and experience gained by 5%.  30 minute duration.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHonorHoldFavor; ++i;



//-------------------------------------------------------------------
//---Horde below

var fMightyBloodGarnet = new RewardItem("horde","Mighty Blood Garnet","/info/basics/factions/images/icons/INV_Misc_Gem_Bloodstone_02.gif");
fMightyBloodGarnet.itemTokenPrice = new Array();
fMightyBloodGarnet.itemTokenPrice[0] = new Array(0,10,0,0);
fMightyBloodGarnet.itemStats = new Array();
fMightyBloodGarnet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Mighty Blood Garnet</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+14 Attack Power<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMightyBloodGarnet; ++i;

var fStarkBloodGarnet = new RewardItem("horde","Stark Blood Garnet","/info/basics/factions/images/icons/INV_Misc_Gem_Ruby_01.gif");
fStarkBloodGarnet.itemTokenPrice = new Array();
fStarkBloodGarnet.itemTokenPrice[0] = new Array(0,10,0,0);
fStarkBloodGarnet.itemStats = new Array();
fStarkBloodGarnet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Stark Blood Garnet</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+8 Spell Damage<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStarkBloodGarnet; ++i;


var fBarbedDeepPeridot = new RewardItem("horde","Barbed Deep Peridot","/info/basics/factions/images/icons/INV_Misc_Gem_EmeraldRough_0.gif");
fBarbedDeepPeridot.itemTokenPrice = new Array();
fBarbedDeepPeridot.itemTokenPrice[0] = new Array(0,10,0,0);
fBarbedDeepPeridot.itemStats = new Array();
fBarbedDeepPeridot.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Barbed Deep Peridot</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+3 Stamina, +4 Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow or Blue Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBarbedDeepPeridot; ++i;

var fNotchedDeepPeridot = new RewardItem("horde","Notched Deep Peridot","/info/basics/factions/images/icons/INV_Misc_Gem_DeepPeridot_03.gif");
fNotchedDeepPeridot.itemTokenPrice = new Array();
fNotchedDeepPeridot.itemTokenPrice[0] = new Array(0,10,0,0);
fNotchedDeepPeridot.itemStats = new Array();
fNotchedDeepPeridot.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Notched Deep Peridot</span>\
<br>Binds when picked up<br>Unique<br>\
<br>+3 Stamina, +4 Spell Critical Strike Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow or Blue Socket.\"</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNotchedDeepPeridot; ++i;

var fBandOfTheVictor = new RewardItem("horde","Band of the Victor","/info/basics/factions/images/icons/INV_jewelry_ring_36_aee84_8.gif");
fBandOfTheVictor.itemTokenPrice = new Array();
fBandOfTheVictor.itemTokenPrice[0] = new Array(0,15,0,0);
fBandOfTheVictor.itemStats = new Array();
fBandOfTheVictor.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Band of the Victor</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+25 Stamina<br>Requires Level 60<br>\
Red Socket<br>\
Socket Bonus: +4 Attack Power<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 13.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheVictor; ++i;

var fCircletOfTheVictor = new RewardItem("horde","Circlet of the Victor","/info/basics/factions/images/icons/INV_jewelry_ring_36_aee84_8.gif");
fCircletOfTheVictor.itemTokenPrice = new Array();
fCircletOfTheVictor.itemTokenPrice[0] = new Array(0,15,0,0);
fCircletOfTheVictor.itemStats = new Array();
fCircletOfTheVictor.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div>\
<div class=\"myTable\"><span class=\"myBlue\">Circlet of the Victor</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+25 Stamina<br>Requires Level 60<br>\
Red Socket<br>\
Socket Bonus: +2 Spell Damage<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 13.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCircletOfTheVictor; ++i;

var fThrallmarFavor = new RewardItem("horde","Thrallmar Favor","/info/basics/factions/images/icons/Racial_Orc_BerserkerStrengt.gif");
fThrallmarFavor.itemTokenPrice = new Array();
fThrallmarFavor.itemTokenPrice[0] = new Array(0,5,0,0);
fThrallmarFavor.itemStats = new Array();
fThrallmarFavor.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span>Thrallmar Favor<br>Binds when picked up<br>\
<span class=\"myGreen\">Use: In Hellfire Peninsula and Hellfire Citadel, increases Thrallmar reputation gained from killing monsters by 25% and experience gained by 5%.  30 minute duration.</span></div>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fThrallmarFavor; ++i;





//------END REWARDS DEFINITION------
