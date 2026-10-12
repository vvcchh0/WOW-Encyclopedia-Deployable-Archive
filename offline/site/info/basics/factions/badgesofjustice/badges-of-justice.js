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
		outPutString += thisObject.itemHonorPrice[thisBracket]+"<img src='boj.gif'>&nbsp;";
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

var fKhadgarsKnapsack = new RewardItem("alliance","Khadgar's Knapsack","/info/basics/factions/images/icons/INV_Misc_Bag_10_Green.gif");
fKhadgarsKnapsack.itemHonorPrice = new Array();
fKhadgarsKnapsack.itemHonorPrice[0] = 25
fKhadgarsKnapsack.itemStats = new Array();
fKhadgarsKnapsack.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Khadgar's Knapsack</span>\
<br>Binds when picked up<br>Held In Off Hand<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 49.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fKhadgarsKnapsack; ++i;

var fTalismanOfKalecgos = new RewardItem("alliance","Talisman of Kalecgos","/info/basics/factions/images/icons/INV_Offhand_OutlandRaid_02.gif");
fTalismanOfKalecgos.itemHonorPrice = new Array();
fTalismanOfKalecgos.itemHonorPrice[0] = 25
fTalismanOfKalecgos.itemStats = new Array();
fTalismanOfKalecgos.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Talisman of Kalecgos</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+14 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage done by Arcane spells and effects by up to 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTalismanOfKalecgos; ++i;


var fMazthorilHonorShield = new RewardItem("alliance","Mazthoril Honor Shield","/info/basics/factions/images/icons/INV_Shield_37.gif");
fMazthorilHonorShield.itemHonorPrice = new Array();
fMazthorilHonorShield.itemHonorPrice[0] = 33
fMazthorilHonorShield.itemStats = new Array();
fMazthorilHonorShield.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Mazthoril Honor Shield</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>4668 Armor<br>115 Block<br>+16 Stamina<br>+17 Intellect<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMazthorilHonorShield; ++i;

var fSearingSunblade = new RewardItem("alliance","Searing Sunblade","/info/basics/factions/images/icons/knife.gif");
fSearingSunblade.itemHonorPrice = new Array();
fSearingSunblade.itemHonorPrice[0] = 50
fSearingSunblade.itemStats = new Array();
fSearingSunblade.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Searing Sunblade</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Dagger</span>\
<br>77 - 145 Damage<span class=\"myRight\">Speed 1.30</span>\
<br>(85.4 damage per second)<br>+24 Agility<br>+22 Stamina<br>Durability 75 / 75<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSearingSunblade; ++i;

var fFlametongueSeal = new RewardItem("alliance","Flametongue Seal","/info/basics/factions/images/icons/Spell_Fire_SealOfFire.gif");
fFlametongueSeal.itemHonorPrice = new Array();
fFlametongueSeal.itemHonorPrice[0] = 25
fFlametongueSeal.itemStats = new Array();
fFlametongueSeal.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Flametongue Seal</span>\
<br>Binds when picked up<br>Held In Off Hand<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage done by Fire spells and effects by up to 49.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFlametongueSeal; ++i;

var fSapphironsWingBone = new RewardItem("alliance","Sapphiron's Wing Bone","/info/basics/factions/images/icons/INV_Misc_Bone_01.gif");
fSapphironsWingBone.itemHonorPrice = new Array();
fSapphironsWingBone.itemHonorPrice[0] = 25
fSapphironsWingBone.itemStats = new Array();
fSapphironsWingBone.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sapphiron's Wing Bone</span>\
<br>Binds when picked up<br>Held In Off Hand<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage done by Frost spells and effects by up to 51.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSapphironsWingBone; ++i;

var fTearsOfHeaven = new RewardItem("alliance","Tears of Heaven","/info/basics/factions/images/icons/INV_Potion_75.gif");
fTearsOfHeaven.itemHonorPrice = new Array();
fTearsOfHeaven.itemHonorPrice[0] = 25
fTearsOfHeaven.itemStats = new Array();
fTearsOfHeaven.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Tears of Heaven</span>\
<br>Binds when picked up<br>Held In Off Hand<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 75.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTearsOfHeaven; ++i;

