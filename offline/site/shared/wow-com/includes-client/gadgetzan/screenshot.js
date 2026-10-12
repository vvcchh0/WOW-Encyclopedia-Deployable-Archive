function screenshot(number, language, align, caption, text)
{	
	var fullScreenS = "'" + path + theDirectory + language + "ss" + number + ".jpg'";

	var captionS = "'" + caption + "'"

		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "'+align+'">');
		document.write('<tr><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/top.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/left.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('<td><a href = "javascript:popUpOmega('+ fullScreenS +',800,600,'+captionS+');"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');	document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/right.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right.gif"></td>');
		document.write('</tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span class="smallBold"><a href = "javascript:popUpOmega('+ fullScreenS +',800,600,'+captionS+');">'+ text +'</a></span></td></tr>');
		document.write('</table>');
}

function screenshotResized(number, width, height, language, align, caption, text)
{	
	var fullScreenS = "'" + path + theDirectory + language + "ss" + number + ".jpg'";

	var captionS = "'" + caption + "'"

		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "'+align+'">');
		document.write('<tr><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/top.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/left.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('<td><a href = "javascript:popUpOmega('+ fullScreenS +','+ width +','+ height +','+captionS+');"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');	document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/right.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right.gif"></td>');
		document.write('</tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span class="smallBold"><a href = "javascript:popUpOmega('+ fullScreenS +','+ width +','+ height +','+captionS+');">'+ text +'</a></span></td></tr>');
		document.write('</table>');
}

function drawThumbnail(number, width, height, language, align, linking, text)
{	
	var fullScreenS = "'" + path + theDirectory + language + "ss" + number + ".jpg'";

	var linkingS = "'" + linking + "'"

		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "'+align+'">');
		document.write('<tr><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/top.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/left.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('<td><a href="'+ linking +'"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');	document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/right.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right.gif"></td>');
		document.write('</tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span class="smallBold">'+ text +'</span></td></tr>');
		document.write('</table>');
}

function screenshotvar(number, language, align, caption, text) 
{	
	var fullScreenS = "'" + path + theDirectory + language + "ss" + number + ".jpg'";
	
	var captionS = "'" + caption + "'"

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');
		document.write('<tr><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/top.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/top-right.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/left.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('<td><a href = "javascript:popUpOmega('+ fullScreenS +','+ sswidth +','+ ssheight +','+ captionS +');"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');	document.write('<td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/right.gif"><img src = "/shared/wow-com/images/layout/pixel.gif"></td>');
		document.write('</tr><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left.gif"></td>');
		document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0"><tr>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-left-left.gif"></td><td background = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot.gif" width = "100%"><img src = "/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right-right.gif"></td>');
		document.write('</tr></table></td>');
		document.write('<td><img src = "/shared/wow-com/images/gadgetzan/borders/screenshot/bot-right.gif"></td>');
		document.write('</tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span class="smallBold"><a href = "javascript:popUpOmega('+ fullScreenS +','+ sswidth +','+ ssheight +','+captionS+');">'+ text +'</a></span></td></tr>');
		document.write('</table>');
}

function screenshotNoBorder(number, language, align, caption, text) {	

	var fullScreenS = "'" + path + theDirectory + language + "ss" + number + ".jpg'";

	var captionS = "'" + caption + "'"

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else if (align == "left")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "left">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');
		document.write('<tr><td>');
		document.write('<a href = "javascript:popUpOmega('+ fullScreenS +', 800, 600,'+captionS+');"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a>');
		document.write('</td></tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'">'+ text +'</a></span></td></tr>');
		document.write('</table>');
}

function screenshotNoBorderResized(number, width, height, language, align, caption, text) {	

	var fullScreenS = "'" + path + theDirectory + language + "ss" + number + ".jpg'";

	var captionS = "'" + caption + "'"

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else if (align == "left")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "left">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');
		document.write('<tr><td>');
		document.write('<a href = "javascript:popUpOmega('+ fullScreenS +','+ width +','+ height +','+captionS+');"><img src = "'+ path + theDirectory + language + 'ss'+ number +'-thumb.jpg" border = "0"></a>');
		document.write('</td></tr>');
	if (text)
		document.write('<tr><td colspan = 3 align = center><span><a href = "javascript:popUpOmega('+ fullScreenS +','+ width +','+ height +','+captionS+');">'+ text +'</a></span></td></tr>');
		document.write('</table>');
}

var theURL = document.location.href;
var path = theURL;
var letter;
for (var i = (path.length - 1); letter != "/"; i--)
{
  letter = path.charAt(i);
}

i = i+1;
path = path.substring(0, i);

var x = 0;
for (var i = 0; x != 3; i++)
{
  letter = path.charAt(i);
  if (letter == "/") x++;
}

path = path.substring((i - 1), path.length) + "/";
