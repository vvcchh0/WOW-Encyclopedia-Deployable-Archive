function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}
function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

function updateCookie () {
    createCookie("toplist_conf", document.spells.layoutType + "," + document.spells.pageLength + "," + document.spells.numOfTables);
}

//read cookie
var topList_conf = readCookie("toplist_conf"); 
var topList_conf_vars = new Array("wide",20,1);
if (topList_conf) { topList_conf_vars = topList_conf.split(","); }

if (!Array.prototype.push) { 
    Array.prototype.push = function() { 
        for(var i = 0; i < arguments.length; i++) { 
            this[this.length] = arguments[i];
        }
        return this.length;
    }
}

var dataDir = "/toplist/data/" + lang;
var topListLocalDataRoutes = {};

var today = new Date(2008, 4, 12, 21, 0, 44);
var latestServerQuery = "undefined";
var file1 = file2 = file3 = file4 = file5 = file6 = file7 = latestQuery = dataMissing = errorMsg = "";
var pos = avgPos = avgCount = suggestTimeout = 0;
var daysCalculated = false;
var daysArr = suggestions = new Array();
months = new Array("January","February","March","April","May","June","July","August","September","October","November","December");

var THROTTLE_PERIOD = 1250;
var DAYSDELAY = 2;
var spellcreateNameArray = new Array();
var spellcreateNumberArray = new Array();
var spellcreateIdArray = new Array();

var killedbyNameArray = new Array();
var killedbyNumberArray = new Array();
var killedbyIdArray = new Array();

var auctionsoldNameArray = new Array();
var auctionsoldNumberArray = new Array();
var auctionsoldIdArray = new Array();

var gameobjlootNameArray = new Array();
var gameobjlootNumberArray = new Array();
var gameobjlootIdArray = new Array();

var unitlootNameArray = new Array();
var unitlootNumberArray = new Array();
var unitlootIdArray = new Array();

