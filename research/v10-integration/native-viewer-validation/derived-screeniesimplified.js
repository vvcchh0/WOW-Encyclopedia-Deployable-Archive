/* Omega Skip's Lightbox - SAFETY NOT GUARANTEED! */
/* Memo to self: Clean up this code, for it is wretched */
/* ############# GLOBAL VARIABLES ############# */

ticked = 0;
hideMe = true;
sliderTicked = 0;
nowViewing = 0;
animationLock = false;

/* ############# FUNCTIONS ############# */

function goToHighRes() 
{
	var currentScreen = nowViewing + 1;
	window.location = theDirectory +"ss"+currentScreen +"-hires.jpg";
}

function loadCheckForShot() {
	shotList = new Array();
	dirList = new Array();
	hiResList = new Array();
	theShot = 1;
	for(i=0; i<screenshotsTotal; i++) {
		if (i == screenshotsCommonTotal){
			theDirectory = theLocDirectory;
			theShot = 1;
		}
		shotList[i] = theDirectory+"ss"+(theShot)+".jpg";
		dirList[i] = theDirectory;
		hiResList[i] = theShot;
		theShot++;
	}
	checkForSpecifiedShot = new URLSearchParams(window.location.search).getAll("s");
nowViewing = 1;
if (checkForSpecifiedShot.length === 1 && /^[0-9]+$/.test(checkForSpecifiedShot[0])) {
	var parsedShot = Number(checkForSpecifiedShot[0]);
	if (Number.isSafeInteger(parsedShot) &&
		parsedShot >= 1 &&
		typeof shotList !== "undefined" &&
		parsedShot <= shotList.length)
		nowViewing = parsedShot;
}

	omegaLightBox(nowViewing-1);
	document.getElementById("dCurrent").innerHTML = nowViewing+1;
	ieCrutch = nowViewing + 1;
	document.getElementById("screenLink").href = dirList[nowViewing] +"ss"+ hiResList[nowViewing] +"-hires.jpg";
	document.getElementById("dTotal").innerHTML = shotList.length;
}

function omegaLightBox(thisScreenshot)
{
	nowViewing = thisScreenshot;
	screenImage = new Image();
	screenImage.src = shotList[nowViewing];
	nextShot = new Image();
	nextShot.src = (shotList[nowViewing+1]) ? shotList[nowViewing+1] : shotList[0];
	prevShot = new Image();
	prevShot.src = (shotList[nowViewing-1]) ? shotList[nowViewing-1] : shotList[shotList.length-1];
	loadScreenshot(nowViewing);
}

function loadScreenshot(thisScreenshot)
{
  if(screenImage.complete && !animationLock)
	{
		document.getElementById("Screenie").style.width = screenImage.width + "px";
		document.getElementById("Screenie").style.height = screenImage.height + "px";
		document.getElementById("Screenie2").style.width = screenImage.width + "px";
		document.getElementById("Screenie2").style.height = screenImage.height + "px";
		document.getElementById("Screenie").style.backgroundImage = "url('"+screenImage.src+"')";
		if(navigator.userAgent.indexOf("MSIE") != -1)
		{
			document.getElementById("imageRoot").style.display = "block";
			ieTestImage = new Image();
			ieTestImage.src = shotList[nowViewing];
			resizeFixForIESix();
		}
		else document.getElementById("imageRoot").style.display = "table";
	}
	else
	{
		document.getElementById("Screenie").style.height = "450px";
		document.getElementById("Screenie").style.width = "700px";
		window.setTimeout("loadScreenshot('"+thisScreenshot+"')",250);
	}
}

function prevScreen() {nextScreenshot();}
function nextScreen() {prevScreenshot();}

function nextScreenshot() { if(!animationLock) slideShowNextFader(); }
function prevScreenshot() { if(!animationLock) slideShowPrevFader(); }

function slideShowNextFader()
{
	animationLock = true;
	if(nextShot.complete)
	{
		document.getElementById("Screenie").style.cursor = "default";
		nowViewing = (shotList[nowViewing+1]) ? nowViewing+1 : 0;
		document.getElementById("Screenie2").style.backgroundImage = "url('"+nextShot.src+"')";
		deltaY = nextShot.height - screenImage.height;
		deltaX = nextShot.width - screenImage.width;
		document.getElementById("Screenie2").onclick = function(){nextScreenshot()};
		startTheFader = window.setInterval("fadeInNextScreenshot()",10);
	}
	else
	{
		document.getElementById("Screenie").style.cursor = "wait";
		window.setTimeout("slideShowNextFader()",250);
	}
}

