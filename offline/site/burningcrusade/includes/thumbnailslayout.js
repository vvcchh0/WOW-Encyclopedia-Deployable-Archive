  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("@");
}
	var queryCurrentPage = pair[0];
	var queryTotalPages = pair[1];
	
	if (!queryCurrentPage) {
		queryCurrentPage = 1;
		queryTotalPages = 1;
	}
	
function printPageNumbers() {	
var sPath = window.location.pathname;
var sPage = sPath.substring(sPath.lastIndexOf('/') + 1);

	if (pages != 1) {
	for (x = 1; x<=pages; x++) {
		document.write("<a href ="+ path + sPage +"?"+ x +"@"+ pages +">");

		if (x == currentPage)
			document.write("<font color = ffffff>");
		document.write(x);
		if (x == currentPage)
			document.write("</font>");
		document.write("</a>");
		if (x != pages)
			document.write(" | ");
		
	}
}

}