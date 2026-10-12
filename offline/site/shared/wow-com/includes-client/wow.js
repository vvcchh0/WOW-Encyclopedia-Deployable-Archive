


	var styleSheet;

	var agt    = navigator.userAgent.toLowerCase();
	var appVer = navigator.appVersion.toLowerCase();

	var verInt = parseInt(appVer);

	var ie     = (appVer.indexOf('msie') != -1);

	var opera  = (agt.indexOf('opera') != -1);

    var mozilla = ((agt.indexOf('mozilla')!=-1) && (agt.indexOf('opera')==-1)
					&& (agt.indexOf('spoofer')==-1) && (agt.indexOf('compatible') == -1)
	                && (agt.indexOf('webtv')==-1) && (agt.indexOf('hotjava')==-1));

	var ns4     = (mozilla && (verInt == 4));

        if (ie && !opera) {

            styleSheet = document.styleSheets["pageStyle"];


            styleSheet.addRule ("b", "font-size: x-small");
            styleSheet.addRule ("span", "font-size: x-small");
            styleSheet.addRule (".postBody", "font-size: x-small");

        } else if ( mozilla && !ns4 ) {
		

            styleSheet = document.styleSheets[0];

            styleSheet.insertRule('b { font-size: small; }',styleSheet.cssRules.length);
            styleSheet.insertRule('span { font-size: small; }',styleSheet.cssRules.length);
            styleSheet.insertRule('.postBody { font-size: small; }',styleSheet.cssRules.length);

        }






var clean=1;
var pageName;
var imageName;

if (document.images) {

  newsovr 			= new Image(113,24); newsovr.src = "/shared/wow-com/images/menu/mainmenu/news-header-on.gif";
  newsoff 			= new Image(113,24); newsoff.src = "/shared/wow-com/images/menu/mainmenu/news-header.gif";

  infoovr 		= new Image(113,24); infoovr.src = "/shared/wow-com/images/menu/mainmenu/info-header-on.gif";
  infooff 		= new Image(113,24); infooff.src = "/shared/wow-com/images/menu/mainmenu/info-header.gif";

  forumsovr 		= new Image(113,24); forumsovr.src = "/shared/wow-com/images/menu/mainmenu/forums-header-on.gif";
  forumsoff 		= new Image(113,24); forumsoff.src = "/shared/wow-com/images/menu/mainmenu/forums-header.gif";

  linksovr 	= new Image(113,24); linksovr.src = "/shared/wow-com/images/menu/mainmenu/links-header-on.gif";
  linksoff 	= new Image(113,24); linksoff.src = "/shared/wow-com/images/menu/mainmenu/links-header.gif";

  supportovr 		= new Image(113,24); supportovr.src = "/shared/wow-com/images/menu/mainmenu/support-header-on.gif";
  supportoff 		= new Image(113,24); supportoff.src = "/shared/wow-com/images/menu/mainmenu/support-header.gif";

  accountovr 		= new Image(113,24); accountovr.src = "/shared/wow-com/images/menu/mainmenu/account-header-on.gif";
  accountoff 		= new Image(113,24); accountoff.src = "/shared/wow-com/images/menu/mainmenu/account-header.gif";  
  
  

  news_iconovr 			= new Image(41,24); news_iconovr.src = "/shared/wow-com/images/menu/mainmenu/news-icon-on.gif";
  news_iconoff 			= new Image(41,24); news_iconoff.src = "/shared/wow-com/images/menu/mainmenu/news-icon-off.gif";

  info_iconovr 			= new Image(41,24); info_iconovr.src = "/shared/wow-com/images/menu/mainmenu/info-icon-on.gif";
  info_iconoff 			= new Image(41,24); info_iconoff.src = "/shared/wow-com/images/menu/mainmenu/info-icon-off.gif";

  forums_iconovr 		= new Image(41,24); forums_iconovr.src = "/shared/wow-com/images/menu/mainmenu/forums-icon-on.gif";
  forums_iconoff 		= new Image(41,24); forums_iconoff.src = "/shared/wow-com/images/menu/mainmenu/forums-icon-off.gif";

  links_iconovr 	= new Image(41,24); links_iconovr.src = "/shared/wow-com/images/menu/mainmenu/links-icon-on.gif";
  links_iconoff 	= new Image(41,24); links_iconoff.src = "/shared/wow-com/images/menu/mainmenu/links-icon-off.gif";

  support_iconovr 		= new Image(41,24); support_iconovr.src = "/shared/wow-com/images/menu/mainmenu/support-icon-on.gif";
  support_iconoff 		= new Image(41,24); support_iconoff.src = "/shared/wow-com/images/menu/mainmenu/support-icon-off.gif"; 

  account_iconovr 		= new Image(41,24); account_iconovr.src = "/shared/wow-com/images/menu/mainmenu/account-icon-on.gif";
  account_iconoff 		= new Image(41,24); account_iconoff.src = "/shared/wow-com/images/menu/mainmenu/account-icon-off.gif"; 

}



