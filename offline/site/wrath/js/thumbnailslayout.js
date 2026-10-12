function screenshot(number, notThumb) {
	if(!notThumb)
		notThumb = number;
	massiveReplaceString += '<table cellpadding="0" cellspacing="0" border="0"><tr><td><div class="ssborder" style="background-image:url('+ theDirectory + 'ss'+ number +'-thumb.jpg);"><div><a href = "'+ whichImageviewer +'.xml?s='+ notThumb +'"><img src="'+roothost+'images/layout/ssborder1.png" class="png" /></a></div></div></td></tr>';
	massiveReplaceString += '</table>';
}

var theURL = document.location.href;
var path = theURL;
var letter;

path = roothost;



var query = window.location.search.substring(1);
  var vars = query.split("s=");
/*  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("@");
}*/
	var queryCurrentPage = vars[1];

	var queryTotalPages;
	
	if (!queryCurrentPage) {
		queryCurrentPage = 1;
		queryTotalPages = 1;
	}
	
function printPageNumbers() {	
var sPath = window.location.pathname;
var sPage = sPath.substring(sPath.lastIndexOf('/') + 1);


massiveReplaceString += "<div style='margin:0 40px;'>"

	if (pages != 1) {
		var calcPreviousPage = eval(queryCurrentPage) - 1;
		var calcNextPage = eval(queryCurrentPage) + 1;
		if (calcPreviousPage)
			massiveReplaceString += "<div class='pagearrow left'><a href ="+ path + sPage +"?s="+ calcPreviousPage +"><img src='./images/layout/arrow-prev.gif' /></a><div class='pageprev'><a href ="+ path + sPage +"?s="+ calcPreviousPage +">"+ tPrev +"</a></div><div class='pageprevshadow'>"+ tPrev +"</div></div>";
			else massiveReplaceString += "<div class='pagearrow left'><img src='./images/layout/arrow-prevgrey.gif' /><div class='pageprev'>"+ tPrev +"</div><div class='pageprevshadow'>"+ tPrev +"</div></div>";

	if (queryCurrentPage != queryTotalPages)
		massiveReplaceString += "<div class='pagearrow right'><div class='pagenext'><a href ="+ path + sPage +"?s="+ calcNextPage +">"+ tNext +"</a></div><div class='pagenextshadow'>"+ tNext +"</div><a href ="+ path + sPage +"?s="+ calcNextPage +"><img src='./images/layout/arrow-next.gif' /></a></div>";
		else massiveReplaceString += "<div class='pagearrow right'><div class='pagenext'>"+ tNext +"</div><div class='pagenextshadow'>"+ tNext +"</div><img src='./images/layout/arrow-nextgrey.gif' /></div>";

	for (x = 1; x<=pages; x++) {
		massiveReplaceString += "<a href ="+ path + sPage +"?s="+ x +" class='paging'>";

		if (x == currentPage)
			massiveReplaceString += "<span>";
		massiveReplaceString += x;
		if (x == currentPage)
			massiveReplaceString += "</span>";
		massiveReplaceString += "</a>";
		if (x != pages)
			massiveReplaceString += "<span class='paging-divider'>&nbsp;&nbsp;&nbsp;&nbsp;</span>";
	}
}

massiveReplaceString += "</div>"
}