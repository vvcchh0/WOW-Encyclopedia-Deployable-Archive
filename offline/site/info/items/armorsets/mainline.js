//Objects
function CharacterClass(allowedRaces,classesName,classesID)
{
	//Properties
	this.allowedRaces = allowedRaces;
	this.classesName = classesName;
	this.classesID = classesID;
	//Methods
	this.filterRaces = characterClassFilterFunction;
}

function CharacterRace(allowedClasses,raceName,raceID,pvpFaction)
{
	//Properties
	this.allowedClasses = allowedClasses;
	this.raceName = raceName;
	this.raceID = raceID;
	this.pvpFaction = pvpFaction;
	//Methods
	this.filterClasses = characterRaceFilterFunction;
}

function ArmorSet(setName,itemIDs,characterClass,pvpFaction)
{
	//Properties
	this.setName = setName;
	this.itemIDs = itemIDs;
	this.characterClass = characterClass;
	this.pvpFaction = pvpFaction;
	//Methods
	this.updateImage = imageUpdater;
	this.updateNav = navUpdater;
	this.isntForRace = raceEligibilityCheck;
}

function PvPSubSetsContainer(childSets,pvpFaction)
{
	this.pvpFaction = pvpFaction;
	this.childSets = childSets;
	this.isPvPSetContainer = true;
}

//Methods
function characterClassFilterFunction()
{
	for(i=0; i<10; i++)
	{
		graveyard.appendChild(raceDropdown[i]);
	}
	for(i=0; i<this.allowedRaces.length; i++)
	{
		raceDropdownRoot.appendChild(document.getElementById(this.allowedRaces[i].raceName+"Option"));
	}
	document.getElementById(currentRace.raceName+"Option").selected = true;
}

function characterRaceFilterFunction()
{
	for(i=0; i<9; i++) { classDropdown[i].className = "ineligible"; }
	for(i=0; i<this.allowedClasses.length; i++)
	{
		document.getElementById(this.allowedClasses[i]+"Option").className = "eligible";
	}
	document.getElementById(currentClass.classesName+"Option").selected = true;
}

function imageUpdater()
{
	var tempSubsetNumber = (this.pvpFaction == "horde" || this.pvpFaction == "alliance") ? "" : subSetNumber;
	mainSetImage.style.backgroundImage = "url(/info/items/armorsets/images/"+currentTierPath+"/"+this.characterClass.classesName+tempSubsetNumber+"/"+currentRace.raceName+"-"+currentGender+".jpg)";
}

function navUpdater()
{
	this.characterClass.filterRaces();
	currentRace.filterClasses();
	var tempSubsetNumber = (this.pvpFaction == "horde" || this.pvpFaction == "alliance") ? "" : subSetNumber;
	for(i=0; i<9; i++) { inventoryThumbs[i].style.display = "none"; };
	inventoryContainer.style.height = Math.round(this.itemIDs.length/2)*64+2+"px";
	for(i=0; i<this.itemIDs.length; i++)
	{
		inventoryThumbs[i].name = this.itemIDs[i];
		inventoryThumbs[i].style.cssFloat = inventoryThumbs[i].style.styleFloat = "left";
		inventoryThumbs[i].style.display = "block";
		inventoryThumbs[i].style.backgroundImage = "url(/info/items/armorsets/images/"+currentTierPath+"/"+this.characterClass.classesName+tempSubsetNumber+"/"+armorPieces[i]+".jpg)";
		inventoryThumbs[i].onmouseover = function() { enhancedTooltipFilter(this.name); /*enhancedXmlTTip(this.name);*/ };
		inventoryThumbs[i].onmouseout = function() { hideTip(); };
	}
	if(this.itemIDs.length%2 == 1) inventoryThumbs[this.itemIDs.length-1].style.cssFloat = inventoryThumbs[this.itemIDs.length-1].style.styleFloat = "none";
	nameHolder.innerHTML = this.setName;
}

function raceEligibilityCheck()
{
	var testResult = true;
	for(i = 0; i<this.characterClass.allowedRaces.length; i++)
	{
		if(currentRace.raceID == this.characterClass.allowedRaces[i].raceID) testResult = false;
	}
	return testResult;
}

