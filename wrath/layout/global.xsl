<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"/>

<!-- Language Settings-->
<xsl:template match="@*|node()">
   <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
   </xsl:copy>
</xsl:template>

<xsl:variable name="lang" select="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpage%2F%40lang&amp;reason=external-or-uncollected-resource" />
<xsl:variable name="loc" select="document(concat('../strings/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fstrings.xml&amp;reason=external-or-uncollected-resource'))" />
<xsl:variable name="baseurl" select="$loc/strs/str[@id='wrath.base']"/>

<!-- Document Header-->

<xsl:template name="head">
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title><xsl:value-of select="$loc/strs/str[@id='wrath']"/></title>
	<link rel="alternate" type="application/rss+xml" title="Wrath of the Lich King Updates RSS Feed" href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fstrings%2F%7B%24lang%7D%2Frss.xml&amp;reason=invalid-overlay-or-uncollected-site-resource" />

	<style type="text/css">
	@import url(<xsl:value-of select="$baseurl"/>css/master.css);
	@import url(<xsl:value-of select="$baseurl"/>css/<xsl:value-of select="$lang"/>/language.css);
	<xsl:call-template name="styles"/>
	</style>
	
	<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7B%24baseurl%7Djs%2Fdetection.js&amp;reason=invalid-overlay-or-uncollected-site-resource"></script>
	<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7B%24baseurl%7Djs%2Ffunctions.js&amp;reason=invalid-overlay-or-uncollected-site-resource"></script>
	
	<script type="text/javascript">
	
		//Set the Mediahost Variable
		var lang = "<xsl:value-of select="$lang"/>";
		var mediahost = "<xsl:value-of select="$loc/strs/str[@id='wrath.mediahost']"/>";
		var roothost = "<xsl:value-of select="$baseurl"/>";
	
		

			//Flash External Interface
			var flashMovie;
			
			function callExternalInterface() {
				thisMovie("flashmainFlash").openMovie();
			}
			
			function thisMovie(movieName) {
				if (navigator.appName.indexOf("Microsoft") != -1) {
					return window[movieName]
				}
				else {
					return document[movieName]
				}
			}
			
			//<![CDATA[
			// Browser-specific CSS		
		
			if (is_ie6 &amp;&amp; !is_ie7)
			document.write('<link rel="stylesheet" type="text/css" media="screen, projection" href="'+ roothost +'/css/ie.css" />');
			if (is_ie7)
			document.write('<link rel="stylesheet" type="text/css" media="screen, projection" href="'+ roothost +'/css/ie7.css" />');
			if (is_opera)
			document.write('<link rel="stylesheet" type="text/css" media="screen, projection" href="'+ roothost +'/css/opera.css" />');
			if (is_safari)
			document.write('<link rel="stylesheet" type="text/css" media="screen, projection" href="'+ roothost +'/css/safari.css" />');
		//]]>
	</script>
	
</xsl:template>


<!-- Styles Template -->

<xsl:template name="styles">

</xsl:template>


<!-- General Flash Template -->

<xsl:template name="flash">
	<xsl:param name="id" />
	<xsl:param name="width" />
	<xsl:param name="height" />
	<xsl:param name="src" />
   	<xsl:param name="quality" />
	<xsl:param name="base" />
	<xsl:param name="flashvars" />
	<xsl:param name="bgcolor" />
	<xsl:param name="menu" />
	<xsl:param name="wmode" />
	<xsl:param name="noflash" />
	<xsl:param name="allowScriptAccess" />
	

		<div id="{$id}"></div>
		<script type="text/javascript">
		var flashId="<xsl:value-of select='$id'/>";
		printFlash("<xsl:value-of select='$id'/>", "<xsl:value-of select='$src'/>", "<xsl:value-of select='$wmode'/>", "<xsl:value-of select='$menu'/>", "<xsl:value-of select='$bgcolor'/>", "<xsl:value-of select='$width'/>", "<xsl:value-of select='$height'/>", "<xsl:value-of select='$quality'/>", "<xsl:value-of select='$base'/>", "<xsl:value-of select='$flashvars'/>", "<xsl:value-of select='$allowScriptAccess'/>", "<xsl:value-of select='$noflash'/>")
		</script>	
	
</xsl:template>


<!-- Language Selection Drop Down menu -->


