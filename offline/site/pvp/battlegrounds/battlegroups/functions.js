var numberOfColumns = 3;

//Get the number of realms in each battlegroup
	var battleCounter = new Array;
	var j = 0;
	while (realms[j]){
	if (!battleCounter[realms[j][2]-1])
		battleCounter[realms[j][2]-1] = 0;
		battleCounter[realms[j][2]-1]++;
		j++;
	}

	
//Get the max number of realms in each row
	var maxRealmsInRow = new Array;
	j = 0;

	while (j < battleCounter.length){
		whichRow = Math.floor(j/numberOfColumns);
		if (!maxRealmsInRow[whichRow])
			maxRealmsInRow[whichRow] = 0;
		temp = battleCounter[j];
		if (temp > maxRealmsInRow[whichRow])
			maxRealmsInRow[whichRow] = temp;
		j++;
	}

document.write('<center><table>');
document.write('<tr><td valign = top>');

document.write('<a name = "battlegroup1"></a><table width = 250 cellspacing = "0" cellpadding = "0"><tr><td colspan = 2><table cellspacing = "0" cellpadding = "0" border = "0" width = "100%"><tr><td><img src = "images/borders/header-left.gif"></td><td width = "24" background = "images/borders/header-bg.gif"><span style = "position: relative; left: -3;"><img src = "images/icons/'+ battlegroupIcons[0] +'.gif"></span></td><td background = "images/borders/header-bg.gif"><span style = "position: relative; left: -5; top: -1;"><img src = "images/iconborder.gif"></span></td><td width = "100%" bgcolor = "#05374A" background = "images/borders/header-bg.gif" valign = "bottom"><img src = "images/text/'+ battlegroupIcons[0] +'.gif" style = "margin-left: 10px;"></td><td><img src = "images/borders/header-right.gif"></td></tr></table></td></tr><tr><td>');

document.write('<table width = 100% border = 0 cellpadding = 0 cellspacing = 0><tr><td width = 7 background = "images/borders/metalborder-left.gif"></td><td bgcolor = 0b0b0b valign = "top"><table width = 100% border = 0 cellpadding = 0 cellspacing = 0>');

function sortNumber(a, b){
	result = a[2] - b[2];
	return result;
}

var sorted = new Array;
sorted = realms.sort(sortNumber);

theLast = sorted.length - 1;

lastBattlegroup = sorted[theLast][2];
var z = 1;

var eachTable = 0;

for (var i = 0; sorted[i]; i++) {

	if (z + 1 == sorted[i][2]){	
		whichGroup = z + 1;
		document.write('</table></td><td background = "images/borders/metalborder-right.gif" width = 6><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "'+ maxRealmsInRow[Math.floor((whichGroup-2)/numberOfColumns)] * 24 +'"></td></tr></table>');

		document.write('<table cellpadding = "0" cellspacing = "0" border = "0"><tr><td><img src = "images/borders/metalborder-bot-left.gif"></td><td width = "100%" background = "images/borders/metalborder-bot.gif"></td>');
		document.write('<td><img src = "images/borders/metalborder-bot-right.gif"></td>');
		document.write('</tr>');		
		
		document.write('</table></td></tr></table>')	
		if (z == lastBattlegroup - 1 && lastBattlegroup%numberOfColumns == 1)
			document.write('</td></tr></table><p><table width = 250><tr><td valign = top align = center>');		
		else if (z%numberOfColumns == 0)
			document.write('</td></tr></table><p><table width = 250><tr><td valign = top>');
		else		
			document.write('</td><td>&nbsp;&nbsp;&nbsp;</td><td valign = top>');		

document.write('<a name = "#battlegroup'+ whichGroup +'"></a><table width = 250 cellspacing = "0" cellpadding = "0"><tr><td colspan = 2><table cellspacing = "0" cellpadding = "0" border = "0" width = "100%"><tr><td><img src = "images/borders/header-left.gif"></td><td width = "24" background = "images/borders/header-bg.gif"><span style = "position: relative; left: -3;"><img src = "images/icons/'+ battlegroupIcons[whichGroup-1] +'.gif"></span></td><td background = "images/borders/header-bg.gif"><span style = "position: relative; left: -5; top: -1;"><img src = "images/iconborder.gif"></span></td><td width = "100%" bgcolor = "#05374A" background = "images/borders/header-bg.gif" valign = "bottom"><img src = "images/text/'+ battlegroupIcons[whichGroup-1] +'.gif" style = "margin-left: 10px;"></td><td><img src = "images/borders/header-right.gif"></td></tr></table></td></tr><tr><td>');			
		
		document.write('<table border = 0 cellspacing = 0 cellpadding = 0 width = 100%><tr><td background = "images/borders/metalborder-left.gif" width = 7></td><td bgcolor = 0b0b0b valign = "top"><table width = 100% border = 0 cellpadding = 0 cellspacing = 0>');
		
		eachTable = 0;
		z++;
	}
	
	if (eachTable%2 == 0)
		theBgColor = "";
	else
		theBgColor = "bgcolor = 252115";
	
	document.write('<tr><td class = rankingRow '+ theBgColor +' id = "realmRow'+i+'"><span id = "realmID'+ i +'">');
	document.write(sorted[i][0]);
	document.write('</span></td><td class = rankingRowCenter '+ theBgColor +' id = "realmRowRight'+ i +'"><font color = "f0f0f0">');

	whichType = sorted[i][1];
/*	if (whichType == "PvP")
		document.write('<font color = "f20000">');
	else if (whichType == "Normal")
		document.write('<font color = "d87500">');
	else if (whichType == "RP")
		document.write('<font color = "2ed800">');
	else
		document.write('<font color = "d8c600">');*/
	document.write(whichType);
	document.write('</font></td></tr>');		
	
	eachTable++;
	
}
http://asun-xp.corp.blizzard.net:8080/pvp/battlegrounds/battlegroups.html?inputRealmName=spire#battlegroup3

