// awb512-119-u
	var linkClass="menuLink";//initial css style of links
	var menuNumber=7;
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
	var NoOffFirstLineMenus=12;			// Number of main menu  items
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

	var TargetLoc="menuCommunity";				// span id for relative positioning
	var MenuWrap=1;				// enables/ disables menu wrap 1 or 0
	var RightToLeft=0;				// enables/ disables right to left unfold 1 or 0
	var BottomUp=0;				// enables/ disables Bottom up unfold 1 or 0
	var UnfoldsOnClick=0;			// Level 1 unfolds onclick/ onmouseover
	var BaseHref="";				// BaseHref lets you specify the root directory for relative links. 
						// The script precedes your relative links with BaseHref
						// For instance: 
						// when your BaseHref= "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu7_var.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu7_var.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
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
	var MenuSlide="true";

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
Menu1=new Array(bulletImg+"Overview"+underLine,"/community/ ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu2=new Array(bulletImg+"Beta Signup"+underLine,"/misc/beta-signup.html ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu3=new Array(bulletImg+"Comics"+underLine,"/community/comics.html ",menuBg,25,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
	Menu3_1=new Array(bulletImg+"May, 2008"+underLine,"/community/comics/2008-05.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_2=new Array(bulletImg+"April, 2008"+underLine,"/community/comics/2008-04.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_3=new Array(bulletImg+"Mar, 2008"+underLine,"/community/comics/2008-03.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_4=new Array(bulletImg+"Feb, 2008"+underLine,"/community/comics/2008-02.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_5=new Array(bulletImg+"Jan, 2008"+underLine,"/community/comics/2008-01.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_6=new Array(bulletImg+"Dec, 2007"+underLine,"/community/comics/2007-12.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
    Menu3_7=new Array(bulletImg+"Nov, 2007"+underLine,"/community/comics/2007-11.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_8=new Array(bulletImg+"Oct, 2007"+underLine,"/community/comics/2007-10.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
    Menu3_9=new Array(bulletImg+"Sept, 2007"+underLine,"/community/comics/2007-09.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_9=new Array(bulletImg+"Aug, 2007"+underLine,"/community/comics/2007-08.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_10=new Array(bulletImg+"July, 2007"+underLine,"/community/comics/2007-07.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_11=new Array(bulletImg+"June, 2007"+underLine,"/community/comics/2007-06.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
    Menu3_12=new Array(bulletImg+"May, 2007"+underLine,"/community/comics/2007-05.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_13=new Array(bulletImg+"April, 2007"+underLine,"/community/comics/2007-04.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
    Menu3_14=new Array(bulletImg+"Mar, 2007"+underLine,"/community/comics/2007-03.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_15=new Array(bulletImg+"Feb, 2007"+underLine,"/community/comics/2007-02.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_16=new Array(bulletImg+"Jan, 2007"+underLine,"/community/comics/2007-01.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
    Menu3_17=new Array(bulletImg+"Dec, 2006"+underLine,"/community/comics/2006-12.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
    Menu3_18=new Array(bulletImg+"Nov, 2006"+underLine,"/community/comics/2006-11.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_19=new Array(bulletImg+"Oct, 2006"+underLine,"/community/comics/2006-10.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_20=new Array(bulletImg+"Sept, 2006"+underLine,"/community/comics/2006-09.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_21=new Array(bulletImg+"Aug, 2006"+underLine,"/community/comics/2006-08.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_22=new Array(bulletImg+"July, 2006"+underLine,"/community/comics/2006-07.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_23=new Array(bulletImg+"June, 2006"+underLine,"/community/comics/2006-06.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_24=new Array(bulletImg+"May, 2006"+underLine,"/community/comics/2006-05.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu3_25=new Array(bulletImg+"PA Comics"+underLine,"/community/pa-comics.html ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu4=new Array(bulletImg+"Machinima"+underLine,"/community/machinima/ ",menuBg,3,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
	Menu4_1=new Array(bulletImg+"Welcome"+underLine,"/community/machinima/welcome.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu4_2=new Array(bulletImg+"Fair-Use Guide"+underLine,"/community/machinima/letter.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu4_3=new Array(bulletImg+"Machinima Movies"+underLine,"/community/machinima/movies.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu5=new Array(bulletImg+"Player Stories"+underLine,"/community/stories/",menuBg,3,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
	Menu5_1=new Array(bulletImg+"Current Stories"+underLine,"/community/stories/stories.xml",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu5_2=new Array(bulletImg+"Story Archive"+underLine,"/community/stories/archive.xml",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu5_3=new Array(bulletImg+"Submit a Story"+underLine,"/community/stories/submit.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu6=new Array(bulletImg+"Community Spotlight"+underLine,"/community/communitylinks.html ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu7=new Array(bulletImg+"Contests"+underLine,"/contests/ ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu8=new Array(bulletImg+"Guild Relations"+underLine,"/community/guildrelations.html ",menuBg,1,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu8_1=new Array(bulletImg+"Guild Nexus"+underLine,"/community/guildnexus.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9=new Array(bulletImg+"Real-Life Events"+underLine,"/community/reallifeevents.html ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu10=new Array(bulletImg+"Fan Art"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu7_var.js&requested=http%3A%2F%2Fwww.blizzard.com%2Finblizz%2Ffanart%2F&reason=external-or-uncollected-resource ",menuBg,3,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
  Menu10_1=new Array(bulletImg+"Current Fan Art"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu7_var.js&requested=http%3A%2F%2Fwww.blizzard.com%2Finblizz%2Ffanart%2F&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu10_2=new Array(bulletImg+"Art Contest 2006"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu7_var.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fus%2Finblizz%2Fcontests%2Fartcontest2006%2Findex.html&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu10_3=new Array(bulletImg+"Submit Fan Art"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu7_var.js&requested=http%3A%2F%2Fwww.blizzard.com%2Finblizz%2Ffanart%2Frules.shtml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11=new Array(bulletImg+"Fansites"+underLine,"/community/fansites.html ",menuBg,1,15,140,"transparent","","","","transparent","",-1,-1,-1,"",""); 
 Menu11_1=new Array(bulletImg+"Fan Site Kit"+underLine,"/wrath/downloads.xml ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu12=new Array(bulletImg+"Fan Wallpapers"+underLine,"/downloads/wallpapers/fan-wallpapers/ ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
