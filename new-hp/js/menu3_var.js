// awb512-119-u

	var linkClass="menuLink";//initial css style of links
	var menuNumber=3;

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
	
	var NoOffFirstLineMenus=16;			// Number of main menu  items
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

	var TargetLoc="menuGameGuide";				// span id for relative positioning
	var MenuWrap=1;				// enables/ disables menu wrap 1 or 0
	var RightToLeft=0;				// enables/ disables right to left unfold 1 or 0
	var BottomUp=0;				// enables/ disables Bottom up unfold 1 or 0
	var UnfoldsOnClick=0;			// Level 1 unfolds onclick/ onmouseover
	var BaseHref="";				// BaseHref lets you specify the root directory for relative links. 
						// The script precedes your relative links with BaseHref
						// For instance: 
						// when your BaseHref= "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
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
Menu1=new Array(bulletImg+"Game Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html",menuBg,5,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu1_1=new Array(bulletImg+"Archived News"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/archivednews.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_2=new Array(bulletImg+"Content Index"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/content-index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_3=new Array(bulletImg+"Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_4=new Array(bulletImg+"Report Errors"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/guide.html#errors",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu1_5=new Array(bulletImg+"General Links"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/general-links.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2=new Array(bulletImgIndent+"Introduction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#introduction",menuBgIndent,10,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu2_1=new Array(bulletImg+"Intro to WoW"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/beginners/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_2=new Array(bulletImg+"What is WoW"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guide.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu2_3=new Array(bulletImg+"Features"+underLine,"/WOW-Encyclopedia-Deployable-Archive/features/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_3_1=new Array(bulletImg+"WoW Classic"+underLine,"/WOW-Encyclopedia-Deployable-Archive/misc/features.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_3_2=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/burningcrusade/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_3_3=new Array(bulletImg+"Wrath of Lich King"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/features.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu2_4=new Array(bulletImg+"Look & Feel"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/beginners/index.html#lookAndFeel",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_5=new Array(bulletImg+"Story"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_6=new Array(bulletImg+"Awards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/misc/awards.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_7=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_8=new Array(bulletImg+"System Req."+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/technology.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
	Menu2_8_1=new Array(bulletImg+"Classic"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/technology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu2_8_2=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/faq.html#sys",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_9=new Array(bulletImg+"Free Trials"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/trial/index.html?referrer=WORLDOFWARCRAFT&source=wowhome&promo=1",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_10=new Array(bulletImg+"Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/classic-credits.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_10_1=new Array(bulletImg+"Classic Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/classic-credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu2_10_2=new Array(bulletImg+"BC Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bc-credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");



Menu3=new Array(bulletImgIndent+"Getting Started"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#gettingstarted",menuBgIndent,15,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu3_1=new Array(bulletImg+"Quick Start"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/gettingstarted.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_2=new Array(bulletImg+"Realm Types"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/realmtypes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_3=new Array(bulletImg+"First Few Levels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/firstfewlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_4=new Array(bulletImg+"Character Info"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/characters.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_5=new Array(bulletImg+"Character Titles"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/titles.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6=new Array(bulletImg+"Controls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/controls.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_1=new Array(bulletImg+"Voice Chat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/voicechat.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_2=new Array(bulletImg+"Chat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_2_1=new Array(bulletImg+"Overview"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-overview.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_2_2=new Array(bulletImg+"Customization"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-customization.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_2_3=new Array(bulletImg+"Other"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-other.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_2_4=new Array(bulletImg+"Q&A"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-qna.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_2_5=new Array(bulletImg+"Command Glossary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-commandglossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_3=new Array(bulletImg+"Emotes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/emotes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_4=new Array(bulletImg+"Dancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_5=new Array(bulletImg+"Macros"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/macros.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu3_6_5_1=new Array(bulletImg+"Macro Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/macroguide-one.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_6_6=new Array(bulletImg+"Slash Commands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/slashcommands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_7=new Array(bulletImg+"Combat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/combat.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_7_1=new Array(bulletImg+"Death System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/death.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_7_2=new Array(bulletImg+"Duels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/duels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_7_3=new Array(bulletImg+"Resistances"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/resistances.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_7_4=new Array(bulletImg+"Spells & Abilities"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_8=new Array(bulletImg+"Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/quests.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_8_1=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/questbasics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_8_2=new Array(bulletImg+"Levels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/questlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_8_3=new Array(bulletImg+"Management"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/questmanagement.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_8_4=new Array(bulletImg+"Daily Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/dailyquests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_9=new Array(bulletImg+"Combat Pets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/combatpets.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_10=new Array(bulletImg+"Small Pets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/smallpets.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_11=new Array(bulletImg+"Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_12=new Array(bulletImg+"Monster Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/monsterbasics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_13=new Array(bulletImg+"NPCs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/npcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_14=new Array(bulletImg+"Rest System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/resting.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu3_15=new Array(bulletImg+"Glossary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/glossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu4=new Array(bulletImgIndent+"Character"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#character",menuBgIndent,8,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu4_1=new Array(bulletImg+"Character Info"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/characters.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_2=new Array(bulletImg+"Character Titles"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/titles.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3=new Array(bulletImg+"Races"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/index.html",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_1=new Array(bulletImg+"Draenei"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/draenei.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_2=new Array(bulletImg+"Dwarves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dwarves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_3=new Array(bulletImg+"Gnomes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/gnomes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_4=new Array(bulletImg+"Humans"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/humans.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_5=new Array(bulletImg+"Night Elves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/nightelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_6=new Array(bulletImg+"Blood Elves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/bloodelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_7=new Array(bulletImg+"Orcs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/orcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_8=new Array(bulletImg+"Tauren"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/tauren.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_9=new Array(bulletImg+"Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/trolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_3_10=new Array(bulletImg+"Undead"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/undead.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu4_4=new Array(bulletImg+"Classes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/index.html",menuBg,11,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_1=new Array(bulletImg+"Druid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/index.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_1_1=new Array(bulletImg+"Druid Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_1_2=new Array(bulletImg+"Druid Shapeshifting"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/shapeshifting.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_1_3=new Array(bulletImg+"Druid Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_1_4=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_2=new Array(bulletImg+"Hunter"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/index.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_2_1=new Array(bulletImg+"Hunter Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_2_2=new Array(bulletImg+"Hunter Pets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/pets.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_2_3=new Array(bulletImg+"Hunter Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_2_4=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_3=new Array(bulletImg+"Mage"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_3_1=new Array(bulletImg+"Mage Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_3_2=new Array(bulletImg+"Mage Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_3_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_4=new Array(bulletImg+"Paladin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_4_1=new Array(bulletImg+"Paladin Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_4_2=new Array(bulletImg+"Paladin Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_4_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_5=new Array(bulletImg+"Priest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_5_1=new Array(bulletImg+"Priest Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_5_2=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_6=new Array(bulletImg+"Rogue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_6_1=new Array(bulletImg+"Rogue Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_6_2=new Array(bulletImg+"Rogue Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_6_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_7=new Array(bulletImg+"Shaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/index.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_7_1=new Array(bulletImg+"Shaman Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_7_2=new Array(bulletImg+"Shaman Totems"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/totems.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_7_3=new Array(bulletImg+"Shaman Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_7_4=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_8=new Array(bulletImg+"Warlock"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_8_1=new Array(bulletImg+"Warlock Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_8_2=new Array(bulletImg+"Warlock Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_8_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_9=new Array(bulletImg+"Warrior"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_9_1=new Array(bulletImg+"Warrior Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_9_2=new Array(bulletImg+"Warrior Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_9_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/talent-index/index.html","",9,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_1=new Array(bulletImg+"Druid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_2=new Array(bulletImg+"Hunter"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_3=new Array(bulletImg+"Mage"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_4=new Array(bulletImg+"Paladin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_5=new Array(bulletImg+"Priest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_6=new Array(bulletImg+"Rogue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_7=new Array(bulletImg+"Shaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_8=new Array(bulletImg+"Warlock"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_10_9=new Array(bulletImg+"Warrior"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_4_11=new Array(bulletImg+"Class Guides"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/classlinks.html","",0,15,125,"","","","","","",-1,-1,-1,"","");

Menu4_5=new Array(bulletImg+"Professions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/index.html",menuBg,16,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_1=new Array(bulletImg+"Introduction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/intro.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_2=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_3=new Array(bulletImg+"Alchemy"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/alchemy.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_4=new Array(bulletImg+"Blacksmithing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/blacksmithing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_5=new Array(bulletImg+"Cooking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/cooking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_6=new Array(bulletImg+"Enchanting"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/enchanting.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_7=new Array(bulletImg+"Engineering"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/engineering.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_8=new Array(bulletImg+"First Aid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/firstaid.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_9=new Array(bulletImg+"Fishing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/fishing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_10=new Array(bulletImg+"Herbalism"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/herbalism.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_11=new Array(bulletImg+"Leatherworking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/leatherworking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_12=new Array(bulletImg+"Mining"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/mining.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_13=new Array(bulletImg+"Skinning"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/skinning.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_14=new Array(bulletImg+"Tailoring"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/tailoring.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_15=new Array(bulletImg+"Jewelcrafting"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/jewelcrafting.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_15_1=new Array(bulletImg+"Socketed Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/socketeditems.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_5_16=new Array(bulletImg+"Profession Links"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/professionlinks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu4_6=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/talent-index/index.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu4_6_1=new Array(bulletImg+"Talent Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_7=new Array(bulletImg+"Dancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu4_8=new Array(bulletImg+"High-End Content"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/highleveloptions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu5=new Array(bulletImgIndent+"Reputations"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/reputation.html",menuBgIndent,4,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu5_1=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/reputation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_2=new Array(bulletImg+"Classic"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/index.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_2_1=new Array(bulletImg+"Argent Dawn"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/argent/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_2_2=new Array(bulletImg+"Brood of Nozdormu"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/broodofnozdormu/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_2_3=new Array(bulletImg+"Cenarion Circle"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/cenarion/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_2_4=new Array(bulletImg+"Darkmoon Faire"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu5_2_4_1=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/rewards.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu5_2_4_2=new Array(bulletImg+"Fortune Teller"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/buffs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_2_5=new Array(bulletImg+"Thorium Brotherhood"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/thorium/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_2_6=new Array(bulletImg+"Timbermaw Hold"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/timbermaw/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_2_7=new Array(bulletImg+"Zandalar Tribe"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zandalar/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu5_2_7_1=new Array(bulletImg+"Vendor Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zandalar/vendor.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu5_2_7_2=new Array(bulletImg+"Class Quest Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zandalar/quests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_3=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/reputation.html#BC",menuBg,22,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_1=new Array(bulletImg+"Hellfire Peninsula"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/hellfire/hellfire.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");					    Menu5_3_2=new Array(bulletImg+"Hellfire PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/hellfire/hellfire-tokens.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_3=new Array(bulletImg+"Cenarion Expedition"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/cenarionxp/cenarionxp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_4=new Array(bulletImg+"Sporeggar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/sporeggar/sporeggar.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_5=new Array(bulletImg+"Zangarmarsh PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zangarmarsh/zangarpvp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_6=new Array(bulletImg+"Aldor/Scryers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/aldorscryers/aldor-scryers.xml.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_6_1=new Array(bulletImg+"Inscriptions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_7=new Array(bulletImg+"Lower City"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/lowercity/lowercity.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_8=new Array(bulletImg+"The Consortium"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/consortium/consortium.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_9=new Array(bulletImg+"Bone Wastes PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/bonewastes/bonewastes.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_10=new Array(bulletImg+"The Sha'Tar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/shatar/shatar.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_11=new Array(bulletImg+"Keepers of Time"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/keepers/keepers.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_12=new Array(bulletImg+"Scale of Sands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/keepers/scale.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_13=new Array(bulletImg+"Nagrand"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/nagrand/nagrand.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_14=new Array(bulletImg+"Halaa PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/halaa/halaa.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_15=new Array(bulletImg+"The Violet Eye"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/violeteye/violeteye.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_16=new Array(bulletImg+"Violet Eye Rings"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/violeteye/violeteyerings.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_17=new Array(bulletImg+"Ogri'la"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1038%26searchType%3Ditems&reason=external-or-uncollected-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_17_1=new Array(bulletImg+"Ogri'la"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/ogrila-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_18=new Array(bulletImg+"Sha'tari Skyguard"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1031%26searchType%3Ditems&reason=external-or-uncollected-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu5_3_18_1=new Array(bulletImg+"Skyguard Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/skyguard-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_19=new Array(bulletImg+"Netherwing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1015%26searchType%3Ditems&reason=external-or-uncollected-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu5_3_19_1=new Array(bulletImg+"Netherwing Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/netherwing-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_20=new Array(bulletImg+"Ashtongue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1012%26searchType%3Ditems&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_21=new Array(bulletImg+"Badges of Justice"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/badgesofjustice/badges-of-justice.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu5_3_22=new Array(bulletImg+"Badges of Justice 2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/badgesofjustice/badges-of-justice2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu5_4=new Array(bulletImg+"Armory Listing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Ffactions.xml&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
	
Menu6=new Array(bulletImgIndent+"Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#items",menuBgIndent,14,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu6_1=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_2=new Array(bulletImg+"Item Database"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fitem-search.xml&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_3=new Array(bulletImg+"Item Management"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/management.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_4=new Array(bulletImg+"Bags"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bags.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_5=new Array(bulletImg+"Socketed Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/socketeditems.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_6=new Array(bulletImg+"Banking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/banking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_7=new Array(bulletImg+"Dressing Room"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/dressingroom/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_8=new Array(bulletImg+"Merchants"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/merchants.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_9=new Array(bulletImg+"Mail"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mail.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_10=new Array(bulletImg+"Trading"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/trading.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_10_1=new Array(bulletImg+"Auction Houses"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/auctionhouses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_10_2=new Array(bulletImg+"Auction House Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/auctionhousetips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_10_3=new Array(bulletImg+"Chat Auctions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chatauctions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_11=new Array(bulletImg+"Food/Drink"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/food.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_12=new Array(bulletImg+"High Level Armor Sets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/armorsets/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_13=new Array(bulletImg+"Badges of Justice"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/badgesofjustice/badges-of-justice.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu6_14=new Array(bulletImg+"Badges of Justice 2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/badgesofjustice/badges-of-justice2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");


Menu7=new Array(bulletImgIndent+"The World"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#world",menuBgIndent,6,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu7_1=new Array(bulletImg+"World Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/flashmap/index.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_1_1=new Array(bulletImg+"Outland Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/outlandmap.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_2=new Array(bulletImg+"Exploring the Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/map.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_3=new Array(bulletImg+"Region Levels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/regionlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4=new Array(bulletImg+"Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/dungeons.html",menuBg,8,15,125,"","","","","","",-1,-1,-1,"","");

Menu7_4_1=new Array(bulletImg+"Instancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/instancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_2=new Array(bulletImg+"Dungeon Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/dungeontips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu7_4_3=new Array(bulletImg+"Classic Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html",menuBg,19,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_1=new Array(bulletImg+"Blackfathom Depths"+underLine,"/info/basics/worlddungeons.html#Blackfathom Depths",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_2=new Array(bulletImg+"Blackrock Depths"+underLine,"/info/basics/worlddungeons.html#Blackrock Depths",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_3=new Array(bulletImg+"Blackrock Spire"+underLine,"/info/basics/worlddungeons.html#Blackrock Spire",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_4=new Array(bulletImg+"Deadmines"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Deadmines",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_5=new Array(bulletImg+"Dire Maul"+underLine,"/info/basics/worlddungeons.html#Dire Maul",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_6=new Array(bulletImg+"Gnomeregan"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Gnomeregan",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_7=new Array(bulletImg+"Maraudon"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Maraudon",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_8=new Array(bulletImg+"Ragefire Chasm"+underLine,"/info/basics/worlddungeons.html#Ragefire Chasm",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_9=new Array(bulletImg+"Razorfen Downs"+underLine,"/info/basics/worlddungeons.html#Razorfen Downs",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_10=new Array(bulletImg+"Razorfen Kraul"+underLine,"/info/basics/worlddungeons.html#Razorfen Kraul",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_11=new Array(bulletImg+"Scholomance"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Scholomance","",0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_12=new Array(bulletImg+"Shadowfang Keep"+underLine,"/info/basics/worlddungeons.html#Shadowfang Keep",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_13=new Array(bulletImg+"Stratholme"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Stratholme",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_14=new Array(bulletImg+"Scarlet Monastery"+underLine,"/info/basics/worlddungeons.html#The Scarlet Monastery",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_15=new Array(bulletImg+"The Stockades"+underLine,"/info/basics/worlddungeons.html#The Stockades",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_16=new Array(bulletImg+"The Sunken Temple"+underLine,"/info/basics/worlddungeons.html#The Sunken Temple",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_17=new Array(bulletImg+"Uldaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Uldaman",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_18=new Array(bulletImg+"Wailing Caverns"+underLine,"/info/basics/worlddungeons.html#Wailing Caverns",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_3_19=new Array(bulletImg+"Zul'Farrak"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#ZulFarrak",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");


Menu7_4_4=new Array(bulletImg+"AQ War Effor Rankings"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_5=new Array(bulletImg+"Raid Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/calendar/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu7_4_6=new Array(bulletImg+"Classic Raid Areas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html",menuBg,8,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_1=new Array(bulletImg+"Raid Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/calendar/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_2=new Array(bulletImg+"Blackwing Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#bwl",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_3=new Array(bulletImg+"Molten Core"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#mc",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_4=new Array(bulletImg+"Onyxia's Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#onx",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_5=new Array(bulletImg+"Zul'Gurub"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#ZG",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_6=new Array(bulletImg+"Ahn'Qiraj"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#aq20",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_6_1=new Array(bulletImg+"AQ Ranking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_6_2=new Array(bulletImg+"AQ Server Stats"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/wareffort.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_7=new Array(bulletImg+"Naxxramas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#naxx",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_6_8=new Array(bulletImg+"Outdoor"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#outdoor",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");


Menu7_4_7=new Array(bulletImg+"BC Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bcworlddungeons.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_7_1=new Array(bulletImg+"Hellfire Citadel"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/hellfire-citadel.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_7_2=new Array(bulletImg+"Coilfang Reservoir"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/coilfang-reservoir.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_7_3=new Array(bulletImg+"Auchindoun"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/auchindoun.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_7_4=new Array(bulletImg+"Caverns of Time"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/caverns-of-time.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_7_5=new Array(bulletImg+"Tempest Keep"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tempest-keep.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_7_6=new Array(bulletImg+"Karazhan"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/karazhan.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_7_7=new Array(bulletImg+"Zul'Aman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/zulaman.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu7_4_8=new Array(bulletImg+"BC Raid Areas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bcraidarea.html",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_1=new Array(bulletImg+"Raid Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/calendar/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_2=new Array(bulletImg+"Karazhan"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/karazhan.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_3=new Array(bulletImg+"Zul'Aman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/zulaman.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_4=new Array(bulletImg+"Magtheridon's Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/hellfire-citadel.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_5=new Array(bulletImg+"Serpentshrine Cavern"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/coilfang-reservoir.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_6=new Array(bulletImg+"Tempest Keep"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tempest-keep.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_7=new Array(bulletImg+"Gruul's Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/gruuls-lair.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_8=new Array(bulletImg+"The Battle for Mount Hyjal"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/caverns-of-time.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_9=new Array(bulletImg+"Doom Lord Kazzak"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/doom-lord-kazzak.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_4_8_10=new Array(bulletImg+"Doomwalker"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/doomwalker.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu7_5=new Array(bulletImg+"Major Cities"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_5_1=new Array(bulletImg+"Darnassus"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#darnassus",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_5_2=new Array(bulletImg+"Ironforge"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#ironforge",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_5_3=new Array(bulletImg+"Orgrimmar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#orgrimmar",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_5_4=new Array(bulletImg+"Stormwind"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#stormwind",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_5_5=new Array(bulletImg+"Thunder Bluff"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#thunderbluff",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_5_6=new Array(bulletImg+"Undercity"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#undercity",menuBg,0,17,125,"","","","","","",-1,-1,-1,"","");

Menu7_6=new Array(bulletImg+"In-Game Events"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html",menuBg,19,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_1=new Array(bulletImg+"Events Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/calendar/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_2=new Array(bulletImg+"New Year's Eve"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/newyears/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_3=new Array(bulletImg+"Lunar Festival"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/lunarnewyears/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_4=new Array(bulletImg+"Love is in the Air"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_5=new Array(bulletImg+"Noblegarden"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#noblegarden",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_6=new Array(bulletImg+"Children's Week"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/childrensweek/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_7=new Array(bulletImg+"Midsummer Fire Festival"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/midsummer/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_8=new Array(bulletImg+"Harvest Festival"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/harvestfestival/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_9=new Array(bulletImg+"Brewfest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/brewfest/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_10=new Array(bulletImg+"Hallow's End"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/hallowsend/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_11=new Array(bulletImg+"Winter Veil"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/winterveil/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_12=new Array(bulletImg+"AQ War Effort"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_13=new Array(bulletImg+"Battlegrounds Holiday"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#calltoarms",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_14=new Array(bulletImg+"Darkmoon Faire Event"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_15=new Array(bulletImg+"Elemental Invasions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#elemental",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_16=new Array(bulletImg+"Fishing Extravaganza"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/fishing/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_17=new Array(bulletImg+"Gurubashi Arena"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#gurubashi",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_18=new Array(bulletImg+"The Scourge Invasion"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/scourgeinvasion/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu7_6_19=new Array(bulletImg+"Brewfest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/brewfest/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu8=new Array(bulletImgIndent+"Transportation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#transportation",menuBgIndent,3,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu8_1=new Array(bulletImg+"Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/index.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1=new Array(bulletImg+"Racial Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/index.html#racial",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_1=new Array(bulletImg+"Horses"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/horses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_2=new Array(bulletImg+"Kodos"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/kodos.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_3=new Array(bulletImg+"Mechanostriders"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/mechanostriders.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_4=new Array(bulletImg+"Nightsabers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/nightsabers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_5=new Array(bulletImg+"Rams"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/rams.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_6=new Array(bulletImg+"Raptors"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/raptors.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_7=new Array(bulletImg+"Skeletal Horses"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/skeletalhorses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_8=new Array(bulletImg+"Wolves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/wolves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_9=new Array(bulletImg+"Elekks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/elekks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_1_10=new Array(bulletImg+"Hawkstriders"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/hawkstriders.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_2=new Array(bulletImg+"Class Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/index.html#class",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
	Menu8_1_2_1=new Array(bulletImg+"Paladin Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/paladin.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu8_1_2_2=new Array(bulletImg+"Warlock Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/warlock.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_3=new Array(bulletImg+"Alterac Valley Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#av",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_4=new Array(bulletImg+"PvP Reward Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#pvp",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_5=new Array(bulletImg+"Talbuks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_6=new Array(bulletImg+"Special Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#misc",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_1_7=new Array(bulletImg+"Flying Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/flying.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu8_2=new Array(bulletImg+"Public Transportation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_2_1=new Array(bulletImg+"Gryphons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#gryphons",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_2_2=new Array(bulletImg+"Hippogryphs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#hippogryphs",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_2_3=new Array(bulletImg+"Deeprun Tram"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#deepruntram",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_2_4=new Array(bulletImg+"Wyverns"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#wyverns",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_2_5=new Array(bulletImg+"Vampire Bats"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#bats",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_2_6=new Array(bulletImg+"Goblin Zeppelin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#zeppelin",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_2_7=new Array(bulletImg+"Boats"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#boats",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu8_3=new Array(bulletImg+"Transportation FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/transportation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9=new Array(bulletImgIndent+"Player Interaction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#playerinteraction",menuBgIndent,4,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu9_1=new Array(bulletImg+"Guilds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guilds.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_1_1=new Array(bulletImg+"Joining Guilds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/joiningguilds.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_1_2=new Array(bulletImg+"Guild Management"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guildtab.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_1_3=new Array(bulletImg+"Guild Leadership"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guildleadership.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_1_4=new Array(bulletImg+"Guild Banks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guildbanks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu9_2=new Array(bulletImg+"Parties/Raids"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/parties.html",menuBg,9,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_1=new Array(bulletImg+"Roles"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partyroles.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_2=new Array(bulletImg+"Find a Party"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partygrouping.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_3=new Array(bulletImg+"Looking for Group"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/lookingforgroup.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_4=new Array(bulletImg+"Etiquette"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partyrules.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_5=new Array(bulletImg+"Party Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partytips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_6=new Array(bulletImg+"Pulling"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partiespulling.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_7=new Array(bulletImg+"Crowd Control"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partycrowdcontrol.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_8=new Array(bulletImg+"Raid Groups"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidgroups.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_2_9=new Array(bulletImg+"Raid Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidtips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu9_3=new Array(bulletImg+"How to Be Nice"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/benice.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4=new Array(bulletImg+"Controls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/controls.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_1=new Array(bulletImg+"Chat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_1_1=new Array(bulletImg+"Overview"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-overview.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_1_2=new Array(bulletImg+"Customization"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-customization.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_1_3=new Array(bulletImg+"Other"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-other.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_1_4=new Array(bulletImg+"Q&A"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-qna.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_1_5=new Array(bulletImg+"Command Glossary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-commandglossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_2=new Array(bulletImg+"Emotes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/emotes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_3=new Array(bulletImg+"Dancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_4=new Array(bulletImg+"Macros"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/macros.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_4_1=new Array(bulletImg+"Macro Guide I"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/macroguide-one.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu9_4_5=new Array(bulletImg+"Slash Commands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/slashcommands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu10=new Array(bulletImgIndent+"Player vs Player"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/index.html",menuBgIndent,11,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu10_1=new Array(bulletImg+"Arena"+underLine,"/WOW-Encyclopedia-Deployable-Archive/misc/arenatournament/index.xml.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
 Menu10_1_1=new Array(bulletImg+"Arena Tournament"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Farena-tournament.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu10_1_2=new Array(bulletImg+"Arena Intro"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/arena/index.xml.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu10_1_3=new Array(bulletImg+"Inside Arenas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/insider/11/arena.xml.html ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu10_1_4=new Array(bulletImg+"Item Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fpvprewards.xml&reason=external-or-uncollected-resource ",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_2=new Array(bulletImg+"Honor System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honorguide.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_2_1=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honor-system-faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_2_2=new Array(bulletImg+"Ranks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/ranks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_3=new Array(bulletImg+"Honor vs. Arena"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honorvsarena.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_4=new Array(bulletImg+"PvP Combat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/pvpcombat.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_5=new Array(bulletImg+"Surviving PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/survivingpvp.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_6=new Array(bulletImg+"Battlegrounds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/index.html",menuBg,8,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_1=new Array(bulletImg+"General Info"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_2=new Array(bulletImg+"Queue System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/battlegrounds-queue-system.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_3=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_4=new Array(bulletImg+"Alterac Valley"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info-alteracvalley.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_4_1=new Array(bulletImg+"Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/quests-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_4_2=new Array(bulletImg+"Enemies"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/enemies-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_4_3=new Array(bulletImg+"Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/map-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_4_4=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/alterac/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_4_5=new Array(bulletImg+"Score Screen"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/scores-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_4_6=new Array(bulletImg+"Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/tips-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_5=new Array(bulletImg+"Arathi Basin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info-arathi.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_5_1=new Array(bulletImg+"Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/map-arathi.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_5_2=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/arathi/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_5_3=new Array(bulletImg+"Score Screen"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/scores-arathi.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_6=new Array(bulletImg+"Warsong Gulch"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info-warsong.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_6_1=new Array(bulletImg+"Power-Ups"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/powerups-warsong.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_6_2=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/warsong/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu10_6_6_3=new Array(bulletImg+"Score Screen"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/scores-warsong.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_7=new Array(bulletImg+"Eye of the Storm"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/eyeofthestorm/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_6_8=new Array(bulletImg+"Cross-Realm BGs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/battlegroups/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_7=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fpvprewards.xml&reason=external-or-uncollected-resource",menuBg,14,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_1=new Array(bulletImg+"Armory Listing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fpvprewards.xml&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
	Menu10_7_2=new Array(bulletImg+"General Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/rewards-general.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_3=new Array(bulletImg+"Rare Class Armor"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/rewards-class-armor.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_4=new Array(bulletImg+"Vindicator's Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/rewards-vindicators-armor.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_5=new Array(bulletImg+"Weapons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/rewards-weapons.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_6=new Array(bulletImg+"Armor Sets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/armorsets/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_7=new Array(bulletImg+"Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#pvp",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_8=new Array(bulletImg+"Alterac V. Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/alterac/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_9=new Array(bulletImg+"Arathi Basin Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/arathi/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_10=new Array(bulletImg+"Warsong Gulch Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/warsong/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_11=new Array(bulletImg+"Hellfire PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/hellfire/hellfire-tokens.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_12=new Array(bulletImg+"Zangarmarsh PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zangarmarsh/zangarpvp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu10_7_13=new Array(bulletImg+"Bone Wastes PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/bonewastes/bonewastes.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu10_7_14=new Array(bulletImg+"Halaa PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/halaa/halaa.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu10_8=new Array(bulletImg+"Horde vs. Alli. FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/hordevalliance.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu10_9=new Array(bulletImg+"Azeroth Outdoor PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/outdoorpvp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"",""); 
Menu10_10=new Array(bulletImg+"Outland Outdoor PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"",""); 
Menu10_11=new Array(bulletImg+"Halaa PvP Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/halaa-tips.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"",""); 

Menu11=new Array(bulletImgIndent+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/index.html",menuBgIndent,29,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu11_1=new Array(bulletImg+"General FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/general.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_2=new Array(bulletImg+"Battlegrounds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_3=new Array(bulletImg+"Blizzard Downloader"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/blizzarddownloader.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_4=new Array(bulletImg+"Character"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/characters.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_5=new Array(bulletImg+"Classes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/classes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_6=new Array(bulletImg+"Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/dungeons.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_7=new Array(bulletImg+"Gameplay"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/gameplay.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_8=new Array(bulletImg+"Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/guide.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_9=new Array(bulletImg+"Honor System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honor-system-faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_10=new Array(bulletImg+"Horde vs Alliance"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/hordevalliance.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_11=new Array(bulletImg+"Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/items.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_12=new Array(bulletImg+"NPCs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/npcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_13=new Array(bulletImg+"Paid Char Transfer"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fus.blizzard.com%2Fsupport%2Farticle.xml%3FarticleId%3D20558&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_14=new Array(bulletImg+"Parental Controls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/parentalcontrols.xml.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu11_14_1=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fus.blizzard.com%2Fsupport%2Farticle.xml%3FarticleId%3D20484&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_15=new Array(bulletImg+"Patches"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/patches.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_16=new Array(bulletImg+"PTR"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/ptr.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_17=new Array(bulletImg+"Recruit-A-Friend"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fus.blizzard.com%2Fsupport%2Farticle.xml%3FarticleId%3D20588&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_18=new Array(bulletImg+"Scroll of Resur."+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fus.blizzard.com%2Fsupport%2Farticle.xml%3FarticleId%3D20592&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_19=new Array(bulletImg+"Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/quests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_20=new Array(bulletImg+"Races"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/races.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_21=new Array(bulletImg+"Realms"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/realms.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_22=new Array(bulletImg+"Skills"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/skills.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_23=new Array(bulletImg+"Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_24=new Array(bulletImg+"Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/support.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_25=new Array(bulletImg+"Technology"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/technology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_26=new Array(bulletImg+"Transportation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/transportation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_27=new Array(bulletImg+"World"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/world.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_28=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu11_29=new Array(bulletImg+"Wrath"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/faq.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu12=new Array(bulletImgIndent+"Story"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/index.html",menuBgIndent,4,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu12_1=new Array(bulletImg+"Encyclopedia"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/encyclopedia/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_2=new Array(bulletImg+"Timeline"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/timeline.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_3=new Array(bulletImg+"History"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/index.html#history",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_3_1=new Array(bulletImg+"Chapter 1"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter1.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_3_2=new Array(bulletImg+"Chapter 2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_3_3=new Array(bulletImg+"Chapter 3"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter3.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_3_4=new Array(bulletImg+"Chapter 4"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter4.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_3_5=new Array(bulletImg+"Chapter 5"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter5.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_3_6=new Array(bulletImg+"Chapter 6"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter6.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu12_4=new Array(bulletImg+"Lore"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/index.html#lore",menuBg,9,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_1=new Array(bulletImg+"The Murlocs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/misc/murloclore/murlocs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_2=new Array(bulletImg+"Road to Damnation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/1p11/roadtodamnation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_3=new Array(bulletImg+"War of Shifting Sands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/shiftingsands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_4=new Array(bulletImg+"Troll Compendium"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/index.html",menuBg,13,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_1=new Array(bulletImg+"History 1"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/history.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_2=new Array(bulletImg+"History 2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/history2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_3=new Array(bulletImg+"Biology"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/biology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_4=new Array(bulletImg+"Trivia"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/trollsandnightelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_5=new Array(bulletImg+"Forest Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/foresttrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_6=new Array(bulletImg+"Forest Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/foresttribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_7=new Array(bulletImg+"Jungle Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/jungletrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_8=new Array(bulletImg+"Jungle Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/jungletribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_9=new Array(bulletImg+"Ice Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/icetrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_10=new Array(bulletImg+"Ice Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/icetribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_11=new Array(bulletImg+"Sand Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/sandtrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_12=new Array(bulletImg+"Sand Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/sandtribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu12_4_4_13=new Array(bulletImg+"Other Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/othertrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_5=new Array(bulletImg+"Undead Plague"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/undeadplague.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_6=new Array(bulletImg+"The Story So Far"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/story.html#top",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_7=new Array(bulletImg+"Shaman/Paladins"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/classcombo.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_8=new Array(bulletImg+"Unbroken"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/unbroken/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
Menu12_4_9=new Array(bulletImg+"Rise of Lich King"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/unbroken/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu13=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/index.html",menuBg,5,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu13_1=new Array(bulletImg+"Features"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/burningcrusade/index.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu13_2=new Array(bulletImg+"Townhall"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/index.html",menuBg,10,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_1=new Array(bulletImg+"Professions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/professions.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_2=new Array(bulletImg+"Silvermoon City"+underLine,"/WOW-Encyclopedia-Deployable-Archive/insider/10/silvermoon.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_3=new Array(bulletImg+"The Story So Far"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/story.html#top",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_4=new Array(bulletImg+"Caverns of Time"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/cavernsoftime.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_5=new Array(bulletImg+"Hellfire Citadel"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/hellfirecitadel.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_6=new Array(bulletImg+"Karazhan"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/karazhan.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_7=new Array(bulletImg+"Shaman/Paladins"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/classcombo.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_8=new Array(bulletImg+"Nether Drakes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/netherdrake.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_9=new Array(bulletImg+"Jewelcrafting"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/jewelcrafting.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_2_10=new Array(bulletImg+"Beastiary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/bestiary.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu13_3=new Array(bulletImg+"Media"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/index.html",menuBg,4,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_3_1=new Array(bulletImg+"Screenshots"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/screenshots.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_3_2=new Array(bulletImg+"Artwork"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/artwork.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_3_3=new Array(bulletImg+"Wallpapers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/wallpapers.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu13_3_4=new Array(bulletImg+"Movies"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/movies.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu13_4=new Array(bulletImg+"Flash Mini-site"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fmedia.worldofwarcraft.com%2Fbc-minisite%2Findex.htm&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu13_5=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/faq.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");

Menu14=new Array(bulletImg+"Wrath of Lich King"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/index.html",menuBg,3,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu14_1=new Array(bulletImg+"Features"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/features.xml.html",menuBg,3,15,140,"","","","","","",-1,-1,-1,"","");
	Menu14_1_1=new Array(bulletImg+"Rise of Lich King"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/features/story/story.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu14_1_2=new Array(bulletImg+"Borean Tundra"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/features/northrend/borean-tundra.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu14_1_3=new Array(bulletImg+"Howling Fjord"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/features/northrend/howling-fjord.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu14_2=new Array(bulletImg+"Media"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/index.html",menuBg,4,15,140,"","","","","","",-1,-1,-1,"","");
	Menu14_2_1=new Array(bulletImg+"Screenshots"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/screenshots.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu14_2_2=new Array(bulletImg+"Artwork"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/artwork.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu14_2_3=new Array(bulletImg+"Wallpapers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/wallpapers.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
	Menu14_2_4=new Array(bulletImg+"Movies"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/movies.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu14_3=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/faq.xml.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");

Menu15=new Array(bulletImg+"Under Development"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/index.html",menuBg,4,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
Menu15_1=new Array(bulletImg+"Public Test Realm"+underLine,"/WOW-Encyclopedia-Deployable-Archive/ptr/index.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu15_2=new Array(bulletImg+"PTR FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/ptr.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu15_3=new Array(bulletImg+"PTR Forum"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnew-hp%2Fjs%2Fmenu3_var.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11572&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");
Menu15_4=new Array(bulletImg+"PTR Patch Notes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/patchnotes/test-realm-patchnotes.html",menuBg,0,15,140,"","","","","","",-1,-1,-1,"","");

Menu16=new Array(bulletImgIndent+"Previous Patches"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/index.html",menuBgIndent,16,15,140,"transparent","","","","transparent","",-1,-1,-1,"","");
	Menu16_1=new Array(bulletImg+"Patch 2.4.0"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/2p4.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_2=new Array(bulletImg+"Patch 2.3.0"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/2p3.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_3=new Array(bulletImg+"Patch 2.2.0"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/2p2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_4=new Array(bulletImg+"Patch 2.1.0"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/2p1.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_5=new Array(bulletImg+"Patch 2.0.1"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/2p01.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_6=new Array(bulletImg+"Patch 1.12"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p12.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_7=new Array(bulletImg+"Patch 1.11"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p11.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_8=new Array(bulletImg+"Patch 1.10"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p10.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_9=new Array(bulletImg+"Patch 1.9"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p9.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_10=new Array(bulletImg+"Patch 1.8"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p8.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_11=new Array(bulletImg+"Patch 1.7"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p7.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_12=new Array(bulletImg+"Patch 1.6"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p6.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_13=new Array(bulletImg+"Patch 1.5"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p5.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_14=new Array(bulletImg+"Patch 1.4"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p4.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_15=new Array(bulletImg+"Patch 1.3"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/implemented/1p3.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu16_16=new Array(bulletImg+"Patch 1.2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/patchnotes/patch-12-18-04.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 