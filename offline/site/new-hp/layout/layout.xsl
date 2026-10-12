<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html"/>

<xsl:template match="@*|node()">
   <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
   </xsl:copy>
</xsl:template>
 


<!-- ######## Page Layout Template ################################################ -->
<xsl:template match="page">

<html>
<head>
	<title><xsl:value-of select='@title'/></title>  

	<style type="text/css" media="screen">
		@import "/new-hp/css/loader_screen.css";
		@import "/shared/global/menu/topnav/topnav.css";
	</style>

	<script type="text/javascript">
		var scriptsLoaded=0;
		if(document.location.href.indexOf("worldofwarcraft.com") != -1) document.domain = "worldofwarcraft.com";
		try {
 		 document.execCommand("BackgroundImageCache", false, true);
	} catch(err) {}
	</script>
	
  	<xsl:choose>
	<!-- Includes/code called only on xml pages-->
      <xsl:when test="@type = 'front' or @type = 'xml'">	
			<script type="text/javascript" src = "/shared/wow-com/includes-client/detection.js"></script>
			<script type="text/javascript">
				scriptsLoaded=1;
			</script>		
			<script type="text/javascript" src="/new-hp/js/functions.js"></script>
			<script type="text/javascript" src="/new-hp/js/p7_eqCols2_10.js"></script>
			<!--<base target="_top"/>-->

	  </xsl:when>
	 </xsl:choose>

	<!-- Opera/Safari always need these loaded-->
	<script language = "javascript">
	//<![CDATA[
	var agt=navigator.userAgent.toLowerCase();
	var iePos  = appVer.indexOf('msie');
	var is_opera = (agt.indexOf("opera") != -1);
	var is_ie   = ((iePos!=-1) && (!is_opera));
	var is_safari = ((agt.indexOf('safari')!=-1)&&(agt.indexOf('mac')!=-1))?true:false;
	if((is_opera || is_safari) && scriptsLoaded){
	 	document.write("<script language=JavaScript src="/shared/wow-com/includes-client/detection.js" />");
	 	document.write("<script type=text/javascript src="/new-hp/js/functions.js" />");
		document.write("<script type=text/javascript src="/new-hp/js/p7_eqCols2_10.js" />");		
	}
	//]]>
	</script>
		
	<!-- Browser Specific CSS -->
	<script language = "javascript">
	//<![CDATA[
	if (is_ie)
		document.write('<link rel="stylesheet" type="text/css" href="/new-hp/css/additional_win_ie.css" media="screen, projection" />');

	if(is_opera)
		document.write('<link rel="stylesheet" type="text/css" href="/new-hp/css/additional_opera.css" media="screen, projection" />');
	//]]> 
	</script>
	
	<script src="/new-hp/js/screenie.js"></script>
	<link rel="stylesheet" href="/new-hp/js/screenie.css"/>   

    <link rel="alternate" type="application/rss+xml"  href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Frss.xml&reason=invalid-overlay-or-uncollected-site-resource" title="World of Warcraft Community Site"/>
</head>
<body>
<div id="shared_topnav"><script>global_nav_lang = "";</script><script src="/shared/global/menu/topnav/buildtopnav.js"></script></div>
<a name="pagetop"></a>
  	
	<xsl:choose>
	<!-- Includes/code called only the front page -->
      <xsl:when test="@type = 'front'">
	  	<script type='text/javascript' src="/new-hp/js/countryMenu.js"></script>
		<script type='text/javascript' src="/new-hp/js/menu132_com.js"></script>
		<script language = "javascript">operaBool=1;</script>
		<script language = "javascript">
			//code that fixes the issue with the bottom iron border in Safari
			if(is_safari)
				addEvent(window, 'load', fixFrame);
			function fixFrame() {document.getElementById("ironFrame").style.marginTop="-20px";}
		</script>
      </xsl:when>
	  <!-- Includes/code called on all others pages -->
	  
      <xsl:otherwise>
	  	<link rel="stylesheet" type="text/css" href="/new-hp/css/additional_html_css.css" media="screen, projection" />
		<link rel="stylesheet" type="text/css" href="/shared/wow-com/includes-client/wow.css" id = "pageStyle"/>
		<!--<script language="JavaScript" src = "/shared/wow-com/includes-client/wow.js"></script>-->
      </xsl:otherwise>  
    </xsl:choose>
	
<div id="bg-top"></div>

<center>
<table cellspacing = "0" cellpadding = "0" border = "0"><tr><td>
<div id="hp">

	<!--Search Box-->
    <div style="position:relative; z-index:999999;">
	<div class="top-nav">
		
	
	<form name = "topSearch" id = "topSearch" onSubmit="return searchCall()">

	<div id = "searchBoxContainer">
		<div class="searchBoxLeft"></div>
		<div class="searchBoxBg">
			<ul>
				<li class="searchBoxInput"><input name = "searchBox" id="searchBox" class="searchBoxForm"/></li>
				<li class="searchBoxSelect">
					<select id="searchType" name="searchType" class="searchBoxForm">
						<option value="site">Community Site</option>
						<option value="encyclopedia">Encyclopedia</option>
						<option value="ingamesupport">In-game Support</option>
						<option value="techsupport">Tech Support</option>
					</select>
				</li>				
				<li class="searchBoxButton">
					<xsl:call-template name="redButton">
						<xsl:with-param name="id" select="'searchBoxButton'"/>
						<xsl:with-param name="label" select="'Search'"/>
						<xsl:with-param name="width" select="'55'"/>
						<xsl:with-param name="xCoord" select="'8'"/>
						<xsl:with-param name="url" select="'javascript:searchCall()'"/>
					</xsl:call-template>
				</li>
				
			</ul>
		</div>
		<div class="searchBoxRight"></div>
		
	</div>				
				
	</form>
	
		
	</div>
	</div>
	<!--End Search Box-->


<div class="top-nav-container"> 



	<div style="position: absolute; right: 170px; top: 38px; z-index:999999">
		<div id="countryDropDown" style="z-index:999999999;"></div>
	</div>	
	<!--
	<div class="theme-container">		
		<div class="select-theme"></div>
			<div class="alliance"><a href="#" onclick="setActiveStyleSheet('', 1);return false;"><img src="/new-hp/images/pixel.gif" height="25" width="38" border="0" title="Select Alliance Theme" /></a></div>
			<div class="horde"><a href="#" onclick="setActiveStyleSheet('orc', 1);return false;"><img src="/new-hp/images/pixel.gif" height="50" width="38" border="0" title="Select Horde Theme" /></a></div>
	</div>
	-->
    <div style="position: absolute; top: 0; left: 0; z-index: 20002;">
	
	<xsl:choose>
	<!-- Includes/code called only the front page -->
      <xsl:when test="@type = 'front'">
			<div id="wow-logo">
					<a href="/index.xml"><img src="/new-hp/images/pixel.gif" width="252" height="103" alt="wowlogo" title="World of Warcraft" /></a></div>		
      </xsl:when>
	  <!-- Includes/code called on all others pages -->
      <xsl:otherwise>
			<div id="wow-logo2">
				<a href="/index.xml"><img src="/new-hp/images/pixel.gif" width="252" height="103" alt="wowlogo" title="World of Warcraft" /></a>
			</div>
      </xsl:otherwise>
    </xsl:choose>
    </div>
	
   