var fLightBearersFaithShield = new RewardItem("alliance","Light-Bearer's Faith Shield","/info/basics/factions/images/icons/INV_Shield_33.gif");
fLightBearersFaithShield.itemHonorPrice = new Array();
fLightBearersFaithShield.itemHonorPrice[0] = 33
fLightBearersFaithShield.itemStats = new Array();
fLightBearersFaithShield.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Light-Bearer's Faith Shield</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>4261 Armor<br>101 Block<br>+21 Stamina<br>+22 Intellect<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 55.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLightBearersFaithShield; ++i;

var fOrbOfTheSoulEater = new RewardItem("alliance","Orb of the Soul-Eater","/info/basics/factions/images/icons/INV_Misc_Orb_04.gif");
fOrbOfTheSoulEater.itemHonorPrice = new Array();
fOrbOfTheSoulEater.itemHonorPrice[0] = 25
fOrbOfTheSoulEater.itemStats = new Array();
fOrbOfTheSoulEater.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Orb of the Soul-Eater</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+18 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage done by Shadow spells and effects by up to 51.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fOrbOfTheSoulEater; ++i;

var fAzureShieldOfColdarra = new RewardItem("alliance","Azure-Shield of Coldarra","/info/basics/factions/images/icons/INV_Shield_33.gif");
fAzureShieldOfColdarra.itemHonorPrice = new Array();
fAzureShieldOfColdarra.itemHonorPrice[0] = 33
fAzureShieldOfColdarra.itemStats = new Array();
fAzureShieldOfColdarra.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Azure-Shield of Coldarra</span>\
<br>Binds when picked up<br>Off Hand<span class=\"myRight\">Shield</span>\
<br>4668 Armor<br>115 Block<br>+31 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 33.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAzureShieldOfColdarra; ++i;

var fRingOfCrypticDreams = new RewardItem("alliance","Ring of Cryptic Dreams","/info/basics/factions/images/icons/INV_Jewelry_Ring_56.gif");
fRingOfCrypticDreams.itemHonorPrice = new Array();
fRingOfCrypticDreams.itemHonorPrice[0] = 25
fRingOfCrypticDreams.itemStats = new Array();
fRingOfCrypticDreams.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Ring of Cryptic Dreams</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+16 Stamina<br>+17 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRingOfCrypticDreams; ++i;


var fBandOfHalos = new RewardItem("alliance","Band of Halos","/info/basics/factions/images/icons/INV_Jewelry_Ring_53.gif");
fBandOfHalos.itemHonorPrice = new Array();
fBandOfHalos.itemHonorPrice[0] = 25
fBandOfHalos.itemStats = new Array();
fBandOfHalos.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of Halos</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+22 Stamina<br>+21 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfHalos; ++i;

var fRingOfArathiWarlords = new RewardItem("alliance","Ring of Arathi Warlords","/info/basics/factions/images/icons/jewelry_ring_aq_01.gif");
fRingOfArathiWarlords.itemHonorPrice = new Array();
fRingOfArathiWarlords.itemHonorPrice[0] = 25
fRingOfArathiWarlords.itemStats = new Array();
fRingOfArathiWarlords.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Ring of Arathi Warlords</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRingOfArathiWarlords; ++i;


var fRingOfUnyieldingForce = new RewardItem("alliance","Ring of Unyielding Force","/info/basics/factions/images/icons/INV_Jewelry_Ring_46.gif");
fRingOfUnyieldingForce.itemHonorPrice = new Array();
fRingOfUnyieldingForce.itemHonorPrice[0] = 25
fRingOfUnyieldingForce.itemStats = new Array();
fRingOfUnyieldingForce.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Ring of Unyielding Force</span>\
<br>Binds when picked up<br>Unique<br>Finger<br><span class=\"myGreen\">294 Armor</span><br>+31 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRingOfUnyieldingForce; ++i;

var fManasurgePendant = new RewardItem("alliance","Manasurge Pendant","/info/basics/factions/images/icons/INV_Jewelry_Necklace_30.gif");
fManasurgePendant.itemHonorPrice = new Array();
fManasurgePendant.itemHonorPrice[0] = 25
fManasurgePendant.itemStats = new Array();
fManasurgePendant.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Manasurge Pendant</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+24 Stamina<br>+22 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 28.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fManasurgePendant; ++i;


