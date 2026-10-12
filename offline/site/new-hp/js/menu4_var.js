// awb512-119-u

	var linkClass="menuLink";//initial css style of links
	var menuNumber=4;
	var agt=navigator.userAgent.toLowerCase(), appVer = navigator.appVersion.toLowerCase(), iePos  = appVer.indexOf('msie'), is_opera = (agt.indexOf("opera") != -1), is_ie   = ((iePos!=-1) && (!is_opera));
	if(is_ie){
		var menuBg="";
		var menuBgIndent="";
		var underLine="<img src='/new-hp/images/menu/mainmenu/bullet-trans-line.gif'/>";
		var bulletImg="<img src='/new-hp/images/menu/mainmenu/bullet-trans-dot.gif' align='left'/>";
		var bulletImgIndent="<img src='/new-hp/images/menu/mainmenu/bullet-trans-dot-indent.gif' align='left'/>";
	}else{
		var menuBg="/new-hp/images/menu/mainmenu/bullet-trans-bg.gif";
		var menuBgIndent="/new-hp/images/menu/mainmenu/bullet-trans-indent-bg.gif";
		var bulletImgIndent="<img src = /shared/wow-com/images/layout/pixel.gif width=16 height=1/>";
		var underLine="";
		var bulletImg="";
	}
	var NoOffFirstLineMenus=8;			// Number of main menu  items
						// Colorvariables:
						// Color variables take HTML predefined color names or "#rrggbb" strings
						//For transparency make colors and border color ""
	var LowBgColor="black";			// Background color when mouse is not over
	var HighBgColor="#0B2237";			// Background color when mouse is over
	var FontLowColor="#F4C400";			// Font color when mouse is not over
	var FontHighColor="white";			// Font color when mouse is over
	var BorderColor="#A5A5A5";			// Border color
	var BorderWidthMain=0;			// Border width main items
	var BorderWidthSub=1;			// Border width sub items
 	var BorderBtwnMain=0;			// Border width between elements main items
	var BorderBtwnSub=0;			// Border width between elements sub items
	var FontFamily="arial,comic sans ms,technical";	// Font family menu items
	var FontSize=11;				// Font size menu items
	var FontBold=1;				// Bold menu items 1 or 0
	var FontItalic=0;				// Italic menu items 1 or 0
	var MenuTextCentered="left";		// Item text position left, center or right
	var MenuCentered="left";			// Menu horizontal position can be: left, center, right
	var MenuVerticalCentered="top";		// Menu vertical position top, middle,bottom or static
	var ChildOverlap=.2;			// horizontal overlap child/ parent
	var ChildVerticalOverlap=.2;			// vertical overlap child/ parent
	var StartTop=33;				// Menu offset x coordinate
	var StartLeft=17;				// Menu offset y coordinate
	
	if(!is_ie)StartLeft=6;
	var VerCorrect=0;				// Multiple frames y correction
	var HorCorrect=0;				// Multiple frames x correction
	var DistFrmFrameBrdr=0;			// Distance between main menu and frame border
	if(is_ie)
		var LeftPaddng=0;				// Left padding
	else
		var LeftPaddng=10;				// Left padding
	var TopPaddng=-1;				// Top padding. If set to -1 text is vertically centered
	var FirstLineHorizontal=0;			// Number defines to which level the menu must unfold horizontal; 0 is all vertical
	var MenuFramesVertical=1;			// Frames in cols or rows 1 or 0
	var DissapearDelay=500;			// delay before menu folds in
	var UnfoldDelay=0;			// delay before sub unfolds
	var UnfoldDelay2=100;			// delay before sub builds	
	var TakeOverBgColor=1;			// Menu frame takes over background color subitem frame
	var FirstLineFrame="space";			// Frame where first level appears
	var SecLineFrame="space";			// Frame where sub levels appear
	var DocTargetFrame="space";		// Frame where target documents appear

	var TargetLoc="menuInteractive";				// span id for relative positioning
	var MenuWrap=1;				// enables/ disables menu wrap 1 or 0
	var RightToLeft=0;				// enables/ disables right to left unfold 1 or 0
	var BottomUp=0;				// enables/ disables Bottom up unfold 1 or 0
	var UnfoldsOnClick=0;			// Level 1 unfolds onclick/ onmouseover
	var BaseHref="";				// BaseHref lets you specify the root directory for relative links. 
						// The script precedes your relative links with BaseHref
						// For instance: 
						// when your BaseHref= "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
						// Can also be used when you use images in the textfields of the menu
						// "MenuX=new Array(bulletImg+"<img src=\""+BaseHref+"MyImage\">"
						// For testing on your harddisk use syntax like: BaseHref="file:///C|/MyFiles/Homepage/"

	var Arrws=["/shared/wow-com/images/subnav/tri.gif",14,15,"/shared/wow-com/images/subnav/tri.gif",14,15,"/shared/wow-com/images/subnav/tri.gif",14,15,"/shared/wow-com/images/subnav/tri.gif",14,15];

						// Arrow source, width and height.
						// If arrow images are not needed keep source ""

	var MenuUsesFrames=1;			// MenuUsesFrames is only 0 when Main menu, submenus,
						// document targets and script are in the same frame.
						// In all other cases it must be 1

	var RememberStatus=0;			// RememberStatus: When set to 1, menu unfolds to the presetted menu item. 
						// When set to 2 only the relevant main item stays highligthed
						// The preset is done by setting a variable in the head section of the target document.
						// 2_2_1 represents the menu item Menu2_2_1=new Array(.......

	var OverFormElements=0;			// Set this to 0 when the menu does not need to cover form elements.
	var BuildOnDemand=1;			// 1/0 When set to 1 the sub menus are build when the parent is moused over
	var BgImgLeftOffset=5;			// Only relevant when bg image is used as rollover
	var ScaleMenu=0;				// 1/0 When set to 0 Menu scales with browser text size setting

	var HooverBold=0;				// 1 or 0
	var HooverItalic=0;				// 1 or 0
	var HooverUnderLine=0;			// 1 or 0
	var HooverTextSize=0;			// 0=off, number is font size difference on hoover
	var HooverVariant=0;			// 1 or 0

						// Below some pretty useless effects, since only IE6+ supports them
						// I provided 3 effects: MenuSlide, MenuShadow and MenuOpacity
						// If you don't need MenuSlide just leave in the line var MenuSlide="";
						// delete the other MenuSlide statements
						// In general leave the MenuSlide you need in and delete the others.
						// Above is also valid for MenuShadow and MenuOpacity
						// You can also use other effects by specifying another filter for MenuShadow and MenuOpacity.
						// You can add more filters by concanating the strings
	var MenuSlide="";

	var MenuShadow="";
	var MenuShadow="progid:DXImageTransform.Microsoft.DropShadow(color=#000000, offX=2, offY=2, positive=1)";
	var MenuShadow="progid:DXImageTransform.Microsoft.Shadow(color=#000000, direction=135, strength=3)";

	var MenuOpacity="";
	var MenuOpacity="progid:DXImageTransform.Microsoft.Alpha(opacity=85)";

	function BeforeStart(){return}
	function AfterBuild(){parent.clearFiller(menuNumber);return}
	function BeforeFirstOpen(){return}
	function AfterCloseAll(){return}

