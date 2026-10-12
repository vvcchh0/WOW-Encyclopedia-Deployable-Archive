/* Omega Skip's Lightbox - SAFETY NOT GUARANTEED! */
/* Memo to self: Clean up this code, for it is wretched */
/* ############# GLOBAL VARIABLES, DEFAULT VALUES ############# */



ticked = 0;
hideMe = true;
sliderTicked = 0;
nowViewing = 0;
animationLock = false;
currentPage = 0;
shotsPerPage = 12;

//alert("Screenie Loaded")
/* ############# FUNCTIONS ############# */

/*
<div id="dumpster" style="display:none;">
	<div id="redBlock">
		<div id="c0ver" onClick="hideScreenie();" class="coverStyle"></div>
		<div id="pictureFrame" onClick="hideScreenie();" class="pictureFrameStyle">
			<center>
				<div id="Screenie" onClick="nextScreenshot();" onMouseOver="hideMe = false;" onMouseOut="hideMe = true;" class="screenieStyle">
					<div id="Screenie2" class="screenieStyle" style="width:100%; height:100%; opacity:0; filter:alpha(opacity=0);"></div>
				</div>
			</center>
		</div>
	</div>
</div>
*/

function omegaLightBox(thisScreenshot, omegaoverride)
{
	if(omegaoverride)
	{ 
	screenImage = new Image();
	screenImage.src = thisScreenshot; nextShot = prevShot = fwdGifElement = backGifElement = null; 
	}
	else { 
	nowViewing = thisScreenshot;
	screenImage = new Image();
	screenImage.src = shotList[nowViewing];
	nextShot = new Image();
	nextShot.src = (shotList[nowViewing+1]) ? shotList[nowViewing+1] : shotList[0];
	prevShot = new Image();
	prevShot.src = (shotList[nowViewing-1]) ? shotList[nowViewing-1] : shotList[shotList.length-1];
	}
	
	
		
	/**/
	if(!document.getElementById("dumpster"))
	{
		
		closeGifElement = document.createElement("img");
		closeGifElement.src = "/new-hp/images/menu/closeGif.gif";
		closeGifElement.onclick = function(){setHide(true); hideScreenie()};
		closeGifElement.className = "closeGifStyle";

		if(prevShot){
		backGifElement = document.createElement("img");
		backGifElement.src = "/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fscreenie.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fimages%2Fmenu%2FbackGif.gif&reason=invalid-overlay-or-uncollected-site-resource";
		backGifElement.onclick = function(){prevScreenshot()};
		backGifElement.className = "backGifStyle"; 
		}
		
		if(nextShot){
		fwdGifElement = document.createElement("img");
		fwdGifElement.src = "/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fscreenie.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fimages%2Fmenu%2FfwdGif.gif&reason=invalid-overlay-or-uncollected-site-resource";
		fwdGifElement.onclick = function(){nextScreenshot()};
		fwdGifElement.className = "fwdGifStyle";
		}
		
		screenie2Element = document.createElement("div");
		screenie2Element.id = "Screenie2";
		screenie2Element.className = "screenie2Style";
		screenie2Element.style.cursor = "pointer"; 
		if(nextShot){ screenie2Element.onclick = function(){nextScreenshot()}; }
		else { screenie2Element.onclick = function(){ closeGifElement.onclick()}; screenie2Element.title = "Close" }

		screenieElement = document.createElement("div");
		screenieElement.id = "Screenie";
		screenieElement.className = "screenieStyle";
		screenieElement.onmouseover = function(){setHide(false)};
		screenieElement.onmouseout = function(){setHide(true);};		
		screenieElement.appendChild(closeGifElement);
		if(prevShot){
		screenieElement.appendChild(fwdGifElement);
		screenieElement.appendChild(backGifElement); 
		}
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
		window.onscroll = window.onresize = adjustBackgroundStuff

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

var currwidth;
var mod = (is_ie)?8:0
function resizeScreenshot()
{	 	 
 if (ticked >= 310 || screenImage.width - currwidth <= 2 )
  {  document.getElementById("Screenie").style.width = screenImage.width + "px"
  	 
	 ticked = 0;
	 animationLock = false;
    window.clearInterval(startTheAnimation);							//stop the animation
	}
	else
	{  
		//document.getElementById("Screenie").style.width = (screenImage.width*ticked/300) + "px";
		//ticked += 10;
		currwidth = document.getElementById("Screenie").style.width.slice(0,-2)
		currwidth -= (currwidth - screenImage.width - mod)/3
		
		document.getElementById("Screenie").style.width = currwidth + "px"
	}
	 //document.getElementById("output").innerHTML = "nimagewidth: " + screenImage.width  + " |  currwidth: " + currwidth;
}

function adjustBackgroundStuff()
{
	windowHeight = (window.innerHeight) ? window.innerHeight : document.body.clientHeight;
	windowWidth = (window.innerWidth) ? window.innerWidth : document.body.clientHeight;
	//document.getElementById("pictureFrame").style.top = "75px";
	document.getElementById("c0ver").style.width = document.body.scrollWidth + "px";
	document.getElementById("c0ver").style.height = document.body.scrollHeight + "px";
	scrolltop = (document.body.scrollTop)?document.body.scrollTop:document.documentElement.scrollTop
	document.getElementById("pictureFrame").style.top = scrolltop + 30 + "px";
	
}

function setHide(thisValue) { hideMe = thisValue; }

function hideScreenie()
{
	if (hideMe)
	{   currwidth = 1; animationLock = false; window.clearInterval(startTheAnimation);
		document.getElementById("Screenie").style.width = "1px";
		//document.getElementById("Screenie").style.height = "1px";
		document.getElementById("dumpster").appendChild(document.getElementById("redBlock"));
	}
}

function nextScreenshot()
{ 
	if(!animationLock) slideShowResizer();
}

function prevScreenshot()
{ 
	if(!animationLock) slideShowResizerPrev();
}

function resizeNewScreenshot()
{
	if (sliderTicked >= 160)
  {
    window.clearInterval(startTheResizer);							//stop the animation
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
    window.clearInterval(startTheResizerPrev);							//stop the animation
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

function printPages()
{
	numPages = Math.ceil(shotList.length/shotsPerPage);//)'><img src='images/photos/test.jpg'></a></div>
	outString = "";
	for(i = 0; i < shotsPerPage; i++)
	{
		n = shotsPerPage*currentPage+i;
		if(shotList[n])
		{
			thumbnail = shotList[n].replace(".jpg","-thumb.jpg");
			outString += "<div><a href='javascript:omegaLightBox("+n+")'><img src='"+thumbnail+"'></a></div>";
		}
	}
	document.getElementById("galleryPictures").innerHTML = outString;
	document.getElementById("pageNum").innerHTML = currentPage+1;
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

/*onLoad*/
function addEvent(obj, evType, fn){  
 if (obj.addEventListener){ obj.addEventListener(evType, fn, false); return true; }
 else if (obj.attachEvent){ var r = obj.attachEvent("on"+evType, fn); return r; } else { return false; } }

addEvent(window, 'load',omegaScan);

function omegaScan(){
  anc = document.getElementsByTagName("a") 
  for(i=0; i<anc.length; i++)
  { if(anc[i].rel=="screenie"){ anc[i].onclick = addomega;  }
  }
}

function addomega()
{ omegaLightBox(this.href,1); return false; }

