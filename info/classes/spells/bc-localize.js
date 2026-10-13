var rankString = "Rank";							
var requiresLevelString = "Requires Level";
var allianceOnly = "<span class = 'newEffect'>Alliance Only</span>";
var hordeOnly = "<span class = 'newEffect'>Horde Only</span>";

function printIntroString(whichString, newEffects) {
	stringLowerCase = whichString.toLowerCase();
	document.write("<img src = /WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/smallcaps/plain/w.gif align = 'left'>elcome to the "+ whichString +" Spells and Abilities Preview Page! Listed below are some of the new spells available to the "+stringLowerCase+" beyond level 60. The page lists spells new to the game along with a screenshot of the spell in action.");
	if (newEffects)
		document.write(" Also displayed are the new ranks for spells that have new effects (denoted in red).");
	document.write(" The page does not show higher ranks of old spells");
	if (newEffects)
		document.write(" that don't have new effects");
	document.write(".<p>Also be sure to check out the <a href = '/info/classes/bc-"+ stringLowerCase +"/talents.html'>Talent Preview</a> for more "+ whichString +" updates!");
	document.write(".<p><small>Note: The spells and abilities listed below are not final and may be subject to change in final release.</small>");


}

var barArray = new Array;

barArray[0] = "Mana";
barArray[1] = "Energy";
barArray[2] = "Rage";
barArray[3] = "Health";

function convertCastTime(theCastTime) {
	if (theCastTime < 0)
		return "";
	if (theCastTime == 1)
		return "Next melee";
	if (theCastTime == 0)
		return "Instant cast";					//LOCALIZE THIS
	theResult = theCastTime/1000;
	if (theResult >= 60) {
		theResult = theResult/60;
		printOut = theResult + " min cast";		//LOCALIZE THIS
	} else
		printOut = theResult + " sec cast";		//LOCALIZE THIS
	return printOut;
}

function convertRange(theRange) {
	if (theRange == 0)
		return "";
	else {
		printOut = theRange + " yd range";		//LOCALIZE THIS
		return printOut;
	}
}

function convertBar(theCost, theBar) {
	if (theCost == 0 || theBar < 0)
		return "";
	else {
		printOut = theCost + " "+ barArray[theBar];		//LOCALIZE THIS
		return printOut;
	}
}

function convertCooldown(cooldown) {
	if (cooldown <= 0)
		return "";
	theResult = cooldown/1000;
	if (theResult >= 60) {
		theResult = theResult/60;
		printOut = theResult + " min cooldown";		//LOCALIZE THIS
	} else
		printOut = theResult + " sec cooldown";		//LOCALIZE THIS
	return printOut;
}

function convertRank (theRank) {
	return rankString +' '+ theRank;				//CHANGE ORDER IF NEEDED
}