function slideShowPrevFader()
{
	animationLock = true;
	if(prevShot.complete)
	{
		document.getElementById("Screenie").style.cursor = "default";
		nowViewing = (shotList[nowViewing-1]) ? nowViewing-1 : shotList.length-1;
		document.getElementById("Screenie2").style.backgroundImage = "url('"+prevShot.src+"')";
		deltaY = prevShot.height - screenImage.height;
		deltaX = prevShot.width - screenImage.width;
		document.getElementById("Screenie2").onclick = function(){prevScreenshot()};
		startTheFaderPrev = window.setInterval("fadeInPrevScreenshot()",10);
	}
	else
	{
		document.getElementById("Screenie").style.cursor = "wait";
		window.setTimeout("slideShowPrevFader()",250);
	}
}

function resizeFixForIESix()
{
	if(ieTestImage.complete)
	{
		if(!document.getElementById("frankenImage"))
		{
			frankenImageElement = document.createElement("img");
			frankenImageElement.id = "frankenImage";
			frankenImageElement.style.visibility = "visible";
			frankenImageElement.style.position = "absolute";
			frankenImageElement.style.top = "0";
			frankenImageElement.style.left = "0";
			document.getElementsByTagName("body")[0].appendChild(frankenImageElement);
		}
		document.getElementById("frankenImage").src = ieTestImage.src;
		document.getElementById("Screenie").style.width = document.getElementById("frankenImage").width + "px";
		document.getElementById("Screenie").style.height = document.getElementById("frankenImage").height + "px";
		animationLock = false;
		delete ieTestImage;
		if(!document.getElementById("trashCompactor"))
		{
			disposalElement = document.createElement("div");
			disposalElement.id = "trashCompactor";
			disposalElement.display = "none";
			document.getElementsByTagName("body")[0].appendChild(disposalElement);
		}
		document.getElementById("trashCompactor").appendChild(document.getElementById("frankenImage"));
		document.getElementById("trashCompactor").removeChild(document.getElementById("trashCompactor").firstChild);
	}
	else
	{
		window.setTimeout("resizeFixForIESix()",250);
	}
}

function fadeInNextScreenshot()
{
		window.clearInterval(startTheFader);							//stop the animation
		document.getElementById("Screenie").style.backgroundImage = "url('"+shotList[nowViewing]+"')";
		document.getElementById("Screenie2").style.opacity = 0;
		document.getElementById("Screenie2").style.filter = "alpha(opacity=0)";
		document.getElementById("Screenie").style.width = (screenImage.width+deltaX) + "px";
		document.getElementById("Screenie").style.height = (screenImage.height+deltaY) + "px";
		document.getElementById("Screenie2").style.width = (screenImage.width+deltaX) + "px";
		document.getElementById("Screenie2").style.height = (screenImage.height+deltaY) + "px";
		sliderTicked = 0;
		delete prevShot;
		prevShot = screenImage;
		delete screenImage;
		screenImage = nextShot;
		delete nextShot;
		nextShot = new Image();
		nextShot.src = (shotList[nowViewing+1]) ? shotList[nowViewing+1] : shotList[0];
		document.getElementById("dCurrent").innerHTML = ieCrutch = nowViewing+1;
		document.getElementById("screenLink").href = dirList[nowViewing] +"ss"+ hiResList[nowViewing] +"-hires.jpg";
		if(navigator.userAgent.indexOf("MSIE") != -1)
		{
			ieTestImage = new Image();
			ieTestImage.src = shotList[nowViewing];
			resizeFixForIESix();
		}
		else animationLock = false;
}

function fadeInPrevScreenshot()
{
		window.clearInterval(startTheFaderPrev);							//stop the animation
		document.getElementById("Screenie").style.backgroundImage = "url('"+shotList[nowViewing]+"')";
		document.getElementById("Screenie2").style.opacity = 0;
		document.getElementById("Screenie2").style.filter = "alpha(opacity=0)";
		document.getElementById("Screenie").style.width = (screenImage.width+deltaX) + "px";
		document.getElementById("Screenie").style.height = (screenImage.height+deltaY) + "px";
		document.getElementById("Screenie2").style.width = (screenImage.width+deltaX) + "px";
		document.getElementById("Screenie2").style.height = (screenImage.height+deltaY) + "px";
		sliderTicked = 0;
		delete nextShot;
		nextShot = screenImage;
		delete screenImage;
		screenImage = prevShot;
		delete prevShot;
		prevShot = new Image();
		prevShot.src = (shotList[nowViewing-1]) ? shotList[nowViewing-1] : shotList[shotList.length-1];
		document.getElementById("dCurrent").innerHTML = ieCrutch = nowViewing+1;
		document.getElementById("screenLink").href = dirList[nowViewing] +"ss"+ hiResList[nowViewing] +"-hires.jpg";
		if(navigator.userAgent.indexOf("MSIE") != -1)
		{
			ieTestImage = new Image();
			ieTestImage.src = shotList[nowViewing];
			resizeFixForIESix();
		}
		else animationLock = false;
}

window.onload = loadCheckForShot;

/* -- N.E.D.M. -- */