ticked = 0;													//global variable, used to keep track of time
okayToGo = true;											//global variable; if false, locks the animation function call down as long as an animation is in progress
forwardBackward = 1;										//global variable, determines whether animation cycles normally (1) or in reverse (-1)
currentCreature = 0;
theNewContainer = 1;
theOldContainer = 2;
creaturePic = "/wrath/images/bestiary/creature0.jpg";
numCreatures = false;
animationFunction = "rightOrLeft()";

function toggleContainers()
{
  theNewContainer = (theNewContainer == "1") ? "2" : "1";
  theOldContainer = (theOldContainer == "1") ? "2" : "1";
}

function containerSwitch()
{
  toggleContainers();
	document.getElementById("bestiaryThumb"+theNewContainer).style.backgroundImage = "url(/wrath/images/bestiary/thumb-creature"+newCreature+".jpg)";
  document.getElementById("loreContainer_"+theNewContainer).innerHTML = document.getElementById("creature"+newCreature).innerHTML;
	if(document.getElementById("creature"+newCreature+"hasShots"))
	{
		var shotNumber = eval(document.getElementById("creature"+newCreature+"hasShots").className);
		for(i=0; i<shotNumber; i++)
		{
			document.getElementById("screenshotThumb"+theNewContainer+"_"+i).style.backgroundImage = "url(/wrath/images/bestiary/creature"+newCreature+"thumb"+i+".gif)";
			document.getElementById("screenshotThumb"+theNewContainer+"_"+i).className = "/wrath/images/bestiary/creature"+newCreature+"shot"+i+".jpg";
			document.getElementById("screenshotThumb"+theNewContainer+"_"+i).onclick = function() { fiatLux(this.className); }
			document.getElementById("screenshotThumb"+theNewContainer+"_"+i).style.display = "block";
		}
	}
}

function countCreatures()
{
	numCreatures = 0;
	creatureListRoot = document.getElementById("creaturesList");
	for(i=0; i<creatureListRoot.childNodes.length; i++)
	{
		if(creatureListRoot.childNodes[i].nodeName == "LI")
		{
			for(j=0; j<creatureListRoot.childNodes[i].childNodes.length; j++)
			{
				if(creatureListRoot.childNodes[i].childNodes[j].nodeName == "A") numCreatures++;
			}
		}
	}
}

function itemSlideShow(prevOrNext)								//called if the user clicks "Previous" or "Next"; has 1 (next) or -1 (previous) as a parameter
{
  if (okayToGo)													//if the function is not locked
  {
		if(!numCreatures) countCreatures();
		newCreature = currentCreature + prevOrNext;							//used later to determine the next Div ID in the monsterNames array
    if (newCreature >= numCreatures) newCreature = 0;			//overflow catch; if the new identifier is larger than the number of elements in the array 
    else if (newCreature < 0) newCreature = numCreatures-1;		//or less than zero, jump to zero (the former) or to the last element in the array (the latter)
		forwardBackward = prevOrNext;								//grabs the function parameter, sets the scroll direction accordingly
    if(prevOrNext!= 1) animationFunction = "backwardScroll()"
		moveItem(newCreature);											//calls the Animation Control Function, passing the new item identifier as a parameter
  }
}

function moveItem(thisCreature)										//Animation Control Function
{
  if(okayToGo && thisCreature != currentCreature)						//if the function is not locked and the user clicked on a new item (not the current one)
  {
		newCreature = thisCreature;											//grabs the parameter, stores it for later use
		creaturePic = "/wrath/images/bestiary/creature"+newCreature+".jpg";
		containerSwitch();
		newBestiaryContainer = document.getElementById("mainContainer_"+theNewContainer);
		newBestiaryContainer.style.zIndex = 50+10*forwardBackward;		//tricky; if forward, new item slides in behind the current item
		oldBestiaryContainer = document.getElementById("mainContainer_"+theOldContainer);
		oldBestiaryContainer.style.zIndex = 50+20*forwardBackward;	    //if backward, new item slides in in front of the current item
		startTheMove = window.setInterval(animationFunction,20);		//calls the Animation Execution Function
  }
}

function rightOrLeft()											//Animation Execution Function
{
  if (ticked > 1000)											//after one second has passed, i.e. one cycle is finished
  {
		window.clearInterval(startTheMove);							//stop the animation
		ticked = 0;													//reset the timer
		forwardBackward = 1;										//reset the scroll direction
		currentCreature = newCreature;								//make the new item the current item
		for(i=0; i<3; i++)
		{
			document.getElementById("screenshotThumb"+theOldContainer+"_"+i).style.display = "none";
		}
		okayToGo = true;											//unlock the Animation Control Function
  }
  else
  {
		okayToGo = false;
		thisAngle = (Math.PI/2)*(ticked/990);	
		newBestiaryContainer.style.left = (877-Math.sin(thisAngle)*577)+"px"; 
		newBestiaryContainer.style.top = (10-(forwardBackward*Math.cos(thisAngle)*10))+"px"; 
		oldBestiaryContainer.style.left = (877-Math.sin(thisAngle+Math.PI/2)*577)+"px"; 
		oldBestiaryContainer.style.top = (10-(forwardBackward*Math.cos(thisAngle+Math.PI/2)*120))+"px"; 
		ticked += 30;
  }
}

function backwardScroll()
{
	if (ticked > 1000)											//after one second has passed, i.e. one cycle is finished
  {
		window.clearInterval(startTheMove);							//stop the animation
		ticked = 0;													//reset the timer
		animationFunction = "rightOrLeft()";										//reset the scroll direction
		forwardBackward = 1;
		currentCreature = newCreature;								//make the new item the current item
		for(i=0; i<3; i++)
		{
			document.getElementById("screenshotThumb"+theOldContainer+"_"+i).style.display = "none";
		}
		okayToGo = true;											//unlock the Animation Control Function
  }
  else
  {
		okayToGo = false;
		thisAngle = (Math.PI/2)*(ticked/990);	
		newBestiaryContainer.style.left = (877-Math.sin(thisAngle)*577)+"px"; 
		newBestiaryContainer.style.top = (10+Math.cos(thisAngle)*120)+"px"; 
		oldBestiaryContainer.style.left = (877-Math.sin(thisAngle+Math.PI/2)*577)+"px"; 
		oldBestiaryContainer.style.top = (10+Math.cos(thisAngle+Math.PI/2)*10)+"px"; 
		ticked += 30;
  }
}