<xsl:template name="dropdownMenu">
	<xsl:param name="defaultValue" />
	<xsl:param name="hiddenId" />
	<xsl:param name="dropdownList" />
	
	<script type="text/javascript">
		var varOver<xsl:value-of select ="$hiddenId" /> = 0;
	</script>
	
	
	<div class="dropdown" onMouseOver="javascript: varOver{$hiddenId} = 1;" onMouseOut="javascript: varOver{$hiddenId} = 0;"><div class="dropdown-bg"></div><a id="display{$hiddenId}" href="javascript: document.formDropdown{$hiddenId}.dummy{$hiddenId}.focus();"><xsl:value-of select="$defaultValue" /></a></div>
	  
	<div style="position:relative;"><div style="position:absolute;"><form name="formDropdown{$hiddenId}" id="formDropdown{$hiddenId}" style="height:0px;"><input type="button" id="dummy{$hiddenId}" onFocus="javascript: dropdownMenuToggle('dropdownHidden{$hiddenId}');" onBlur="javascript: if(!varOver{$hiddenId}) document.getElementById('dropdownHidden{$hiddenId}').style.display='none';" size="2" style="position:relative; left:-5000px;"/></form></div></div>
	
	
	<div class="drop-lang" style="display:none;" id="dropdownHiddenLang" onMouseOver="javascript:varOverLang=1;" onMouseOut="javascript:varOverLang=0;">
		<div class="light-tip">
			<table cellpadding="0" cellspacing="0">
				<tr><td class="tl"></td><td class="t"></td><td class="tr"></td></tr>
				<tr><td class="l"><q></q></td>
				<td class="bg">
				<ul>
					<li style="margin-top:.5em;"><a href="javascript: selectLang('{$loc/strs/str[@id='wrath.labels.english-us']}', 'en_us');"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.english-us']"/></a></li>
					<li><a href="javascript: selectLang('{$loc/strs/str[@id='wrath.labels.english-gb']}', 'en_gb');"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.english-gb']"/></a></li>
					<li><a href="javascript: selectLang('{$loc/strs/str[@id='wrath.labels.german']}', 'de_de');"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.german']"/></a></li>
					<li><a href="javascript: selectLang('{$loc/strs/str[@id='wrath.labels.spanish']}', 'es_es');"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.spanish']"/></a></li>
					<li><a href="javascript: selectLang('{$loc/strs/str[@id='wrath.labels.french']}', 'fr_fr');"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.french']"/></a></li>
					<li style="margin-bottom:.5em;"><a href="javascript: selectLang('{$loc/strs/str[@id='wrath.labels.korean']}', 'ko_kr');"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.korean']"/></a></li>
				</ul>
				</td><td class="r"><q></q></td>
				</tr>
				<tr><td class="bl"></td><td class="b"></td><td class="br"></td></tr>
			</table>
		</div> 
	</div>
			
</xsl:template>

<!-- Share PAGE HTML Code-->

<xsl:template match="page">
	<html>
		<head>
			<xsl:call-template name="head" />
		</head>
		<body>
			<div>
			<xsl:attribute name="class"><xsl:choose><xsl:when test="@pageType='front'">frontpage-container</xsl:when><xsl:otherwise>page-container</xsl:otherwise></xsl:choose></xsl:attribute>
				<div class="content-container">
					<xsl:call-template name="nav"/>
					<xsl:apply-templates />
				</div>
			</div>


		<xsl:choose>
			<xsl:when test="$lang='en_us'">
				<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.google-analytics.com%2Fga.js&amp;reason=external-or-uncollected-resource"></script>
				<script type="text/javascript">
				var pageTracker = _gat._getTracker("UA-544112-18");
				pageTracker._setDomainName("worldofwarcraft.com");
				pageTracker._initData();
				pageTracker._trackPageview();
				</script>
			</xsl:when>
			<xsl:when test="$lang='ko_kr'">
				<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.google-analytics.com%2Fga.js&amp;reason=external-or-uncollected-resource"></script>
				<script type="text/javascript">
				var pageTracker = _gat._getTracker("UA-544112-20");
				pageTracker._setDomainName("worldofwarcraft.co.kr");
				pageTracker._initData();
				pageTracker._trackPageview();
				</script>
			</xsl:when>
			<xsl:when test="$lang='de_de' or $lang='es_es' or $lang='fr_fr' or $lang='en_gb'">
				<script type="text/javascript" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.google-analytics.com%2Fga.js&amp;reason=external-or-uncollected-resource"></script>
				<script type="text/javascript">
				var pageTracker = _gat._getTracker("UA-544112-21");
				pageTracker._setDomainName("wow-europe.com");
				pageTracker._initData();
				pageTracker._trackPageview();
				</script>
			</xsl:when>
		</xsl:choose>
		
		</body>
	</html>
</xsl:template>




<!-- Frontpage HTML Code-->

