<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/wrath/layout/global.xsl"/>

<xsl:template name="styles">
	div.sub-header-top { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="features/@background"/>-t.jpg'); }
	div.sub-header-left { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="features/@background"/>-l.jpg'); height: 400px; }
	div.sub-header-right { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="features/@background"/>-r.jpg'); height: 400px; }
</xsl:template>

<xsl:template match="features">
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$loc/strs/str[@id='wrath.subtitle.name.features']"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>

<xsl:template name="pagecontents">
	<script type="text/javascript" src="/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Ffeatures.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fstrings%2F%7B%24lang%7D%2Fstrings.js&reason=invalid-overlay-or-uncollected-site-resource"></script>
	<xsl:call-template name="feature-page"/>
</xsl:template>

<xsl:template name="feature-page">
<div class="features">
 <div class="deathknight-top">
   <div class="subcat">
	<div class="top-rule"></div>
	<h1><xsl:value-of select="$loc/strs/features/str[@id='label.latestupdates']"/></h1>
<div class="update-list">

<xsl:for-each select="update"> 
	<xsl:variable name="name" select="name" />
	<xsl:variable name="category" select="category" />
	<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Ffeatures.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&reason=invalid-overlay-or-uncollected-site-resource" class="feature-update">
		<xsl:attribute name="style">
			<xsl:choose>
				<xsl:when test="position() &lt;= 4">display:block</xsl:when>
				<xsl:otherwise>display:none</xsl:otherwise>
			</xsl:choose>
		</xsl:attribute>
		<ul> 
			<li class="item"><span><xsl:value-of select="$loc/strs/str[@id=$name]"/></span></li>
			<li><strong><xsl:value-of select="$loc/strs/features/str[@id='label.category']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/></strong>&#160;<xsl:value-of select="$loc/strs/str[@id=$category]"/></li>
			<li class="date"><strong><xsl:value-of select="$loc/strs/movies/str[@id='label.dateadded']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/></strong>&#160;
				<xsl:call-template name="stringorder">
					<xsl:with-param name="datainsert1" select="month"/>
					<xsl:with-param name="datainsert2" select="day"/>
					<xsl:with-param name="datainsert3" select="year"/>
					<xsl:with-param name="orderid" select="'wrath.order.date'"/>				
				</xsl:call-template>			
			</li>
		</ul>
	</a>
</xsl:for-each>	

</div>
<script>function iterate(){ return rval;}</script>
<!-- Deathknight -->
	<div class="feature-category">
	 <div class="deathknight">
	  <h1><xsl:value-of select="$loc/strs/str[@id='wrath.deathknight.title']"/></h1>
	  <span><xsl:value-of select="$loc/strs/str[@id='wrath.deathknight.desc']"/></span>
	  <div class="fblock-container">
<xsl:for-each select="deathknight">
<xsl:call-template name="feature"/>
</xsl:for-each>
<div class="fblock" style="display:none">
<a class="feature-toggle" href=""><xsl:value-of select="$loc/strs/str[@id='wrath.labels.showall']"/><em></em></a>
</div>
		</div>
	 </div>
	</div>

<!-- Dungeons -->
	<div class="feature-category">
	 <div class="dungeons">
	  <h1><xsl:value-of select="$loc/strs/str[@id='wrath.dungeons.title']"/></h1>
	  <span><xsl:value-of select="$loc/strs/str[@id='wrath.dungeons.desc']"/></span>
	  <div class="fblock-container">
<xsl:for-each select="dungeons">
<xsl:call-template name="feature"/>
</xsl:for-each>
<div class="fblock" style="display:none">
<a class="feature-toggle" href=""><xsl:value-of select="$loc/strs/str[@id='wrath.labels.showall']"/><em></em></a>
</div>
		</div>
	 </div>
	</div>

<!-- story -->
	<div class="feature-category">
	 <div class="story">
	  <h1><xsl:value-of select="$loc/strs/str[@id='wrath.story.title']"/></h1>
	  <span><xsl:value-of select="$loc/strs/str[@id='wrath.story.desc']"/></span>
	  <div class="fblock-container">
<xsl:for-each select="story">
<div class="coll">
    <xsl:attribute name="style">
        <xsl:choose><xsl:when test="position() &lt;= 2">display:block</xsl:when>
        <xsl:otherwise>display:none</xsl:otherwise></xsl:choose>
    </xsl:attribute>
<xsl:call-template name="feature"/>
</div>
</xsl:for-each>
<div class="fblock">
<a class="feature-toggle" onclick="showall(this)" href="javascript:;"><u><xsl:value-of select="$loc/strs/str[@id='wrath.labels.showall']"/></u></a>
</div>
		</div>
	 </div>
	</div>
<!-- environment -->
	<div class="feature-category">
	 <div class="environment">
	  <h1><xsl:value-of select="$loc/strs/str[@id='wrath.environments.title']"/></h1>
	  <span><xsl:value-of select="$loc/strs/str[@id='wrath.environments.desc']"/></span>
	  <div class="fblock-container">
<xsl:for-each select="environment">
<div class="coll">
    <xsl:attribute name="style">
        <xsl:choose><xsl:when test="position() &lt;= 2">display:block</xsl:when>
        <xsl:otherwise>display:none</xsl:otherwise></xsl:choose>
    </xsl:attribute>
<xsl:call-template name="feature"/>
</div>
</xsl:for-each>
<div class="fblock">
<a class="feature-toggle" onclick="showall(this)" href="javascript:;"><u><xsl:value-of select="$loc/strs/str[@id='wrath.labels.showall']"/></u></a>
</div>
		</div>
	 </div>
	</div>

<!-- factions -->
	<div class="feature-category">
	 <div class="factions">
	  <h1><xsl:value-of select="$loc/strs/str[@id='wrath.factions.title']"/></h1>
	  <span><xsl:value-of select="$loc/strs/str[@id='wrath.factions.desc']"/></span>
	  <div class="fblock-container">
<xsl:for-each select="factions">
<div class="coll">
    <xsl:attribute name="style">
        <xsl:choose><xsl:when test="position() &lt;= 2">display:block</xsl:when>
        <xsl:otherwise>display:none</xsl:otherwise></xsl:choose>
    </xsl:attribute>
<xsl:call-template name="feature"/>
</div>
</xsl:for-each>
<div class="fblock"><xsl:for-each select="factions"><xsl:attribute name="style"> <xsl:choose><xsl:when test="position() &lt; 2">display:none</xsl:when><xsl:otherwise>display:block</xsl:otherwise></xsl:choose></xsl:attribute></xsl:for-each>
<a class="feature-toggle" onclick="showall(this)" href="javascript:;"><u><xsl:value-of select="$loc/strs/str[@id='wrath.labels.showall']"/></u></a>
</div>
		</div>
	 </div>
	</div>


<!-- Bestiary -->
	<div class="feature-category">
	 <div class="dungeons">
	  <h1><xsl:value-of select="$loc/strs/str[@id='wrath.bestiary.title']"/></h1>
	  <span><xsl:value-of select="$loc/strs/str[@id='wrath.bestiary.desc']"/></span>
	  <div class="fblock-container">
			<xsl:for-each select="bestiary">
				<xsl:call-template name="feature"/>
			</xsl:for-each>
		</div>
	 </div>
	</div>
<!-- blanks 
	<div class="feature-category" style="background:none">
		<div class="blanks">
			<h1><xsl:value-of select="$loc/strs/str[@id='wrath.bestiary.title']"/></h1>
			<span><xsl:value-of select="$loc/strs/str[@id='wrath.label.comingsoon']"/></span>
		</div>
		<div class="blanks-bot"></div>
	</div>
-->

  </div>
 </div>
</div>
<div class="features-bot"></div>
</xsl:template>

<!-- main features block -->
<xsl:template name="feature">
<xsl:variable name="name" select="name" />
<xsl:variable name="desc" select="desc" />
<xsl:variable name="imgPath" select="concat('images/layout/features/', thumb, '')" />
	    <div class="fblock">
		 <a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Ffeatures.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&reason=invalid-overlay-or-uncollected-site-resource">
		  <dfn><h2><xsl:value-of select="$loc/strs/str[@id=$name]"/></h2>
		  <span><strong><xsl:value-of select="$loc/strs/movies/str[@id='label.dateadded']"/><xsl:value-of select="$loc/strs/str[@id='wrath.colon']"/></strong>&#160;
			<xsl:call-template name="stringorder">
				<xsl:with-param name="datainsert1" select="month"/>
				<xsl:with-param name="datainsert2" select="day"/>
				<xsl:with-param name="datainsert3" select="year"/>
				<xsl:with-param name="orderid" select="'wrath.order.date'"/>				
			</xsl:call-template>
			</span>
			<p><xsl:value-of select="$loc/strs/str[@id=$desc]"/></p>
		  </dfn>
			<em style="background:url('{$imgPath}');"></em>
		 </a>
		 </div>
</xsl:template>


</xsl:stylesheet>