</div>
<div>

    <div id="hpWrapper">
		<table cellspacing = "0" cellpadding = "0" border = "0" width = "100%"><tr><td valign = "top">
        <div id="navWrapper">
            <div id="nav"><div id = "ne-top-left"></div><div id = "ne-center"></div><div id = "ne-bottom-left"></div><div id = "ne-nav-bg"></div><div id = "ne-top-right"></div>
			
                <div id="leftMenu">
					<div id="leftMenuContainer">
					<xsl:apply-templates select="document('/new-hp/layout/menu.xml')/menu/category" />
					</div>
                </div>
            </div>
            <div style="clear: both;"></div>
        </div>
		</td>
		<td valign = "top">
        <div id="mainWrapper">
            <div id="main">
                
				<div id="main-content-wrapper">
                    <div id="main-content">
						<table border="0" cellpadding="0" cellspacing="0"><tr><td>
						<div id="main-top"><div><div></div></div></div>
						</td></tr>
						<tr><td>
                        <div id="contentPadding">
                            <div id="cnt">
                                
              
  
                                            <div id="cnt-wrapper">
											  	<div id = "contentContainer">
												
													<xsl:apply-templates />
													
												</div>
                                            </div>

       
                                
                            </div>
					<div style="clear: both; font-size: 1px;">&#160;</div> <!-- netscape fix -->
						<center>
							<div id="copyright">
								<span class="esrb">
									<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.blizzard.com%2Fprivacy.shtml&reason=external-or-uncollected-resource" target="_blank">
									<img src="/new-hp/images/ectppsvivendi.gif" width="117" height="43" border="0" alt="esrb" title="ESRB Privacy Certified" /></a></span>
								<span class="rating">
									<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.esrb.org%2Fesrbratings_guide.asp&reason=external-or-uncollected-resource" target="_blank">
									<img src="/shared/wow-com/images/icons/esrb/teen-desc.gif" width="125" height="70" border="0" alt="rating" title="Rated Teen" /></a></span>
								<span class="esrb-caution">
									<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.esrb.org%2Fesrbratings_guide.asp&reason=external-or-uncollected-resource" target="_blank">
									<img src="/shared/wow-com/images/icons/esrb/content-warning.gif" width="147" height="44" border="0" alt="esrb-caution" title="ESRB Notice" /></a></span>
									<span class="textlinks">

									<small>
									<a href = "/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.blizzard.com%2Fprivacy.shtml&reason=external-or-uncollected-resource" target="_blank">Online Privacy Policy</a> | 
									<a href = "/legal/index.html">Legal Documents</a> | 
									<a href = "/policy/index.html">Policies</a>
									<br/>&#169;2008 Blizzard Entertainment, Inc. All rights reserved.</small>

								</span>
							</div><!-- end copyright -->
						</center>
					</div>
						<map name="bot_blizzlogo_Map">
						<area shape="rect" alt="Blizzard.com" coords="8,8,86,54" href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.blizzard.com&reason=external-or-uncollected-resource"/>
						</map>
						</td></tr>
						<tr><td>
						<div id="main-bottom"><div><div><div id="blizzlogo-bot" style="background:none !important;"><img src = "/new-hp/images/new/bot-blizzlogo.gif" width = "97" height = "57" border = "0" usemap = "#bot_blizzlogo_Map" alt = "Blizzard.com" style="position: absolute; top: 14px; left: 45%;"/></div></div></div></div>
                    	</td></tr></table>
					</div>
                </div>
               
                <div style="position:relative;"><div id="statue-left"></div><div id="statue-right"></div><img src="/new-hp/images/burningcrusade/statue-left.jpg" alt="statue" style="position: absolute; top: -445px; left: -243px;" id="statue-main" /></div>
            </div><!-- /main -->
			
        </div><!-- /mainWrapper -->
		</td>
		</tr></table>
    </div><!-- /hpWrapper -->
</div>
</div><!-- /hp -->
</td></tr></table>
</center>
<div id="ironFrame"></div>

<!--iframes that call the left side menus-->
<iframe src = "/new-hp/menus/menu1.htm" width = "0" height = "0" frameborder = "0" id="menuIframe1" name="menuIframe1"></iframe>
<iframe src = "/new-hp/menus/menu2.htm" width = "0" height = "0" frameborder = "0" id="menuIframe2" name="menuIframe2"></iframe>
<iframe src = "/new-hp/menus/menu3.htm" width = "0" height = "0" frameborder = "0" id="menuIframe3" name="menuIframe3"></iframe>
<iframe src = "/new-hp/menus/menu4.htm" width = "0" height = "0" frameborder = "0" id="menuIframe4" name="menuIframe4"></iframe>
<iframe src = "/new-hp/menus/menu5.htm" width = "0" height = "0" frameborder = "0" id="menuIframe5" name="menuIframe5"></iframe>
<iframe src = "/new-hp/menus/menu6.htm" width = "0" height = "0" frameborder = "0" id="menuIframe6" name="menuIframe6"></iframe>
<iframe src = "/new-hp/menus/menu7.htm" width = "0" height = "0" frameborder = "0" id="menuIframe7" name="menuIframe7"></iframe>
<iframe src = "/new-hp/menus/menu8.htm" width = "0" height = "0" frameborder = "0" id="menuIframe8" name="menuIframe8"></iframe>
<div id = "pageEnd"></div>

<script type="text/javascript" src="/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.google-analytics.com%2Fga.js&reason=external-or-uncollected-resource"></script>
<script type="text/javascript">
var pageTracker = _gat._getTracker("UA-544112-18");
pageTracker._setDomainName("worldofwarcraft.com");
pageTracker._initData();
pageTracker._trackPageview();
</script>

</body>
</html>


</xsl:template>


<!-- ######## Left Side Menu ################################################ -->
<xsl:template match="menu/category">
	<xsl:variable name="positionNum">
		<xsl:number value="position()" format="1" />
	</xsl:variable>
   
                    <div id="{@name}"><!--This div id is used by the menu script to place the dynamic menus-->
						
                        <div id="{@name}-button" class="menu-button-off" onclick="javascript:toggleNewMenu({$positionNum}-1);">
                            <span id="{@name}-icon" class="{@name}-icon-off">&#160;</span>
                            <a id="{@name}-header" class="{@name}-header-off"><em>Game Guide</em></a>
                            <a id="{@name}-collapse"></a>
                            <span class="menuEntry-rightBorder"></span>
						</div>
						
                        <div id="{@name}-inner">
							
                            <script type="text/javascript">
								//This script handles the default status of each menu based on the user's cookies
								targ = "<xsl:value-of select='@name'/>"; targ = targ.replace("menu","");
                                if (menuCookie[<xsl:value-of select='$positionNum'/>-1] == 0) 
								{ foldMenu(targ,1); } 
								else { foldMenu(targ,2); }

                            </script>

						
                            <div class="leftMenu-cont-top"></div>
							<div class="leftMenu-cont-mid">
							    <div class="m-left">
                                    <div class="m-right">
                                        <div class="leftMenu-cnt">
                                            <ul class="mainNav">
												<div id = "menuFiller{$positionNum}" style = "position:relative;">
												
												<xsl:for-each select="current()/menuItem">
													<xsl:call-template name = "menuFiller"/>
												</xsl:for-each>
												</div>
                                			</ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="leftMenu-cont-bot"></div>
                        </div>
                    </div>   
   
</xsl:template>

