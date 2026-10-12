var ticked = 0;													//global variable, used to keep track of time
var okayToGo = true;											//global variable; if false, locks the animation function call down as long as an animation is in progress
var forwardBackward = 1;										//global variable, determines whether animation cycles normally (1) or in reverse (-1)
var currentCreature = 8;
var theNewContainer = 1;
var theOldContainer = 2;

function toggleContainers()
{
  theNewContainer = (theNewContainer == 1) ? 2 : 1;
  theOldContainer = (theOldContainer == 1) ? 2 : 1;
}

function containerSwitch(theNewCreature)
{
  toggleContainers();
  if(isIE_PNG) headerPNG = '<img src="/shared/wow-com/images/layout/pixel.gif" style="filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src=images/bestiary/title-'+theNewCreature.creatureName+'.png);">';
  else headerPNG = "<img src=images/bestiary/title-"+theNewCreature.creatureName+".png>";
  document.getElementById("headerContainer_"+theNewContainer).innerHTML = headerPNG;
  document.getElementById("thumbContainer_"+theNewContainer).style.height = theNewCreature.thumbHeight+"px";
  document.getElementById("thumbContained_"+theNewContainer).innerHTML = "<a href=javascript:bestiaryPopUp('"+theNewCreature.creatureName+"',"+theNewCreature.imgWidth+")><img src='images/bestiary/thumb-"+theNewCreature.creatureName+".jpg' border='0'></a>";
  document.getElementById("loreContainer_"+theNewContainer).innerHTML = theNewCreature.lore;
}

function bestiaryPopUp(namedCreature,imageWidth) 
{
	//Browser detection - is the user relying on the one browser where this script does not work?
	var is_safari = ((navigator.appName.indexOf('safari')!=-1)&&(navigator.appName.indexOf('mac')!=-1))?true:false;
	var screenshot = "images/bestiary/"+namedCreature+".jpg"; //gimp variable for Safari =P

	var name = "Sheenscrot";
	var imgDimensions = (imageWidth == 800) ? [800,600] : [600,800];
	widthHeight = "width=" + imgDimensions[0] + ",height=" + imgDimensions[1];
	winFeatures = "width=" + imgDimensions[0] + ",height=" + imgDimensions[1] + ",left=50,top=50,menubar=no,resizable=no,scrollbars=no,statusbar=no,toolbar=no,locationbar=no"
	if (is_safari) spawn = window.open(screenshot,name,winFeatures);
	else
	{
		spawn = window.open("/shared/wow-com/images/layout/pixel.gif",name,winFeatures)
		spawn.document.write("<html><head><title><\/title><\/head><body onBlur='self.close()' style='background-image:url(images/bestiary/"+namedCreature+".jpg); background-repeat:no-repeat;'><\/body><\/html>"); 
		spawn.document.close();
	}
}

//Martin's quick and dirty (also slick and purdy) PNG fix for IE
var isIE_PNG = (navigator.appName == "Microsoft Internet Explorer" && navigator.userAgent.indexOf('Opera') == -1);
function pngImage(imgSource)
{
  if(isIE_PNG) document.write('<img src="/shared/wow-com/images/layout/pixel.gif" style="filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='+imgSource+');">');
  else document.write("<img src="+imgSource+">");
}

function itemSlideShow(prevOrNext)								//called if the user clicks "Previous" or "Next"; has 1 (next) or -1 (previous) as a parameter
{
  if (okayToGo)													//if the function is not locked
  {
    newCreature = currentCreature + prevOrNext;							//used later to determine the next Div ID in the monsterNames array
    if (newCreature >= aBestiary.length) newCreature = 0;			//overflow catch; if the new identifier is larger than the number of elements in the array 
    else if (newCreature < 0) newCreature = aBestiary.length -1;		//or less than zero, jump to zero (the former) or to the last element in the array (the latter)
    forwardBackward = prevOrNext;								//grabs the function parameter, sets the scroll direction accordingly
    moveItem(newCreature);											//calls the Animation Control Function, passing the new item identifier as a parameter
  }
}

function moveItem(thisCreature)										//Animation Control Function
{
  if(okayToGo && thisCreature != currentCreature)						//if the function is not locked and the user clicked on a new item (not the current one)
  {
    containerSwitch(aBestiary[thisCreature]);
	newCreature = thisCreature;											//grabs the parameter, stores it for later use
	document.getElementById("mainContainer_"+theNewContainer).style.zIndex = 50+10*forwardBackward;		//tricky; if forward, new item slides in behind the current item
	document.getElementById("mainContainer_"+theOldContainer).style.zIndex = 50+20*forwardBackward;	    //if backward, new item slides in in front of the current item
	startTheMove = window.setInterval("rightOrLeft()",20);		//calls the Animation Execution Function
  }
}

function rightOrLeft()											//Animation Execution Function
{
  if (ticked == 1020)											//after one second has passed, i.e. one cycle is finished
  {
    window.clearInterval(startTheMove);							//stop the animation
	ticked = 0;													//reset the timer
	forwardBackward = 1;										//reset the scroll direction
	currentCreature = newCreature;								//make the new item the current item
    okayToGo = true;											//unlock the Animation Control Function
  }
  else
  {
    okayToGo = false;											//lock the Animation Control Function
	thisAngle = (Math.PI/2)*(ticked/1000);						//percentual angle, measured in radians; goes from 0 to 1.5708 (or 90 degrees)
	document.getElementById("mainContainer_"+theNewContainer).style.left = " "+(735-Math.sin(thisAngle)*700)+"px"; //sets the X coordinate, following a sine curve
	document.getElementById("mainContainer_"+theNewContainer).style.top = " "+(105-(forwardBackward*Math.cos(thisAngle)*55))+"px"; //sets the Y coordinate, following a cosine curve
	document.getElementById("mainContainer_"+theOldContainer).style.left = " "+(735-Math.sin(thisAngle+Math.PI/2)*700)+"px"; //la la la, math is fun
	document.getElementById("mainContainer_"+theOldContainer).style.top = " "+(105-(forwardBackward*Math.cos(thisAngle+Math.PI/2)*55))+"px"; //oooh, look, numbers! =)
	ticked += 20;												//increase the timekeeper
  }
}