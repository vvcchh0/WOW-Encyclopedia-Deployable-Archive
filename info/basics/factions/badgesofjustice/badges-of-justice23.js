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

var fIdolOfTerror = new RewardItem("alliance","Idol of Terror","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fability_druid_droar.gif&reason=external-or-uncollected-resource");
fIdolOfTerror.itemHonorPrice = new Array();
fIdolOfTerror.itemHonorPrice[5] = 20
fIdolOfTerror.itemStats = new Array();
fIdolOfTerror.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Idol of Terror</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Idol</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your Mangle ability has a chance to grant 65 agility for 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIdolOfTerror; ++i;


var fIdolOfBuddingLife = new RewardItem("alliance","Idol of Budding Life","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Nature_Protection.gif&reason=external-or-uncollected-resource");
fIdolOfBuddingLife.itemHonorPrice = new Array();
fIdolOfBuddingLife.itemHonorPrice[5] = 20
fIdolOfBuddingLife.itemStats = new Array();
fIdolOfBuddingLife.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Idol of Budding Life</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Idol</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Reduces the mana cost of Rejuvenation by 36.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIdolOfBuddingLife; ++i;

var fIdolOfTheUnseenMoon = new RewardItem("alliance","Idol of the Unseen Moon","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Nature_Sentinal.gif&reason=external-or-uncollected-resource");
fIdolOfTheUnseenMoon.itemHonorPrice = new Array();
fIdolOfTheUnseenMoon.itemHonorPrice[5] = 20
fIdolOfTheUnseenMoon.itemStats = new Array();
fIdolOfTheUnseenMoon.itemStats[5] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Idol of the Unseen Moon</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Idol</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your Moonfire ability has a chance to grant up to 140 spell damage and healing for 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIdolOfTheUnseenMoon; ++i;

var fLibramOfDivineJudgement = new RewardItem("alliance","Libram of Divine Judgement","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Relics_LibramofGrace.jpg&reason=external-or-uncollected-resource");
fLibramOfDivineJudgement.itemHonorPrice = new Array();
fLibramOfDivineJudgement.itemHonorPrice[6] = 20
fLibramOfDivineJudgement.itemStats = new Array();
fLibramOfDivineJudgement.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Libram of Divine Judgement</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Libram</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your Judgement of Command ability has a chance to grant 200 attack power for 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLibramOfDivineJudgement; ++i;

var fLibramOfDivinePurpose = new RewardItem("alliance","Libram of Divine Purpose","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_relics_libramofhope.jpg");
fLibramOfDivinePurpose.itemHonorPrice = new Array();
fLibramOfDivinePurpose.itemHonorPrice[6] = 20
fLibramOfDivinePurpose.itemStats = new Array();
fLibramOfDivinePurpose.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Libram of Divine Purpose</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Libram</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases the damage done by your Seal of Righteousness and Judgement of Righteousness abilities by up to 63.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLibramOfDivinePurpose; ++i;


var fLibramOfMending = new RewardItem("alliance","Libram of Mending","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Relics_LibramofTruth.jpg&reason=external-or-uncollected-resource");
fLibramOfMending.itemHonorPrice = new Array();
fLibramOfMending.itemHonorPrice[6] = 20
fLibramOfMending.itemStats = new Array();
fLibramOfMending.itemStats[6] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Libram of Mending</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Libram</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your Holy Light spell grants 22 mana per 5 sec. for 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLibramOfMending; ++i;

var fSkycallTotem = new RewardItem("alliance","Skycall Totem","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Nature_CallStorm.gif&reason=external-or-uncollected-resource");
fSkycallTotem.itemHonorPrice = new Array();
fSkycallTotem.itemHonorPrice[7] = 20
fSkycallTotem.itemStats = new Array();
fSkycallTotem.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Skycall Totem</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Totem</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your Lightning Bolt spell has a chance to grant 100 spell haste rating for 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSkycallTotem; ++i;

var fStonebreakersTotem = new RewardItem("alliance","Stonebreaker's Totem","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Nature_Earthquake.gif&reason=external-or-uncollected-resource");
fStonebreakersTotem.itemHonorPrice = new Array();
fStonebreakersTotem.itemHonorPrice[7] = 20
fStonebreakersTotem.itemStats = new Array();
fStonebreakersTotem.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Stonebreaker's Totem</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Totem</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your Shock spells have a chance to grant 110 attack power for 10 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStonebreakersTotem; ++i;

var fTotemOfLivingWater = new RewardItem("alliance","Totem of Living Water","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Frost_SummonWaterElem.gif&reason=external-or-uncollected-resource");
fTotemOfLivingWater.itemHonorPrice = new Array();
fTotemOfLivingWater.itemHonorPrice[7] = 20
fTotemOfLivingWater.itemStats = new Array();
fTotemOfLivingWater.itemStats[7] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Totem of Living Water</span>\
<br>Binds when picked up<br>Unique<br>Relic<span class=\"myRight\">Totem</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Reduces the mana cost of Chain Heal by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTotemOfLivingWater; ++i;

var fAmaniMaskOfDeath = new RewardItem("alliance","Amani Mask of Death","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_114.jpg");
fAmaniMaskOfDeath.itemHonorPrice = new Array();
fAmaniMaskOfDeath.itemHonorPrice[4] = 75
fAmaniMaskOfDeath.itemStats = new Array();
fAmaniMaskOfDeath.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Amani Mask of Death</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Plate</span>\
<br>1306 Armor<br>+46 Strength<br>+51 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Stamina</span>\
<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 33.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAmaniMaskOfDeath; ++i;

var fBloodthirstersWargreaves = new RewardItem("alliance","Bloodthirster's Wargreaves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_plate_28.jpg");
fBloodthirstersWargreaves.itemHonorPrice = new Array();
fBloodthirstersWargreaves.itemHonorPrice[4] = 75
fBloodthirstersWargreaves.itemStats = new Array();
fBloodthirstersWargreaves.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bloodthirster's Wargreaves</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1406 Armor<br>+46 Strength<br>+43 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span>\
<span class=\"myGray\">Socket Bonus: +4 Strength</span>\
<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBloodthirstersWargreaves; ++i;


