function spell(spellName, school, level, rank, description, DONTLOCALIZE, castTime, range, barCost, barType, extra, cooldown) {
	this.spellName = spellName;
	this.school = school;
	this.level = level;
	this.rank = rank;
	this.description = description;
	this.DONTLOCALIZE = DONTLOCALIZE;
	this.castTime = castTime;	
	this.range = range;		
	this.barCost = barCost;
	this.barType = barType;
	this.extra = extra;	
	this.cooldown = cooldown;		
}

function printSpell(whichSpell){

	var theSpellRank = spellsArray.rank[whichSpell];
								document.write('<table cellspacing = "0" cellpadding = "0" border = "0" width = "90%"><tr><td valign = top width = "450"><table border = "0" width = "459" cellpadding = "0" cellspacing = "0"><tr><td><img src = "/shared/wow-com/images/borders/plainboxwithshadow/top-left.gif" width = 14 height = 13></td><td background = "/shared/wow-com/images/borders/plainboxwithshadow/top.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/borders/plainboxwithshadow/top-right.gif" width = 19 height = 13></td></tr><tr><td background = "/shared/wow-com/images/borders/plainboxwithshadow/left.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"</td><td width = "100%" style = "padding: 5px"><table border = 0 cellpadding = 0 cellspacing = 0 width = 100%><tr><td style = "padding-right: 10px;" rowspan = 5 valign = top width = 51><div id = "wrapper"><div id = "iconOverParchment"><img src = "../images/talents/icon-over-parchment.gif" border = 0></div></div>');
								document.write('<img src = images/spells/'+ spellsArray.DONTLOCALIZE[whichSpell] +'.jpg width = 51 height = 53>');
								document.write('</td><td width = "100%"><table cellspacing = "0" cellpadding = "0" border = "0" width = "100%"><tr><td width = "1"><img src = "/shared/wow-com/images/headers/minisubheader/minisubheader-end.gif" width = "1" height = "16"></td><td bgcolor = "#05374A" width = "100%"><span class = "smallBold" style = "color:white;">&nbsp;<b>');
	document.write(spellsArray.spellName[whichSpell]);
								document.write('</b>');
	if (theSpellRank > 0) 
		document.write('- '+ convertRank(theSpellRank));
								document.write('</td><td width = "1"><img src = "/shared/wow-com/images/headers/minisubheader/minisubheader-end.gif" width = "1" height = "16"></td></tr></table></td></tr><tr><td style = "padding-left: 10;"><span class = "smallBlack">');
	if (spellsArray.level[whichSpell] > 0)
		document.write(requiresLevelString +' '+ spellsArray.level[whichSpell] +'<br>');
	if (spellsArray.barCost[whichSpell] || spellsArray.range[whichSpell])
		document.write('<span style=text-align:left;float:left; class=smallBlack>'+ convertBar(spellsArray.barCost[whichSpell], spellsArray.barType[whichSpell]) +'</span><span style=text-align:right;float:right; class=smallBlack>'+ convertRange(spellsArray.range[whichSpell]) +'</span><br>');
	if (spellsArray.castTime[whichSpell] >= 0 || spellsArray.cooldown[whichSpell])
		document.write('<span style=text-align:left;float:left; class=smallBlack>'+ convertCastTime(spellsArray.castTime[whichSpell]) +'</span><span style=text-align:right;float:right; class=smallBlack>'+ convertCooldown(spellsArray.cooldown[whichSpell]) +'</span><br>');
	if (spellsArray.extra[whichSpell])
		document.write(spellsArray.extra[whichSpell]+ '<br>');
	document.write('<span class=smallBold>');

	document.write(spellsArray.description[whichSpell]);
								
							document.write('</span></span></td></tr></table></td><td background = "/shared/wow-com/images/borders/plainboxwithshadow/right.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td></tr><tr><td><img src = "/shared/wow-com/images/borders/plainboxwithshadow/bot-left.gif" width = 14 height = 25></td><td background = "/shared/wow-com/images/borders/plainboxwithshadow/bot.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/borders/plainboxwithshadow/bot-right.gif" width=19 height=25></td></tr></table></td><td valign = top>');

	if (theSpellRank == 0 || theSpellRank == 1)
		screenshotSpells(whichSpell, spellsArray.spellName[whichSpell]);
	else
		document.write('<img src = "/shared/wow-com/images/layout/pixel.gif" height = 1 width = 183>');
							document.write('</td></tr></table><p>');
}

