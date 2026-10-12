var resetMonth = 1;
var resetDay = 1;

var reset7 = 0;
var reset5 = 0;
var reset3 = 1;

var t = 0;
var raid = new Array;
raid[t] = [0, "Blackwing Lair", 7]; t++;
raid[t] = [0, "Molten Core", 7]; t++;
raid[t] = [0, "Temple of Ahn&#146;Qiraj", 7]; t++;
raid[t] = [0, "Naxxramas", 7]; t++;
raid[t] = [0, "Onyxia", 5]; t++;
raid[t] = [0, "Zul&#146;Gurub", 3]; t++;
raid[t] = [0, "Ruins of Ahn&#146;Qiraj", 3]; t++;
raid[t] = [0, "Magtheridon", 7]; t++;
raid[t] = [0, "Gruul&#146;s Lair", 7]; t++;
raid[t] = [0, "CoT: Battle for Mount Hyjal", 7]; t++;
raid[t] = [0, "Tempest Keep: The Eye", 7]; t++;
raid[t] = [0, "Coilfang Reservoir: Serpentshrine Cavern", 7]; t++;
raid[t] = [0, "Karazhan", 7]; t++;
raid[t] = [0, "Black Temple", 7]; t++;
raid[t] = [0, "Zul&#146;Aman", 3]; t++;


var monthArrayName = new Array;
monthArrayName[1] = "January";
monthArrayName[2] = "February";
monthArrayName[3] = "March";
monthArrayName[4] = "April";
monthArrayName[5] = "May";
monthArrayName[6] = "June";
monthArrayName[7] = "July";
monthArrayName[8] = "August";
monthArrayName[9] = "September";
monthArrayName[10] = "October";
monthArrayName[11] = "November";
monthArrayName[12] = "December";

var weekdayName = new Array;
weekdayName[0] = "Sunday";
weekdayName[1] = "Monday";
weekdayName[2] = "Tuesday";
weekdayName[3] = "Wednesday";
weekdayName[4] = "Thursday";
weekdayName[5] = "Friday";
weekdayName[6] = "Saturday";

var textpreviousmonth = "Previous Month";
var textnextmonth = "Next Month";

var textresettime = "Reset Time";

var threeAM = "4:00AM";
var eightAM = "8:00AM";

var textmaintenance = "Every 7 days";

var legendnote = "Note: icons on the calendar denote days when instances are reset";

var raidtext1 = "All raid instances reset at a certain realm time on certain days, regardless of when players were actually saved to the instance. The reset times are as follows:";

var classicRaids = "<p><div style='padding-left:20px;'>\
<b style='color:ffe400;'>" + raid[0][1] +  "</b>: <span style='color:ffffff;'>Every 7 Days during weekly maintenance</span><br>\
<b style='color:ffe400;'>" + raid[1][1] +  "</b>: <span style='color:ffffff;'>Every 7 Days during weekly maintenance</span><br>\
<b style='color:ffe400;'>" + raid[2][1] +  "<small style='color:ffe400;'>(40-man)</small></b>: <span style='color:ffffff;'>Every 7 Days during weekly maintenance</span><br>\
<b style='color:ffe400;'>" + raid[3][1] +  "</b>: <span style='color:ffffff;'>Every 7 Days during weekly maintenance</span><br>\
<b style='color:ffe400;'>" + raid[4][1] +  "</b>: <span style='color:ffffff;'>Every 5 Days at 4:00AM</span><br>\
<b style='color:ffe400;'>" + raid[5][1] +  "</b>: <span style='color:ffffff;'>Every 3 Days at 4:00AM</span><br>\
<b style='color:ffe400;'>" + raid[6][1] +  "<small style='color:ffe400;'>(20-man)</small></b>: <span style='color:ffffff;'>Every 3 Days at 4:00AM</span><br>\
</div><p>";

var bcRaids = "<p><div style='padding-left:20px;'>\
<b style='color:ffe400;'>All displayed instances</b>: <span style='color:ffffff;'>Every 7 Days.</span><br>\
Except <b style='color:ffe400;'>" + raid[14][1] +  "</b>: <span style='color:ffffff;'>Every 3 Days at 8:00AM.</span><br><br>\
Additionally, Heroic level instances reset every day at 4:00AM realm time. Introduced in The Burning Crusade, Heroic-level instances are alternate versions of the new five-man instances that have been considerably increased in difficulty, and have their own set of more powerful rewards. Each new instance has its own requirements for setting its difficulty level to heroic, such as special keys. Once everyone in a five-man group who wishes to enter an instance has the key to unlock heroic difficulty for that instance, the group leader simply has to set the instance to heroic in the group leader menu.\
</div><p>";

var raidtext2 = "Resets occur at 4:00AM or during weekly maintenance. <p>\
As the reset time approaches, players inside instances will be informed of the impending reset every hour on the hour. 15 minutes before the reset, the /reminders become more frequent; once the reset time is reached, all players in the \
instance will be ported to their bind point. You can access your saved raid status at any time via <b>/raidinfo</b>, and you \
will be informed of your status regarding an instance when you zone into the dungeon.";