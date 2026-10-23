function screenshot(number, align, text) {	

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else if (align == "left")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "left">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');	
	document.write('<tr><td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top-left.gif"></td>');
	document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0" width = 100%><tr>');
	document.write('<td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top-left-left.gif"></td><td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top.gif" width = "100%"><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top-right-right.gif"></td>');
	document.write('</tr></table></td>');
	document.write('<td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top-right.gif"></td>');
	document.write('</tr><tr>');
	document.write('<td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/left.gif"><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/layout/pixel.gif"></td>');
	document.write('<td><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');	document.write('<td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/right.gif"><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/layout/pixel.gif"></td>');
	document.write('</tr><tr>');
	document.write('<td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot-left.gif"></td>');
	document.write('<td><table cellspacing = "0" cellpadding = "0" border = "0" width = "100%"><tr>');
	document.write('<td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot-left-left.gif"></td><td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot.gif" width = "100%"><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/layout/pixel.gif"></td><td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot-right-right.gif"></td>');
	document.write('</tr></table></td>');
	document.write('<td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot-right.gif"></td>');
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

var __WOW_LOVE_STORY_PREVIEW_FALLBACKS = {"1":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss1.jpg","2":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss2.jpg","3":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss3.jpg","4":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss4.jpg","5":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss5.jpg","6":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss6.jpg","7":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss7.jpg","8":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss8.jpg","9":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss9.jpg","10":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss10.jpg","11":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss11.jpg","12":"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/images/ss12.jpg"};
var __WOW_LOVE_STORY_PAGE_ROUTES = ["/info/events/loveisintheair","/info/events/loveisintheair/","/info/events/loveisintheair/index.html"];
var __WOW_LOVE_STORY_BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/";
function __wowLoveStoryPreview(number) {
  var pathname = String((document.location && document.location.pathname) || '/');
  var prefix = __WOW_LOVE_STORY_BASE_PATH;
  if (prefix !== '/' && pathname.indexOf(prefix) === 0) pathname = pathname.substring(prefix.length - 1);
  if (__WOW_LOVE_STORY_PAGE_ROUTES.indexOf(pathname) < 0) return '';
  if (typeof theDirectory !== 'string' || theDirectory !== 'images/' || typeof screenshotsTotal === 'undefined' || Number(screenshotsTotal) !== 12) return '';
  var n = Number(number);
  if (n < 1 || n > 12 || Math.floor(n) !== n || String(number) !== String(n)) return '';
  return __WOW_LOVE_STORY_PREVIEW_FALLBACKS[String(n)] || '';
}
function screenshotThinBorder(number, align, text) {	

	if (align == "right")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "right">');
	else if (align == "left")
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0" align = "left">');
	else
		document.write('<table cellspacing = "0" cellpadding = "0" border = "0">');


	document.write('  <tr>');
	document.write('    <td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/top-left.gif" width = "3" height = "2"></td>');
	document.write('    <td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/top.gif"></td>');
	document.write('    <td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/top-right.gif" width = "6" height = "2"></td>');
	document.write('  </tr>');
	document.write('  <tr>');
	document.write('    <td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/left.gif"></td>');
	var __loveStoryPreview = __wowLoveStoryPreview(number);
	if (__loveStoryPreview)
		document.write('<td><a href = "'+ __loveStoryPreview +'"><img src = "'+ __loveStoryPreview +'" border = "0" style = "max-width:200px;height:auto;"></a></td>');
	else
		document.write('<td><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'"><img src = "'+ path + theDirectory + 'ss'+ number +'-thumb.jpg" border = "0"></a></td>');
	document.write('    <td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/right.gif"></td>');
	document.write('  </tr>');
	document.write('    <td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/bot-left.gif" width = "3" height = "7"></td>');
	document.write('    <td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/bot.gif"></td>');
	document.write('    <td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/gold-thin/bot-right.gif" width = "6" height = "7"></td>');
	document.write('  </tr>');

	if (text) {
		if (__loveStoryPreview)
			document.write('<tr><td colspan = 3 align = center><span><a href = "'+ __loveStoryPreview +'">'+ text +'</a></span></td></tr>');
		else
			document.write('<tr><td colspan = 3 align = center><span><a href = "/imageviewer.html?'+ path +','+ theDirectory +','+ number +','+ screenshotsTotal +','+ theURL +'">'+ text +'</a></span></td></tr>');
	}
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