<!-- ######## Menu Filler Template (draws top level menu item to display before dynamic menu is drawn) ################################################ -->
<xsl:template name="menuFiller">
	<xsl:variable name="positionNum">
		<xsl:number value="position()" format="1" />
	</xsl:variable>
  	<xsl:choose>
      <xsl:when test="@indent = 'yes'"><!--Alternate template for indented menu items-->
		<div style = "font-weight:bold; text-decoration: none; font-family:arial,comic sans ms,technical; font-size: 11px; position: relative; left: -3px; background-image:url('/new-hp/images/menu/mainmenu/bullet-trans-indent-bg.gif'); width:139px; height:15px; _height:18px; padding:0px; margin:0px; _margin-bottom:-3px; border:0px; padding-left:10px;">&#160;&#160;<a href = "/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2F%7B%40url%7D&reason=invalid-overlay-or-uncollected-site-resource" class="menuFiller"><xsl:value-of select='@name'/></a></div>
      </xsl:when>
      <xsl:otherwise>
		<div style = "font-weight:bold; text-decoration: none; font-family:arial,comic sans ms,technical; font-size: 11px; position: relative; left: -3px; background-image:url('/new-hp/images/menu/mainmenu/bullet-trans-bg.gif');        width:139px; height:15px; _height:18px; padding:0px; margin:0px; _margin-bottom:-3px; border:0px; padding-left:10px;"><a href = "/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2F%7B%40url%7D&reason=invalid-overlay-or-uncollected-site-resource" class="menuFiller"><xsl:value-of select='@name'/></a></div>
      </xsl:otherwise>
    </xsl:choose>


</xsl:template>


<!-- ######## News Post Tempate (draws front page news) ################################################ -->
<xsl:template match="newsposts" >
	<xsl:call-template name="newsposts">
		<xsl:with-param name="xmlfeed" select="@xmlfeed"/>
	</xsl:call-template>
</xsl:template>



<xsl:template name="newsposts">
<xsl:param name="xmlfeed"></xsl:param>

<div class="module-container">

					
				  	<xsl:choose><!-- handles alternating colors for news items-->
				      	<xsl:when test="$xmlfeed">						
							<xsl:apply-templates select="document($xmlfeed)/rss/channel/item" />
						</xsl:when>
    					<xsl:otherwise>
							<xsl:apply-templates select="item" />
						</xsl:otherwise>
					</xsl:choose>
					

</div><!-- /module-container/ -->

		 
</xsl:template>


  
<xsl:template match="item">
	<xsl:variable name="positionNum">
		<xsl:number value="position()" format="1" />
	</xsl:variable>

  	<xsl:choose><!-- handles alternating colors for news items-->
      <xsl:when test="$positionNum mod 2 = 1">
			<xsl:call-template name = "newsPostDraw">
				<xsl:with-param name="hilite" select="'alt'"></xsl:with-param>
				<xsl:with-param name="positionNum" select="$positionNum"></xsl:with-param>
			</xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
			<xsl:call-template name = "newsPostDraw">
				<xsl:with-param name="hilite" select="''"></xsl:with-param>
				<xsl:with-param name="positionNum" select="$positionNum"></xsl:with-param>
			</xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>

</xsl:template>



<xsl:template name="newsPostDraw">
	<xsl:param name="hilite" />
	<xsl:param name="positionNum" />
	
	
					<script type="text/javascript">
						var postId<xsl:value-of select='$positionNum'/>="<xsl:value-of select='pubDate'/>-<xsl:value-of select='string-length()'/>"
					</script>
					
<!-- ##### News Item 1 Expanded ##### -->		
					
					<div id="news{pubDate}-{string-length()}" class="news-expand">
								<div class="news-border-left"></div>
								<div class="news-border-right"></div>
						<div class="news-listing">
						<div class="hoverContainer" onmouseover="javascript:this.style.background="#EEDB99"" onmouseout="javascript:this.style.background="/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Fnone&reason=invalid-overlay-or-uncollected-site-resource"" onclick="javascript:toggleEntry('{pubDate}-{string-length()}','{$hilite}')">
						  <div>
						    <div class="news-top">
							<ul>
								<li class="item-icon">
								
								<xsl:choose>
									<xsl:when test="icon">
										<img src="/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fimages%2Ficons%2F%7Bicon%7D.gif&reason=invalid-overlay-or-uncollected-site-resource" alt="new-post" border="0" />
									</xsl:when>
									<xsl:otherwise>
										<img src="/new-hp/images/icons/news-wow.gif" alt="new-post" border="0" />
									</xsl:otherwise>
								</xsl:choose>
								</li>
								<li class="news-entry">
									<h1><a href="javascript:dummyFunction();"><xsl:value-of select='title'/></a></h1>
									<span class="user">Posted by: </span><small><xsl:value-of select='author'/><span class="user">|</span>&#160;<span class="posted-date"><xsl:value-of select='pubDate'/></span></small>
								</li>
								<li class="news-entry-date">
									<span><strong><xsl:value-of select='pubDate'/></strong></span>
								</li>
								<li class="news-toggle"><a href="javascript:toggleEntry('{pubDate}-{string-length()}','{$hilite}')"><img src="/v2/images/pixel.gif" alt="" /></a></li>
							</ul>
							</div><!-- /news-top/ -->
						  </div>
						</div>
						</div><!-- /news-listing/ -->
						<div class="news-item">
							<blockquote>
								<dl>
									<dd>
										<ul>
											<li>
												<div class="letter-box0"></div>
												<div class="blog-post">
													<xsl:apply-templates select='description'/>
												</div><!-- /blog-post/ -->								
											</li>
										</ul>
									</dd>
								</dl>
							</blockquote>
						</div><!-- /news-item/ -->
					</div>
					<script type="text/javascript">
					
					
					//handles default statuses of each news post based on cookie
					var position = <xsl:value-of select='$positionNum'/>;
					var localId = postId<xsl:value-of select='$positionNum'/>;
					var cookieState = getcookie(localId);
					var defaultOpen = "<xsl:value-of select='defaultOpen'/>";
					

					//<![CDATA[		
					if ((cookieState == 1) || (position==1 && cookieState!='0') || (defaultOpen == 1 && cookieState!='0')) {
					//]]>
					} else {
						document.getElementById("news"+localId).className = "news-collapse"+"<xsl:value-of select='$hilite'/>";				
					}


					</script>			
					

</xsl:template>
   


<!-- ######## Red Buttons ################################################ -->
<xsl:template match="redButton" >
	<xsl:call-template name="redButton">
			<xsl:with-param name="label" select="@label"/>
			<xsl:with-param name="url" select="@url"/>
			<xsl:with-param name="width" select="@width"/>
			<xsl:with-param name="xCoord" select="@xCoord"/>
			<xsl:with-param name="slant" select="@slant"/>
			<xsl:with-param name="id" select="@id"/>
	</xsl:call-template>
</xsl:template>

<xsl:template name="redButton">
   <xsl:param name="label"></xsl:param>
   <xsl:param name="url">#</xsl:param>
   <xsl:param name="width">100</xsl:param>
   <xsl:param name="height">22</xsl:param>
   <xsl:param name="xCoord">4</xsl:param>
   <xsl:param name="slant">0</xsl:param>
   <xsl:param name="id">redButton</xsl:param>

		<div class="redButton-container">
		<div class="leftNopadd">
			
				<xsl:choose>
		            <xsl:when test="$slant = 1">
						<img src = "/new-hp/images/button-left-slant.gif" width = "10" height = "{$height}"/>
					</xsl:when>
					<xsl:otherwise>
						<img src = "/new-hp/images/button-left.gif" width = "5" height = "{$height}"/>
					</xsl:otherwise>
				</xsl:choose>			
			
				
		</div>		
		<div class="leftNopadd rdbtn" style="" >
        <a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2F%7B%24url%7D&reason=invalid-overlay-or-uncollected-site-resource" style="width:{$width}px; line-height:21px;"><xsl:value-of select="$label"/></a>
        <div class="rdbtn_sh" style="width:{$width}px; line-height:21px;"><xsl:value-of select="$label"/></div>
