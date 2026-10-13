loreTexts["alliance"] = "<h3>Sporeggar</h3>\
In the far west of Zangarmarsh, nestled between Marshlight Lake and the Spawning Glen, lies Sporeggar, the village of the sporelings. The sporelings, a mostly peaceful race of mushroom-men native to Outland, are facing numerous threats to their quiet way of life. Historically the greatest threat to the sporelings has been the marsh walkers. However, fungal giants in the marsh recently began devouring spore sacs, which contain the sporelings' offspring. In addition, the Bloodscale naga have settled just to the northeast of Sporeggar, where they pose a clear threat to the village's safety. The sporelings have therefore begun appealing to travelers passing through Sporeggar, asking the strangers for help in these dire times.\
<br/><br/>\
The sporelings may seem primitive at first glance, but they possess a natural bond with the marsh, and they gladly share their home's secret blessings with their friends. True to their shy and careful nature, the sporelings have learned to craft cloaks that let their wearer slip through the marshes. The sporelings also possess an intuitive knowledge of alchemy, and so they know how to extract wondrous properties from the marsh's many mushrooms. One final piece of advice for adventurers seeking to befriend the sporelings: the people of Sporeggar have little use for your coin. They prefer to trade their goods for the glowcap mushrooms found throughout Zangarmarsh.";

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

var fRecipeSporelingSnack = new RewardItem("alliance","Recipe: Sporeling Snack","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_03.gif&reason=external-or-uncollected-resource");
fRecipeSporelingSnack.itemMoneyPrice = new Array();
fRecipeSporelingSnack.itemMoneyPrice[0] = 20000
fRecipeSporelingSnack.itemStats = new Array();
fRecipeSporelingSnack.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Recipe: Sporeling Snack<br>Requires Cooking (310)<br>Use: Teaches you how to cook a Sporeling Snack.<br>\
<br>\
<b>Sporeling Snack</b><br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Increases the Stamina and Spirit of your pet by 20.  Lasts for 30 min.</span>\
<br>\
<span class=\"myYellow\">\"Pets love sporeling snacks!\"</span>\
<br>Requires Strange Spores</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeSporelingSnack; ++i;

var fRecipeClamBar = new RewardItem("alliance","Recipe: Clam Bar","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_03.gif&reason=external-or-uncollected-resource");
fRecipeClamBar.itemTokenPrice = new Array();
fRecipeClamBar.itemTokenPrice[0] = new Array(1,0,0,0);
fRecipeClamBar.itemStats = new Array();
fRecipeClamBar.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Recipe: Clam Bar<br>Requires Cooking (300)<br>Use: Teaches you how to deep fry a Clam Bar!  Is there anything quite this tasty?<br>\
<br>\
<b>Clam Bar</b><br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Restores 4320 health over 30 sec.  Must remain seated while eating.  If you spend at least 10 seconds eating you will become well fed and gain 20 Stamina and Spirit for 30 min.</span>\
<br>\
<span class=\"myYellow\">\"Chewy and Delicious!\"</span>\
<br>Requires Jaggal Clam Meat (2), Soothing Spices<br>\
<span class=\"myYellow\">\"How can something this disgusting taste this good!\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeClamBar; ++i;

var fMarshLichen = new RewardItem("alliance","Marsh Lichen","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mushroom_01.gif&reason=external-or-uncollected-resource");
fMarshLichen.itemTokenPrice = new Array();
fMarshLichen.itemTokenPrice[0] = new Array(2,0,0,0);
fMarshLichen.itemStats = new Array();
fMarshLichen.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Marsh Lichen<br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Restores 4320 health over 30 sec.  Must remain seated while eating.  If you spend at least 10 seconds eating you will become well fed and gain 10 Spirit for 10 min.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMarshLichen; ++i;

var fTallstalkMushroom = new RewardItem("alliance","Tallstalk Mushroom","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mushroom_10.gif&reason=external-or-uncollected-resource");
fTallstalkMushroom.itemTokenPrice = new Array();
fTallstalkMushroom.itemTokenPrice[0] = new Array(1,0,0,0);
fTallstalkMushroom.itemStats = new Array();
fTallstalkMushroom.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Tallstalk Mushroom<br>Requires Level 40<br>Requires Sporeggar - Friendly<br>\
<span class=\"myGreen\">Use: Shows the location of all nearby giants on the minimap for 1 hour.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTallstalkMushroom; ++i;

var fRedcapToadstool = new RewardItem("alliance","Redcap Toadstool","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mushroom_07.gif&reason=external-or-uncollected-resource");
fRedcapToadstool.itemTokenPrice = new Array();
fRedcapToadstool.itemTokenPrice[1] = new Array(1,0,0,0);
fRedcapToadstool.itemStats = new Array();
fRedcapToadstool.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Redcap Toadstool<br>Requires Level 40<br>Requires Sporeggar - Honored<br>\
<span class=\"myGreen\">Use: Removes 1 poison effects.  Lowers Nature Resistance by 50 for 1 min.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRedcapToadstool; ++i;