var schoolCurrent = 0;
var spellCurrent = 0;

function printAllSpells() {
	while (spellsArray.spellName[spellCurrent]) {
		if (spellsArray.school[spellCurrent] == schoolCurrent) {
			document.write('</blockquote></div></div><div class = "guideHeader"><table width="100%" align="center" cellspacing = "0" cellpadding = "0" border = "0" ><tr>	<td width="10"><img src="/shared/wow-com/images/headers/tabheader/tabheader-left-left.jpg" width="17" height="29" border="0" ></td>    <td width = "362" background = "/shared/wow-com/images/headers/tabheader/tabheader-left.jpg" align = "left" NOWRAP><h3 class = "guideTitle">'+ school[schoolCurrent] +'</h3></td><td width="100%" background = "/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg"></td></tr></table></div><div class = "postContainerPlain"><div class = "postBody"><blockquote>');
			schoolCurrent++;
		}
		printSpell(spellCurrent);
		spellCurrent++;
	}
	document.write('</blockquote>');
}

function screenshotSpells(number, text) {	

	document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');	
	document.write('<tr><td><img src = "/shared/wow-com/images/borders/screenshot/top-left.gif"></td>');
	document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0" width = 100%><tr>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/top-left-left.gif"></td><td background = "/shared/wow-com/images/borders/screenshot/top.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/borders/screenshot/top-right-right.gif"></td>');
	document.write('</tr></table></td>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/top-right.gif"></td>');
	document.write('</tr><tr>');
	document.write('<td background = "/shared/wow-com/images/borders/screenshot/left.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
	document.write('<td><a href = "#none" onClick = "javascript: screenshotSpellsPopUp('+ number +');"><img src = "/info/classes/bc-'+ theClassStringLowerCase +'/images/spells/screenshots/'+ spellsArray.DONTLOCALIZE[number] +'-thumb.jpg" border = "0"></a></td>');	document.write('<td background = "/shared/wow-com/images/borders/screenshot/right.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
	document.write('</tr><tr>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/bot-left.gif"></td>');
	document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0" width = "100%"><tr>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/bot-left-left.gif"></td><td background = "/shared/wow-com/images/borders/screenshot/bot.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/borders/screenshot/bot-right-right.gif"></td>');
	document.write('</tr></table></td>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/bot-right.gif"></td>');
	document.write('</tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span><a href = "#none" onClick = "javascript: screenshotSpellsPopUp('+ number +');">'+ text +'</a></span></td></tr>');
	document.write('</table>');
}

function screenshotSpellsPopUp(namedCreature) 
{
	imageWidth = 800;
	//Browser detection - is the user relying on the one browser where this script does not work?
	var is_safari = ((navigator.appName.indexOf('safari')!=-1)&&(navigator.appName.indexOf('mac')!=-1))?true:false;
	var screenshot = "/info/classes/bc-"+ theClassStringLowerCase +"/images/spells/"+ spellsArray.DONTLOCALIZE[namedCreature] +".jpg"; //gimp variable for Safari =P

	var name = "Sheenscrot";
	var imgDimensions = (imageWidth == 800) ? [800,577] : [577,800];
	widthHeight = "width=" + imgDimensions[0] + ",height=" + imgDimensions[1];
	winFeatures = "width=" + imgDimensions[0] + ",height=" + imgDimensions[1] + ",left=200,top=25,menubar=no,resizable=no,scrollbars=no,statusbar=no,toolbar=no,locationbar=no"
	if (is_safari) spawn = window.open(screenshot,name,winFeatures);
	else
	{
		spawn = window.open("/shared/wow-com/images/layout/pixel.gif",name,winFeatures)
		spawn.document.write("<html><head><title><\/title><\/head><body onBlur='self.close()' style='background-image:url(/info/classes/bc-"+ theClassStringLowerCase +"/images/spells/screenshots/"+ spellsArray.DONTLOCALIZE[namedCreature] +".jpg); background-repeat:no-repeat;'><\/body><\/html>"); 
		spawn.document.close();
	}
}