var fBonefistGauntlets = new RewardItem("alliance","Bonefist Gauntlets","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_67.jpg");
fBonefistGauntlets.itemHonorPrice = new Array();
fBonefistGauntlets.itemHonorPrice[4] = 60
fBonefistGauntlets.itemStats = new Array();
fBonefistGauntlets.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bonefist Gauntlets</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>1005 Armor<br>+51 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Stamina</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases your parry rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBonefistGauntlets; ++i;

var fIrontuskGirdle = new RewardItem("alliance","Iron-tusk Girdle","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_belt_27.jpg");
fIrontuskGirdle.itemHonorPrice = new Array();
fIrontuskGirdle.itemHonorPrice[4] = 60
fIrontuskGirdle.itemStats = new Array();
fIrontuskGirdle.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Iron-tusk Girdle</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>904 Armor<br>+45 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Dodge Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your dodge rating by 33.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fIrontuskGirdle; ++i;

var fBracersOfTheAncientPhalanx = new RewardItem("alliance","Bracers of the Ancient Phalanx","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Bracer_19.gif");
fBracersOfTheAncientPhalanx.itemHonorPrice = new Array();
fBracersOfTheAncientPhalanx.itemHonorPrice[4] = 35
fBracersOfTheAncientPhalanx.itemStats = new Array();
fBracersOfTheAncientPhalanx.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Bracers of the Ancient Phalanx</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>703 Armor<br>+45 Stamina<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 23.<BR></span>\
<span class=\"myGreen\">Equip: Increases your expertise rating by 22.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBracersOfTheAncientPhalanx; ++i;

var fEterniumRageshackles = new RewardItem("alliance","Eternium Rage-shackles","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_15.jpg");
fEterniumRageshackles.itemHonorPrice = new Array();
fEterniumRageshackles.itemHonorPrice[4] = 35
fEterniumRageshackles.itemStats = new Array();
fEterniumRageshackles.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Eternium Rage-shackles</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>703 Armor<br>+32 Strength<br>+32 Stamina<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 150 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fEterniumRageshackles; ++i;

var fChainOfUnleashedRage = new RewardItem("alliance","Chain of Unleashed Rage","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_belt_18.jpg");
fChainOfUnleashedRage.itemHonorPrice = new Array();
fChainOfUnleashedRage.itemHonorPrice[4] = 60
fChainOfUnleashedRage.itemStats = new Array();
fChainOfUnleashedRage.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Chain of Unleashed Rage</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>904 Armor<br>+34 Strength<br>+37 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +3 Hit Rating</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 154 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fChainOfUnleashedRage; ++i;

var fFuriousDeathgrips = new RewardItem("alliance","Furious Deathgrips","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_67.jpg");
fFuriousDeathgrips.itemHonorPrice = new Array();
fFuriousDeathgrips.itemHonorPrice[4] = 60
fFuriousDeathgrips.itemStats = new Array();
fFuriousDeathgrips.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Furious Deathgrips</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>1005 Armor<br>+34 Strength<br>+37 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Strength</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFuriousDeathgrips; ++i;

var fPauldronsOfGruesomeFate = new RewardItem("alliance","Pauldrons of Gruesome Fate","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Shoulder_81.gif&reason=external-or-uncollected-resource");
fPauldronsOfGruesomeFate.itemHonorPrice = new Array();
fPauldronsOfGruesomeFate.itemHonorPrice[4] = 60
fPauldronsOfGruesomeFate.itemStats = new Array();
fPauldronsOfGruesomeFate.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pauldrons of Gruesome Fate</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Plate</span>\
<br>1206 Armor<br>+42 Strength<br>+33 Stamina<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 154 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPauldronsOfGruesomeFate; ++i;

var fUnwaveringLegguards = new RewardItem("alliance","Unwavering Legguards","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_plate_28.jpg");
fUnwaveringLegguards.itemHonorPrice = new Array();
fUnwaveringLegguards.itemHonorPrice[4] = 75
fUnwaveringLegguards.itemStats = new Array();
fUnwaveringLegguards.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Unwavering Legguards</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1406 Armor<br>+73 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Stamina</span>\
<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 22.</span>\
<br>\
<span class=\"myGreen\">Increases your shield block rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 59.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fUnwaveringLegguards; ++i;

var fChestguardOfTheStoicGuardian = new RewardItem("alliance","Chestguard of the Stoic Guardian","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_plate_22.jpg");
fChestguardOfTheStoicGuardian.itemHonorPrice = new Array();
fChestguardOfTheStoicGuardian.itemHonorPrice[4] = 75
fChestguardOfTheStoicGuardian.itemStats = new Array();
fChestguardOfTheStoicGuardian.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Chestguard of the Stoic Guardian</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Plate</span>\
<br>1607 Armor<br>+60 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Stamina</span>\
<br>Durability 165 / 165<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your dodge rating by 38.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fChestguardOfTheStoicGuardian; ++i;

var fGirdleOfTheProtector = new RewardItem("alliance","Girdle of the Protector","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_belt_27.jpg");
fGirdleOfTheProtector.itemHonorPrice = new Array();
fGirdleOfTheProtector.itemHonorPrice[4] = 60
fGirdleOfTheProtector.itemStats = new Array();
fGirdleOfTheProtector.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Girdle of the Protector</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Plate</span>\
<br>904 Armor<br>+40 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Stamina</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 11.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your dodge rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGirdleOfTheProtector; ++i;

var fHandguardsOfTheTemplar = new RewardItem("alliance","Handguards of the Templar","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_67.jpg");
fHandguardsOfTheTemplar.itemHonorPrice = new Array();
fHandguardsOfTheTemplar.itemHonorPrice[4] = 60
fHandguardsOfTheTemplar.itemStats = new Array();
fHandguardsOfTheTemplar.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Handguards of the Templar</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Plate</span>\
<br>1005 Armor<br>+25 Stamina<br>+28 Intellect<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Improves spell haste rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 4 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHandguardsOfTheTemplar; ++i;

var fHighJusticarsLegplates = new RewardItem("alliance","High Justicar's Legplates","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_plate_28.jpg");
fHighJusticarsLegplates.itemHonorPrice = new Array();
fHighJusticarsLegplates.itemHonorPrice[4] = 75
fHighJusticarsLegplates.itemStats = new Array();
fHighJusticarsLegplates.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">High Justicar's Legplates</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Plate</span>\
<br>1406 Armor<br>+33 Stamina<br>+37 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +9 Healing</span>\
<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 101 and damage done by up to 34 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHighJusticarsLegplates; ++i;

var fImplacableGuardianSabatons = new RewardItem("alliance","Implacable Guardian Sabatons","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_plate_10.jpg");
fImplacableGuardianSabatons.itemHonorPrice = new Array();
fImplacableGuardianSabatons.itemHonorPrice[4] = 60
fImplacableGuardianSabatons.itemStats = new Array();
fImplacableGuardianSabatons.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Implacable Guardian Sabatons</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1105 Armor<br>+21 Stamina<br>+22 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +3 Intellect</span>\
<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 10 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fImplacableGuardianSabatons; ++i;

var fSabatonsOfTheRighteousDefender = new RewardItem("alliance","Sabatons of the Righteous Defender","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_plate_10.jpg");
fSabatonsOfTheRighteousDefender.itemHonorPrice = new Array();
fSabatonsOfTheRighteousDefender.itemHonorPrice[4] = 60
fSabatonsOfTheRighteousDefender.itemStats = new Array();
fSabatonsOfTheRighteousDefender.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Sabatons of the Righteous Defender</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Plate</span>\
<br>1105 Armor<br>+45 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Stamina</span>\
<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases the block value of your shield by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSabatonsOfTheRighteousDefender; ++i;

var fVambracesOfTheNaaru = new RewardItem("alliance","Vambraces of the Naaru","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_02.jpg");
fVambracesOfTheNaaru.itemHonorPrice = new Array();
fVambracesOfTheNaaru.itemHonorPrice[4] = 35
fVambracesOfTheNaaru.itemStats = new Array();
fVambracesOfTheNaaru.itemStats[4] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vambraces of the Naaru</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Plate</span>\
<br>703 Armor<br>+12 Stamina<br>+25 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: 1 Mana per 5 sec.</span>\
<br>Durability 55 / 55<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 55 and damage done by up to 19 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVambracesOfTheNaaru; ++i;

var fGauntletsOfSniping = new RewardItem("alliance","Gauntlets of Sniping","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_25.jpg");
fGauntletsOfSniping.itemHonorPrice = new Array();
fGauntletsOfSniping.itemHonorPrice[3] = 60
fGauntletsOfSniping.itemStats = new Array();
fGauntletsOfSniping.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gauntlets of Sniping</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>562 Armor<br>+20 Agility<br>+27 Stamina<br>+20 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 58.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGauntletsOfSniping; ++i;

var fShiftingCamouflagePants = new RewardItem("alliance","Shifting Camouflage Pants","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_leather_23.jpg");
fShiftingCamouflagePants.itemHonorPrice = new Array();
fShiftingCamouflagePants.itemHonorPrice[3] = 75
fShiftingCamouflagePants.itemStats = new Array();
fShiftingCamouflagePants.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Shifting Camouflage Pants</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>787 Armor<br>+34 Agility<br>+45 Stamina<br>+30 Intellect<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 90.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 175 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fShiftingCamouflagePants; ++i;

var fWarFeatheredLoop = new RewardItem("alliance","War-Feathered Loop","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_22.gif");
fWarFeatheredLoop.itemHonorPrice = new Array();
fWarFeatheredLoop.itemHonorPrice[3] = 60
fWarFeatheredLoop.itemStats = new Array();
fWarFeatheredLoop.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">War-Feathered Loop</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>506 Armor<br>+29 Agility<br>+36 Stamina<br>+28 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 56.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 70 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWarFeatheredLoop; ++i;

var fSteadyingBracers = new RewardItem("alliance","Steadying Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_02.jpg");
fSteadyingBracers.itemHonorPrice = new Array();
fSteadyingBracers.itemHonorPrice[3] = 35
fSteadyingBracers.itemStats = new Array();
fSteadyingBracers.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Steadying Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>394 Armor<br>+18 Agility<br>+21 Stamina<br>+19 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 105 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSteadyingBracers; ++i;

var fEarthquakeBracers = new RewardItem("alliance","Earthquake Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_02.jpg");
fEarthquakeBracers.itemHonorPrice = new Array();
fEarthquakeBracers.itemHonorPrice[3] = 35
fEarthquakeBracers.itemStats = new Array();
fEarthquakeBracers.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Earthquake Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>394 Armor<br>+19 Stamina<br>+21 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fEarthquakeBracers; ++i;


var fHauberkOfTheFuriousElements = new RewardItem("alliance","Hauberk of the Furious Elements","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_mail_05.jpg");
fHauberkOfTheFuriousElements.itemHonorPrice = new Array();
fHauberkOfTheFuriousElements.itemHonorPrice[3] = 75
fHauberkOfTheFuriousElements.itemStats = new Array();
fHauberkOfTheFuriousElements.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Hauberk of the Furious Elements</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>900 Armor<br>+39 Stamina<br>+34 Intellect<br>Durability 140 / 140<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell haste rating by 35.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 54.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHauberkOfTheFuriousElements; ++i;

var fPauldronsOfTheFuriousElements = new RewardItem("alliance","Pauldrons of the Furious Elements","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Shoulder_86.gif&reason=external-or-uncollected-resource");
fPauldronsOfTheFuriousElements.itemHonorPrice = new Array();
fPauldronsOfTheFuriousElements.itemHonorPrice[3] = 60
fPauldronsOfTheFuriousElements.itemStats = new Array();
fPauldronsOfTheFuriousElements.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pauldrons of the Furious Elements</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Mail</span>\
<br>675 Armor<br>+28 Stamina<br>+24 Intellect<br>Durability 85 / 85<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell haste rating by 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPauldronsOfTheFuriousElements; ++i;