<!--			<script language="VBScript">
				Sub <xsl:value-of select='$id'/>Flash_FSCommand(ByVal command, ByVal args)
				    call <xsl:value-of select='$id'/>Flash_DoFSCommand(command, args)
				end sub
			</script>
			<script language = "javascript">
				function <xsl:value-of select='$id'/>Flash_DoFSCommand(command, args) { 
					if (args.indexOf('javascript:')>=0) {
						var javascriptCalls = args.split(":");
						eval(javascriptCalls[1]);
					}else{
						document.location.href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Fargs&reason=invalid-overlay-or-uncollected-site-resource"		
					}
				}
			</script>
			<xsl:call-template name="flash">
					<xsl:with-param name="id" select="$id"/>
					<xsl:with-param name="src" select="'/new-hp/flash/button.swf'"/>
					<xsl:with-param name="width" select="$width"/>
					<xsl:with-param name="height" select="$height"/>
					<xsl:with-param name="flashvars" select="concat('textLabelString=',$label,'&#38;xCoord=',$xCoord,'&#38;canvasWidth=',$width,'&#38;theURL=',$url)"/>
					<xsl:with-param name="noflash" select="concat('&lt;a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2F%2C%24url%2C&reason=invalid-overlay-or-uncollected-site-resource"&gt;&lt;img src = "/new-hp/images/learnmore.gif" border=0 alt=',$label,'&gt;&lt;/a&gt;')"></xsl:with-param>
			</xsl:call-template>
-->
		</div>
		<div class="leftNopadd">
					<img src = "/new-hp/images/button-right.gif" width = "7" height = "{$height}"/>
		</div>
		</div>

</xsl:template>




<!-- ######## Small Cap ################################################ -->
<xsl:template match="cap" >
	<xsl:call-template name="cap">
			<xsl:with-param name="letter"><xsl:apply-templates /></xsl:with-param>
			<xsl:with-param name="align" select="@align"/>
	</xsl:call-template>
</xsl:template>

<xsl:template name="cap">
   <xsl:param name="letter" />
   <xsl:param name="align">left</xsl:param>
 		<img src = "/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Fsmallcaps%2Fplain%2F%7B%24letter%7D.gif&reason=invalid-overlay-or-uncollected-site-resource" align="{$align}" style="margin-right: 4px;" />
</xsl:template>



<!-- ######## Tooltip Template ################################################ -->
<xsl:template name="toolTipInclude">


<!--
progid:DXImageTransform.Microsoft.AlphaImageLoader(enabled=true, sizingMethod=scale src="/shared/wow-com/images/backgrounds/blue-bg.png") 
-->
<style type="text/css">

#contents{
visibility: hidden;
position: absolute;
Z-INDEX: 999999;
width: 5px;
background-color: #010721;
filter:progid:DXImageTransform.Microsoft.Alpha(opacity=85) progid:DXImageTransform.Microsoft.Shadow(color=#000000, direction=135, strength=3);
}


#dynamicTooltip{
visibility: hidden;
position: absolute;
Z-INDEX: 999999;
}

#tooltipText{
visibility: hidden;
color: #ffffff;
font-family: verdana, arial, sans-serif;
font-size:8pt;
font-weight:normal;
padding: 4px;
white-space:nowrap;

}

.trans_div {

/* This is an IE filter command. Other browsers will ignore it */
/* It goes into the trans_div class */


}

/* Square bracketed class styles are usable non-IE type browsers */
/* This is a seperate css entry, not part of the original trans_div class */

.trans_div[class] {
background-image:url(/shared/wow-com/images/backgrounds/blue-bg.png);
}

</style>


<div id="contents">


<table cellspacing = "0" cellpadding = "0" border = "0" width = "100%">
<tr>
	<td><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
	<td bgcolor = "#000000"></td>
	<td><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
</tr>
<tr>
	<td bgcolor = "#000000"></td>
	<td>
	
			<table cellspacing = "0" cellpadding = "0" border = "0" width = "100%">
			  <tr>
				<td width = "1" height = "1" bgcolor = "#000000"></td>
				<td bgcolor = "#D5D5D7" height = "1"><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
				<td width = "1" height = "1" bgcolor = "#000000"></td>
			  </tr>
			  <tr>
				<td bgcolor = "#A5A5A5" width = "1"><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
				<td valign = "top" class = "trans_div"><div id="tooltipText"></div></td> 
				<td bgcolor = "#A5A5A5" width = "1"><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
			  </tr>
			  <tr>
				<td width = "1" height = "1" bgcolor = "#000000"></td>
				<td bgcolor = "#4F4F4F"><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "2"/></td>
				<td width = "1" height = "1" bgcolor = "#000000"></td>
			  </tr>
			</table>
	
	</td>
	<td bgcolor = "#000000"></td>
</tr>
<tr>
	<td><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
	<td bgcolor = "#000000"></td>
	<td><img src = "/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
</tr>
</table>

			

</div>

<script type="text/javascript" src="/shared/third-party/tooltip.js"></script>

</xsl:template>


<xsl:template match="toolTipContents" >
	<xsl:call-template name="toolTipContents">
			<xsl:with-param name="id" select="@id"></xsl:with-param>
			<xsl:with-param name="contents"><xsl:apply-templates /></xsl:with-param>
	</xsl:call-template>
</xsl:template>



<xsl:template name="toolTipContents">
	<xsl:param name="id" />
   	<xsl:param name="contents" />
		<style type="text/css">
			#<xsl:value-of select='$id'/>{visibility: hidden;position: absolute;Z-INDEX: 999999;}		
		</style>
		<div id = "{$id}"><xsl:apply-templates /></div>
</xsl:template>

   
<xsl:template match="toolTip" >
	<xsl:call-template name="toolTip">
			<xsl:with-param name="id" select="@id"></xsl:with-param>
			<xsl:with-param name="contents"><xsl:apply-templates /></xsl:with-param>
	</xsl:call-template>
</xsl:template>

<xsl:template name="toolTip">
	<xsl:param name="id" />
   	<xsl:param name="contents" />
		<span onMouseover="ddrivetip('~{$id}');" onMouseout="hideddrivetip();"><xsl:apply-templates /></span>
</xsl:template>
   


<!-- ######## Flash Template (used for flash objects) ################################################ -->
<xsl:template match="flash" >
	<xsl:call-template name="flash">
			<xsl:with-param name="id" select="@id"></xsl:with-param>
			<xsl:with-param name="width" select="@width"></xsl:with-param>
			<xsl:with-param name="height" select="@height"></xsl:with-param>	
			<xsl:with-param name="src" select="@src"></xsl:with-param>
			<xsl:with-param name="quality" select="@quality"></xsl:with-param>
			<xsl:with-param name="base" select="@base"></xsl:with-param>
			<xsl:with-param name="flashvars" select="@flashvars"></xsl:with-param>
			<xsl:with-param name="bgcolor" select="@bgcolor"></xsl:with-param>
			<xsl:with-param name="menu" select="@menu"></xsl:with-param>
			<xsl:with-param name="wmode" select="@wmode"></xsl:with-param>

	</xsl:call-template>
</xsl:template>



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
	<xsl:param name="noflash" select="current()"/>
	

		<div id="{$id}"></div>


		<script language = "javascript">

			printFlash("<xsl:value-of select='$id'/>", "<xsl:value-of select='$src'/>", "<xsl:value-of select='$wmode'/>", "<xsl:value-of select='$menu'/>", "<xsl:value-of select='$bgcolor'/>", "<xsl:value-of select='$width'/>", "<xsl:value-of select='$height'/>", "<xsl:value-of select='$quality'/>", "<xsl:value-of select='$base'/>", "<xsl:value-of select='$flashvars'/>", "<xsl:value-of select='$noflash'/>")
		
		</script>	
	
