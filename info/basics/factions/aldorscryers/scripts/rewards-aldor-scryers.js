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

var fDesignGleamingGoldenDraenite = new RewardItem("alliance","Design: Gleaming Golden Draenite","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignGleamingGoldenDraenite.itemMoneyPrice = new Array();
fDesignGleamingGoldenDraenite.itemMoneyPrice[0] = 50000
fDesignGleamingGoldenDraenite.itemStats = new Array();
fDesignGleamingGoldenDraenite.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Gleaming Golden Draenite</span>\
<br>Requires Jewelcrafting (305)<br>Requires The Aldor - Friendly<br>Use: Teaches you how to cut a Gleaming Golden Draenite.<br>\
<br>\
<span class=\"myGreen\">Gleaming Golden Draenite</span>\
<br>+6 Spell Critical Rating<br>\
<span class=\"myYellow\">\"Matches a Yellow Socket.\"</span>\
<br>\
<br>Requires Golden Draenite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignGleamingGoldenDraenite; ++i;

var fPatternFlameheartBracers = new RewardItem("alliance","Pattern: Flameheart Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternFlameheartBracers.itemMoneyPrice = new Array();
fPatternFlameheartBracers.itemMoneyPrice[0] = 60000
fPatternFlameheartBracers.itemStats = new Array();
fPatternFlameheartBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Flameheart Bracers<br>Binds when picked up<br>Requires Tailoring (350)<br>Requires The Aldor - Friendly<br>Use: Teaches you how to sew Flameheart Bracers.<br>\
<br>\
<span class=\"myBlue\">Flameheart Bracers</span>\
<br>Binds when equipped<br>Wrist<span class=\"myRight\">Cloth</span>\
<br>67 Armor<br>+12 Stamina<br>+8 Intellect<br>+30 Fire Resistance<br>Requires Level 69<br>\
<br>Requires Bolt of Netherweave (5), Primal Fire (5), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFlameheartBracers; ++i;

var fPatternBlastguardBelt = new RewardItem("alliance","Pattern: Blastguard Belt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternBlastguardBelt.itemMoneyPrice = new Array();
fPatternBlastguardBelt.itemMoneyPrice[1] = 80000
fPatternBlastguardBelt.itemStats = new Array();
fPatternBlastguardBelt.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Blastguard Belt<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Aldor - Honored<br>Use: Teaches you how to make a Blastguard Belt.<br>\
<br>\
<span class=\"myBlue\">Blastguard Belt</span>\
<br>Binds when equipped<br>Waist<span class=\"myRight\">Leather</span>\
<br>160 Armor<br>+27 Stamina<br>+30 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +8 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Fel Hide (6), Primal Fire (3), Primal Water (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternBlastguardBelt; ++i;

var fPatternFlamescaleBelt = new RewardItem("alliance","Pattern: Flamescale Belt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternFlamescaleBelt.itemMoneyPrice = new Array();
fPatternFlamescaleBelt.itemMoneyPrice[1] = 80000
fPatternFlamescaleBelt.itemStats = new Array();
fPatternFlamescaleBelt.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Flamescale Belt<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Aldor - Honored<br>Use: Teaches you how to make a Flamescale Belt.<br>\
<br>\
<span class=\"myBlue\">Flamescale Belt</span>\
<br>Binds when equipped<br>Waist<span class=\"myRight\">Mail</span>\
<br>357 Armor<br>+27 Stamina<br>+30 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +8 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Crystal Infused Leather (8), Primal Fire (3), Primal Water (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFlamescaleBelt; ++i;


var fPlansFlamebaneBracers = new RewardItem("alliance","Plans: Flamebane Bracers","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansFlamebaneBracers.itemMoneyPrice = new Array();
fPlansFlamebaneBracers.itemMoneyPrice[0] = 60000
fPlansFlamebaneBracers.itemStats = new Array();
fPlansFlamebaneBracers.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Flamebane Bracers<br>Binds when picked up<br>Requires Blacksmithing (350)<br>Requires The Aldor - Friendly<br>Use: Teaches you how to make Flamebane Bracers.<br>\
<br>\
<span class=\"myBlue\">Flamebane Bracers</span>\
<br>Binds when equipped<br>Wrist<span class=\"myRight\">Plate</span>\
<br>497 Armor<br>+15 Stamina<br>+28 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +2 Parry Rating</span>\
<br>Requires Level 69<br>\
<br>\
<span class=\"myYellow\">Shadow Guard (0/4)</span>\
<br> Flamebane Breastplate<br> Flamebane Helm<br> Flamebane Gloves<br> Flamebane Bracers<br>\
<br><span class=\"myGray\">(3) Set: Increases your parry rating by 20.</span><br>\
<br>Requires Fel Iron Bar (6), Primal Water (3), Primal Fire (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansFlamebaneBracers; ++i;

var fDesignRoyalShadowDraenite = new RewardItem("alliance","Design: Royal Shadow Draenite","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignRoyalShadowDraenite.itemMoneyPrice = new Array();
fDesignRoyalShadowDraenite.itemMoneyPrice[1] = 50000
fDesignRoyalShadowDraenite.itemStats = new Array();
fDesignRoyalShadowDraenite.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Royal Shadow Draenite</span>\
<br>Requires Jewelcrafting (305)<br>Requires The Aldor - Honored<br>Use: Teaches you how to cut a Royal Shadow Draenite.<br>\
<br>\
<span class=\"myGreen\">Royal Shadow Draenite</span>\
<br>+7 Healing Spells & +1 Mana per 5 Seconds<br>\
<span class=\"myYellow\">\"Matches a Red or Blue Socket.\"</span>\
<br>\
<br>Requires Shadow Draenite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignRoyalShadowDraenite; ++i;

var fPlansFlamebaneGloves = new RewardItem("alliance","Plans: Flamebane Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansFlamebaneGloves.itemMoneyPrice = new Array();
fPlansFlamebaneGloves.itemMoneyPrice[1] = 60000
fPlansFlamebaneGloves.itemStats = new Array();
fPlansFlamebaneGloves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Flamebane Gloves<br>Binds when picked up<br>Requires Blacksmithing (360)<br>Requires The Aldor - Honored<br>Use: Teaches you how to make Flamebane Gloves.<br>\
<br>\
<span class=\"myBlue\">Flamebane Gloves</span>\
<br>Binds when equipped<br>Hand<span class=\"myRight\">Plate</span>\
<br>722 Armor<br>+21 Stamina<br>+30 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Parry Rating</span>\
<br>Requires Level 70<br>\
<br>\
<span class=\"myYellow\">Shadow Guard (0/4)</span>\
<br> Flamebane Breastplate<br> Flamebane Helm<br> Flamebane Gloves<br> Flamebane Bracers<br>\
<br><span class=\"myGray\">(3) Set: Increases your parry rating by 20.</span><br>\
<br>Requires Fel Iron Bar (8), Primal Water (4), Primal Fire (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansFlamebaneGloves; ++i;

var fPatternFlameheartGloves = new RewardItem("alliance","Pattern: Flameheart Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternFlameheartGloves.itemMoneyPrice = new Array();
fPatternFlameheartGloves.itemMoneyPrice[1] = 80000
fPatternFlameheartGloves.itemStats = new Array();
fPatternFlameheartGloves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Flameheart Gloves<br>Binds when picked up<br>Requires Tailoring (360)<br>Requires The Aldor - Honored<br>Use: Teaches you how to sew Flameheart Gloves.<br>\
<br>\
<span class=\"myBlue\">Flameheart Gloves</span>\
<br>Binds when equipped<br>Hand<span class=\"myRight\">Cloth</span>\
<br>97 Armor<br>+15 Stamina<br>+11 Intellect<br>+40 Fire Resistance<br>Requires Level 70<br>\
<br>Requires Bolt of Netherweave (7), Primal Fire (7), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFlameheartGloves; ++i;

var fPatternSilverSpellthread = new RewardItem("alliance","Pattern: Silver Spellthread","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternSilverSpellthread.itemMoneyPrice = new Array();
fPatternSilverSpellthread.itemMoneyPrice[1] = 60000
fPatternSilverSpellthread.itemStats = new Array();
fPatternSilverSpellthread.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Silver Spellthread<br>Binds when picked up<br>Requires Tailoring (335)<br>Requires The Aldor - Honored<br>Use: Teaches you how to create Silver Spellthread.<br>\
<br>\
<span class=\"myBlue\">Silver Spellthread</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently embroids spellthread into pants increasing healing by up to 46 and stamina by 15.</span>\
<br>\
<br>Requires Rune Thread, Primal Life (5)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternSilverSpellthread; ++i;

var fPatternFlamescaleBoots = new RewardItem("alliance","Pattern: Flamescale Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternFlamescaleBoots.itemMoneyPrice = new Array();
fPatternFlamescaleBoots.itemMoneyPrice[2] = 80000
fPatternFlamescaleBoots.itemStats = new Array();
fPatternFlamescaleBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Flamescale Boots<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Aldor - Revered<br>Use: Teaches you how to make Flamescale Boots.<br>\
<br>\
<span class=\"myBlue\">Flamescale Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Mail</span>\
<br>437 Armor<br>+27 Stamina<br>+30 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Crystal Infused Leather (8), Primal Fire (3), Primal Water (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFlamescaleBoots; ++i;

var fPatternBlastguardBoots = new RewardItem("alliance","Pattern: Blastguard Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternBlastguardBoots.itemMoneyPrice = new Array();
fPatternBlastguardBoots.itemMoneyPrice[2] = 80000
fPatternBlastguardBoots.itemStats = new Array();
fPatternBlastguardBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Blastguard Boots<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Aldor - Revered<br>Use: Teaches you how to make Blastguard Boots.<br>\
<br>\
<span class=\"myBlue\">Blastguard Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Leather</span>\
<br>196 Armor<br>+27 Stamina<br>+30 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Fel Hide (8), Primal Fire (3), Primal Water (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternBlastguardBoots; ++i;

var fPlansFlamebaneBreastplate = new RewardItem("alliance","Plans: Flamebane Breastplate","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansFlamebaneBreastplate.itemMoneyPrice = new Array();
fPlansFlamebaneBreastplate.itemMoneyPrice[2] = 80000
fPlansFlamebaneBreastplate.itemStats = new Array();
fPlansFlamebaneBreastplate.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Flamebane Breastplate<br>Binds when picked up<br>Requires Blacksmithing (365)<br>Requires The Aldor - Revered<br>Use: Teaches you how to make a Flamebane Breastplate.<br>\
<br>\
<span class=\"myBlue\">Flamebane Breastplate</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+19 Stamina<br>+40 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myGray\">Socket Bonus: +4 Defense Rating</span>\
<br>Requires Level 70<br>\
<br>\
<span class=\"myYellow\">Shadow Guard (0/4)</span>\
<br> Flamebane Breastplate<br> Flamebane Helm<br> Flamebane Gloves<br> Flamebane Bracers<br>\
<br><span class=\"myGray\">(3) Set: Increases your parry rating by 20.</span><br>\
<br>Requires Fel Iron Bar (16), Primal Water (6), Primal Fire (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansFlamebaneBreastplate; ++i;

var fPatternVindicatorsArmorKit = new RewardItem("alliance","Pattern: Vindicator's Armor Kit","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternVindicatorsArmorKit.itemMoneyPrice = new Array();
fPatternVindicatorsArmorKit.itemMoneyPrice[2] = 50000
fPatternVindicatorsArmorKit.itemStats = new Array();
fPatternVindicatorsArmorKit.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Vindicator's Armor Kit<br>Binds when picked up<br>Requires Leatherworking (325)<br>Requires The Aldor - Revered<br>Use: Teaches you how to make a Vindicator's Armor Kit.<br>\
<br>Vindicator's Armor Kit<br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Permanently increase the defense rating of an item worn on the chest, legs, hands or feet by 8.  Only usable on items level 60 and above.</span>\
<br>\
<br>Requires Heavy Knothide Leather (3), Primal Earth</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternVindicatorsArmorKit; ++i;

var fAnchoritesRobes = new RewardItem("alliance","Anchorite's Robes","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Cloth_19.gif&reason=external-or-uncollected-resource");
fAnchoritesRobes.itemMoneyPrice = new Array();
fAnchoritesRobes.itemMoneyPrice[1] = 179594
fAnchoritesRobes.itemStats = new Array();
fAnchoritesRobes.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Anchorite's Robes</span>\
<br>Binds when picked up<br>Unique<br>Robe<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+16 Stamina<br>+38 Intellect<br>+18 Spirit<span class=\"myYellowGem\">Yellow Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: 2 mana per 5 sec.</span>\
<br>Durability 80 / 80<br>Requires Level 70<br>Requires The Aldor - Honored<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 29.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAnchoritesRobes; ++i;


var fAuchenaiStaff = new RewardItem("alliance","Auchenai Staff","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpvp%2Fimages%2Fhonorweapons%2Fgrandmarshalsstave.gif&reason=external-or-uncollected-resource");
fAuchenaiStaff.itemMoneyPrice = new Array();
fAuchenaiStaff.itemMoneyPrice[2] = 563267
fAuchenaiStaff.itemStats = new Array();
fAuchenaiStaff.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Auchenai Staff</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>92 - 172 Damage<span class=\"myRight\">Speed 2.10</span>\
<br>(62.8 damage per second)<br>+46 Intellect<br>Durability 100 / 100<br>Requires Level 70<br>Requires The Aldor - Revered<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 121.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAuchenaiStaff; ++i;

var fVindicatorsHauberk = new RewardItem("alliance","Vindicator's Hauberk","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Chest_Plate03.gif&reason=external-or-uncollected-resource");
fVindicatorsHauberk.itemMoneyPrice = new Array();
fVindicatorsHauberk.itemMoneyPrice[2] = 312042
fVindicatorsHauberk.itemStats = new Array();
fVindicatorsHauberk.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Vindicator's Hauberk</span>\
<br>Binds when picked up<br>Unique<br>Chest<span class=\"myRight\">Plate</span>\
<br>1164 Armor<br>+39 Stamina<br>Durability 135 / 135<br>Requires Level 70<br>Requires The Aldor - Revered<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 46.</span>\
<br>\
<span class=\"myGreen\">Increases your dodge rating by 19.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsHauberk; ++i;

var fDesignPendantOfShadowsEnd = new RewardItem("alliance","Design: Pendant of Shadow's End","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_05.gif&reason=external-or-uncollected-resource");
fDesignPendantOfShadowsEnd.itemMoneyPrice = new Array();
fDesignPendantOfShadowsEnd.itemMoneyPrice[2] = 120000
fDesignPendantOfShadowsEnd.itemStats = new Array();
fDesignPendantOfShadowsEnd.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Pendant of Shadow's End</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (360)<br>Requires The Aldor - Revered<br>Use: Teaches you how to craft a Pendant of Shadow's End.<br>\
<br>\
<span class=\"myBlue\">Pendant of Shadow's End</span>\
<br>Binds when equipped<br>Neck<br>+18 Stamina<br>+30 Shadow Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Use: Absorbs 900 to 2700 shadow damage on all nearby party members.  Lasts 5 min.<br>10 Charges</span>\
<br>\
<br>Requires Felsteel Bar (2), Primal Life (6), Primal Shadow (4), Mercurial Adamantite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignPendantOfShadowsEnd; ++i;

var fPatternFlameheartVest = new RewardItem("alliance","Pattern: Flameheart Vest","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternFlameheartVest.itemMoneyPrice = new Array();
fPatternFlameheartVest.itemMoneyPrice[3] = 100000
fPatternFlameheartVest.itemStats = new Array();
fPatternFlameheartVest.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Flameheart Vest<br>Binds when picked up<br>Requires Tailoring (370)<br>Requires The Aldor - Exalted<br>Use: Teaches you how to sew a Flameheart Vest.<br>\
<br>\
<span class=\"myBlue\">Flameheart Vest</span>\
<br>Binds when equipped<br>Unique<br>Chest<span class=\"myRight\">Cloth</span>\
<br>156 Armor<br>+30 Stamina<br>+19 Intellect<br>+50 Fire Resistance<br>Requires Level 70<br>\
<br>Requires Bolt of Netherweave (9), Primal Fire (9), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFlameheartVest; ++i;

var fPatternFlamescaleLeggings = new RewardItem("alliance","Pattern: Flamescale Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternFlamescaleLeggings.itemMoneyPrice = new Array();
fPatternFlamescaleLeggings.itemMoneyPrice[3] = 80000
fPatternFlamescaleLeggings.itemStats = new Array();
fPatternFlamescaleLeggings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Flamescale Leggings<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Aldor - Exalted<br>Use: Teaches you how to make Flamescale Leggings.<br>\
<br>\
<span class=\"myBlue\">Flamescale Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Mail</span>\
<br>556 Armor<br>+30 Stamina<br>+40 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +8 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (6), Crystal Infused Leather (12), Primal Fire (4), Primal Water (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternFlamescaleLeggings; ++i;

var fPatternBlastguardPants = new RewardItem("alliance","Pattern: Blastguard Pants","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternBlastguardPants.itemMoneyPrice = new Array();
fPatternBlastguardPants.itemMoneyPrice[3] = 80000
fPatternBlastguardPants.itemStats = new Array();
fPatternBlastguardPants.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Blastguard Pants<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Aldor - Exalted<br>Use: Teaches you how to make Blastguard Pants.<br>\
<br>\
<span class=\"myBlue\">Blastguard Pants</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+30 Stamina<br>+40 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +8 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (6), Fel Hide (10), Primal Fire (4), Primal Water (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternBlastguardPants; ++i;



var fPlansFlamebaneHelm = new RewardItem("alliance","Plans: Flamebane Helm","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansFlamebaneHelm.itemMoneyPrice = new Array();
fPlansFlamebaneHelm.itemMoneyPrice[3] = 60000
fPlansFlamebaneHelm.itemStats = new Array();
fPlansFlamebaneHelm.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Flamebane Helm<br>Binds when picked up<br>Requires Blacksmithing (355)<br>Requires The Aldor - Exalted<br>Use: Teaches you how to make a Flamebane Helm.<br>\
<br>\
<span class=\"myBlue\">Flamebane Helm</span>\
<br>Binds when equipped<br>Head<span class=\"myRight\">Plate</span>\
<br>930 Armor<br>+19 Stamina<br>+40 Fire Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myRedGem\">Red Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Hit Rating</span>\
<br>Requires Level 70<br>\
<br>\
<span class=\"myYellow\">Shadow Guard (0/4)</span>\
<br> Flamebane Breastplate<br> Flamebane Helm<br> Flamebane Gloves<br> Flamebane Bracers<br>\
<br><span class=\"myGray \">(3) Set: Increases your parry rating by 20.</span><br>\
<br>Requires Fel Iron Bar (12), Primal Water (5), Primal Fire (3)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansFlamebaneHelm; ++i;

var fPatternGoldenSpellthread = new RewardItem("alliance","Pattern: Golden Spellthread","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternGoldenSpellthread.itemMoneyPrice = new Array();
fPatternGoldenSpellthread.itemMoneyPrice[3] = 360000
fPatternGoldenSpellthread.itemStats = new Array();
fPatternGoldenSpellthread.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Golden Spellthread<br>Binds when picked up<br>Requires Tailoring (375)<br>Requires The Aldor - Exalted<br>Use: Teaches you how to create Golden Spellthread.<br>\
<br>\
<span class=\"myPurple\">Golden Spellthread</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently embroids spellthread into pants increasing healing by up to 66 and stamina by 20.</span>\
<br>\
<br>Requires Rune Thread, Primal Life (10), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternGoldenSpellthread; ++i;

var fLightwardensBand = new RewardItem("alliance","Lightwarden's Band","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_48.gif&reason=external-or-uncollected-resource");
fLightwardensBand.itemMoneyPrice = new Array();
fLightwardensBand.itemMoneyPrice[2] = 28410
fLightwardensBand.itemStats = new Array();
fLightwardensBand.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Lightwarden's Band</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+18 Agility<br>+27 Stamina<br>Requires Level 70<br>Requires The Aldor - Revered<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLightwardensBand; ++i;

var fMedallionOfTheLightbearer = new RewardItem("alliance","Medallion of the Lightbearer","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Amulet_04.gif&reason=external-or-uncollected-resource");
fMedallionOfTheLightbearer.itemMoneyPrice = new Array();
fMedallionOfTheLightbearer.itemMoneyPrice[3] = 790112
fMedallionOfTheLightbearer.itemStats = new Array();
fMedallionOfTheLightbearer.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Medallion of the Lightbearer</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+18 Stamina<br>+28 Intellect<br>Requires Level 70<br>Requires The Aldor - Exalted<br>\
<span class=\"myGreen\">Equip: Restores 6 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fMedallionOfTheLightbearer; ++i;

var fVindicatorsBrand = new RewardItem("alliance","Vindicator's Brand","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Sword_Draenei_01.gif&reason=external-or-uncollected-resource");
fVindicatorsBrand.itemMoneyPrice = new Array();
fVindicatorsBrand.itemMoneyPrice[3] = 1979818
fVindicatorsBrand.itemStats = new Array();
fVindicatorsBrand.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Vindicator's Brand</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Sword</span>\
<br>142 - 275 Damage<span class=\"myRight\">Speed 2.60</span>\
<br>(81.2 damage per second)<br>Durability 105 / 105<br>Requires Level 70<br>Requires The Aldor - Exalted<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 38.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fVindicatorsBrand; ++i;

var fAldorTabard = new RewardItem("alliance","Aldor Tabard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Falteracvalley%2Fstormpikebattletabard.gif&reason=external-or-uncollected-resource");
fAldorTabard.itemMoneyPrice = new Array();
fAldorTabard.itemMoneyPrice[3] = 10000
fAldorTabard.itemStats = new Array();
fAldorTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Aldor Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires The Aldor - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAldorTabard; ++i;




//-------------------------------------------------------------------
//---Horde below

var fDesignRunedBloodGarnet = new RewardItem("horde","Design: Runed Blood Garnet","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignRunedBloodGarnet.itemMoneyPrice = new Array();
fDesignRunedBloodGarnet.itemMoneyPrice[0] = 60000
fDesignRunedBloodGarnet.itemStats = new Array();
fDesignRunedBloodGarnet.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Runed Blood Garnet</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (315)<br>Requires The Scryers - Friendly<br>Use: Teaches you how to cut a Runed Blood Garnet.<br>\
<br>\
<span class=\"myGreen\">Runed Blood Garnet</span>\
<br>+7 Spell Damage<br>\
<span class=\"myYellow\">\"Matches a Red Socket.\"</span>\
<br>\
<br>Requires Blood Garnet</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignRunedBloodGarnet; ++i;

var fDesignDazzlingDeepPeridot = new RewardItem("horde","Design: Dazzling Deep Peridot","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_05.gif&reason=external-or-uncollected-resource");
fDesignDazzlingDeepPeridot.itemMoneyPrice = new Array();
fDesignDazzlingDeepPeridot.itemMoneyPrice[1] = 60000
fDesignDazzlingDeepPeridot.itemStats = new Array();
fDesignDazzlingDeepPeridot.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Dazzling Deep Peridot</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (325)<br>Requires The Scryers - Honored<br>Use: Teaches you how to cut a Dazzling Deep Peridot.<br>\
<br>\
<span class=\"myGreen\">Dazzling Deep Peridot</span>\
<br>+1 Mana every 5 Sec and +3 Intellect<br>\
<span class=\"myYellow\">\"Matches a Yellow or Blue Socket.\"</span>\
<br>\
<br>Requires Deep Peridot</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignDazzlingDeepPeridot; ++i;

var fPlansEnchantedAdamantiteBelt = new RewardItem("horde","Plans: Enchanted Adamantite Belt","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansEnchantedAdamantiteBelt.itemMoneyPrice = new Array();
fPlansEnchantedAdamantiteBelt.itemMoneyPrice[0] = 60000
fPlansEnchantedAdamantiteBelt.itemStats = new Array();
fPlansEnchantedAdamantiteBelt.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Enchanted Adamantite Belt<br>Binds when picked up<br>Requires Blacksmithing (355)<br>Requires The Scryers - Friendly<br>Use: Teaches you how to make an Enchanted Adamantite Belt.<br>\
<br>\
<span class=\"myBlue\">Enchanted Adamantite Belt</span>\
<br>Binds when equipped<br>Waist<span class=\"myRight\">Plate</span>\
<br>644 Armor<br>+21 Stamina<br>+30 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +3 Defense Rating</span>\
<br>Requires Level 70<br>\
<br>\
<span class=\"myYellow\">Enchanted Adamantite Armor (0/4)</span>\
<br> Enchanted Adamantite Breastplate<br> Enchanted Adamantite Leggings<br> Enchanted Adamantite Boots<br> Enchanted Adamantite Belt<br>\
<br><span class=\"myGray\">(3) Set: Increases your parry rating by 20.</span><br>\
<br>Requires Hardened Adamantite Bar (2), Arcane Dust (8), Large Prismatic Shard (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansEnchantedAdamantiteBelt; ++i;

var fPatternEnchantedFelscaleGloves = new RewardItem("horde","Pattern: Enchanted Felscale Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternEnchantedFelscaleGloves.itemMoneyPrice = new Array();
fPatternEnchantedFelscaleGloves.itemMoneyPrice[1] = 80000
fPatternEnchantedFelscaleGloves.itemStats = new Array();
fPatternEnchantedFelscaleGloves.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Enchanted Felscale Gloves<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Scryers - Honored<br>Use: Teaches you how to make Enchanted Felscale Gloves.<br>\
<br>\
<span class=\"myBlue\">Enchanted Felscale Gloves</span>\
<br>Binds when equipped<br>Hand<span class=\"myRight\">Mail</span>\
<br>397 Armor<br>+27 Stamina<br>+30 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Fel Scales (10), Primal Mana (6)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternEnchantedFelscaleGloves; ++i;

var fPatternEnchantedClefthoofBoots = new RewardItem("horde","Pattern: Enchanted Clefthoof Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternEnchantedClefthoofBoots.itemMoneyPrice = new Array();
fPatternEnchantedClefthoofBoots.itemMoneyPrice[1] = 80000
fPatternEnchantedClefthoofBoots.itemStats = new Array();
fPatternEnchantedClefthoofBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Enchanted Clefthoof Boots<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Scryers - Honored<br>Use: Teaches you how to make Enchanted Clefthoof Boots.<br>\
<br>\
<span class=\"myBlue\">Enchanted Clefthoof Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Leather</span>\
<br>196 Armor<br>+27 Stamina<br>+30 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Thick Clefthoof Leather (16), Primal Mana (6)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternEnchantedClefthoofBoots; ++i;

var fPatternMysticSpellthread = new RewardItem("horde","Pattern: Mystic Spellthread","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternMysticSpellthread.itemMoneyPrice = new Array();
fPatternMysticSpellthread.itemMoneyPrice[1] = 60000
fPatternMysticSpellthread.itemStats = new Array();
fPatternMysticSpellthread.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Mystic Spellthread<br>Binds when picked up<br>Requires Tailoring (335)<br>Requires The Scryers - Honored<br>Use: Teaches you how to create Mystic Spellthread.<br>\
<br>\
<span class=\"myBlue\">Mystic Spellthread</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently embroids spellthread into pants increasing spell damage by up to 25 and stamina by 15.</span>\
<br>\
<br>Requires Rune Thread, Primal Mana (5)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternMysticSpellthread; ++i;

var fDesignPendantOfWithering = new RewardItem("horde","Design: Pendant of Withering","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_05.gif&reason=external-or-uncollected-resource");
fDesignPendantOfWithering.itemMoneyPrice = new Array();
fDesignPendantOfWithering.itemMoneyPrice[2] = 120000
fDesignPendantOfWithering.itemStats = new Array();
fDesignPendantOfWithering.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Pendant of Withering</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (360)<br>Requires The Scryers - Revered<br>Use: Teaches you how to craft a Pendant of Withering.<br>\
<br>\
<span class=\"myBlue\">Pendant of Withering</span>\
<br>Binds when equipped<br>Neck<br>+18 Stamina<br>+30 Nature Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Use: Absorbs 900 to 2700 nature damage on all nearby party members.  Lasts 5 mins.<br>10 Charges</span>\
<br>\
<br>Requires Felsteel Bar (2), Primal Shadow (6), Primal Life (4), Mercurial Adamantite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignPendantOfWithering; ++i;

var fRecipeElixirOfMajorFirepower = new RewardItem("horde","Recipe: Elixir of Major Firepower","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeElixirOfMajorFirepower.itemMoneyPrice = new Array();
fRecipeElixirOfMajorFirepower.itemMoneyPrice[2] = 60000
fRecipeElixirOfMajorFirepower.itemStats = new Array();
fRecipeElixirOfMajorFirepower.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Elixir of Major Firepower</span>\
<br>Binds when picked up<br>Requires Alchemy (345)<br>Requires The Scryers - Revered<br>Use: Teaches you how to make an Elixir of Major Firepower.<br>\
<br>Elixir of Major Firepower<br>Requires Level 50<br>\
<span class=\"myGreen\">Use: Increases fire spell damage by up to 55 for 1 hour. Battle Elixir.</span>\
<br>\
<br>Requires Mote of Fire (2), Ancient Lichen, Imbued Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeElixirOfMajorFirepower; ++i;



var fPlansEnchantedAdamantiteBoots = new RewardItem("horde","Plans: Enchanted Adamantite Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansEnchantedAdamantiteBoots.itemMoneyPrice = new Array();
fPlansEnchantedAdamantiteBoots.itemMoneyPrice[1] = 60000
fPlansEnchantedAdamantiteBoots.itemStats = new Array();
fPlansEnchantedAdamantiteBoots.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Enchanted Adamantite Boots<br>Binds when picked up<br>Requires Blacksmithing (355)<br>Requires The Scryers - Honored<br>Use: Teaches you how to make Enchanted Adamantite Boots.<br>\
<br>\
<span class=\"myBlue\">Enchanted Adamantite Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Plate</span>\
<br>787 Armor<br>+21 Stamina<br>+30 Arcane Resistance<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +3 Dodge Rating</span>\
<br>Requires Level 70<br>\
<br>\
<span class=\"myYellow\">Enchanted Adamantite Armor (0/4)</span>\
<br> Enchanted Adamantite Breastplate<br> Enchanted Adamantite Leggings<br> Enchanted Adamantite Boots<br> Enchanted Adamantite Belt<br>\
<br>\
<span class=\"myGray\">(3) Set: Increases your parry rating by 20.</span>\
<br>\
<br>Requires Hardened Adamantite Bar (3), Arcane Dust (12), Large Prismatic Shard (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansEnchantedAdamantiteBoots; ++i;

var fPatternEnchantedFelscaleBoots = new RewardItem("horde","Pattern: Enchanted Felscale Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternEnchantedFelscaleBoots.itemMoneyPrice = new Array();
fPatternEnchantedFelscaleBoots.itemMoneyPrice[2] = 80000
fPatternEnchantedFelscaleBoots.itemStats = new Array();
fPatternEnchantedFelscaleBoots.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Enchanted Felscale Boots<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Scryers - Revered<br>Use: Teaches you how to make Enchanted Felscale Boots.<br>\
<br>\
<span class=\"myBlue\">Enchanted Felscale Boots</span>\
<br>Binds when equipped<br>Feet<span class=\"myRight\">Mail</span>\
<br>437 Armor<br>+27 Stamina<br>+30 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Fel Scales (10), Primal Mana (6)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternEnchantedFelscaleBoots; ++i;

var fPatternEnchantedClefthoofGloves = new RewardItem("horde","Pattern: Enchanted Clefthoof Gloves","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternEnchantedClefthoofGloves.itemMoneyPrice = new Array();
fPatternEnchantedClefthoofGloves.itemMoneyPrice[2] = 80000
fPatternEnchantedClefthoofGloves.itemStats = new Array();
fPatternEnchantedClefthoofGloves.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Enchanted Clefthoof Gloves<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Scryers - Revered<br>Use: Teaches you how to make Enchanted Clefthoof Gloves.<br>\
<br>\
<span class=\"myBlue\">Enchanted Clefthoof Gloves</span>\
<br>Binds when equipped<br>Hand<span class=\"myRight\">Leather</span>\
<br>178 Armor<br>+27 Stamina<br>+30 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +6 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (4), Thick Clefthoof Leather (16), Primal Mana (6)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternEnchantedClefthoofGloves; ++i;

var fPlansEnchantedAdamantiteBreastplate = new RewardItem("horde","Plans: Enchanted Adamantite Breastplate","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansEnchantedAdamantiteBreastplate.itemMoneyPrice = new Array();
fPlansEnchantedAdamantiteBreastplate.itemMoneyPrice[2] = 60000
fPlansEnchantedAdamantiteBreastplate.itemStats = new Array();
fPlansEnchantedAdamantiteBreastplate.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Enchanted Adamantite Breastplate<br>Binds when picked up<br>Requires Blacksmithing (360)<br>Requires The Scryers - Revered<br>Use: Teaches you how to make Enchanted Adamantite Breastplate.<br>\
<br>\
<span class=\"myBlue\">Enchanted Adamantite Breastplate</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Plate</span>\
<br>1154 Armor<br>+27 Stamina<br>+40 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Hit Rating</span>\
<br>Requires Level 70<br>\
<br>\
<span class=\"myYellow\">Enchanted Adamantite Armor (0/4)</span>\
<br> Enchanted Adamantite Breastplate<br> Enchanted Adamantite Leggings<br> Enchanted Adamantite Boots<br> Enchanted Adamantite Belt<br>\
<br>\
<span class=\"myGray\">(3) Set: Increases your parry rating by 20.</span>\
<br>\
<br>Requires Hardened Adamantite Bar (4), Arcane Dust (20), Large Prismatic Shard (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansEnchantedAdamantiteBreastplate; ++i;

var fGauntletsOfTheChosen = new RewardItem("horde","Gauntlets of the Chosen","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Gauntlets_26.gif&reason=external-or-uncollected-resource");
fGauntletsOfTheChosen.itemMoneyPrice = new Array();
fGauntletsOfTheChosen.itemMoneyPrice[2] = 160892
fGauntletsOfTheChosen.itemStats = new Array();
fGauntletsOfTheChosen.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Gauntlets of the Chosen</span>\
<br>Binds when picked up<br>Unique<br>Hand<span class=\"myRight\">Plate</span>\
<br>728 Armor<br>+15 Agility<br>+30 Stamina<br>Durability 45 / 45<br>Requires Level 70<br>Requires The Scryers - Revered<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGauntletsOfTheChosen; ++i;

var fRetainersLeggings = new RewardItem("horde","Retainer's Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Leather_18.gif&reason=external-or-uncollected-resource");
fRetainersLeggings.itemMoneyPrice = new Array();
fRetainersLeggings.itemMoneyPrice[2] = 226120
fRetainersLeggings.itemStats = new Array();
fRetainersLeggings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Retainer's Leggings</span>\
<br>Binds when picked up<br>Unique<br>Legs<span class=\"myRight\">Leather</span>\
<br>256 Armor<br>+28 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>Requires The Scryers - Revered<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 26.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 92.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRetainersLeggings; ++i;

var fSeersCane = new RewardItem("horde","Seer's Cane","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Staff_38.gif&reason=external-or-uncollected-resource");
fSeersCane.itemMoneyPrice = new Array();
fSeersCane.itemMoneyPrice[2] = 569315
fSeersCane.itemStats = new Array();
fSeersCane.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Seer's Cane</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>92 - 172 Damage<span class=\"myRight\">Speed 2.10</span>\
<br>(62.8 damage per second)<br>+28 Stamina<br>+46 Intellect<br>Durability 100 / 100<br>Requires Level 70<br>Requires The Scryers - Revered<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 228.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 10 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSeersCane; ++i;

var fScryersBloodgem = new RewardItem("horde","Scryer's Bloodgem","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Gem_Bloodstone_02.gif&reason=external-or-uncollected-resource");
fScryersBloodgem.itemMoneyPrice = new Array();
fScryersBloodgem.itemMoneyPrice[2] = 175952
fScryersBloodgem.itemStats = new Array();
fScryersBloodgem.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Scryer's Bloodgem</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>Requires The Scryers - Revered<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 32.</span>\
<br>\
<span class=\"myGreen\">Use: Increases spell damage by up to 150 and healing by up to 280 for 15 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fScryersBloodgem; ++i;

var fPatternMagistersArmorKit = new RewardItem("horde","Pattern: Magister's Armor Kit","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternMagistersArmorKit.itemMoneyPrice = new Array();
fPatternMagistersArmorKit.itemMoneyPrice[2] = 50000
fPatternMagistersArmorKit.itemStats = new Array();
fPatternMagistersArmorKit.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Magister's Armor Kit<br>Binds when picked up<br>Requires Leatherworking (325)<br>Requires The Scryers - Revered<br>Use: Teaches you how to make a Magister's Armor Kit.<br>\
<br>Magister's Armor Kit<br>Requires Level 55<br>\
<span class=\"myGreen\">Use: Permanently increase the mana regeneration of an item worn on the chest, legs, hands or feet by 3 mana every 5 seconds.  Only usable on items level 60 and above.</span>\
<br>\
<br>Requires Heavy Knothide Leather (3), Primal Mana</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternMagistersArmorKit; ++i;

var fPatternEnchantedFelscaleLeggings = new RewardItem("horde","Enchanted Felscale Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternEnchantedFelscaleLeggings.itemMoneyPrice = new Array();
fPatternEnchantedFelscaleLeggings.itemMoneyPrice[3] = 80000
fPatternEnchantedFelscaleLeggings.itemStats = new Array();
fPatternEnchantedFelscaleLeggings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Enchanted Felscale Leggings<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Scryers - Exalted<br>Use: Teaches you how to make Enchanted Felscale Leggings.<br>\
<br>\
<span class=\"myBlue\">Enchanted Felscale Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Mail</span>\
<br>556 Armor<br>+30 Stamina<br>+40 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +8 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (6), Fel Scales (12), Primal Mana (8)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternEnchantedFelscaleLeggings; ++i;

var fPlansEnchantedAdamantiteLeggings = new RewardItem("horde","Plans: Enchanted Adamantite Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansEnchantedAdamantiteLeggings.itemMoneyPrice = new Array();
fPlansEnchantedAdamantiteLeggings.itemMoneyPrice[3] = 80000
fPlansEnchantedAdamantiteLeggings.itemStats = new Array();
fPlansEnchantedAdamantiteLeggings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Enchanted Adamantite Leggings<br>Binds when picked up<br>Requires Blacksmithing (365)<br>Requires The Scryers - Exalted<br>Use: Teaches you how to make Enchanted Adamantite Leggings.<br>\
<br>\
<span class=\"myBlue\">Enchanted Adamantite Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Plate</span>\
<br>1019 Armor<br>+27 Stamina<br>+40 Arcane Resistance<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +4 Defense Rating</span>\
<br>Requires Level 70<br>\
<br>\
<span class=\"myYellow\">Enchanted Adamantite Armor (0/4)</span>\
<br> Enchanted Adamantite Breastplate<br> Enchanted Adamantite Leggings<br> Enchanted Adamantite Boots<br> Enchanted Adamantite Belt<br>\
<br>\
<span class=\"myGray\">(3) Set: Increases your parry rating by 20.</span>\
<br>\
<br>Requires Hardened Adamantite Bar (4), Arcane Dust (24), Large Prismatic Shard (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansEnchantedAdamantiteLeggings; ++i;

var fPatternEnchantedClefthoofLeggings = new RewardItem("horde","Pattern: Enchanted Clefthoof Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternEnchantedClefthoofLeggings.itemMoneyPrice = new Array();
fPatternEnchantedClefthoofLeggings.itemMoneyPrice[3] = 80000
fPatternEnchantedClefthoofLeggings.itemStats = new Array();
fPatternEnchantedClefthoofLeggings.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Enchanted Clefthoof Leggings<br>Binds when picked up<br>Requires Leatherworking (350)<br>Requires The Scryers - Exalted<br>Use: Teaches you how to make Enchanted Clefthoof Leggings.<br>\
<br>\
<span class=\"myBlue\">Enchanted Clefthoof Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Leather</span>\
<br>249 Armor<br>+30 Stamina<br>+40 Arcane Resistance<span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +8 Attack Power</span>\
<br>Requires Level 69<br>\
<br>Requires Heavy Knothide Leather (6), Thick Clefthoof Leather (24), Primal Mana (8)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternEnchantedClefthoofLeggings; ++i;

var fPatternRunicSpellthread = new RewardItem("horde","Pattern: Runic Spellthread","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternRunicSpellthread.itemMoneyPrice = new Array();
fPatternRunicSpellthread.itemMoneyPrice[3] = 360000
fPatternRunicSpellthread.itemStats = new Array();
fPatternRunicSpellthread.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Runic Spellthread<br>Binds when picked up<br>Requires Tailoring (375)<br>Requires The Scryers - Exalted<br>Use: Teaches you how to create Runic Spellthread.<br>\
<br>\
<span class=\"myPurple\">Runic Spellthread</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently embroids spellthread into pants increasing spell damage and healing by up to 35 and stamina by 20.</span>\
<br>\
<br>Requires Rune Thread, Primal Mana (10), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternRunicSpellthread; ++i;

var fRetainersBlade = new RewardItem("horde","Retainer's Blade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Weapon_Shortblade_29.gif&reason=external-or-uncollected-resource");
fRetainersBlade.itemMoneyPrice = new Array();
fRetainersBlade.itemMoneyPrice[3] = 1987127
fRetainersBlade.itemStats = new Array();
fRetainersBlade.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Retainer's Blade</span>\
<br>Binds when picked up<br>Unique<br>One-Hand<span class=\"myRight\">Dagger</span>\
<br>97 - 146 Damage<span class=\"myRight\">Speed 1.50</span>\
<br>(81.0 damage per second)<br>+22 Agility<br>+21 Stamina<br>Durability 75 / 75<br>Requires Level 70<br>Requires The Scryers - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRetainersBlade; ++i;

var fSeersSignet = new RewardItem("horde","Seer's Signet","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_52.gif&reason=external-or-uncollected-resource");
fSeersSignet.itemMoneyPrice = new Array();
fSeersSignet.itemMoneyPrice[3] = 790112
fSeersSignet.itemStats = new Array();
fSeersSignet.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Seer's Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+24 Stamina<br>Requires Level 70<br>Requires The Scryers - Exalted<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 12.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 34.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSeersSignet; ++i;

var fScryersTabard = new RewardItem("horde","Scryers Tabard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Falteracvalley%2Fstormpikebattletabard.gif&reason=external-or-uncollected-resource");
fScryersTabard.itemMoneyPrice = new Array();
fScryersTabard.itemMoneyPrice[3] = 10000
fScryersTabard.itemStats = new Array();
fScryersTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Scryers Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires The Scryers - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fScryersTabard; ++i;



//-------------------------------------------------------------------
//---Horde below




//------END REWARDS DEFINITION------