var fNecklaceOfEternalHope = new RewardItem("alliance","Necklace of Eternal Hope","/info/basics/factions/images/icons/INV_Jewelry_Necklace_31.gif");
fNecklaceOfEternalHope.itemHonorPrice = new Array();
fNecklaceOfEternalHope.itemHonorPrice[0] = 25
fNecklaceOfEternalHope.itemStats = new Array();
fNecklaceOfEternalHope.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Necklace of Eternal Hope</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+22 Stamina<br>+21 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 48.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNecklaceOfEternalHope; ++i;

var fChokerOfVileIntent = new RewardItem("alliance","Choker of Vile Intent","/info/basics/factions/images/icons/INV_Jewelry_Necklace_04.gif");
fChokerOfVileIntent.itemHonorPrice = new Array();
fChokerOfVileIntent.itemHonorPrice[0] = 25
fChokerOfVileIntent.itemStats = new Array();
fChokerOfVileIntent.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Choker of Vile Intent</span>\
<br>Binds when picked up<br>Neck<br>+20 Agility<br>+18 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 42.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fChokerOfVileIntent; ++i;

var fNecklaceOfTheJuggernaut = new RewardItem("alliance","Necklace of the Juggernaut","/info/basics/factions/images/icons/inv_jewelry_necklace_03.gif");
fNecklaceOfTheJuggernaut.itemHonorPrice = new Array();
fNecklaceOfTheJuggernaut.itemHonorPrice[0] = 25
fNecklaceOfTheJuggernaut.itemStats = new Array();
fNecklaceOfTheJuggernaut.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Necklace of the Juggernaut</span>\
<br>Binds when picked up<br>Neck<br>+19 Agility<br>+33 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNecklaceOfTheJuggernaut; ++i;


var fShawlOfShiftingProbabilities = new RewardItem("alliance","Shawl of Shifting Probabilities","/info/basics/factions/images/icons/INV_Misc_Cape_16.gif");
fShawlOfShiftingProbabilities.itemHonorPrice = new Array();
fShawlOfShiftingProbabilities.itemHonorPrice[0] = 25
fShawlOfShiftingProbabilities.itemStats = new Array();
fShawlOfShiftingProbabilities.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Shawl of Shifting Probabilities</span>\
<br>Binds when picked up<br>Back<br>93 Armor<br>+18 Stamina<br>+16 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fShawlOfShiftingProbabilities; ++i;

var fBishopsCloak = new RewardItem("alliance","Bishop's Cloak","/info/basics/factions/images/icons/INV_Misc_Cape_02.gif");
fBishopsCloak.itemHonorPrice = new Array();
fBishopsCloak.itemHonorPrice[0] = 25
fBishopsCloak.itemStats = new Array();
fBishopsCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bishop's Cloak</span>\
<br>Binds when picked up<br>Back<br>93 Armor<br>+16 Stamina<br>+17 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 46.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBishopsCloak; ++i;


var fBloodKnightWarCloak = new RewardItem("alliance","Blood Knight War Cloak","/info/basics/factions/images/icons/INV_Misc_Cape_18.gif");
fBloodKnightWarCloak.itemHonorPrice = new Array();
fBloodKnightWarCloak.itemHonorPrice[0] = 25
fBloodKnightWarCloak.itemStats = new Array();
fBloodKnightWarCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Blood Knight War Cloak</span>\
<br>Binds when picked up<br>Back<br>93 Armor<br>+23 Agility<br>+22 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 48.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBloodKnightWarCloak; ++i;

var fFarstriderDefendersCloak = new RewardItem("alliance","Farstrider Defender's Cloak","/info/basics/factions/images/icons/INV_Misc_Cape_Naxx_02.gif");
fFarstriderDefendersCloak.itemHonorPrice = new Array();
fFarstriderDefendersCloak.itemHonorPrice[0] = 25
fFarstriderDefendersCloak.itemStats = new Array();
fFarstriderDefendersCloak.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Farstrider Defender's Cloak</span>\
<br>Binds when picked up<br>Back<br><span class=\"myGreen\">267 Armor</span><br>+30 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFarstriderDefendersCloak; ++i;


