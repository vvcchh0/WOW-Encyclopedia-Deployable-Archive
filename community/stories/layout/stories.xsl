<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html"/>

<xsl:include href="/WOW-Encyclopedia-Deployable-Archive/new-hp/layout/layout.xsl"/>



<xsl:template match="flashtitle"> <!--This code, the dropcap, and ss below are duplicated in the dungeon specific gameguide XSL-->
<div class="dt">
<xsl:call-template name="flash">
<xsl:with-param name="id" select="'d_ttl'"/>
<xsl:with-param name="src" select="'/WOW-Encyclopedia-Deployable-Archive/info/swf/d_ttl.swf'"/>
<xsl:with-param name="width" select="600"/>
<xsl:with-param name="height" select="68"/>
<xsl:with-param name="wmode" select="'transparent'"/>
<xsl:with-param name="flashvars" select="concat('ttl=',@title)"/>
</xsl:call-template>
</div>
<div class="dt_block"/>
</xsl:template>

<xsl:template match="dropcap"><div class="dropcap">
<xsl:call-template name="flash">
        <xsl:with-param name="id" select="concat('dropcap',@value)"/>
        <xsl:with-param name="src" select="'/WOW-Encyclopedia-Deployable-Archive/info/swf/d_cap.swf'"/>
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
  <td class="tl"><img src="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top-left.gif"/></td><td class="tm" background="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top.gif"></td><td class="tr"><img src="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/top-right.gif"/></td>
 </tr><tr>
  <td class="l" background="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/left.gif"></td><td><xsl:apply-templates/> </td><td class="r" background="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/right.gif"></td>
 </tr><tr>
  <td class="bl"><img src="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot-left.gif"/></td><td class="bm" background="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot.gif"></td><td class="br"><img src="/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/screenshot/bot-right.gif"/></td>
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


<xsl:template match="storiesbg">
<link rel="stylesheet" href="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.css?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fcss%2Fstyles.css&amp;reason=invalid-overlay-or-uncollected-site-resource"/>
<script src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fjs%2Ffunctions.js&amp;reason=invalid-overlay-or-uncollected-site-resource"></script>
<div class = "redBannerBg">	<div class = "redBannerLeft"></div>	<div class = "redBannerLabel" style="width:90%" ><!----></div>	<div class = "redBannerRight"></div> </div>
<div><img style="position:absolute; margin-top:-99px;" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fimages%2Fheader_top.gif&amp;reason=external-or-uncollected-resource" /></div><img title="'Seriously, I'm NOT Val Kilmer.'" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fimages%2Fheader.jpg&amp;reason=external-or-uncollected-resource" />
<script language = "javascript">var pageId = "<xsl:value-of select="@pageId"/>"; </script>


<xsl:call-template name="XmlSubnavTag-main" />

<div class="postContainerPlain"><div class="postBody">
<xsl:apply-templates/>
</div></div>

</xsl:template>


<xsl:template match="storycontent">
<div class="mod_parch_mid"><div class="mod_parch_top"><div class="mod_parch_btm">

<xsl:choose>

<xsl:when test="@type = 'new'">
<xsl:for-each select="document('/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Farchive%2Fstory_index.xml&amp;reason=external-or-uncollected-resource')/root/batch[position()=1]">
<xsl:for-each select="story">

<table class="st_current"><tr>
      <td class="byline"><a class="readlink" href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Farchive%2F%7B%40file%7D&amp;reason=invalid-overlay-or-uncollected-site-resource"/><span><a class="closelink" onclick="showStory(this);" href="javascript:;"/></span><h2><xsl:value-of select="@title"/></h2><xsl:value-of select="@name"/>  <xsl:if test="@loc != '' ">, </xsl:if> <em><xsl:value-of select="@loc"/></em>
      <xsl:if test="@loc != '' "> <br /></xsl:if> 
    <xsl:value-of select="@char"/><xsl:if test="@realm != '' ">, </xsl:if> <em><xsl:value-of select="@realm"/></em>
      </td>
      </tr><tr>
      <td>
      <div class="st_desc"><xsl:apply-templates /> [<a onClick="showStory(this);" href="javascript:;">more</a>]</div>
	  <div style="display: none;">      
          <xsl:for-each select="document(concat('/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Farchive%2F&amp;reason=external-or-uncollected-resource',@file))/page/root">
          <xsl:apply-templates/>
          </xsl:for-each>
	  </div>      	
      </td>
   </tr></table>
