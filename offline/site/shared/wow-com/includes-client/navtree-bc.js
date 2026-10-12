// awb512-119-u
	var linkClass="subMenuLink";
	var menuNumber=9;
	var agt=navigator.userAgent.toLowerCase(), appVer = navigator.appVersion.toLowerCase(), iePos  = appVer.indexOf('msie'), is_opera = (agt.indexOf("opera") != -1), is_ie   = ((iePos!=-1) && (!is_opera));
	if(is_ie){
		var menuBg="";
		var menuBgIndent="";
		var underLine="<img src=/new-hp/images/menu/mainmenu/bullet-trans-line-blue.gif />";
		var bulletImg="<img src=/new-hp/images/menu/mainmenu/bullet-trans-dot-blue.gif align=left />";
		var bulletImgIndent="<img src=/new-hp/images/menu/mainmenu/bullet-trans-dot-indent.gif align=left />";
	}else{
		var menuBg="/new-hp/images/menu/mainmenu/bullet-trans-bg-blue.gif";
		var menuBgIndent="/new-hp/images/menu/mainmenu/bullet-trans-indent-bg.gif";
		var bulletImgIndent="<img src = /images/layout/pixel.gif width=16 height=1 />";
		var underLine="";
		var bulletImg="";
	}
	var NoOffFirstLineMenus=1;			// Number of main menu  items
						// Colorvariables:
						// Color variables take HTML predefined color names or "#rrggbb" strings
						//For transparency make colors and border color ""
	var LowBgColor="#051B38";			// Background color when mouse is not over
	var HighBgColor="#013A88";			// Background color when mouse is over
	var FontLowColor="white";			// Font color when mouse is not over
	var FontHighColor="white";			// Font color when mouse is over
	var BorderColor="#116EED";			// Border color
	var BorderWidthMain=0;			// Border width main items
	var BorderWidthSub=1;			// Border width sub items
 	var BorderBtwnMain=0;			// Border width between elements main items
	var BorderBtwnSub=0;			// Border width between elements sub items
	var FontFamily="arial,comic sans ms,technical";	// Font family menu items
	var FontSize=11;				// Font size menu items
	var FontBold=0;				// Bold menu items 1 or 0
	var FontItalic=0;				// Italic menu items 1 or 0
	var MenuTextCentered="left";		// Item text position left, center or right
	var MenuCentered="left";			// Menu horizontal position can be: left, center, right
	var MenuVerticalCentered="top";		// Menu vertical position top, middle,bottom or static
	var ChildOverlap=.2;			// horizontal overlap child/ parent
	var ChildVerticalOverlap=.2;			// vertical overlap child/ parent
	var StartTop=-9;				// Menu offset x coordinate
	var StartLeft=0;				// Menu offset y coordinate
	var VerCorrect=0;				// Multiple frames y correction
	var HorCorrect=0;				// Multiple frames x correction
	var DistFrmFrameBrdr=0;			// Distance between main menu and frame border
	if(is_ie)
		var LeftPaddng=9;				// Left padding
	else
		var LeftPaddng=9;				// Left padding
	var TopPaddng=-1;				// Top padding. If set to -1 text is vertically centered
	var FirstLineHorizontal=1;			// Number defines to which level the menu must unfold horizontal; 0 is all vertical
	var MenuFramesVertical=1;			// Frames in cols or rows 1 or 0
	var DissapearDelay=500;			// delay before menu folds in
	var UnfoldDelay=0;			// delay before sub unfolds
	var UnfoldDelay2=100;			// delay before sub builds
	var TakeOverBgColor=1;			// Menu frame takes over background color subitem frame
	var FirstLineFrame="space";			// Frame where first level appears
	var SecLineFrame="space";			// Frame where sub levels appear
	var DocTargetFrame="space";		// Frame where target documents appear
	var TargetLoc="filterMenu";				// span id for relative positioning
	var MenuWrap=1;				// enables/ disables menu wrap 1 or 0
	var RightToLeft=0;				// enables/ disables right to left unfold 1 or 0
	var BottomUp=0;				// enables/ disables Bottom up unfold 1 or 0
	var UnfoldsOnClick=0;			// Level 1 unfolds onclick/ onmouseover
	var BaseHref="";				// BaseHref lets you specify the root directory for relative links. 
						// The script precedes your relative links with BaseHref
						// For instance: 
						// when your BaseHref= "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-bc.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-bc.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
						// Can also be used when you use images in the textfields of the menu
						// "MenuX=new Array("<img src=\""+BaseHref+"MyImage\">"
						// For testing on your harddisk use syntax like: BaseHref="file:///C|/MyFiles/Homepage/"


	var Arrws=['/shared/wow-com/images/subnav/tri.gif',14,15,'/shared/wow-com/images/subnav/arrow_right2.gif',18,12,'/shared/wow-com/images/subnav/arrow_right2.gif',5,10];	// Arrow source, width and height


						// Arrow source, width and height.
						// If arrow images are not needed keep source ""

	var MenuUsesFrames=0;			// MenuUsesFrames is only 0 when Main menu, submenus,
						// document targets and script are in the same frame.
						// In all other cases it must be 1

	var RememberStatus=0;			// RememberStatus: When set to 1, menu unfolds to the presetted menu item. 
						// When set to 2 only the relevant main item stays highligthed
						// The preset is done by setting a variable in the head section of the target document.
						// <head>
						//	<script type="text/javascript">var SetMenu="2_2_1";</script>
						// </head>
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
	var MenuOpacity="progid:DXImageTransform.Microsoft.Alpha(opacity=90)";

	function BeforeStart(){return}
	function AfterBuild(){return}
	function BeforeFirstOpen(){return}
	function AfterCloseAll(){return}


