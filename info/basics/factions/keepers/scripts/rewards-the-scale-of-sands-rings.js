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

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Sage)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+19 Stamina<br>+18 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Sage)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+21 Stamina<br>+19 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Sage)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>+20 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;



var fBandOfTheEternalSage = new RewardItem("alliance","Band of the Eternal Sage","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_55.jpg");
fBandOfTheEternalSage.itemStats = new Array();
fBandOfTheEternalSage.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of the Eternal Sage</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>+20 Intellect<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Your offensive spells have a chance on hit to increase your spell damage by 95 for 10 secs.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheEternalSage; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Restorer)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+19 Stamina<br>+18 Intellect<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Restorer)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+21 Stamina<br>+19 Intellect<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 51.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Restorer)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>+21 Intellect<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 55.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;


var fBandOfTheEternalRestorer = new RewardItem("alliance","Band of the Eternal Restorer","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_55.jpg");
fBandOfTheEternalRestorer.itemStats = new Array();
fBandOfTheEternalRestorer.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of the Eternal Restorer</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>+21 Intellect<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 55.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Your healing spells have a chance to increase your healing by 175 for 10 secs.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheEternalRestorer; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Champion)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+22 Agility<br>+24 Stamina<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Champion)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+23 Agility<br>+24 Stamina<br>\
<span class=\"myGreen\">Equip: Increases attack power by 52.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Champion)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Agility<br>+28 Stamina<br>\
<span class=\"myGreen\">Equip: Increases attack power by 58.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfTheEternalChampion = new RewardItem("alliance","Band of the Eternal Champion","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_55.jpg");
fBandOfTheEternalChampion.itemStats = new Array();
fBandOfTheEternalChampion.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of the Eternal Champion</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Agility<br>+28 Stamina<br>\
<span class=\"myGreen\">Equip: Increases attack power by 58.</span>\
<br>\
<span class=\"myGreen\">Equip: Chance on hit to increase your attack power by 160 for 10 seconds.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheEternalChampion; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Defender)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+33 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 33.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Defender)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+34 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfEternity = new RewardItem("alliance","Band of Eternity (Defender)","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_54.jpg");
fBandOfEternity.itemStats = new Array();
fBandOfEternity.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Eternity</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+37 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfEternity; ++i;

var fBandOfTheEternalDefender = new RewardItem("alliance","Band of the Eternal Defender","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_55.jpg");
fBandOfTheEternalDefender.itemStats = new Array();
fBandOfTheEternalDefender.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of the Eternal Defender</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+37 Stamina<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 38.</span>\
<br>\
<span class=\"myGreen\">Equip: When struck in combat has a chance of increasing your armor by 800 for 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheEternalDefender; ++i;

//-------------------------------------------------------------------
//---Horde below







//------END REWARDS DEFINITION------