var fGleamingEarthenBracers = new RewardItem("alliance","Gleaming Earthen Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_02.jpg");
fGleamingEarthenBracers.itemHonorPrice = new Array();
fGleamingEarthenBracers.itemHonorPrice[3] = 35
fGleamingEarthenBracers.itemStats = new Array();
fGleamingEarthenBracers.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gleaming Earthen Bracers</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Mail</span>\
<br>394 Armor<br>+18 Stamina<br>+20 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 55 and damage done by up to 19 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 10 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGleamingEarthenBracers; ++i;



var fGripsOfNaturesWrath = new RewardItem("alliance","Grips of Nature's Wrath","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_68.jpg");
fGripsOfNaturesWrath.itemHonorPrice = new Array();
fGripsOfNaturesWrath.itemHonorPrice[3] = 60
fGripsOfNaturesWrath.itemStats = new Array();
fGripsOfNaturesWrath.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Grips of Nature's Wrath</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>562 Armor<br>+30 Stamina<br>+27 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Damage</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGripsOfNaturesWrath; ++i;


var fMankindosBelt = new RewardItem("alliance","Man'kin'do's Belt","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_22.gif");
fMankindosBelt.itemHonorPrice = new Array();
fMankindosBelt.itemHonorPrice[3] = 60
fMankindosBelt.itemStats = new Array();
fMankindosBelt.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Man'kin'do's Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>506 Armor<br>+21 Stamina<br>+26 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell haste rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 64 and damage done by up to 22 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 8 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMankindosBelt; ++i;

var fNaturalLifeLeggings = new RewardItem("alliance","Natural Life Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Mail_26.gif&reason=external-or-uncollected-resource");
fNaturalLifeLeggings.itemHonorPrice = new Array();
fNaturalLifeLeggings.itemHonorPrice[3] = 75
fNaturalLifeLeggings.itemStats = new Array();
fNaturalLifeLeggings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Natural Life Leggings</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Mail</span>\
<br>787 Armor<br>+45 Stamina<br>+38 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: 2 mana per 5 sec.</span>\
<br>Durability 105 / 105<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 88 and damage done by up to 30 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNaturalLifeLeggings; ++i;


var fTreadsOfTheLifePath = new RewardItem("alliance","Treads of the Life Path","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_chain_13.jpg");
fTreadsOfTheLifePath.itemHonorPrice = new Array();
fTreadsOfTheLifePath.itemHonorPrice[3] = 60
fTreadsOfTheLifePath.itemStats = new Array();
fTreadsOfTheLifePath.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Treads of the Life Path</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>619 Armor<br>+21 Stamina<br>+33 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +7 Healing</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTreadsOfTheLifePath; ++i;

var fPolishedWaterscaleGloves = new RewardItem("alliance","Polished Waterscale Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_68.jpg");
fPolishedWaterscaleGloves.itemHonorPrice = new Array();
fPolishedWaterscaleGloves.itemHonorPrice[3] = 60
fPolishedWaterscaleGloves.itemTokenPrice = new Array();
fPolishedWaterscaleGloves.itemTokenPrice[3] = new Array(0,0,0,0);
fPolishedWaterscaleGloves.itemStats = new Array();
fPolishedWaterscaleGloves.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Polished Waterscale Gloves</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Mail</span>\
<br>562 Armor<br>+33 Stamina<br>+22 Intellect<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 13 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPolishedWaterscaleGloves; ++i;


var fStormwrap = new RewardItem("alliance","Stormwrap","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_22.gif");
fStormwrap.itemHonorPrice = new Array();
fStormwrap.itemHonorPrice[3] = 60
fStormwrap.itemStats = new Array();
fStormwrap.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Stormwrap</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Mail</span>\
<br>506 Armor<br>+21 Stamina<br>+26 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Damage</span>\
<br>Durability 50 / 50<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 13.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStormwrap; ++i;

var fTreadsOfBoomingThunder = new RewardItem("alliance","Treads of Booming Thunder","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_chain_05.jpg");
fTreadsOfBoomingThunder.itemHonorPrice = new Array();
fTreadsOfBoomingThunder.itemHonorPrice[3] = 60
fTreadsOfBoomingThunder.itemStats = new Array();
fTreadsOfBoomingThunder.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Treads of Booming Thunder</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Mail</span>\
<br>619 Armor<br>+21 Stamina<br>+33 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Spell Critical Strike Rating</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTreadsOfBoomingThunder; ++i;


var fMasterAssassinWristwraps = new RewardItem("alliance","Master Assassin Wristwraps","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fMasterAssassinWristwraps.itemHonorPrice = new Array();
fMasterAssassinWristwraps.itemHonorPrice[2] = 35
fMasterAssassinWristwraps.itemStats = new Array();
fMasterAssassinWristwraps.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Master Assassin Wristwraps</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>177 Armor<br>+17 Agility<br>+22 Stamina<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Critical Strike Rating</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMasterAssassinWristwraps; ++i;

var fShallowgraveTrousers = new RewardItem("alliance","Shallow-grave Trousers","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Leather_09.gif&reason=external-or-uncollected-resource");
fShallowgraveTrousers.itemHonorPrice = new Array();
fShallowgraveTrousers.itemHonorPrice[2] = 75
fShallowgraveTrousers.itemTokenPrice = new Array();
fShallowgraveTrousers.itemTokenPrice[2] = new Array(0,0,0,0);
fShallowgraveTrousers.itemStats = new Array();
fShallowgraveTrousers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Shallow-grave Trousers</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>353 Armor<br>+45 Agility<br>+46 Stamina<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves haste rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 92.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fShallowgraveTrousers; ++i;

var fNynjahsTabiBoots = new RewardItem("alliance","Nyn'jah's Tabi Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_07.jpg");
fNynjahsTabiBoots.itemHonorPrice = new Array();
fNynjahsTabiBoots.itemHonorPrice[2] = 60
fNynjahsTabiBoots.itemStats = new Array();
fNynjahsTabiBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Nyn'jah's Tabi Boots</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>278 Armor<br>+29 Agility<br>+21 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +3 Hit Rating</span>\
<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 60.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fNynjahsTabiBoots; ++i;

var fTrickstersStickyfingers = new RewardItem("alliance","Trickster's Stickyfingers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_50.jpg");
fTrickstersStickyfingers.itemHonorPrice = new Array();
fTrickstersStickyfingers.itemHonorPrice[2] = 60
fTrickstersStickyfingers.itemTokenPrice = new Array();
fTrickstersStickyfingers.itemTokenPrice[2] = new Array(0,0,0,0);
fTrickstersStickyfingers.itemStats = new Array();
fTrickstersStickyfingers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Trickster's Stickyfingers</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>252 Armor<br>+30 Agility<br>+28 Stamina<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves haste rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 68.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTrickstersStickyfingers; ++i;

var fArmwrapsOfTheKaldoreiProtector = new RewardItem("alliance","Armwraps of the Kaldorei Protector","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_02.jpg");
fArmwrapsOfTheKaldoreiProtector.itemHonorPrice = new Array();
fArmwrapsOfTheKaldoreiProtector.itemHonorPrice[2] = 35
fArmwrapsOfTheKaldoreiProtector.itemTokenPrice = new Array();
fArmwrapsOfTheKaldoreiProtector.itemTokenPrice[2] = new Array(0,0,0,0);
fArmwrapsOfTheKaldoreiProtector.itemStats = new Array();
fArmwrapsOfTheKaldoreiProtector.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Armwraps of the Kaldorei Protector</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>177 Armor<br>+19 Stamina<br>+22 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 26.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fArmwrapsOfTheKaldoreiProtector; ++i;


var fLifestepBelt = new RewardItem("alliance","Life-step Belt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_belt_11.jpg");
fLifestepBelt.itemHonorPrice = new Array();
fLifestepBelt.itemHonorPrice[2] = 60
fLifestepBelt.itemStats = new Array();
fLifestepBelt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Life-step Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>227 Armor<br>+20 Stamina<br>+23 Intellect<br>+22 Spirit<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +7 Healing</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLifestepBelt; ++i;


var fBandOfTheSwiftPaw = new RewardItem("alliance","Band of the Swift Paw","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_12.jpg");
fBandOfTheSwiftPaw.itemHonorPrice = new Array();
fBandOfTheSwiftPaw.itemHonorPrice[2] = 35
fBandOfTheSwiftPaw.itemStats = new Array();
fBandOfTheSwiftPaw.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Band of the Swift Paw</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>317 Armor<br>+21 Strength<br>+22 Agility<br>+31 Stamina<br>+10 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Strength</span>\
<br>Durability 40 / 40<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfTheSwiftPaw; ++i;

var fBlessedEluniteCoverings = new RewardItem("alliance","Blessed Elunite Coverings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_cloth_06.jpg");
fBlessedEluniteCoverings.itemHonorPrice = new Array();
fBlessedEluniteCoverings.itemHonorPrice[2] = 75
fBlessedEluniteCoverings.itemTokenPrice = new Array();
fBlessedEluniteCoverings.itemTokenPrice[2] = new Array(0,0,0,0);
fBlessedEluniteCoverings.itemStats = new Array();
fBlessedEluniteCoverings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Blessed Elunite Coverings</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>404 Armor<br>+33 Stamina<br>+34 Intellect<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +5 Spell Damage</span>\
<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 54.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBlessedEluniteCoverings; ++i;

var fFootwrapsOfWildEncroachment = new RewardItem("alliance","Footwraps of Wild Encroachment","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_boots_wolf.jpg");
fFootwrapsOfWildEncroachment.itemHonorPrice = new Array();
fFootwrapsOfWildEncroachment.itemHonorPrice[2] = 60
fFootwrapsOfWildEncroachment.itemStats = new Array();
fFootwrapsOfWildEncroachment.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Footwraps of Wild Encroachment</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>418 Armor<br>+29 Strength<br>+29 Agility<br>+28 Stamina<br>+19 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Strength</span>\
<br>Durability 60 / 60<br>Requires Level 70</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFootwrapsOfWildEncroachment; ++i;

var fMoonwalkers = new RewardItem("alliance","Moon-walkers","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Boots_Cloth_16.gif");
fMoonwalkers.itemHonorPrice = new Array();
fMoonwalkers.itemHonorPrice[2] = 60
fMoonwalkers.itemStats = new Array();
fMoonwalkers.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Moon-walkers</span>\
<br>Binds when picked up<br>Feet<span class=\"myRight\">Leather</span>\
<br>278 Armor<br>+30 Stamina<br>+28 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +3 Spell Hit Rating</span>\
<br>Durability 60 / 60<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMoonwalkers; ++i;

var fGnarledIronwoodPauldrons = new RewardItem("alliance","Gnarled Ironwood Pauldrons","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_shoulder_83.jpg");
fGnarledIronwoodPauldrons.itemHonorPrice = new Array();
fGnarledIronwoodPauldrons.itemHonorPrice[2] = 60
fGnarledIronwoodPauldrons.itemTokenPrice = new Array();
fGnarledIronwoodPauldrons.itemTokenPrice[2] = new Array(0,0,0,0);
fGnarledIronwoodPauldrons.itemStats = new Array();
fGnarledIronwoodPauldrons.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gnarled Ironwood Pauldrons</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>303 Armor<br>+21 Stamina<br>+23 Intellect<br>+26 Spirit<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +7 Healing</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 73 and damage done by up to 25 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGnarledIronwoodPauldrons; ++i;

var fPantsOfSplendidRecovery = new RewardItem("alliance","Pants of Splendid Recovery","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_leather_23.jpg");
fPantsOfSplendidRecovery.itemHonorPrice = new Array();
fPantsOfSplendidRecovery.itemHonorPrice[2] = 75
fPantsOfSplendidRecovery.itemStats = new Array();
fPantsOfSplendidRecovery.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pants of Splendid Recovery</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Leather</span>\
<br>353 Armor<br>+30 Stamina<br>+40 Intellect<br>+31 Spirit<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: 2 mana per 5 sec.</span>\
<br>Durability 90 / 90<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 86 and damage done by up to 29 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPantsOfSplendidRecovery; ++i;

var fGargonsBracersPeacefulSlumber = new RewardItem("alliance","Gargon's Bracers of Peaceful Slumber","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_08.jpg");
fGargonsBracersPeacefulSlumber.itemHonorPrice = new Array();
fGargonsBracersPeacefulSlumber.itemHonorPrice[2] = 35
fGargonsBracersPeacefulSlumber.itemStats = new Array();
fGargonsBracersPeacefulSlumber.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gargon's Bracers of Peaceful Slumber</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Leather</span>\
<br>177 Armor<br>+12 Stamina<br>+25 Intellect<br>+17 Spirit<span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Healing</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 55 and damage done by up to 19 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGargonsBracersPeacefulSlumber; ++i;

var fGraspOfTheMoonkin = new RewardItem("alliance","Grasp of the Moonkin","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_50.jpg");
fGraspOfTheMoonkin.itemHonorPrice = new Array();
fGraspOfTheMoonkin.itemHonorPrice[2] = 60
fGraspOfTheMoonkin.itemTokenPrice = new Array();
fGraspOfTheMoonkin.itemTokenPrice[2] = new Array(0,0,0,0);
fGraspOfTheMoonkin.itemStats = new Array();
fGraspOfTheMoonkin.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Grasp of the Moonkin</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Leather</span>\
<br>252 Armor<br>+28 Stamina<br>+30 Intellect<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell haste rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGraspOfTheMoonkin; ++i;


var fPauldronsOfTribalFury = new RewardItem("alliance","Pauldrons of Tribal Fury","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_shoulder_83.jpg");
fPauldronsOfTribalFury.itemHonorPrice = new Array();
fPauldronsOfTribalFury.itemHonorPrice[2] = 60
fPauldronsOfTribalFury.itemStats = new Array();
fPauldronsOfTribalFury.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pauldrons of Tribal Fury</span>\
<br>Binds when picked up<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>303 Armor<br>+21 Stamina<br>+23 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Damage</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPauldronsOfTribalFury; ++i;

var fStarfireWaistband = new RewardItem("alliance","Starfire Waistband","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_belt_08.jpg");
fStarfireWaistband.itemHonorPrice = new Array();
fStarfireWaistband.itemHonorPrice[2] = 60
fStarfireWaistband.itemTokenPrice = new Array();
fStarfireWaistband.itemTokenPrice[2] = new Array(0,0,0,0);
fStarfireWaistband.itemStats = new Array();
fStarfireWaistband.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Starfire Waistband</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>227 Armor<br>+20 Stamina<br>+23 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Damage</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 22.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStarfireWaistband; ++i;

var fMaskOfPrimalPower = new RewardItem("alliance","Mask of Primal Power","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_112.jpg");
fMaskOfPrimalPower.itemHonorPrice = new Array();
fMaskOfPrimalPower.itemHonorPrice[2] = 75
fMaskOfPrimalPower.itemTokenPrice = new Array();
fMaskOfPrimalPower.itemTokenPrice[2] = new Array(0,0,0,0);
fMaskOfPrimalPower.itemStats = new Array();
fMaskOfPrimalPower.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Mask of Primal Power</span>\
<br>Binds when picked up<br>Head<span class=\"myRight\">Leather</span>\
<br>328 Armor<br>+33 Stamina<br>+39 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +5 Spell Damage</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 30.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 46.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMaskOfPrimalPower; ++i;

var fVestmentsOfHibernation = new RewardItem("alliance","Vestments of Hibernation","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_leather_08.jpg");
fVestmentsOfHibernation.itemHonorPrice = new Array();
fVestmentsOfHibernation.itemHonorPrice[2] = 75
fVestmentsOfHibernation.itemStats = new Array();
fVestmentsOfHibernation.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vestments of Hibernation</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>684 Armor<br>+46 Strength<br>+45 Agility<br>+36 Stamina<br>+13 Intellect<br>Durability 120 / 120<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 150 of your opponent's armor.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVestmentsOfHibernation; ++i;

var fWaistguardOfTheGreatBeast = new RewardItem("alliance","Waistguard of the Great Beast","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Belt_22.gif");
fWaistguardOfTheGreatBeast.itemHonorPrice = new Array();
fWaistguardOfTheGreatBeast.itemHonorPrice[2] = 60
fWaistguardOfTheGreatBeast.itemTokenPrice = new Array();
fWaistguardOfTheGreatBeast.itemTokenPrice[2] = new Array(0,0,0,0);
fWaistguardOfTheGreatBeast.itemStats = new Array();
fWaistguardOfTheGreatBeast.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Waistguard of the Great Beast</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Leather</span>\
<br>367 Armor<br>+29 Strength<br>+28 Agility<br>+30 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +3 Strength</span>\
<br>Durability 40 / 40<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 18.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWaistguardOfTheGreatBeast; ++i;


var fRunedSpellcuffs = new RewardItem("alliance","Runed Spell-cuffs","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_09.jpg");
fRunedSpellcuffs.itemHonorPrice = new Array();
fRunedSpellcuffs.itemHonorPrice[1] = 35
fRunedSpellcuffs.itemTokenPrice = new Array();
fRunedSpellcuffs.itemTokenPrice[1] = new Array(0,0,0,0);
fRunedSpellcuffs.itemStats = new Array();
fRunedSpellcuffs.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Runed Spell-cuffs</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>94 Armor<br>+20 Stamina<br>+18 Intellect<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell haste rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRunedSpellcuffs; ++i;

var fPantaloonsOfArcaneAnnihilation = new RewardItem("alliance","Pantaloons of Arcane Annihilation","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Cloth_21.gif&reason=external-or-uncollected-resource");
fPantaloonsOfArcaneAnnihilation.itemHonorPrice = new Array();
fPantaloonsOfArcaneAnnihilation.itemHonorPrice[1] = 75
fPantaloonsOfArcaneAnnihilation.itemTokenPrice = new Array();
fPantaloonsOfArcaneAnnihilation.itemTokenPrice[1] = new Array(0,0,0,0);
fPantaloonsOfArcaneAnnihilation.itemStats = new Array();
fPantaloonsOfArcaneAnnihilation.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pantaloons of Arcane Annihilation</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>188 Armor<br>+34 Stamina<br>+35 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell haste rating by 45.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 54.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPantaloonsOfArcaneAnnihilation; ++i;

var fStudiousWraps = new RewardItem("alliance","Studious Wraps","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_14.jpg");
fStudiousWraps.itemHonorPrice = new Array();
fStudiousWraps.itemHonorPrice[1] = 60
fStudiousWraps.itemStats = new Array();
fStudiousWraps.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Studious Wraps</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>135 Armor<br>+21 Stamina<br>+22 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Damage</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 25.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStudiousWraps; ++i;


var fVoodoowovenBelt = new RewardItem("alliance","Voodoo-woven Belt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_belt_03.jpg");
fVoodoowovenBelt.itemHonorPrice = new Array();
fVoodoowovenBelt.itemHonorPrice[1] = 60
fVoodoowovenBelt.itemTokenPrice = new Array();
fVoodoowovenBelt.itemTokenPrice[1] = new Array(0,0,0,0);
fVoodoowovenBelt.itemStats = new Array();
fVoodoowovenBelt.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Voodoo-woven Belt</span>\
<br>Binds when picked up<br>Waist<span class=\"myRight\">Cloth</span>\
<br>121 Armor<br>+19 Stamina<br>+22 Intellect<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 40.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVoodoowovenBelt; ++i;

var fAchromicTrousersOfTheNaaru = new RewardItem("alliance","Achromic Trousers of the Naaru","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Plate_09.gif&reason=external-or-uncollected-resource");
fAchromicTrousersOfTheNaaru.itemHonorPrice = new Array();
fAchromicTrousersOfTheNaaru.itemHonorPrice[1] = 75
fAchromicTrousersOfTheNaaru.itemTokenPrice = new Array();
fAchromicTrousersOfTheNaaru.itemTokenPrice[1] = new Array(0,0,0,0);
fAchromicTrousersOfTheNaaru.itemStats = new Array();
fAchromicTrousersOfTheNaaru.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Achromic Trousers of the Naaru</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>188 Armor<br>+34 Stamina<br>+35 Intellect<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell haste rating by 45.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 101 and damage done by up to 34 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAchromicTrousersOfTheNaaru; ++i;


var fLightBlessedBonds = new RewardItem("alliance","Light-Blessed Bonds","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_gauntlets_06.jpg");
fLightBlessedBonds.itemHonorPrice = new Array();
fLightBlessedBonds.itemHonorPrice[1] = 60
fLightBlessedBonds.itemTokenPrice = new Array();
fLightBlessedBonds.itemTokenPrice[1] = new Array(0,0,0,0);
fLightBlessedBonds.itemStats = new Array();
fLightBlessedBonds.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Light-Blessed Bonds</span>\
<br>Binds when picked up<br>Hand<span class=\"myRight\">Cloth</span>\
<br>135 Armor<br>+21 Stamina<br>+22 Intellect<br>+25 Spirit<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +7 Healing</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 75 and damage done by up to 25 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLightBlessedBonds; ++i;


var fWristguardsOfTranquilThought = new RewardItem("alliance","Wristguards of Tranquil Thought","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_bracer_07.jpg");
fWristguardsOfTranquilThought.itemHonorPrice = new Array();
fWristguardsOfTranquilThought.itemHonorPrice[1] = 35
fWristguardsOfTranquilThought.itemStats = new Array();
fWristguardsOfTranquilThought.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Wristguards of Tranquil Thought</span>\
<br>Binds when picked up<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>94 Armor<br>+12 Stamina<br>+17 Intellect<br>+16 Spirit<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 35 / 35<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 55 and damage done by up to 19 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWristguardsOfTranquilThought; ++i;


var fSlikksCloakOfPlacation = new RewardItem("alliance","Slikk's Cloak of Placation","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_cape_18.jpg");
fSlikksCloakOfPlacation.itemHonorPrice = new Array();
fSlikksCloakOfPlacation.itemHonorPrice[0] = 35
fSlikksCloakOfPlacation.itemTokenPrice = new Array();
fSlikksCloakOfPlacation.itemTokenPrice[0] = new Array(0,0,0,0);
fSlikksCloakOfPlacation.itemStats = new Array();
fSlikksCloakOfPlacation.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Slikk's Cloak of Placation</span>\
<br>Binds when picked up<br>Back<br>346 Armor<br>+37 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your dodge rating by 25.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSlikksCloakOfPlacation; ++i;

var fKharmaasShroudOfHope = new RewardItem("alliance","Kharmaa's Shroud of Hope","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_cape_06.jpg");
fKharmaasShroudOfHope.itemHonorPrice = new Array();
fKharmaasShroudOfHope.itemHonorPrice[0] = 60
fKharmaasShroudOfHope.itemStats = new Array();
fKharmaasShroudOfHope.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Kharmaa's Shroud of Hope</span>\
<br>Binds when picked up<br>Back<br>114 Armor<br>+34 Stamina<br>+15 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 51 and damage done by up to 17 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
<br>\
<span class=\"myYellow\">\"Everything happens for a reason\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fKharmaasShroudOfHope; ++i;

var fCloakOfSubjugatedPower = new RewardItem("alliance","Cloak of Subjugated Power","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_cape_20.jpg");
fCloakOfSubjugatedPower.itemHonorPrice = new Array();
fCloakOfSubjugatedPower.itemHonorPrice[0] = 60
fCloakOfSubjugatedPower.itemStats = new Array();
fCloakOfSubjugatedPower.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Cloak of Subjugated Power</span>\
<br>Binds when picked up<br>Back<br>114 Armor<br>+34 Stamina<br>+15 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 16.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 23.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 27.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCloakOfSubjugatedPower; ++i;

var fDorysEmbrace = new RewardItem("alliance","Dory's Embrace","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_cape_20.jpg");
fDorysEmbrace.itemHonorPrice = new Array();
fDorysEmbrace.itemHonorPrice[0] = 60
fDorysEmbrace.itemStats = new Array();
fDorysEmbrace.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Dory's Embrace</span>\
<br>Binds when picked up<br>Back<br>114 Armor<br>+34 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves your resilience rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 46.</span>\
<br>\
<span class=\"myGreen\">Equip: Your attacks ignore 112 of your opponent's armor.</span>\
<br>\
<span class=\"myYellow\">\"Approximately priceless.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDorysEmbrace; ++i;

var fFetishOfThePrimalGods = new RewardItem("alliance","Fetish of the Primal Gods","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Offhand_ZulAman.gif&reason=external-or-uncollected-resource");
fFetishOfThePrimalGods.itemHonorPrice = new Array();
fFetishOfThePrimalGods.itemHonorPrice[0] = 35
fFetishOfThePrimalGods.itemTokenPrice = new Array();
fFetishOfThePrimalGods.itemTokenPrice[0] = new Array(0,0,0,0);
fFetishOfThePrimalGods.itemStats = new Array();
fFetishOfThePrimalGods.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Fetish of the Primal Gods</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+24 Stamina<br>+17 Intellect<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell haste by 17.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 37.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFetishOfThePrimalGods; ++i;

var fVoodooShaker = new RewardItem("alliance","Voodoo Shaker","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Offhand_ZulAman_01.gif&reason=external-or-uncollected-resource");
fVoodooShaker.itemHonorPrice = new Array();
fVoodooShaker.itemHonorPrice[0] = 35
fVoodooShaker.itemTokenPrice = new Array();
fVoodooShaker.itemTokenPrice[0] = new Array(0,0,0,0);
fVoodooShaker.itemStats = new Array();
fVoodooShaker.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Voodoo Shaker</span>\
<br>Binds when picked up<br>Held In Off Hand<br>+18 Stamina<br>+20 Intellect<br>+25 Spirit<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 55 and damage done by up to 19 for all magical spells and effects.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVoodooShaker; ++i;

var fCarvedWitchDoctorsStick = new RewardItem("alliance","Carved Witch Doctor's Stick","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Wand_12.gif&reason=external-or-uncollected-resource");
fCarvedWitchDoctorsStick.itemHonorPrice = new Array();
fCarvedWitchDoctorsStick.itemHonorPrice[0] = 25
fCarvedWitchDoctorsStick.itemStats = new Array();
fCarvedWitchDoctorsStick.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Carved Witch Doctor's Stick</span>\
<br>Binds when picked up<br>Ranged<span class=\"myRight\">Wand</span>\
<br>184 - 343 Shadow Damage<span class=\"myRight\">Speed 1.50</span>\
<br>(175.7 damage per second)<br>+9 Stamina<br>+15 Intellect<span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +2 Spell Damage</span>\
<br>Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 18.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCarvedWitchDoctorsStick; ++i;

var fBroochOfDeftness = new RewardItem("alliance","Brooch of Deftness","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_necklace_28.jpg");
fBroochOfDeftness.itemHonorPrice = new Array();
fBroochOfDeftness.itemHonorPrice[0] = 35
fBroochOfDeftness.itemTokenPrice = new Array();
fBroochOfDeftness.itemTokenPrice[0] = new Array(0,0,0,0);
fBroochOfDeftness.itemStats = new Array();
fBroochOfDeftness.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Brooch of Deftness</span>\
<br>Binds when picked up<br>Neck<br>+48 Stamina<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 22.<BR></span>\
<span class=\"myGreen\">Equip: Increases your expertise rating by 21.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBroochOfDeftness; ++i;

var fDetermination = new RewardItem("alliance","Battlemaster's Determination","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FAbility_Warrior_EndlessRage.gif&reason=external-or-uncollected-resource");
fDetermination.itemHonorPrice = new Array();
fDetermination.itemHonorPrice[8] = 75
fDetermination.itemStats = new Array();
fDetermination.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Battlemaster's Determination</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 80.</span>\
<br>\
<span class=\"myGreen\">Use: Increases maximum health by 1750 for 15 sec. (3 Min Cooldown).</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDetermination; ++i;

var fPerseverance = new RewardItem("alliance","Battlemaster's Perseverance","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_Heroism.gif&reason=external-or-uncollected-resource");
fPerseverance.itemHonorPrice = new Array();
fPerseverance.itemHonorPrice[8] = 75
fPerseverance.itemStats = new Array();
fPerseverance.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Battlemaster's Perseverance</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases healing done by up to 88 and damage done by up to 30 for all magical spells and effects.</span>\
<br>\
<span class=\"myGreen\">Use: Increases maximum health by 1750 for 15 sec. (3 Min Cooldown).</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPerseverance; ++i;

var fAudacity = new RewardItem("alliance","Battlemaster's Audacity","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_Heroism.gif&reason=external-or-uncollected-resource");
fAudacity.itemHonorPrice = new Array();
fAudacity.itemHonorPrice[8] = 75
fAudacity.itemStats = new Array();
fAudacity.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Battlemaster's Audacity</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 47.</span>\
<br>\
<span class=\"myGreen\">Use: Increases maximum health by 1750 for 15 sec. (3 Min Cooldown).</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAudacity; ++i;

var fCruelty = new RewardItem("alliance","Battlemaster's Cruelty","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FAbility_Warrior_FocusedRage.gif&reason=external-or-uncollected-resource");
fCruelty.itemHonorPrice = new Array();
fCruelty.itemHonorPrice[8] = 75
fCruelty.itemStats = new Array();
fCruelty.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Battlemaster's Cruelty</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 40.</span>\
<br>\
<span class=\"myGreen\">Use: Increases maximum health by 1750 for 15 sec. (3 Min Cooldown).</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCruelty; ++i;

var fDepravity = new RewardItem("alliance","Battlemaster's Depravity","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fbadgesofjustice%2Fbadges-of-justice23.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FAbility_Rogue_Sinister.gif&reason=external-or-uncollected-resource");
fDepravity.itemHonorPrice = new Array();
fDepravity.itemHonorPrice[8] = 75
fDepravity.itemStats = new Array();
fDepravity.itemStats[8] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Battlemaster's Depravity</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 40.</span>\
<br>\
<span class=\"myGreen\">Use: Increases maximum health by 1750 for 15 sec. (3 Min Cooldown).</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDepravity; ++i;


//-------------------------------------------------------------------
//---Horde below






//------END REWARDS DEFINITION------
