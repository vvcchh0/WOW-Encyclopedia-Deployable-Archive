/* --------- Faction Lore ------------- */
loreTexts["alliance"] ="<h3>Kurenai</h3>\
The Kurenai are a group of Broken who have escaped the grasp of their various slavers in Outland. They recently took possession of Telaar, a town in the far south of Nagrand. Unlike many other Broken, the Kurenai are trying their best to overcome their demonic taint. Nevertheless, despite their noble intent, the Kurenai are cautious toward all outsiders, who sometimes mistake the Kurenai for their wretched brethren. A number of Kurenai also dwell in Zangarmarsh at the Orebor Harborage, where they are trying to strengthen the ties between the draenei at Telredor and the Kurenai home city of Telaar. Yet the path of the Kurenai's destiny is long and dangerous, and many threats lurk on the winding road ahead... quite literally. In order for messengers to pass swiftly between Telaar and Telredor, the roads of Zangarmarsh must be secured. The task will prove difficult, considering the marsh's abundance of mostly aggressive wildlife.\
<br /><br />\
The most imminent danger to the Kurenai, though, comes from ogres. In Zangarmarsh, the Ango'rosh ogres are moving in from the west, while in Nagrand, ogres from the Boulderfist and Warmaul clans are a constant threat to the safety of Telaar. Infighting between the ogre clans has displaced some of the big brutes from their mounds, sending them out searching for food in regions that had previously been spared the ogres' insatiable appetite. Another problem the Kurenai face in Nagrand is being caused by a different group of Broken: the Murkblood tribe. These savage Broken sacked the Mag'har settlement of Sunspring Post, slaying many orcs and destroying any chance of peaceful coexistence between Kurenai and Mag'har in the near future. To make matters worse, the Murkblood tribe seems to be planning to use their newfound strength against the people of Telaar.\
<br /><br />\
Because the Kurenai are trying to mend their ties to their draenei brethren, they are supporting the draenei's decision to join the Alliance by allowing all Alliance members to enter Telaar unharmed. Those who seek out Telaar will find that the Kurenai, although wary of strangers at first, are good people who greatly honor the friendship of their proven allies.";
loreTexts["horde"] ="<h3>The Mag'har</h3>\
South of Zangarmarsh lie the grassy plains of Nagrand, homeland of the orcs. Travelers following the northeastern roads of Nagrand will come upon a settlement of brown-skinned orcs: a place called Garadar. This village belongs to the Mag'har, a group of orcs who managed to escape any form of demonic corruption. Though they endured great change, the Mag'har have retained their traditional way of life. Nonetheless, the Mag'har are far from safe.\
<br /><br />\
With the rise of the brutish Warmaul ogres in Nagrand, the Mag'har find themselves facing a truly terrifying enemy. To make matters worse, the foul Murkblood Broken have sacked the orc village of Sunspring Post, the Mag'har's only other territorial holding in Nagrand. While the orcs combat both ogres and Broken, whispers of yet another threat linger: a force emanating from some hidden place, stirring the spirits of the orcs' long-dead ancestors.\
<br /><br />\
The Mag'har have been separated from their kin for a long time, but they still have strong ties to their Azerothian brethren. Like the Horde, the Mag'har are hostile towards all members of the Alliance.";

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

