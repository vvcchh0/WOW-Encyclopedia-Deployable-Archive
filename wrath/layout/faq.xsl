<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/WOW-Encyclopedia-Deployable-Archive/wrath/layout/global.xsl"/>

<xsl:template name="styles">
	div.sub-header-top { background: url('images/layout/header9-t.jpg'); }
	div.sub-header-left { background: url('images/layout/header9-l.jpg'); height: 400px; }
	div.sub-header-right { background: url('images/layout/header9-r.jpg'); height: 400px; }
	div.sub-text-container { margin: 0; }
</xsl:template>

<xsl:template match="faq">
	<xsl:variable name="faqdocument" select="document(concat('../strings/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Ffaq.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffaq.xml&amp;reason=external-or-uncollected-resource'))"/>
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$faqdocument/content/@name"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>

<xsl:template name="pagecontents">
<xsl:variable name="faqdocument" select="document(concat('../strings/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Ffaq.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffaq.xml&amp;reason=external-or-uncollected-resource'))"/>
	<a name="top"></a>
	<div class="blacktop"></div>
	<div class="blackmid">
		<div class="faq">
			<xsl:call-template name="questionlist">
				<xsl:with-param name="faqdocument" select="$faqdocument"/>
			</xsl:call-template>
			<div class="hr"/>
			<xsl:call-template name="faqlist">
				<xsl:with-param name="faqdocument" select="$faqdocument"/>
			</xsl:call-template>		
	
		</div>
	</div>
	<div class="blackbot"></div>
</xsl:template>

<xsl:template name="questionlist">
<xsl:param name="faqdocument"/>
	<xsl:for-each select="$faqdocument/content/category">
		<h1><xsl:value-of select="@name"/></h1>
		<ul>
		<xsl:for-each select="faq">
			<li><a href = "#{count(parent::*/preceding-sibling::*) + 1}_{position()}"><xsl:value-of select="@question"/></a></li>
		</xsl:for-each>
		</ul>
		<br/>
	</xsl:for-each>

</xsl:template>

<xsl:template name="faqlist">
<xsl:param name="faqdocument"/>
	<xsl:for-each select="$faqdocument/content/category">
		<h1><xsl:value-of select="@name"/></h1>
		<blockquote>
		<xsl:for-each select="faq">
			<a name="{count(parent::*/preceding-sibling::*) + 1}_{position()}"></a>
			<h2><xsl:value-of select="@question"/></h2>
			<p>
			<xsl:apply-templates />
			</p>
			<div class="hr"><div class="top">[ <a href="#top"><xsl:value-of select="$loc/strs/str[@id='wrath.labels.faqtop']"/></a> ]</div></div>
			
		</xsl:for-each>
		</blockquote>
		<br/>
	</xsl:for-each>

</xsl:template>


</xsl:stylesheet>