<xsl:template match="frontpage">
	<div class="frontpage-right">
		<div class="frontpage-right-top"/>
		<div class="frontpage-mainflash">
		
		<xsl:call-template name="flash">
			<xsl:with-param name="id" select="'flashmain'"/>
			<xsl:with-param name="src" select="concat($loc/strs/str[@id='wrath.mediahost'],'flash/global/loader.swf')"/>
			<xsl:with-param name="wmode" select="'window'"/>
			<xsl:with-param name="width" select="'514'"/>
			<xsl:with-param name="height" select="'1013'"/>
			<xsl:with-param name="base" select="concat($baseurl,'flash/global')"/>
			<xsl:with-param name="bgcolor" select="'#000000'"/>
			<xsl:with-param name="allowScriptAccess" select="'always'"/>			
			<xsl:with-param name="quality" select="'autohigh'"/>
				<xsl:with-param name="flashvars" select="concat(
					'&amp;flang=',$lang,
					'&amp;mainfile=',$loc/strs/str[@id='wrath.mediahost'],'flash/global/main.swf',
					'&amp;trailerfile=',$loc/strs/str[@id='wrath.mediahost'],'movies/wrath-trailer/',$loc/strs/str[@id='wrath.main.trailerfile'],
					'&amp;moviecontrolsfile=',$loc/strs/str[@id='wrath.mediahost'],'flash/global/moviecontrols.swf'
				)"/>			
			<xsl:with-param name="noflash">&lt;div class='frontpage-arthas'&gt;&lt;/div&gt;</xsl:with-param>			
		</xsl:call-template>
		
		</div>
		<div class="frontpage-right-bottom"/>		
	</div>
	<div class="frontpage-left">
		<div class="frontpage-news-top">
			<xsl:call-template name="wrathlogo-frontpage"/>
		</div>
		<div class="frontpage-news-featured">
			<xsl:call-template name="featured" />
		</div>		
		<div class="frontpage-news-mid">	
			<div class="frontpage-news-midtop">	
				<div class="frontpage-news-content">
					<div class="frontpage-news-spacer"></div>
					<div class="frontpage-news-text" id="ajaxcontentarea">
						<div class="language-filter-front">
							<xsl:call-template name="dropdownMenu">
								<xsl:with-param name="hiddenId" select="'Lang'"/>
								<xsl:with-param name="defaultValue" select="$loc/strs/str[@id='wrath.lang']" />
							</xsl:call-template>
						</div>
						<a class="toggle-flash" href="javascript:toggleFlash();"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.flashtoggle']"/></a>&#160;&#160;&#160;|&#160;&#160;&#160;					
						<a class="toggle-flash" href="{$loc/strs/str[@id='wrath.labels.jobs.link']}"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.jobs']"/></a>
						<br/>
						<xsl:apply-templates select="document(concat('../strings/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Foverview.xml&amp;reason=external-or-uncollected-resource'))"/>
		
					</div>
					<div class="frontpage-news-spacer"></div>
				</div>
			</div>				
		</div>	
		<div class="frontpage-news-bottom">
			<div class="reldiv">
				<div class="frontpage-news-right"></div>
				<div class="frontpage-news-left"></div>
				<div class="blizzlogocontainerfront">
					<xsl:call-template name="blizzardlogo"/>			
				</div>
			</div>	
		</div>		
	</div>	
</xsl:template>


<!-- Wrath of the Lich King Logo  -->

<xsl:template name="wrathlogo-frontpage">
	<div class="logocontainer-frontpage">
		<div class="logocontainer-frontpage2">
			<xsl:call-template name="wrathlogo"/>
		</div>
	</div>	
</xsl:template>

<xsl:template name="wrathlogo-subpage">
	<div class="logocontainer-subpage">
		<xsl:call-template name="wrathlogo"/>
	</div>
</xsl:template>

<xsl:template name="wrathlogo">
		<div class="wrathlogopng">
			<div class="wrathlogogif" style="background: url('{$baseurl}images/language/{$lang}/logo_wrath.gif');"><a href="/WOW-Encyclopedia-Deployable-Archive/wrath/index.html"></a></div>
		</div>
</xsl:template>


<!-- Wallpaper Entry -->
<xsl:template name="wallpaper">
	<xsl:param name="title"></xsl:param>
	<xsl:param name="wallid"></xsl:param>
	
	<a name="w{$wallid}"></a>
	<div class="wallpaper">
		<div class="wallpaper2">
			<div class="wall-thumb">
				<ul>
					<li style="height:213px; background:url(./images/wallpapers/wall{$wallid}/wall{$wallid}-thumb.jpg) 0 0 no-repeat;" onmouseover="this.style.backgroundPosition='0 -213px'" onmouseout="this.style.backgroundPosition='0 0'"><a href="#" onclick="fiatLux('./images/wallpapers/wall{$wallid}/wall{$wallid}-800x600.jpg'); return false"></a></li>
					<li style="height:83px; background:url(./images/wallpapers/wall{$wallid}/wall{$wallid}-shadow.png) 0 0 no-repeat;" class="png"></li>
				</ul>
			</div>
			<div class="wall-info">
				<h1><xsl:apply-templates select="$title"/></h1>
				<ul>
					<li><a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fimages%2Fwallpapers%2Fwall%7B%24wallid%7D%2Fwall%7B%24wallid%7D-800x600.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource" target="_blank">800 x 600</a></li>
					<li><a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fimages%2Fwallpapers%2Fwall%7B%24wallid%7D%2Fwall%7B%24wallid%7D-1024x768.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource" target="_blank">1024 x 768</a></li>
					<li><a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fimages%2Fwallpapers%2Fwall%7B%24wallid%7D%2Fwall%7B%24wallid%7D-1280x960.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource" target="_blank">1280 x 960</a></li>
					<li><a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fimages%2Fwallpapers%2Fwall%7B%24wallid%7D%2Fwall%7B%24wallid%7D-1280x1024.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource" target="_blank">1280 x 1024</a></li>
					<li><a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fimages%2Fwallpapers%2Fwall%7B%24wallid%7D%2Fwall%7B%24wallid%7D-1600x1200.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource" target="_blank">1600 x 1200</a></li>
					<li><a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fimages%2Fwallpapers%2Fwall%7B%24wallid%7D%2Fwall%7B%24wallid%7D-1680x1050.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource" target="_blank">1680 x 1050</a></li>
					<li><a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fimages%2Fwallpapers%2Fwall%7B%24wallid%7D%2Fwall%7B%24wallid%7D-1920x1200.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource" target="_blank">1920 x 1200</a></li>
				</ul>
			</div>
		</div>
	</div>