var fPetrifiedLichenGuard = new RewardItem("alliance","Petrified Lichen Guard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Shield_21.gif&reason=external-or-uncollected-resource");
fPetrifiedLichenGuard.itemTokenPrice = new Array();
fPetrifiedLichenGuard.itemTokenPrice[1] = new Array(15,0,0,0);
fPetrifiedLichenGuard.itemStats = new Array();
fPetrifiedLichenGuard.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Petrified Lichen Guard</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>3043 Armor<br>62 Block<br>+15 Strength<br>+24 Stamina<br>Durability 100 / 100<br>Requires Level 62<br>Requires Sporeggar - Honored<br>\
<span class=\"myGreen\">Equip: Afflicts your attacker with deadly poison spores each time you block.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPetrifiedLichenGuard; ++i;

var fSporelingsFirestick = new RewardItem("alliance","Sporeling's Firestick","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fwand.gif&reason=external-or-uncollected-resource");
fSporelingsFirestick.itemTokenPrice = new Array();
fSporelingsFirestick.itemTokenPrice[2] = new Array(20,0,0,0);
fSporelingsFirestick.itemStats = new Array();
fSporelingsFirestick.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Sporeling's Firestick</span>\
<br>Binds when picked up<br>Unique<br>Ranged<span class=\"myRight\">Wand</span>\
<br>88 - 164 Fire Damage<span class=\"myRight\">Speed 1.30</span>\
<br>(96.9 damage per second)<br>+12 Stamina<br>+9 Intellect<br>Durability 65 / 65<br>Requires Level 62<br>Requires Sporeggar - Revered<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 11.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSporelingsFirestick; ++i;

var fHardenedStoneShard = new RewardItem("alliance","Hardened Stone Shard","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Weapon_ShortBlade_08.gif");
fHardenedStoneShard.itemTokenPrice = new Array();
fHardenedStoneShard.itemTokenPrice[2] = new Array(45,0,0,0);
fHardenedStoneShard.itemStats = new Array();
fHardenedStoneShard.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Hardened Stone Shard</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>79 - 120 Damage<span class=\"myRight\">Speed 1.80</span>\
<br>(55.3 damage per second)<br>+16 Stamina<br>Durability 65 / 65<br>Requires Level 62<br>Requires Sporeggar - Revered<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHardenedStoneShard; ++i;

var fRecipeTransmutePrimalEarthToWater = new RewardItem("alliance","Recipe: Transmute Primal Earth to Water","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_06.gif&reason=external-or-uncollected-resource");
fRecipeTransmutePrimalEarthToWater.itemTokenPrice = new Array();
fRecipeTransmutePrimalEarthToWater.itemTokenPrice[2] = new Array(25,0,0,0);
fRecipeTransmutePrimalEarthToWater.itemStats = new Array();
fRecipeTransmutePrimalEarthToWater.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Transmute Primal Earth to Water</span>\
<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires Sporeggar - Revered<br>Use: Teaches you how to Transmute Primal Earth into Primal Water.<br>\
<br>\
<span class=\"myGreen\"><b>Primal Water</b></span>\
<br>Requires Primal Earth</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmutePrimalEarthToWater; ++i;


var fMuckCoveredDrape = new RewardItem("alliance","Muck-Covered Drape","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Cape_17.gif&reason=external-or-uncollected-resource");
fMuckCoveredDrape.itemTokenPrice = new Array();
fMuckCoveredDrape.itemTokenPrice[1] = new Array(25,0,0,0);
fMuckCoveredDrape.itemStats = new Array();
fMuckCoveredDrape.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Muck-Covered Drape</span>\
<br>Binds when picked up<br>Back<br>66 Armor<br>+30 Stamina<br>Requires Level 64<br>Requires Sporeggar - Honored<br>\
<span class=\"myGreen\">Use: Reduces your threat to enemy targets within 30 yards, making them less likely to attack you.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMuckCoveredDrape; ++i;

var fRecipeShroudingPotion = new RewardItem("alliance","Recipe: Shrouding Potion","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fsporeggar%2Fscripts%2Frewards-sporeggar.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_06.gif&reason=external-or-uncollected-resource");
fRecipeShroudingPotion.itemTokenPrice = new Array();
fRecipeShroudingPotion.itemTokenPrice[3] = new Array(30,0,0,0);
fRecipeShroudingPotion.itemStats = new Array();
fRecipeShroudingPotion.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Shrouding Potion</span>\
<br>Binds when picked up<br>Requires Alchemy (335)<br>Requires Sporeggar - Exalted<br>Use: Teaches you how to make a Shrouding Potion.<br>\
<br>\
<b>Shrouding Potion</b><br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Shrouds you from nearby enemies so you seem less threatening to them.</span>\
<br>Requires Ragveil (3), Netherbloom, Imbued Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeShroudingPotion; ++i;




//-------------------------------------------------------------------
//---Horde below







//------END REWARDS DEFINITION------
