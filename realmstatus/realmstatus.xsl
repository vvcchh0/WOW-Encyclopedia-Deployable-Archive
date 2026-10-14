<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" />

<xsl:template name="rankingRowAlternate">
  <xsl:attribute name="class">
           <xsl:choose>
             <xsl:when test="position() mod 2 = 0">
                serverStatus1
             </xsl:when>
             <xsl:otherwise>
                serverStatus2
             </xsl:otherwise>
           </xsl:choose>		
  </xsl:attribute>		

</xsl:template>


<xsl:template match="/">
<span>


<table cellspacing = "0" cellpadding = "0" border = "0" width = "100%">
<tr>
	<td width = "12"><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-top-left.gif" width = "12" height = "12"/></td>
	<td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-top.gif"></td>
	<td width = "12"><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-top-right.gif" width = "12" height = "12"/></td>
</tr>
<tr>
	<td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-left.gif"></td>
	<td>

				<table cellspacing = "0" cellpadding = "3" width = "100%">
				<tr>
					<td class = "rankingHeader" align = "left" nowrap="nowrap">Status</td>
					<td class = "rankingHeader" align = "left" nowrap="nowrap">Realm Name&#160;</td>
					<td class = "rankingHeader" align = "left" nowrap="nowrap">Type&#160;</td>
					<td class = "rankingHeader" align = "left" nowrap="nowrap">Population&#160;</td>
				</tr>
				<tr>
					<td colspan = "5" background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/shadow.gif"><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/layout/pixel.gif" width = "1" height = "1"/></td>
				</tr>
				<xsl:for-each select="rs/r">

				<tr>
					<td align = "center">
					
						<xsl:call-template name="rankingRowAlternate"/>
					
					
						<xsl:choose>
			                <xsl:when test="@s = 1">
			                   <img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/icons/serverstatus/uparrow.gif" width = "18" height = "18"/>
			                </xsl:when>
			                <xsl:otherwise>
			                   <img src = "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Frealmstatus%2Frealmstatus.xsl&amp;requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fimages%2Ficons%2Fserverstatus%2Fdownarrow.gif&amp;reason=external-or-uncollected-resource" width = "18" height = "18"/>
			                </xsl:otherwise>
		             	</xsl:choose>					
				
					</td>
					<td>
						<xsl:call-template name="rankingRowAlternate"/>
						
						<xsl:choose>
			                <xsl:when test="@s = 1">
			                   <b class = "smallBold" style = "color: #234303;"><xsl:value-of select="@n"/></b>
			                </xsl:when>
			                <xsl:otherwise>
			                   <b class = "smallBold" style = "color: #660D02;"><xsl:value-of select="@n"/></b>
			                </xsl:otherwise>
		             	</xsl:choose>								
						
						
						
					</td>
					<td>
						<xsl:call-template name="rankingRowAlternate"/>
						
						
						<xsl:choose>
			                <xsl:when test="@t = 1">
			                   <small style = "color: #234303;">Normal</small>
			                </xsl:when>
			                <xsl:when test="@t = 2">
			                   <small style = "color: #660D02;">(PVP)</small>
			                </xsl:when>
			                <xsl:when test="@t = 3">
			                   <small style = "color: #535600;">(RP)</small>
			                </xsl:when>
			                <xsl:when test="@t = 4">
			                   <small style = "color: #535600;">(RPPVP)</small>
			                </xsl:when>
		             	</xsl:choose>

					</td>
					<td>					
						<xsl:call-template name="rankingRowAlternate"/>
							<xsl:choose>
				                <xsl:when test="@l = 1">
				                   <small style = "color: #234303;">Low</small>
				                </xsl:when>
				                <xsl:when test="@l = 2">
				                   <small style = "color: #535600;">Medium</small>
				                </xsl:when>
				                <xsl:when test="@l = 3">
				                   <small style = "color: #660D02;">High</small>
				                </xsl:when>
				                <xsl:when test="@l = 4">
				                   <small style = "color: #660D02;">Max (Queued)</small>
				                </xsl:when>							
			             </xsl:choose>					
										
				</td>
				</tr>

                </xsl:for-each>
				</table>

	</td>
	<td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-right.gif"></td>
</tr>
<tr>
	<td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-bot-left.gif" width = "12" height = "11"/></td>
	<td background = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-bot.gif"></td>
	<td><img src = "/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/borders/metalborder/metalborder-bot-right.gif" width = "12" height = "11"/></td>
</tr>
</table>

</span>

</xsl:template>
</xsl:stylesheet>