</xsl:template>


<xsl:template match="art">
<!-- art viewer-->
<div class="feature-ss png" onmouseover="this.style.backgroundPosition='0 -188px'" onmouseout="this.style.backgroundPosition='0 0'"><div style="background:url('{$baseurl}images/artwork/ss{@id}-thumb.jpg') 6px 6px no-repeat;"><a href="#" onclick="fiatLux('{$baseurl}images/artwork/ss{@id}.jpg'); return false"></a></div></div>
</xsl:template>

<xsl:template match="customart">
<!-- art viewer-->
<div class="customart" style="float:{@align}; {@style}">
<a href="#" onclick="fiatLux('{$baseurl}images/artwork/ss{@id}.jpg'); return false"><img src="/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7B%24baseurl%7Dimages%2Fartwork%2Fss%7B%40id%7D-thumb.jpg&amp;reason=invalid-overlay-or-uncollected-site-resource"/></a></div>
</xsl:template>


<xsl:template match="flashchar">
<!-- They be steppin' to our crew. Let's bounce! -->
<div id="flashchar" style="position:absolute; top:-200px; margin-left:-40px;"></div>
<div style="height:{@bheight}px; width:250px; display:block; "><!-- --> </div>
<xsl:call-template name="flash">
					<xsl:with-param name="id" select="'flashchar'"/>
					<xsl:with-param name="src" select="concat($loc/strs/str[@id='wrath.base'],'flash/global/',@swf,'.swf')"/>
					<xsl:with-param name="wmode" select="'transparent'"/>
					<xsl:with-param name="width" select="@width"/>
					<xsl:with-param name="height" select="@height"/>
					<xsl:with-param name="bgcolor" select="'#000000'"/>
					<xsl:with-param name="quality" select="'autohigh'"/>      

</xsl:call-template>                  

</xsl:template>


<xsl:template match="ss">
<!-- screenshot viewer-->
<div class="feature-ss png" onmouseover="this.style.backgroundPosition='0 -188px'" onmouseout="this.style.backgroundPosition='0 0'"><div style="background:url('{$baseurl}images/screenshots/ss{@id}-thumb.jpg') 6px 6px no-repeat;"><a href="#" onclick="fiatLux('{$baseurl}images/screenshots/ss{@id}.jpg'); return false"></a></div></div>
</xsl:template>


<!-- Lightbox -->
<xsl:template name="lightbox">
<div id="blackDrop" onClick="closeLightbox()"></div>
<div id="lightBoxRoot" onClick="closeLightbox()">
	<div id="cornerFour">
		<div id="lightBoxHolder" title="{$loc/strs/str[@id='wrath.labels.clicktoclose']}"></div>
	</div>
</div>
</xsl:template>


<!-- Graphic Letter -->
<xsl:template match="cap">
	<xsl:call-template name="cap">
			<xsl:with-param name="letter"><xsl:apply-templates /></xsl:with-param>
			<xsl:with-param name="align" select="'left'"/>
	</xsl:call-template>
</xsl:template>

<xsl:template name="cap">
   <xsl:param name="letter" />
   <xsl:param name="align">left</xsl:param>
 		<img src="/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7B%24baseurl%7D%2Fimages%2Fletters%2F%7B%24letter%7D.gif&amp;reason=invalid-overlay-or-uncollected-site-resource" align="{$align}" class="smallcap" />
</xsl:template>