var questcompleteNameArray = new Array();
var questcompleteNumberArray = new Array();
var questcompleteIdArray = new Array();

    function createXMLHttpRequest() {
        try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
        try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        alert("XMLHttpRequest not supported");
        return null;
    }

    function preLoadChecker (feed, pos) {
        var id = feed.substr(feed.length-11, 8); //must be format xxxxx_12022004.js, must be 8 digits
        if(document.spells.data[id] || dataMissing.indexOf(id) != -1) {
            removeTable(pos); 
            if(dataMissing.indexOf(id) != -1) { injectTable(id, pos);} else { initTableContent(id, pos); }
        } else {
            ajaxCall(feed, pos);
        }     
    }

    function ajaxCall (feed, pos) {
        var id = feed.substr(feed.length-11, 8);
        var topListDataRequest = dataDir + "/" + feed;
        var topListDataRoute = topListLocalDataRoutes[topListDataRequest];
        if (!topListDataRoute) {
            removeTable(pos); dataMissing += id; injectTable(id, pos);
            return;
        }
        var xhr = createXMLHttpRequest();
        
		xhr.onreadystatechange = function() {
            if (xhr.readyState==4) { // Request is finished
                if (xhr.status==200) {
                    try {
                        eval(xhr.responseText);
                      } catch (e) {
                        $("error").innerHTML = "An error has occured during loading the data. [eval]";
                      }
                    removeTable(pos);
                    initTableContent(id, pos);
                } else if (xhr.status == 404) { removeTable(pos); dataMissing += id; injectTable(id, pos);}
                else { alert("Message returned, but with error status. (" + xhr.status +")");  }
            } 
        };
        xhr.open("GET", topListDataRoute, true);
        if( xhr.overrideMimeType ) { xhr.overrideMimeType( 'text/plain' ); }
        xhr.send(null);
    }

    document.spells = new function() {
        this.data = new Array();
    
        this.getData = function(id) {
            return this.data[id];
        }
	    
        this.allNames = new Array();
        
        this.pageLength = parseInt(topList_conf_vars[1]);
        this.totalPages = this.searchMatches = 0;
        this.numOfTables = topList_conf_vars[2];
        this.activeTables = 3;
        this.isActivity = false;
        this.searchPattern = this.searchInfo = "";
        this.layoutType = topList_conf_vars[0];
        this.category = category;
        this.browseGlobally = true;
    	
        this.getAllNames = function () { 
            var result = 0; 
            for (var key in this.allNames) { 
                if (typeof(this.allNames[key]) == "string") { 
                    result ++; 
                } 
            } 
            return result; 
        }

        this.sortData = function(id, field, desc) {
			this.data[id].sort(function(a, b) {
                var result = 0;
                if (field == 0 || field == 3) { // numsort
                    if (desc && desc == true) {
                        result = a[field] - b[field];
                    } else {
                        result = b[field] - a[field];
                    }
                } else { // stringsort
                    var temp = new Array(a[field], b[field]);
                    temp.sort();
                    if (temp[0] == a[field]) {
                        result = -1;
                    } else {
                        result = 1;
                    }
                    if (desc && desc == true) {
                        result *= -1;
                    }
                }
                return result;
            });
        }
      
       this.importData = function(id, numArr, nameArr, idArr) {// adjust for dynamic loading 
            var itemId = 0;
            if (!this.data[id]) { this.data[id] = new Array(); } 
            if (!this.allNames) { this.allNames = new Array(); }
            for (var x = 0; x < numArr.length ; x++) { 
                this.data[id][this.data[id].length] = new Array(numArr[x], nameArr[x], idArr[x], x);
                this.allNames[nameArr[x]] = ""; 
            } 
            return true; 
        }
    }
				
    function initTableContent(id, pos) {
        if (document.spells.category == "killedby") { 
            if (!document.spells.data[id]) document.spells.importData(id, killedbyNumberArray[id], killedbyNameArray[id], killedbyIdArray[id]);
        }
        else if (document.spells.category == "spellcreate") { 
            if (!document.spells.data[id]) document.spells.importData(id, spellcreateNumberArray[id], spellcreateNameArray[id], spellcreateIdArray[id]);
        }
        else if (document.spells.category == "auctionsold") { 
            if (!document.spells.data[id]) document.spells.importData(id, auctionsoldNumberArray[id], auctionsoldNameArray[id], auctionsoldIdArray[id]);
        }
        else if (document.spells.category == "gameobjloot") { 
            if (!document.spells.data[id]) document.spells.importData(id, gameobjlootNumberArray[id], gameobjlootNameArray[id], gameobjlootIdArray[id]);
        }
        else if (document.spells.category == "unitloot") { 
            if (!document.spells.data[id]) document.spells.importData(id, unitlootNumberArray[id], unitlootNameArray[id], unitlootIdArray[id]);
        }
        else if (document.spells.category == "questcomplete") { 
            if (!document.spells.data[id]) document.spells.importData(id, questcompleteNumberArray[id], questcompleteNameArray[id], questcompleteIdArray[id]);
        }
        injectTable(id, pos);
    }

    function injectTable(actualId, position){
        var theTable = $("stats");
		var tbody = theTable.getElementsByTagName('tbody')[0];
        var tr = tbody.firstChild;
        var cells = tr.childNodes;
		var elem;
		var nextElem;
		
        var cell = document.createElement('td');
        cell.id = position;
        cell.setAttribute("valign", "top");
        cell.innerHTML += drawTable(actualId, position);

        if (cells.length != 0) {
			for(var g = 0; g < cells.length; g++) {
                elem = cells[g];
				nextElem = cells[g + 1];
				if (elem.nodeName == "TD") {
					if (position > elem.id && nextElem == null) {
	                    tr.appendChild(cell);
	                    break;
	                }        
	                else if (position < elem.id ) {            
	                    tr.insertBefore(cell, elem);
	                    break;
	                }
				}
            }
        } else { tr.appendChild(cell); } 

        renderTableData(actualId, null, null, null, position); // render actual tbody content (build DOM), all but headers
        
        document.spells.activeTables = tr.childNodes.length - 1;
        if(!is_opera) { 
            $(actualId + "_" + position + "_div").setOpacity(0); 
            new Effect.Appear(actualId + "_" + position + "_div", {duration: 0.6});
        }
    }

    // renders the table content when browsing/changing pagelength, searching. also generates the navigation
    function renderTableData(id, pageNum, field, sortType, position) { 

        if (dataMissing.indexOf(id) == -1 && document.spells.data[id].length > 250) { //if data avail
    		var arr = document.spells.data[id]; 
            var tbody = document.createElement("tbody"); 
            tbody.id = id + "_" + position;
            var totalPages = Math.floor(arr.length/document.spells.pageLength);
            document.spells.totalPages = totalPages;
            
            if (document.spells.searchPattern && pageNum == null && !sortType) {
                for (var c = 0; c < arr.length; c++) {
                    if (arr[c][1].toLowerCase().indexOf(document.spells.searchPattern.toLowerCase()) != -1) { pageNum = Math.floor((c/document.spells.pageLength)); break; }
                }
            }
    
            if (!pageNum) var pageNum = 0;        
    
            var startPos = pageNum * document.spells.pageLength;
            var endPos = parseInt(startPos + document.spells.pageLength);            
    
            var pager = getPager(id, pageNum, totalPages, position);
            
            tbody.appendChild(pager);         
    
            var headers = document.createElement("tr");
                headers.className = "headers";
    
            var headerPos = document.createElement("td"); 
            var posSortLink = document.createElement("A");
                posSortLink.innerHTML = labelHeaderRank;
                posSortLink.className = "pos";
                if (field == 3) {
                    posSortLink.className += " sort" + sortType;
                } else if (field == null) { posSortLink.className += " sortasc"; } 
                posSortLink.onclick = function () { sortContent(this, 3); }
                headerPos.appendChild(posSortLink);
                
            var headerName = document.createElement("td"); 
            var itemSortLink = document.createElement("A");
                itemSortLink.className = "item";
                switch (category) {
                    case "killedby": itemSortLink.innerHTML = labelHeaderCreature; itemSortLink.className += " creature"; break;
                    case "questcomplete": itemSortLink.innerHTML = labelHeaderQuests; itemSortLink.className += " quests"; break;                
                    default: itemSortLink.innerHTML = labelHeaderItem; break;
                }
                if(field == 1) {
                    itemSortLink.className += " sort" + sortType;
                }
                itemSortLink.onclick = function () { sortContent(this, 1); }
                headerName.appendChild(itemSortLink);
    
                
            var headerNum = document.createElement("td"); 
            var numSortLink = document.createElement("A");
                numSortLink.innerHTML = (document.spells.category != "killedby" ? labelHeaderCount : labelPlayersKilled);
                numSortLink.className = "count";
                if(field == 0) {
                    numSortLink.className += " sort" + sortType;
                }
                numSortLink.onclick = function () { sortContent(this, 0); }
                headerNum.appendChild(numSortLink);
    
                headers.appendChild(headerPos);
                headers.appendChild(headerName);            
                headers.appendChild(headerNum);
                
                tbody.appendChild(headers);
    
                if (document.spells.pageLength > 20) var counter = 0;
                
            for (var x = startPos; x < endPos; x++) { 
    
                if (document.spells.pageLength > 20) counter++;
                
                var nrAppendix = "";
                var exactMatchFound = (arr[x][1].toLowerCase() == document.spells.searchPattern.toLowerCase()) ? true : false; //sets matchFound to true/false
    
                var tr = document.createElement("tr"); 
                tr.className = (x%2 != 0 ? "even" : "odd"); 
                if (document.spells.pageLength > 20 && counter%20 == 0) tr.className += " splitter";
                if (document.spells.searchPattern != "") { tr.className += (exactMatchFound) ? " match": ""; }
                tr.id = arr[x][2];
    
                var pos = document.createElement("td"); 
                    pos.className = "pos";
               
                if (lang != "de" && lang != "fr") {
                    var lastDigit = (arr[x][3] + 1).toString();
                    lastDigit = lastDigit.substr((lastDigit.length - 1), 1);
                    switch (lastDigit) {
                        case "1": nrAppendix = numberFirstSuffix; break;
                        case "2": nrAppendix = numberSecondSuffix; break;            
                        case "3": nrAppendix = numberThirdSuffix; break;
                        default: nrAppendix = numberDefaultSuffix; break;
                    }
                    if (arr[x][3] == 11 || arr[x][3] == 12 || arr[x][3] == 13) nrAppendix = numberDefaultSuffix;
                } else { 
                    if (lang == "fr" && arr[x][3] == 1) { nrAppendix = numberFirstSuffix; }
                    else { nrAppendix = numberDefaultSuffix; }
                }
    
                var posAppendix = document.createElement((lang != "de" ? "sup" : "span"));
                posAppendix.appendChild(document.createTextNode(nrAppendix))
                pos.appendChild(document.createTextNode(arr[x][3] + 1)); 
                pos.appendChild(posAppendix); 
    
                if (exactMatchFound) { avgPos += x + 1; }
            
                var name = document.createElement("td"); 
                name.setAttribute("itemfullname", arr[x][1].toString())
    
                var itemName = "";
                    if (arr[x][1].length >= 21 && document.spells.layoutType != "wide") {
                        itemName = arr[x][1].substr(0, (arr[x][1].length >= 21) ? 18 : arr[x][1].length); if(arr[x][1].length >= 21) itemName += "...";
                        name.onmouseover = function () { ddrivetip(this.getAttribute("itemfullname")); } 
                        name.onmouseout = function () { hideddrivetip(); } 
                    } 
                    else if (arr[x][1].length > 35 && document.spells.layoutType == "wide") {
                        itemName = arr[x][1].substr(0, 33); itemName += "...";
                        name.onmouseover = function () { ddrivetip(this.getAttribute("itemfullname")); } 
                        name.onmouseout = function () { hideddrivetip(); } 
                    } else { itemName = arr[x][1]; }
                if(exactMatchFound) { 
                    name.onmouseover = function () { ddrivetip(document.spells.searchInfo); }
                    name.onmouseout = function () { hideddrivetip(); }
                } 
                name.appendChild(document.createTextNode(itemName)); 
                name.className = "item";
                name.onclick = function () { $('gievItem').value = this.getAttribute("itemfullname"); }
                if (exactMatchFound) { document.spells.searchMatches++; }
    
                var num = document.createElement("td");

                num.appendChild(document.createTextNode((arr[x][0] != null) ? formatInteger(arr[x][0]) : "n/a"));

                if (exactMatchFound) avgCount += arr[x][0];
            
                tr.appendChild(pos); 
                tr.appendChild(name); 
                tr.appendChild(num); 
                
                tbody.appendChild(tr); 
            } 
    
            tbody.appendChild(pager.cloneNode(true));
            
            var oldBody = $(id + "_" + position + "_table").getElementsByTagName('tbody')[0]; 
            oldBody.parentNode.replaceChild(tbody, oldBody); 
        } else { renderEmptyTable(id, position); }
    }

    function renderEmptyTable(id, position) {
        var tbody = document.createElement("tbody"); 
            tbody.className = "emptyTable"; 
        
        var infoSpan = document.createElement("span");
            infoSpan.className = "noData";
            infoSpan.innerHTML = (dataMissing.indexOf(id) != -1) ? "Historical ranking data for this date has not been recovered." : labelNoDataAvail;

        var tr1 = document.createElement("tr");
            tr1.className = "navi";
        
        var td1 = document.createElement("td");
            td1.colSpan = 3;

            tr1.appendChild(td1);
            tbody.appendChild(tr1);

            for (var x = 0; x < document.spells.pageLength; x++) {
                var span = document.createElement("span");
                    span.innerHTML = "&nbsp;";
                var tr = document.createElement("tr");
                var td = document.createElement("td");
                    td.colSpan = 3;
                    (x == 0 || (document.spells.pageLength > 20 && x == document.spells.pageLength - 1)) ? td.appendChild(infoSpan.cloneNode(true)): td.appendChild(span);
                tr.appendChild(td);
                tbody.appendChild(tr); 
            }

        var tr2 = document.createElement("tr");
            tr2.className = "emptyTableHeaders";
        var td2 = document.createElement("td");
            td2.colSpan = 3;

            tr2.appendChild(td2);
            tbody.appendChild(tr2);
        var oldBody = $(id + "_" + position + "_table").getElementsByTagName('tbody')[0]; 
            oldBody.parentNode.replaceChild(tbody, oldBody);
    }

	//removes a TD containing a table
    function removeTable (position, type) {
        var theTable = $("stats");
		var tbody = theTable.getElementsByTagName('tbody')[0];
        var tr = tbody.firstChild;
        var cells = tr.childNodes;
        var elem;

        for (var x = 0; x < cells.length; x++) {
            elem = cells[x];
            if (elem.nodeType == 1 && elem.id == position) { 
                tr.removeChild(elem)
            }
        }
        document.spells.activeTables = tr.childNodes.length - 1;
    }
	
    // sorts the table content
	function sortContent(header, field) {
        var tbody = header.parentNode.parentNode.parentNode;
        var table = $(tbody.id + "_table");
        var id = tbody.id.substr(0, 8);
        var position = tbody.id.substr(9,1);
        var sortType = "";
        
        if (field == 3) { sortType = (table.getAttribute("posSortType") == "desc" || table.getAttribute("posSortType") == "") ? "asc" : "desc"; table.setAttribute("posSortType", sortType); } 
        else if (field == 0) { sortType = (table.getAttribute("numSortType") == "asc" || table.getAttribute("numSortType") == "") ? "desc" : "asc"; table.setAttribute("numSortType", sortType); } 
        else if (field == 1) { 
            sortType = (table.getAttribute("itemSortType") == "asc" || table.getAttribute("itemSortType") == "") ? "desc" : "asc"; 
            table.setAttribute("itemSortType", sortType); 
            document.spells.sortData(id, field, (sortType == "desc") ? true : false);
        } 
        if (field != 1) document.spells.sortData(id, field, (sortType == "asc") ? true : false);
        renderTableData(id, null, field, sortType, position);
    }

    // called from within renderTableData. generates the actual page numbers
    function getPager (id, pageNum, totalPages, position) {
        var pager = document.createElement("tr");
       	pager.className = "navigation";
        
        var pagerCnt = document.createElement("td"); 
			pagerCnt.colSpan = "3";
		var prevDiv = document.createElement("div");
			prevDiv.className = "pagerPrevDiv";
        if (pageNum - 1 >= 0) {
            var prevLink = document.createElement("a");
            if (document.spells.browseGlobally) {  
                prevLink.setAttribute("href", "javascript:redrawTables('pageAll'," + (pageNum - 1) + ")");
            } else { 
                prevLink.setAttribute("href", 'javascript:renderTableData("' + id + '",' + (pageNum - 1) + ', null, null, ' + position + ')');
            }    
            prevLink.setAttribute("title", labelJumpToPrevPage);
            prevLink.className = "prev";
			prevDiv.appendChild(prevLink);
        } else { prevDiv.className += " prevOff"; }           
            var pCounter = nCounter = 0;
            if (document.spells.layoutType == "wide") {
                if (document.spells.pageLength == 20) pCounter = nCounter = 2;
                else if (document.spells.pageLength == 50) pCounter = nCounter = 3;
                else pCounter = nCounter = 3;
            } else { 
                if (document.spells.pageLength == 20) pCounter = nCounter = 1;
                else if (document.spells.pageLength == 50) pCounter = nCounter = 2;
                else pCounter = nCounter = 3;
            }
            var navigationDiv = document.createElement("div");
				navigationDiv.className = "pagerNavigationDiv"
			
			var pageSeperator = "<span>&middot;</span>"
            var output2 = "";            

	            //shows "50 ..."
				if (document.spells.browseGlobally) {
	                if (pageNum > 0 + nCounter) { output2 += "<a title=\" "+ labelJumpToFirstPage + " \" href=\"javascript:redrawTables('pageAll',0)\">1</a>" + pageSeperator; }
	            } else {
	                if (pageNum > 0 + nCounter) { output2 += "<a title=\" "+ labelJumpToFirstPage + " \" href=\"javascript:renderTableData('" +  id + "',0, null, null, " + position + ")\">1</a>" + pageSeperator; } 
	            }
	            
                if ((pageNum - (pCounter - 1)) > 10 && totalPages > 10) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 9 + ")\">10</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" + id + "'," + 9 + ", null, null, " + position + ")\">10</a>" + pageSeperator; }    
                if ((pageNum - (pCounter - 1)) > 20 && totalPages > 20) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 19 + ")\">20</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" + id + "'," + 19 + ", null, null, " + position + ")\">20</a>" + pageSeperator; }                    
                if ((pageNum - (pCounter - 1)) > 30 && totalPages > 30) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 29 + ")\">30</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" + id + "'," + 29 + ", null, null, " + position + ")\">30</a>" + pageSeperator; }    
                if ((pageNum - (pCounter - 1)) > 40 && totalPages > 40) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 39 + ")\">40</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" + id + "'," + 39 + ", null, null, " + position + ")\">40</a>" + pageSeperator; }    
                
                // displays previous <pcounter> pages
	            for (var g = (pageNum - pCounter); g < pageNum; g++) {
	                if (document.spells.browseGlobally) {
	                    if (g < pageNum && g + 1 > 0) { 
	                        output2 += "<a href=\"javascript:redrawTables('pageAll'," + g + ")\">" +(g+1)+ "</a>" + pageSeperator;
	                    }
	                } else {
	                    if (g < pageNum && g + 1 > 0) { 
	                        output2 += "<a href=\"javascript:renderTableData('" +  id + "'," + g + ", null, null," + position + ")\">" +(g+1)+ "</a>" + pageSeperator;
	                    }
	                }
	            }
	            
	            //displays current page
	            output2 += '<span class="currPage">' + (pageNum + 1) + '</span>'; if (pageNum + 1 != totalPages) output2 += pageSeperator
    
	            // displays next <ncounter> pages
	            for (var f = pageNum + 1; f <= pageNum + nCounter; f++) {
	                if (document.spells.browseGlobally) {
	                    if (f < totalPages) { output2 += "<a title=\"Browse to next page\" href=\"javascript:redrawTables('pageAll'," + f + ")\">" +(f+1)+ "</a>"; if (f + 1 != totalPages) output2 += pageSeperator;
	                    } /* else { output2 += "<li>&nbsp;</li>"; }*/
	                } else { 
	                    if (f < totalPages) { output2 += "<a title=\"Browse to next page\" href=\"javascript:renderTableData('" +  id + "'," + f + ", null, null, " + position + ")\">" +(f+1)+ "</a>" + pageSeperator; 
	                    } /*else { output2 += "<li>&nbsp;</li>"; }  */              
	                }                
	            }

                if ((pageNum + (pCounter + 1)) < 10 && totalPages > 10) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 9 + ")\">10</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" +  id + "'," + 9 + ", null, null, " + position + ")\">10</a>" + pageSeperator; }   
                if ((pageNum + (pCounter + 1)) < 20 && totalPages > 20) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 19 + ")\">20</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" +  id + "'," + 19 + ", null, null, " + position + ")\">20</a>" + pageSeperator; }                    
                if ((pageNum + (pCounter + 1)) < 30 && totalPages > 30) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 29 + ")\">30</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" +  id + "'," + 29 + ", null, null, " + position + ")\">30</a>" + pageSeperator; }                    
                if ((pageNum + (pCounter + 1)) < 40 && totalPages > 40) if (document.spells.browseGlobally) { output2 += "<a href=\"javascript:redrawTables('pageAll'," + 39 + ")\">40</a>" + pageSeperator; } else { output2 += "<a href=\"javascript:renderTableData('" +  id + "'," + 39 + ", null, null, " + position + ")\">40</a>" + pageSeperator; }                    
                
	            if (document.spells.browseGlobally) { 
	                if (pageNum < (totalPages - nCounter)-1) { output2 += "<a title=\" "+ labelJumpToLastPage + " \" href=\"javascript:redrawTables('pageAll'," + (totalPages-1) + ")\">" +(totalPages)+ "</a>"; }
	            } else {
	                if (pageNum < (totalPages - nCounter)-1) { output2 += "<a title=\" "+ labelJumpToLastPage + " \" href=\"javascript:renderTableData('" +  id + "'," + (totalPages-1) + ", null, null, " + position + ")\">" +(totalPages)+ "</a>"; }
	            }

            navigationDiv.innerHTML = output2; 

			var nextDiv = document.createElement("div");
				nextDiv.className = "pagerNextDiv";
            if (pageNum + 1 < totalPages) {
                var nextLink = document.createElement("a");
                if (document.spells.browseGlobally) {  
                    nextLink.setAttribute("href", "javascript:redrawTables('pageAll'," + (pageNum + 1) + ")");
                } else { 
                    nextLink.setAttribute("href", 'javascript:renderTableData("' + id + '",' + (pageNum + 1) + ', null, null, ' + position + ')');
                }
                nextLink.setAttribute("title", labelJumpToNextPage);
                nextLink.className = "next";
				nextDiv.appendChild(nextLink);
            } else { nextDiv.className += " nextOff"; }

			pagerCnt.appendChild(prevDiv);
            pagerCnt.appendChild(navigationDiv);
			pagerCnt.appendChild(nextDiv);
			pager.appendChild(pagerCnt);

        return pager;
    }
        
    function timeoutEvent (callerFunction) {
        suggestTimeout = setTimeout(callerFunction, 666);
    }
    function clearTimeoutEvent () {
        if (suggestTimeout) { clearTimeout(suggestTimeout); timeout = null; }
    }    
    function hideBox (elem) {
    	if($(elem)) {
            if (!is_opera) { Effect.Fade(elem, {duration: 0.5}); } else { $(elem).style.display = "none"; }
        }
    }
    function showTableDates(tableId, position) {
        if(tableId.toString().length == 7) tableId = "0" + tableId;
        var table = $(tableId + "_" + position + "_tableDates");
        if(table) { 
            table.className = "tableDate-active"; 
            table.lastChild.firstChild.style.display = "block";
        }
    }
    function hideTablesDatesBox (tableId, position) {
        if(tableId.toString().length == 7) tableId = "0" + tableId;
        var table = $(tableId + "_" + position + "_tableDates");
        if (table) { table.className = "tableDate";
        	if(table.lastChild) {
                table.lastChild.firstChild.style.display = "none";
            }
        }
    }

    function redrawTables(type, pageNumber) {
        var theTable = $("stats");
		var tbody = theTable.getElementsByTagName('tbody')[0];
		var tr = tbody.firstChild;
        var cellNodes = tr.childNodes;
        var divNodes = cellNode = divId = "";

        if(type == "tableViewChanged") {
            if (document.spells.numOfTables > 1) { 
                document.getElementsByTagName("body")[0].className = "narrow";
                document.spells.layoutType = "narrow";
                $("browseAll").style.display = "inline";
            } else { 
                document.getElementsByTagName("body")[0].className = "wide"; 
                document.spells.layoutType = "wide";
                $("browseAll").style.display = "none";
            }
        }

        for (var e = 0; e < cellNodes.length; e++) {
            cellNode = cellNodes[e];
            if(cellNode.nodeName == "TD") {
				divNodes = cellNode.childNodes;
				for (var b = 0; b < divNodes.length; b++) {
                    divNode = divNodes[b];
                    if (divNode.nodeName == "DIV") {
						divId = divNode.id.substring(0, divNode.id.length - 6);	
                        if(type == "redraw" || type == "pageAll") {
                            renderTableData(divId, pageNumber, null, null, cellNode.id );
						}
                        else if(type == "categoryChange" || type == "tableViewChanged") {
							if(cellNode.id == 1) renderTableData(divId, pageNumber, null, null, cellNode.id );
                        } 
                    }
                }
            }
        }
        var tableOffsetHeight = $("stats").offsetHeight;   
        if(type == "tableViewChanged") {
    		deleteChildNodesRecursively(tr);			            
            $("stats").style.height = tableOffsetHeight + "px";
            init();
            updateCookie();
        }
    }
 
	function deleteChildNodesRecursively (parentNode) {
        var elems = parentNode.childNodes;
		for (x = (elems.length - 1); x >= 0; x--) {
			if (elems[x].nodeType == 1 && elems[x].id > document.spells.numOfTables) { parentNode.removeChild(elems[x]); }
		}    
	}

    function getNextSibling(node) { 
        var result = null; 
        for(var sibling = node; sibling != null; sibling = sibling.nextSibling){ 
            if(sibling.nodeType == 1) { 
                result = sibling; 
                break; 
            } 
        } 
        return result; 
    }
    
    function drawTable(actualId, position) {
        var output = "";
        output += "<div id=\"" + actualId + "_" + position + "_div\" class=\"box\">";
        output += "   <table cellpadding=\"0\" cellspacing=\"0\" border=\"0\">";
        output += "       <tr>";
        output += "            <td id=\"singleTable-top\" colspan=\"3\" style=\"height: 30px;\" align=\"center\"><div id='" + actualId + "_" + position + "_tableDates' class=\"tableDate\">" + generateTableDates(actualId, position) + "</div></td>";
        output += "        </tr>";
        output += "        <tr>";
        output += "            <td width=\"4\" style=\"background: url(/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Ftoplist%2Fincludes-client%2Fjs%2Flogic.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ftoplist%2Fimages%2Ftable-left.jpg&reason=external-or-uncollected-resource) repeat-y 0 0;\"><img src=\"/WOW-Encyclopedia-Deployable-Archive/toplist/images/pixel.gif\" width=\"4\" height=\"22\" border=\"0\"></td>";
        output += "            <td valign=\"top\">";
        output += "                 <table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" class=\"statsTable\" id=\"" + actualId + "_" + position + "_table\">";
        output += "                     <thead>";
        output += "                         <tr>";
        output += "                             <td class=\"position\"><img src=\"/WOW-Encyclopedia-Deployable-Archive/toplist/images/pixel.gif\" height=\"1\" width=\"43\" border=\"0\"></td>";
        output += "                             <td><img src=\"/WOW-Encyclopedia-Deployable-Archive/toplist/images/pixel.gif\" height=\"1\" width=\"135\" border=\"0\"></td>";
        output += "                             <td><img src=\"/WOW-Encyclopedia-Deployable-Archive/toplist/images/pixel.gif\" height=\"1\" width=\"62\" border=\"0\"></td>";
        output += "                         </tr>";
        output += "                     </thead>";
        output += "                     <tbody>";
        output += "                     </tbody>";
        output += "                 </table>";
        output += "            </td>";
        output += "            <td width=\"4\" style=\"background: url(/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Ftoplist%2Fincludes-client%2Fjs%2Flogic.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Ftoplist%2Fimages%2Ftable-right.jpg&reason=external-or-uncollected-resource) repeat-y 0 0;\"><img src=\"/WOW-Encyclopedia-Deployable-Archive/toplist/images/pixel.gif\" width=\"4\" height=\"22\" border=\"0\"></td>";
        output += "        </tr>";
        output += "       <tr>";
        output += "            <td id=\"singleTable-bot\" colspan=\"3\" style=\"height: 6px; background-color: #111111;\"></td>";                            
        output += "        </tr>";
        output += "    </table>"; 
        output += "</div>";
        return output;
    }

    function getDigitDate (dateObj, type) {
        var mo = dateObj.getMonth()+1;
        var day = dateObj.getDate();
        mo = (mo < 10) ? "0" + mo : mo;
        day = (day < 10) ? "0" + day : day;
        var currDate = "";
        if (!type) { currDate = day + "" + mo + "" + dateObj.getFullYear(); if (!daysCalculated) daysArr.push(currDate); }
        else { currDate = day + "/" + mo + "/" + dateObj.getFullYear(); }
        return currDate;
    }
    
    function getFormattedDate (day, month, year) {
        var tmpDate = new Date(months[month-1]+" 1, " + year);
        day = (day.charAt(0) == "0") ? day.substr(1) : day;
        tmpDate.setDate(day);
        var separator = (lang == "de") ? ". " : " "; // generates a dot after the weekdays number
        var m = (lang != "fr") ? M[tmpDate.getMonth()] : M[tmpDate.getMonth()].toLowerCase().substr(0, 3) + ".";
        var d = (lang != "fr") ? D[tmpDate.getDay()] + ", " : D[tmpDate.getDay()] + " ";
        var formattedDate = d + "" + tmpDate.getDate() + "" + separator + "" + m + " " + tmpDate.getFullYear();
        return formattedDate;
    }
    
    //takes a number and returns the number with commas at every "thousands"-position
    function formatInteger (n) {
        var tmpNum = "";
        var splitArr = new Array();
        
        var numLength = n.toString().length;
        var thousands = Math.floor(numLength / 3);
        
        for (var x = 0; x <= thousands; x++) {
            numLength = n.toString().length;
            if (numLength >= 3) {
                tmpNum = n.toString().slice(numLength-3, numLength);
                n = n.toString().substring(0, numLength-3);
                splitArr.push(tmpNum);
            } else { if (n.length != 0) { splitArr.push(n); } }
        }
        
        splitArr.reverse();
        
        var formattedNum = "";
        for (var i = 0; i < splitArr.length; i++) { 
            formattedNum += splitArr[i];  
            if (i == splitArr.length - 1) continue;
            formattedNum += numDelimiter;
        }
        return formattedNum;
    }
    
    //generates delay for searchbox input, every <THROTTLE_PERIOD>ms it generates suggestions   
    function throttleSubmission() {
        if (getSearchString() != latestQuery) {
            avgPos = 0;
            avgCount = 0;
            if ($("gievItem").value.length < 3 ) { $('searchInfo').innerHTML = labelMinimumCharactersForSearch; } else { $('searchInfo').innerHTML = ""; }
            $('searchInfo').className = "";
            document.spells.searchMatches = 0;
            document.spells.searchPattern = getSearchString();
            if($("suggestBox")) $("sbContainer").removeChild($("sbContainer").firstChild); //please make more flexible
            if (document.spells.searchPattern.length > 2 || document.spells.searchPattern == " ") { 
                displaySuggestions();
            } 
            latestQuery = getSearchString();
        }
        setTimeout('throttleSubmission();', THROTTLE_PERIOD);
    }

    function getSearchString() {
        return $("gievItem").value;
    }
    
    function displaySuggestions () {
        var suggestions = new Array();   
        var exactMatch = false;
        for (var key in document.spells.allNames) { 
            if (typeof(document.spells.allNames[key]) == "string") { 
                if (key.toLowerCase().indexOf(document.spells.searchPattern.toLowerCase()) != -1) suggestions.push(key);
                if (key.toLowerCase() == document.spells.searchPattern.toLowerCase()) { exactMatch = true; break; };
            } 
        } 
        
        suggestions.sort();
        if (exactMatch) { 
            redrawTables("redraw"); 
            document.spells.searchPattern = suggestions[0];
            var queryInfo = "<strong>" + document.spells.searchPattern + "</strong><br><br>" + labelAverageRank + "" + Math.round(avgPos/document.spells.searchMatches) + "<br>" + labelAverageCount +  "" + formatInteger(Math.round(avgCount/document.spells.searchMatches)) + " (<strong>" + document.spells.searchMatches + "</strong> " + labelMatches + ")<br>" + document.spells.getAllNames() + " " + labelItemsSearched;
            setSearchInfo(queryInfo);
        }
        else if (suggestions.length == 1) { 
            document.spells.searchPattern = suggestions[0]; 
            redrawTables("redraw"); 
            var queryInfo = "<strong>" + document.spells.searchPattern + "</strong><br><br>" + labelAverageRank + "" + Math.round(avgPos/document.spells.searchMatches) + "<br>" + labelAverageCount +  "" + formatInteger(Math.round(avgCount/document.spells.searchMatches)) + " (<strong>" + document.spells.searchMatches + "</strong> " + labelMatches + ")<br>" + document.spells.getAllNames() + " " + labelItemsSearched;
            setSearchInfo(queryInfo);
        }
        else if (suggestions.length > 1) { //display suggestBox
			var suggestBox = document.createElement("DIV");
			suggestBox.id = "suggestBox";
			$("sbContainer").appendChild(suggestBox);
			$("suggestBox").onmouseout = function () { timeoutEvent("hideBox('suggestBox')"); }
			$("suggestBox").onmouseover = function () { clearTimeoutEvent(); }			
            var maxLength = 0;
			for (var w = 0; w < suggestions.length; w++) {
				var option = document.createElement("a");
				option.appendChild(document.createTextNode(suggestions[w]));
				option.onclick = function () { $("gievItem").value = this.firstChild.nodeValue; return false; }
				option.href = "#";
				$("suggestBox").appendChild(option);
                maxLength = (suggestions[w].length > maxLength) ? suggestions[w].length : maxLength;
			}
            $("suggestBox").style.width = (maxLength < 22) ? "142px" : ((maxLength/5)*2.8+2) + "em"; 

            if (!is_opera) { $("suggestBox").setOpacity(0); new Effect.Appear("suggestBox", {duration: 0.3}); }

		} else { // display errorMsg
            $('searchInfo').className = "error";
            $('searchInfo').innerHTML = labelNoSearchResultsFound;
			if($("suggestBox")) $("sbContainer").removeChild($("suggestBox")); //please make more flexible
		}
    }
    
    function setSearchInfo(info) {
        document.spells.searchInfo = info;
        return true;
    }

    function toggleGlobalPager () {
		if (!document.spells.browseGlobally) {
        	document.spells.browseGlobally = true; 
	        redrawTables("pageAll"); 
		} else {
        	document.spells.browseGlobally = false; 
	        redrawTables("redraw"); 
		}
    }

    function initPageLengthChange (value) {
        displayProgressIndicator();
        document.spells.pageLength = parseInt(value); 
        updateCookie();
        $("stats").style.height = "1px";
        redrawTables("redraw");
        displayProgressIndicator();
    }
    
    function initLayoutChange (numDays) {
        document.spells.numOfTables = parseInt(numDays);
        redrawTables('tableViewChanged');
    }
    
    function calculateDays () { // is only run once
        var shortDate = "";
        var filename = "";
      
        for (var x = DAYSDELAY; x < DAYSDELAY + 7; x++) {
            c = today.getDate() - x;
            today.setDate(c);
            shortDate = getDigitDate(today, false);
            filename = document.spells.category + "_" + shortDate + ".js";
			switch (x) {
                case DAYSDELAY: file1 = filename;
                case DAYSDELAY + 1: file2 = filename;
                case DAYSDELAY + 2: file3 = filename;
                case DAYSDELAY + 3: file4 = filename;
				case DAYSDELAY + 4: file5 = filename;
				case DAYSDELAY + 5: file6 = filename;
				case DAYSDELAY + 6: file7 = filename;
            }
            today = new Date(2008, 4, 12, 21, 0, 44);
        }
		daysCalculated = true;
	    if (is_moz) { $("categoryVisual").setOpacity(0); window.setTimeout("Effect.Appear('categoryVisual')", 0); }
	    if (is_moz) { $("categoryHeader").setOpacity(0); window.setTimeout("Effect.Appear('categoryHeader')", 200); }
    }

	function displayProgressIndicator (delay) {
		if(!delay) var delay = 7;
		if (!document.spells.isActivity) {
			if (!is_opera) { $("progress").setOpacity(0); Effect.Appear("progress", {duration: 0.5}); }
			document.spells.isActivity = true;
		} else {
 			document.spells.isActivity = false;
			if (!is_opera) window.setTimeout("Effect.Fade('progress', {duration: 0.5})", (document.spells.activeTables * document.spells.pageLength) * delay);
		}
	}
	
    function generateTableDates (tableId, position) {
        var output = "";
        var tableIdTmp = tableId;
        if (tableId.charAt(0) == "0") tableIdTmp = tableId.substr(1, tableId.length);
        output += "<div class=\"showTableDatesButton\" onclick=\"showTableDates(" + tableIdTmp + "," + position + ");\" onmouseout=\"timeoutEvent('hideTablesDatesBox(" + tableIdTmp + "," + position + ")')\" onmouseover=\"clearTimeoutEvent()\">" + getFormattedDate(tableId.substr(0, 2), tableId.substr(2, 2), tableId.substr(4, 4)) + "</div><div style=\"position: relative; top: 6px;\"><div onmouseover=\"clearTimeoutEvent()\" onmouseout=\"timeoutEvent('hideTablesDatesBox(" + tableIdTmp + "," + position + ")')\" class=\"dateSelector\">";
        var fileName = displayDate = "";
        for (var c = 0; c < daysArr.length; c++) {
            filename = document.spells.category + "_" + daysArr[c] + ".js";
            displayDate = getFormattedDate(daysArr[c].substr(0, 2), daysArr[c].substr(2, 2), daysArr[c].substr(4, 4));            
            output += "<a onclick=\"preLoadChecker('" + filename + "'," + position + "); this.parentNode.style.visibility = 'hidden'; return false;\" href=\"#\">" + displayDate + "</a>";
        }
        output += "</div></div>";
        return output;    
    }
    
    function init () {
		displayProgressIndicator();
		$("queryInfo").innerHTML = $("gievItem").value = "";
        $("length" + document.spells.pageLength).checked = "true";
        $("numTablesSelect").options[document.spells.numOfTables - 1].selected = "true";

        if (category == "killedby") labelAverageCount = labelAverageKills;

        $("categoryHeader").className = document.spells.category + "Header";
        $("categoryVisual").className = document.spells.category + "Visual";

		if (!daysCalculated) calculateDays();
        	for (var i = 0; i < document.spells.numOfTables; i++) {
                switch (i) {
                    case 0: if($("1") == null) { window.setTimeout("preLoadChecker('" + file1 + "'," + (i+1) + ")", 0); } break;
                    case 1: if($("2") == null) { window.setTimeout("preLoadChecker('" + file2 + "'," + (i+1) + ")", 200); } break;
                    case 2: if($("3") == null) { window.setTimeout("preLoadChecker('" + file3 + "'," + (i+1) + ")", 200); } break;
                    case 3: if($("4") == null) { window.setTimeout("preLoadChecker('" + file4 + "'," + (i+1) + ")", 200); } break;
                    case 4: if($("5") == null) { window.setTimeout("preLoadChecker('" + file5 + "'," + (i+1) + ")", 200); } break;
                    case 5: if($("6") == null) { window.setTimeout("preLoadChecker('" + file6 + "'," + (i+1) + ")", 200); } break;
                    case 6: if($("7") == null) { window.setTimeout("preLoadChecker('" + file7 + "'," + (i+1) + ")", 200); } break;
                }
            } 

        $("gievItem").onChange = throttleSubmission();
        $("gievItem").onfocus = function () { 
            if (this.value.length < 3) {
                $('searchInfo').innerHTML = labelMinimumCharactersForSearch;
                if(!is_opera) {
                    $("searchInfo").setOpacity(0); 
                    new Effect.Appear("searchInfo", {duration: 0.5});
                }
            }
         };
        displayProgressIndicator();
    }
