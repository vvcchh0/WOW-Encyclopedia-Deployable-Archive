<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:import href="/wrath/layout/global.xsl"/>
<xsl:template name="styles">
	div.sub-header-top { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="deathknight/@background"/>-t.jpg'); }
	div.sub-header-left { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="deathknight/@background"/>-l.jpg'); height: 400px; }
	div.sub-header-right { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="deathknight/@background"/>-r.jpg'); height: 400px; }
</xsl:template>

<xsl:template match="qdrop">
<div class="qdrop"></div>
</xsl:template>

<xsl:template match="bgfracture">
<div class="bgshim"><div class="bgfracture"></div></div>
</xsl:template>


<xsl:template match="deathknight">
<xsl:variable name="feature" select="@feature"/>
<xsl:variable name="class" select="@class"/>
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$loc/strs/deathknight/str[@id=$class]"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>
<xsl:template name="pagecontents">
			<xsl:call-template name="deathknight">
				<xsl:with-param name="class" select="@class"/>
			</xsl:call-template>
</xsl:template>
<xsl:template name="deathknight">
<xsl:param name="class"/>
<div class="{$class}">
<div class="dk_subnav"><xsl:call-template name="zones" /></div>
<div class="features">
 <div class="deathknight-top">
   <div class="subcat story">
	<div class="top-rule_fade"></div>
	<div class="copy">
<xsl:variable name="textPath" select="document(concat('../strings/',$lang,'/features/',$class,'.xml'))" />
<xsl:for-each select="$textPath/content/section">
  	<xsl:apply-templates/>
</xsl:for-each>
<xsl:call-template name="zones-footer"/>
	</div>
  </div>
 </div>
</div>
<div class="features-bot"></div>
</div>
<xsl:call-template name="lightbox" />
</xsl:template>





<xsl:variable name="zonePath" select="document('../features.xml')" />
<xsl:template match="zones" name="zones">
<div class="zone-list">
<h2 style="visibility:hidden"><xsl:value-of select="$loc/strs/deathknight/str[@id='name']"/></h2>
<xsl:for-each select="$zonePath/page/features/deathknight">
<xsl:variable name="name" select="name" />
	<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fdeathknight.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&reason=invalid-overlay-or-uncollected-site-resource" class="zone-menu">
	 <ul>
	  <li class="item"><span><xsl:value-of select="$loc/strs/str[@id=$name]"/></span></li>
	 </ul>
	</a>
</xsl:for-each>	
</div>
</xsl:template>


<xsl:template name="zones-footer">
<div class="zones-footer">
	<div>
	<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fdeathknight.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffeatures.xml&reason=invalid-overlay-or-uncollected-site-resource"><span>&#171;</span><xsl:value-of select="' '"/><xsl:value-of select="$loc/strs/str[@id='labels.returntofeatures']"/></a>
	<xsl:for-each select="$zonePath/page/features/deathknight">
	<xsl:variable name="name" select="name" />
	&#160;&#183;&#160;&#160;<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fdeathknight.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&reason=invalid-overlay-or-uncollected-site-resource"><xsl:value-of select="$loc/strs/str[@id=$name]"/></a>
	</xsl:for-each>
	</div>
</div>
</xsl:template>

</xsl:stylesheet>


