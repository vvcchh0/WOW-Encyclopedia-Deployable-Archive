/* Omega Skip's Tooltip - SAFETY NOT GUARANTEED! */
/* Memo to self: Clean up this code, for it is wretched */
/* ############# GLOBAL VARIABLES, DEFAULT VALUES ############# */

is_safari = ((navigator.userAgent.indexOf("Safari")!=-1))?true:false;
isShowing = false;
topBottom = 1;
lockTtip = false;
isMousedOver = false;
mouseX = 0;
mouseY = 0;

/*##### INCLUDE THIS STYLE IN ANY DOCUMENT USING TOOLTIPS: #####

	.toolBoxStyle
	{
		position:absolute; 
		top:20px; 
		color:#FFFFFF; 
		background:url(/blizzcon07/images/trans.png);
		_background:url(/blizzcon07/images/pixel.gif);
		_filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='images/trans.png', sizingMethod='scale');
		border:1px solid #DDDDDD; 
		font-family:Arial, Helvetica, sans-serif; 
		padding:2px;
		font-size:12px; 
		border-bottom-color:#666666; 
		border-right-color:#666666; 
		display:none;
		z-index:999999;
	}
	
	.toolBoxStyle div { position:relative; }
	.toolBoxStyle .myRight { position:absolute; right:6px;  }
	.toolBoxStyle .myGreen { display:inline; color:#00FF00; }
	.toolBoxStyle .myRed { display:inline; color:#FF0000; }
	
	.toolBoxStyle b { color:#CC9933; font-size:14px; display:block; }
	.toolBoxStyle .questStyle { color:#CC9933; }
	
	.toolBoxStyle .mySmall { color:#FF0000; font-size:11px; }

##### END STYLE #####*/

/* ############# FUNCTIONS ############# */

function ttipLock()
{
	lockTtip = true;
}

function ttipUnLock()
{
	lockTtip = false;
//	if(hideItem) hideItem();
}

function showTip(toolTipContent)
{
	if(!document.getElementById("toolBox"))
	{
		ttipEmbryo = document.createElement("div");
		ttipEmbryo.id = "toolBox";
		ttipEmbryo.className = "toolBoxStyle";
		ttipEmbryo.onmouseover = function() { ttipLock(); };
		ttipEmbryo.onmouseout = function() { ttipUnLock(); };
		document.getElementsByTagName("body")[0].appendChild(ttipEmbryo);
	}
	if(toolTipContent != null)
	{
		isShowing = true;
		isMousedOver = true;
		document.getElementById("toolBox").style.left = mouseX+10+"px";
		document.getElementById("toolBox").style.top = (!is_safari) ? mouseY+10+document.body.scrollTop+"px" : mouseY+10+"px";
		document.getElementById("toolBox").style.display = "block";
		ttipWindowHeight = document.body.clientHeight;
		ttipWindowWidth = document.body.clientWidth;
		document.getElementById("toolBox").innerHTML = toolTipContent;
	}
}

function hideTip()
{
	isMousedOver = false;
	window.setTimeout("itemBeGone()",62);
}

function itemBeGone()
{
	if(!lockTtip && !isMousedOver)
	{
		document.getElementById("toolBox").style.display = "none";
	  isShowing = false;
	}
}

function tipPosition(callingEvent)
{
  if (!callingEvent) callingEvent = window.event;
	mouseX = callingEvent.clientX;
	mouseY = callingEvent.clientY-1;
  if (isShowing)
  {
		var ttipWindowScrollDistance = (!is_safari) ? document.body.scrollTop : 0;
		if(document.getElementById("toolBox").offsetWidth+mouseX+10 > ttipWindowWidth)
		{
			document.getElementById("toolBox").style.left = ttipWindowWidth - document.getElementById("toolBox").offsetWidth + "px";
		}
		else
		{
			document.getElementById("toolBox").style.left = mouseX+10+"px";
		}
		var ttipOvershoot = (!is_safari) ? (document.getElementById("toolBox").offsetHeight*topBottom) + mouseY + (10*topBottom) : document.getElementById("toolBox").offsetHeight + mouseY + 10 - window.pageYOffset;
		if(ttipOvershoot > ttipWindowHeight)
		{
			document.getElementById("toolBox").style.top = ttipWindowHeight - document.getElementById("toolBox").offsetHeight + ttipWindowScrollDistance + "px";
		}
		else
		{
			document.getElementById("toolBox").style.top = mouseY+10+ttipWindowScrollDistance- (document.getElementById("toolBox").offsetHeight*((1-topBottom)/2)) +"px";
		}
  }
}

document.onmousemove = tipPosition;