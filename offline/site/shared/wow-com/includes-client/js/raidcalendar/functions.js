function drawCalendar () {
    if (type == "both") {
        var cells = document.getElementsByTagName("TD");
        for (var i=0; i< cells.length; i++) {
            cell = cells[i];
            if(cell.className.indexOf("calendarCell") != -1) cell.className += " calendarCellLarge";
        }
        document.getElementById("townhallTable").className = "townhallbig";
        document.getElementById("infoContainer").innerHTML = raidtext1;
        document.getElementById("infoContainer").innerHTML += classicRaids;    
        document.getElementById("infoContainer").innerHTML += bcRaids;    
        document.getElementById("infoContainer").innerHTML += raidtext2;    
    } else {
        var cells = document.getElementsByTagName("TD");
        for (var i=0; i< cells.length; i++) {
            cell = cells[i];
            if(cell.className.indexOf("calendarCell") != -1) cell.className = "calendarCell";
        }
        document.getElementById("townhallTable").className = "townhallbig";
        document.getElementById("infoContainer").innerHTML = raidtext1;
        document.getElementById("infoContainer").innerHTML += (type == "classic") ? classicRaids : bcRaids;    
        document.getElementById("infoContainer").innerHTML += raidtext2;    
    }
    
    if (type == "bc") {
        document.getElementById("bcRaids").style.display = "inline";
        document.getElementById("classicRaids").style.display = "none";
        document.getElementById("classic-link").className = "classic-off";
        document.getElementById("bc-link").className = "bc-on";
    }
    else if (type == "classic") {
        document.getElementById("bcRaids").style.display = "none";
        document.getElementById("classicRaids").style.display = "inline";
        document.getElementById("bc-link").className = "bc-off";
        document.getElementById("classic-link").className = "classic-on";
    } else { 
        document.getElementById("bcRaids").style.display = "inline";
        document.getElementById("classicRaids").style.display = "inline";
   }
    
    initCalendar((currMonth != "") ? currMonth : todate.getMonth()+1, year);
}

function getResetDay (inputResetMonth, inputResetDay) {
	if (inputResetMonth == 1)
		return inputResetDay;
	else {
		var d=1;
		while (d < inputResetMonth) {
			inputResetDay += monthArray[d];
			d++;
		}
	}
	return inputResetDay;
}
	
function clearCalendar(month) {
	i=1;
	while (i <= 42) {
		raidColumn=1;
		while (raidColumn <= raid.length) {
			calendarElement=document.getElementById('raid_'+ i +'_'+raidColumn);
	   		calendarElement.style.display='none';
			raidColumn++;
		}
		i++;
	}
}

function initCalendar(newMonth, year) {
    currMonth = newMonth;
    monthName=monthArrayName[newMonth];
    calendarElement=document.getElementById("monthTitle");
    calendarElement.innerHTML=monthName.toUpperCase();	
    
    var counterDay=0;
    var startDay;
    if (year == 2006 || year == 106)
    	startDay=0;
    else if (year == 2007 || year == 107)
    	startDay=1;
    else if (year == 2008 || year == 108)
    	startDay=2;	
    else if (year == 2009 || year == 109)
    	startDay=4;
    else if (year == 2010 || year == 110)
    	startDay=5;
    else if (year == 2011 || year == 111)
    	startDay=6;
    else if (year == 2012 || year == 112)
    	startDay=0;
    else if (year == 2013 || year == 113)
    	startDay=2;
    else if (year == 2014 || year == 114)
    	startDay=3;
    
    var i=1;
    	var dayCount=1;
    
    if (newMonth == 1){
    	x=(startDay + 1)%7;
    	counterDay=0;
    }else {
    	var monthCount=newMonth - 1;
    	var y=0;
    	counterDay=1;	
    	while (monthCount > 0){
    		y += monthArray[monthCount];
    		monthCount--;
    		counterDay=y;
    	}
    	x=y%7 + 1 + startDay;	
    }
    
    counterDay++;
    
    y=(x - 1)%7;	
    
    if (x == 0)
    	y=6;
    z=y;
    
    clearCalendar(newMonth);
    
    i=1;
    
    beforeStart=y;
    
    while(beforeStart > 0) {
    	
        var calendarElement=document.getElementById("cell_" + beforeStart);
        calendarElement.innerHTML='';
    	beforeStart--;
    }
    
    if (newMonth == todate.getMonth()+1) {
        changeThis=todate.getDate() + y;
    	calendarElement.style.color='ffffff';
        calendarElement=document.getElementById("cell_background_"+changeThis);
    	calendarElement.style.backgroundImage = "url(/shared/wow-com/images/basics/raidcalendar/celltoday.jpg)";
    	savedCell=changeThis;
        
    } else {
        if (savedCell != 0) {
    	    calendarElement=document.getElementById("cell_background_"+savedCell);
    		calendarElement.style.backgroundImage='';
    	}
    }
    
    while (i <= monthArray[newMonth]) {
    	y++;
        var calendarElement=document.getElementById("cell_" + y);
        calendarElement.innerHTML=i;
    	i++;	
    	raidColumn=1;
    	if ((counterDay-resetDay)%7 - reset7==0){	
    
            if(type == "both" || type == "classic") {
        		calendarElement=document.getElementById('raid_'+ y +'_1');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_2');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_3');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_4');
           		calendarElement.style.display='inline';
            }            
    
            if(type == "both" || type == "bc") {
        		calendarElement=document.getElementById('raid_'+ y +'_8');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_9');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_10');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_11');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_12');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_13');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_14');
           		calendarElement.style.display='inline';
            }
    	}
    	
    	if ((counterDay-resetDay)%5 - reset5==0){	
            if(type == "both" || type == "classic") {
        		calendarElement=document.getElementById('raid_'+ y +'_5');
           		calendarElement.style.display='inline';
            }
    	}	
    
    	if ((counterDay-resetDay)%3 - reset3==0){	
            if(type == "both" || type == "classic") {
        		calendarElement=document.getElementById('raid_'+ y +'_6');
           		calendarElement.style.display='inline';
        		calendarElement=document.getElementById('raid_'+ y +'_7');
           		calendarElement.style.display='inline';	
            }
    	}
    	if ((counterDay-resetDay)%3 - reset3==0){	
            if(type == "both" || type == "bc") {
        		calendarElement=document.getElementById('raid_'+ y +'_15');
           		calendarElement.style.display='inline';	
            }
    	}
    	counterDay++;
    }
    while (i <= 42) {
    	y++;
    
    	if (y <= 42) {
    	    var calendarElement=document.getElementById("cell_" + y);
        	calendarElement.innerHTML='';
    	}
    	i++;	
    }
    
    nextMonth=newMonth + 1; 
    previousMonth=newMonth - 1;
    }
	
	function goNextMonth() {
	if (nextMonth < 13)
		initCalendar(nextMonth, year);
}

function goPreviousMonth() {
	if (previousMonth > 0)
		initCalendar(previousMonth, year);
}

function changeView(calendarType) {
    type = calendarType;
    drawCalendar(currMonth);
}
function addEvent(obj, evType, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evType, fn, false);
        return true;
    } else if (obj.attachEvent) {
        var r = obj.attachEvent("on"+evType, fn);
        return r;
    } else {
        return false;
    }
}