//UI Functions
function loadSet(thisSet,resetSubSetNumber)
{
	if(thisSet.length == null)
	{
		//subSetContainer.style.display = "none";
		graveyard.appendChild(subSetContainer);
		if(thisSet.isntForRace(currentRace))
		{
			if(thisSet.pvpFaction)
			{
				for(i=0;i<thisSet.characterClass.allowedRaces.length;i++)
				{
					if(currentRace.pvpFaction == thisSet.characterClass.allowedRaces[i].pvpFaction)
					{
						currentRace = thisSet.characterClass.allowedRaces[i];
						i = thisSet.characterClass.allowedRaces.length;
					}
				}
			}
			else { currentRace = thisSet.characterClass.allowedRaces[1]; }
		}
		thisSet.updateNav();
		thisSet.updateImage();
	}
	else
	{
		if(subSetNumber == "" || resetSubSetNumber == true) { subSetNumber = 1; }
		currentSets = thisSet;
		if(currentSets[0].isPvPSetContainer)
		{
			if(pvpSubSetNumber == "") { pvpSubSetNumber = 0; }
			if(thisSet[pvpSubSetNumber].pvpFaction != currentRace.pvpFaction) { pvpSubSetNumber = (pvpSubSetNumber == 0) ? 1 : 0; }
			var storedPvPSubSetNumber = pvpSubSetNumber;
			currentContainer = thisSet[pvpSubSetNumber];
			loadSet(currentContainer.childSets);
			lastChange = "class";
			displaySubSetDropDown(thisSet[pvpSubSetNumber].childSets);
		}
		else
		{
			displaySubSetDropDown(thisSet);
			if(thisSet[subSetNumber-1].pvpFaction) 
			{
				if(thisSet[subSetNumber-1].pvpFaction != currentRace.pvpFaction) { subSetNumber = (subSetNumber == 1) ? 2 : 1; }
				displaySubsets = false;
			}
			loadSet(thisSet[subSetNumber-1]);
		}
		if(displaySubsets) mainUI.insertBefore(subSetContainer,characterClassUI);
	}
}

function displaySubSetDropDown(thisSet)
{
	displaySubsets = true;
	if(lastChange == "class" || lastChange == "tier")
	{
		var subSetString = "";
		subSetDropdown.innerHTML = "";
		for(i=0; i<thisSet.length; i++)
		{
			isSelected = (i == subSetNumber-1) ? "true" : "";
			var newOption = document.createElement("option");
			newOption.value = i;
			newOption.selected = isSelected;
			newOption.innerHTML = thisSet[i].setName;
			subSetDropdown.appendChild(newOption);
		}
	}
}

function loadSubSet(thisSet)
{
	subSetNumber = eval(thisSet)+1;
	if(currentSets[thisSet].isntForRace(currentRace))
	{
		currentRace = currentSets[thisSet].characterClass.allowedRaces[1];
	}
	currentSets[thisSet].updateNav();
	currentSets[thisSet].updateImage();
}

function loadTier(thisTier)
{
	subSetNumber = "";
	lastChange = "tier";
	currentTierPath = thisTier;
	currentTier = tierCollection[thisTier];
	loadSet(currentTier[currentClass.classesName]);
}

function loadClass(thisClass)
{
	subSetNumber = "";
	lastChange = "class";
	currentClass = classCollection[thisClass];
	loadSet(currentTier[currentClass.classesName]);
}

function loadRace(thisRace)
{
	lastChange = "race";
	currentRace = raceCollection[thisRace];
	loadSet(currentTier[currentClass.classesName]);
}

function loadGender(thisGender)
{
	lastChange = "sex";
	currentGender = thisGender;
	loadSet(currentTier[currentClass.classesName]);
}

function enhancedTooltipFilter(thisID)
{
	if(threadCounter<10)
	{
		enhancedXmlTTip(thisID);
	}
	else
	{
		if(document.getElementById(thisID) == null) showTip("Waiting for server response...");
		else
		{
			currentlyViewedItem = thisID;
			showTip(document.getElementById(thisID).innerHTML);
		}
	}
}

//Constants
raceCollection = new Object();
raceCollection["draenei"] = raceDraenei = new CharacterRace(["hunter","mage","paladin","priest","shaman","warrior"],"draenei",0,"alliance");
raceCollection["dwarf"] = raceDwarf = new CharacterRace(["hunter","paladin","priest","rogue","warrior"],"dwarf",1,"alliance");
raceCollection["gnome"] = raceGnome = new CharacterRace(["mage","rogue","warlock","warrior"],"gnome",2,"alliance");
raceCollection["human"] = raceHuman = new CharacterRace(["mage","paladin","priest","rogue","warlock","warrior"],"human",3,"alliance");
raceCollection["nightelf"] = raceNightelf = new CharacterRace(["druid","hunter","priest","rogue","warrior"],"nightelf",4,"alliance");
raceCollection["bloodelf"] = raceBloodelf = new CharacterRace(["hunter","mage","paladin","priest","rogue","warlock"],"bloodelf",5,"horde");
raceCollection["orc"] = raceOrc = new CharacterRace(["hunter","rogue","shaman","warlock","warrior"],"orc",6,"horde");
raceCollection["tauren"] = raceTauren = new CharacterRace(["druid","hunter","shaman","warrior"],"tauren",7,"horde");
raceCollection["troll"] = raceTroll = new CharacterRace(["hunter","mage","priest","rogue","shaman","warrior"],"troll",8,"horde");
raceCollection["undead"] = raceUndead = new CharacterRace(["mage","priest","rogue","warlock","warrior"],"undead",9,"horde");

