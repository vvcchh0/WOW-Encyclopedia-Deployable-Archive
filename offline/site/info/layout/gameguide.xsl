<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html"/>

<xsl:include href="/new-hp/layout/layout.xsl"/>

<!-- Streamlined dungeon -->

<!-- This doesn't work in IE 5 for no good reason.
<xsl:template match="flashtitle">
<div id="dungeontitle" class="dt">
<script type="text/javascript">
   dttl = "<xsl:value-of select='@title'/>"
   var so = new SWFObject("../swf/d_ttl.swf", "d_ttl", "100%", "96", "8", "#FFFFFF");
   so.addParam("wmode", "transparent"); 
   so.addVariable("ttl",dttl);
   so.write("dungeontitle"); 
</script>

</div>
</xsl:template>
-->

<xsl:template match="flashtitle">
<div class="dt">
<xsl:call-template name="flash">
<xsl:with-param name="id" select="'d_ttl'"/>
<xsl:with-param name="src" select="'../swf/d_ttl.swf'"/>
<xsl:with-param name="width" select="'100%'"/>
<xsl:with-param name="height" select="96"/>
<xsl:with-param name="wmode" select="'transparent'"/>
<xsl:with-param name="flashvars" select="concat('ttl=',@title)"/>
</xsl:call-template>
</div>
</xsl:template>

<xsl:template match="dropcap"><div class="dropcap">
<xsl:call-template name="flash">
        <xsl:with-param name="id" select="concat('dropcap',@value)"/>
        <xsl:with-param name="src" select="'../swf/d_cap.swf'"/>
        <xsl:with-param name="width" select="55"/>
        <xsl:with-param name="height" select="55"/>
        <xsl:with-param name="align" select="left"/>
        <xsl:with-param name="wmode" select="'transparent'"/>
        <xsl:with-param name="flashvars" select="concat('ttl=',@value)"/>
</xsl:call-template></div>
</xsl:template>

<xsl:template match="ss">
<table class="ss" align="{@align}">
 <tr>
  <td class="tl"><img src="/shared/wow-com/images/borders/screenshot/top-left.gif"/></td><td class="tm" background="/shared/wow-com/images/borders/screenshot/top.gif"></td><td class="tr"><img src="/shared/wow-com/images/borders/screenshot/top-right.gif"/></td>
 </tr><tr>
  <td class="l" background="/shared/wow-com/images/borders/screenshot/left.gif"></td><td><xsl:apply-templates/> </td><td class="r" background="/shared/wow-com/images/borders/screenshot/right.gif"></td>
 </tr><tr>
  <td class="bl"><img src="/shared/wow-com/images/borders/screenshot/bot-left.gif"/></td><td class="bm" background="/shared/wow-com/images/borders/screenshot/bot.gif"></td><td class="br"><img src="/shared/wow-com/images/borders/screenshot/bot-right.gif"/></td>
 </tr>
</table>
</xsl:template>

<xsl:template match="inset">
<div class="inset">
<div class="top"><div class="l"><div class="r"><div class="btm">
<div class="tl"><div class="tr"><div class="bl"><div class="br">
<xsl:apply-templates/>
</div></div></div></div></div></div></div></div>
</div><br clear="left"/>
</xsl:template>

<xsl:template match="blockquote">
<div class="bq">
<div class="qu">“</div><xsl:apply-templates/><div class="qu">”</div>
</div>
</xsl:template>



<xsl:template match="dungeon">

<link rel="stylesheet" href="/info/css/dungeons.css"/>

<script>current_dungeon = "<xsl:value-of select='@value'/>"; if(is_ie){ document.write('<link rel="stylesheet" href="/info/css/ie7.css"/>'); } </script>
<script src="/info/js/guide.js"></script>
<div class="dungeon_bg"><div class="dungeon_holder" style="zoom:1; background-image:url(../images/{@value}_banner.jpg);">
<div class = "redBannerBg">	<div class = "redBannerLeft"></div>	<div class = "redBannerLabel"><strong><xsl:value-of select='/page/@title'/></strong> </div>	<div class = "redBannerRight"></div> </div>
<script language = "javascript">var pageId = "<xsl:value-of select='@pageid'/>";</script>
<div class="dsubnav" ><xsl:call-template name="XmlSubnavTag" /></div>
<div class="m_content">
<div class="right_column">
<div class="statscroll"><div class="statscroll_t"><div class="statscroll_b">
<div class="exp_icon"><img id="expimg" src="" align="right" title="Requires The Burning Crusade" /></div>
<script>exps = "<xsl:value-of select='stats/@expansion'/>"; exps = exps.toLowerCase();
ttle = (exps=="burningcrusade")?"The Burning Crusade":(exps=="wrath")?"Wrath of the Lich King":"Wow Classic";
targexpimg = document.getElementById("expimg")
if(exps != "burningcrusade" &amp;&amp; exps != "wrath" &amp;&amp; exps != "wow"){ targexpimg.src = "/new-hp/images/icons/news-wow.gif" }
else {targexpimg.src = "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Flayout%2Fgameguide.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fimages%2Ficons%2Fnews-&reason=invalid-overlay-or-uncollected-site-resource"+exps+".gif" }
targexpimg.title = "Requires " + ttle 
</script>
<div class="stats_map" style="background-image:url(../images/map_{stats/@map}.jpg); background-position:{(stats/@xloc - 81) * -1}px {(stats/@yloc - 149) * -1}px"><img class="p" src="/info/images/map_border.png"/></div>
<div class="stats_loc"><div class="loc_ttl">Location: </div><xsl:value-of select="stats/location/@val"/></div>
<xsl:if test="count(stats/wing) &gt; 1"><div class="wings"><select onchange="wingchange(this,this.value)"><xsl:for-each select="stats/wing"><option><xsl:attribute name="value"><xsl:value-of select="position()"/></xsl:attribute><xsl:value-of select="@name"/></option></xsl:for-each></select></div></xsl:if>
<xsl:for-each select="stats/wing">
<span>
<xsl:if test="position() = 1"><xsl:attribute name="style">display:block</xsl:attribute></xsl:if>
<div class="stats_content">
<table>
<xsl:for-each select="stat">
<tr><td class="statname"><xsl:value-of select="@name"/></td>
<td>
<xsl:choose>
<xsl:when test="@link">[<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Flayout%2Fgameguide.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Flayout%2F%7B%40link%7D&reason=invalid-overlay-or-uncollected-site-resource"><xsl:value-of select="@val"/></a>]</xsl:when>
<xsl:otherwise><xsl:value-of select="@val"/></xsl:otherwise>
</xsl:choose>
</td></tr>
</xsl:for-each></table></div>
<xsl:for-each select="button">
<div style="margin:10px 0 0 70px"><xsl:call-template name="redButton">
        <xsl:with-param name="id" select="concat('button',position())"/>
        <xsl:with-param name="label" select="'Loot Tables'"/>
        <xsl:with-param name="width" select="'160'"/>
        <xsl:with-param name="xCoord" select="'45'"/>
        <xsl:with-param name="url" select="@url"/>
</xsl:call-template></div>
</xsl:for-each></span>
</xsl:for-each>
</div></div></div>
</div>
<xsl:apply-templates select="content"/>
<br clear="all"/> &#160;</div>
</div>
</div>

 
</xsl:template>

</xsl:stylesheet>