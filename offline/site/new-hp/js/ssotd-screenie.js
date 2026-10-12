/* Omega Skip's Lightbox - SAFETY NOT GUARANTEED! */
/* Memo to self: Clean up this code, for it is wretched */
/* ############# GLOBAL VARIABLES, DEFAULT VALUES ############# */

ticked = 0;
hideMe = true;
sliderTicked = 0;
loadBarTicked = 0;
nowViewing = 0;
animationLock = false;
currentPage = 0;
shotsPerPage = 12;
firstLoad = true;
shotList = new Array(); 
slideShow = false;
slideShowDirection = 1;
linkString = "Click to generate a link <br>to this screenshot";

quadrantFader = "";
quadrantTicked = 0;
quadCounter = 0;
quadSpeed = 250; //*4 = Time between slides
/* ############# FUNCTIONS ############# */

function addEvent(obj, evType, fn)
{  
 if (obj.addEventListener){ obj.addEventListener(evType, fn, false); return true; }
 else if (obj.attachEvent){ var r = obj.attachEvent("on"+evType, fn); return r; } else { return false; }
}
 
function linkHere() { document.location = "#" + (currentShotNumber - nowViewing); }

function omegaLightBox(thisScreenshot)
{
	nowViewing = eval(thisScreenshot);
	screenImage = new Image();
	screenImage.src = shotList[nowViewing];
	nextShot = new Image();
	nextShot.src = (shotList[nowViewing+1]) ? shotList[nowViewing+1] : shotList[0];
	prevShot = new Image();
	prevShot.src = (shotList[nowViewing-1]) ? shotList[nowViewing-1] : shotList[shotList.length-1];
	/**/
	if(!document.getElementById("dumpster"))
	{ 
		closeGifElement = document.createElement("div");
		closeGifElement.onclick = function(){this.style.backgroundPosition = "0 top"; setHide(true); hideScreenie()};
		closeGifElement.onmouseover = function(){ this.style.backgroundPosition = "0 bottom"; };
		closeGifElement.onmouseout = function(){ this.style.backgroundPosition = "0 top"; };
		closeGifElement.className = "closeDivStyle";

		backGifElement = document.createElement("div");
		backGifElement.onclick = function(){prevScreenshot()};
		backGifElement.onmouseover = function(){ this.style.backgroundPosition = "0 bottom"; };
		backGifElement.onmouseout = function(){ this.style.backgroundPosition = "0 top"; };
		backGifElement.className = "backGifStyle";
		
		fwdGifElement = document.createElement("div");
		fwdGifElement.onclick = function(){nextScreenshot()};
		fwdGifElement.onmouseover = function(){ this.style.backgroundPosition = "0 bottom"; };
		fwdGifElement.onmouseout = function(){ this.style.backgroundPosition = "0 top"; };
		fwdGifElement.className = "fwdGifStyle";
		
		linkDivElement = document.createElement("div");
		linkDivElement.onclick = function(){linkHere(); };
		linkDivElement.onmouseover = function(){ this.style.backgroundPosition = "0 bottom"; showTip(linkString); };
		linkDivElement.onmouseout = function(){ this.style.backgroundPosition = "0 top"; hideTip(); };
		linkDivElement.className = "linkHereStyle";

		quadParent = document.createElement("div");
		quadParent.onmouseover = function(){ if(!slideShow) this.style.backgroundPosition = "0 bottom"; };
		quadParent.onmouseout = function(){ if(!slideShow) this.style.backgroundPosition = "0 top"; };
		quadParent.onclick = function(){ launchSlideShow();};
		quadParent.className = "quadStyle";
		
		anchorElement = document.createElement("div");
		anchorElement.className = "anchorStyle";
		
		quadElement1 = document.createElement("div");
		quadElement1.id = "quad0";
		quadElement1.className = "quad1Style";

		quadElement2 = document.createElement("div");
		quadElement2.id = "quad1";
		quadElement2.className = "quad2Style";

		quadElement3 = document.createElement("div");
		quadElement3.id = "quad2";
		quadElement3.className = "quad3Style";

		quadElement4 = document.createElement("div");
		quadElement4.id = "quad3";
		quadElement4.className = "quad4Style";

		quadParent.appendChild(anchorElement);
		
		anchorElement.appendChild(quadElement1);
		anchorElement.appendChild(quadElement2);
		anchorElement.appendChild(quadElement3);
		anchorElement.appendChild(quadElement4);

		screenie2Element = document.createElement("div");
		screenie2Element.id = "Screenie2";
		screenie2Element.className = "screenie2Style";
		screenie2Element.onclick = function(){nextScreenshot()};

		screenieElement = document.createElement("div");
		screenieElement.id = "Screenie";
		screenieElement.className = "screenieStyle";
		screenieElement.onmouseover = function(){setHide(false)};
		screenieElement.onmouseout = function(){setHide(true);};		
		screenieElement.appendChild(closeGifElement);
		screenieElement.appendChild(fwdGifElement);
		screenieElement.appendChild(linkDivElement);
		screenieElement.appendChild(quadParent);
		screenieElement.appendChild(backGifElement);
		screenieElement.appendChild(screenie2Element);

		centerElement = document.createElement("center");
		centerElement.appendChild(screenieElement);
		
		pictureFrameElement = document.createElement("div");
		pictureFrameElement.id = "pictureFrame";
		pictureFrameElement.className = "pictureFrameStyle";
		pictureFrameElement.onclick = function(){hideScreenie()};
		pictureFrameElement.appendChild(centerElement);
		
		c0verElement = document.createElement("div");
		c0verElement.id = "c0ver";
		c0verElement.className = "c0verStyle";
		c0verElement.onclick = function(){hideScreenie()};
		
		redBlockElement = document.createElement("div");
		redBlockElement.id = "redBlock";
		redBlockElement.appendChild(c0verElement);
		redBlockElement.appendChild(pictureFrameElement);

		dumpsterElement = document.createElement("div");
		dumpsterElement.id = "dumpster";
		dumpsterElement.className = "dumpsterStyle";
		dumpsterElement.appendChild(redBlockElement);
		
		document.getElementsByTagName("body")[0].appendChild(dumpsterElement);
		addEvent(window, 'resize', adjustBackgroundStuff);
	}
	/**/
	loadScreenshot(nowViewing);
	document.getElementsByTagName("body")[0].appendChild(document.getElementById("redBlock"));
}

