function printTitle(theTitle){
	document.write("<table cellpadding = 0 cellspacing = 0 border = 0 background = 'images/category_title.gif' width = 365><tr><td width = 30><img src = 'images/pixel.gif' height = 27 width = 30></td><td><b><font color = ffbb03 size = 2>"+ theTitle +"</font></b></td></tr></table>");
}


function printBar(server, i, setbg){

	if (theNumber == 43)
		iSaved = i - 1;
	else
		iSaved = i;
	i = server * theNumber + i;
	
	gatheredSingle = gathered[0][i];
	needed = neededArray[iSaved];
	divided = gatheredSingle/needed * 150;
	percentage = Math.floor(gatheredSingle/needed * 100);

	if (gongIsRung) {
		gatheredSingle = needed;
		divided = 150;
		percentage = 100;
	}

	if (setbg == 1)
		backgroundColor = "images/bluebar.gif";	
	else
		backgroundColor = "images/greenbar.gif";
	document.write("<table background = 'images/item.gif' cellpadding = 0 cellspacing = 0 border = 0 height = 25 width = 365>");
	document.write("<tr><td width = 10><img src = 'images/pixel.gif' height = 25 width = 10></td>");
	document.write("<td><img src = 'images/pixel.gif' height = 25 width = 5></td>");
	document.write("<td width = 95>");

	if (setbg == 1)
		document.write("<font color = 'e0f4ff'>" +resourcesName[iSaved] + "</font>");
	else
		document.write(resourcesName[iSaved]);
	
	document.write("</td>");
	document.write("<td width = 13><img src = 'images/pixel.gif' width = 13 height = 1></td>");
	document.write("<td><div style = 'width: 150;'><div style = 'width: "+ divided +"; background: url("+ backgroundColor +");'>")

	if (percentage != 0)
		document.write("<img src = images/pixel.gif height = '15' width = '1'>");
	
	document.write("</div></div></td>");
	document.write("<td width = 80>"+ gatheredSingle +"/"+ needed +"</td></tr>");
	document.write("<tr><td colspan =4></td><td><div style = 'position: relative; top: -18; width: 145; left: 70;'><div style = 'position: absolute;'>"+ percentage +"%</div></div></td></tr></table>");
	
}

function printTotal(AorH){


	if (AorH == 0) {
		gatheredSingle = gatheredAlliance;
		needed = allianceTotal;
		textTotal = textAllianceTotal;
	} else {
		gatheredSingle = gatheredHorde;
		needed = hordeTotal;
		textTotal = textHordeTotal;	
	}
	
	percentage = Math.floor(gatheredSingle/needed * 100);
	divided = gatheredSingle/needed * 150;
	
	if (gongIsRung == 1) {
		percentage = 100;
		divided = 150;
		gatheredSingle = needed;

	}
	
	backgroundColor = "images/tealbar.gif";	
	document.write("<table background = 'images/item.gif' cellpadding = 0 cellspacing = 0 border = 0 height = 25 width = 365>");
	document.write("<tr><td width = 15><img src = 'images/pixel.gif' height = 25 width = 15></td>");
	document.write("<td><img src = 'images/pixel.gif' height = 25 width = 5></td>");
	document.write("<td width = 90>" +textTotal + "</td>");
	document.write("<td width = 13><img src = 'images/pixel.gif' width = 13 height = 1></td>");
	document.write("<td><div style = 'width: 150;'><div style = 'width: "+ divided +"; background: url("+ backgroundColor +");'>")

	if (percentage != 0)
		document.write("<img src = images/pixel.gif height = '15' width = '1'>");
	
	document.write("</div></div></td>");
	document.write("<td width = 80>"+ gatheredSingle +"/"+ needed +"</td></tr>");
	document.write("<tr><td colspan =4></td><td><div style = 'position: relative; top: -15; width: 145; left: 70;'><div style = 'position: absolute;'>"+ percentage +"%</div></div></td></tr></table>");
}

function printServerTotal(){


		gatheredSingle = gatheredTotal;
		needed = neededTotal;
		textTotal = textServerTotal;
	
	percentage = Math.floor(gatheredSingle/needed * 100);
	divided = gatheredSingle/needed * 554;
	
	if (gongIsRung == 1) {
		percentage = 100;
		divided = 554;
	}
	
	backgroundColor = "images/servertotalbar.gif";	
	document.write("<table background = 'images/servertotal.gif' width = 743 cellpadding = 0 cellspacing = 0 border =0><tr><td><img src = 'images/pixel.gif' height = 38></td>");
	document.write("<td width = '143'><img src = 'images/pixel.gif' height = 38 width = 143></td><td><div style = 'width: 554;'><div style = 'width: "+ divided +"; background: url("+ backgroundColor +");'>")

	if (percentage != 0)
		document.write("<img src = images/pixel.gif height = '20' width = '1'>");
	
	document.write("</div></div></td>");
	document.write("<td width = '105'></td></tr>");
	document.write("<tr><td colspan=2></td><td><div style = 'position: relative; top: -25; left: 170;'><div style = 'position: absolute;'><b><font color = ffffff>"+ percentage +"% - "+ gatheredSingle +"/"+ needed +"</font></b></div></div></td></tr></table>");
}

function printBottom() {

	document.write("<table border = 0 cellpadding = 0 cellspacing = 0><tr><td><img src = 'images/category_bottom.gif'></td></tr></table>");

}
