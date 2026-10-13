/***********************************************
* Cool DHTML tooltip script- � Dynamic Drive DHTML code library (www.dynamicdrive.com)
* This notice MUST stay intact for legal use
* Visit Dynamic Drive at http://www.dynamicdrive.com/ for full source code
***********************************************/
var toolTipPage = 1;
var agt=navigator.userAgent.toLowerCase();
var offsetxpoint=10 //Customize x offset of tooltip
var offsetypoint=-10 //Customize y offset of tooltip
var ie=document.all
var ns6=document.getElementById && !document.all
var is_safari = ((agt.indexOf('safari')!=-1)&&(agt.indexOf('mac')!=-1))?true:false;
var enabletip=false


if (ie||ns6)
var contentobj=document.all? document.all["contents"] : document.getElementById? document.getElementById("contents") : ""
var tipTextObj=document.all? document.all["tooltipText"] : document.getElementById? document.getElementById("tooltipText") : ""
var dynamicTipObj=document.all? document.all["dynamicTooltip"] : document.getElementById? document.getElementById("dynamicTooltip") : ""

function ietruebody(){
return (document.compatMode && document.compatMode!="BackCompat")? document.documentElement : document.body
}

function ddrivetip(thetext, thecolor, thewidth){
if (ns6||ie){

if (thetext.indexOf("~") >= 0) {
	//alert(thetext.substring(1,thetext.length))
	eval("tipTextObj.innerHTML = " + thetext.substring(1,thetext.length) + ".innerHTML");
} else {
	tipTextObj.innerHTML = thetext;
	tipTextObj.style.color=thecolor;
}

if (typeof thewidth=="undefined"){ 
	contentobj.style.width=tipTextObj.clientWidth+"px";
	contentobj.style.height=tipTextObj.clientHeight+"px";
} else {

	contentobj.style.width=thewidth+"px";
}

enabletip=true
return false
}
}

function positiontip(e){

if (enabletip){

	var posx = 0;
	var posy = 0;
	if (!e) var e = window.event;
	if (e.pageX || e.pageY)
	{
		posx = e.pageX;
		posy = e.pageY;
		
	}
	else if (e.clientX || e.clientY)
	{
		posx = e.clientX + document.body.scrollLeft;
		posy = e.clientY + document.body.scrollTop;
		
	}
	// posx and posy contain the mouse position relative to the document
	//alert(posx + "," + posy)
	contentobj.style.left=posx+offsetxpoint;
	contentobj.style.top=posy+offsetypoint;
	contentobj.style.visibility="visible"
	tipTextObj.style.visibility="visible"
}
}

function hideddrivetip(){
if (ns6||ie){
enabletip=false
contentobj.style.visibility="hidden"
contentobj.style.left="-1000px"
contentobj.style.backgroundColor=''
contentobj.style.width=''
}
}

document.onmousemove=positiontip
