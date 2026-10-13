// Global Variables
portalOpen = false;
xmlFrameTarget = "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fenhancedtip.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fen_us%2Fdarkportal.htm&reason=invalid-overlay-or-uncollected-site-resource";
currentDomain = "worldofwarcraft.com";
xmlRetrievalFrame = false;
currentlyViewing = "";
threadCounter = 0;

//Functions
function enhancedXmlTTip(thisID)
{
	currentlyViewing = thisID;
	if(document.getElementById(thisID) != null)
	{
		showTip(document.getElementById(thisID).innerHTML);
	}
	else
	{
		showTip("Loading...");
		requestHTML(thisID);
	}
}

function requestHTML(thisID)
{
	if(portalOpen)
	{
		darkPortal.requestXml(thisID);
	}
	else if(!xmlRetrievalFrame)
	{
		xmlRetrievalFrame = document.createElement("iframe");
		xmlRetrievalFrame.name = "darkPortalFrame"; //We put the FUN! in "function"
		xmlRetrievalFrame.id = "xmlPortal";
		xmlRetrievalFrame.style.display = "none";
		document.getElementsByTagName("body")[0].appendChild(xmlRetrievalFrame);
		document.domain = currentDomain;
		xmlRetrievalFrame.src = xmlFrameTarget;
	}
}

function openPortal()
{
	darkPortal = (frames["darkPortalFrame"]) ? frames["darkPortalFrame"] : document.getElementById("xmlPortal").contentWindow;
	portalOpen = true;
	tooltipBuffer = document.createElement("div");
	tooltipBuffer.id = "tooltipBufferDiv";
	tooltipBuffer.style.display = "none";
	document.getElementsByTagName("body")[0].appendChild(tooltipBuffer);
	requestHTML(currentlyViewing);
}

function receivceHTML(thisHTML, thisID)
{
	var newHtmlHolder = document.createElement("div");
	newHtmlHolder.id = thisID;
	newHtmlHolder.innerHTML = thisHTML;
	tooltipBuffer.appendChild(newHtmlHolder);
	if(isShowing && currentlyViewing == thisID) { showTip(thisHTML); }
}