/* --------- Faction Lore ------------- */
loreTexts["alliance"] = "<h3>The Aldor</h3>Shattrath was once the draenei capital of Draenor. Its name means \"dwelling of light.\" When the Burning Legion turned the orcs against the draenei, the fiercest battle was fought there. The draenei fought tooth and nail, but in the end, the city fell. The city was left in ruins and darkness until the Sha'tar arrived. The Sha'tar, whose name means \"born from light\", are the naaru who came to Outland to fight the demons of the Burning Legion. The naaru were drawn to the ruins of Shattrath City, where a small remnant of the draenei priesthood conducted its rites inside a ruined temple. The priesthood, known as the Aldor, quickly regained its strength as word of the Sha'tar's arrival spread. Reconstruction of Shattrath was soon underway.<br /><br />\
It wouldn't be long, however, before the city came under attack once again...";
loreTexts["horde"] = "<h3>The Scryers</h3>This time, the attack came from the armies of Illidan Stormrage. A large regiment of blood elves had been sent by Illidan's ally, Prince Kael'thas Sunstrider, to lay waste to the city. As the regiment of blood elves crossed the bridge, the Aldor's exarchs and vindicators lined up to defend the Terrace of Light. Then the unexpected happened: the blood elves laid down their weapons in front of the city's defenders. Their leader, a blood elf elder known as Voren'thal, stormed into the Terrace of Light and demanded to speak to the naaru A'dal. As the naaru approached him, Voren'thal knelt and uttered the following words: \"I've seen you in a vision, naaru. My race's only hope for survival lies with you. My followers and I are here to serve you.\"<br /><br />\
The defection of Voren'thal and his followers was the largest loss ever incurred by Kael'thas' forces. Nor were these just any blood elves. Many of the best and brightest amongst Kael'thas' scholars and magisters had been swayed by Voren'thal's influence. The naaru accepted the defectors, who became known as the Scryers.";

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

tokenIcons = new Array("aldortoken","scryertoken","nether","warsong");
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

var fInscriptionOfDiscipline = new RewardItem("alliance","Inscription of Discipline","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_SealOfWisdom.gif&reason=external-or-uncollected-resource");
fInscriptionOfDiscipline.itemTokenPrice = new Array();
fInscriptionOfDiscipline.itemTokenPrice[1] = new Array(2,0,0,0);
fInscriptionOfDiscipline.itemStats = new Array();
fInscriptionOfDiscipline.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of Discipline</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Aldor - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds up to 15 spell damage and healing to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfDiscipline; ++i;

var fInscriptionOfFaith = new RewardItem("alliance","Inscription of Faith","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_SealOfSalvation.gif&reason=external-or-uncollected-resource");
fInscriptionOfFaith.itemTokenPrice = new Array();
fInscriptionOfFaith.itemTokenPrice[1] = new Array(2,0,0,0);
fInscriptionOfFaith.itemStats = new Array();
fInscriptionOfFaith.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of Faith</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Aldor - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 29 healing to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfFaith; ++i;

var fInscriptionOfVengeance = new RewardItem("alliance","Inscription of Vengeance","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_FistOfJustice.gif&reason=external-or-uncollected-resource");
fInscriptionOfVengeance.itemTokenPrice = new Array();
fInscriptionOfVengeance.itemTokenPrice[1] = new Array(2,0,0,0);
fInscriptionOfVengeance.itemStats = new Array();
fInscriptionOfVengeance.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of Vengeance</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Aldor - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 26 attack power to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfVengeance; ++i;

var fInscriptionOfWarding = new RewardItem("alliance","Inscription of Warding","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_GreaterBlessing.gif&reason=external-or-uncollected-resource");
fInscriptionOfWarding.itemTokenPrice = new Array();
fInscriptionOfWarding.itemTokenPrice[1] = new Array(2,0,0,0);
fInscriptionOfWarding.itemStats = new Array();
fInscriptionOfWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of Warding</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Aldor - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 13 dodge rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfWarding; ++i;