Menu1=new Array("Burning Crusade","/burningcrusade/index.html","/shared/wow-com/images/subnav/button_bg.gif",9,15,125,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu1_1=new Array(bulletImg+"Druid"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_1=new Array(bulletImg+"Druid Spells"+underLine,"/info/classes/bc-druid/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_2=new Array(bulletImg+"Druid Talents"+underLine,"/info/classes/bc-druid/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_2=new Array(bulletImg+"Hunter"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_1=new Array(bulletImg+"Hunter Spells"+underLine,"/info/classes/bc-hunter/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_2=new Array(bulletImg+"Hunter Talents"+underLine,"/info/classes/bc-hunter/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_3=new Array(bulletImg+"Mechanics"+underLine,"/info/classes/bc-hunter/changes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_3=new Array(bulletImg+"Mage"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1=new Array(bulletImg+"Mage Spells"+underLine,"/info/classes/bc-mage/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2=new Array(bulletImg+"Mage Talents"+underLine,"/info/classes/bc-mage/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_4=new Array(bulletImg+"Paladin"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_1=new Array(bulletImg+"Paladin Spells"+underLine,"/info/classes/bc-paladin/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2=new Array(bulletImg+"Paladin Talents"+underLine,"/info/classes/bc-paladin/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_5=new Array(bulletImg+"Priest"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_5_1=new Array(bulletImg+"Priest Spells"+underLine,"/info/classes/bc-priest/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_5_2=new Array(bulletImg+"Priest Talents"+underLine,"/info/classes/bc-priest/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_6=new Array(bulletImg+"Rogue"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_1=new Array(bulletImg+"Rogue Spells"+underLine,"/info/classes/bc-rogue/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_2=new Array(bulletImg+"Rogue Talents"+underLine,"/info/classes/bc-rogue/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");		
Menu1_7=new Array(bulletImg+"Shaman"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1=new Array(bulletImg+"Shaman Spells"+underLine,"/info/classes/bc-shaman/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2=new Array(bulletImg+"Shaman Talents"+underLine,"/info/classes/bc-shaman/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");		
Menu1_8=new Array(bulletImg+"Warlock"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1=new Array(bulletImg+"Warlock Spells"+underLine,"/info/classes/bc-warlock/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2=new Array(bulletImg+"Warlock Talents"+underLine,"/info/classes/bc-warlock/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");		
Menu1_9=new Array(bulletImg+"Warrior"+underLine,"/burningcrusade/townhall/talents-and-spells.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_1=new Array(bulletImg+"Warrior Spells"+underLine,"/info/classes/bc-warrior/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_2=new Array(bulletImg+"Warrior Talents"+underLine,"/info/classes/bc-warrior/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");		