</xsl:template>

<!-- ######## Red Banner (Used at the top of pages) ################################################ -->
<xsl:template match="redBanner">
	<xsl:call-template name="redBanner"/>
</xsl:template>

<xsl:template name="redBanner">
	<xsl:param name="label" />

	<div class = "redBannerBg">
		<div class = "redBannerLeft"></div>
		<div class = "redBannerLabel"><xsl:apply-templates/></div>
		<div class = "redBannerRight"></div>
	</div>
	
</xsl:template>


<xsl:template match="realmList">
	<xsl:call-template name="realmList"/>
</xsl:template>

<xsl:template name="realmList">
	<xsl:apply-templates select="document('/realmstatus/status.xml')/rs/r" />
</xsl:template>

<xsl:template match="r">
	<option value="{@n}"><xsl:value-of select="@n" /></option>
</xsl:template>

 
<!-- Begin Frost's Includes; SAFETY NOT GUARANTEED! -->

<xsl:template match="subBannerChapter">
  <xsl:call-template name="subBannerChapter">
    <xsl:with-param name="chapterTitle" select="@chapterTitle"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="subBannerChapter">
  <xsl:param name="chapterTitle"/>
  <div style="width:715px; height:29px; background:url('/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg') repeat-x; margin-bottom:-1px;">
    <div style="width:362px; height:29px; float:left; background:url('/shared/wow-com/images/headers/tabheader/tabheader-left.jpg') no-repeat;">
      <img src="/shared/wow-com/images/headers/tabheader/tabheader-left-left.jpg" border="0" align="left"/>
	  <h3 class = "guideTitle" style="margin-top:4px;"><xsl:value-of select="$chapterTitle"/></h3>
	</div>
	<div style="width:353px; height:29px; float:right; background:url('/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg') repeat-x;"></div>
  </div>
  <div class = "postContainerPlain" style="font-size:12px; border-top-width:0px;">
    <div class = "postBody">
	  <xsl:apply-templates/>
	</div>
  </div>
</xsl:template>


<xsl:template match="lorePhantomZone">
	<xsl:call-template name="lorePhantomZone">
	</xsl:call-template>
</xsl:template>

<xsl:template name="lorePhantomZone">
	<div id="phantomZone" style="display:none;">
		<div id="baseDiv" style="position:absolute; top:0; right:0; height:100%;">
			<div id="lorePopFrame" onClick="hideStuff();" class="lorePopFrameStyle">
				<center>
					<div id="loreShadowContainer" class="loreShadowContainerStyle">
						<div id="loreShadow" class="loreShadowStyle" onClick="hideStuff();"></div>

					</div>
					
					<div id="loreRootDiv" class="loreRootDivStyle" onMouseOver="hideMe = false;" onMouseOut="hideMe = true;">
						<div id="allContainer" class="allContainerStyle">
							<div id="loreDiv" class="loreStyle">
								<div id="loreText" class="loreTextStyle"></div>
								<div class="topBlenderStyle"></div>
							</div>
							<div class="bottomBlenderStyle" id="blender2"></div>
							<div id="topRight" class="topRightStyle"></div>
						</div>
						<div id="dragRail" class="dragRailStyle">
							<div style="position:relative; height:100%;">
								<div class="topScroller" onClick="scrollResolver(1)"></div>
								<div class="bottomScroller" onClick="scrollResolver(-1)"></div>						
							</div>
						</div>
						<div id="dragButton" class="draggerStyle" onMouseDown="dragStart(dragButtonZ);"></div>
						<div class="topLeftStyle"></div>
						<div class="topRightControl" onMouseOver="mouseMoveIn('topRight');" onMouseOut="mouseMoveOut('topRight');" onClick="hideMe = true; hideStuff(); mouseMoveOut('topRight');"></div>
					</div>
			
				</center>
			</div>
		</div>
	</div>
</xsl:template>

<xsl:template match="guideChapter">
  <xsl:call-template name="guideChapter">
    <xsl:with-param name="chapterTitle" select="@chapterTitle"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="guideChapter">
  <xsl:param name="chapterTitle"/>
  <div style="width:650px; height:29px; background:url('/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg') repeat-x; margin-bottom:-1px;">
    <div style="width:362px; height:29px; float:left; position:relative; background:url('/shared/wow-com/images/headers/tabheader/tabheader-left.jpg') no-repeat;">
      <img src="/shared/wow-com/images/headers/tabheader/tabheader-left-left.jpg" border="0" align="left"/>
	  	<h3 class = "guideTitle" style="margin-top:4px;"><xsl:value-of select="$chapterTitle"/></h3>
		</div>
    <div style="width:288px; position:relative; height:29px; float:left; background:url('/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg') repeat-x;">
	  	<img src="/shared/wow-com/images/headers/tabheader/tabheader-right.jpg" border="0" align="right" style="position:absolute; right:0px;"/>
		</div>
  </div>
  <div class = "postContainerPlain" style="font-size:12px; border-top-width:1px;">
    <div class = "postBody">
	  <xsl:apply-templates/>
	</div>
  </div>
</xsl:template>

<!-- thumbnail linking to the screenshot gallery -->
<xsl:template match="gallerythumb">
  <xsl:call-template name="gallerythumb">
    <xsl:with-param name="source" select="@src"/>
	<xsl:with-param name="align" select="@align"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="gallerythumb">
  <xsl:param name="source"/>
  <xsl:param name="align">left</xsl:param>
<script language="javascript" type="text/javascript">
  function setGalleryLink(thisScreenshot) { document.getElementById(thisScreenshot).href = "/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fimageviewer.html%3F%2C&reason=invalid-overlay-or-uncollected-site-resource"+ thisScreenshot.split("/ss")[0]+"/,"+ thisScreenshot.split("/ss")[1].replace(/-caption/,"") +","+ screenshotsTotal +","+ window.location.href; }
</script>
  <table border="0" cellpadding="0" cellspacing="0" align="{$align}">
    <tr>
	  <td width="8" style="background-image:url(/shared/wow-com/images/borders/screenshot/top-left.gif);"></td>
	  <td height="6" style="background-image:url(/shared/wow-com/images/borders/screenshot/top.gif);"></td>
	  <td width="9" style="background-image:url(/shared/wow-com/images/borders/screenshot/top-right.gif);"></td>
	</tr>
	<tr>
	  <td width="8" style="background-image:url(/shared/wow-com/images/borders/screenshot/left.gif); background-repeat:repeat-y;"></td>
	  <td><a id="{$source}" href="#" onMouseOver="setGalleryLink('{$source}');"><img src="/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2F%7B%24source%7D-thumb.jpg&reason=invalid-overlay-or-uncollected-site-resource" border="0" style="display:block;"/></a></td>
	  <td width="9" style="background-image:url(/shared/wow-com/images/borders/screenshot/right.gif); background-repeat:repeat-y;"></td>
	</tr>
    <tr>
	  <td width="8" style="background-image:url(/shared/wow-com/images/borders/screenshot/bot-left.gif);"></td>
	  <td height="11" style="background-image:url(/shared/wow-com/images/borders/screenshot/bot.gif);"></td>
	  <td width="9" style="background-image:url(/shared/wow-com/images/borders/screenshot/bot-right.gif);"></td>
	</tr>
	<tr>
	  <td colspan="3" align="center"><span><a id="{$source}-caption" href="#" onMouseOver="setGalleryLink('{$source}-caption');"><xsl:apply-templates/></a></span></td>
	</tr>
  </table>
