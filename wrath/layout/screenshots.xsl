<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/WOW-Encyclopedia-Deployable-Archive/wrath/layout/global.xsl"/>

<xsl:template name="styles">
	div.sub-header-top { background: url('images/layout/header2-t.jpg'); }
	div.sub-header-left { background: url('images/layout/header2-l.jpg'); height: 400px; }
	div.sub-header-right { background: url('images/layout/header2-r.jpg'); height: 400px; }
	div.sub-text-container { margin:0; }
</xsl:template>

<xsl:template match="screenshots">
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$loc/strs/str[@id='wrath.subtitle.name.screenshots']"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>

<xsl:template name="pagecontents">

<script type="text/javascript">
//<![CDATA[
var whichImageviewer = "screenshot";
//]]>
</script>

<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/wrath/images/screenshots/screenshotscounter.js"></script>
<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fscreenshots.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fimages%2Fscreenshots%2F%7B%24lang%7D%2Fscreenshotscounter.js&amp;reason=invalid-overlay-or-uncollected-site-resource"></script>

<script type="text/javascript">

//uncomment below to set a different abolute path; ex: /path/path/
//path = "";
var theCommonDirectory = roothost + "images/screenshots/";
var theLocDirectory = roothost + "images/screenshots/<xsl:value-of select = "$lang" />/";
theDirectory = theCommonDirectory;
</script>

<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fscreenshots.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fstrings%2F%7B%24lang%7D%2Fstrings.js&amp;reason=invalid-overlay-or-uncollected-site-resource"></script>
<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/wrath/js/thumbnailslayout.js"></script>

<div style="text-align:center;">


<script type="text/javascript">
//<![CDATA[
	screenshotsTotal = screenshotsLocTotal + screenshotsCommonTotal;
	var massiveReplaceString = "";
	var columns = 3;
	var pages = 1; 

	var currentPage = queryCurrentPage;

	screenshotsPerPage = 9;
	pages = Math.ceil(screenshotsTotal/screenshotsPerPage);
	queryTotalPages = pages;
	var screenshotsLastPage;
	
	screenshotsLastPage = screenshotsTotal%screenshotsPerPage;
	if (!screenshotsLastPage)
		screenshotsLastPage = screenshotsPerPage;
		
	printPageNumbers();
//]]>
</script>


<script type="text/javascript">
//<![CDATA[
massiveReplaceString += "<div class='screenindex'><div class='blacktop'></div><div class='blackmid'><table style='margin:0 40px;'>";
	
	var theStart = screenshotsCommonTotal - ((currentPage - 1) * screenshotsPerPage);

	if (currentPage == pages)
		screenshotsPerPage = screenshotsLastPage;
	var theEnd = theStart - screenshotsPerPage;
	
	var whichColumn = 1;

	while (theStart > theEnd) {
		if (whichColumn == 1)
			massiveReplaceString += "<tr>";
		massiveReplaceString += "<td>";
		if (theStart > 0)
			screenshot(theStart);
		else {
			theDirectory = theLocDirectory;			
			screenshot(theStart + screenshotsTotal - screenshotsCommonTotal, screenshotsTotal + theStart);
		}
		massiveReplaceString += "<\/td>";
		if (whichColumn == columns){
			massiveReplaceString += "<\/tr>";		
			whichColumn = 1;
		} else 
			whichColumn++;
		theStart--;
	}	
	
massiveReplaceString += "<\/table><\/div><div class='blackbot'><\/div><\/div>";
//]]>
</script>

<div id="replaceDiv"></div>

<script type="text/javascript">
//<![CDATA[
printPageNumbers();
document.getElementById('replaceDiv').innerHTML = massiveReplaceString;
//]]>
</script>

</div>

<br/><br/>
</xsl:template>

</xsl:stylesheet>