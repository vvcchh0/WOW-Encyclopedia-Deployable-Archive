//Global Variables and Constants
is_safari = ((navigator.userAgent.indexOf("Safari")!=-1))?true:false;
isShowing = false;
mouseX = 0;
mouseY = 0;
ttipElement = false;

//Functions
function showTip(toolTipContent)
{
	isShowing = true;
	if(!ttipElement)
	{
		ttipContainer = document.createElement("div");
		ttipContainer.id = "toolTipContainer";
		ttipContainer.className = "toolTipContainerStyle";
		document.getElementsByTagName("body")[0].appendChild(ttipContainer);
/*		
		ttipElement = document.createElement("div");
		ttipElement.id = "toolTipBox";
		ttipElement.className = "toolBoxStyle";
		ttipContainer.appendChild(ttipElement);
*/
		ttipTable = document.createElement("table");
		ttipTable.cellSpacing = "0";
		ttipTable.cellPadding = "0";
		ttipBody = document.createElement("tbody");
		ttipRow1 = document.createElement("tr");
		ttipRow2 = document.createElement("tr");
		ttipRow3 = document.createElement("tr");
		
		ttip11 = document.createElement("td");
		ttip11.className = "c11";
		ttip12 = document.createElement("td");
		ttip12.className = "c12";
		ttip13 = document.createElement("td");
		ttip13.className = "c13";
		ttip21 = document.createElement("td");
		ttip21.className = "c21";
		ttipElement = document.createElement("td");
		ttipElement.id = "toolTipBox";
		ttipElement.className = "newToolBoxStyle";
		ttip23 = document.createElement("td");
		ttip23.className = "c23";
		ttip31 = document.createElement("td");
		ttip31.className = "c31";
		ttip32 = document.createElement("td");
		ttip32.className = "c32";
		ttip33 = document.createElement("td");
		ttip33.className = "c33";

		ttipTable.appendChild(ttipBody);
		ttipBody.appendChild(ttipRow1); ttipBody.appendChild(ttipRow2); ttipBody.appendChild(ttipRow3);
		ttipRow1.appendChild(ttip11); ttipRow1.appendChild(ttip12); ttipRow1.appendChild(ttip13);
		ttipRow2.appendChild(ttip21); ttipRow2.appendChild(ttipElement); ttipRow2.appendChild(ttip23);
		ttipRow3.appendChild(ttip31); ttipRow3.appendChild(ttip32); ttipRow3.appendChild(ttip33);
		ttipContainer.appendChild(ttipTable);
	}
	ttipContainer.style.left = mouseX+10+"px";
  ttipContainer.style.top = mouseY+10+document.body.scrollTop+"px";
  ttipContainer.style.display = "block";
	ttipWindowHeight = (window.innerHeight) ? window.innerHeight : document.body.clientHeight;
  ttipElement.innerHTML = toolTipContent;
	ttipWindowScrollDistance = ((document.documentElement.scrollTop) ? document.documentElement.scrollTop : document.body.scrollTop );
	adjustVerticalPosition();
}

function adjustVerticalPosition()
{
	var ttipOvershoot = (!is_safari) ? ttipElement.offsetHeight + mouseY + 10 : ttipElement.offsetHeight + mouseY + 10 - window.pageYOffset;
	if(ttipOvershoot > ttipWindowHeight)
	{
		ttipContainer.style.top = ttipWindowHeight - ttipElement.offsetHeight + ttipWindowScrollDistance + "px";
	}
	else
	{
		ttipContainer.style.top = (!is_safari) ? mouseY+10+ttipWindowScrollDistance+"px" : mouseY+10+"px";
	}
}

function hideTip()
{
	if (isShowing)
	{
		ttipContainer.style.display = "none";
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
		ttipContainer.style.left = mouseX+10+"px";
		adjustVerticalPosition();
  }
}

function ddrivetip(thisItem) { showTip(thisItem); }
function hideddrivetip() { hideTip(); }

document.onmousemove = tipPosition;