</xsl:template>


<!-- thumbnail linking to a popup -->
<xsl:template match="popupthumb">
  <xsl:call-template name="popupthumb">
    <xsl:with-param name="source" select="@src"/>
		<xsl:with-param name="align" select="@align"/>
		<xsl:with-param name="width" select="@width"/>
		<xsl:with-param name="height" select="@height"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="popupthumb">
  <xsl:param name="source"/>
  <xsl:param name="width"/>
  <xsl:param name="height"/>
  <xsl:param name="align">left</xsl:param>
<script language="javascript" type="text/javascript">
  function setPopupLink(thisScreenshot,width,height) { document.getElementById(thisScreenshot).href = "javascript:popUpOmega('"+thisScreenshot.replace(/-caption/,'')+".jpg',"+width+","+height+");"; }
</script>
  <table border="0" cellpadding="0" cellspacing="0" align="{$align}">
    <tr>
	  <td width="8" style="background-image:url(/shared/wow-com/images/borders/screenshot/top-left.gif);"></td>
	  <td height="6" style="background-image:url(/shared/wow-com/images/borders/screenshot/top.gif);"></td>
	  <td width="9" style="background-image:url(/shared/wow-com/images/borders/screenshot/top-right.gif);"></td>
	</tr>
	<tr>
	  <td width="8" style="background-image:url(/shared/wow-com/images/borders/screenshot/left.gif); background-repeat:repeat-y;"></td>
	  <td><a id="{$source}" href="#" onMouseOver="setPopupLink('{$source}',{$width},{$height});"><img src="/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2F%7B%24source%7D-thumb.jpg&reason=invalid-overlay-or-uncollected-site-resource" border="0" style="display:block;"/></a></td>
	  <td width="9" style="background-image:url(/shared/wow-com/images/borders/screenshot/right.gif); background-repeat:repeat-y;"></td>
	</tr>
    <tr>
	  <td width="8" style="background-image:url(/shared/wow-com/images/borders/screenshot/bot-left.gif);"></td>
	  <td height="11" style="background-image:url(/shared/wow-com/images/borders/screenshot/bot.gif);"></td>
	  <td width="9" style="background-image:url(/shared/wow-com/images/borders/screenshot/bot-right.gif);"></td>
	</tr>
	<tr>
	  <td colspan="3" align="center"><span><a id="{$source}-caption" href="#" onMouseOver="setPopupLink('{$source}-caption',{$width},{$height});"><xsl:apply-templates/></a></span></td>
	</tr>
  </table>
</xsl:template>


<!-- ############ Encyclopedia Content Tag ############ -->

<xsl:template match="encyclopediacontent">
  <xsl:call-template name="encyclopediacontent">
		<xsl:with-param name="align" select="@align"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="encyclopediacontent">

	<style type="text/css">
		@import url(styles/stylesheet.css);
	</style>
		
	<script language="javascript" type="text/javascript" src="/info/encyclopedia/scripts/cascade.js"/>
	<script language="javascript" type="text/javascript" src="/info/encyclopedia/scripts/topic-list.js"/>
	<script language="javascript" type="text/javascript" src="/info/encyclopedia/scripts/link-generator.js"/>

<div class="bg">
	<div class="bgtop">
		<div id="bgtopleft" class="bgtopleft">
			<div class="bgbot">
				<div class="bgbotleft">
					
					<div class="menufloat">
						<div class="encyclopedia-menu">
							<div id="bufferDiv" style="display:none;"></div>
							<div id="dragMenuContainer" class="menuContainerStyle">
								<div id="minimizer" class="minimizerStyle"><a id="minimizerText" class="minimizerTextStyle" href="javascript:minimizeToggle();"></a></div>
								<div id="TopLevel" class="listEntry"></div>
							</div>
						</div>
					</div>
					
					<div style="position:relative;">
						<div style="position:absolute; top:-30px; width:400px; height:30px; z-index:9999999999999999;">
							<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Findex.xml&reason=invalid-overlay-or-uncollected-site-resource" style="display:block;" onmouseover="document.getElementById('bgtopleft').className='bgtopleft-mouseover'" onmouseout="document.getElementById('bgtopleft').className='bgtopleft'">
								<img src="/shared/wow-com/images/layout/pixel.gif" style="width:1px; height:32px;"/>
							</a>
						</div>
					</div>
					
					<div class="outerbox">
						<div class="outerbox-top">
							<div class="outerbox-bot">
								<div class="outerbox-left">
									<div class="outerbox-right">
										<div class="outerbox-topleft">
											<div class="outerbox-botleft">
												<div class="outerbox-topright">
													<div class="outerbox-botright">


														<div class="article-header">
															<div class="avatar" id="avatarImageContainer" style="background:url(images/icons/SentientMortals.jpg);"></div>
															<div class="breadcrumb">
																<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Findex.xml&reason=invalid-overlay-or-uncollected-site-resource">Encyclopedia</a>
																<div id="aBeautifulCherryTree" class="breadcrumb-links"><span></span></div>
															</div>
															<h1 id="headLine" class="article-title"></h1>
														</div>
													
														<div class="content" id="articleContentContainer">
															<div class="content-top">
																<div class="content-bot">
																	<div class="content-right">
																		<div class="content-left">
																			<div class="content-topright">
																				<div class="content-topleft">
																					<div class="content-botright">
																						<div class="content-botleft">
																							<div class="padding">
	
																								<div class="alert" id="categoryAlert">
																									<span>This entry is also a category</span>
																									<a href="#related">Jump to articles in this category</a>
																								</div>

																								<xsl:apply-templates/>

																							</div>
																						</div>
																					</div>
																				</div>
																			</div>
																		</div>
																	</div>
																</div>
															</div>
														</div>

														<a name="related"></a>

														<div id="categoryArticles" class="relatedlinks" style="display:none;">
															<h2>Articles</h2>&#160;<h4>in category "<div id="categoryIdentifier" style="display:inline;"></div>"</h4><br/>
															<ul id="theSoundOfRunningWater" class="articleListContainer"></ul>
														</div>
															
														<div class="relatedlinks">
															<h2>Back to...</h2>
															<div class="backto">
																<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Findex.xml&reason=invalid-overlay-or-uncollected-site-resource">Encyclopedia</a>
																<div id="abbreviatedTree" class="breadcrumb-links"><span></span></div>
															</div> 
														</div>
	
													</div>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					
				</div>
			</div>
		</div>
	</div>
</div>
<script language="javascript" type="text/javascript">initializationSequence();</script>

</xsl:template>

<!-- *********** Faction Tables ************ -->

