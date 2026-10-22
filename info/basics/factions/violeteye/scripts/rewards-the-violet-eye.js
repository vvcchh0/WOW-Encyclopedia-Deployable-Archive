/* --------- Faction Lore ------------- */
loreTexts["alliance"] = "<h3>The Violet Eye</h3>\
Looming over Deadwind Pass, the eldritch tower of Karazhan casts its shadow on the lands below. From the outside, the ruined tower looks as if it was abandoned long ago. Yet those who have come face to face with true evil know that some horrors never truly disappear. The tower’s last master, the wizard Medivh, is gone, but the echoes of his evil deeds linger within the walls of Karazhan.\
<br/><br/>\
Although there seems little hope of ever lifting the shadows from these Light-forsaken lands, there are still people who will stand against the sinister presence that has taken up residence in Karazhan. The Violet Eye is a secret sect of the Kirin Tor, the ruling council of Dalaran. The Violet Eye was assigned to keep an eye on Karazhan and Medivh, in case things got out of hand. And things in Karazhan have indeed gotten out of hand. In recent years, several nobles of Darkshire ventured into Deadwind Pass to investigate the blight that had settled over the region. They entered the dark tower, but never emerged. The Violet Eye, too, sent agents into Karazhan to investigate, but none of them ever reported back. To make matters worse, the wizards of the Violet Eye have discovered what might very well be demonic emanations coming from the tower.\
<br/><br/>\
Whatever haunts the halls of Karazhan, it must be stopped at all costs. The tower was built at a powerful convergence of magical energies: only disaster could result if Karazhan fell into the hands of an enemy unencumbered by conscience or mercy. Members of the Violet Eye are keeping watch at the base of the tower, and they will gladly accept the aid of any adventurer willing to help.";

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
		if (goldPart > 0) outPutString += goldPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/gold.gif'>&nbsp;";
		if (silverPart > 0) outPutString += silverPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/silver.gif'>&nbsp;";
		if (copperPart > 0) outPutString += copperPart+"<img src='/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/basics/factions/copper.gif'>&nbsp;";
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

var fInscriptionOfEndurance = new RewardItem("alliance","Inscription of Endurance","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FAbility_Warrior_ShieldMaste.gif&reason=external-or-uncollected-resource");
fInscriptionOfEndurance.itemMoneyPrice = new Array();
fInscriptionOfEndurance.itemMoneyPrice[1] = 300000
fInscriptionOfEndurance.itemStats = new Array();
fInscriptionOfEndurance.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of Endurance</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Violet Eye - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 7 resistance to all magic schools to a shoulder slot item.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfEndurance; ++i;

