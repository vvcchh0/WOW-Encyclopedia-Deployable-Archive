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



var queryParams = new URLSearchParams(window.location.search);
var queryValues = queryParams.getAll("s");
var queryCurrentPage = 1;
if (queryValues.length === 1 && /^[1-9][0-9]*$/.test(queryValues[0])) {
	var parsedPage = Number(queryValues[0]);
	if (Number.isSafeInteger(parsedPage) && parsedPage >= 1)
		queryCurrentPage = parsedPage;
}
var queryTotalPages = 1;
function printPageNumbers() {
	var actualPages = Number(pages);
	if (!Number.isSafeInteger(actualPages) || actualPages < 1)
		actualPages = 1;
	queryTotalPages = actualPages;
	if (!Number.isSafeInteger(queryCurrentPage) || queryCurrentPage < 1 || queryCurrentPage > actualPages)
		queryCurrentPage = 1;
	currentPage = queryCurrentPage;
	
var sPath = window.location.pathname;
var sPage = sPath.substring(sPath.lastIndexOf('/') + 1);


massiveReplaceString += "<div style='margin:0 40px;'>"

	if (pages != 1) {
		var calcPreviousPage = queryCurrentPage - 1;
		var calcNextPage = queryCurrentPage + 1;
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