function loadScreenshot(thisScreenshot)
{
	adjustBackgroundStuff();
  if(screenImage.complete && !animationLock)
	{	
		document.getElementById("Screenie").style.height = screenImage.height + "px";
		document.getElementById("Screenie").style.width = "1px";
		document.getElementById("Screenie").style.backgroundImage = "url('"+screenImage.src+"')";
		animationLock = true;
		startTheAnimation = window.setInterval("resizeScreenshot()",10);
	}
	else { window.setTimeout("loadScreenshot('"+thisScreenshot+"')",250); }
}


function resizeScreenshot()
{
	targwidth =  screenImage.width;
  targwidth = (!targwidth % 2)?targwidth--:targwidth
	if (ticked >= 210)
  {
		ticked = 0;
		animationLock = false;
    window.clearInterval(startTheAnimation);							//stop the animation
	}
	else
	{
		document.getElementById("Screenie").style.width = (targwidth*ticked/200) + "px";
		ticked += 10;
	}
}

function adjustBackgroundStuff()
{
	windowHeight = (window.innerHeight) ? window.innerHeight : document.body.clientHeight;
	windowWidth = (window.innerWidth) ? window.innerWidth : document.body.clientHeight;
	document.getElementById("c0ver").style.width = document.body.scrollWidth + "px";
	document.getElementById("c0ver").style.height = document.body.scrollHeight + "px";
	document.getElementById("pictureFrame").style.top = document.body.scrollTop + 60 + "px";
	
}

function setHide(thisValue) { hideMe = thisValue; }

function hideScreenie()
{
	if (hideMe)
	{
		document.getElementById("Screenie").style.width = "1px";
		document.getElementById("Screenie").style.height = "1px";
		resetSlideShow();
		document.getElementById("dumpster").appendChild(document.getElementById("redBlock"));
	}
}

function prevScreenshot()
{
	if(!animationLock)
	{
		resetSlideShow();
		backGifElement.style.backgroundPosition = "0 bottom";
		fwdGifElement.style.backgroundPosition = "0 top";
		quadParent.className = "quadStyleB"
		quadElement1.className = "quad1StyleB";
		quadElement2.className = "quad2StyleB";
		quadElement3.className = "quad3StyleB";
		quadElement4.className = "quad4StyleB";
		slideShowDirection = -1;
		slideShowResizerPrev();
	}
}

function nextScreenshot()
{
	if(!animationLock)
	{
		resetSlideShow();
		backGifElement.style.backgroundPosition = "0 top";
		fwdGifElement.style.backgroundPosition = "0 bottom";
		quadParent.className = "quadStyle"
		quadElement1.className = "quad1Style";
		quadElement2.className = "quad2Style";
		quadElement3.className = "quad3Style";
		quadElement4.className = "quad4Style";
		slideShowDirection = 1;
		slideShowResizer();
	}
}