var fRecipeFlaskofChromaticWonder = new RewardItem("alliance","Recipe: Flask of Chromatic Wonder","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeFlaskofChromaticWonder.itemMoneyPrice = new Array();
fRecipeFlaskofChromaticWonder.itemMoneyPrice[1] = 40000
fRecipeFlaskofChromaticWonder.itemStats = new Array();
fRecipeFlaskofChromaticWonder.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Flask of Chromatic Wonder</span>\
<br>Binds when picked up<br>Requires Alchemy (375)<br>Requires The Violet Eye - Honored<br>Use: Teaches you how to make a Flask of Chromatic Wonder.<br>\
<br>\
<span class=\"myTable\">Flask of Chromatic Wonder</span>\
<br>Requires Level 65<br>\
<span class=\"myGreen\">Use: Increases resistance to all schools of magic by 35 and all stats by 18 for 2 hrs. Counts as both at Battle and Guardian elixir. This effect persists through death.</span>\
<br><br>Requires Dreaming Glory (7), Netherbloom (3), Fel Lotus, Imbued Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeFlaskofChromaticWonder; ++i;

var fDesignTheFrozenEye = new RewardItem("alliance","Design: The Frozen Eye","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_05.gif&reason=external-or-uncollected-resource");
fDesignTheFrozenEye.itemMoneyPrice = new Array();
fDesignTheFrozenEye.itemMoneyPrice[1] = 120000
fDesignTheFrozenEye.itemStats = new Array();
fDesignTheFrozenEye.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Design: The Frozen Eye</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (375)<br>Requires The Violet Eye - Honored<br>Use: Teaches you how to craft The Frozen Eye.<br>\
<br>\
<span class=\"myPurple\">The Frozen Eye</span>\
<br>Binds when equipped<br>Unique-Equipped<br>Finger<br>+12 Stamina<br>+35 Frost Resistance<br>Requires Level 70<br>\
<br>Requires Mercurial Adamantite (4), Khorium Bar (2), Primal Water (6), Primal Fire (6)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignTheFrozenEye; ++i;

var fPlansIceguardBreastplate = new RewardItem("alliance","Plans: Iceguard Breastplate","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_04.gif&reason=external-or-uncollected-resource");
fPlansIceguardBreastplate.itemMoneyPrice = new Array();
fPlansIceguardBreastplate.itemMoneyPrice[1] = 240000
fPlansIceguardBreastplate.itemStats = new Array();
fPlansIceguardBreastplate.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Plans: Iceguard Breastplate</span>\
<br>Binds when picked up<br>Requires Blacksmithing (375)<br>Requires The Violet Eye - Honored<br>Use: Teaches you how to make an Iceguard Breastplate.<br>\
<br>\
<span class=\"myPurple\">Iceguard Breastplate</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Plate</span>\
<br>1450 Armor<br>+49 Stamina<br>+60 Frost Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 10.</span>\
<br>\
<br>Requires Khorium Bar (8), Primal Water (12), Primal Fire (12), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansIceguardBreastplate; ++i;

var fPlansIceguardHelm = new RewardItem("alliance","Plans: Iceguard Helm","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_04.gif&reason=external-or-uncollected-resource");
fPlansIceguardHelm.itemMoneyPrice = new Array();
fPlansIceguardHelm.itemMoneyPrice[1] = 240000
fPlansIceguardHelm.itemStats = new Array();
fPlansIceguardHelm.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Plans: Iceguard Helm</span>\
<br>Binds when picked up<br>Requires Blacksmithing (375)<br>Requires The Violet Eye - Honored<br>Use: Teaches you how to make an Iceguard Helm.<br>\
<br>\
<span class=\"myPurple\">Iceguard Helm</span>\
<br>Binds when equipped<br>Head<span class=\"myRight\">Plate</span>\
<br>1030 Armor<br>+64 Stamina<br>+50 Frost Resistance<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 20.</span>\
<br>\
<br>Requires Khorium Bar (8), Primal Water (12), Primal Fire (12), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansIceguardHelm; ++i;


var fPlansIceguardLeggings = new RewardItem("alliance","Plans: Iceguard Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_04.gif&reason=external-or-uncollected-resource");
fPlansIceguardLeggings.itemMoneyPrice = new Array();
fPlansIceguardLeggings.itemMoneyPrice[2] = 240000
fPlansIceguardLeggings.itemStats = new Array();
fPlansIceguardLeggings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Plans: Iceguard Leggings</span>\
<br>Binds when picked up<br>Requires Blacksmithing (375)<br>Requires The Violet Eye - Revered<br>Use: Teaches you how to make Iceguard Leggings.<br>\
<br>\
<span class=\"myPurple\">Iceguard Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Plate</span>\
<br>1110 Armor<br>+55 Stamina<br>+60 Frost Resistance<br>Requires Level 70<br>\
<br>Requires Khorium Bar (8), Primal Water (12), Primal Fire (12), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansIceguardLeggings; ++i;

var fPatternShadowprowlersChestguard = new RewardItem("alliance","Pattern: Shadowprowler's Chestguard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Scroll_04.gif&reason=external-or-uncollected-resource");
fPatternShadowprowlersChestguard.itemMoneyPrice = new Array();
fPatternShadowprowlersChestguard.itemMoneyPrice[2] = 240000
fPatternShadowprowlersChestguard.itemStats = new Array();
fPatternShadowprowlersChestguard.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Pattern: Shadowprowler\'s Chestguard</span>\
<br>Binds when picked up<br>Requires Leatherworking (375)<br>Requires The Violet Eye - Revered<br>Use: Teaches you how to make Shadowprowler\'s Chestguard.<br>\
<br>\
<span class=\"myPurple\">Shadowprowler\'s Chestguard</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Leather</span>\
<br>333 Armor<br>+32 Strength<br>+40 Agility<br>+12 Stamina<br>\
<span class=\"myRedGem\">Red Socket</span><span class=\"myBlueGem\">Blue Socket</span><span class=\"myYellowGem\">Yellow Socket</span><span class=\"myGray\">Socket Bonus: +4 Agility</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves hit rating by 8.</span>\
<br><br>Requires Heavy Knothide Leather (10), Bolt of Soulcloth (16), Primal Earth (12), Primal Shadow (12), Primal Nether (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternShadowprowlersChestguard; ++i;

var fEnchantWeaponGreaterAgility = new RewardItem("alliance","Formula: Enchant Weapon - Greater Agility","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fvioleteye%2Fscripts%2Frewards-the-violet-eye.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Frecipe.gif&reason=external-or-uncollected-resource");
fEnchantWeaponGreaterAgility.itemMoneyPrice = new Array();
fEnchantWeaponGreaterAgility.itemMoneyPrice[3] = 30000
fEnchantWeaponGreaterAgility.itemStats = new Array();
fEnchantWeaponGreaterAgility.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myTable\">Formula: Enchant Weapon - Greater Agility</span>\
<br>Binds when picked up<br>Requires Enchanting (375)<br>Requires The Violet Eye - Exalted<br><span class=\"myGreen\">Use: Teaches you how to permanently enchant a weapon to grant 20 Agility.</span><br>\
";
RewardItems[i] = fEnchantWeaponGreaterAgility; ++i;

var fPatternCloakofDarkness = new RewardItem("alliance","Pattern: Cloak of Darkness","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternCloakofDarkness.itemMoneyPrice = new Array();
fPatternCloakofDarkness.itemMoneyPrice[3] = 50000
fPatternCloakofDarkness.itemStats = new Array();
fPatternCloakofDarkness.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Cloak of Darkness</span>\
<br>Binds when picked up<br>Requires Leatherworking (375)<br>Requires The Violet Eye - Exalted<br>Use: Teaches you how to craft a Cloak of Darkness.<br>\
<br>\
<span class=\"myPurple\">Cloak of Darkness</span>\
<br>Binds when equipped<br>Back\
<br>101 Armor<br>+23 Strength<br>+25 Stamina<br>\
<span class=\"myBlueGem\">Blue Socket</span><span class=\"myGray\">Socket Bonus: +2 Critical Strike Rating</span>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Improves melee critical strike rating by 24.</span>\
<br><br>Requires Heavy Knothide Leather (8), Bolt of Soulcloth (12), Primal Shadow (12), Primal Nether (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternCloakofDarkness; ++i;


//-------------------------------------------------------------------
//---Horde below







//------END REWARDS DEFINITION------