<!-- Page Navigation -->
<xsl:template name="nav">
	<div class="reldiv">
		<div class="nav">
			<xsl:call-template name="flash">
				<xsl:with-param name="id" select="'flashnav'"/>
				<xsl:with-param name="src" select="concat('/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fflash%2F&amp;reason=external-or-uncollected-resource',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnavigation.swf&amp;reason=external-or-uncollected-resource')"/>
				<xsl:with-param name="wmode" select="'transparent'"/>
				<xsl:with-param name="width" select="'980'"/>
				<xsl:with-param name="height" select="'75'"/>
				<xsl:with-param name="base" select="concat($baseurl,'flash/global')"/>  
				<xsl:with-param name="bgcolor" select="'#000000'"/>
				<xsl:with-param name="quality" select="'autohigh'"/>
				<xsl:with-param name="flashvars" select="concat(
					'&amp;flang=',$lang,
					'&amp;menu_1=',$loc/strs/nav/str[@id='wrath.nav.1'],
					'&amp;menu_2=',$loc/strs/nav/str[@id='wrath.nav.2'],
					'&amp;menu_3=',$loc/strs/nav/str[@id='wrath.nav.3'],
					'&amp;menu_4=',$loc/strs/nav/str[@id='wrath.nav.4'],
					'&amp;menu_5=',$loc/strs/nav/str[@id='wrath.nav.5'],
					'&amp;menu_6=',$loc/strs/nav/str[@id='wrath.nav.6'],
					'&amp;menu_7=',$loc/strs/nav/str[@id='wrath.nav.7'],
					'&amp;menu_8=',$loc/strs/nav/str[@id='wrath.nav.8'],
					'&amp;menu_9=',$loc/strs/nav/str[@id='wrath.nav.9'],
					'&amp;menu_1_link=../../',$loc/strs/nav/str[@id='wrath.nav.1']/@link,
					'&amp;menu_2_link=../../',$loc/strs/nav/str[@id='wrath.nav.2']/@link,
					'&amp;menu_3_link=../../',$loc/strs/nav/str[@id='wrath.nav.3']/@link,
					'&amp;menu_4_link=../../',$loc/strs/nav/str[@id='wrath.nav.4']/@link,
					'&amp;menu_5_link=../../',$loc/strs/nav/str[@id='wrath.nav.5']/@link,
					'&amp;menu_6_link=../../',$loc/strs/nav/str[@id='wrath.nav.6']/@link,
					'&amp;menu_7_link=../../',$loc/strs/nav/str[@id='wrath.nav.7']/@link,
					'&amp;menu_8_link=',$loc/strs/nav/str[@id='wrath.nav.8']/@link,
					'&amp;menu_9_link=../../',$loc/strs/nav/str[@id='wrath.nav.9']/@link,
					'&amp;menu_elements=',$loc/strs/navparams/str[@id='wrath.nav.param.menuelements'],
					'&amp;menu_sepchar=',$loc/strs/navparams/str[@id='wrath.nav.param.sepchar'],
					'&amp;menu_vheight=',$loc/strs/navparams/str[@id='wrath.nav.param.vheight'],
					'&amp;menu_yposition=',$loc/strs/navparams/str[@id='wrath.nav.param.yposition'],
					'&amp;menu_space=',$loc/strs/navparams/str[@id='wrath.nav.param.space'],
					'&amp;menu_fontsize=',$loc/strs/navparams/str[@id='wrath.nav.param.fontsize'],
					'&amp;menu_sepfontsize=',$loc/strs/navparams/str[@id='wrath.nav.param.sepfontsize'],
					'&amp;menu_sepdeltay=',$loc/strs/navparams/str[@id='wrath.nav.param.sepdeltay'],
					'&amp;menu_sides=',$loc/strs/navparams/str[@id='wrath.nav.param.sides'],
					'&amp;maintxtmenucolor=',$loc/strs/navparams/str[@id='wrath.nav.param.txtmenucolor'],
					'&amp;maintxtmenuhover=',$loc/strs/navparams/str[@id='wrath.nav.param.txtmenuhover'],
					'&amp;glowcolornormalin=',$loc/strs/navparams/str[@id='wrath.nav.param.glowcolornormalin'],
					'&amp;glowcolornormalout=',$loc/strs/navparams/str[@id='wrath.nav.param.glowcolornormalout'],
					'&amp;glowcolorhoverin=',$loc/strs/navparams/str[@id='wrath.nav.param.glowcolorhoverin'],
					'&amp;glowcolorhoverout=',$loc/strs/navparams/str[@id='wrath.nav.param.glowcolorhoverout'],
					'&amp;fontfile=',$loc/strs/navparams/str[@id='wrath.nav.param.fontfile'],
					'&amp;fontname=',$loc/strs/navparams/str[@id='wrath.nav.param.fontname'],
					'&amp;fontmcname=',$loc/strs/navparams/str[@id='wrath.nav.param.fontmcname'],
					'&amp;fonttxtname=',$loc/strs/navparams/str[@id='wrath.nav.param.fonttxtname']
				)"/>
				<xsl:with-param name="noflash">&lt;div class='navbox'&gt;&lt;div class='navbox-left'&gt;&lt;/div&gt;&lt;div class='navbox-middle'&gt;&lt;div class='navbox-inner-left'>&lt;/div&gt;&lt;div class='navbox-inner-middle'&gt;<xsl:for-each select="$loc/strs/nav/str">&lt;a href = '<xsl:value-of select='$baseurl'/><xsl:value-of select='@link'/>'&gt;<xsl:apply-templates/>&lt;/a&gt;<xsl:choose><xsl:when test="position() &lt; $loc/strs/navparams/str[@id='wrath.nav.param.menuelements']">&lt;em&gt;&lt;/em&gt;</xsl:when></xsl:choose></xsl:for-each>&lt;/div&gt;&lt;div class='navbox-inner-right'&gt;&lt;/div&gt;&lt;/div&gt;&lt;div class='navbox-right'&gt;&lt;/div&gt;&lt;/div&gt;</xsl:with-param>
			</xsl:call-template>

			<xsl:choose>
				<xsl:when test="@pageType = 'front'"></xsl:when>
				<xsl:otherwise>
					<div class="language-filter">
						<strong><xsl:value-of select="$loc/strs/str[@id='wrath.labels.languagecolon']"/></strong><br/>
						<xsl:call-template name="dropdownMenu">
							<xsl:with-param name="hiddenId" select="'Lang'"/>
							<xsl:with-param name="defaultValue" select="$loc/strs/str[@id='wrath.lang']" />
						</xsl:call-template>
					</div>
				</xsl:otherwise>
			</xsl:choose>		
					
		</div>
	</div>
</xsl:template>



<!-- Featured Boxes -->