document.write('</table></td><td background = "images/borders/metalborder-right.gif" width = 6><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "'+ maxRealmsInRow[Math.floor((whichGroup-1)/numberOfColumns)] * 24 +'"></td></tr></table>');

		document.write('<table border = "0" cellpadding = "0" cellspacing = "0"><tr><td><img src = "images/borders/metalborder-bot-left.gif"></td><td width = 100% background = "images/borders/metalborder-bot.gif"></td>');
		document.write('<td><img src = "images/borders/metalborder-bot-right.gif"></td>');
		document.write('</tr>');		

document.write('</table></td></tr></table></td></tr></table></center>');

var matchedArray = new Array;

function findRealm(form){

	clearFoundRealms();
	var goToThisGroup = 0;
	var matchedArrayCounter = 0;

	document.getElementById('threeChars').style.visibility = "hidden";
	document.getElementById('realmNotFound').style.visibility = "hidden";	

	if (form.length < 3) {
		document.getElementById('threeChars').style.visibility = "visible";	
		document.theForm.inputRealmName.value = "";		
		return false;
	}
	
	for (var i = 0; sorted[i]; i++) {
		blah = form.toLowerCase();
		realmNameString = sorted[i][0].toLowerCase();
		blah = realmNameString.match(blah);
		if (blah){
			matchedArray[matchedArrayCounter] = i;
			matchedArrayCounter++;
		 	if (!goToThisGroup) {
				goToThisGroup = sorted[i][2];
				//if (goToThisGroup > 2)
					this.location.href = "index.html#battlegroup" + sorted[i][2];
			}
			document.getElementById('realmID'+i).style.color = "ffcc01";
			document.getElementById('realmRow'+i).className = "rankingRowSearchLeft";			
			document.getElementById('realmRowRight'+i).className = "rankingRowSearch";
		}
	}
	
	if (!goToThisGroup) {
		document.getElementById('realmNotFound').style.visibility = "visible";		
	}
	
	document.theForm.inputRealmName.value = "";
	return false;			
}

function clearFoundRealms() {
	for(k = 0; k < matchedArray.length; k++) {
		document.getElementById('realmID'+matchedArray[k]).style.color = "cccccc";
		document.getElementById('realmRow'+matchedArray[k]).className = "rankingRow";
		document.getElementById('realmRowRight'+matchedArray[k]).className = "rankingRowCenter";
	}
	matchedArray.length = 0;
}


/*  var query = window.location.search.substring(1);
  var vars = query.split("=");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split(",");
}
	if (pair[0])
		findRealm(pair[0]);*/
		
document.write('<p><br><center>');				
document.write('[ <a href = "index.html#top">'+ returnToTop +'</a> ]');		
document.write('</center><p>');						

document.theForm.inputRealmName.focus();	