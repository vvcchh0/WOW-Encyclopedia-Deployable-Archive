<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/wrath/layout/global.xsl"/>

<xsl:template name="styles">
	div.sub-header-top { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="story/@background"/>-t.jpg'); }
	div.sub-header-left { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="story/@background"/>-l.jpg'); height: 400px; }
	div.sub-header-right { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="story/@background"/>-r.jpg'); height: 400px; }
</xsl:template>

<xsl:template match="story">
  	<xsl:variable name="risePath" select="document(concat('../strings/',$lang,'/features/rise.xml'))" />
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$risePath/content/@name"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>

<xsl:template name="pagecontents">
	<xsl:call-template name="story-page"/>
</xsl:template>

<xsl:template name="story-page">
  <xsl:variable name="risePath" select="document(concat('../strings/',$lang,'/features/rise.xml'))" />
 <div class="stories-top"></div>
<div class="features">
<div class="subcat storypad">
<div class="story-top"></div>
 <div class="story-back">
  <div class="story-sides">
  <div class="story-sub-top">
    <div class="story-sub-bot">
  <div class="story-back-top"></div>
  <div class="story-brackets"><i class="left"><b></b></i><i class="right"><b></b></i>
 <div class="story-block">
 <xsl:for-each select="$risePath/content/segment">
 	<div class="story-title">
<h4><xsl:value-of select="$loc/strs/str[@id='labels.chapter']"/>&#160;<span id = "rChap1"><xsl:value-of select="section/@chapter"/></span><strong><xsl:value-of select="$loc/strs/str[@id='labels.chapter']"/>&#160;<span id = "rChap2"><xsl:value-of select="section/@chapter"/></span></strong></h4>
  <h1><xsl:value-of select="@subtitle"/><strong id = "rSubtitle"><xsl:value-of select="section/@subtitle"/></strong></h1>
	</div>
</xsl:for-each>
<div id="replaceSection"></div>

<script type="text/javascript">
  var globalPageCur = 1;
  var totalPages = 9;
	var sectionArray = new Array;
	var chapterArray = new Array;
	var i = 0;

  function goToChapter(whichChapter) {
	  goToPage(chapterArray[whichChapter]);
	}

  function goToPage(whichPage) {  
			if (whichPage == 0 || whichPage > totalPages)
			return false;
			document.getElementById('changePage'+globalPageCur).className = "story-paging";		
		globalPageCur = whichPage;
			document.getElementById('changePage'+globalPageCur).className = "story-paging-off";
		
			if (globalPageCur != 1) {
				elemIdSection.innerHTML = document.getElementById('divSection'+globalPageCur).innerHTML;
				document.getElementById('changeArrowLeft').className = 'story-paging';			
		} else {
				document.getElementById('changeArrowLeft').className = 'arrowleft-off';	
		}  
			if (globalPageCur != totalPages) {
				elemIdSection.innerHTML = document.getElementById('divSection'+globalPageCur).innerHTML;
				document.getElementById('changeArrowRight').className = 'story-paging';					
		} else {
				document.getElementById('changeArrowRight').className = 'arrowright-off';	
		}
		document.getElementById('rChap1').innerHTML = sectionArray[whichPage-1][0];
		document.getElementById('rChap2').innerHTML = sectionArray[whichPage-1][0];		
		document.getElementById('rSubtitle').innerHTML = sectionArray[whichPage-1][1];				
  }  
  
  var elemIdSection = document.getElementById('replaceSection');
  
</script>
  <xsl:for-each select="$risePath/content/segment/section">
  <div id="divSection{position()}" style="display: none;">
  	<xsl:apply-templates/>
	</div>
	
	<script type="text/javascript">
		sectionArray[i] = ["<xsl:value-of select = "@chapter" />", "<xsl:value-of select = "@subtitle" />"];		
		i++;
		
		if (!chapterArray[<xsl:value-of select = "@chapter" />])
			chapterArray[<xsl:value-of select = "@chapter" />] = <xsl:value-of select = "position()" />
			
	</script>
	
  </xsl:for-each>
	
<div class="story-controls">
<div id="replacePaging"></div>
<div id="changeArrowLeft" class="arrowleft"><strong><a href ="#" onclick="goToPage(globalPageCur-1); return false;"><xsl:value-of select="$loc/strs/str[@id='labels.previous']"/></a><xsl:value-of select="$loc/strs/str[@id='labels.previous']"/></strong></div>

<div id="changeArrowRight" class="arrowright"><strong><a href ="#" onclick="goToPage(globalPageCur+1); return false;"><xsl:value-of select="$loc/strs/str[@id='labels.next']"/></a><xsl:value-of select="$loc/strs/str[@id='labels.next']"/></strong></div>

</div>
  <script type="text/javascript">
  //<![CDATA[
  var rsPaging = "";
  for (var i = 1; i <= totalPages; i++) {
  	rsPaging += '<a href = "#" id = "changePage'+ i +'" onClick = "javascript: goToPage('+ i +'); return false;" >' + i +' ';
  }
  
  document.getElementById('replacePaging').innerHTML = rsPaging;
  document.getElementById('changePage1').className = "story-paging-off";
  //]]>
  </script>
<script type="text/javascript">
elemIdSection.innerHTML = document.getElementById('divSection1').innerHTML;
document.getElementById('changeArrowLeft').className = 'arrowleft-off';	

queryChapter=(document.location.hash).replace("#", "");

if (queryChapter)
  goToChapter(queryChapter);
 

</script> 
	</div>
	</div>
	</div>
  </div>
  </div>
 </div>
   <div class="story-footer"><div class="story-bot"><a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fstory.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffeatures.xml&reason=invalid-overlay-or-uncollected-site-resource"><span>&#171;</span><xsl:value-of select="' '"/><xsl:value-of select="$loc/strs/str[@id='labels.returntofeatures']"/></a></div></div> 
 </div>
</div>
<div class="features-bot"></div>
</xsl:template>

<xsl:template match="stories">
  <xsl:variable name="risePath" select="document(concat('../strings/',$lang,'/features/rise.xml'))" />
<div class="story-list">
<h2><xsl:value-of select="$loc/strs/str[@id='wrath.story.chapters']"/></h2>
<xsl:for-each select="$risePath/content/story">
<xsl:variable name="chapter" select="chapter" />
	<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fstory.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&reason=invalid-overlay-or-uncollected-site-resource" class="zone-menu">
	 <ul>
	  <li class="item"><span><xsl:value-of select="$loc/strs/str[@id=$chapter]"/></span></li>
	 </ul>
	</a>
</xsl:for-each>	
</div>
</xsl:template>

</xsl:stylesheet>


