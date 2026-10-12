<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/wrath/layout/global.xsl"/>

<xsl:template name="styles">
	div.sub-header-top { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="@background"/>-t.jpg'); }
	div.sub-header-left { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="@background"/>-l.jpg'); height: 400px; }
	div.sub-header-right { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="@background"/>-r.jpg'); height: 400px; }
</xsl:template>

<xsl:template match="movies">
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$loc/strs/str[@id='wrath.subtitle.name.movies']"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>

<xsl:template name="pagecontents">
	<xsl:call-template name="movies-page"/>
</xsl:template>

<xsl:template name="movies-page">
<div class="movie-frame">
	<xsl:for-each select="movie">
	<xsl:variable name="lang" select="/page/@lang" />	
	<xsl:variable name="imgPath" select="concat('images/language/', $lang, '/movies/', img, '')" />
	<xsl:variable name="moviename" select="name" />
	<xsl:variable name="dlpc" select="urlPC" />
	<xsl:variable name="dlmac" select="urlMac" />
	<xsl:variable name="dlflv" select="urlFlv" />
    <div class="movie">
		<div class="movie-top"></div>
		<div class="movie-bg">
		<xsl:choose>
			<!-- not empty flash movie var: print popup link -->
			<xsl:when test="$dlflv != ''">
				<a href="#" onclick='javascript:window.open("{$loc/strs/str[@id="wrath.mediahost"]}{$loc/strs/movies/str[@id=$dlflv]}","Wrath","status=0,toolbar=0,width=420,height=325,scrollbars=0");return(false);' class="mov" style="background: url('{$imgPath}')">
			 	<p style="display:{temp}">
		 		<xsl:value-of select="$loc/strs/str[@id='wrath.label.comingsoon']"/></p></a>
			 </xsl:when>
			<!-- empty flash movie var: no popup -->
			<xsl:otherwise>
				<a href="{$loc/strs/str[@id='wrath.base']}movies/{$loc/strs/movies/str[@id=$dlpc]}" class="mov" style="background: url('{$imgPath}')">
			 	<p style="display:{temp}">
			 	<xsl:value-of select="$loc/strs/str[@id='wrath.label.comingsoon']"/></p></a>
			 </xsl:otherwise>
		 </xsl:choose>
		 <em><h2><xsl:value-of select="$loc/strs/str[@id=$moviename]"/></h2><h3>(<xsl:value-of select="dimension"/>)</h3>
		 <ul>
		 	<li><xsl:value-of select="$loc/strs/movies/str[@id='label.dateadded']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/>&#160;
			<xsl:call-template name="stringorder">
				<xsl:with-param name="datainsert1" select="month"/>
				<xsl:with-param name="datainsert2" select="day"/>
				<xsl:with-param name="datainsert3" select="year"/>
				<xsl:with-param name="orderid" select="'wrath.order.date'"/>				
			</xsl:call-template>			
			</li>
			<li><strong><xsl:value-of select="$loc/strs/movies/str[@id='label.format']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/></strong>&#160;<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fmovies.xsl&requested=http%3A%2F%2Fwww.divx.com%2F&reason=external-or-uncollected-resource" target="_blank"><xsl:value-of select="$loc/strs/movies/str[@id='label.divx']"/></a>&#160;
			<xsl:choose>
				<xsl:when test="$dlflv">
					<xsl:value-of select="$loc/strs/movies/str[@id='label.and']"/>&#160;<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fmovies.xsl&requested=http%3A%2F%2Fwww.adobe.com%2Fshockwave%2Fdownload%2Fdownload.cgi%3FP1_Prod_Version%3DShockwaveFlash%26%2338%3Bpromoid%3DBIOW&reason=external-or-uncollected-resource" target="_blank"><xsl:value-of select="$loc/strs/movies/str[@id='label.flash']"/></a>
				</xsl:when>
			</xsl:choose>
			</li>
			<li><strong><xsl:value-of select="$loc/strs/movies/str[@id='label.requires']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/></strong>&#160;<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fmovies.xsl&requested=http%3A%2F%2Fwww.divx.com%2Fdivx%2Fwindows%2F&reason=external-or-uncollected-resource" target="_blank"><xsl:value-of select="$loc/strs/movies/str[@id='label.divx.pc']"/></a><xsl:value-of select="$loc/strs/movies/str[@id='label.or']"/><a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fmovies.xsl&requested=http%3A%2F%2Fwww.divx.com%2Fdivx%2Fmac%2F&reason=external-or-uncollected-resource" target="_blank"><xsl:value-of select="$loc/strs/movies/str[@id='label.divx.mac']"/></a></li>
			<li><strong><xsl:value-of select="$loc/strs/movies/str[@id='label.size']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/></strong>&#160;<xsl:value-of select="size"/><xsl:value-of select="$loc/strs/movies/str[@id='label.bytecount']"/>&#160;
			<xsl:choose>
				<xsl:when test="$dlflv">
			/&#160;<xsl:value-of select="stream"/><xsl:value-of select="$loc/strs/movies/str[@id='label.bytecount']"/>
				</xsl:when>
			</xsl:choose>
			</li>
			
			<li><strong><xsl:value-of select="$loc/strs/movies/str[@id='label.download']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/></strong>&#160;
			<a href="{$loc/strs/str[@id='wrath.base']}movies/{$loc/strs/movies/str[@id=$dlpc]}" class="pcd"><xsl:comment>ie</xsl:comment></a><a href="{$loc/strs/str[@id='wrath.base']}movies/{$loc/strs/movies/str[@id=$dlmac]}" class="macd"><xsl:comment>ie</xsl:comment></a>
			<xsl:choose>
				<xsl:when test="$dlflv">
					<a href="#" onclick='javascript:window.open("{$loc/strs/str[@id="wrath.mediahost"]}{$loc/strs/movies/str[@id=$dlflv]}","Wrath","status=0,toolbar=0,width=420,height=325,scrollbars=0");' class="flvd"><xsl:comment>ie</xsl:comment></a>
				</xsl:when>
			</xsl:choose>
			</li>
		 </ul></em>
		</div>
		<div class="movie-bot"></div>
	</div>
	</xsl:for-each>
</div>
</xsl:template>

</xsl:stylesheet>



