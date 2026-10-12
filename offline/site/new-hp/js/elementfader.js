//Global Variables + Constants
fadeAnimationLock = false;
fadeElementRegistry = new Array();
registryPointer = 0;

//Objects + Methods
function FaderElement(thisElement,thisTimer,thisID,thisInterval,thisDirection)
{
	this.fadeElement = thisElement;
	this.animTimer = thisTimer;
	this.elementID = thisID;
	this.fadeInterval = false;
	this.fadeDirection = -1;
	
	this.fade = elementFadeFunction;
	
	fadeElementRegistry[registryPointer++] = this;
}

function elementFadeFunction(thisElement)
{
	if(this.animTimer > 250)
	{
		window.clearInterval(this.fadeInterval);
		this.animTimer = 0;
		this.fadeInterval = false;
	}
	else
	{
		this.fadeElement.style.opacity = this.fadeDirection*(this.animTimer/250)*1+((1-this.fadeDirection)/2);
		this.fadeElement.style.filter = "alpha(opacity="+eval(this.fadeDirection*(this.animTimer/250)*100+(100*(1-this.fadeDirection)/2))+")";
		this.animTimer += 10;
	}
}

//UI Functions
function getFaderById(thisID)
{
	faderFound = false;
	for(i=0; i<fadeElementRegistry.length; i++)
	{
		if (fadeElementRegistry[i].elementID = thisID) faderFound = fadeElementRegistry[i];
	}
	return faderFound;
}

function fadeElement(thisID)
{
	if(!getFaderById(thisID+"Fader"))
	{
		newFader = new FaderElement(document.getElementById(thisID),0,thisID+"Fader")
		newFader.fadeInterval = window.setInterval("getFaderById('"+thisID+"Fader').fade()",10);
	}
	else if(!getFaderById(thisID+"Fader").fadeInterval)
	{
		getFaderById(thisID+"Fader").fadeDirection = -1;
		getFaderById(thisID+"Fader").fadeInterval = window.setInterval("getFaderById('"+thisID+"Fader').fade()",10);
	}
	else getFaderById(thisID+"Fader").fadeDirection = -1;
}

function unFadeElement(thisID)
{
	if(!getFaderById(thisID+"Fader"))
	{
		newFader = new FaderElement(document.getElementById(thisID),0,thisID+"Fader")
		getFaderById(thisID+"Fader").fadeDirection = 1;
		newFader.fadeInterval = window.setInterval("getFaderById('"+thisID+"Fader').fade()",10);
	}
	else if(!getFaderById(thisID+"Fader").fadeInterval)
	{
		getFaderById(thisID+"Fader").fadeDirection = 1;
		newFader.fadeInterval = window.setInterval("getFaderById('"+thisID+"Fader').fade()",10);
	}
	else getFaderById(thisID+"Fader").fadeDirection = 1;
}