var fIconOfTheSilverCrescent = new RewardItem("alliance","Icon of the Silver Crescent","/info/basics/factions/images/icons/INV_Weapon_Shortblade_23.gif");
fIconOfTheSilverCrescent.itemHonorPrice = new Array();
fIconOfTheSilverCrescent.itemHonorPrice[0] = 41
fIconOfTheSilverCrescent.itemStats = new Array();
fIconOfTheSilverCrescent.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Icon of the Silver Crescent</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 43.</span>\
<br>\
<span class=\"myGreen\">Use: Increases damage and healing done by magical spells and effects by up to 155 for 20 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIconOfTheSilverCrescent; ++i;

var fEssenceOfTheMartyr = new RewardItem("alliance","Essence of the Martyr","/info/basics/factions/images/icons/inv_valentinepurefumebottle.gif");
fEssenceOfTheMartyr.itemHonorPrice = new Array();
fEssenceOfTheMartyr.itemHonorPrice[0] = 41
fEssenceOfTheMartyr.itemTokenPrice = new Array();
fEssenceOfTheMartyr.itemTokenPrice[0] = new Array(0,0,0,0);
fEssenceOfTheMartyr.itemStats = new Array();
fEssenceOfTheMartyr.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Essence of the Martyr</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 84.</span>\
<br>\
<span class=\"myGreen\">Use: Increases healing done by spells by up to 297 for 20 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fEssenceOfTheMartyr; ++i;

var fBloodlustBrooch = new RewardItem("alliance","Bloodlust Brooch","/info/basics/factions/images/icons/INV_Misc_MonsterScales_15.gif");
fBloodlustBrooch.itemHonorPrice = new Array();
fBloodlustBrooch.itemHonorPrice[0] = 41
fBloodlustBrooch.itemTokenPrice = new Array();
fBloodlustBrooch.itemTokenPrice[0] = new Array(0,0,0,0);
fBloodlustBrooch.itemStats = new Array();
fBloodlustBrooch.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bloodlust Brooch</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 72.</span>\
<br>\
<span class=\"myGreen\">Use: Increases attack power by 278 for 20 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBloodlustBrooch; ++i;


var fGnomereganAutoBlocker600 = new RewardItem("alliance","Gnomeregan Auto-Blocker 600","/info/basics/factions/images/icons/INV_Battery_02.gif");
fGnomereganAutoBlocker600.itemHonorPrice = new Array();
fGnomereganAutoBlocker600.itemHonorPrice[0] = 41
fGnomereganAutoBlocker600.itemTokenPrice = new Array();
fGnomereganAutoBlocker600.itemTokenPrice = new Array();
fGnomereganAutoBlocker600.itemTokenPrice[0] = new Array(0,0,0,0);
fGnomereganAutoBlocker600.itemStats = new Array();
fGnomereganAutoBlocker600.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gnomeregan Auto-Blocker 600</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 59.</span>\
<br>\
<span class=\"myGreen\">Use: Increases the block value of your shield by 200 for 20 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGnomereganAutoBlocker600; ++i;


var fEverbloomIdol = new RewardItem("alliance","Everbloom Idol","/info/basics/factions/images/icons/Inv_relics_idolofheath.gif");
fEverbloomIdol.itemHonorPrice = new Array();
fEverbloomIdol.itemHonorPrice[0] = 15
fEverbloomIdol.itemTokenPrice = new Array();
fEverbloomIdol.itemTokenPrice[0] = new Array(0,0,0,0);
fEverbloomIdol.itemStats = new Array();
fEverbloomIdol.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Everbloom Idol</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Idol</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases the damage dealt by Shred by 88.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fEverbloomIdol; ++i;

var fLibramOfRepentance = new RewardItem("alliance","Libram of Repentance","/info/basics/factions/images/icons/inv_relics_libramofhope.gif");
fLibramOfRepentance.itemHonorPrice = new Array();
fLibramOfRepentance.itemHonorPrice[0] = 15
fLibramOfRepentance.itemTokenPrice = new Array();
fLibramOfRepentance.itemTokenPrice[0] = new Array(0,0,0,0);
fLibramOfRepentance.itemStats = new Array();
fLibramOfRepentance.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Libram of Repentance</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Libram</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases your block rating by 42 while Holy Shield is active.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLibramOfRepentance; ++i;

