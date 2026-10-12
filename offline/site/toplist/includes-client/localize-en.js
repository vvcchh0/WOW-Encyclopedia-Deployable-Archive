if (!lang) var lang = "en";
if (!category) var category = "killedby"; // no change required!

M = new Array("January","February","March","April","May","June","July","August","September","October","November","December");
D = new Array("Sun","Mon","Tue","Wed","Thu","Fri","Sat");
var labelHeaderRank = "Rank";
var labelHeaderItem = "Item";    
var labelHeaderCreature = "Creature";    
var labelHeaderCount = "Count";
var labelHeaderQuests = "Quests";
var labelNumberOfDays = "# of days: "; // text for the "select how many days to display" box
var labelSearch = "Search: "; // text for the search box
var labelBrowseGlobal = "browse globally";
var introText = ""; // leave empty here, see below
var labelSortBy = "sort by ";
var labelPlayersKilled = "Count";
var labelNoSearchResultsFound = "No search results found.";
var labelMinimumCharactersForSearch = "(type at least 3 characters)";

var labelAverageRank = "Average rank: ";
var labelAverageCount = "Average count: ";
var labelAverageKills = "Average kills: ";
var labelItemsSearched = "entries searched"; // will be used like "10002 entries have been searched..."
var labelMatches = "matches"; // will be used like "10002 entries have been searched..."

var labelJumpToLastPage = "Jump to last page."
var labelJumpToFirstPage = "Jump to first page."
var labelJumpToNextPage = "Jump to next page."
var labelJumpToPrevPage = "Jump to previous page."

var labelNoDataAvail = "No data available."; // i.e. 7.000.000
var numDelimiter = ","; // i.e. 7.000.000

switch (category) {
    case "killedby": introText = "Below is a list of the most dangerous creatures in World of Warcraft. These monsters have slaughtered many hapless adventurers in the past few days. Caution is advised when confronting any of these dangerous foes."; break;
    case "spellcreate": introText = "Below is a list of the most common items created by players or NPCs in World of Warcraft over the past few days."; break;
    case "unitloot": introText = "Below is a list of the most commonly looted items from the past few days. Check the list to see what items the players have wrested away from their enemies."; break;
    case "auctionsold": introText = "Below is a list of the auction house's most frequently sold items. A good place to start if you're looking for a way to make some quick gold."; break;
    case "gameobjloot": introText = "Below is a list of the most gathered items in World of Warcraft over the past few days."; break; 
    case "questcomplete": introText = "Below is a list of the most commonly completed quests."; break; 
}

// suffixes for numbers to be displayed in the rank column
var numberFirstSuffix = "st"; //i.e. 1st
var numberSecondSuffix = "nd"; //i.e. 2nd
var numberThirdSuffix = "rd"; //i.e. 3rd
var numberDefaultSuffix = "th"; //i.e. 200th









