// awb512-119-u
	var linkClass="menuLink";//initial css style of links
	var menuNumber=6;
	var agt=navigator.userAgent.toLowerCase(), appVer = navigator.appVersion.toLowerCase(), iePos  = appVer.indexOf('msie'), is_opera = (agt.indexOf("opera") != -1), is_ie   = ((iePos!=-1) && (!is_opera));
	if(is_ie){
		var menuBg="";
		var menuBgIndent="";
		var underLine="<img src='/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-line.gif'/>";
		var bulletImg="<img src='/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-dot.gif' align='left'/>";
		var bulletImgIndent="<img src='/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-dot-indent.gif' align='left'/>";
	}else{
		var menuBg="/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-bg.gif";
		var menuBgIndent="/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-indent-bg.gif";
		var bulletImgIndent="<img src = /WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/layout/pixel.gif width=16 height=1/>";
		var underLine="";
		var bulletImg="";
	}
	var NoOffFirstLineMenus=6;			// Number of main menu  items
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

	var TargetLoc="menuForums";				// span id for relative positioning
	var MenuWrap=1;				// enables/ disables menu wrap 1 or 0
	var RightToLeft=0;				// enables/ disables right to left unfold 1 or 0
	var BottomUp=0;				// enables/ disables Bottom up unfold 1 or 0
	var UnfoldsOnClick=0;			// Level 1 unfolds onclick/ onmouseover
	var BaseHref="";				// BaseHref lets you specify the root directory for relative links. 
						// The script precedes your relative links with BaseHref
						// For instance: 
						// when your BaseHref= "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
						// Can also be used when you use images in the textfields of the menu
						// "MenuX=new Array(bulletImg+"<img src=\""+BaseHref+"MyImage\">"
						// For testing on your harddisk use syntax like: BaseHref="file:///C|/MyFiles/Homepage/"

	var Arrws=["/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/tri.gif",14,15,"/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/tri.gif",14,15,"/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/tri.gif",14,15,"/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/tri.gif",14,15];

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
Menu1=new Array(bulletImg+"General"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10001%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,14,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
  Menu1_1=new Array(bulletImg+"Arena Tournament"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D6304584&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_2=new Array(bulletImg+"Wrath of the Lich King"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D1793231&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_3=new Array(bulletImg+"Welcome to WoW"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3Fsid%3D1%26forumId%3D69356&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_4=new Array(bulletImg+"Player vs Player"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11117%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_5=new Array(bulletImg+"Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11118%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_6=new Array(bulletImg+"Raids and Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11126%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_7=new Array(bulletImg+"Professions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11116%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_8=new Array(bulletImg+"Roleplaying"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11125%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_9=new Array(bulletImg+"Suggestions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11122%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_10=new Array(bulletImg+"UI and Macros"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11114%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_11=new Array(bulletImg+"Off-Topic"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11121%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_12=new Array(bulletImg+"Strategy Guides"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3Fsid%3D1%26forumId%3D69355&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_13=new Array(bulletImg+"Trading Card Game"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fentertainment.upperdeck.com%2Fwow%2Fcommunity%2Fforums%2Fdefault.aspx&reason=external-or-uncollected-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
  Menu1_14=new Array(bulletImg+"StarCraft II"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D1793233&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu2=new Array(bulletImg+"Class Forums"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2F%23classes&reason=invalid-overlay-or-uncollected-site-resource",menuBg,9,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
  Menu2_1=new Array(bulletImg+"Druid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10015%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_2=new Array(bulletImg+"Hunter"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10016%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_3=new Array(bulletImg+"Mage"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10017%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_4=new Array(bulletImg+"Paladin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10018%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_5=new Array(bulletImg+"Priest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10019%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_6=new Array(bulletImg+"Rogue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10020%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_7=new Array(bulletImg+"Shaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10021%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_8=new Array(bulletImg+"Warlock"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10014%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu2_9=new Array(bulletImg+"Warrior"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10022%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3=new Array(bulletImg+"Realm Forums"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fchild-forum.html%3FforumId%3D11119%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,1,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
  Menu3_1=new Array(bulletImg+"Battlegroup Forums"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fchild-forum.html%3FforumId%3D69357&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4=new Array(bulletImg+"Guild Recruitment"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11123%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu5=new Array(bulletImg+"Guild Relations"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11124%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu6=new Array(bulletImg+"Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11110%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,7,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
  Menu6_1=new Array(bulletImg+"Technical Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11110%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu6_2=new Array(bulletImg+"Customer Service Forum"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11112&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu6_3=new Array(bulletImg+"Mac Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11111&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu6_4=new Array(bulletImg+"Realm Status"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11113&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu6_5=new Array(bulletImg+"Bug Reports"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10023&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu6_6=new Array(bulletImg+"PTR"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11572&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu6_7=new Array(bulletImg+"Blizzard Archive"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu6_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11120&reason=invalid-overlay-or-uncollected-site-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
