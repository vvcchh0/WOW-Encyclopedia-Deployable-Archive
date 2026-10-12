//flash detection
var MM_contentVersion = 8;
var plugin = (navigator.mimeTypes && navigator.mimeTypes["application/x-shockwave-flash"]) ? navigator.mimeTypes["application/x-shockwave-flash"].enabledPlugin : 0;
if ( plugin ) {
		var words = navigator.plugins["Shockwave Flash"].description.split(" ");
	    for (var i = 0; i < words.length; ++i)
	    {
		if (isNaN(parseInt(words[i])))
		continue;
		var MM_PluginVersion = words[i]; 
	    }
	var MM_FlashCanPlay = MM_PluginVersion >= MM_contentVersion;
}
else if (navigator.userAgent && navigator.userAgent.indexOf("MSIE")>=0 
   && (navigator.appVersion.indexOf("Win") != -1)) {
	document.write('<SCR' + 'IPT LANGUAGE=VBScript\> \n'); //FS hide this from IE4.5 Mac by splitting the tag
	document.write('on error resume next \n');
	document.write('MM_FlashCanPlay = ( IsObject(CreateObject("ShockwaveFlash.ShockwaveFlash." & MM_contentVersion)))\n');
	document.write('</SCR' + 'IPT\> \n');
}

var flashString;
var tempObj;
var flashCount=1;
//printFlash uses innerHTML to render flash objs to get around the IE flash rendering issue
function printFlash(id, src, wmode, menu, bgcolor, width, height, quality, base, flashvars, allowScriptAccess, noflash){
	
	if(MM_FlashCanPlay && getcookie("showflash")!="false"){
		
		flashString = '<object id= "' + id + 'Flash" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="' + width + '" height="' + height + '"><param name="movie" value="' + src + '"></param><param name="quality" value="' + quality + '"></param>';
		if(base){
		flashString+='<param name="base" value="' + base + '"/>';
		}
		if(allowScriptAccess){
		flashString+='<param name="allowScriptAccess" value="' + allowScriptAccess + '"/>';
		}
		
		flashString+='<param name="flashvars" value="' + flashvars + '" ></param><param name="bgcolor" value="' + bgcolor + '" ></param><param name="menu" value="' + menu + '" ></param><param name="wmode" value="' + wmode + '" ></param><param name="salign" value="tl" ></param><embed name= "' + id + 'Flash" src="' + src + '" wmode="' + wmode + '" menu="' + menu + '" bgcolor="' + bgcolor + '" width="' + width + '" height="' + height + '" quality="' + quality + '" pluginspage="/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fjs%2Ffunctions.js&requested=http%3A%2F%2Fwww.macromedia.com%2Fgo%2Fgetflas%2Fnew-hplayer&reason=external-or-uncollected-resource" type="application/x-shockwave-flash" salign="tl" base="' + base + '"allowScriptAccess="' + allowScriptAccess + '" flashvars="' + flashvars + '" /></object>';
		
	}else{
	
		flashString=noflash;

	}
	
	if(is_opera && is_mac && id=="flashfeatured")//kill the WotLK flash feature box for Mac Opera
		flashString=noflash;
		
		
	if(is_safari)
		document.write(flashString)
	else	
		document.getElementById(id).innerHTML = flashString;
	
	document.getElementById(id).style.display="block";
		
}

function dropdownMenuToggle(whichOne){
	theStyle = document.getElementById(whichOne).style;

	if (theStyle.display == "none") {
		theStyle.display = "block";	
	} else
		theStyle.display = "none";
}


function selectLang(theDisplay, cookieValue) {
	document.getElementById("dropdownHiddenLang").style.display = "none";
	document.getElementById("displayLang").innerHTML = theDisplay;
	setcookie("cookieLangId", cookieValue, "");
	/*
  	if(cookieValue == "en_us") {
    	document.location.href="/index.xml"+roothost;
  	} else if(cookieValue == "ko_kr") {
    	document.location.href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fjs%2Ffunctions.js&requested=http%3A%2F%2Fwww.worldofwarcraft.co.kr&reason=external-or-uncollected-resource"+roothost;
  	} else {
    	document.location.href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fjs%2Ffunctions.js&requested=http%3A%2F%2Fwww.wow-europe.com&reason=external-or-uncollected-resource"+roothost;
  	}
	*/
		
	document.location.reload();
	
	/*
		document.getElementById("dropdownHiddenLang").style.display = "none";
	document.getElementById("displayLang").innerHTML = theDisplay;
  	setcookie("cookieLangId", cookieValue, "");
  	
	if(cookieValue == "en_us") {
    	document.location.href="/index.xml"+roothost;
  	} else if(cookieValue == "ko_kr") {
    	document.location.href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fjs%2Ffunctions.js&requested=http%3A%2F%2Fwww.worldofwarcraft.co.kr&reason=external-or-uncollected-resource"+roothost;
  	} else {
    	document.location.href="/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fwrath%2Fjs%2Ffunctions.js&requested=http%3A%2F%2Fwww.wow-europe.com&reason=external-or-uncollected-resource"+roothost;
  	}
	
	//document.location.reload();
	*/
	
	
	
	
	
}

