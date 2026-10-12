function ShowFlash(url, width, height){
		document.write('<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fflashmap%2Fflashview.js&requested=http%3A%2F%2Fdownload.macromedia.com%2Fpub%2Fshockwave%2Fcabs%2Fflash%2Fswflash.cab%23version%3D7%2C0%2C19%2C0&reason=external-or-uncollected-resource" width="' + width + '" height="' + height + '"id=wow_flash VIEWASTEXT id=wow_flash >');
	document.write('<param name="movie" value="' + url + '">');
	document.write('<param name="allowScriptAccess" value="always" />');
	document.write('<param name="quality" value="high">');
	document.write('<PARAM NAME=wmode VALUE=transparent>');
	document.write('<embed src="' + url + '" quality="high" allowScriptAccess="always" pluginspage="/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fflashmap%2Fflashview.js&requested=http%3A%2F%2Fwww.macromedia.com%2Fgo%2Fgetflashplayer&reason=external-or-uncollected-resource" type="application/x-shockwave-flash" wmode="transparent" width="' + width + '" height="' + height + '"></embed>');
	document.write('</object>');
}