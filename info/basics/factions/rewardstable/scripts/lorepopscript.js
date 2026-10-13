/* ------- Sproing Stuff ------- */

tictoc = 0;
sproingLock = false;

function sproing()
{
	hideNewMenu(9);
	if (!sproingLock)
	{
		document.getElementById("baseDiv").style.width = "715px";
		sproingLock = true;
		document.getElementById("loreRootDiv").style.filter = "alpha(opacity=0)";
		document.getElementById("targetDiv").appendChild(document.getElementById("baseDiv"));
//		document.getElementsByTagName("body")[0].appendChild(document.getElementById("baseDiv"));
		document.getElementById("lorePopFrame").style.top = (document.body.scrollTop > 0) ? document.body.scrollTop - 25 + "px" : document.documentElement.scrollTop - 25 + "px";
		if(navigator.userAgent.indexOf("Opera") == -1)
		{
			flubber = window.setInterval("badabinger()",20);
		}
		else
		{
			document.getElementById("loreRootDiv").style.width = "604px";
			document.getElementById("loreShadowContainer").style.width = "604px";
			document.getElementById("loreRootDiv").style.height = "670px";
			document.getElementById("loreShadow").style.height = "670px";
			document.getElementById("loreRootDiv").style.opacity = 1;
			document.getElementById("loreText").style.display = "block";
			if (document.getElementById("loreText").offsetHeight > 560 )
			{
				document.getElementById("dragButton").style.visibility = "visible";
				document.getElementById("dragRail").style.visibility = "visible";
			}
			document.getElementById("loreText").style.opacity = 1;
			sproingLock = false;
//			stretcher =  window.setInterval("kapowzer()",20);
//			alert("Please get a REAL browser.");
		}
	}
}

function badabinger()
{
	if (tictoc == 210)
	{
		window.clearInterval(flubber);
		document.getElementById("loreRootDiv").style.filter = "";
		tictoc = 0;
		stretcher =  window.setInterval("kapowzer()",20);
	}
	else
	{
		document.getElementById("loreRootDiv").style.opacity = (tictoc/200);
		document.getElementById("loreRootDiv").style.filter = "alpha(opacity="+100*tictoc/200+")";
		tictoc += 10;
	}
}

function kapowzer()
{
	if (tictoc == 160)
	{
		window.clearInterval(stretcher);
		tictoc = 0;
		expander = window.setInterval("sproinger()",20);
	}
	else
	{
		document.getElementById("loreRootDiv").style.width = 200 + 404 * (tictoc/150) + "px";
		document.getElementById("loreShadowContainer").style.width = 200 + 404 * (tictoc/150) + "px";
		tictoc += 10;
	}
}

function sproinger()
{
	if (tictoc == 310)
	{
		window.clearInterval(expander);
		tictoc = 0;
		document.getElementById("loreText").style.filter = "alpha(opacity=0)";
		document.getElementById("loreText").style.display = "block";
		fader = window.setInterval("kablooier()",20);
	}
	else
	{
		document.getElementById("loreRootDiv").style.height = 100 + 570 * (tictoc/300) + "px";
		document.getElementById("loreShadow").style.height = 100 + 570 * (tictoc/300) + "px";
		tictoc += 10;
	}
}

function kablooier()
{
	if (tictoc == 110)
	{
		window.clearInterval(fader);
		document.getElementById("loreText").style.filter = "";
		if (document.getElementById("loreText").offsetHeight > 560 )
		{
			document.getElementById("dragButton").style.visibility = "visible";
			document.getElementById("dragRail").style.visibility = "visible";
		}
		tictoc = 0;
		sproingLock = false;
	}
	else
	{
		document.getElementById("loreText").style.opacity = (tictoc/100);
		document.getElementById("loreText").style.filter = "alpha(opacity="+100*tictoc/100+")";
		tictoc += 10;
	}
}

function hideStuff()
{
	if (hideMe && !sproingLock)
	{
		document.getElementById("phantomZone").appendChild(document.getElementById("baseDiv"));
//		document.getElementById("baseDiv").style.display = "none";
		document.getElementById("dragButton").style.visibility = "hidden";
		document.getElementById("dragRail").style.visibility = "hidden";
		document.getElementById("loreText").style.opacity = 0;
		document.getElementById("loreText").style.display = "none";
		document.getElementById("loreRootDiv").style.width = "200px";
		document.getElementById("loreRootDiv").style.height = "100px";
		document.getElementById("loreRootDiv").style.opacity = 0;
		document.getElementById("loreShadowContainer").style.width = "200px";
		document.getElementById("loreShadow").style.height = "100px";
		document.getElementById("dragButton").style.top = "200px";
		dragObjects["dragButton"].yOffset = 200;
		document.getElementById("loreText").style.top = "0px";
		showNewMenu(9);
	}
}