function resetSlideShow()
{
	if(slideShow)
	{
		quadParent.style.backgroundPosition = "0 top";
		quadElement1.style.opacity = quadElement2.style.opacity = quadElement3.style.opacity = quadElement4.style.opacity = 0;
		quadElement1.style.filter = quadElement2.style.filter = quadElement3.style.filter = quadElement4.style.filter = "alpha(opacity=0)";
		slideShow = false;
		window.clearInterval(quadrantFader);
		quadrantTicked = 0;
	}
}

function launchSlideShow()
{
	if(!animationLock)
	{
		if(!slideShow)
		{
			slideShow = true;
			quadElement1.style.opacity = quadElement2.style.opacity = quadElement3.style.opacity = quadElement4.style.opacity = 1;
			quadElement1.style.filter = quadElement2.style.filter = quadElement3.style.filter = quadElement4.style.filter = "alpha(opacity=100)";
			quadCounter = 3*((1-slideShowDirection)/2);
			activeQuadrant = document.getElementById("quad"+quadCounter);
			quadrantFader = window.setInterval("quadrantFade()",10);
		}
		else
		{
			resetSlideShow();
		}
	}
}

function quadrantFade()
{
	if (quadrantTicked > quadSpeed)
  {
    window.clearInterval(quadrantFader);
		quadrantTicked = 0;
		quadCounter += slideShowDirection;
		if(quadCounter <= 3 && quadCounter >= 0)
		{
			activeQuadrant = document.getElementById("quad"+quadCounter);
			quadrantFader = window.setInterval("quadrantFade()",10);
		}
		else
		{
			if(slideShow)
			{
				if(slideShowDirection == 1)
				{
					quadCounter = 0;
					backGifElement.style.backgroundPosition = "0 top";
					fwdGifElement.style.backgroundPosition = "0 bottom";
					slideShowResizer();
				}
				else
				{
					quadCounter = 3;
					backGifElement.style.backgroundPosition = "0 bottom";
					fwdGifElement.style.backgroundPosition = "0 top";
					slideShowResizerPrev();
				}
			}
		}
	}
	else
	{
		activeQuadrant.style.opacity = 1 - (quadrantTicked/quadSpeed);
		activeQuadrant.style.filter = "alpha(opacity="+(100 - 100*(quadrantTicked/quadSpeed))+")";
		quadrantTicked += 10;
	}
}

function resizeNewScreenshot()
{
	if (sliderTicked >= 160)
  {
    window.clearInterval(startTheResizer);
		document.getElementById("Screenie").style.backgroundImage = "url('"+shotList[nowViewing]+"')";
		document.getElementById("Screenie2").style.opacity = 0;
		document.getElementById("Screenie2").style.filter = "alpha(opacity=0)";
		sliderTicked = 0;
		animationLock = false;
		delete prevShot;
		prevShot = screenImage;
		delete screenImage;
		screenImage = nextShot;
		delete nextShot;
		nextShot = new Image();
		nextShot.src = (shotList[nowViewing+1]) ? shotList[nowViewing+1] : shotList[0];
		if(slideShow)
		{
			quadCounter = 3*((1-slideShowDirection)/2);
			activeQuadrant = document.getElementById("quad"+quadCounter);
			quadElement1.style.opacity = quadElement2.style.opacity = quadElement3.style.opacity = quadElement4.style.opacity = 1;
			quadElement1.style.filter = quadElement2.style.filter = quadElement3.style.filter = quadElement4.style.filter = "alpha(opacity=100)";
			quadrantFader = window.setInterval("quadrantFade()",10);
		}
	}
	else
	{
		document.getElementById("Screenie2").style.opacity = sliderTicked/150;
		document.getElementById("Screenie2").style.filter = "alpha(opacity="+(sliderTicked/150)*100+")"; //;
		document.getElementById("Screenie").style.width = (screenImage.width+(deltaX*sliderTicked/150)) + "px";
		document.getElementById("Screenie").style.height = (screenImage.height+(deltaY*sliderTicked/150)) + "px";
		sliderTicked += 10;
	}
}