<xsl:template name="featured">
	<xsl:call-template name="flash">
		<xsl:with-param name="id" select="'flashfeatured'"/>
		<xsl:with-param name="src" select="concat($loc/strs/str[@id='wrath.base'],'flash/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffeatured.swf&amp;reason=external-or-uncollected-resource')"/>
		<xsl:with-param name="wmode" select="'window'"/>
		<xsl:with-param name="width" select="'466'"/>
		<xsl:with-param name="height" select="'183'"/>
		<xsl:with-param name="base" select="concat($baseurl,'flash/global')"/>
		<xsl:with-param name="allowScriptAccess" select="'always'"/>			
		<xsl:with-param name="bgcolor" select="'#000000'"/>
		<xsl:with-param name="quality" select="'autohigh'"/>
		<xsl:with-param name="flashvars" select="concat(
			'&amp;flang=',$lang,
			'&amp;title1=',$loc/strs/str[@id='wrath.featured.title.1'],
			'&amp;sub1=',$loc/strs/str[@id='wrath.featured.sub.1'],
			'&amp;link1=../../',$loc/strs/str[@id='wrath.featured.link.1'],
			'&amp;bg1path=../../',$loc/strs/str[@id='wrath.featured.img.1'],
			'&amp;fontsize1=',$loc/strs/str[@id='wrath.featured.param.fontsize.1'],
			'&amp;fontsizesmall1=',$loc/strs/str[@id='wrath.featured.param.fontsizesmall.1'],
			'&amp;yposition1=',$loc/strs/str[@id='wrath.featured.param.yposition.1'],
			'&amp;letterspacing1=',$loc/strs/str[@id='wrath.featured.param.letterspacing.1'],
			'&amp;title2=',$loc/strs/str[@id='wrath.featured.title.2'],
			'&amp;sub2=',$loc/strs/str[@id='wrath.featured.sub.2'],
			'&amp;link2=../../',$loc/strs/str[@id='wrath.featured.link.2'],
			'&amp;bg2path=../../',$loc/strs/str[@id='wrath.featured.img.2'],
			'&amp;fontsize2=',$loc/strs/str[@id='wrath.featured.param.fontsize.2'],
			'&amp;fontsizesmall2=',$loc/strs/str[@id='wrath.featured.param.fontsizesmall.2'],
			'&amp;yposition2=',$loc/strs/str[@id='wrath.featured.param.yposition.2'],
			'&amp;letterspacing2=',$loc/strs/str[@id='wrath.featured.param.letterspacing.2'],
			'&amp;title3=',$loc/strs/str[@id='wrath.featured.title.3'],
			'&amp;sub3=',$loc/strs/str[@id='wrath.featured.sub.3'],
			'&amp;link3=../../',$loc/strs/str[@id='wrath.featured.link.3'],
			'&amp;bg3path=../../',$loc/strs/str[@id='wrath.featured.img.3'],
			'&amp;fontsize3=',$loc/strs/str[@id='wrath.featured.param.fontsize.3'],
			'&amp;fontsizesmall3=',$loc/strs/str[@id='wrath.featured.param.fontsizesmall.3'],
			'&amp;yposition3=',$loc/strs/str[@id='wrath.featured.param.yposition.3'],
			'&amp;letterspacing3=',$loc/strs/str[@id='wrath.featured.param.letterspacing.3'],
			'&amp;titlecolor1=',$loc/strs/str[@id='wrath.featured.param.titlecolor.1'],
			'&amp;subcolor1=',$loc/strs/str[@id='wrath.featured.param.subcolor.1'],
			'&amp;titlecolor2=',$loc/strs/str[@id='wrath.featured.param.titlecolor.2'],
			'&amp;subcolor2=',$loc/strs/str[@id='wrath.featured.param.subcolor.2'],
			'&amp;titlecolor3=',$loc/strs/str[@id='wrath.featured.param.titlecolor.3'],
			'&amp;subcolor3=',$loc/strs/str[@id='wrath.featured.param.subcolor.3']			
		)"/>
		<xsl:with-param name="noflash">&lt;a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fmovies.xml&amp;reason=invalid-overlay-or-uncollected-site-resource" class='watch-trailer' &gt;&lt;/a&gt;&lt;div class='feature-container'&gt;&lt;div class='feature1' style='background:url(<xsl:value-of select="$loc/strs/str[@id='wrath.featured.img.1']"/>)'&gt;&lt;div class='feature-title'&gt;&lt;h1&gt;<xsl:value-of select="$loc/strs/str[@id='wrath.featured.title.1']"/>&lt;/h1&gt;&lt;h2&gt;<xsl:value-of select="$loc/strs/str[@id='wrath.featured.sub.1']"/>&lt;/h2&gt;&lt;/div&gt;&lt;/div&gt;&lt;div class='feature2' style='background:url(<xsl:value-of select="$loc/strs/str[@id='wrath.featured.img.2']"/>)'&gt;&lt;div class='feature-title'&gt;&lt;h1&gt;<xsl:value-of select="$loc/strs/str[@id='wrath.featured.title.2']"/>&lt;/h1&gt;&lt;h2&gt;<xsl:value-of select="$loc/strs/str[@id='wrath.featured.sub.2']"/>&lt;/h2&gt;&lt;/div&gt;&lt;/div&gt;&lt;div class='feature3' style='background:url(<xsl:value-of select="$loc/strs/str[@id='wrath.featured.img.3']"/>)'&gt;&lt;div class='feature-title'&gt;&lt;h1&gt;<xsl:value-of select="$loc/strs/str[@id='wrath.featured.title.3']"/>&lt;/h1&gt;&lt;h2&gt;<xsl:value-of select="$loc/strs/str[@id='wrath.featured.sub.3']"/>&lt;/h2&gt;&lt;/div&gt;&lt;/div&gt;&lt;div class='feature-links'&gt;&lt;a href='<xsl:value-of select="$loc/strs/str[@id='wrath.featured.link.1']"/>' class='link1'&gt;&lt;/a&gt;&lt;a href='<xsl:value-of select="$loc/strs/str[@id='wrath.featured.link.2']"/>' class='link2'&gt;&lt;/a&gt;&lt;a href='<xsl:value-of select="$loc/strs/str[@id='wrath.featured.link.3']"/>' class='link3'&gt;&lt;/a&gt;&lt;/div&gt;&lt;div class='feature-overlay'&gt;&lt;/div&gt;&lt;/div&gt;</xsl:with-param>
	</xsl:call-template>
