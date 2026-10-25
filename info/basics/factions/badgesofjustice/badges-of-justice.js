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

var fKhadgarsKnapsack = new RewardItem("alliance","Khadgar's Knapsack","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Bag_10_Green.gif&reason=external-or-uncollected-resource");
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

var fTalismanOfKalecgos = new RewardItem("alliance","Talisman of Kalecgos","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Offhand_OutlandRaid_02.gif&reason=external-or-uncollected-resource");
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


var fMazthorilHonorShield = new RewardItem("alliance","Mazthoril Honor Shield","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Shield_37.gif&reason=external-or-uncollected-resource");
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

var fSearingSunblade = new RewardItem("alliance","Searing Sunblade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fknife.gif&reason=external-or-uncollected-resource");
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

var fFlametongueSeal = new RewardItem("alliance","Flametongue Seal","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_spell_fire_sealoffire.png");
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

var fSapphironsWingBone = new RewardItem("alliance","Sapphiron's Wing Bone","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Bone_01.gif&reason=external-or-uncollected-resource");
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

var fTearsOfHeaven = new RewardItem("alliance","Tears of Heaven","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Potion_75.gif&reason=external-or-uncollected-resource");
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

var fLightBearersFaithShield = new RewardItem("alliance","Light-Bearer's Faith Shield","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_shield_33.jpg");
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

var fOrbOfTheSoulEater = new RewardItem("alliance","Orb of the Soul-Eater","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_orb_04.jpg");
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

var fAzureShieldOfColdarra = new RewardItem("alliance","Azure-Shield of Coldarra","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_shield_33.jpg");
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

var fRingOfCrypticDreams = new RewardItem("alliance","Ring of Cryptic Dreams","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_56.gif&reason=external-or-uncollected-resource");
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


var fBandOfHalos = new RewardItem("alliance","Band of Halos","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_53.gif&reason=external-or-uncollected-resource");
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

var fRingOfArathiWarlords = new RewardItem("alliance","Ring of Arathi Warlords","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fjewelry_ring_aq_01.gif&reason=external-or-uncollected-resource");
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


var fRingOfUnyieldingForce = new RewardItem("alliance","Ring of Unyielding Force","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_ring_46.jpg");
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

var fManasurgePendant = new RewardItem("alliance","Manasurge Pendant","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_necklace_30.jpg");
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


var fNecklaceOfEternalHope = new RewardItem("alliance","Necklace of Eternal Hope","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_necklace_31.jpg");
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

var fChokerOfVileIntent = new RewardItem("alliance","Choker of Vile Intent","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_necklace_04.jpg");
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

var fNecklaceOfTheJuggernaut = new RewardItem("alliance","Necklace of the Juggernaut","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_necklace_03.jpg");
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


var fShawlOfShiftingProbabilities = new RewardItem("alliance","Shawl of Shifting Probabilities","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Cape_16.gif&reason=external-or-uncollected-resource");
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

var fBishopsCloak = new RewardItem("alliance","Bishop's Cloak","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Cape_02.gif&reason=external-or-uncollected-resource");
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


var fBloodKnightWarCloak = new RewardItem("alliance","Blood Knight War Cloak","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_cape_18.jpg");
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

var fFarstriderDefendersCloak = new RewardItem("alliance","Farstrider Defender's Cloak","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Cape_Naxx_02.gif&reason=external-or-uncollected-resource");
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


var fIconOfTheSilverCrescent = new RewardItem("alliance","Icon of the Silver Crescent","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Shortblade_23.gif&reason=external-or-uncollected-resource");
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

var fEssenceOfTheMartyr = new RewardItem("alliance","Essence of the Martyr","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Finv_valentinepurefumebottle.gif&reason=external-or-uncollected-resource");
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

var fBloodlustBrooch = new RewardItem("alliance","Bloodlust Brooch","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_MonsterScales_15.gif&reason=external-or-uncollected-resource");
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


var fGnomereganAutoBlocker600 = new RewardItem("alliance","Gnomeregan Auto-Blocker 600","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_battery_02.jpg");
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


var fEverbloomIdol = new RewardItem("alliance","Everbloom Idol","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FInv_relics_idolofheath.gif&reason=external-or-uncollected-resource");
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

var fLibramOfRepentance = new RewardItem("alliance","Libram of Repentance","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_relics_libramofhope.jpg");
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

var fTotemOfThePulsingEarth = new RewardItem("alliance","Totem of the Pulsing Earth","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Elemental_Primal_Earth.gif&reason=external-or-uncollected-resource");
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

var fPrimalNether = new RewardItem("alliance","Primal Nether","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Elemental_Primal_Nether.gif&reason=external-or-uncollected-resource");
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

var fInfernoForgedBoots = new RewardItem("alliance","Inferno Forged Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_chain_08.jpg");
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

var fInfernoForgedGloves = new RewardItem("alliance","Inferno Forged Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_10.jpg");
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

var fInfernoForgedHauberk = new RewardItem("alliance","Inferno Forged Hauberk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_plate09.jpg");
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

var fInfernoForgedLeggings = new RewardItem("alliance","Inferno Forged Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Mail_14.gif&reason=external-or-uncollected-resource");
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


var fInfernoHardenedBoots = new RewardItem("alliance","Inferno Hardened Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_07.jpg");
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


var fInfernoHardenedChestguard = new RewardItem("alliance","Inferno Hardened Chestguard","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_leather_07.jpg");
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

var fInfernoHardenedGloves = new RewardItem("alliance","Inferno Hardened Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_26.jpg");
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

var fInfernoHardenedLeggings = new RewardItem("alliance","Inferno Hardened Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_leather_18.jpg");
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

var fInfernoTemperedBoots = new RewardItem("alliance","Inferno Tempered Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_chain_08.jpg");
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




var fInfernoTemperedChestguard = new RewardItem("alliance","Inferno Tempered Chestguard","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_plate09.jpg");
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


var fInfernoTemperedGauntlets = new RewardItem("alliance","Inferno Tempered Gauntlets","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_22.jpg");
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


var fInfernoTemperedLeggings = new RewardItem("alliance","Inferno Tempered Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_04.gif&reason=external-or-uncollected-resource");
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

var fInfernoweaveBoots = new RewardItem("alliance","Infernoweave Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_02.jpg");
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

var fInfernoweaveGloves = new RewardItem("alliance","Infernoweave Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_26.jpg");
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

var fInfernoweaveLeggings = new RewardItem("alliance","Infernoweave Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_06.gif&reason=external-or-uncollected-resource");
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

var fInfernoweaveRobe = new RewardItem("alliance","Infernoweave Robe","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_cloth_18.jpg");
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

var fFaceguardOfDetermination = new RewardItem("alliance","Faceguard of Determination","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_01.jpg");
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

var fHelmetOfTheSteadfastChampion = new RewardItem("alliance","Helmet of the Steadfast Champion","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_16.jpg");
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

var fCowlOfBeastlyRage = new RewardItem("alliance","Cowl of Beastly Rage","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_38.jpg");
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

var fMaskOfTheDeceiver = new RewardItem("alliance","Mask of the Deceiver","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_73.jpg");
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

var fStormMastersHelmet = new RewardItem("alliance","Storm Master's Helmet","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_69.jpg");
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

var fWarpstalkerHelm = new RewardItem("alliance","Warpstalker Helm","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_72.jpg");
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

var fManaBindersCowl = new RewardItem("alliance","Mana-Binders Cowl","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
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

var fCowlOfNaaruBlessings = new RewardItem("alliance","Cowl of Naaru Blessings","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Helmet_30.gif");
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