function getexpirydate(nodays){
	var UTCstring;
	Today = new Date();
	nomilli=Date.parse(Today);
	Today.setTime(nomilli+nodays*24*60*60*1000);
	UTCstring = Today.toUTCString();
	return UTCstring;
}

function getcookie(cookiename) {
	 var cookiestring=""+document.cookie;
	 var index1=cookiestring.indexOf(cookiename);
	 if (index1==-1 || cookiename=="") return ""; 
	 var index2=cookiestring.indexOf(';',index1);
	 if (index2==-1) index2=cookiestring.length; 
	 return unescape(cookiestring.substring(index1+cookiename.length+1,index2));
}

function setcookie(name,value,expire,domain){
	var expireString="EXPIRES="+ getexpirydate(365)+";"
	var domainString="DOMAIN="+ domain
	if(expire=="session")
		expireString="";
	if(!domain)
		domainString="";		
	cookiestring=name+"="+escape(value)+";"+expireString+"PATH=/;"+domainString;
	document.cookie=cookiestring;
}

function toggleFlash(){

	if(MM_FlashCanPlay){
		if(getcookie("showflash")=="false")
			setcookie("showflash", "true");
		else
			setcookie("showflash", "false");
	}
	document.location.reload();

}

function showNoflashMessage(){

	if(!MM_FlashCanPlay){
	
		document.getElementById("noflash-message").style.display="block";
	
	}

}


ticked = 0;
animationLock = false;

function fiatLux(thisImage)
{
 if(!animationLock)
 {
	animationLock = true;
	imageHolder = new Image();
	document.getElementById("lightBoxRoot").style.visibility = "hidden";
	document.getElementsByTagName("body")[0].appendChild(document.getElementById("blackDrop"));
	document.getElementsByTagName("body")[0].appendChild(document.getElementById("lightBoxRoot"));
	imageHolder.src = thisImage;
	windowWidth = (window.innerWidth) ? window.innerWidth : document.documentElement.clientWidth;
	windowHeight = (window.innerHeight) ? window.innerHeight : document.documentElement.clientHeight;
	scrollDistance = (navigator.userAgent.indexOf("Safari")==-1) ? document.documentElement.scrollTop : window.pageYOffset;
	displayLightBox();
 }
}

function displayLightBox()
{
	if(imageHolder.complete)
	{
		document.getElementById("lightBoxHolder").style.width = imageHolder.width + "px";
		document.getElementById("lightBoxHolder").style.height = imageHolder.height + "px";
		document.getElementById("lightBoxHolder").style.backgroundImage = "url("+imageHolder.src+")";
		document.getElementById("lightBoxRoot").style.width = imageHolder.width + 20 + "px";
		document.getElementById("lightBoxRoot").style.height = imageHolder.height + 20 + "px";
		document.getElementById("lightBoxRoot").style.left = (windowWidth/2)-(imageHolder.width/2) + "px";
		document.getElementById("blackDrop").style.display = "block";
		document.getElementById("blackDrop").style.height = document.body.scrollHeight+"px";
		document.getElementById("lightBoxRoot").style.top = 40+scrollDistance+"px";
		document.getElementById("lightBoxRoot").style.visibility = "visible";
		delete imageHolder;
		animationLock = false;
	}
	else window.setTimeout("displayLightBox()",250);
}

function fadeLightBox()
{
	if(ticked==20)
	{
		window.clearInterval(fadeAnimationHolder);
		ticked = 0;
		delete imageHolder;
		animationLock = false;
	}
	else
	{
		document.getElementById("lightBoxRoot").style.opacity = ticked/10;
		document.getElementById("lightBoxRoot").style.filter = "alpha(opacity="+100+")";
		ticked += 10;
	}
}

function closeLightbox()
{
	if(!animationLock)
	{
		document.getElementById("lightBoxRoot").style.visibility = "hidden";
		document.getElementById("blackDrop").style.display = "none";
	}
}

function showall(targ)
{ p = targ.parentNode.parentNode; //alert(p)
  for(i=2; i<p.childNodes.length; i++)
{ cn = p.childNodes[i]; 
  if(cn.className.indexOf("coll")>=0){
	  tdisp = cn.style.display
	  cn.style.display = (tdisp=="block")?"none":"block"; 
	  targ.className = (tdisp == "block")?"feature-toggle":"feature-toggle-up"
	  targ.childNodes[0].innerHTML = (tdisp == "block")?showAll:showLess
	  } }
}