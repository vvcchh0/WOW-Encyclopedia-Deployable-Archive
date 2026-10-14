<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/WOW-Encyclopedia-Deployable-Archive/wrath/layout/global.xsl"/>

<xsl:template name="styles">
	div.sub-header-top { background: url('images/layout/header5-t.jpg'); }
	div.sub-header-left { background: url('images/layout/header5-l.jpg'); height: 400px; }
	div.sub-header-right { background: url('images/layout/header5-r.jpg'); height: 400px; }
	div.sub-text-container { margin:0; }
</xsl:template>

<xsl:template match="wallpapers">
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$loc/strs/str[@id='wrath.subtitle.name.wallpapers']"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>


<xsl:template match="downloads">
    <xsl:call-template name="subpage"> 
		<xsl:with-param name="subtitlename" select="$loc/strs/str[@id='wrath.subtitle.name.downloads']"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>

<xsl:template name="wp_content">

<div style="padding-bottom:67px; position:relative; top:-53px; ">


<xsl:call-template name="wallpaper">
	<xsl:with-param name="title" select="$loc/strs/str[@id='wrath.wallpapers.6.title']" />
	<xsl:with-param name="wallid" select="'6'" />
</xsl:call-template>

<xsl:call-template name="wallpaper">
	<xsl:with-param name="title" select="$loc/strs/str[@id='wrath.wallpapers.8.title']" />
	<xsl:with-param name="wallid" select="'8'" />
</xsl:call-template>

<xsl:choose>
<xsl:when test="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fdownloads.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fpage%2F%40dl&amp;reason=external-or-uncollected-resource"> <div class="morewall">[ <a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fdownloads.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7B%24baseurl%7D%2Fwallpapers.xml&amp;reason=invalid-overlay-or-uncollected-site-resource"><xsl:value-of select="$loc/strs/str[@id='labels.morewallpapers']"/></a> ]</div> </xsl:when>
<xsl:otherwise>
<xsl:call-template name="wallpaper">
	<xsl:with-param name="title" select="$loc/strs/str[@id='wrath.wallpapers.2.title']" />
	<xsl:with-param name="wallid" select="'2'" />
</xsl:call-template>

<xsl:call-template name="wallpaper">
	<xsl:with-param name="title" select="$loc/strs/str[@id='wrath.wallpapers.7.title']" />
	<xsl:with-param name="wallid" select="'7'" />
</xsl:call-template>
</xsl:otherwise>
</xsl:choose>

</div>

</xsl:template>

<xsl:template name="pagecontents">
<xsl:choose>
<xsl:when test="/page/@dl = 'true'">
<div class="downloads">
<div class="dl_content"> 
<h1><xsl:copy-of select="$loc/strs/str[@id='wrath.downloads.fankit.title']"/></h1>
<div class="dl_link"><div class="file">(<xsl:copy-of select="$loc/strs/str[@id='wrath.downloads.fankit.filesize']"/>)</div><a href="{$loc/strs/str[@id='wrath.downloads.fankit.link']}"><img class="png" src="/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fdownloads.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7B%24baseurl%7D%2Fimages%2Flayout%2Fdl_icon.png&amp;reason=external-or-uncollected-resource" align="absmiddle"/><xsl:copy-of select="$loc/strs/str[@id='wrath.downloads.fankit.download']"/>  </a></div>
<xsl:copy-of select="$loc/strs/str[@id='wrath.downloads.fankit.desc']"/>
</div></div>
<div id="wp_title"></div>
<xsl:call-template name="flash-sub-title">
<xsl:with-param name="fl_title" select="$loc/strs/str[@id='wrath.subtitle.name.wallpapers']" /><xsl:with-param name="fl_loc" select="'wp_title'" /> </xsl:call-template>
<xsl:call-template name="wp_content"/></xsl:when>
<xsl:otherwise><xsl:call-template name="wp_content"/></xsl:otherwise>

</xsl:choose>



<xsl:call-template name="lightbox" />

</xsl:template>

</xsl:stylesheet>