classCollection = new Object();
classCollection["druid"] = new CharacterClass([raceNightelf,raceTauren],"druid",0);
classCollection["hunter"] = new CharacterClass([raceDraenei,raceDwarf,raceNightelf,raceBloodelf,raceOrc,raceTauren,raceTroll],"hunter",1);
classCollection["mage"] = new CharacterClass([raceDraenei,raceGnome,raceHuman,raceBloodelf,raceTroll,raceUndead],"mage",2);
classCollection["paladin"] = new CharacterClass([raceDraenei,raceDwarf,raceHuman,raceBloodelf],"paladin",3);
classCollection["priest"] = new CharacterClass([raceDraenei,raceDwarf,raceHuman,raceNightelf,raceBloodelf,raceTroll,raceUndead],"priest",4);
classCollection["rogue"] = new CharacterClass([raceDwarf,raceGnome,raceHuman,raceNightelf,raceBloodelf,raceOrc,raceTroll,raceUndead],"rogue",5);
classCollection["shaman"] = new CharacterClass([raceDraenei,raceOrc,raceTauren,raceTroll],"shaman",6);
classCollection["warlock"] = new CharacterClass([raceGnome,raceHuman,raceBloodelf,raceOrc,raceUndead],"warlock",7);
classCollection["warrior"] = new CharacterClass([raceDraenei,raceDwarf,raceGnome,raceHuman,raceNightelf,raceOrc,raceTauren,raceTroll,raceUndead],"warrior",8);

//Initiator Function
function firstLoad()
{
	lastChange = "";
	currentGender = "female";
	subSetNumber = "";
	pvpSubSetNumber = "";
	currentClass = classCollection["druid"];
	currentRace = raceHuman;
	currentTier = dungeonOne;
	currentTierPath = "dungeon1";
	displaySubsets = true;
	mainUI = document.getElementById("uiTableElement");
	characterClassUI = document.getElementById("characterClassRow");
	inventoryContainer = document.getElementById("inventoryFrameDiv");
	subSetContainer = document.getElementById("subSetRow");
	subSetDropdown = document.getElementById("subSetSelector");
	nameHolder = document.getElementById("nameHolderDiv");
	mainSetImage = document.getElementById("mainSetImageDiv");
	graveyard = document.getElementById("graveyardDiv");
	classDropdownRoot = document.getElementById("classSelector");
	raceDropdownRoot = document.getElementById("raceSelector");
	var i = 0;
	raceDropdown = new Object();
	raceDropdown[i++] = document.getElementById("draeneiOption");
	raceDropdown[i++] = document.getElementById("dwarfOption");
	raceDropdown[i++] = document.getElementById("gnomeOption");
	raceDropdown[i++] = document.getElementById("humanOption");
	raceDropdown[i++] = document.getElementById("nightelfOption");
	raceDropdown[i++] = document.getElementById("bloodelfOption");
	raceDropdown[i++] = document.getElementById("orcOption");
	raceDropdown[i++] = document.getElementById("taurenOption");
	raceDropdown[i++] = document.getElementById("trollOption");
	raceDropdown[i++] = document.getElementById("undeadOption");
	i=0;
	classDropdown = new Array();
	classDropdown[i++] = document.getElementById("druidOption");
	classDropdown[i++] = document.getElementById("hunterOption");
	classDropdown[i++] = document.getElementById("mageOption");
	classDropdown[i++] = document.getElementById("paladinOption");
	classDropdown[i++] = document.getElementById("priestOption");
	classDropdown[i++] = document.getElementById("rogueOption");
	classDropdown[i++] = document.getElementById("shamanOption");
	classDropdown[i++] = document.getElementById("warlockOption");
	classDropdown[i++] = document.getElementById("warriorOption");
	i=0;
	inventoryThumbs = new Array();
	inventoryThumbs[i++] = document.getElementById("inventoryHead");
	inventoryThumbs[i++] = document.getElementById("inventoryChest");
	inventoryThumbs[i++] = document.getElementById("inventoryHands");
	inventoryThumbs[i++] = document.getElementById("inventoryShoulder");
	inventoryThumbs[i++] = document.getElementById("inventoryLegs");
	inventoryThumbs[i++] = document.getElementById("inventoryFeet");
	inventoryThumbs[i++] = document.getElementById("inventoryWrist");
	inventoryThumbs[i++] = document.getElementById("inventoryWaist");
	inventoryThumbs[i++] = document.getElementById("inventoryRing");
	i=0;
	armorPieces = new Array();
	armorPieces[i++] = "head";
	armorPieces[i++] = "chest";
	armorPieces[i++] = "hands";
	armorPieces[i++] = "shoulder";
	armorPieces[i++] = "legs";
	armorPieces[i++] = "feet";
	armorPieces[i++] = "wrist";
	armorPieces[i++] = "waist";
	armorPieces[i++] = "finger";
	loadSet(currentTier[currentClass.classesName]);
}