/* ------- Sproing Stuff ------- */
function debugMessage(thisMessage) { document.getElementById("debugAlert").innerHTML = thisMessage; }

mouseAtY = 0;

isDragging = false;
dragTarget = "dragButton";
targetOffsetY = 0;
dragObjects = new Object();
hideMe = true;

function DragObject(yOffset, targetID)
{
  this.yOffset = yOffset;
  this.targetID = targetID;
}

dragButtonZ = new DragObject(200, "dragButton");
dragObjects["dragButton"] = dragButtonZ;

function dragStart(thisObject)
{
  isDragging = true;
  dragTarget = thisObject.targetID;
  thisObject.yOffset -= mouseAtY;
}

function cockBlock() { return false; }

function dragStop()
{
  if(isDragging)
  {
    isDragging = false;
    dragObjects["dragButton"].yOffset += mouseAtY;
		dragTarget = "";
  }
}

function dragTheThing(callingEvent)
{
//	tipPosition(callingEvent);
	if (!callingEvent) callingEvent = window.event;
  mouseAtY = callingEvent.clientY;
//	debugMessage(document.getElementById("dragButton").offsetTop);
  if (isDragging)
  {
		document.getElementById("dragButton").style.top = mouseAtY+dragObjects["dragButton"].yOffset+"px";
		document.getElementById("loreText").style.top = ((mouseAtY+dragObjects["dragButton"].yOffset-200)/200) * -1 * (document.getElementById("loreText").offsetHeight - 561) + "px";
//	debugMessage(document.getElementById("loreText").offsetHeight);
		if (document.getElementById("dragButton").offsetTop <= 199)
		{
			document.getElementById("dragButton").style.top = "200px";
	    isDragging = false;
			dragObjects["dragButton"].yOffset = 200;
		}
		else if (document.getElementById("dragButton").offsetTop >= 401)
		{
			document.getElementById("dragButton").style.top = "400px";
	    isDragging = false;
			dragObjects["dragButton"].yOffset = 400;
		}
  }
	else { tipPosition(callingEvent); }
}

mouseCount = 0;

function scrollResolver(direction)
{
	if (document.getElementById("loreText").offsetHeight > 560 )
	{
		if (direction > 0) //Up
		{
			if(dragObjects["dragButton"].yOffset-20*direction <= 200)
			{
				document.getElementById("dragButton").style.top = "200px";
				document.getElementById("loreText").style.top = "0px";
				dragObjects["dragButton"].yOffset = 200;
			}
			else
			{
				document.getElementById("dragButton").style.top = dragObjects["dragButton"].yOffset-20*direction+"px";
				document.getElementById("loreText").style.top = ((-20*direction+dragObjects["dragButton"].yOffset-200)/200) * -1 * (document.getElementById("loreText").offsetHeight - 561) + "px";
				dragObjects["dragButton"].yOffset += -20*direction;
			}
		}
		else if (direction < 0) //Down
		{
			if(dragObjects["dragButton"].yOffset-20*direction >= 400)
			{
				document.getElementById("dragButton").style.top = "400px";
				document.getElementById("loreText").style.top = -1 * (document.getElementById("loreText").offsetHeight - 561) + "px";
				dragObjects["dragButton"].yOffset = 400;
			}
			else
			{
				document.getElementById("dragButton").style.top = dragObjects["dragButton"].yOffset-20*direction+"px";
				document.getElementById("loreText").style.top = ((-20*direction+dragObjects["dragButton"].yOffset-200)/200) * -1 * (document.getElementById("loreText").offsetHeight - 561) + "px";
				dragObjects["dragButton"].yOffset += -20*direction;
			}
		}
	}
}

function flarb(scrollEvent)
{
	if(hideMe == false)
	{
		var direction = 0;
		if (!scrollEvent) scrollEvent = window.event;
		if (scrollEvent.wheelDelta)
		{
			direction = scrollEvent.wheelDelta/120;
			if (window.opera) direction = -direction;
		}
		else if (scrollEvent.detail) { direction = -scrollEvent.detail/3; }
		scrollResolver(direction);
		if (scrollEvent.preventDefault) scrollEvent.preventDefault();	//FF
		return false;																									//IE
	}
}

document.onmousemove = dragTheThing;
document.onmouseup = dragStop;
document.onselectstart = cockBlock;
document.onmousedown = cockBlock;
document.onmousewheel = flarb;
if (document.addEventListener) { document.addEventListener('DOMMouseScroll', flarb, false); }