// Menu tree:
// MenuX=new Array(bulletImg+"ItemText","Link","background image",number of sub elements,height,width,"bgcolor","bghighcolor",
//	"fontcolor","fonthighcolor","bordercolor","fontfamily",fontsize,fontbold,fontitalic,"textalign","statustext");
// Color and font variables defined in the menu tree take precedence over the global variables
// Fontsize, fontbold and fontitalic are ignored when set to -1.
// For rollover images ItemText or background image format is:  "rollover?"+BaseHref+"Image1.jpg?"+BaseHref+"Image2.jpg" 
Menu1=new Array(bulletImg+"Armory"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2F&reason=external-or-uncollected-resource ",menuBg,11,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu1_1=new Array(bulletImg+"Updates"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2F%23updates.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_2=new Array(bulletImg+"Item Search"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fitem-search.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_3=new Array(bulletImg+"Character Search"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fcharacter-search.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_4=new Array(bulletImg+"Guild Search"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fguild-search.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_5=new Array(bulletImg+"Team Search"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fteam-search.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_6=new Array(bulletImg+"Arena Ladder"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Farena-ladder.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_7=new Array(bulletImg+"Dungeons/Raids"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fdungeons.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_8=new Array(bulletImg+"Factions"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffactions.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_9=new Array(bulletImg+"PvP Rewards"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fpvprewards.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_10=new Array(bulletImg+"FAQ"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-armory.xml&reason=external-or-uncollected-resource ",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_1=new Array(bulletImg+"Arena Ladder"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-arena-ladder.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_2=new Array(bulletImg+"Arena Tournament"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-arena-tournament.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_3=new Array(bulletImg+"Character Profiles"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-character-sheet.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_4=new Array(bulletImg+"Guild Profiles"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-guild-info.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_5=new Array(bulletImg+"Items"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-item-info.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_6=new Array(bulletImg+"Find an Upgrade"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-item-info-recommended.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_7=new Array(bulletImg+"Team Profiles"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffaq-team-info.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_11=new Array(bulletImg+"Known Issues"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fthread.html%3FtopicId%3D2765957433%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");



Menu2=new Array(bulletImg+"Arena"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Farena-tournament.xml&reason=external-or-uncollected-resource ",menuBg,4,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
 Menu2_1=new Array(bulletImg+"Arena Tournament"+underLine,"/pvp/tournament/index.xml ",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
 Menu2_1_1=new Array(bulletImg+"Tournament Forum"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D6304584&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu2_2=new Array(bulletImg+"Arena Intro"+underLine,"/pvp/arena/index.xml ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu2_3=new Array(bulletImg+"Inside Arenas"+underLine,"/insider/11/arena.xml ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu2_4=new Array(bulletImg+"Item Rewards"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu4_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fpvprewards.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
//Menu3=new Array(bulletImg+"Game Statistics"+underLine,"/toplist/buttons.html ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu3=new Array(bulletImg+"Encyclopedia"+underLine,"/info/encyclopedia/index.xml ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");

Menu4=new Array(bulletImg+"Talent Calculators"+underLine,"/info/classes/talent-index/ ",menuBg,10,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
  Menu4_1=new Array(bulletImg+"Basics"+underLine,"/info/basics/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_2=new Array(bulletImg+"Druid"+underLine,"/info/classes/druid/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_3=new Array(bulletImg+"Hunter"+underLine,"/info/classes/hunter/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_4=new Array(bulletImg+"Mage"+underLine,"/info/classes/mage/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_5=new Array(bulletImg+"Paladin"+underLine,"/info/classes/paladin/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_6=new Array(bulletImg+"Priest"+underLine,"/info/classes/priest/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_7=new Array(bulletImg+"Rogue"+underLine,"/info/classes/rogue/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_8=new Array(bulletImg+"Shaman"+underLine,"/info/classes/shaman/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_9=new Array(bulletImg+"Warlock"+underLine,"/info/classes/warlock/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu4_10=new Array(bulletImg+"Warrior"+underLine,"/info/classes/warrior/talents.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5=new Array(bulletImg+"Events Calendar"+underLine,"/info/events/calendar/ ",menuBg,17,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu5_1=new Array(bulletImg+"New Year's Eve"+underLine,"/info/events/newyears/",menuBg,0,16,125,"","","","","","",-1,-1,-1,"","");
Menu5_2=new Array(bulletImg+"Lunar Festival"+underLine,"/info/events/lunarnewyears/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_3=new Array(bulletImg+"Love is in the Air"+underLine,"/info/events/loveisintheair/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_4=new Array(bulletImg+"Noblegarden"+underLine,"/community/ingameevents.html#noblegarden",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_5=new Array(bulletImg+"Children's Week"+underLine,"/info/events/childrensweek/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_6=new Array(bulletImg+"Midsummer Fire Festival"+underLine,"/info/events/midsummer/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_7=new Array(bulletImg+"Harvest Festival"+underLine,"/info/events/harvestfestival/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_8=new Array(bulletImg+"Brewfest"+underLine,"/info/events/brewfest/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_9=new Array(bulletImg+"Hallow's End"+underLine,"/info/events/hallowsend/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_10=new Array(bulletImg+"Winter Veil"+underLine,"/info/events/winterveil/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_11=new Array(bulletImg+"AQ War Effort"+underLine,"/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_12=new Array(bulletImg+"Battlegrounds Holiday"+underLine,"/community/ingameevents.html#calltoarms",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_13=new Array(bulletImg+"Darkmoon Faire Event"+underLine,"/info/basics/factions/darkmoon/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_14=new Array(bulletImg+"Elemental Invasions"+underLine,"/community/ingameevents.html#elemental",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_15=new Array(bulletImg+"Fishing Extravaganza"+underLine,"/info/events/fishing/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_16=new Array(bulletImg+"Gurubashi Arena"+underLine,"/community/ingameevents.html#gurubashi",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_17=new Array(bulletImg+"The Scourge Invasion"+underLine,"/info/events/scourgeinvasion/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu6=new Array(bulletImg+"Armor Sets"+underLine,"/info/items/armorsets/ ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu7=new Array(bulletImg+"World Map"+underLine,"/info/flashmap/ ",menuBg,1,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu7_1=new Array(bulletImg+"Outland Map"+underLine,"/burningcrusade/townhall/outlandmap.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8=new Array(bulletImg+"Battlegroups"+underLine,"/pvp/battlegrounds/battlegroups/",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");

