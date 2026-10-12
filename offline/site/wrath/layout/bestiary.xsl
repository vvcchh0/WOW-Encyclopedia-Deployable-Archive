<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:import href="/wrath/layout/global.xsl"/>
<xsl:template name="styles">
	div.sub-header-top { background-image:url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="bestiary/@background"/>-t.jpg'); }
	div.sub-header-left { background-image:url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="bestiary/@background"/>-l.jpg'); height: 400px; }
	div.sub-header-right { background-image:url('<xsl:value-of select="$baseurl"/>images/layout/<xsl:value-of select="bestiary/@background"/>-r.jpg'); height: 400px; }
</xsl:template>

<xsl:template match="qdrop">
	<div class="qdrop"></div>
</xsl:template>

<xsl:template match="bgfracture">
	<div class="bgshim"><div class="bgfracture"></div></div>
</xsl:template>

<xsl:template match="bestiary">
	<xsl:variable name="class" select="@class"/>
	<xsl:call-template name="subpage">
		<xsl:with-param name="subtitlename" select="$loc/strs/bestiary/str[@id=$class]"/>  <!-- Header text string -->
	</xsl:call-template>
</xsl:template>

<xsl:template name="pagecontents">
	<xsl:call-template name="bestiary">
		<xsl:with-param name="class" select="@class"/>
	</xsl:call-template>
</xsl:template>

<xsl:template name="bestiary">
	<xsl:param name="class"/>
	<xsl:variable name="textPath" select="document(concat('../strings/',$lang,'/features/',$class,'.xml'))" />
	<script language="javascript" src="/wrath/js/bestiary-script.js"></script>
	<div class="{$class}">
		<div class="features">
			<div class="deathknight-top">
				<div class="subcat story">
					<div class="top-rule">
						<div class="little-icicle"></div>
					</div>
					<div class="bestiarySlideshowArrows">
						<a href ="javascript:itemSlideShow(-1)" class="bestiaryArrowLeft"><xsl:value-of select="$loc/strs/str[@id='labels.previous']"/></a>
						<a href ="javascript:itemSlideShow(1)" class="bestiaryArrowRight"><xsl:value-of select="$loc/strs/str[@id='labels.next']"/></a>
					</div>
					<div class="bestiaryRoot">
						<div class="bestiaryFrame">
							<div class="bestiaryLeftBox">
								<div>
									<xsl:for-each select="$textPath/content/maintext">
										<xsl:apply-templates/>
									</xsl:for-each>
								</div>
							</div>
							<div class="bestiaryContainer" id="mainContainer_1">
								<div class="bestiaryContainerTop"></div>
								<div class="bestiaryContainerMiddle">
								
									<div class="bestiaryContainerThumb">
										<div>
											<div style="background-image:url(/wrath/images/bestiary/thumb-creature0.jpg);" onClick="fiatLux(creaturePic)" id="bestiaryThumb1"></div>
										</div>
									</div>

									<span id="loreContainer_1">
										<xsl:apply-templates select="$textPath/content/creatures/creature[last()-1]"/>
									</span>
								</div>
								<div class="bestiaryContainerBottom">
									<div>
										<div id="screenshotThumb1_2" style="left:238px;" onMouseOver="this.style.zIndex='4'; this.style.top='0'" onMouseOut="this.style.zIndex='1'; this.style.top='-10px'"></div>
										<div id="screenshotThumb1_1" style="left:119px;" onMouseOver="this.style.zIndex='4'; this.style.top='0'" onMouseOut="this.style.zIndex='2'; this.style.top='-10px'"></div>
										<div id="screenshotThumb1_0" style="left:0;" onMouseOver="this.style.zIndex='4'; this.style.top='0'" onMouseOut="this.style.zIndex='3'; this.style.top='-10px'"></div>
									</div>
								</div>
							</div>

							<div class="bestiaryContainer" style="left:877px;" id="mainContainer_2">
								<div class="bestiaryContainerTop"></div>
								<div class="bestiaryContainerMiddle">

									<div class="bestiaryContainerThumb">
										<div>
											<div style="background-image:url(/wrath/images/bestiary/thumb-creature1.jpg);" onClick="fiatLux(creaturePic)" id="bestiaryThumb2"></div>
										</div>
									</div>

									<span id="loreContainer_2">
										<xsl:apply-templates select="$textPath/content/creatures/creature[last()]"/>
									</span>
								</div>
								<div class="bestiaryContainerBottom">
									<div>
										<div id="screenshotThumb2_2" style="left:238px;" onMouseOver="this.style.zIndex='4'; this.style.top='0'" onMouseOut="this.style.zIndex='1'; this.style.top='-10px'"></div>
										<div id="screenshotThumb2_1" style="left:119px;" onMouseOver="this.style.zIndex='4'; this.style.top='0'" onMouseOut="this.style.zIndex='2'; this.style.top='-10px'"></div>
										<div id="screenshotThumb2_0" style="left:0;" onMouseOver="this.style.zIndex='4'; this.style.top='0'" onMouseOut="this.style.zIndex='3'; this.style.top='-10px'"></div>
									</div>
								</div>
							</div>

						</div>
						<div style="height:400px;"></div>
						<div style="display:none;" onClick="alert(this.innerHTML)">
							<xsl:for-each select="$textPath/content/creatures/creature">
								<xsl:apply-templates/>
							</xsl:for-each>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div class="features-bot"></div>
	</div>
	<xsl:call-template name="lightbox" />
	<script language="javascript">document.getElementById("loreContainer_1").innerHTML = document.getElementById("creature0").innerHTML; moveItem(2)</script>
</xsl:template>

<xsl:variable name="zonePath" select="document('../features.xml')" />

<xsl:template match="zones" name="zones">
	<div class="zone-list">
		<h2 style="visibility:hidden"><xsl:value-of select="$loc/strs/deathknight/str[@id='name']"/></h2>
		<xsl:for-each select="$zonePath/page/features/deathknight">
			<xsl:variable name="name" select="name" />
			<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fbestiary.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2F%7Burl%7D&reason=invalid-overlay-or-uncollected-site-resource" class="zone-menu">
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
			<a href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Flayout%2Fbestiary.xsl&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ffeatures.xml&reason=invalid-overlay-or-uncollected-site-resource"><span>&#171;</span><xsl:value-of select="' '"/><xsl:value-of select="$loc/strs/str[@id='labels.returntofeatures']"/></a>
		</div>
	</div>
</xsl:template>

</xsl:stylesheet>