var fTotemOfThePulsingEarth = new RewardItem("alliance","Totem of the Pulsing Earth","/info/basics/factions/images/icons/INV_Elemental_Primal_Earth.gif");
fTotemOfThePulsingEarth.itemHonorPrice = new Array();
fTotemOfThePulsingEarth.itemHonorPrice[0] = 15
fTotemOfThePulsingEarth.itemTokenPrice = new Array();
fTotemOfThePulsingEarth.itemTokenPrice[0] = new Array(0,0,0,0);
fTotemOfThePulsingEarth.itemStats = new Array();
fTotemOfThePulsingEarth.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Totem of the Pulsing Earth</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Totem</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Reduces the mana cost of Lightning Bolt by 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTotemOfThePulsingEarth; ++i;

var fPrimalNether = new RewardItem("alliance","Primal Nether","/info/basics/factions/images/icons/INV_Elemental_Primal_Nether.gif");
fPrimalNether.itemHonorPrice = new Array();
fPrimalNether.itemHonorPrice[0] = 10
fPrimalNether.itemTokenPrice = new Array();
fPrimalNether.itemTokenPrice[0] = new Array(0,0,0,0);
fPrimalNether.itemStats = new Array();
fPrimalNether.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Primal Nether</span>\
<br>Binds when picked up</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPrimalNether; ++i;

var fInfernoForgedBoots = new RewardItem("alliance","Inferno Forged Boots","/info/basics/factions/images/icons/INV_Boots_Chain_08.gif");
fInfernoForgedBoots.itemHonorPrice = new Array();
fInfernoForgedBoots.itemHonorPrice[0] = 20
fInfernoForgedBoots.itemTokenPrice = new Array();
fInfernoForgedBoots.itemTokenPrice[0] = new Array(0,0,0,0);
fInfernoForgedBoots.itemStats = new Array();
fInfernoForgedBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Forged Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>558 Armor<br>+36 Stamina<br>+45 Fire Resistance<br>Durability 70 / 70<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoForgedBoots; ++i;

var fInfernoForgedGloves = new RewardItem("alliance","Inferno Forged Gloves","/info/basics/factions/images/icons/INV_Gauntlets_10.gif");
fInfernoForgedGloves.itemHonorPrice = new Array();
fInfernoForgedGloves.itemHonorPrice[0] = 20
fInfernoForgedGloves.itemTokenPrice = new Array();
fInfernoForgedGloves.itemTokenPrice[0] = new Array(0,0,0,0);
fInfernoForgedGloves.itemStats = new Array();
fInfernoForgedGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Forged Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>507 Armor<br>+52 Stamina<br>+40 Fire Resistance<br>Durability 50 / 50<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoForgedGloves; ++i;

var fInfernoForgedHauberk = new RewardItem("alliance","Inferno Forged Hauberk","/info/basics/factions/images/icons/INV_Chest_Plate09.gif");
fInfernoForgedHauberk.itemHonorPrice = new Array();
fInfernoForgedHauberk.itemHonorPrice[0] = 30
fInfernoForgedHauberk.itemTokenPrice = new Array();
fInfernoForgedHauberk.itemTokenPrice[0] = new Array(0,0,0,0);
fInfernoForgedHauberk.itemStats = new Array();
fInfernoForgedHauberk.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Forged Hauberk</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>812 Armor<br>+54 Stamina<br>+60 Fire Resistance<br>Durability 140 / 140<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoForgedHauberk; ++i;

var fInfernoForgedLeggings = new RewardItem("alliance","Inferno Forged Leggings","/info/basics/factions/images/icons/INV_Pants_Mail_14.gif");
fInfernoForgedLeggings.itemHonorPrice = new Array();
fInfernoForgedLeggings.itemHonorPrice[0] = 30
fInfernoForgedLeggings.itemTokenPrice = new Array();
fInfernoForgedLeggings.itemTokenPrice[0] = new Array(0,0,0,0);
fInfernoForgedLeggings.itemStats = new Array();
fInfernoForgedLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Forged Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>710 Armor<br>+69 Stamina<br>+55 Fire Resistance<br>Durability 105 / 105<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoForgedLeggings; ++i;


var fInfernoHardenedBoots = new RewardItem("alliance","Inferno Hardened Boots","/info/basics/factions/images/icons/INV_Boots_07.gif");
fInfernoHardenedBoots.itemHonorPrice = new Array();
fInfernoHardenedBoots.itemHonorPrice[0] = 20
fInfernoHardenedBoots.itemTokenPrice = new Array();
fInfernoHardenedBoots.itemTokenPrice[0] = new Array(0,0,0,0);
fInfernoHardenedBoots.itemStats = new Array();
fInfernoHardenedBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Hardened Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>250 Armor<br>+36 Stamina<br>+45 Fire Resistance<br>Durability 60 / 60<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoHardenedBoots; ++i;