<xsl:template match="factionTable">
  <xsl:call-template name="factionTable">
		<xsl:with-param name="allianceHorde" select="@allianceHorde"/>
		<xsl:with-param name="repLevels" select="@repLevels"/>
		<xsl:with-param name="pvpTable" select="@pvpTable"/>
		<xsl:with-param name="allianceName" select="@allianceName"/>
		<xsl:with-param name="hordeName" select="@hordeName"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="factionTable">

  <xsl:param name="allianceHorde"/>
  <xsl:param name="repLevels"/>
  <xsl:param name="pvpTable">false</xsl:param>
	<xsl:param name="allianceName">None</xsl:param>
	<xsl:param name="hordeName">None</xsl:param>

	<script language="javascript">
	
	function dropToggle()
	{

		if(is_safari) { safariEscapeGoat(); }
		else
		{
			document.getElementById("dropBox").style.overflow = (document.getElementById("dropBox").style.overflow == "hidden") ? "visible" : "hidden";
		}
	}
	
	previousListItem = 0;
	function nowThisIsHappening(thisListItem)
	{
		if(is_safari) { safariEscapeGoat(); }
		else
		{
			if (thisListItem != previousListItem)
			{
				document.getElementById("slotZero").innerHTML = document.getElementById("slot"+thisListItem).innerHTML;
				previousListItem = thisListItem;
				/* INSERT ADDITIONAL CODE HERE */
				levelBracket = thisListItem;
				reloadTable();
			}
			dropToggle();
		}
	}

	function safariEscapeGoat()
	{
		levelBracket = (levelBracket &lt; 3) ? levelBracket+1 : 0;
		document.getElementById("slotZero").childNodes[1].innerHTML = document.getElementById("slot"+levelBracket).childNodes[1].innerHTML;
		reloadTable();
	}
	
	</script>
<xsl:choose>
	<xsl:when test="@pvpTable = 'true'">
		<style type="text/css">
			.lorePopBG { position:relative; margin-left:35px; background:url(/info/basics/factions/rewardstable/images/table-pvpbg.jpg) top left no-repeat; width:320px; height:450px; }
			.lorePopButton { cursor: pointer; position:absolute; top:129px; left:14px; background:url(/info/basics/factions/rewardstable/images/pvptable-pvpbutton.jpg) bottom left; width:120px; height:143px; }
		</style>
	</xsl:when>
	<xsl:otherwise>
		<style type="text/css">
			.lorePopBG { position:relative; margin-left:35px; background:url(/info/basics/factions/rewardstable/images/table-lorebg.jpg) top left no-repeat; width:320px; height:450px; }
			.lorePopButton { cursor: pointer; position:absolute; top:129px; left:14px; background:url(/info/basics/factions/rewardstable/images/loretable-lorebutton.jpg) bottom left; width:120px; height:143px; }
		</style>
	</xsl:otherwise>
</xsl:choose>
			
	<div class="lorePopBG">
		<div id="loreButton" onMouseOver="mouseMoveIn('loreButton');" onMouseOut="mouseMoveOut('loreButton');" onClick="sproing();" class="lorePopButton"></div>
		<table border="0" cellpadding="0" cellspacing="0" height="330" style="position:absolute; top:50px; left:103px; width:475px;">

			<xsl:choose>
				<xsl:when test="@allianceHorde = 'true'">
					<tr style="visibility:visible';">
						<td height="40" width="50"></td>
						<td height="40" width="182" id="allianceButton" style="background:url(/info/basics/factions/rewardstable/images/button-alliance.jpg) bottom left;" valign="middle">
							<br /><a style="font-family:Verdana; color:#FFD100; font-weight:bold; font-size:12px; text-decoration:none; margin-left:45px;" href="javascript:switchClick('alliance','horde'); hiliteBlink('loreButton');"><xsl:value-of select="@allianceName"/></a>
						</td>
						<td height="40" width="243" id="hordeButton" style="background:url(/info/basics/factions/rewardstable/images/button-horde.jpg) top left;" valign="middle" colspan="2">
							<br /><a style="font-family:Verdana; color:#FFD100; font-weight:bold; font-size:12px; text-decoration:none; margin-left:65px;" href="javascript:switchClick('horde','alliance'); hiliteBlink('loreButton');"><xsl:value-of select="@hordeName"/></a>
						</td>
					</tr>
				</xsl:when>
				<xsl:otherwise>
					<tr style="visibility:hidden';">
						<td height="40" width="50"></td>
						<td height="40" width="182" id="allianceButton" valign="middle">
							<br /><a style="font-family:Verdana; color:#FFD100; font-weight:bold; font-size:12px; text-decoration:none; margin-left:45px;" href="javascript:switchClick('alliance','horde'); hiliteBlink('loreButton');"><xsl:value-of select="factionTable/allianceName"/></a>
						</td>
						<td height="40" width="243" id="hordeButton" valign="middle" colspan="2">
							<br /><a style="font-family:Verdana; color:#FFD100; font-weight:bold; font-size:12px; text-decoration:none; margin-left:65px;" href="javascript:switchClick('horde','alliance'); hiliteBlink('loreButton');"><xsl:value-of select="factionTable/hordeName"/></a>
						</td>
					</tr>
				</xsl:otherwise>
			</xsl:choose>
			
			<tr>
				<td valign="top" colspan="4">
					<div style="position:relative;">

						<div id="allianceRewards" style="position:absolute; left:24px; visibility:hidden;">
							<table cellpadding="0" cellspacing="0" border="0" width="440" id="allianceFaction">
								<tr>
									<td colspan="3" height="36" style="background-image:url(/info/basics/factions/rewardstable/images/top-alliance-test.jpg);"></td>
								</tr>
								<tr>
									<td class="table_left"></td>
									<td class="table_center">
										<table width="414" cellpadding="0" cellspacing="0" border="0" style="background-image:url(/shared/wow-com/images/basics/factions/item-back207x55.jpg);"><tbody id="alliance_rewards"><tr></tr></tbody></table>
									</td>
									<td class="table_right"></td>
								</tr>
								<tr>
									<td colspan="3" height="17" style="background-image:url(/info/basics/factions/rewardstable/images/bottom-test.png); _background-image:url(/info/basics/factions/rewardstable/images/pixel.gif); _filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src="/info/basics/factions/rewardstable/images/bottom-test.png", sizingMethod='scale');"></td>
								</tr>
							</table>	  
						</div>
		
						<div id="hordeRewards" style="position:absolute; left:24px; visibility:visible;">
							<table cellpadding="0" cellspacing="0" border="0" width="440" id="hordeFaction">
								<tr>
									<td colspan="3" height="36" style="background-image:url(/info/basics/factions/rewardstable/images/top-horde-test.jpg);"></td>
								</tr>
								<tr>
									<td class="table_left"></td>
									<td class="table_center">
										<table width="414" cellpadding="0" cellspacing="0" border="0" style="background-image:url(/shared/wow-com/images/basics/factions/item-back207x55.jpg);"><tbody id="horde_rewards"><tr></tr></tbody></table>
									</td>
									<td class="table_right"></td>
								</tr>
								<tr>
									<td colspan="3" height="17" style="background-image:url(/info/basics/factions/rewardstable/images/bottom-test.png);"></td>
								</tr>
							</table>	  
						</div>

<xsl:if test="@repLevels = 'true'">
						<div class="dropDowner">
							<div class="dropDownArrow" onClick="dropToggle();"></div>
							<ul class="dropDownListStyle" style="overflow:hidden;" id="dropBox">
								<li id="slotZero" style="display:block; line-height:22px; margin-top:4px;"><a href="javascript:nowThisIsHappening(0);">Reputation Level:</a></li>
								<li id="slot0"><a href="javascript:nowThisIsHappening(0);"> Friendly</a></li>
								<li id="slot1"><a href="javascript:nowThisIsHappening(1);"> Honored</a></li>
								<li id="slot2"><a href="javascript:nowThisIsHappening(2);"> Revered</a></li>
								<li id="slot3"><a href="javascript:nowThisIsHappening(3);"> Exalted</a></li>
								<div class="dropDownFillerStyle"></div>
							</ul>
						</div>
</xsl:if>
						
					</div>
				</td>
			</tr>

		</table>
	</div>

</xsl:template>

<xsl:template match="XmlSubnavTag">
  <xsl:call-template name="XmlSubnavTag"/>
</xsl:template>

