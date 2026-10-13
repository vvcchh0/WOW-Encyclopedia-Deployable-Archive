<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:import href="/WOW-Encyclopedia-Deployable-Archive/wrath/layout/global.xsl"/>
	
	<xsl:template name="styles">
		div.sub-header-top { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="northrend/@background"/>-t.jpg'); }
		div.sub-header-left { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="northrend/@background"/>-l.jpg'); height: 400px; }
		div.sub-header-right { background: url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="northrend/@background"/>-r.jpg'); height: 400px; }
	</xsl:template>
	
	<xsl:template match="northrend">
		<xsl:variable name="zone" select="@zone"/>
		<xsl:variable name="class" select="@class"/>
		<xsl:call-template name="subpage">
			<xsl:with-param name="subtitlename" select="$loc/strs/northrend/str[@id=$zone]"/>  <!-- Header text string -->
		</xsl:call-template>
	</xsl:template>
	
	<xsl:template name="pagecontents">
		<xsl:call-template name="environment">
			<xsl:with-param name="class" select="@class"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template name="environment">
		<xsl:param name="class"/>
		<div class="{$class}">
			<div class="features">
				<div class="features-top">
					<div class="subcat story">
						<div class="top-rule"></div>
						<div class="copy">
							<xsl:variable name="textPath" select="document(concat('../strings/',$lang,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fnorthrend.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffeatures%2F&amp;reason=external-or-uncollected-resource',$class,'.xml'))" />
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
	
	<xsl:template match="zones">
		<div class="zone-list">
			<h2><xsl:value-of select="$loc/strs/northrend/str[@id='name']"/></h2>
			<xsl:for-each select="$zonePath/page/features/environment">
				<xsl:variable name="name" select="name" />
				<a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fnorthrend.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&amp;reason=invalid-overlay-or-uncollected-site-resource" class="zone-menu">
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
				<a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fnorthrend.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffeatures.xml&amp;reason=invalid-overlay-or-uncollected-site-resource"><span>&#171;</span><xsl:value-of select="' '"/><xsl:value-of select="$loc/strs/str[@id='labels.returntofeatures']"/></a>
				<xsl:for-each select="$zonePath/page/features/environment">
					<xsl:variable name="name" select="name" />
					&#160;&#183;&#160;&#160;<a href="/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fnorthrend.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&amp;reason=invalid-overlay-or-uncollected-site-resource"><xsl:value-of select="$loc/strs/str[@id=$name]"/></a>
				</xsl:for-each>
			</div>
		</div>
	</xsl:template>
	
	<xsl:template match="movie">
		<xsl:call-template name="flash">
			<xsl:with-param name="id" select="@id"/>
			<xsl:with-param name="src" select="concat(@root,'/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fnorthrend.xsl&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fflash%2Fglobal%2Fmovieplayer-nosound.swf&amp;reason=external-or-uncollected-resource')"/>
			<xsl:with-param name="wmode" select="'transparent'"/>
			<xsl:with-param name="width" select="'455'"/>
			<xsl:with-param name="height" select="'313'"/>
			<xsl:with-param name="flashvars" select="concat(
			'&amp;flv_file=',@root,@url,
			'&amp;thumb_file=',@root,@thumb
			)"/>	
			<xsl:with-param name="quality" select="'autohigh'"/>
			<xsl:with-param name="noflash"></xsl:with-param>
		</xsl:call-template>
	</xsl:template>

</xsl:stylesheet>