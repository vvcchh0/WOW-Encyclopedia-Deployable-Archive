function replaceText()
{
	iNdex = 0;
  topicList.sort(wordSort);
  allText = document.getElementsByTagName("p");
  for(iNdex=0; iNdex < topicList.length; iNdex++)
  {
    keepGoing = true;
		for(i=0; i<allText.length; i++) { textRecursive(allText[i]); }
  }
}

function textRecursive(thisElement)
{
  if(thisElement.hasChildNodes())
  {
		var j=0;
		for(j=0;j<thisElement.childNodes.length;j++)
		{
			if(thisElement.childNodes[j].nodeName != "A" && thisElement.childNodes[j].nodeName != "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fencyclopedia%2Fscripts%2Flink-generator.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2FA&reason=external-or-uncollected-resource") textRecursive(thisElement.childNodes[j]);
		}
	}
	else
	{
		if (thisElement.data && topicsArray[topicList[iNdex]].topic != document.title)
		{
			lowestBall = thisElement.data.length;
			findFirstOccurrence = new RegExp("\\b"+topicsArray[topicList[iNdex]].topic+"\\b","i");
			lowBall = thisElement.data.search(findFirstOccurrence);
			if(lowBall >= 0 && lowBall < lowestBall)
			{
				replaceTargetString = topicsArray[topicList[iNdex]].topic;
				lowestBall = lowBall;
			}
			if(topicsArray[topicList[iNdex]].synonymsArray)
			{
				for(l = 0; l < topicsArray[topicList[iNdex]].synonymsArray.length; l++)
				{
					findFirstOccurrence = new RegExp("\\b"+topicsArray[topicList[iNdex]].synonymsArray[l]+"\\b","i");
					lowBall = thisElement.data.search(findFirstOccurrence);
					if(lowBall >= 0 && lowBall < lowestBall)
					{
						replaceTargetString = topicsArray[topicList[iNdex]].synonymsArray[l];
						lowestBall = lowBall;
					}
				}
			}
			if (lowestBall < thisElement.data.length && keepGoing)
			{
				keepGoing = false;
				if(thisElement.parentNode.nodeName != "SPAN") replaceWithLink(thisElement,replaceTargetString);
			}
		}
  } 
}

function replaceWithLink(thisElement,thisString)
{
	findThisString = new RegExp('\\b'+thisString+'\\b',"i");
	replaceString = "<a href="+topicsArray[topicList[iNdex]].linkString+">"+thisElement.parentNode.innerHTML.match(findThisString)+"</a>";  
	stringBuffer = thisElement.parentNode.innerHTML.replace(findThisString,replaceString);
  thisElement.parentNode.innerHTML = stringBuffer;
}

function wordSort(aItem, bItem) { return bItem.split(" ").length - aItem.split(" ").length; }