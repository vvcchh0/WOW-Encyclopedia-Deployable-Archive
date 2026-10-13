/*
Dynamic Faction Reward Table, Version 1.Monkey

This javascript creates a faction rewards table almost from scratch, using only
a rather simple and easy to maintain array made up of items of a custom datatype
(RewardItem) which contains all the necessary information for the table and the
tooltip.

The main loop takes each element from the RewardItems array and appends them as
new child nodes to the appropriate section of the rewards table. The benefit is
that the order of the items in the array does not matter; they are automatically
placed in the correct faction/reputation bracket. This makes adding and removing
items to the table very easy, and the only thing that needs to be edited for
localization is the single RewardItems array. The creation of the actual table
is done by the script.
*/

//------MAIN LOOP:
//	- Select the proper level range data for each item
//	- Take each item from the rewards array and add it to the rewards table.

var levelBracket = 0;
DOMpickiness = (!is_safari) ? 0 : 1;

function hideRepLevels(theseLevels)
{
	for(l=0; l<theseLevels.length; l++)
	{
		document.getElementById("slot"+theseLevels[l]).style.display = "none";
	}
}

function neutralFactions()
{
	document.getElementById("allianceButton").style.backgroundImage = "url(images/button-alliance.jpg)";
	document.getElementById("hordeButton").style.backgroundImage = "url(images/button-horde.jpg)";
}

var reputationsList = new Array();
reputationsList[0]  = "friendly";
reputationsList[1]  = "honored";
reputationsList[2]  = "revered";
reputationsList[3]  = "exalted";
var factionsList = new Array();
factionsList[0] = "alliance";
factionsList[1] = "horde";
  
function loadTable()
{
	numItems = new Object();					//Firefox compatibility FOR TEH SUCK
	numItems["horde"] = 0;
	numItems["horde"]["friendly"] = 0;
	numItems["horde"]["honored"] = 0;
	numItems["horde"]["revered"] = 0;
	numItems["horde"]["exalted"] = 0;
	numItems["alliance"] = 0;
	numItems["alliance"]["friendly"] = 0;
	numItems["alliance"]["honored"] = 0;
	numItems["alliance"]["revered"] = 0;
	numItems["alliance"]["exalted"] = 0;
	for (i=0; i<RewardItems.length; i++)
	{
		selectBracket(RewardItems[i],levelBracket);
		if (RewardItems[i].itemHTML != "none") addRewardItem(RewardItems[i],i);
	}
}

function reloadTable()
{
  for (j=0; j<2; j++)
  {
    for (k=0; k<4; k++)
		{
			deletionTarget = factionsList[j]+"_rewards";
			rowsLength = document.getElementById(deletionTarget).childNodes.length;
			for (l=0; l<rowsLength; l++)
			{
				document.getElementById(deletionTarget).removeChild(document.getElementById(deletionTarget).lastChild);
			}
		}
  }
  loadTable();
}

pearlCounter = 0;
hatchButtonTime = new Date();
dharmaMonths = new Array("January","February","March","April","May","June","July","August","September","October","November","December");
function dharma_pearl()
{
	switch(Math.floor(Math.random()*6))
	{
		case 0: alertOutput = "Your lucky numbers are: 4-8-15-16-23-42"; break;
		case 1: alertOutput = "Look behind you, a two-headed monkey!"; break;
		case 2: alertOutput = "Your sound card, err, I mean your mouse works perfectly!"; break;
		case 3: alertOutput = "What, did you expect some sort of easter egg?"; break;
		case 4: alertOutput = "Stop poking the merchandise!"; break;
		case 5: alertOutput = "Please write down three things you like about Sundays, then press \"Ok\" to continue."; break;
	}
	alert(alertOutput);
}
//------END MAIN LOOP------
//------ADDING AN ITEM------
//This funtion is a bit tricky, so I'll comment each step

function addRewardItem(rewardItem,i)																//expects a RewardItem as an argument
{
  insertionTarget = rewardItem.playerFaction+"_rewards";					//determines in what bracket the item goes, for example alliance_friendly
	currentRow = document.getElementById(insertionTarget).childNodes.length - 1;	//determines at what row in the bracket the item should be placed, so it's row 0, 1, 2, 3...
  rewardItemCell = createItemCell(rewardItem,i);													//creates the HTML code for the item
  
  if (numItems[rewardItem.playerFaction]%2 == 0)
  {																								//If there is still room in this row, we add the item here (there is room for two items per row)
    var newRow = document.createElement("tr");													//Create a new row
		document.getElementById(insertionTarget).appendChild(newRow);					//Append the new row to the bracket
    newRow.appendChild(rewardItemCell);															//Append the item as a child node to the new row
  }																								//Append the item as a child node to the current row
  else																							//If the current row is full (has already two items in it)
  {
    document.getElementById(insertionTarget).childNodes[currentRow].appendChild(rewardItemCell);
  }
  
  numItems[rewardItem.playerFaction]++;
}