var fInfernoHardenedChestguard = new RewardItem("alliance","Inferno Hardened Chestguard","/info/basics/factions/images/icons/INV_Chest_Leather_07.gif");
fInfernoHardenedChestguard.itemHonorPrice = new Array();
fInfernoHardenedChestguard.itemHonorPrice[0] = 30
fInfernoHardenedChestguard.itemStats = new Array();
fInfernoHardenedChestguard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Hardened Chestguard</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>364 Armor<br>+54 Stamina<br>+60 Fire Resistance<br>Durability 120 / 120<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoHardenedChestguard; ++i;

var fInfernoHardenedGloves = new RewardItem("alliance","Inferno Hardened Gloves","/info/basics/factions/images/icons/INV_Gauntlets_26.gif");
fInfernoHardenedGloves.itemHonorPrice = new Array();
fInfernoHardenedGloves.itemHonorPrice[0] = 20
fInfernoHardenedGloves.itemStats = new Array();
fInfernoHardenedGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Hardened Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>228 Armor<br>+52 Stamina<br>+40 Fire Resistance<br>Durability 40 / 40<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoHardenedGloves; ++i;

var fInfernoHardenedLeggings = new RewardItem("alliance","Inferno Hardened Leggings","/info/basics/factions/images/icons/INV_Pants_Leather_18.gif");
fInfernoHardenedLeggings.itemHonorPrice = new Array();
fInfernoHardenedLeggings.itemHonorPrice[0] = 30
fInfernoHardenedLeggings.itemTokenPrice = new Array();
fInfernoHardenedLeggings.itemTokenPrice[0] = new Array(0,0,0,0);
fInfernoHardenedLeggings.itemStats = new Array();
fInfernoHardenedLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Hardened Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>319 Armor<br>+69 Stamina<br>+55 Fire Resistance<br>Durability 90 / 90<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoHardenedLeggings; ++i;

var fInfernoTemperedBoots = new RewardItem("alliance","Inferno Tempered Boots","/info/basics/factions/images/icons/INV_Boots_Chain_08.gif");
fInfernoTemperedBoots.itemHonorPrice = new Array();
fInfernoTemperedBoots.itemHonorPrice[0] = 30
fInfernoTemperedBoots.itemStats = new Array();
fInfernoTemperedBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Tempered Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>997 Armor<br>+36 Stamina<br>+45 Fire Resistance<br>Durability 75 / 75<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoTemperedBoots; ++i;




var fInfernoTemperedChestguard = new RewardItem("alliance","Inferno Tempered Chestguard","/info/basics/factions/images/icons/INV_Chest_Plate09.gif");
fInfernoTemperedChestguard.itemHonorPrice = new Array();
fInfernoTemperedChestguard.itemHonorPrice[0] = 30
fInfernoTemperedChestguard.itemTokenPrice = new Array();
fInfernoTemperedChestguard.itemTokenPrice[0] = new Array(0,0,0,0);
fInfernoTemperedChestguard.itemStats = new Array();
fInfernoTemperedChestguard.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Tempered Chestguard</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1450 Armor<br>+54 Stamina<br>+60 Fire Resistance<br>Durability 165 / 165<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoTemperedChestguard; ++i;


var fInfernoTemperedGauntlets = new RewardItem("alliance","Inferno Tempered Gauntlets","/info/basics/factions/images/icons/INV_Gauntlets_22.gif");
fInfernoTemperedGauntlets.itemHonorPrice = new Array();
fInfernoTemperedGauntlets.itemHonorPrice[0] = 20
fInfernoTemperedGauntlets.itemStats = new Array();
fInfernoTemperedGauntlets.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Tempered Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>906 Armor<br>+52 Stamina<br>+40 Fire Resistance<br>Durability 55 / 55<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoTemperedGauntlets; ++i;