function ovrImg( imageName ) {
  if ( document.images ) {
    document[ imageName ].src = eval(imageName + "ovr.src");
  }
}

function offImg( imageName ) {
  if ( document.images ) {
    document[ imageName ].src = eval(imageName + "off.src");
  }
}




window.name= "mainPage";


//Show layer//
function showLayer(layerName){

	obj = document.getElementById(layerName);
	obj.style.visibility="visible";

}

//Hide layer//
function hideLayer(layerName){

	obj = document.getElementById(layerName);
	obj.style.visibility="hidden";

}

function toggleComplete(showThis) {
	if (document.getElementById(showThis).style.display == "none") {
		document.getElementById(showThis).style.display = "inline"
		document.getElementById(showThis).style.visibility = "visible";
	} else {
		document.getElementById(showThis).style.display = "none"
		document.getElementById(showThis).style.visibility = "hidden";
	}
}

function showComplete(showThis) {
	document.getElementById(showThis).style.display = "inline";
	document.getElementById(showThis).style.visibility = "visible";
}

function hideComplete(showThis) {
	document.getElementById(showThis).style.display = "none";
	document.getElementById(showThis).style.visibility = "hidden";
}

function showPic (whichpic, num) {

	var placeholder = whichpic;
	placeholder2 = placeholder;
	placeholder = placeholder + 1;

	for (var i = 1; i <= num; i++) {
		placeholder = placeholder2 + i;
		document.getElementById(placeholder).src = document.getElementById(placeholder).name;
	}
	return true;
}

function toggleNews(showThis, num) {
	if (document.getElementById(showThis).style.display == "none") {
		document.getElementById(showThis).style.display = "inline"
		document.getElementById(showThis).style.visibility = "visible";
		showPic(showThis, num);
	} else {
		document.getElementById(showThis).style.display = "none"
		document.getElementById(showThis).style.visibility = "hidden";
	}
}

var	menuOverCurrent = "gameInfoIntroduction";
var	menuOverCurrentText = "gameInfoIntroductionText";

function showMe(showThis) {

	hideMenu();
	document.getElementById(showThis).style.visibility = "visible";
	menuOverCurrent = showThis;
	menuOverCurrentText = showThis + "Text";
	keepRollOver(menuOverCurrentText);
	document.getElementById('mouseTrapMenu').style.visibility = "visible";
}
	
function hideMe(hideThis) {
	document.getElementById(hideThis).style.visibility = "hidden";
}

/*
function hideMenu() {
	document.getElementById(menuOverCurrent).style.visibility = "hidden";
	document.getElementById(menuOverCurrentText).style.backgroundColor = "";
	document.getElementById(menuOverCurrentText).className = "menuLeftOff";
}
*/

function keepRollOver(theParent) {
	document.getElementById(theParent).style.backgroundColor = "0B2237";
	document.getElementById(theParent).className = "menuLeftOver";
}

function getexpirydate(nodays){
	var UTCstring;
	Today = new Date();
	nomilli=Date.parse(Today);
	Today.setTime(nomilli+nodays*24*60*60*1000);
	UTCstring = Today.toUTCString();
	return UTCstring;
}

