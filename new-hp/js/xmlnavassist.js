// XML Escapegoat
function escapeGoat(result)
{
	var iconId;
	if (result!=1)
		categoryItemString = '<a href = "' + Menu2[1] + '"><img src = "/shared/wow-com/images/subnav/icon_' + Menu2[0].toLowerCase() + '.jpg" width="59" height="65" border = "0"></a>';
	else 
		categoryItemString = '<a href = "' + Menu1[1] + '"><img src = "/shared/wow-com/images/subnav/icon_' + Menu1[0].toLowerCase() + '.jpg" width="59" height="65" border = "0"></a>';
	document.getElementById("navIconTableCell").innerHTML = categoryItemString;
}