var fInfernoTemperedLeggings = new RewardItem("alliance","Inferno Tempered Leggings","/info/basics/factions/images/icons/INV_Pants_04.gif");
fInfernoTemperedLeggings.itemHonorPrice = new Array();
fInfernoTemperedLeggings.itemHonorPrice[0] = 30
fInfernoTemperedLeggings.itemStats = new Array();
fInfernoTemperedLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Inferno Tempered Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1269 Armor<br>+69 Stamina<br>+55 Fire Resistance<br>Durability 120 / 120<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoTemperedLeggings; ++i;

var fInfernoweaveBoots = new RewardItem("alliance","Infernoweave Boots","/info/basics/factions/images/icons/INV_Boots_02.gif");
fInfernoweaveBoots.itemHonorPrice = new Array();
fInfernoweaveBoots.itemHonorPrice[0] = 20
fInfernoweaveBoots.itemStats = new Array();
fInfernoweaveBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Infernoweave Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Cloth</span>\
<br>134 Armor<br>+36 Stamina<br>+45 Fire Resistance<br>Durability 50 / 50<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoweaveBoots; ++i;

var fInfernoweaveGloves = new RewardItem("alliance","Infernoweave Gloves","/info/basics/factions/images/icons/INV_Gauntlets_26.gif");
fInfernoweaveGloves.itemHonorPrice = new Array();
fInfernoweaveGloves.itemHonorPrice[0] = 20
fInfernoweaveGloves.itemStats = new Array();
fInfernoweaveGloves.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Infernoweave Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>121 Armor<br>+52 Stamina<br>+40 Fire Resistance<br>Durability 35 / 35<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoweaveGloves; ++i;

var fInfernoweaveLeggings = new RewardItem("alliance","Infernoweave Leggings","/info/basics/factions/images/icons/INV_Pants_06.gif");
fInfernoweaveLeggings.itemHonorPrice = new Array();
fInfernoweaveLeggings.itemHonorPrice[0] = 20
fInfernoweaveLeggings.itemStats = new Array();
fInfernoweaveLeggings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Infernoweave Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>170 Armor<br>+69 Stamina<br>+55 Fire Resistance<br>Durability 75 / 75<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoweaveLeggings; ++i;

var fInfernoweaveRobe = new RewardItem("alliance","Infernoweave Robe","/info/basics/factions/images/icons/INV_Chest_Cloth_18.gif");
fInfernoweaveRobe.itemHonorPrice = new Array();
fInfernoweaveRobe.itemHonorPrice[0] = 30
fInfernoweaveRobe.itemStats = new Array();
fInfernoweaveRobe.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Infernoweave Robe</span>\
<br>Binds when picked up<br>Robe<span class=\"myRight\">Cloth</span>\
<br>194 Armor<br>+54 Stamina<br>+60 Fire Resistance<br>Durability 100 / 100<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInfernoweaveRobe; ++i;

var fFaceguardOfDetermination = new RewardItem("alliance","Faceguard of Determination","/info/basics/factions/images/icons/INV_Helmet_01.gif");
fFaceguardOfDetermination.itemHonorPrice = new Array();
fFaceguardOfDetermination.itemHonorPrice[0] = 50
fFaceguardOfDetermination.itemStats = new Array();
fFaceguardOfDetermination.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Faceguard of Determination</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>1129 Armor<br>+36 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myMetaGem\">Meta Socket</span><span class=\"myGray\">Socket Bonus: +6 Stamina</span>\
<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 32.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your dodge rating by 24.</span>\
<br>\
<span class=\"myGreen\">Increases your shield block rating by 24.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFaceguardOfDetermination; ++i;

var fHelmetOfTheSteadfastChampion = new RewardItem("alliance","Helmet of the Steadfast Champion","/info/basics/factions/images/icons/INV_Helmet_16.gif");
fHelmetOfTheSteadfastChampion.itemHonorPrice = new Array();
fHelmetOfTheSteadfastChampion.itemHonorPrice[0] = 50
fHelmetOfTheSteadfastChampion.itemStats = new Array();
fHelmetOfTheSteadfastChampion.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Helmet of the Steadfast Champion</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>1129 Armor<br>+36 Stamina<br>+24 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: 2 mana per 5 sec.</span>\
<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 70.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 10 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHelmetOfTheSteadfastChampion; ++i;

