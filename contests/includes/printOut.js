


var leadingZero;

var x = thumb.length-1;

document.write("<center><table border = 0 cellpadding = 5 cellspacing = 0>");

while (x >= 1) {
	document.write("<tr>");
		for (var columnsLoop = columns; columnsLoop > 0; columnsLoop--)
		{
			if (thumb[x]){
				if (x < 10)
					leadingZero = "0";
				else 
					leadingZero = "";
					
				document.write("<td align = \"center\" valign = \"top\" width = \""+ 100/columns +"%\"><table cellpadding = \"0\" cellspacing = \"0\" border = \"0\"><tr><td colspan = \"3\" width = \"220\"><img src=/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot-202x152/large-ss-thumb-border-top.gif width = \"220\" height = \"8\"></td></tr><tr><td width = \"8\"><img src=/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot-202x152/large-ss-thumb-border-left.gif width = \"8\" height = \"152\"></td><td width = \"202\">");
				document.write("<a href=/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcontests%2Fincludes%2FprintOut.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fwow%2Fssotd%2Fimageviewer.aspx%3FImageIndex%3D&reason=external-or-uncollected-resource"+ x +"&Set="+ set +"><img src="+ path +"ss"+ leadingZero + x  +"-thumb.jpg border = 0></a><br>");
				document.write("</td><td width = \"10\"><img src=/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot-202x152/large-ss-thumb-border-right.gif width = \"10\" height = \"152\"></td></tr><tr><td colspan = \"3\" width = \"220\"><img src=/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot-202x152/large-ss-thumb-border-bot.gif width = \"220\" height = \"11\"></td></tr><tr><td colspan = \"3\" width = \"220\"><span>");

				if (thumb[x][0] != "")
				{
					document.write("<small class = \"blood\"><i>"+thumb[x][0] +"</i></small>");
					
					if (thumb[x][0] !="" && (thumb[x][1] != "" || thumb[x][2] != ""))
						document.write(" - ");		
				}
					
				if (thumb[x][1] !="" || thumb[x][2] != "")
				{
					document.write(" <small>Submitted by </small> ");

					if (thumb[x][1] != "")
						document.write("<b>"+ thumb[x][1] +"</b> ");
			
					if (thumb[x][1] != "" && thumb[x][2] != "") 
						document.write("<small> of </small>");
			
					if (thumb[x][2] != "")
						document.write(" <b>"+thumb[x][2] +"</b> ");
				}

				document.write("</span></td></tr></table></td>");
				x--;
			}
		}
	document.write("</tr>")
	
	document.write("<tr><td colspan = "+ columns +">&nbsp;</td></tr>");
	
}

document.write("</table></center>");