var fPatternNetherfuryBelt = new RewardItem("alliance","Pattern: Netherfury Belt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternNetherfuryBelt.itemMoneyPrice = new Array();
fPatternNetherfuryBelt.itemMoneyPrice[0] = 120000
fPatternNetherfuryBelt.itemStats = new Array();
fPatternNetherfuryBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Netherfury Belt</span>\
<br>Binds when picked up<br>Requires Leatherworking (340)<br>Requires Kurenai - Friendly<br>Use: Teaches you how to make a Netherfury Belt.<br>\
<br>\
<span class=\"myBlue\">Netherfury Belt</span>\
<br>Binds when equipped<br>Waist<span class=\"myRight\">Mail</span>\
<br>339 Armor<br>+27 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +3 Spell Crit Rating</span>\
<br>Requires Level 67<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fury of the Nether (0/3)</span>\
<br>Requires Leatherworking (350)<br><br> <span class=\"myGray\">Netherfury Belt<br> Netherfury Boots<br> Netherfury Leggings<br></span>\
<br><span class=\"myGray\">(3) Set: +20 Intellect.</span><br><br>Requires Heavy Knothide Leather (4), Crystal Infused Leather (8), Primal Water (3), Primal Mana (3), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNetherfuryBelt; ++i;

var fPatternNetherfuryLeggings = new RewardItem("alliance","Pattern: Netherfury Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternNetherfuryLeggings.itemMoneyPrice = new Array();
fPatternNetherfuryLeggings.itemMoneyPrice[1] = 120000
fPatternNetherfuryLeggings.itemStats = new Array();
fPatternNetherfuryLeggings.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Netherfury Leggings</span>\
<br>Binds when picked up<br>Requires Leatherworking (340)<br>Requires Kurenai - Honored<br>Use: Teaches you how to make Netherfury Leggings.<br>\
<br>\
<span class=\"myBlue\">Netherfury Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Mail</span>\
<br>527 Armor<br>+37 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Crit Rating</span>\
<br>Requires Level 67<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 10 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fury of the Nether (0/3)</span>\
<br>Requires Leatherworking (350)<br> <span class=\"myGray\"> Netherfury Belt<br> Netherfury Boots<br> Netherfury Leggings<br>\
<br>(3) Set: +20 Intellect.</span><br><br>Requires Heavy Knothide Leather (8), Crystal Infused Leather (12), Primal Water (5), Primal Mana (5), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNetherfuryLeggings; ++i;

var fPatternReinforcedMiningBag = new RewardItem("alliance","Pattern: Reinforced Mining Bag","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternReinforcedMiningBag.itemMoneyPrice = new Array();
fPatternReinforcedMiningBag.itemMoneyPrice[1] = 50000
fPatternReinforcedMiningBag.itemStats = new Array();
fPatternReinforcedMiningBag.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Reinforced Mining Bag<br>Binds when picked up<br>Requires Leatherworking (325)<br>Requires Kurenai - Honored<br>Use: Teaches you how to make a Reinforced Mining Bag.<br>\
<br>\
<span class=\"myGreen\">Reinforced Mining Bag</span>\
<br>Binds when equipped<br>28 Slot Mining Bag<br><br>Requires Heavy Knothide Leather (6), Primal Earth (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternReinforcedMiningBag; ++i;

var fPatternNetherfuryBoots = new RewardItem("alliance","Pattern: Netherfury Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternNetherfuryBoots.itemMoneyPrice = new Array();
fPatternNetherfuryBoots.itemMoneyPrice[2] = 120000
fPatternNetherfuryBoots.itemStats = new Array();
fPatternNetherfuryBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Netherfury Boots</span>\
<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires Kurenai - Revered<br>Use: Teaches you how to make Netherfury Boots.<br>\
<br>\
<span class=\"myBlue\">Netherfury Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Mail</span>\
<br>392 Armor<br>+36 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +3 Spell Crit Rating</span>\
<br>Requires Level 69<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fury of the Nether (0/3)</span>\
<br>Requires Leatherworking (350)<br> <span class=\"myGray\">Netherfury Belt<br> Netherfury Boots<br> Netherfury Leggings<br>\
<br>(3) Set: +20 Intellect.</span><br><br>Requires Heavy Knothide Leather (6), Crystal Infused Leather (10), Primal Water (4), Primal Mana (4), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNetherfuryBoots; ++i;

var fRecipeTransmutePrimalFireToEarth = new RewardItem("alliance","Recipe: Transmute Primal Fire to Earth","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeTransmutePrimalFireToEarth.itemMoneyPrice = new Array();
fRecipeTransmutePrimalFireToEarth.itemMoneyPrice[2] = 80000
fRecipeTransmutePrimalFireToEarth.itemStats = new Array();
fRecipeTransmutePrimalFireToEarth.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Transmute Primal Fire to Earth</span>\
<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires Kurenai - Revered<br>Use: Teaches you how to Transmute Primal Fire into Primal Earth.<br>\
<br>\
<span class=\"myGreen\">Primal Earth</span><br>\
<br>Requires Primal Fire</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmutePrimalFireToEarth; ++i;

var fKurenaiKilt = new RewardItem("alliance","Kurenai Kilt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_leather_14.jpg");
fKurenaiKilt.itemMoneyPrice = new Array();
fKurenaiKilt.itemMoneyPrice[2] = 218818
fKurenaiKilt.itemStats = new Array();
fKurenaiKilt.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Kurenai Kilt</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Leather</span>\
<br>256 Armor<br>+11 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: 2 mana per 5 sec.</span>\
<br>Durability 75 / 75<br>Requires Level 70<br>Requires Kurenai - Revered<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 44.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fKurenaiKilt; ++i;

var fBandOfElementalSpirits = new RewardItem("alliance","Band of Elemental Spirits","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fnagrand%2Fscripts%2Frewards-nagrand.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_35.gif&reason=external-or-uncollected-resource");
fBandOfElementalSpirits.itemMoneyPrice = new Array();
fBandOfElementalSpirits.itemMoneyPrice[2] = 175952
fBandOfElementalSpirits.itemStats = new Array();
fBandOfElementalSpirits.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Band of Elemental Spirits</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+15 Stamina<br>+26 Intellect<br>+15 Spirit<br>Requires Level 70<br>Requires Kurenai - Revered</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfElementalSpirits; ++i;

var fFarSeersHelm = new RewardItem("alliance","Far Seer's Helm","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_04.jpg");
fFarSeersHelm.itemMoneyPrice = new Array();
fFarSeersHelm.itemMoneyPrice[3] = 207131
fFarSeersHelm.itemStats = new Array();
fFarSeersHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Far Seer's Helm</span>\
<br>Binds when picked up<br>Unique<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+37 Stamina<br>+25 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFarSeersHelm; ++i;

var fArechronsGift = new RewardItem("alliance","Arechron's Gift","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fnagrand%2Fscripts%2Frewards-nagrand.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mace_45.gif&reason=external-or-uncollected-resource");
fArechronsGift.itemMoneyPrice = new Array();
fArechronsGift.itemMoneyPrice[3] = 524392
fArechronsGift.itemStats = new Array();
fArechronsGift.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Arechron's Gift</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>261 - 392 Damage<span class=\"myRight\">Speed 3.50</span>\
<br>(93.3 damage per second)<br>Durability 100 / 100<br>Requires Level 70<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 42.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 84.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fArechronsGift; ++i;

var fCloakOfTheAncientSpirits = new RewardItem("alliance","Cloak of the Ancient Spirits","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fnagrand%2Fscripts%2Frewards-nagrand.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Cape_19.gif&reason=external-or-uncollected-resource");
fCloakOfTheAncientSpirits.itemMoneyPrice = new Array();
fCloakOfTheAncientSpirits.itemMoneyPrice[3] = 130314
fCloakOfTheAncientSpirits.itemStats = new Array();
fCloakOfTheAncientSpirits.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Cloak of the Ancient Spirits</span>\
<br>Binds when picked up<br>Unique<br>Back<br>78 Armor<br>+15 Stamina<br>+26 Intellect<br>Requires Level 70<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCloakOfTheAncientSpirits; ++i;

var fReinsOfTheCobaltRidingTalbuk = new RewardItem("alliance","Reins of the Cobalt Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheCobaltRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheCobaltRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheCobaltRidingTalbuk.itemStats = new Array();
fReinsOfTheCobaltRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Cobalt Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Cobalt Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheCobaltRidingTalbuk; ++i;

var fReinsOfTheSilverRidingTalbuk = new RewardItem("alliance","Reins of the Silver Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheSilverRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheSilverRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheSilverRidingTalbuk.itemStats = new Array();
fReinsOfTheSilverRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Silver Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Silver Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheSilverRidingTalbuk; ++i;

var fReinsOfTheTanRidingTalbuk = new RewardItem("alliance","Reins of the Tan Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheTanRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheTanRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheTanRidingTalbuk.itemStats = new Array();
fReinsOfTheTanRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Tan Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Tan Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheTanRidingTalbuk; ++i;

var fReinsOfTheWhiteRidingTalbuk = new RewardItem("alliance","Reins of the White Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheWhiteRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheWhiteRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheWhiteRidingTalbuk.itemStats = new Array();
fReinsOfTheWhiteRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the White Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable White Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheWhiteRidingTalbuk; ++i;

var fReinsOfTheCobaltWarTalbuk = new RewardItem("alliance","Reins of the Cobalt War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheCobaltWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheCobaltWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheCobaltWarTalbuk.itemStats = new Array();
fReinsOfTheCobaltWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Cobalt War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Cobalt War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheCobaltWarTalbuk; ++i;

var fReinsOfTheSilverWarTalbuk = new RewardItem("alliance","Reins of the Silver War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheSilverWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheSilverWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheSilverWarTalbuk.itemStats = new Array();
fReinsOfTheSilverWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Silver War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Silver War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheSilverWarTalbuk; ++i;

var fReinsOfTheTanWarTalbuk = new RewardItem("alliance","Reins of the Tan War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheTanWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheTanWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheTanWarTalbuk.itemStats = new Array();
fReinsOfTheTanWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Tan War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Tan War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheTanWarTalbuk; ++i;

var fReinsOfTheWhiteWarTalbuk = new RewardItem("alliance","Reins of the White War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheWhiteWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheWhiteWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheWhiteWarTalbuk.itemStats = new Array();
fReinsOfTheWhiteWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the White War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires Kurenai - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable White War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheWhiteWarTalbuk; ++i;

var fKurenaiTabard = new RewardItem("alliance","Kurenai Tabard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fnagrand%2Fscripts%2Frewards-nagrand.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Falteracvalley%2Fstormpikebattletabard.gif&reason=external-or-uncollected-resource");
fKurenaiTabard.itemMoneyPrice = new Array();
fKurenaiTabard.itemMoneyPrice[3] = 10000
fKurenaiTabard.itemStats = new Array();
fKurenaiTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Kurenai Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires Kurenai - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fKurenaiTabard; ++i;



//-------------------------------------------------------------------
//---Horde below

var fPatternNetherfuryBelt = new RewardItem("horde","Pattern: Netherfury Belt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternNetherfuryBelt.itemMoneyPrice = new Array();
fPatternNetherfuryBelt.itemMoneyPrice[0] = 120000
fPatternNetherfuryBelt.itemStats = new Array();
fPatternNetherfuryBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Netherfury Belt</span>\
<br>Binds when picked up<br>Requires Leatherworking (340)<br>Requires The Mag'har - Friendly<br>Use: Teaches you how to make a Netherfury Belt.<br>\
<br>\
<span class=\"myBlue\">Netherfury Belt</span>\
<br>Binds when equipped<br>Waist<span class=\"myRight\">Mail</span>\
<br>339 Armor<br>+27 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +3 Spell Crit Rating</span>\
<br>Requires Level 67<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 9 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fury of the Nether (0/3)</span>\
<br>Requires Leatherworking (350)<br><br> <span class=\"myGray\">Netherfury Belt<br> Netherfury Boots<br> Netherfury Leggings<br></span>\
<br><span class=\"myGray\">(3) Set: +20 Intellect.</span><br><br>Requires Heavy Knothide Leather (4), Crystal Infused Leather (8), Primal Water (3), Primal Mana (3), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNetherfuryBelt; ++i;

var fPatternNetherfuryLeggings = new RewardItem("horde","Pattern: Netherfury Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternNetherfuryLeggings.itemMoneyPrice = new Array();
fPatternNetherfuryLeggings.itemMoneyPrice[1] = 120000
fPatternNetherfuryLeggings.itemStats = new Array();
fPatternNetherfuryLeggings.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Netherfury Leggings</span>\
<br>Binds when picked up<br>Requires Leatherworking (340)<br>Requires The Mag'har - Honored<br>Use: Teaches you how to make Netherfury Leggings.<br>\
<br>\
<span class=\"myBlue\">Netherfury Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Mail</span>\
<br>527 Armor<br>+37 Stamina<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Spell Crit Rating</span>\
<br>Requires Level 67<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 10 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fury of the Nether (0/3)</span>\
<br>Requires Leatherworking (350)<br> <span class=\"myGray\"> Netherfury Belt<br> Netherfury Boots<br> Netherfury Leggings<br>\
<br>(3) Set: +20 Intellect.</span><br><br>Requires Heavy Knothide Leather (8), Crystal Infused Leather (12), Primal Water (5), Primal Mana (5), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNetherfuryLeggings; ++i;

var fPatternNetherfuryBoots = new RewardItem("horde","Pattern: Netherfury Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternNetherfuryBoots.itemMoneyPrice = new Array();
fPatternNetherfuryBoots.itemMoneyPrice[2] = 120000
fPatternNetherfuryBoots.itemStats = new Array();
fPatternNetherfuryBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Netherfury Boots</span>\
<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Mag'har - Revered<br>Use: Teaches you how to make Netherfury Boots.<br>\
<br>\
<span class=\"myBlue\">Netherfury Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Mail</span>\
<br>392 Armor<br>+36 Stamina<span class=\"myBlueGem\">Blue Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +3 Spell Crit Rating</span>\
<br>Requires Level 69<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 7 mana per 5 sec.</span>\
<br>\
<br>\
<span class=\"myYellow\">Fury of the Nether (0/3)</span>\
<br>Requires Leatherworking (350)<br> <span class=\"myGray\">Netherfury Belt<br> Netherfury Boots<br> Netherfury Leggings<br>\
<br>(3) Set: +20 Intellect.</span><br><br>Requires Heavy Knothide Leather (6), Crystal Infused Leather (10), Primal Water (4), Primal Mana (4), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNetherfuryBoots; ++i;

var fPatternReinforcedMiningBag = new RewardItem("horde","Pattern: Reinforced Mining Bag","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternReinforcedMiningBag.itemMoneyPrice = new Array();
fPatternReinforcedMiningBag.itemMoneyPrice[1] = 50000
fPatternReinforcedMiningBag.itemStats = new Array();
fPatternReinforcedMiningBag.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Reinforced Mining Bag<br>Binds when picked up<br>Requires Leatherworking (325)<br>Requires The Mag'har - Honored<br>Use: Teaches you how to make a Reinforced Mining Bag.<br>\
<br>\
<span class=\"myGreen\">Reinforced Mining Bag</span>\
<br>Binds when equipped<br>28 Slot Mining Bag<br><br>Requires Heavy Knothide Leather (6), Primal Earth (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternReinforcedMiningBag; ++i;



var fRecipeTransmutePrimalFireToEarth = new RewardItem("horde","Recipe: Transmute Primal Fire to Earth","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeTransmutePrimalFireToEarth.itemMoneyPrice = new Array();
fRecipeTransmutePrimalFireToEarth.itemMoneyPrice[2] = 80000
fRecipeTransmutePrimalFireToEarth.itemStats = new Array();
fRecipeTransmutePrimalFireToEarth.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Transmute Primal Fire to Earth</span>\
<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires The Mag'har - Revered<br>Use: Teaches you how to Transmute Primal Fire into Primal Earth.<br>\
<br>\
<span class=\"myGreen\">Primal Earth</span><br>\
<br>Requires Primal Fire</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmutePrimalFireToEarth; ++i;

var fTempestLeggings = new RewardItem("horde","Tempest Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_pants_leather_14.jpg");
fTempestLeggings.itemMoneyPrice = new Array();
fTempestLeggings.itemMoneyPrice[2] = 218004
fTempestLeggings.itemStats = new Array();
fTempestLeggings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Tempest Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Leather</span>\
<br>256 Armor<br>+11 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: 2 mana per 5 sec.</span>\
<br>Durability 75 / 75<br>Requires Level 70<br>Requires The Mag'har - Revered<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 18.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 44.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTempestLeggings; ++i;

var fBandOfAncestralSpirits = new RewardItem("horde","Band of Ancestral Spirits","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fnagrand%2Fscripts%2Frewards-nagrand.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_15.gif&reason=external-or-uncollected-resource");
fBandOfAncestralSpirits.itemMoneyPrice = new Array();
fBandOfAncestralSpirits.itemMoneyPrice[2] = 175952
fBandOfAncestralSpirits.itemStats = new Array();
fBandOfAncestralSpirits.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Band of Ancestral Spirits</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+15 Stamina<br>+26 Intellect<br>+15 Spirit<br>Requires Level 70<br>Requires The Mag'har - Revered</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fBandOfAncestralSpirits; ++i;

var fTalbukHideSpaulders = new RewardItem("horde","Talbuk Hide Spaulders","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fnagrand%2Fscripts%2Frewards-nagrand.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Shoulder_07.gif&reason=external-or-uncollected-resource");
fTalbukHideSpaulders.itemMoneyPrice = new Array();
fTalbukHideSpaulders.itemMoneyPrice[2] = 167132
fTalbukHideSpaulders.itemStats = new Array();
fTalbukHideSpaulders.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Talbuk Hide Spaulders</span>\
<br>Binds when picked up<br>Unique<br>Shoulder<span class=\"myRight\">Leather</span>\
<br>219 Armor<br>+20 Agility<br>Durability 60 / 60<br>Requires Level 70<br>Requires The Mag'har - Revered<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 15.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 70.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTalbukHideSpaulders; ++i;

var fEarthcallersHeaddress = new RewardItem("horde","Earthcaller's Headdress","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_17.jpg");
fEarthcallersHeaddress.itemMoneyPrice = new Array();
fEarthcallersHeaddress.itemMoneyPrice[3] = 206398
fEarthcallersHeaddress.itemStats = new Array();
fEarthcallersHeaddress.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Earthcaller's Headdress</span>\
<br>Binds when picked up<br>Unique<br>Head<span class=\"myRight\">Mail</span>\
<br>530 Armor<br>+37 Stamina<br>+25 Intellect<span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Critical Strike Rating</span>\
<br>Durability 70 / 70<br>Requires Level 70<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Equip: Increases attack power by 50.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fEarthcallersHeaddress; ++i;

var fHellscreamsWill = new RewardItem("horde","Hellscream's Will","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_axe_44.jpg");
fHellscreamsWill.itemMoneyPrice = new Array();
fHellscreamsWill.itemMoneyPrice[3] = 522358
fHellscreamsWill.itemStats = new Array();
fHellscreamsWill.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Hellscream's Will</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Axe</span>\
<br>261 - 392 Damage<span class=\"myRight\">Speed 3.50</span>\
<br>(93.3 damage per second)<br>Durability 100 / 100<br>Requires Level 70<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 42.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 84.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fHellscreamsWill; ++i;

var fCeremonialCover = new RewardItem("horde","Ceremonial Cover","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_cape_06.jpg");
fCeremonialCover.itemMoneyPrice = new Array();
fCeremonialCover.itemMoneyPrice[3] = 126329
fCeremonialCover.itemStats = new Array();
fCeremonialCover.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Ceremonial Cover</span>\
<br>Binds when picked up<br>Unique<br>Back<br>78 Armor<br>+15 Stamina<br>+26 Intellect<br>Requires Level 70<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCeremonialCover; ++i;

var fReinsOfTheCobaltRidingTalbuk = new RewardItem("horde","Reins of the Cobalt Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheCobaltRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheCobaltRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheCobaltRidingTalbuk.itemStats = new Array();
fReinsOfTheCobaltRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Cobalt Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Cobalt Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheCobaltRidingTalbuk; ++i;

var fReinsOfTheSilverRidingTalbuk = new RewardItem("horde","Reins of the Silver Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheSilverRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheSilverRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheSilverRidingTalbuk.itemStats = new Array();
fReinsOfTheSilverRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Silver Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Silver Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheSilverRidingTalbuk; ++i;

var fReinsOfTheTanRidingTalbuk = new RewardItem("horde","Reins of the Tan Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheTanRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheTanRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheTanRidingTalbuk.itemStats = new Array();
fReinsOfTheTanRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Tan Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Tan Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheTanRidingTalbuk; ++i;

var fReinsOfTheWhiteRidingTalbuk = new RewardItem("horde","Reins of the White Riding Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheWhiteRidingTalbuk.itemMoneyPrice = new Array();
fReinsOfTheWhiteRidingTalbuk.itemMoneyPrice[3] = 700000
fReinsOfTheWhiteRidingTalbuk.itemStats = new Array();
fReinsOfTheWhiteRidingTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the White Riding Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable White Riding Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheWhiteRidingTalbuk; ++i;

var fReinsOfTheCobaltWarTalbuk = new RewardItem("horde","Reins of the Cobalt War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheCobaltWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheCobaltWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheCobaltWarTalbuk.itemStats = new Array();
fReinsOfTheCobaltWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Cobalt War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Cobalt War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheCobaltWarTalbuk; ++i;

var fReinsOfTheSilverWarTalbuk = new RewardItem("horde","Reins of the Silver War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheSilverWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheSilverWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheSilverWarTalbuk.itemStats = new Array();
fReinsOfTheSilverWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Silver War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Silver War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheSilverWarTalbuk; ++i;

var fReinsOfTheTanWarTalbuk = new RewardItem("horde","Reins of the Tan War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheTanWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheTanWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheTanWarTalbuk.itemStats = new Array();
fReinsOfTheTanWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the Tan War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable Tan War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheTanWarTalbuk; ++i;

var fReinsOfTheWhiteWarTalbuk = new RewardItem("horde","Reins of the White War Talbuk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_foot_centaur.jpg");
fReinsOfTheWhiteWarTalbuk.itemMoneyPrice = new Array();
fReinsOfTheWhiteWarTalbuk.itemMoneyPrice[3] = 1000000
fReinsOfTheWhiteWarTalbuk.itemStats = new Array();
fReinsOfTheWhiteWarTalbuk.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Reins of the White War Talbuk</span>\
<br>Binds when picked up<br>Requires Level 60<br>Requires Riding (150)<br>Requires The Mag'har - Exalted<br>\
<span class=\"myGreen\">Use: Summons and dismisses a rideable White War Talbuk.  This is a very fast mount.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReinsOfTheWhiteWarTalbuk; ++i;

var fKurenaiTabard = new RewardItem("horde","Mag'har Tabard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fnagrand%2Fscripts%2Frewards-nagrand.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Falteracvalley%2Fstormpikebattletabard.gif&reason=external-or-uncollected-resource");
fKurenaiTabard.itemMoneyPrice = new Array();
fKurenaiTabard.itemMoneyPrice[3] = 10000
fKurenaiTabard.itemStats = new Array();
fKurenaiTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Kurenai Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires The Mag'har - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fKurenaiTabard; ++i;

//-------------------------------------------------------------------
//---Horde below




//------END REWARDS DEFINITION------