var fCowlOfBeastlyRage = new RewardItem("alliance","Cowl of Beastly Rage","/info/basics/factions/images/icons/INV_Helmet_38.gif");
fCowlOfBeastlyRage.itemHonorPrice = new Array();
fCowlOfBeastlyRage.itemHonorPrice[0] = 50
fCowlOfBeastlyRage.itemStats = new Array();
fCowlOfBeastlyRage.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Cowl of Beastly Rage</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br><span class=\"myGreen\">423 Armor</span><br>+29 Strength<br>+26 Agility<br>+27 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myMetaGem\">Meta Socket</span><span class=\"myGray\">Socket Bonus: +4 Strength</span>\
<br>Durability 70 / 70<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCowlOfBeastlyRage; ++i;

var fMaskOfTheDeceiver = new RewardItem("alliance","Mask of the Deceiver","/info/basics/factions/images/icons/INV_Helmet_73.gif");
fMaskOfTheDeceiver.itemHonorPrice = new Array();
fMaskOfTheDeceiver.itemHonorPrice[0] = 50
fMaskOfTheDeceiver.itemStats = new Array();
fMaskOfTheDeceiver.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Mask of the Deceiver</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>283 Armor<br>+32 Agility<br>+36 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myMetaGem\">Meta Socket</span><span class=\"myGray\">Socket Bonus: +4 Agility</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 64.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMaskOfTheDeceiver; ++i;

var fStormMastersHelmet = new RewardItem("alliance","Storm Master's Helmet","/info/basics/factions/images/icons/INV_Helmet_69.gif");
fStormMastersHelmet.itemHonorPrice = new Array();
fStormMastersHelmet.itemHonorPrice[0] = 50
fStormMastersHelmet.itemStats = new Array();
fStormMastersHelmet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Storm Master's Helmet</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>632 Armor<br>+24 Stamina<br>+32 Intellect<span class=\"myMetaGem\">Meta Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Crit Rating</span>\
<br>Durability 85 / 85<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 37.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormMastersHelmet; ++i;

var fWarpstalkerHelm = new RewardItem("alliance","Warpstalker Helm","/info/basics/factions/images/icons/INV_Helmet_72.gif");
fWarpstalkerHelm.itemHonorPrice = new Array();
fWarpstalkerHelm.itemHonorPrice[0] = 50
fWarpstalkerHelm.itemStats = new Array();
fWarpstalkerHelm.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Warpstalker Helm</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Mail</span>\
<br>632 Armor<br>+24 Agility<br>+36 Stamina<br>+32 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myMetaGem\">Meta Socket</span><span class=\"myGray\">Socket Bonus: 2 mana per 5 sec.</span>\
<br>Durability 85 / 85<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 48.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarpstalkerHelm; ++i;

var fManaBindersCowl = new RewardItem("alliance","Mana-Binders Cowl","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fManaBindersCowl.itemHonorPrice = new Array();
fManaBindersCowl.itemHonorPrice[0] = 50
fManaBindersCowl.itemStats = new Array();
fManaBindersCowl.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Mana-Binders Cowl</span>\
<br>Binds when picked up<br>Unique<br>Head<span class=\"myRight\">Cloth</span>\
<br>151 Armor<br>+38 Stamina<br>+29 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myMetaGem\">Meta Socket</span><span class=\"myGray\">Socket Bonus: +5 Spell Damage</span>\
<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fManaBindersCowl; ++i;

var fCowlOfNaaruBlessings = new RewardItem("alliance","Cowl of Naaru Blessings","/info/basics/factions/images/icons/INV_Helmet_30.gif");
fCowlOfNaaruBlessings.itemHonorPrice = new Array();
fCowlOfNaaruBlessings.itemHonorPrice[0] = 50
fCowlOfNaaruBlessings.itemStats = new Array();
fCowlOfNaaruBlessings.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Cowl of Naaru Blessings</span>\
<br>Binds when picked up<br>Unique<br>Head<span class=\"myRight\">Cloth</span>\
<br>151 Armor<br>+28 Stamina<br>+29 Intellect<br>+23 Spirit<span class=\"myBlueGem\">Blue Socket</span><span class=\"myMetaGem\">Meta Socket</span><span class=\"myGray\">Socket Bonus: +9 Healing</span>\
<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 66.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCowlOfNaaruBlessings; ++i;




//-------------------------------------------------------------------
//---Horde below






//------END REWARDS DEFINITION------