function getcookie2(cookiename) {
	 var cookiestring=""+document.cookie;
	 var index1=cookiestring.indexOf(cookiename);
	 if (index1==-1 || cookiename=="") return ""; 
	 var index2=cookiestring.indexOf(';',index1);
	 if (index2==-1) index2=cookiestring.length; 
	 return unescape(cookiestring.substring(index1+cookiename.length+1,index2));
}
function setcookie(name,value){
	cookiestring=name+"="+escape(value)+";EXPIRES="+ getexpirydate(365)+";PATH=/";
	document.cookie=cookiestring;
}

var cookieArray;
var tempString;
if(!(tempString = getcookie2("menuCookie"))){
	setcookie('menuCookie', '0 0 1 1 1 0 1 1');
	cookieArray = [0, 0, 1, 1, 1, 0, 1, 1];
} else {
	cookieArray = tempString.split(" ");
}


function showTheAccount() {

	if (showAccount == 0) {
		document.getElementById('menuAccount').style.visibility = "visible";
		document.getElementById('menuAccount').style.display = "inline";		
		showAccount = 1;
	} else {
		document.getElementById('menuAccount').style.visibility = "hidden";
		document.getElementById('menuAccount').style.display = "none";		
		showAccount = 0;
	}

}

function hideText(thisText) {
	document.getElementById(thisText).style.visibility = "hidden";
	document.getElementById(thisText).style.display = "none";	
}

function popUp (url, width, height, name) {


		widthHeight = "width=" + width + ",height=" + height;

		winFeatures = "width=" + width + ",height=" + height + ",menubar=no,resizable=no,scrollbars=yes,status=no,toolbar=no,location=no"


			spawn = window.open(url,name,winFeatures);


}

   function PageQuery(q) {
        if(q.length > 1)
            this.q = q.substring(1, q.length);
        else
            this.q = null;
        this.keyValuePairs = new Array();
        if(q) {
            for(var i=0; i < this.q.split("&").length; i++) {
                this.keyValuePairs[i] = this.q.split("&")[i];
            }
        }
        this.getKeyValuePairs = function() { return this.keyValuePairs; }
        this.getValue = function(s) {
            for(var j=0; j < this.keyValuePairs.length; j++) {
                if(this.keyValuePairs[j].split("=")[0] == s)
                    return this.keyValuePairs[j].split("=")[1];
            }
            return false;
        }

        this.getParameters = function() {
            var a = new Array(this.getLength());
            for(var j=0; j < this.keyValuePairs.length; j++) {
                a[j] = this.keyValuePairs[j].split("=")[0];
            }
            return a;
        }
        this.getLength = function() { return this.keyValuePairs.length; }
   }

    function queryString(key, defaultValue){
        var page = new PageQuery(window.location.search);
        var queryValue = page.getValue(key);
        if (queryValue)
            return unescape(queryValue);
        else
            return defaultValue;
    }

    function setSelectIndexToValue(selectObject, optionValue) {
        if ((selectObject != "") && (optionValue != "") && (selectObject.selectedIndex > -1) && (selectObject[selectObject.selectedIndex].value != optionValue)) {
            var newIndex = 0;
            for (var i = 0; i < selectObject.length; i++) {
                if (selectObject[i].value == optionValue) {
                    newIndex = i;
                    break;
                }
            }
            selectObject.selectedIndex = newIndex;
        }
     }

    function appendUrlParam(source, paramName, paramValue) {
        var result = "";
        if (source != "")
            result = source + '&';
        result = result + paramName + "=" + escape(paramValue);
        return result;
    }

    function insertUrlParam(source, paramName, paramValue) {
        var tempUrl = "";
        var anchorArray = source.split("#");
        var queryArray = anchorArray[0].split("?");
        tempUrl = queryArray[0] + "?";
        if (queryArray.length > 1)
           tempUrl = tempUrl + queryArray[1] + "&";
        tempUrl = tempUrl + paramName + "=" + escape(paramValue);
        if (anchorArray.length > 1)
           tempUrl = tempUrl + "#" + anchorArray[1];
        return tempUrl;
    }






