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

var fPatternHeavyClefthoofBoots = new RewardItem("alliance","Pattern: Heavy Clefthoof Boots","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternHeavyClefthoofBoots.itemMoneyPrice = new Array();
fPatternHeavyClefthoofBoots.itemMoneyPrice[0] = 140000
fPatternHeavyClefthoofBoots.itemStats = new Array();
fPatternHeavyClefthoofBoots.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Heavy Clefthoof Boots</span>\
<br>Binds when picked up<br>Requires Leatherworking (355)<br>Requires Cenarion Expedition - Friendly<br>Use: Teaches you how to make Heavy Clefthoof Boots.<br>\
<br>\
	<span class=\"myBlue\">Heavy Clefthoof Boots</span>\
	<br>Binds when equipped<br>Feet<span class=\"myRight\">Leather</span>\
	<br>394 Armor<br>+30 Stamina<br>\
	<span class=\"myYellowGem\">Yellow Socket</span>\
	<span class=\"myBlueGem\">Blue Socket</span>\
	<span class=\"myGray\">Socket Bonus: +3 Dodge Rating</span><br>\
	Durability 50 / 50<br>Requires Level 69<br>\
	<span class=\"myGreen\">Equip: Increases defense rating by 21.</span>\
	<br>\
	<br>\
	<span class=\"myYellow\">Strength of the Clefthoof (0/3)</span>\
	<br>Requires Leatherworking (350)<br> Heavy Clefthoof Boots<br> Heavy Clefthoof Leggings<br> Heavy Clefthoof Vest<br>\
	<br>(3) Set: +20 Strength.\
<br>Requires Heavy Knothide Leather (4), Thick Clefthoof Leather (20), Primal Earth (4), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternHeavyClefthoofBoots; ++i;

var fSchematicGreenSmokeFlare = new RewardItem("alliance","Schematic: Green Smoke Flare","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fSchematicGreenSmokeFlare.itemMoneyPrice = new Array();
fSchematicGreenSmokeFlare.itemMoneyPrice[0] = 60000
fSchematicGreenSmokeFlare.itemStats = new Array();
fSchematicGreenSmokeFlare.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Schematic: Green Smoke Flare<br>Binds when picked up<br>Requires Engineering (335)<br>Requires Cenarion Expedition - Friendly<br>Use: Teaches you how to make a Green Smoke Flare.<br>\
<br>\
<b>Green Smoke Flare</b><br>\
<span class=\"myGreen\">Use: Throw a green smoke flare at a specific location that lasts for 5 min.</span>\
<br>Requires Elemental Blasting Powder, Netherweave Cloth, Green Dye</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fSchematicGreenSmokeFlare; ++i;


var fExpeditionFlare = new RewardItem("alliance","Expedition Flare","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Enchant_EssenceAstralSm.gif&reason=external-or-uncollected-resource");
fExpeditionFlare.itemMoneyPrice = new Array();
fExpeditionFlare.itemMoneyPrice[0] = 8000
fExpeditionFlare.itemStats = new Array();
fExpeditionFlare.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Expedition Flare<br>Binds when picked up<br>Requires Level 60<br>Requires Cenarion Expedition - Friendly<br>\
<span class=\"myGreen\">Use: Send a distress flare into the sky, calling for a Cenarion Expedition unit to come to your aid.  Can only be used in Zangarmarsh while outdoors.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExpeditionFlare; ++i;

var fScoutsArrow = new RewardItem("alliance","Scout's Arrow","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fscoutsarrow.gif&reason=external-or-uncollected-resource");
fScoutsArrow.itemMoneyPrice = new Array();
fScoutsArrow.itemMoneyPrice[0] = 2000
fScoutsArrow.itemStats = new Array();
fScoutsArrow.itemStats[0] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Scout's Arrow</span>\
<br>Projectile<span class=\"myRight\">Arrow</span><br>\
Adds 26.0 damage per second<br>Requires Level 61<br>Requires Cenarion Expedition - Friendly</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fScoutsArrow; ++i;

var fPatternHeavyClefthoofLeggings = new RewardItem("alliance","Pattern: Heavy Clefthoof Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternHeavyClefthoofLeggings.itemMoneyPrice = new Array();
fPatternHeavyClefthoofLeggings.itemMoneyPrice[1] = 140000
fPatternHeavyClefthoofLeggings.itemStats = new Array();
fPatternHeavyClefthoofLeggings.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Heavy Clefthoof Leggings</span>\
<br>Binds when picked up<br>Requires Leatherworking (355)<br>Requires Cenarion Expedition - Honored<br>Use: Teaches you how to make Heavy Clefthoof Leggings.<br>\
<br>\
<span class=\"myBlue\">Heavy Clefthoof Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Leather</span>\
<br>503 Armor<br>+33 Stamina<br>\
<span class=\"myBlueGem\">Blue Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span>\
<span class=\"myGray\">Socket Bonus: +4 Dodge Rating</span><br>\
Durability 75 / 75<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 29.</span>\
<br>\
<br>\
<span class=\"myYellow\">Strength of the Clefthoof (0/3)</span>\
<br>Requires Leatherworking (350)<br> Heavy Clefthoof Boots<br> Heavy Clefthoof Leggings<br> Heavy Clefthoof Vest<br>\
<br>(3) Set: +20 Strength.\
<br>Requires Heavy Knothide Leather (6), Thick Clefthoof Leather (34), Primal Earth (4), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternHeavyClefthoofLeggings; ++i;

var fPlansAdamantiteSharpeningStone = new RewardItem("alliance","Plans: Adamantite Sharpening Stone","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansAdamantiteSharpeningStone.itemMoneyPrice = new Array();
fPlansAdamantiteSharpeningStone.itemMoneyPrice[1] = 60000
fPlansAdamantiteSharpeningStone.itemStats = new Array();
fPlansAdamantiteSharpeningStone.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Adamantite Sharpening Stone<br>Binds when picked up<br>Requires Blacksmithing (350)<br>Requires Cenarion Expedition - Honored<br>Use: Teaches you how to make an Adamantite Sharpening Stone.<br>\
<br>\
<span class=\"myGreen\"><b>Adamantite Sharpening Stone</b></span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Increase sharp weapon damage by 12 and add 14 melee critical hit rating for 30 minutes.</span>\
<br>Requires Adamantite Bar, Mote of Earth (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansAdamantiteSharpeningStone; ++i;

var fPlansAdamantiteWeightstone = new RewardItem("alliance","Plans: Adamantite Weightstone","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansAdamantiteWeightstone.itemMoneyPrice = new Array();
fPlansAdamantiteWeightstone.itemMoneyPrice[1] = 60000
fPlansAdamantiteWeightstone.itemStats = new Array();
fPlansAdamantiteWeightstone.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Adamantite Weightstone<br>Binds when picked up<br>Requires Blacksmithing (350)<br>Requires Cenarion Expedition - Honored<br>Use: Teaches you how to make an Adamantite Weightstone.<br>\
<br>\
<span class=\"myGreen\"><b>Adamantite Weightstone</b></span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Increase blunt weapon damage by 12 and add 14 critical hit rating for 30 minutes.</span>\
<br>Requires Adamantite Bar, Netherweave Cloth (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansAdamantiteWeightstone; ++i;

var fRecipeTransmuteEarthstormDiamond = new RewardItem("alliance","Recipe: Transmute Earthstorm Diamond","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fRecipeTransmuteEarthstormDiamond.itemMoneyPrice = new Array();
fRecipeTransmuteEarthstormDiamond.itemMoneyPrice[1] = 80000
fRecipeTransmuteEarthstormDiamond.itemStats = new Array();
fRecipeTransmuteEarthstormDiamond.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
	<tr>\
		<td>\
			<div class=\"myTable\">\
				Recipe: Transmute Earthstorm Diamond<br>\
				Binds when picked up<br>\
				Requires Alchemy (350)<br>\
				Requires Cenarion Expedition - Honored<br>\
				Use: Teaches you how to Transmute an Earthstorm Diamond.<br>\
				<br>\
				<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
					<tr>\
						<td>\
							<span class=\"myBlue\">Earthstorm Diamond</span>\
						</td>\
					</tr>\
				</table>\
				<br>Requires Deep Peridot (3), Shadow Draenite (3), Golden Draenite (3), Primal Earth (2), Primal Water (2)\
			</div>\
		</td>\
	</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmuteEarthstormDiamond; ++i;


var fPatternClefthideLegArmor = new RewardItem("alliance","Pattern: Clefthide Leg Armor","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternClefthideLegArmor.itemMoneyPrice = new Array();
fPatternClefthideLegArmor.itemMoneyPrice[1] = 60000
fPatternClefthideLegArmor.itemStats = new Array();
fPatternClefthideLegArmor.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Clefthide Leg Armor<br>Binds when picked up<br>Requires Leatherworking (335)<br>Requires Cenarion Expedition - Honored<br>Use: Teaches you how to make Clefthide Leg Armor.<br>\
<br>\
<span class=\"myBlue\">Clefthide Leg Armor</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently attach clefthide armor onto pants to increase stamina by 30 and agility by 10.</span>\
<br>Requires Heavy Knothide Leather (4), Thick Clefthoof Leather (8), Primal Earth (4)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternClefthideLegArmor; ++i;

var fPlansGreaterRuneOfWarding = new RewardItem("alliance","Plans: Greater Rune of Warding","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPlansGreaterRuneOfWarding.itemMoneyPrice = new Array();
fPlansGreaterRuneOfWarding.itemMoneyPrice[1] = 60000
fPlansGreaterRuneOfWarding.itemStats = new Array();
fPlansGreaterRuneOfWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Plans: Greater Rune of Warding<br>Binds when picked up<br>Requires Blacksmithing (350)<br>Requires Cenarion Expedition - Honored<br>Use: Teaches you how to make a Greater Rune of Warding.<br>\
<br>\
<b>Greater Rune of Warding</b><br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Enchant a piece of chest armor so it has a 25% chance per hit of giving you 400 points of physical damage absorption. 90 sec. cooldown. Lasts for 1 hour.</span>\
<br>Requires Khorium Bar</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansGreaterRuneOfWarding; ++i;

var fPreserversCudgel = new RewardItem("alliance","Preserver's Cudgel","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Mace_11.gif&reason=external-or-uncollected-resource");
fPreserversCudgel.itemMoneyPrice = new Array();
fPreserversCudgel.itemMoneyPrice[1] = 359704
fPreserversCudgel.itemStats = new Array();
fPreserversCudgel.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Preserver's Cudgel</span>\
<br>Binds when picked up<br>Main Hand<span class=\"myRight\">Mace</span>\
<br>62 - 145 Damage<span class=\"myRight\">Speed 2.50</span>\
<br>(41.4 damage per second)<br>+16 Stamina<br>+11 Intellect<br>Durability 90 / 90<br>Requires Level 62<br>Requires Cenarion Expedition - Honored<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 105.</span>\
<br>\
<span class=\"myGreen\">Equip: Restores 5 mana per 5 sec.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPreserversCudgel; ++i;

var fRecipeEarthenElixir = new RewardItem("alliance","Recipe: Earthen Elixir","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fRecipeEarthenElixir.itemMoneyPrice = new Array();
fRecipeEarthenElixir.itemMoneyPrice[1] = 40000
fRecipeEarthenElixir.itemStats = new Array();
fRecipeEarthenElixir.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Recipe: Earthen Elixir<br>Binds when picked up<br>Requires Alchemy (320)<br>Requires Cenarion Expedition - Honored<br>Use: Teaches you how to make an Earthen Elixir.<br>\
<br>\
<b>Earthen Elixir</b><br>Requires Level 50<br>\
<span class=\"myGreen\">Use: Prevents up to 20 damage done by a physical or magical attack for 1 hour. Guardian Elixir.</span>\
<br>Requires Dreaming Glory, Ragveil (2), Imbued Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeEarthenElixir; ++i;


var fWardensHauberk = new RewardItem("alliance","Warden's Hauberk","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_chest_leather_08.jpg");
fWardensHauberk.itemMoneyPrice = new Array();
fWardensHauberk.itemMoneyPrice[1] = 181153
fWardensHauberk.itemStats = new Array();
fWardensHauberk.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Warden's Hauberk</span>\
<br>Binds when picked up<br>Chest<span class=\"myRight\">Leather</span>\
<br>238 Armor<br>+39 Agility<br>+30 Stamina<br>Durability 100 / 100<br>\
<span class=\"myRedGem\">Red Socket</span>\
<span class=\"myRedGem\">Red Socket</span>\
<span class=\"myRedGem\">Red Socket</span>\
<span class=\"myGray\">Socket Bonus: +4 Hit Rating</span><br>\
Requires Level 62<br>Requires Cenarion Expedition - Honored</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWardensHauberk; ++i;

var fExplorersWalkingStick = new RewardItem("alliance","Explorer's Walking Stick","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Staff_31.gif&reason=external-or-uncollected-resource");
fExplorersWalkingStick.itemMoneyPrice = new Array();
fExplorersWalkingStick.itemMoneyPrice[1] = 447982
fExplorersWalkingStick.itemStats = new Array();
fExplorersWalkingStick.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Explorer's Walking Stick</span>\
<br>Binds when picked up<br>Two Hand<span class=\"myRight\">Staff</span>\
<br>132 - 199 Damage<span class=\"myRight\">Speed 2.30</span>\
<br>(72.0 damage per second)<br>+51 Stamina<br>Durability 100 / 100<br>Requires Level 62<br>Requires Cenarion Expedition - Honored<br>\
<span class=\"myGreen\">Equip: Increases attack power by 68.</span>\
<br>\
<span class=\"myGreen\">Equip: Run speed increased slightly.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fExplorersWalkingStick; ++i;


var fGlyphOfNatureWarding = new RewardItem("alliance","Glyph of Nature Warding","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fglyph.gif&reason=external-or-uncollected-resource");
fGlyphOfNatureWarding.itemMoneyPrice = new Array();
fGlyphOfNatureWarding.itemMoneyPrice[1] = 1000000
fGlyphOfNatureWarding.itemStats = new Array();
fGlyphOfNatureWarding.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of Nature Warding</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Cenarion Expedition - Honored<br>\
<span class=\"myGreen\">Use: Permanently adds 20 Nature resistance to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfNatureWarding; ++i;

var fDesignNightseyePanther = new RewardItem("alliance","Design: Nightseye Panther","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fDesignNightseyePanther.itemMoneyPrice = new Array();
fDesignNightseyePanther.itemMoneyPrice[2] = 120000
fDesignNightseyePanther.itemStats = new Array();
fDesignNightseyePanther.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Design: Nightseye Panther</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (370)<br>Requires Cenarion Expedition - Revered<br>Use: Teaches you how to craft a Nightseye Panther.<br>\
<br>\
<span class=\"myBlue\">Figurine - Nightseye Panther</span>\
<br>Binds when picked up<br>Unique<br>Trinket<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases your effective stealth level by 1.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 54.</span>\
<br>\
<span class=\"myGreen\">Use: Increases attack power by 320 for 12 sec.</span>\
<br>Requires Hardened Adamantite Bar (6), Nightseye (2), Primal Shadow (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignNightseyePanther; ++i;


var fPatternHeavyClefthoofVest = new RewardItem("alliance","Pattern: Heavy Clefthoof Vest","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_05.jpg");
fPatternHeavyClefthoofVest.itemMoneyPrice = new Array();
fPatternHeavyClefthoofVest.itemMoneyPrice[1] = 160000
fPatternHeavyClefthoofVest.itemStats = new Array();
fPatternHeavyClefthoofVest.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Pattern: Heavy Clefthoof Vest</span>\
<br>Binds when picked up<br>Requires Leatherworking (360)<br>Requires Cenarion Expedition - Honored<br>Use: Teaches you how to make a Heavy Clefthoof Vest.<br>\
<br>\
<span class=\"myBlue\">Heavy Clefthoof Vest</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Leather</span>\
<br>500 Armor<br>+45 Stamina</span><br>\
<span class=\"myYellowGem\">Yellow Socket</span>\
<span class=\"myYellowGem\">Yellow Socket</span>\
<span class=\"myBlueGem\">Blue Socket</span>\
<span class=\"myGray\">Socket Bonus: +4 Dodge Rating</span><br>\
<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 24.</span>\
<br>\
<br>\
<span class=\"myYellow\">Strength of the Clefthoof (0/3)</span>\
<br>Requires Leatherworking (350)<br> Heavy Clefthoof Boots<br> Heavy Clefthoof Leggings<br> Heavy Clefthoof Vest<br>\
<br>(3) Set: +20 Strength.<br>\
<br>Requires Heavy Knothide Leather (6), Thick Clefthoof Leather (40), Primal Earth (4), Rune Thread (2)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternHeavyClefthoofVest; ++i;

var fFormulaEnchantGlovesSpellStrike = new RewardItem("alliance","Formula: Enchant Gloves - Spell Strike","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Frecipe.gif&reason=external-or-uncollected-resource");
fFormulaEnchantGlovesSpellStrike.itemMoneyPrice = new Array();
fFormulaEnchantGlovesSpellStrike.itemMoneyPrice[2] = 80000
fFormulaEnchantGlovesSpellStrike.itemStats = new Array();
fFormulaEnchantGlovesSpellStrike.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Gloves - Spell Strike</span>\
<br>Binds when picked up<br>Requires Enchanting (360)<br>Requires Cenarion Expedition - Revered<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant gloves to grant 15 spell hit rating.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantGlovesSpellStrike; ++i;


var fRecipeTransmutePrimalWaterToAir = new RewardItem("alliance","Recipe: Transmute Primal Water to Air","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeTransmutePrimalWaterToAir.itemMoneyPrice = new Array();
fRecipeTransmutePrimalWaterToAir.itemMoneyPrice[2] = 80000
fRecipeTransmutePrimalWaterToAir.itemStats = new Array();
fRecipeTransmutePrimalWaterToAir.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Transmute Primal Water to Air</span>\
<br>Binds when picked up<br>Requires Alchemy (350)<br>Requires Cenarion Expedition - Revered<br>Use: Teaches you how to Transmute Primal Water into Air.<br>\
<br>\
<span class=\"myGreen\"><b>Primal Air</b></span>\
<br>Requires Primal Water</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeTransmutePrimalWaterToAir; ++i;

var fPlansWildguardHelm = new RewardItem("alliance","Plans: Wildguard Helm","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_04.jpg");
fPlansWildguardHelm.itemMoneyPrice = new Array();
fPlansWildguardHelm.itemMoneyPrice[2] = 240000
fPlansWildguardHelm.itemStats = new Array();
fPlansWildguardHelm.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Plans: Wildguard Helm</span>\
<br>Binds when picked up<br>Requires Blacksmithing (375)<br>Requires Cenarion Expedition - Revered<br>Use: Teaches you how to make a Wildguard Helm.<br>\
<br>\
<span class=\"myPurple\">Wildguard Helm</span>\
<br>Binds when equipped<br>Head<span class=\"myRight\">Plate</span>\
<br>1178 Armor<br>+58 Stamina<br>+50 Nature Resistance<br>Durability 100 / 100<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 28.</span>\
<br>Requires Felsteel Bar (8), Primal Life (12), Primal Shadow (12), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansWildguardHelm; ++i;

var fPlansWildguardLeggings = new RewardItem("alliance","Plans: Wildguard Leggings","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_04.jpg");
fPlansWildguardLeggings.itemMoneyPrice = new Array();
fPlansWildguardLeggings.itemMoneyPrice[2] = 240000
fPlansWildguardLeggings.itemStats = new Array();
fPlansWildguardLeggings.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Plans: Wildguard Leggings</span>\
<br>Binds when picked up<br>Requires Blacksmithing (375)<br>Requires Cenarion Expedition - Revered<br>Use: Teaches you how to make Wildguard Leggings.<br>\
<br>\
<span class=\"myPurple\">Wildguard Leggings</span>\
<br>Binds when equipped<br>Legs<span class=\"myRight\">Plate</span>\
<br>1269 Armor<br>+55 Stamina<br>+60 Nature Resistance<br>Durability 120 / 120<br>Requires Level 70\
<br>Requires Felsteel Bar (8), Primal Life (12), Primal Shadow (12), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansWildguardLeggings; ++i;

var fWardensArrow = new RewardItem("alliance","Warden's Arrow","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fwardensarrow.gif&reason=external-or-uncollected-resource");
fWardensArrow.itemMoneyPrice = new Array();
fWardensArrow.itemMoneyPrice[2] = 5000
fWardensArrow.itemStats = new Array();
fWardensArrow.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Warden's Arrow</span>\
<br>Projectile<span class=\"myRight\">Arrow</span><br>Adds 37.0 damage per second<br>Requires Level 68<br>Requires Cenarion Expedition - Revered</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWardensArrow; ++i;


var fGlyphOfFerocity = new RewardItem("alliance","Glyph of Ferocity","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Fglyphofferocity.gif&reason=external-or-uncollected-resource");
fGlyphOfFerocity.itemMoneyPrice = new Array();
fGlyphOfFerocity.itemMoneyPrice[2] = 1000000
fGlyphOfFerocity.itemStats = new Array();
fGlyphOfFerocity.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Glyph of Ferocity</span>\
<br>Binds when picked up<br>Requires Level 70<br>Requires Cenarion Expedition - Revered<br>\
<span class=\"myGreen\">Use: Permanently adds 34 attack power and 16 hit rating to a head slot item. Does not stack with other enchantments for the selected equipment slot.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fGlyphOfFerocity; ++i;


var fReservoirKey = new RewardItem("alliance","Reservoir Key","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_misc_key_13.jpg");
fReservoirKey.itemMoneyPrice = new Array();
fReservoirKey.itemMoneyPrice[1] = 100000
fReservoirKey.itemStats = new Array();
fReservoirKey.itemStats[1] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Reservoir Key<br>Binds when picked up<br>Unique<br>Requires Cenarion Expedition - Honored<br>\
<span class=\"myYellow\">\"Unlocks Heroic Difficulty for Coilfang Reservoir dungeons.\"</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fReservoirKey; ++i;

var fWatchersCowl = new RewardItem("alliance","Watcher's Cowl","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_helmet_34.jpg");
fWatchersCowl.itemMoneyPrice = new Array();
fWatchersCowl.itemMoneyPrice[2] = 127371
fWatchersCowl.itemStats = new Array();
fWatchersCowl.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Watcher's Cowl</span>\
<br>Binds when picked up<br>Unique<br>Head<span class=\"myRight\">Cloth</span>\
<br>127 Armor<br>+21 Stamina<br>+36 Intellect<br>+14 Spirit<br>Durability 50 / 50<br>Requires Level 70<br>Requires Cenarion Expedition - Revered<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 79.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWatchersCowl; ++i;

var fStrengthOfTheUntamed = new RewardItem("alliance","Strength of the Untamed","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_jewelry_necklace_06.jpg");
fStrengthOfTheUntamed.itemMoneyPrice = new Array();
fStrengthOfTheUntamed.itemMoneyPrice[2] = 175952
fStrengthOfTheUntamed.itemStats = new Array();
fStrengthOfTheUntamed.itemStats[2] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myBlue\">Strength of the Untamed</span>\
<br>Binds when picked up<br>Unique<br>Neck<br>+27 Stamina<br>Requires Level 70<br>Requires Cenarion Expedition - Revered<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 19.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases your dodge rating by 18.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fStrengthOfTheUntamed; ++i;

var fRecipeMajorNatureProtectionPotion = new RewardItem("alliance","Recipe: Major Nature Protection Potion","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeMajorNatureProtectionPotion.itemMoneyPrice = new Array();
fRecipeMajorNatureProtectionPotion.itemMoneyPrice[3] = 100000
fRecipeMajorNatureProtectionPotion.itemStats = new Array();
fRecipeMajorNatureProtectionPotion.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Recipe: Major Nature Protection Potion<br>Binds when picked up<br>Requires Alchemy (360)<br>Requires Cenarion Expedition - Exalted<br>Use: Teaches you how to make a Major Nature Protection Potion.<br>\
<br>\
<b>Major Nature Protection Potion</b><br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Absorbs 2800 to 4000 nature damage.  Lasts 2 min.</span>\
<br>Requires Primal Life, Mana Thistle (3), Imbued Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeMajorNatureProtectionPotion; ++i;


var fRecipeFlaskOfDistilledWisdom = new RewardItem("alliance","Recipe: Flask of Distilled Wisdom","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_06.jpg");
fRecipeFlaskOfDistilledWisdom.itemMoneyPrice = new Array();
fRecipeFlaskOfDistilledWisdom.itemMoneyPrice[3] = 40000
fRecipeFlaskOfDistilledWisdom.itemStats = new Array();
fRecipeFlaskOfDistilledWisdom.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Recipe: Flask of Distilled Wisdom</span>\
<br>Requires Alchemy (300)<br>Use: Teaches you how to make a Flask of Distilled Wisdom.<br>\
<br>\
<b>Flask of Distilled Wisdom</b><br>Requires Level 50<br>\
<span class=\"myGreen\">Use: Increases the player's Intellect by 65 for 2 hours. Counts as both a Battle and Guardian Elixir.  This effect persists through death.</span>\
<br>Requires Dreamfoil (7), Icecap (3), Black Lotus, Crystal Vial</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fRecipeFlaskOfDistilledWisdom; ++i;

var fPlansWildguardBreastplate = new RewardItem("alliance","Plans: Wildguard Breastplate","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_04.jpg");
fPlansWildguardBreastplate.itemMoneyPrice = new Array();
fPlansWildguardBreastplate.itemMoneyPrice[3] = 240000
fPlansWildguardBreastplate.itemStats = new Array();
fPlansWildguardBreastplate.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Plans: Wildguard Breastplate</span>\
<br>Binds when picked up<br>Requires Blacksmithing (375)<br>Requires Cenarion Expedition - Exalted<br>Use: Teaches you how to make a Wildguard Breastplate.<br>\
<br>\
<span class=\"myPurple\">Wildguard Breastplate</span>\
<br>Binds when equipped<br>Chest<span class=\"myRight\">Plate</span>\
<br>1450 Armor<br>+45 Stamina<br>+60 Nature Resistance<br>Durability 165 / 165<br>Requires Level 70<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 14.</span>\
<br>Requires Felsteel Bar (8), Primal Life (12), Primal Shadow (12), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPlansWildguardBreastplate; ++i;

var fPatternNethercleftLegArmor = new RewardItem("alliance","Pattern: Nethercleft Leg Armor","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/INV_Scroll_03.jpg");
fPatternNethercleftLegArmor.itemMoneyPrice = new Array();
fPatternNethercleftLegArmor.itemMoneyPrice[3] = 120000
fPatternNethercleftLegArmor.itemStats = new Array();
fPatternNethercleftLegArmor.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Pattern: Nethercleft Leg Armor<br>Binds when picked up<br>Requires Leatherworking (365)<br>Requires Cenarion Expedition - Exalted<br>Use: Teaches you how to make Nethercleft Leg Armor.<br>\
<br>\
<span class=\"myBlue\">Nethercleft Leg Armor</span>\
<br>Requires Level 60<br>\
<span class=\"myGreen\">Use: Permanently attach clefthide armor onto pants to increase stamina by 40 and agility by 12.</span>\
<br>Requires Heavy Knothide Leather (4), Thick Clefthoof Leather (16), Primal Earth (8), Primal Nether</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fPatternNethercleftLegArmor; ++i;

var fDesignTheNaturalWard = new RewardItem("alliance","Design: The Natural Ward","/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons/canonical_inv_scroll_04.jpg");
fDesignTheNaturalWard.itemMoneyPrice = new Array();
fDesignTheNaturalWard.itemMoneyPrice[3] = 120000
fDesignTheNaturalWard.itemStats = new Array();
fDesignTheNaturalWard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Design: The Natural Ward</span>\
<br>Binds when picked up<br>Requires Jewelcrafting (375)<br>Requires Cenarion Expedition - Exalted<br>Use: Teaches you how to craft The Natural Ward.<br>\
<br>\
<span class=\"myPurple\">The Natural Ward</span>\
<br>Binds when equipped<br>Unique-Equipped<br>Finger<br>+28 Stamina<br>+35 Nature Resistance<br>Requires Level 70\
<br>Requires Mercurial Adamantite (4), Felsteel Bar (2), Primal Life (6), Primal Shadow (6)</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fDesignTheNaturalWard; ++i;

var fFormulaEnchantCloakStealth = new RewardItem("alliance","Formula: Enchant Cloak - Stealth","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2Frecipe.gif&reason=external-or-uncollected-resource");
fFormulaEnchantCloakStealth.itemMoneyPrice = new Array();
fFormulaEnchantCloakStealth.itemMoneyPrice[3] = 100000
fFormulaEnchantCloakStealth.itemStats = new Array();
fFormulaEnchantCloakStealth.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myGreen\">Formula: Enchant Cloak - Stealth</span>\
<br>Binds when picked up<br>Requires Enchanting (300)<br>Requires Cenarion Expedition - Exalted<br>\
<span class=\"myGreen\">Use: Teaches you how to permanently enchant a cloak to increase stealth.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fFormulaEnchantCloakStealth; ++i;


var fEarthwarden = new RewardItem("alliance","Earthwarden","/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/images/icons/INV_Hammer_10.gif");
fEarthwarden.itemMoneyPrice = new Array();
fEarthwarden.itemMoneyPrice[3] = 2537735
fEarthwarden.itemStats = new Array();
fEarthwarden.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Earthwarden</span>\
<br>Binds when picked up<br>Unique<br>Two Hand<span class=\"myRight\">Mace</span>\
<br>142 - 279 Damage<span class=\"myRight\">Speed 3.20</span>\
<br>(65.8 damage per second)<br>500 Armor<br>+ 39 Stamina<br>Requires Level 70<br>Requires Cenarion Expedition - Exalted<br>\
<span class=\"myGreen\">Equip: Increases defense rating by 27.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases feral combat skill rating by 24.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases attack power by 556 in Cat, Bear, Dire Bear, and Moonkin forms only.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fEarthwarden; ++i;


var fWindcallersOrb = new RewardItem("alliance","Windcaller's Orb","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Misc_Orb_01.gif&reason=external-or-uncollected-resource");
fWindcallersOrb.itemMoneyPrice = new Array();
fWindcallersOrb.itemMoneyPrice[3] = 790112
fWindcallersOrb.itemStats = new Array();
fWindcallersOrb.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Windcaller's Orb</span>\
<br>Binds when picked up<br>Unique<br>Held In Off Hand<br>+16 Intellect<br>+12 Spirit<br>Requires Level 70<br>Requires Cenarion Expedition - Exalted<br>\
<span class=\"myGreen\">Equip: Increases healing done by spells and effects by up to 64.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fWindcallersOrb; ++i;

var fAshyensGift = new RewardItem("alliance","Ashyen's Gift","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fimages%2Ficons%2FINV_Jewelry_Ring_51.gif&reason=external-or-uncollected-resource");
fAshyensGift.itemMoneyPrice = new Array();
fAshyensGift.itemMoneyPrice[3] = 790112
fAshyensGift.itemStats = new Array();
fAshyensGift.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">\
<span class=\"myPurple\">Ashyen's Gift</span>\
<br>Binds when picked up<br>Unique<br>Finger<br>+30 Stamina<br>Requires Level 70<br>Requires Cenarion Expedition - Exalted<br>\
<span class=\"myGreen\">Equip: Improves spell hit rating by 21.</span>\
<br>\
<span class=\"myGreen\">Equip: Increases damage and healing done by magical spells and effects by up to 23.</span>\
</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fAshyensGift; ++i;

var fCenarionExpeditionTabard = new RewardItem("alliance","Cenarion Expedition Tabard","/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fcenarionxp%2Fscripts%2Frewards-cenarion-expedition.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fbasics%2Ffactions%2Falteracvalley%2Fstormpikebattletabard.gif&reason=external-or-uncollected-resource");
fCenarionExpeditionTabard.itemMoneyPrice = new Array();
fCenarionExpeditionTabard.itemMoneyPrice[3] = 10000
fCenarionExpeditionTabard.itemStats = new Array();
fCenarionExpeditionTabard.itemStats[3] = "\
<table width=\"275\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">\
<tr>\
<td>\
<div class=\"myTable\">Cenarion Expedition Tabard<br>Binds when picked up<br>Unique<br>Tabard<br>Requires Cenarion Expedition - Exalted</div>\
</td>\
</tr>\
</table>\
";
RewardItems[i] = fCenarionExpeditionTabard; ++i;



//-------------------------------------------------------------------
//---Horde below







//------END REWARDS DEFINITION------