var fGreaterInscriptionOfDiscipline = new RewardItem("alliance","Greater Inscription of Discipline","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_SealOfWisdom.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfDiscipline.itemTokenPrice = new Array();
fGreaterInscriptionOfDiscipline.itemTokenPrice[3] = new Array(8,0,0,0);
fGreaterInscriptionOfDiscipline.itemStats = new Array();
fGreaterInscriptionOfDiscipline.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of Discipline</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Aldor - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds up to 18 spell damage and healing and 10 spell critical strike rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfDiscipline; ++i;

var fGreaterInscriptionOfFaith = new RewardItem("alliance","Greater Inscription of Faith","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_GreaterBlessingo.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfFaith.itemTokenPrice = new Array();
fGreaterInscriptionOfFaith.itemTokenPrice[3] = new Array(8,0,0,0);
fGreaterInscriptionOfFaith.itemStats = new Array();
fGreaterInscriptionOfFaith.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of Faith</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Aldor - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds up to 33 healing and 4 mana per 5 sec. to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfFaith; ++i;

var fGreaterInscriptionOfVengeance = new RewardItem("alliance","Greater Inscription of Vengeance","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_GreaterBofKings.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfVengeance.itemTokenPrice = new Array();
fGreaterInscriptionOfVengeance.itemTokenPrice[3] = new Array(8,0,0,0);
fGreaterInscriptionOfVengeance.itemStats = new Array();
fGreaterInscriptionOfVengeance.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of Vengeance</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Aldor - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds 30 attack power and 10 critical strike rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfVengeance; ++i;

var fGreaterInscriptionOfWarding = new RewardItem("alliance","Greater Inscription of Warding","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_BlessingOfP.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfWarding.itemTokenPrice = new Array();
fGreaterInscriptionOfWarding.itemTokenPrice[3] = new Array(8,0,0,0);
fGreaterInscriptionOfWarding.itemStats = new Array();
fGreaterInscriptionOfWarding.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of Warding</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Aldor - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds 15 dodge rating and 10 defense rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfWarding; ++i;

//-------------------------------------------------------------------
//---Horde below

var fInscriptionOfTheBlade = new RewardItem("horde","Inscription of the Blade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FAbility_DualWield.gif&reason=external-or-uncollected-resource");
fInscriptionOfTheBlade.itemTokenPrice = new Array();
fInscriptionOfTheBlade.itemTokenPrice[1] = new Array(0,2,0,0);
fInscriptionOfTheBlade.itemStats = new Array();
fInscriptionOfTheBlade.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of the Blade</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Scryers - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 13 critical strike rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfTheBlade; ++i;

var fInscriptionOfTheKnight = new RewardItem("horde","Inscription of the Knight","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_ChampionsBond.gif&reason=external-or-uncollected-resource");
fInscriptionOfTheKnight.itemTokenPrice = new Array();
fInscriptionOfTheKnight.itemTokenPrice[1] = new Array(0,2,0,0);
fInscriptionOfTheKnight.itemStats = new Array();
fInscriptionOfTheKnight.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of the Knight</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Scryers - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 13 defense rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfTheKnight; ++i;


var fInscriptionOfTheOracle = new RewardItem("horde","Inscription of the Oracle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_SpiritualGuidenc.gif&reason=external-or-uncollected-resource");
fInscriptionOfTheOracle.itemTokenPrice = new Array();
fInscriptionOfTheOracle.itemTokenPrice[1] = new Array(0,2,0,0);
fInscriptionOfTheOracle.itemStats = new Array();
fInscriptionOfTheOracle.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of the Oracle</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Scryers - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 5 mana per 5 sec. to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfTheOracle; ++i;

var fInscriptionOfTheOrb = new RewardItem("horde","Inscription of the Orb","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Orb_04.gif&reason=external-or-uncollected-resource");
fInscriptionOfTheOrb.itemTokenPrice = new Array();
fInscriptionOfTheOrb.itemTokenPrice[1] = new Array(0,2,0,0);
fInscriptionOfTheOrb.itemStats = new Array();
fInscriptionOfTheOrb.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Inscription of the Orb</span>\
<br>Binds when picked up<br>Requires Level 64<br>Requires The Scryers - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 13 spell critical strike rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fInscriptionOfTheOrb; ++i;

var fGreaterInscriptionOfTheBlade = new RewardItem("horde","Greater Inscription of the Blade","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_WeaponMastery.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfTheBlade.itemTokenPrice = new Array();
fGreaterInscriptionOfTheBlade.itemTokenPrice[3] = new Array(0,8,0,0);
fGreaterInscriptionOfTheBlade.itemStats = new Array();
fGreaterInscriptionOfTheBlade.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of the Blade</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Scryers - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds 15 critical strike rating and 20 attack power to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfTheBlade; ++i;

var fGreaterInscriptionOfTheKnight = new RewardItem("horde","Greater Inscription of the Knight","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_ChampionsGrace.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfTheKnight.itemTokenPrice = new Array();
fGreaterInscriptionOfTheKnight.itemTokenPrice[3] = new Array(0,8,0,0);
fGreaterInscriptionOfTheKnight.itemStats = new Array();
fGreaterInscriptionOfTheKnight.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of the Knight</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Scryers - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds 15 defense rating and 10 dodge rating to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfTheKnight; ++i;

var fGreaterInscriptionOfTheOracle = new RewardItem("horde","Greater Inscription of the Oracle","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FSpell_Holy_PowerInfusion.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfTheOracle.itemTokenPrice = new Array();
fGreaterInscriptionOfTheOracle.itemTokenPrice[3] = new Array(0,8,0,0);
fGreaterInscriptionOfTheOracle.itemStats = new Array();
fGreaterInscriptionOfTheOracle.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of the Oracle</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Scryers - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds 6 mana per 5 sec. and up to 22 healing to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfTheOracle; ++i;

var fGreaterInscriptionOfTheOrb = new RewardItem("horde","Greater Inscription of the Orb","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Faldorscryers%2Fscripts%2Frewards-aldor-scryers-tokens.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Orb_03.gif&reason=external-or-uncollected-resource");
fGreaterInscriptionOfTheOrb.itemTokenPrice = new Array();
fGreaterInscriptionOfTheOrb.itemTokenPrice[3] = new Array(0,8,0,0);
fGreaterInscriptionOfTheOrb.itemStats = new Array();
fGreaterInscriptionOfTheOrb.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Greater Inscription of the Orb</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires The Scryers - Exalted<br>\
<span class=\"myGreen\">Use: Permanently adds 15 spell critical strike rating and up to 12 spell damage to a shoulder slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGreaterInscriptionOfTheOrb; ++i;

//-------------------------------------------------------------------
//---Horde below




//------END REWARDS DEFINITION------
