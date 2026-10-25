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

var fDesignPotentFlameSpessarite = new RewardItem("alliance","Design: Potent Flame Spessarite","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fDesignPotentFlameSpessarite.itemMoneyPrice = new Array();
fDesignPotentFlameSpessarite.itemMoneyPrice[0] = 60000
fDesignPotentFlameSpessarite.itemStats = new Array();
fDesignPotentFlameSpessarite.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Design: Potent Flame Spessarite</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (325)<br>Requires Lower City - Friendly<br>Use: Teaches you how to cut a Potent Flame Spessarite.<br>\
<br>\
<span class=\"myGreen\">Potent Flame Spessarite</span>\
<br>+3 Spell Critical Rating and +4 Spell Damage <br>\
<span class=\"myYellow\">\"Matches a Yellow or Red Socket.\"</span>\
<br>Requires Flame Spessarite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignPotentFlameSpessarite; ++i;

var fPatternCloakOfArcaneEvasion = new RewardItem("alliance","Pattern: Cloak of Arcane Evasion","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternCloakOfArcaneEvasion.itemMoneyPrice = new Array();
fPatternCloakOfArcaneEvasion.itemMoneyPrice[1] = 60000
fPatternCloakOfArcaneEvasion.itemStats = new Array();
fPatternCloakOfArcaneEvasion.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Cloak of Arcane Evasion<br>Binds when picked up<br>Requires Tailoring (350)<br>Requires Lower City - Honored<br>Use: Teaches you how to sew a Cloak of Arcane Evasion.<br>\
<br>\
<span class=\"myBlue\">Cloak of Arcane Evasion</span>\
<br>Binds when equipped<br>Back<br>76 Armor<br>+12 Stamina<br>+32 Arcane Resistance<br>Requires Level 69<br><br>Requires Bolt of Imbued Netherweave (4), Primal Mana (3), Primal Life (3), Netherweb Spider Silk (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternCloakOfArcaneEvasion; ++i;

var fGlyphOfShadowWarding = new RewardItem("alliance","Glyph of Shadow Warding","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Shadow_SealOfKings.gif&reason=external-or-uncollected-resource");
fGlyphOfShadowWarding.itemMoneyPrice = new Array();
fGlyphOfShadowWarding.itemMoneyPrice[1] = 1000000
fGlyphOfShadowWarding.itemStats = new Array();
fGlyphOfShadowWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of Shadow Warding</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Lower City - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 20 Shadow resistance to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfShadowWarding; ++i;

var fDesignFelsteelBoar = new RewardItem("alliance","Design: Felsteel Boar","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fDesignFelsteelBoar.itemMoneyPrice = new Array();
fDesignFelsteelBoar.itemMoneyPrice[2] = 120000
fDesignFelsteelBoar.itemStats = new Array();
fDesignFelsteelBoar.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Felsteel Boar</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (370)<br>Requires Lower City - Revered<br>Use: Teaches you how to craft a Felsteel Boar.<br>\
<br>\
<span class=\"myBlue\">Figurine - Felsteel Boar</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases attack power by 68.</span>\
<br>\
<span class=\"myGreen\">Use: Summons the Felsteel Boar to fight for you for 30 seconds.</span>\
<br><br>Requires Felsteel Bar (8), Blood Garnet (2), Primal Earth (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignFelsteelBoar; ++i;

var fDesignPendantOfThawing = new RewardItem("alliance","Design: Pendant of Thawing","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fDesignPendantOfThawing.itemMoneyPrice = new Array();
fDesignPendantOfThawing.itemMoneyPrice[2] = 120000
fDesignPendantOfThawing.itemStats = new Array();
fDesignPendantOfThawing.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Pendant of Thawing</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (360)<br>Requires Lower City - Revered<br>Use: Teaches you how to craft a Pendant of Thawing.<br>\
<br>\
<span class=\"myBlue\">Pendant of Thawing</span>\
<br>Binds when equipped<br>Neck<br>+18 Stamina<br>+30 Frost Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Use: Absorbs 900 to 2700 frost damage on all nearby party members.  Lasts 5 min.<br>10 Charges</span>\
<br><br>Requires Felsteel Bar (2), Primal Fire (6), Primal Water (4), Mercurial Adamantite</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignPendantOfThawing; ++i;

var fRecipeElixirOfMajorShadowPower = new RewardItem("alliance","Recipe: Elixir of Major Shadow Power","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeElixirOfMajorShadowPower.itemMoneyPrice = new Array();
fRecipeElixirOfMajorShadowPower.itemMoneyPrice[2] = 80000
fRecipeElixirOfMajorShadowPower.itemStats = new Array();
fRecipeElixirOfMajorShadowPower.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Elixir of Major Shadow Power</span>\
<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires Lower City - Revered<br>Use: Teaches you how to make an Elixir of Major Shadow Power.<br>\
<br>Elixir of Major Shadow Power<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Increases shadow spell damage by up to 65 for 1 hour.</span>\
<br><br>Requires Ancient Lichen, Nightmare Vine, Imbued Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeElixirOfMajorShadowPower; ++i;

var fAuchenaiKey = new RewardItem("alliance","Auchenai Key","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Key_11.gif&reason=external-or-uncollected-resource");
fAuchenaiKey.itemMoneyPrice = new Array();
fAuchenaiKey.itemMoneyPrice[1] = 100000
fAuchenaiKey.itemStats = new Array();
fAuchenaiKey.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Auchenai Key<br>Binds when picked up<br>Unique<br>Requires Lower City - Honored<br>\
<span class=\"myYellow\">\"Unlocks access to  Heroic mode for Auchindoun dungeons.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAuchenaiKey; ++i;

var fGlyphOfTheOutcast = new RewardItem("alliance","Glyph of the Outcast","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FAbility_Rogue_MasterOfSubtl.gif&reason=external-or-uncollected-resource");
fGlyphOfTheOutcast.itemMoneyPrice = new Array();
fGlyphOfTheOutcast.itemMoneyPrice[2] = 1000000
fGlyphOfTheOutcast.itemStats = new Array();
fGlyphOfTheOutcast.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of the Outcast</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Lower City - Revered<br>\
<span class=\"myGreen\">Use: Permanently adds 17 Strength and 16 Intellect to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfTheOutcast; ++i;

var fLeggingsOfTheSkettisExile = new RewardItem("alliance","Leggings of the Skettis Exile","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Pants_Cloth_09.gif&reason=external-or-uncollected-resource");
fLeggingsOfTheSkettisExile.itemMoneyPrice = new Array();
fLeggingsOfTheSkettisExile.itemMoneyPrice[2] = 174403
fLeggingsOfTheSkettisExile.itemStats = new Array();
fLeggingsOfTheSkettisExile.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Leggings of the Skettis Exile</span>\
<br>Binds when picked up<br>Legs<span class=\"myRight\">Cloth</span>\
<br>136 Armor<br>+33 Intellect<br>+33 Spirit<br>Durability 65 / 65<br>Requires Level 70<br>Requires Lower City - Revered<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 39.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLeggingsOfTheSkettisExile; ++i;

var fSalvagersHauberk = new RewardItem("alliance","Salvager's Hauberk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_plate09.jpg");
fSalvagersHauberk.itemMoneyPrice = new Array();
fSalvagersHauberk.itemMoneyPrice[2] = 260629
fSalvagersHauberk.itemStats = new Array();
fSalvagersHauberk.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Salvager's Hauberk</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Mail</span>\
<br>652 Armor<br>+49 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>Requires Lower City - Revered<br>\
<span class=\"myGreen\">Equip: Improves critical strike rating by 33.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 66.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSalvagersHauberk; ++i;

var fLowerCityPrayerbook = new RewardItem("alliance","Lower City Prayerbook","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Book_11.gif&reason=external-or-uncollected-resource");
fLowerCityPrayerbook.itemMoneyPrice = new Array();
fLowerCityPrayerbook.itemMoneyPrice[2] = 175952
fLowerCityPrayerbook.itemStats = new Array();
fLowerCityPrayerbook.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Lower City Prayerbook</span>\
<br>Binds when picked up<br>Trinket<br>Requires Level 70<br>Requires Lower City - Revered<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 70.</span>\
<br>\
<span class=\"myGreen\">Use: Your heals each cost 22 less mana for the next 15 sec.</span>\
<br>\
<span class=\"myYellow\">\"Short prayers from a dozen different faiths are contained in this book.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLowerCityPrayerbook; ++i;

var fRecipeFlaskOfChromaticResistance = new RewardItem("alliance","Recipe: Flask of Chromatic Resistance","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeFlaskOfChromaticResistance.itemMoneyPrice = new Array();
fRecipeFlaskOfChromaticResistance.itemMoneyPrice[3] = 40000
fRecipeFlaskOfChromaticResistance.itemStats = new Array();
fRecipeFlaskOfChromaticResistance.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Flask of Chromatic Resistance</span>\
<br>Requires Alchemy (300)<br>Requires Lower City - Exalted<br>Use: Teaches you how to make a Flask of Chromatic Resistance.<br>\
<br>Flask of Chromatic Resistance<br>Requires Level 50<br>\
<span class=\"myGreen\">Use: Increases your resistance to all schools of magic by 25 for 2 hours.  You can only have the effect of one flask at a time.  This effect persists through death and stacks with all other resistance spells and items.</span>\
<br>\
<br>Requires Icecap (30), Mountain Silversage (10), Black Lotus, Crystal Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeFlaskOfChromaticResistance; ++i;

var fGavelOfUnearthedSecrets = new RewardItem("alliance","Gavel of Unearthed Secrets","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_hammer_08.jpg");
fGavelOfUnearthedSecrets.itemMoneyPrice = new Array();
fGavelOfUnearthedSecrets.itemMoneyPrice[3] = 482214
fGavelOfUnearthedSecrets.itemStats = new Array();
fGavelOfUnearthedSecrets.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Gavel of Unearthed Secrets</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Mace</span>\
<br>47 - 176 Damage<span class=\"myRight\">Speed 2.70</span>\
<br>(41.4 damage per second)<br>+22 Stamina<br>+15 Intellect<br>Durability 105 / 105<br>Requires Level 70<br>Requires Lower City - Exalted<br>\
<span class=\"myGreen\">Equip: Improves spell critical strike rating by 14.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 150.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGavelOfUnearthedSecrets; ++i;

var fShapeshiftersSignet = new RewardItem("alliance","Shapeshifter's Signet","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_41.gif&reason=external-or-uncollected-resource");
fShapeshiftersSignet.itemMoneyPrice = new Array();
fShapeshiftersSignet.itemMoneyPrice[3] = 197528
fShapeshiftersSignet.itemStats = new Array();
fShapeshiftersSignet.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Shapeshifter's Signet</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+23 Agility<br>+16 Stamina<br>Requires Level 70<br>Requires Lower City - Exalted<br>\
<span class=\"myGreen\">Equip: Increases feral combat skill rating by 20.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases dagger skill rating by 20.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fShapeshiftersSignet; ++i;

var fTridentOfTheOutcastTribe = new RewardItem("alliance","Trident of the Outcast Tribe","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Spear_04.gif&reason=external-or-uncollected-resource");
fTridentOfTheOutcastTribe.itemMoneyPrice = new Array();
fTridentOfTheOutcastTribe.itemMoneyPrice[3] = 2392799
fTridentOfTheOutcastTribe.itemStats = new Array();
fTridentOfTheOutcastTribe.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Trident of the Outcast Tribe</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Polearm</span>\
<br>262 - 394 Damage<span class=\"myRight\">Speed 3.20</span>\
<br>(102.5 damage per second)<br>+35 Strength<br>+52 Stamina<br>Durability 120 / 120<br>Requires Level 70<br>Requires Lower City - Exalted<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 35.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fTridentOfTheOutcastTribe; ++i;

var fLowerCityTabard = new RewardItem("alliance","Lower City Tabard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Flowercity%2Fscripts%2Frewards-lowercity.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Falteracvalley%2Fstormpikebattletabard.gif&reason=external-or-uncollected-resource");
fLowerCityTabard.itemMoneyPrice = new Array();
fLowerCityTabard.itemMoneyPrice[3] = 10000
fLowerCityTabard.itemStats = new Array();
fLowerCityTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Lower City Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires Lower City - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fLowerCityTabard; ++i;



//-------------------------------------------------------------------
//---Horde below







//------END REWARDS DEFINITION------