</xsl:template>




<!-- Sub Page Flash Title Template  -->

<xsl:template name="flash-sub-title">
<xsl:param name="fl_title" />
<xsl:param name="fl_loc" />
<xsl:call-template name="flash">
					<xsl:with-param name="id" select="$fl_loc"/>
					<xsl:with-param name="src" select="concat($loc/strs/str[@id='wrath.base'],'flash/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsubtitle.swf&amp;reason=external-or-uncollected-resource')"/>
					<xsl:with-param name="wmode" select="'transparent'"/>
					<xsl:with-param name="width" select="'814'"/>
					<xsl:with-param name="height" select="'170'"/>
					<xsl:with-param name="base" select="concat($baseurl,'flash/global')"/>
					<xsl:with-param name="bgcolor" select="'#000000'"/>
					<xsl:with-param name="quality" select="'autohigh'"/>
					<xsl:with-param name="flashvars" select="concat(
						'&amp;flang=',$lang,
						'&amp;sub_fontsize=',$loc/strs/str[@id='wrath.subtitle.param.fontsize'],
						'&amp;sub_deltax=',$loc/strs/str[@id='wrath.subtitle.param.deltax'],
						'&amp;sub_deltay=',$loc/strs/str[@id='wrath.subtitle.param.deltay'],
						'&amp;sub_x=',$loc/strs/str[@id='wrath.subtitle.param.x'],
						'&amp;sub_y=',$loc/strs/str[@id='wrath.subtitle.param.y'],
						'&amp;subtxtcolor=',$loc/strs/str[@id='wrath.subtitle.param.txtcolor'],
						'&amp;sub_letterspacing=',$loc/strs/str[@id='wrath.subtitle.param.letterspacing'],				
						'&amp;sub_title=',$fl_title)"/>
					<xsl:with-param name="noflash">&lt;div class='subtitle-container'&gt;&lt;div class='reldiv'&gt;&lt;div class='sub-crest'&gt;&lt;/div&gt;&lt;div class='sub-orangetext' style='color: #<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.txtcolorshadow']"/>; font-size:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfontsize']"/>; font-family:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfont']"/>; margin: <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmargintopshadow']"/> 0 0 <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmarginleftshadow']"/>;'&gt;<xsl:value-of select="$fl_title"/>&lt;/div&gt;&lt;div class='sub-orangetext' style='color: #<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.txtcolor']"/>; font-size:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfontsize']"/>; font-family:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfont']"/>; margin: <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmargintop']"/> 0 0 <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmarginleft']"/>;'&gt;<xsl:value-of select="$fl_title"/>&lt;/div&gt;&lt;/div&gt;&lt;/div&gt;</xsl:with-param>
				</xsl:call-template>
</xsl:template>


<!-- Sub Page Contents  -->

<xsl:template name="pagecontents">

</xsl:template>