</xsl:for-each>
</xsl:for-each>
</xsl:when>

<xsl:when test="@type = 'archive'">
<xsl:for-each select="document('/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Farchive%2Fstory_index.xml&amp;reason=external-or-uncollected-resource')/root/batch/story">
<table class="st_archive">
<xsl:if test="not(position() mod 2)"><xsl:attribute name="class">st_archive zebra</xsl:attribute> </xsl:if>
<tr>
    <td class="byline"><a class="readlink" href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Farchive%2F%7B%40file%7D&amp;reason=invalid-overlay-or-uncollected-site-resource"/><h2><xsl:value-of select="@title"/></h2><span><xsl:if test="@name = 'Anonymous'"><xsl:attribute name="class">anon</xsl:attribute></xsl:if><xsl:value-of select="@name"/></span> <xsl:if test="@loc != '' ">, </xsl:if> <em><xsl:value-of select="@loc"/></em>
    <xsl:if test="@loc != '' and @char != ''"> - </xsl:if> 
    <xsl:value-of select="@char"/><xsl:if test="@realm != '' ">, </xsl:if> <em><xsl:value-of select="@realm"/></em>
    </td>
</tr><tr>
      <td class="st_desc"><xsl:apply-templates /> [<a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Farchive%2F%7B%40file%7D&amp;reason=invalid-overlay-or-uncollected-site-resource">more</a>]</td>
   </tr></table>
</xsl:for-each>
</xsl:when>

<xsl:otherwise>
<xsl:apply-templates select="document(concat('/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Flayout%2Fstories.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fstories%2Farchive%2F&amp;reason=external-or-uncollected-resource',@value))" />
</xsl:otherwise>
</xsl:choose></div></div></div>
</xsl:template>

<xsl:template match="root">
<link rel="stylesheet" href="/WOW-Encyclopedia-Deployable-Archive/community/stories/css/styles.css"/>
<div class = "redBannerBg">	<div class = "redBannerLeft"></div>	<div class = "redBannerLabel" style="width:90%" ><!----></div>	<div class = "redBannerRight"></div> </div>
<div><img style="position:absolute; margin-top:-99px;" src="/WOW-Encyclopedia-Deployable-Archive/community/stories/images/header_top.gif" /></div><img title="'I'm serious. For realsies.'" src="/WOW-Encyclopedia-Deployable-Archive/community/stories/images/header.jpg" />
<div class="postContainerPlain"><div class="postBody">
<div class="top_parch"><a class="arc_btn" href="/WOW-Encyclopedia-Deployable-Archive/community/stories/archive.xml.html"/><a class="new_btn" href="/WOW-Encyclopedia-Deployable-Archive/community/stories/stories.xml.html"/></div><div class="top_block"/>
<div class="mod_parch_mid"><div class="mod_parch_top"><div class="mod_parch_btm">
<h2><xsl:value-of select="@title"/></h2><div class="byline">
<div><span><xsl:value-of select="@char"/></span><xsl:if test="@realm != '' ">, </xsl:if> <em><xsl:value-of select="@realm"/></em></div>
<span><xsl:if test="@name = 'Anonymous'"><xsl:attribute name="class">anon</xsl:attribute></xsl:if><xsl:value-of select="@name"/></span>  <xsl:if test="@loc != '' ">, </xsl:if> <em><xsl:value-of select="@loc"/></em></div>
<xsl:apply-templates/>
</div></div></div>
</div></div>
</xsl:template>


</xsl:stylesheet>