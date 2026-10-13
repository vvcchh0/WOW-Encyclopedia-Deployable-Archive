var global_nav_lang, opt;

function buildtopnav(){

global_nav_lang = (global_nav_lang) ? global_nav_lang.toLowerCase() : "";

linkarray = new Array(); 
outstring = "";

switch(global_nav_lang){
 case "fr_fr": 
	link1 = new Object();
	link1.text = "WoW-Europe.com"
	link1.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wow-europe.com%2Ffr%2Findex.xml&reason=external-or-uncollected-resource"

	link2 = new Object();
	link2.text = "l'Armurerie"
	link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Feu.wowarmory.com%2F&reason=external-or-uncollected-resource"
	
	link3 = new Object();
	link3.text = "Forums"
	link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.wow-europe.com%2Findex.html%3Fsid%3D2&reason=external-or-uncollected-resource"
 break;
 
 case "es_es": 
 	link1 = new Object();
	link1.text = "WoW-Europe.com"
	link1.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wow-europe.com%2Fes%2Findex.xml&reason=external-or-uncollected-resource"

	link2 = new Object();
	link2.text = "La Armería"
	link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Feu.wowarmory.com%2F&reason=external-or-uncollected-resource"
	
	link3 = new Object();
	link3.text = "Foros"
	link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.wow-europe.com%2Findex.html%3Fsid%3D4&reason=external-or-uncollected-resource"
 break;
 
 case "en_gb": 
 	link1 = new Object();
	link1.text = "WoW-Europe.com"
	link1.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wow-europe.com%2Fen%2Findex.xml&reason=external-or-uncollected-resource"

	link2 = new Object();
	link2.text = "Armory"
	link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Feu.wowarmory.com%2F&reason=external-or-uncollected-resource"
	
	link3 = new Object();
	link3.text = "Forums"
	link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.wow-europe.com%2Findex.html%3Fsid%3D1&reason=external-or-uncollected-resource"
 break;

 case "de_de": 
 	link1 = new Object();
	link1.text = "WoW-Europe.com"
	link1.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wow-europe.com%2Fde%2Findex.xml&reason=external-or-uncollected-resource"

	link2 = new Object();
	link2.text = "Das Arsenal"
	link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Feu.wowarmory.com%2F&reason=external-or-uncollected-resource"
	
	link3 = new Object();
	link3.text = "Foren"
	link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.wow-europe.com%2Findex.html%3Fsid%3D3&reason=external-or-uncollected-resource"
 break;

case "zh_tw":
 	link1 = new Object();
	link1.text = "魔獸世界官網"
	link1.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wowtaiwan.com.tw&reason=external-or-uncollected-resource"

	link2 = new Object();
	link2.text = "英雄榜"
	link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Ftw.wowarmory.com%2F&reason=external-or-uncollected-resource"
	
	link3 = new Object();
	link3.text = "官網論壇"
	link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforum.wowtaiwan.com.tw%2Ftwow_forums_page1.asp&reason=external-or-uncollected-resource"
	opt = false;
break;

case "ko_kr":
	opt = true;
break;

 case "es_mx": 
 	link1 = new Object();
	link1.text = "WorldofWarcraft.com"
	link1.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fes%2F&reason=invalid-overlay-or-uncollected-site-resource"

	link2 = new Object();
	link2.text = "La Armeria"
	link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wowarmory.com%2F&reason=external-or-uncollected-resource" 	
	
	link3 = new Object();
	link3.text = "Foros"
	link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Findex.html%3Fsid%3D2&reason=invalid-overlay-or-uncollected-site-resource"
 break;
 
  case "ru_ru": 
 	link1 = new Object();
	link1.text = "Wow-Europe.com"
	link1.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wow-europe.com%2Fru%2Findex.xml&reason=external-or-uncollected-resource"

	link2 = new Object();
	link2.text = "Оружейная"
	link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Feu.wowarmory.com%2F&reason=external-or-uncollected-resource" 	
	
	link3 = new Object();
	link3.text = "Форумы"
	link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.wow-europe.com%2Findex.html%3Fsid%3D5&reason=external-or-uncollected-resource"
 break;


 default:
    link1 = new Object();
    link1.text = "WorldofWarcraft.com"
    link1.href = "/WOW-Encyclopedia-Deployable-Archive/index.xml.html"
    
    link2 = new Object();
    link2.text = "The Armory"
    link2.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fwww.wowarmory.com%2F&reason=external-or-uncollected-resource"
    
    link3 = new Object();
    link3.text = "Forums"
    link3.href = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Findex.html%3Fsid%3D1&reason=invalid-overlay-or-uncollected-site-resource"
break;
 
}

//
linkarray.push(link1) 
linkarray.push(link2)
linkarray.push(link3)

for(i=0; i<linkarray.length; i++)
{ div = (i<linkarray.length-1) ? "<img src='/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fforums.worldofwarcraft.com%2Fjs%2Fbuildtopnav.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fimages%2Ftopnav_div.gif&reason=invalid-overlay-or-uncollected-site-resource'/>":""
  outstring += "<a href='"+linkarray[i].href+ "'>"+ linkarray[i].text +"</a>"+div; }

	topnavguts = "";
	topnavguts += "<div class='topnav'><div class='tn_interior'>";
	topnavguts += outstring;
	topnavguts += "</div></div><div class='tn_push'></div>";
	
	if(document.location.href) hrefString = document.location.href; else hrefString = document.location;
	
	divclass = (hrefString.indexOf("forums")>=0)?"tn_forums":(hrefString.indexOf("armory")>=0)?"tn_armory":"tn_wow";

	targ = document.getElementById("shared_topnav");
    if(targ != null) {
    	targ.innerHTML = topnavguts;
    	if(!targ.className || targ.className == ""){targ.className = divclass;}
    	if(targ.className.indexOf("tn_armory")>=0){ document.body.style.backgroundPosition = "50% 26px"; }
    	if(targ.className.indexOf("tn_forums")>=0){ document.body.style.backgroundPosition = "100% 26px"; } 

    }
}

buildtopnav();