//This function creates the new cell to be added to the rewards table
function createItemCell(rewardItem)																//expects a RewardItem as an argument
{									//first, we need a new table cell to add to the rewards table, and we need to format the cell
  //alert(rewardItem)
  itemCell = document.createElement("td");														//create a new table cell
  cellStyle = document.createAttribute("class");												//create a new "class" attribute
  cellStyle.nodeValue="style_cell";																//set the new attribute's value to "style_cell"
  itemCell.setAttributeNode(cellStyle);															//add the attribute to the new cell
												//now we add (and format) a div that will contain the image and the text
  outerDiv = document.createElement("div");														//create a new div-element
  outerDivStyle = document.createAttribute("class");											//create a new "class" attribute
  outerDivStyle.nodeValue="style_wrapper";														//set the new attribute's value to "style_wrapper"
  outerDiv.setAttributeNode(outerDivStyle);														//add the attribute to the new div-element
  itemCell.appendChild(outerDiv);																//append the div to the table cell
												//here, we add the image, taking the image data from the rewardItem, and we apply a style to it
  itemIcon = document.createElement("img");														//create a new image element
  itemIcon.src = rewardItem.itemIcon;
  iconStyle = document.createAttribute("class");												//create a new "class" attribute
  iconStyle.nodeValue="style_icon";																//set the new attribute's value to "style_icon"

  //alert("here");
  //itemIcon.onmouseover=function(){showTip(rewardItem.itemHTML)};
  //itemIcon.onmouseout=function(){hideTip()};

  itemIcon.setAttributeNode(iconStyle);															//add the attribute to the new image element
  outerDiv.appendChild(itemIcon);																//append the icon to the div
												//create a new font element that will contain the item's name
  nameFont = document.createElement("font");													//create a new "font" element
  nameStyle = document.createAttribute("class");												//create a new "class" attribute
  nameStyle.nodeValue="style_name";																//set the attribute's value to "style_name"
  nameFont.setAttributeNode(nameStyle);															//add the attribute to then new font element
  rewardName = document.createTextNode(rewardItem.itemName);									//create a "text" node containing the item name
  nameFont.appendChild(rewardName);																//append the text to the font element
  outerDiv.appendChild(nameFont);																//append the font element to the div
  outerDiv.innerHTML="<a onmouseover=showTip(RewardItems["+i+"].itemHTML) onmouseout='hideTip();' ondblclick='dharma_pearl();'>"+outerDiv.innerHTML+"</a>";
  
  if (rewardItem.itemCost != "none")
  {
    priceDiv = document.createElement("div");													//create a new "div" element
    priceStyle = document.createAttribute("class");												//create a new "class" attribute
    priceStyle.nodeValue="style_price";															//set the attribute's value to "style_price"
    priceDiv.setAttributeNode(priceStyle);														//add the attribute to then new div element
    priceDiv.innerHTML = rewardItem.itemCost;													//add the actual price as innerHTML
    outerDiv.appendChild(priceDiv);																//append the price to the div element
  }
  
  return itemCell;																				//pass the new cell back to the calling instance
}
//------END ADDING AN ITEM------

function switchClick(factionA,factionB)
{
	mouseMoveIn(factionA+"Button");
  mouseMoveOut(factionB+"Button");
	document.getElementById(factionA+"Rewards").style.visibility = "visible";
  document.getElementById(factionB+"Rewards").style.visibility = "hidden";
	document.getElementById("loreText").innerHTML = loreTexts[factionA];
}

function mouseMoveIn(thisElement) { document.getElementById(thisElement).style.backgroundPosition = "top left"; }
function mouseMoveOut(thisElement) { document.getElementById(thisElement).style.backgroundPosition = "bottom left"; }

function hiliteBlink(thisElement)
{
	mouseMoveIn(thisElement);
	window.setTimeout("mouseMoveOut('"+thisElement+"')", 500);
}

loreTexts = new Object();