<xsl:template name="subpage">
	<xsl:param name="subtitlename" />
	<div class="sub-header-top">
		<xsl:call-template name="wrathlogo-subpage"/>	
	</div>
	<div class="sub-header-left" />
	<div class="sub-contents-container">
		<div class="sub-wood-top">
			<div class="sub-title">		
				<xsl:call-template name="flash">
					<xsl:with-param name="id" select="'flashsubtitle'"/>
					<xsl:with-param name="src" select="concat($loc/strs/str[@id='wrath.base'],'flash/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fglobal.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fsubtitle.swf&amp;reason=external-or-uncollected-resource')"/>
					<xsl:with-param name="wmode" select="'transparent'"/>
					<xsl:with-param name="width" select="'814'"/>
					<xsl:with-param name="height" select="'170'"/>
					<xsl:with-param name="base" select="concat($baseurl,'flash/global')"/>
					<xsl:with-param name="bgcolor" select="'#000000'"/>
					<xsl:with-param name="quality" select="'autohigh'"/>
					<xsl:with-param name="flashvars" select="concat(
						'&amp;flang=',$lang,
						'&amp;sub_fontsize=',$loc/strs/str[@id='wrath.subtitle.param.fontsize'],
						'&amp;sub_deltax=',$loc/strs/str[@id='wrath.subtitle.param.deltax'],
						'&amp;sub_deltay=',$loc/strs/str[@id='wrath.subtitle.param.deltay'],
						'&amp;sub_x=',$loc/strs/str[@id='wrath.subtitle.param.x'],
						'&amp;sub_y=',$loc/strs/str[@id='wrath.subtitle.param.y'],
						'&amp;subtxtcolor=',$loc/strs/str[@id='wrath.subtitle.param.txtcolor'],
						'&amp;sub_letterspacing=',$loc/strs/str[@id='wrath.subtitle.param.letterspacing'],				
						'&amp;sub_title=',$subtitlename)"/>
					<xsl:with-param name="noflash">&lt;div class='subtitle-container'&gt;&lt;div class='reldiv'&gt;&lt;div class='sub-crest'&gt;&lt;/div&gt;&lt;div class='sub-orangetext' style='color: #<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.txtcolorshadow']"/>; font-size:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfontsize']"/>; font-family:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfont']"/>; margin: <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmargintopshadow']"/> 0 0 <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmarginleftshadow']"/>;'&gt;<xsl:value-of select="$subtitlename"/>&lt;/div&gt;&lt;div class='sub-orangetext' style='color: #<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.txtcolor']"/>; font-size:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfontsize']"/>; font-family:<xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashfont']"/>; margin: <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmargintop']"/> 0 0 <xsl:value-of select="$loc/strs/str[@id='wrath.subtitle.param.noflashmarginleft']"/>;'&gt;<xsl:value-of select="$subtitlename"/>&lt;/div&gt;&lt;/div&gt;&lt;/div&gt;</xsl:with-param>
				</xsl:call-template>
			</div>		
		</div>
		<div class="sub-wood-container">
			<div class="sub-wood-contents">
				<div class="sub-text-container">
					<xsl:call-template name="pagecontents"/>
				</div>				
			</div>
		</div>
	</div>
	<div class="sub-header-right" />
	<div class="sub-wood-footer" />
	<div class="sub-footer">		
		<div class="blizzlogocontainer">
			<xsl:call-template name="blizzardlogo"/>			
		</div>
	</div>		
	
	
</xsl:template>


<!--  Localization Ordering Template  -->
<xsl:template name="stringorder">
<xsl:param name="orderid"/>
<xsl:param name="datainsert1"/>
<xsl:param name="datainsert2"/>
<xsl:param name="datainsert3"/>
<xsl:param name="datainsert4"/>


<xsl:for-each select="$loc/strs/order[@id=$orderid]/str">
<xsl:variable name="nodecount" select="count($loc/strs/order[@id=$orderid]/str)"/>
<xsl:variable name="positionNum" select="position()"/>
        <xsl:choose>
            <xsl:when test="@id">
                <xsl:variable name="comparestring" select="@id"/>   
                <xsl:value-of select="../../str[@id=$comparestring]"/>
            </xsl:when>
            <xsl:when test="@select='datainsert1'">
                <xsl:value-of select="$datainsert1"/>
            </xsl:when>
            <xsl:when test="@select='datainsert2'">
                <xsl:value-of select="$datainsert2"/>
            </xsl:when>
            <xsl:when test="@select='datainsert3'">
                <xsl:value-of select="$datainsert3"/>
            </xsl:when>
            <xsl:when test="@select='datainsert4'">
                <xsl:value-of select="$datainsert4"/>
            </xsl:when> 
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="$positionNum&lt;$nodecount and @space">&#160;</xsl:when>
        </xsl:choose>
</xsl:for-each>
    
</xsl:template>



<!-- Blizzard Entertainment Logo  -->

<xsl:template name="blizzardlogo">
	<div class="blizzlogo"><a href="{$loc/strs/str[@id='wrath.legal.blizzardlogolink']}"></a></div>
	<div class="legalcontainer">
    <div id="wowcomlink"><span style="font-size:11px;"><a href="/WOW-Encyclopedia-Deployable-Archive/index.xml.html"><img src="/WOW-Encyclopedia-Deployable-Archive/wrath/images/layout/backarrow.gif" width="24" height="24" border="0" style="vertical-align:middle;"/> <xsl:value-of select="$loc/strs/str[@id='wrath.labels.returnlink']"/></a></span></div>
		<div style="margin: 0 0 12px;">
			<a href="{$loc/strs/str[@id='wrath.labels.jobs.link']}" class="link-jobs"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.jobs.bottom']"/></a>
		</div>
        
		<a href="{$loc/strs/str[@id='wrath.legal.onlineprivacylink']}"><xsl:value-of select="$loc/strs/str[@id='wrath.legal.onlineprivacy']"/></a>
		<br />
		<a href="{$loc/strs/str[@id='wrath.legal.blizzardrightslink']}"><xsl:value-of select="$loc/strs/str[@id='wrath.legal.blizzardrights']"/></a>
		<br />	
		<div class="copyrights">	
			<xsl:value-of select="$loc/strs/str[@id='wrath.legal.copyrights']"/>
		</div>
	</div>
</xsl:template>


</xsl:stylesheet>
