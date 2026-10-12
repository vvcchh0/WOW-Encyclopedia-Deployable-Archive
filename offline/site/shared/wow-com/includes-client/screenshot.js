function screenshot(number, align, text) {	

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else if (align == "left")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "left">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');	
	document.write('<tr><td><img src = "/shared/wow-com/images/borders/screenshot/top-left.gif"></td>');
	document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0" width = 100%><tr>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/top-left-left.gif"></td><td background = "/shared/wow-com/images/borders/screenshot/top.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/borders/screenshot/top-right-right.gif"></td>');
	document.write('</tr></table></td>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/top-right.gif"></td>');
	document.write('</tr><tr>');
	document.write('<td background = "/shared/wow-com/images/borders/screenshot/left.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
	document.write('<td><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');	document.write('<td background = "/shared/wow-com/images/borders/screenshot/right.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
	document.write('</tr><tr>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/bot-left.gif"></td>');
	document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0" width = "100%"><tr>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/bot-left-left.gif"></td><td background = "/shared/wow-com/images/borders/screenshot/bot.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/borders/screenshot/bot-right-right.gif"></td>');
	document.write('</tr></table></td>');
	document.write('<td><img src = "/shared/wow-com/images/borders/screenshot/bot-right.gif"></td>');
	document.write('</tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'">'+ text +'</a></span></td></tr>');
	document.write('</table>');
}

function screenshotNoBorder(number, align, text) {	

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else if (align == "left")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "left">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');
	document.write('<tr><td>');
	document.write('<a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a>');
	document.write('</td></tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'">'+ text +'</a></span></td></tr>');
	document.write('</table>');
}

function screenshotThinBorder(number, align, text) {	

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else if (align == "left")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "left">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');


	document.write('  <tr>');
	document.write('    <td><img src = "/shared/wow-com/images/borders/gold-thin/top-left.gif" width = "3" height = "2"></td>');
	document.write('    <td background = "/shared/wow-com/images/borders/gold-thin/top.gif"></td>');
	document.write('    <td><img src = "/shared/wow-com/images/borders/gold-thin/top-right.gif" width = "6" height = "2"></td>');
	document.write('  </tr>');
	document.write('  <tr>');
	document.write('    <td background = "/shared/wow-com/images/borders/gold-thin/left.gif"></td>');
	document.write('<td><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');
	document.write('    <td background = "/shared/wow-com/images/borders/gold-thin/right.gif"></td>');
	document.write('  </tr>');
	document.write('    <td><img src = "/shared/wow-com/images/borders/gold-thin/bot-left.gif" width = "3" height = "7"></td>');
	document.write('    <td background = "/shared/wow-com/images/borders/gold-thin/bot.gif"></td>');
	document.write('    <td><img src = "/shared/wow-com/images/borders/gold-thin/bot-right.gif" width = "6" height = "7"></td>');
	document.write('  </tr>');

	if (text)
		document.write('<tr><td colspan = 3 align = center><span><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'">'+ text +'</a></span></td></tr>');
	document.write('</table>');
}

var theURL = document.location.href;
var path = theURL;
var letter;
for (var i = (path.length - 1); letter != "/"; i--) {
  letter = path.charAt(i);
}
i = i+1;
path = path.substring(0, i);

var x = 0;
for (var i = 0; x != 3; i++) {
  letter = path.charAt(i);
  if (letter == "/")
  	x++;
}

path = path.substring((i - 1), path.length) + "/";
