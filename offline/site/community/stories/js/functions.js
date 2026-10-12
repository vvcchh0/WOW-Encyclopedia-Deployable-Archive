function grabXML(somefile){ 
if (window.XMLHttpRequest) { var xmldata = new XMLHttpRequest(); }
else { var xmldata = new ActiveXObject("MSXML2.XMLHTTP.3.0"); }

xmldata.onreadystatechange = function() { 
	if(xmldata.readyState == 4)
	{ 
		if(xmldata.responseXML != null) parsedata(xmldata.responseXML);
  	else {  alert("Data Failure");  }
	}
}

xmldata.open("GET", somefile, true);
xmldata.send(null);

}

function parsedata(dataref)
{ 
  data = dataref.getElementsByTagName("batch")
  alert(data.childNodes.length);

}

function getStoryId()
{ cpg = (document.location.href) ? document.location.href : document.location;
	if(cpg.indexOf("?")>0)
	{	parr = cpg.split('#'); cpg = parr[parr.length-1];
		storyid = cpg.slice(cpg.indexOf('storyid=') + 1); }
}

function showStory(targ)
{ //alert(targ.parentNode.parentNode.parentNode.parentNode.parentNode); 
 pdiv = targ.parentNode.parentNode.parentNode.parentNode
  tdivs = pdiv.getElementsByTagName("div")
  alinks = pdiv.parentNode.getElementsByTagName("a");
  //alert(alinks.length + " : tdivs : " + tdivs.length);
if(tdivs[0].style.display == "none"){
  tdivs[0].style.display = "block";
  tdivs[1].style.display = "none";
  alinks[1].style.display = "none";  
}
else {
  tdivs[0].style.display = "none";
  tdivs[1].style.display = "block";
  alinks[1].style.display = "block";
	}
}