function resizeNewScreenshotPrev()
{
	if (sliderTicked >= 160)
  {
    window.clearInterval(startTheResizerPrev);
		document.getElementById("Screenie").style.backgroundImage = "url('"+shotList[nowViewing]+"')";
		document.getElementById("Screenie2").style.opacity = 0;
		document.getElementById("Screenie2").style.filter = "alpha(opacity=0)";
		sliderTicked = 0;
		animationLock = false;
		delete nextShot;
		nextShot = screenImage;
		delete screenImage;
		screenImage = prevShot;
		delete prevShot;
		prevShot = new Image();
		prevShot.src = (shotList[nowViewing-1]) ? shotList[nowViewing-1] : shotList[shotList.length-1];
		if(slideShow)
		{
			quadCounter = 3*((1-slideShowDirection)/2);
			activeQuadrant = document.getElementById("quad"+quadCounter);
			quadElement1.style.opacity = quadElement2.style.opacity = quadElement3.style.opacity = quadElement4.style.opacity = 1;
			quadElement1.style.filter = quadElement2.style.filter = quadElement3.style.filter = quadElement4.style.filter = "alpha(opacity=100)";
			quadrantFader = window.setInterval("quadrantFade()",10);
		}
	}
	else
	{
		document.getElementById("Screenie2").style.opacity = sliderTicked/150;
		document.getElementById("Screenie2").style.filter = "alpha(opacity="+(sliderTicked/150)*100+")"; //;
		document.getElementById("Screenie").style.width = (screenImage.width+(deltaX*sliderTicked/150)) + "px";
		document.getElementById("Screenie").style.height = (screenImage.height+(deltaY*sliderTicked/150)) + "px";
		sliderTicked += 10;
	}
}

function pause() { alert("STOP! Hammertime!"); }

function slideShowResizer()
{
	animationLock = true;
	if(nextShot.complete)
	{
		document.getElementById("Screenie").style.cursor = "default";
		nowViewing = (shotList[nowViewing+1]) ? nowViewing+1 : 0;
		document.getElementById("Screenie2").style.backgroundImage = "url('"+nextShot.src+"')";
		deltaY = nextShot.height - screenImage.height;
		deltaX = nextShot.width - screenImage.width;
		screenie2Element.onclick = function(){nextScreenshot()};
		startTheResizer = window.setInterval("resizeNewScreenshot()",10);
		if(nowViewing%12 == 0) galleryNext();
	}
	else
	{
		document.getElementById("Screenie").style.cursor = "wait";
		window.setTimeout("slideShowResizer()",250);
	}
}

function slideShowResizerPrev()
{
	animationLock = true;
	if(prevShot.complete)
	{
		if(nowViewing%12 == 0) galleryPrev();
		document.getElementById("Screenie").style.cursor = "default";
		nowViewing = (shotList[nowViewing-1]) ? nowViewing-1 : shotList.length-1;
		document.getElementById("Screenie2").style.backgroundImage = "url('"+prevShot.src+"')";
		deltaY = prevShot.height - screenImage.height;
		deltaX = prevShot.width - screenImage.width;
		screenie2Element.onclick = function(){prevScreenshot()};
		startTheResizerPrev = window.setInterval("resizeNewScreenshotPrev()",10);
	}
	else
	{
		document.getElementById("Screenie").style.cursor = "wait";
		window.setTimeout("slideShowResizerPrev()",250);
	}
}


/* -- N.E.D.M. -- */

function addshots(dir,filename,endnum)
{
	startnum = 0;
	for(i=endnum; i>0; i--)
	{
		shotList[endnum-i] = "" + dir + "/" + filename + (i) +".jpg";
	}
	printPages();
}

function printPages()
{
	numPages = Math.ceil(shotList.length/shotsPerPage);
	if(document.location.href.split("#")[1] > 0 && firstLoad)
	{
		calculatedIndex = currentShotNumber - document.location.href.split("#")[1];
		currentPage = Math.floor(calculatedIndex/shotsPerPage);	
	}
	outString = "";
	for(i = 0; i < shotsPerPage; i++)
	{
		n = shotsPerPage*currentPage+i;
		if(shotList[n])
		{
			thumbnail = shotList[n].replace(".jpg","-thumb.jpg");
			outString += "<div><div><a href='javascript:omegaLightBox("+n+")'><img src='"+thumbnail+"'></a></div></div>";
		}
	}
	document.getElementById("galleryPictures").innerHTML = outString;
	document.getElementById("pageNum").innerHTML = "" + Number(currentPage+1) + " of " + numPages + "";
	if(document.location.href.split("#")[1] != null && firstLoad)
	{
		if(document.location.href.split("#")[1] > 0) { window.setTimeout('omegaLightBox(calculatedIndex)',250); }
		else { window.setTimeout('omegaLightBox(0)',250); }
		firstLoad = false;
	}
}

function galleryPrev()
{
	if(currentPage > 0) { currentPage--; }
	else { currentPage = numPages-1; }
	printPages();
}

function galleryNext()
{
	if(currentPage < numPages-1) { currentPage++; }
	else { currentPage = 0; }
	printPages();
}

function ThumbSize(size) 
{
	currimage = shotsPerPage * currentPage; 
	shotsPerPage = (size=="sixteen")?16:(size=="twelve")?12:9;
	document.getElementById("galleryPictures").className = "pictureGallery " + size;
	currentPage = Math.floor(currimage / shotsPerPage);
	printPages();
	if(currentPage > numPages)
	{
		currentPage = numPages-1;
		printPages();
	}
}