<xsl:template match="XmlSubnavTag-main" name="XmlSubnavTag-main">
  <xsl:call-template name="XmlSubnavTag">
  <xsl:with-param name="altjs" select="'navtree-main.js'"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="XmlSubnavTag"> 
<xsl:param name="altjs" select="."/>
    <xsl:choose>
        <xsl:when test="$altjs = 'navtree-main.js'">
            <script type="text/javascript" src="/shared/wow-com/includes-client/navtree-main.js"></script>
        </xsl:when>
        <xsl:otherwise>
            <script type="text/javascript" src="/shared/wow-com/includes-client/navtree.js"></script>
        </xsl:otherwise>
    </xsl:choose>
	<script type="text/javascript" src="/new-hp/js/menu132_com.js"></script>
	<script type="text/javascript" src="/shared/wow-com/includes-client/navtreefunctions.js"></script>
	<script type="text/javascript" src="/new-hp/js/xmlnavassist.js"></script>
	<link rel="stylesheet" href="/new-hp/css/xmlnavassiststyle.css"/>
    
	<div class="navigation">
		<center>
			<table cellspacing = "0" cellpadding = "0" border = "0" width = "96%">
				<tr>
					<td id="navIconTableCell" width="59" rowspan="3" valign = "top" style="background:url(/shared/wow-com/images/parchment/plain/light.jpg);"></td>
					<script language = "javascript">escapeGoat(result);</script>
					<td height="15" background="/shared/wow-com/images/subnav/nav_top.jpg"></td>
					<td width="18" height="65" rowspan="3" style="background:url(/shared/wow-com/images/parchment/plain/light.jpg);" valign="top"><img src="/shared/wow-com/images/subnav/nav_right.jpg" /></td>
				</tr>
				<tr>
					<td style="height:17px; background:url(/shared/wow-com/images/subnav/nav_middle.jpg) repeat-x;" nowrap="nowrap"><div id = "filterMenu"></div></td>
				</tr>
				<tr>
					<td style="padding-top:0; background:url(/shared/wow-com/images/subnav/subnav_topright.gif) repeat-x;">
							<table width="100%" cellpadding="0" cellspacing="0" border="0" style="height:33px; margin-top:0;">
								<tr>
									<td width="5" height="33" style="background-image:url(/shared/wow-com/images/subnav/leftsubnav.jpg); background-position:top; background-repeat:repeat-x;"></td>
									<td height="33" background="/shared/wow-com/images/subnav/subnav.jpg" width="100%">
										<table width="100%" height="33" cellpadding="0" cellspacing="0" border="0">
											<tr>
												<td width="5" height="5" background="/shared/wow-com/images/subnav/subnav_topleft.gif"></td>
												<td height="5" background="/shared/wow-com/images/subnav/subnav_top.gif"></td>
												<td width="6" height="5" background="/shared/wow-com/images/subnav/subnav_topright.gif"></td>
											</tr> 
											<tr>
												<td width="5" height="19" background="/shared/wow-com/images/subnav/subnav_left.gif"></td>
												<td height="19" style="text-align:center;" background="/shared/wow-com/images/subnav/subnav_bg.gif" valign="middle">
													<img src="/images/layout/pixel.gif" width="1" height="1" />
													<small id="subNavTwoContainer" class="button" style="color:#808080; letter-spacing:normal;"></small>
													<script language = "javascript">printSubNav2(result);</script>
												</td>
												<td width="6" height="19" background="/shared/wow-com/images/subnav/subnav_right.gif"></td>
											</tr>
											<tr>
												<td width="5" height="9" background="/shared/wow-com/images/subnav/subnav_botleft.gif"></td>
												<td height="9" background="/shared/wow-com/images/subnav/subnav_bot.gif"></td>
												<td width="6" height="9" background="/shared/wow-com/images/subnav/subnav_botright.gif"></td>
											</tr>
										</table>
									</td>
								</tr>
							</table>
					</td>
				</tr>
			</table>
		</center>
	</div>
	
</xsl:template>


<!-- End Frost's Includes. NEDM. -->

<xsl:template name="relatedlinks" match="relatedlinks">
<div class = "guideHeader" style="height:29px; overflow:hidden">
<table width="100%" align="center" cellspacing = "0" cellpadding = "0" border = "0">
<tr>
	<td width="10" ><img src="/shared/wow-com/images/headers/tabheader/tabheader-left-left.jpg" width="17" height="29" border="0"/></td>
    <td width = "362"  background = "/shared/wow-com/images/headers/tabheader/tabheader-left.jpg" align = "left"><h3 class = "guideTitle" style="width:362px">Related Links</h3></td>
	
	<td width="100%"  background = "/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg" align = "right"><img src = "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%40P%40&reason=invalid-overlay-or-uncollected-site-resource" width = '1' height = '2'/><div id="fsguide"></div><script language = "javascript">
if (stripId(Menu1[0]) == "Game Guide") 
document.getElementById('fsguide').innerHTML = "&lt;a href = 'mailto:wowguide@blizzard.com?subject=Fan Strategy: " + stripId(pageId) + "&amp;body=Strategy relates to: " + document.location.href + "%0A%0AAuthor Name:%0A%0AType your strategy here(or attach):%0A%0A%0A%0A%0A%0A---------------%0ARead the submission guidelines before submitting your strategy%0Ahttp://www.worldofwarcraft.com/info/faq/guide-strategies.html%0ABy sending this email, you agree that Blizzard Entertainment, Inc., shall have the right to share any and all tips, guidelines, advice and suggestions you submit with the rest of the World of Warcraft Community through the World of Warcraft Community Site located at www.worldofwarcaft.com, as well as any online or printed strategy guides related to Blizzard Entertainment, Inc.\'s World of Warcraft game.'&gt;&lt;img src = "/shared/wow-com/images/buttons/button-submitstrat.gif" width = '127' height ='22' border = '0' alt = 'Submit a strategy on this page'&gt;&lt;/a&gt;";
</script></td>	
	<td background = "/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg"><img src = "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%40P%40&reason=invalid-overlay-or-uncollected-site-resource" width = '3' height = '1'/></td>
	<td width="127" background = "/shared/wow-com/images/headers/tabheader/tabheader-bg.jpg"><img src = "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Flayout%2Flayout.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%40P%40&reason=invalid-overlay-or-uncollected-site-resource" width = '1' height = '2'/><div id="rlguide"></div>
<script language = "javascript">
if (document.location.href.indexOf("/account/") == -1 &amp;&amp; document.location.href.indexOf("/loginsupport/") == -1)
document.getElementById('rlguide').innerHTML = "&lt;a href = 'mailto:wowguide@blizzard.com?subject=Wow Guide Error: " + stripId(pageId) + "&amp;body=Error on page: " + document.location.href + "%0A%0AType your error report here:%0A%0A%0A%0A%0A%0A---------------%0ARead the error reporting guidelines before submitting your email%0Ahttp://www.worldofwarcraft.com/info/faq/guide.html%0APlease use this email to report guide errors only. Any problems with the game or your account should be reported here: http://www.blizzard.com/support/wow/?id=aww01730p'&gt;&lt;img src = "/shared/wow-com/images/buttons/button-reporterror.gif" width = '127' height ='22' border = '0' alt = 'Report an error on this page'&gt;&lt;/a&gt;";
</script></td>
</tr>
</table>
</div>

<div class = "postContainerPlain">
<div class = "postBody" style="font-size:12px; line-height:17px;">
<script language = "javascript"> printSubNav(result,2); printRelatedLinks(result); </script>
</div>
</div>

</xsl:template>

</xsl:stylesheet>