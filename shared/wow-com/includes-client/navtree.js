// awb512-119-u
	var linkClass="subMenuLink";
	var menuNumber=9;
	var agt=navigator.userAgent.toLowerCase(), appVer = navigator.appVersion.toLowerCase(), iePos  = appVer.indexOf('msie'), is_opera = (agt.indexOf("opera") != -1), is_ie   = ((iePos!=-1) && (!is_opera));
	if(is_ie){
		var menuBg="";
		var menuBgIndent="";
		var underLine="<img src=/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-line-blue.gif />";
		var bulletImg="<img src=/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-dot-blue.gif align=left />";
		var bulletImgIndent="<img src=/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-dot-indent.gif align=left />";
	}else{
		var menuBg="/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-bg-blue.gif";
		var menuBgIndent="/WOW-Encyclopedia-Deployable-Archive/new-hp/images/menu/mainmenu/bullet-trans-indent-bg.gif";
		var bulletImgIndent="<img src = /WOW-Encyclopedia-Deployable-Archive/images/layout/pixel.gif width=16 height=1 />";
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
						// when your BaseHref= "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
						// Can also be used when you use images in the textfields of the menu
						// "MenuX=new Array("<img src=\""+BaseHref+"MyImage\">"
						// For testing on your harddisk use syntax like: BaseHref="file:///C|/MyFiles/Homepage/"


	var Arrws=['/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/tri.gif',14,15,'/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/arrow_right2.gif',18,12,'/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/arrow_right2.gif',5,10];	// Arrow source, width and height


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



Menu1=new Array("Game Guide","/WOW-Encyclopedia-Deployable-Archive/info/index.html","/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/button_bg.gif",12,15,125,"transparent","","","","transparent","",-1,-1,-1,"","");

Menu1_1=new Array(bulletImg+"Introduction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#introduction",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_1=new Array(bulletImg+"Intro to WoW"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/beginners/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_2=new Array(bulletImg+"What is WoW"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guide.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_3=new Array(bulletImg+"Features"+underLine,"/WOW-Encyclopedia-Deployable-Archive/features/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_1_3_1=new Array(bulletImg+"WoW Classic"+underLine,"/WOW-Encyclopedia-Deployable-Archive/misc/features.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_1_3_2=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/burningcrusade/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_1_3_3=new Array(bulletImg+"Wrath"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/features.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_4=new Array(bulletImg+"Look & Feel"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/beginners/index.html#lookAndFeel",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_5=new Array(bulletImg+"Story"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_6=new Array(bulletImg+"Awards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/misc/awards.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_7=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_8=new Array(bulletImg+"System Req."+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/technology.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_8_1=new Array(bulletImg+"Classic System Req."+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/technology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu1_1_8_2=new Array(bulletImg+"BC System Req."+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/faq.html#sys",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu1_1_9=new Array(bulletImg+"Free Trials"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/trial/index.html?referrer=WORLDOFWARCRAFT&source=wowhome&promo=1",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_10=new Array(bulletImg+"Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/classic-credits.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
 Menu1_1_10_1=new Array(bulletImg+"Classic Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/classic-credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_10_2=new Array(bulletImg+"BC Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bc-credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");




Menu1_2=new Array(bulletImg+"Getting Started"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#gettingstarted",menuBg,15,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_1=new Array(bulletImg+"Quick Start"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/gettingstarted.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_2=new Array(bulletImg+"Realm Types"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/realmtypes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_3=new Array(bulletImg+"First Few Levels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/firstfewlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_4=new Array(bulletImg+"Character Attributes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/characters.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_5=new Array(bulletImg+"Character Titles"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/titles.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_6=new Array(bulletImg+"Controls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/controls.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_1=new Array(bulletImg+"Chat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_1=new Array(bulletImg+"Overview"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-overview.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_2=new Array(bulletImg+"Customization"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-customization.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_3=new Array(bulletImg+"Other"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-other.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_4=new Array(bulletImg+"Q and A"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-qna.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_5=new Array(bulletImg+"Command Glossary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-commandglossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_2=new Array(bulletImg+"Emotes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/emotes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_3=new Array(bulletImg+"Dancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_4=new Array(bulletImg+"High-End Content"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/highleveloptions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_5=new Array(bulletImg+"Macros"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/macros.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_6=new Array(bulletImg+"Slash Commands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/slashcommands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_2_7=new Array(bulletImg+"Combat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/combat.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_1=new Array(bulletImg+"Death System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/death.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_2=new Array(bulletImg+"Duels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/duels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_3=new Array(bulletImg+"Resistances"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/resistances.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_4=new Array(bulletImg+"Spells & Abilities"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_2_8=new Array(bulletImg+"Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/quests.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_1=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/questbasics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_2=new Array(bulletImg+"Levels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/questlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_3=new Array(bulletImg+"Management"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/questmanagement.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_4=new Array(bulletImg+"Daily Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/dailyquests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_2_9=new Array(bulletImg+"Combat Pets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/combatpets.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_10=new Array(bulletImg+"Small Pets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/smallpets.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_11=new Array(bulletImg+"Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_12=new Array(bulletImg+"Monster Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/monsterbasics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_13=new Array(bulletImg+"NPCs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/npcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_14=new Array(bulletImg+"Rest System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/resting.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_15=new Array(bulletImg+"Glossary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/glossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");



Menu1_3=new Array(bulletImg+"Character"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#character",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
  		Menu1_3_1=new Array(bulletImg+"Races"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/index.html",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_1=new Array(bulletImg+"Draenei"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/draenei.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_2=new Array(bulletImg+"Dwarves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dwarves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_3=new Array(bulletImg+"Gnomes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/gnomes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_4=new Array(bulletImg+"Humans"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/humans.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_5=new Array(bulletImg+"Night Elves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/nightelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_6=new Array(bulletImg+"Blood Elves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/bloodelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_7=new Array(bulletImg+"Orcs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/orcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_8=new Array(bulletImg+"Tauren"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/tauren.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_9=new Array(bulletImg+"Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/trolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_10=new Array(bulletImg+"Undead"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/undead.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

	

  Menu1_3_2=new Array(bulletImg+"Classes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/index.html","",10,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_1=new Array(bulletImg+"Druid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/index.html","",4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_1=new Array(bulletImg+"Druid Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_2=new Array(bulletImg+"Druid Shape Shifting"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/shapeshifting.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_3=new Array(bulletImg+"Druid Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_4=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_2=new Array(bulletImg+"Hunter"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/index.html","",4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_1=new Array(bulletImg+"Hunter Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_2=new Array(bulletImg+"Hunter Pets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/pets.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_3=new Array(bulletImg+"Hunter Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_4=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_3=new Array(bulletImg+"Mage"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/index.html","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_3_1=new Array(bulletImg+"Mage Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_3_2=new Array(bulletImg+"Mage Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_3_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_4=new Array(bulletImg+"Paladin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/index.html","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_4_1=new Array(bulletImg+"Paladin Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_4_2=new Array(bulletImg+"Paladin Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_4_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_5=new Array(bulletImg+"Priest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/index.html","",2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_5_1=new Array(bulletImg+"Priest Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	 	Menu1_3_2_5_2=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_6=new Array(bulletImg+"Rogue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/index.html","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_6_1=new Array(bulletImg+"Rogue Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_6_2=new Array(bulletImg+"Rogue Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_6_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_7=new Array(bulletImg+"Shaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/index.html","",4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_1=new Array(bulletImg+"Shaman Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_2=new Array(bulletImg+"Shaman Totems"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/totems.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_3=new Array(bulletImg+"Shaman Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_4=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_8=new Array(bulletImg+"Warlock"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/index.html","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_8_1=new Array(bulletImg+"Warlock Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_8_2=new Array(bulletImg+"Warlock Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_8_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_9=new Array(bulletImg+"Warrior"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/index.html","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_9_1=new Array(bulletImg+"Warrior Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_9_2=new Array(bulletImg+"Warrior Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_9_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_10=new Array(bulletImg+"Class Links"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/classlinks.html","",0,15,125,"","","","","","",-1,-1,-1,"","");

	  
	Menu1_3_3=new Array(bulletImg+"Talents"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/talent-index/index.html",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
	    Menu1_3_3_1=new Array(bulletImg+"Talent Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_2=new Array(bulletImg+"Druid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/druid/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_3=new Array(bulletImg+"Hunter"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/hunter/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_4=new Array(bulletImg+"Mage"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/mage/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_5=new Array(bulletImg+"Paladin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/paladin/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_6=new Array(bulletImg+"Priest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/priest/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_7=new Array(bulletImg+"Rogue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/rogue/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_8=new Array(bulletImg+"Shaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/shaman/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_9=new Array(bulletImg+"Warlock"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warlock/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_10=new Array(bulletImg+"Warrior"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/warrior/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

  	Menu1_3_4=new Array(bulletImg+"Professions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/index.html",menuBg,16,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_1=new Array(bulletImg+"Introduction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/intro.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_2=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_3=new Array(bulletImg+"Alchemy"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/alchemy.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_4=new Array(bulletImg+"Blacksmithing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/blacksmithing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_5=new Array(bulletImg+"Cooking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/cooking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_6=new Array(bulletImg+"Enchanting"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/enchanting.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_7=new Array(bulletImg+"Engineering"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/engineering.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_8=new Array(bulletImg+"First Aid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/firstaid.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_9=new Array(bulletImg+"Fishing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/fishing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_10=new Array(bulletImg+"Herbalism"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/herbalism.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_11=new Array(bulletImg+"Leatherworking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/leatherworking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_12=new Array(bulletImg+"Mining"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/mining.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_13=new Array(bulletImg+"Skinning"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/skinning.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_14=new Array(bulletImg+"Tailoring"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/tailoring.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_15=new Array(bulletImg+"Jewelcrafting"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/jewelcrafting.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_3_4_15_1=new Array(bulletImg+"Socketed Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/socketeditems.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_16=new Array(bulletImg+"Profession Links"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/professions/professionlinks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		

	
	Menu1_3_5=new Array(bulletImg+"Dancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_6=new Array(bulletImg+"High-End Content"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/highleveloptions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
Menu1_4=new Array(bulletImg+"Reputations"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/reputation.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_1=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/reputation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_2=new Array(bulletImg+"Classic"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/index.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_1=new Array(bulletImg+"Argent Dawn"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/argent/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_2=new Array(bulletImg+"Brood of Nozdormu"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/broodofnozdormu/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_3=new Array(bulletImg+"Cenarion Circle"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/cenarion/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_4=new Array(bulletImg+"Darkmoon Faire"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_4_1=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/rewards.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_4_2=new Array(bulletImg+"Fortune Teller"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/buffs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_5=new Array(bulletImg+"Thorium Brotherhood"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/thorium/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_6=new Array(bulletImg+"Timbermaw Hold"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/timbermaw/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_7=new Array(bulletImg+"Zandalar Tribe"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zandalar/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_7_1=new Array(bulletImg+"Vendor Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zandalar/vendor.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_7_2=new Array(bulletImg+"Class Quest Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zandalar/quests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
/* New Factions */
	Menu1_4_3=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/reputation.html#BC",menuBg,21,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_1=new Array(bulletImg+"Hellfire Peninsula"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/hellfire/hellfire.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_2=new Array(bulletImg+"Hellfire PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/hellfire/hellfire-tokens.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_4_3_3=new Array(bulletImg+"Cenarion Expedition"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/cenarionxp/cenarionxp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_4=new Array(bulletImg+"Sporeggar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/sporeggar/sporeggar.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_5=new Array(bulletImg+"Zangarmarsh PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zangarmarsh/zangarpvp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_4_3_6=new Array(bulletImg+"Aldor and Scryers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/aldorscryers/aldor-scryers.xml.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");6
		Menu1_4_3_6_1=new Array(bulletImg+"Inscriptions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_7=new Array(bulletImg+"Lower City"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/lowercity/lowercity.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_4_3_8=new Array(bulletImg+"The Consortium"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/consortium/consortium.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_9=new Array(bulletImg+"Bone Wastes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/bonewastes/bonewastes.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_10=new Array(bulletImg+"The Sha'tar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/shatar/shatar.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_11=new Array(bulletImg+"Keepers of Time"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/keepers/keepers.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_12=new Array(bulletImg+"Scale of the Sands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/keepers/scale.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_13=new Array(bulletImg+"Nagrand"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/nagrand/nagrand.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_14=new Array(bulletImg+"Nagrand PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/halaa/halaa.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_15=new Array(bulletImg+"Violet Eye"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/violeteye/violeteye.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_16=new Array(bulletImg+"Violet Eye Rings"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/violeteye/violeteyerings.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_17=new Array(bulletImg+"Ogri'la"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1038%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_17_1=new Array(bulletImg+"Ogri'la Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/ogrila-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_18=new Array(bulletImg+"Sha'tari Skyguard"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1031%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_3_18_1=new Array(bulletImg+"Sha'tari Skyguard Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/skyguard-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_19=new Array(bulletImg+"Netherwing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1015%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_3_19_1=new Array(bulletImg+"Netherwing Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/netherwing-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_20=new Array(bulletImg+"Ashtongue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1012%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_21=new Array(bulletImg+"Badges of Justice"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/badgesofjustice/badges-of-justice.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_3_21_1=new Array(bulletImg+"Badges of Justice 2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/badgesofjustice/badges-of-justice2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_4=new Array(bulletImg+"Armory Listing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Ffactions.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

	
Menu1_5=new Array(bulletImg+"Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#items",menuBg,12,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_1=new Array(bulletImg+"Basics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_2=new Array(bulletImg+"Item Database"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fitem-search.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_3=new Array(bulletImg+"Item Management"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/management.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_4=new Array(bulletImg+"Bags"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bags.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_5=new Array(bulletImg+"Socketed Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/socketeditems.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_6=new Array(bulletImg+"Banking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/banking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_7=new Array(bulletImg+"Dressing Room"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/dressingroom/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_8=new Array(bulletImg+"Merchants"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/merchants.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_9=new Array(bulletImg+"Mail"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mail.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_10=new Array(bulletImg+"Trading"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/trading.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_5_10_1=new Array(bulletImg+"Auction Houses"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/auctionhouses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_5_10_2=new Array(bulletImg+"Auction House Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/auctionhousetips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_5_10_3=new Array(bulletImg+"Chat Auctions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chatauctions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
  Menu1_5_11=new Array(bulletImg+"Food/Drink"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/food.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_12=new Array(bulletImg+"High Level Armor Sets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/armorsets/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  



Menu1_6=new Array(bulletImg+"The World"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#world",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_1=new Array(bulletImg+"World Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/flashmap/index.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_1_1=new Array(bulletImg+"Outland Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/outlandmap.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_2=new Array(bulletImg+"Exploring the Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/map.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_3=new Array(bulletImg+"Regions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_3_1=new Array(bulletImg+"Region Levels"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/regionlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_3_2=new Array(bulletImg+"Silithus Intro"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/shiftingsands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_4=new Array(bulletImg+"Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/dungeons.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_1=new Array(bulletImg+"Instancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/instancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_2=new Array(bulletImg+"Dungeon Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/dungeontips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_3=new Array(bulletImg+"Classic Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html","",19,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_1=new Array(bulletImg+"Blackfathom Deeps"+underLine,"/info/basics/worlddungeons.html#Blackfathom Deeps",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_2=new Array(bulletImg+"Blackrock Depths"+underLine,"/info/basics/worlddungeons.html#Blackrock Depths",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_3=new Array(bulletImg+"Blackrock Spire"+underLine,"/info/basics/worlddungeons.html#Blackrock Spire",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_4=new Array(bulletImg+"Deadmines"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Deadmines",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_5=new Array(bulletImg+"Dire Maul"+underLine,"/info/basics/worlddungeons.html#Dire Maul",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_6=new Array(bulletImg+"Gnomeregan"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Gnomeregan",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_7=new Array(bulletImg+"Maraudon"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Maraudon",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_8=new Array(bulletImg+"Ragefire Chasm"+underLine,"/info/basics/worlddungeons.html#Ragefire Chasm",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_9=new Array(bulletImg+"Razorfen Downs"+underLine,"/info/basics/worlddungeons.html#Razorfen Downs",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_10=new Array(bulletImg+"Razorfen Kraul"+underLine,"/info/basics/worlddungeons.html#Razorfen Kraul",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_11=new Array(bulletImg+"Scholomance"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Scholomance",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_12=new Array(bulletImg+"Shadowfang Keep"+underLine,"/info/basics/worlddungeons.html#Shadowfang Keep",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_13=new Array(bulletImg+"Stratholme"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Stratholme",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_14=new Array(bulletImg+"Scarlet Monastery"+underLine,"/info/basics/worlddungeons.html#The Scarlet Monastery",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_15=new Array(bulletImg+"The Stockades"+underLine,"/info/basics/worlddungeons.html#The Stockades",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_16=new Array(bulletImg+"The Sunken Temple"+underLine,"/info/basics/worlddungeons.html#The Sunken Temple",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_17=new Array(bulletImg+"Uldaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#Uldaman",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_18=new Array(bulletImg+"Wailing Caverns"+underLine,"/info/basics/worlddungeons.html#Wailing Caverns",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_19=new Array(bulletImg+"Zul&#39;Farrak"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/worlddungeons.html#ZulFarrak",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_4=new Array(bulletImg+"BC Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bcworlddungeons.html","",5,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_1=new Array(bulletImg+"Hellfire Citadel"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/hellfire-citadel.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_2=new Array(bulletImg+"Coilfang Reservoir"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/coilfang-reservoir.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_3=new Array(bulletImg+"Auchindoun"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/auchindoun.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_4=new Array(bulletImg+"Caverns of Time"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/caverns-of-time.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_5=new Array(bulletImg+"Tempest Keep"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tempest-keep.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
				
		
		
			
	Menu1_6_5=new Array(bulletImg+"Raid Areas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_5_1=new Array(bulletImg+"Raid Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/calendar/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_5_2=new Array(bulletImg+"Classic Raid Areas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_1=new Array(bulletImg+"Blackwing Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#bwl",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_2=new Array(bulletImg+"Molten Core"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#mc",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_3=new Array(bulletImg+"Onyxia&#39;s Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#onx",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_4=new Array(bulletImg+"Zul&#39;Gurub"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#ZG",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_5=new Array(bulletImg+"Ahn&#39;Qiraj"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#aq20",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_1=new Array(bulletImg+"AQ Ranking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_2=new Array(bulletImg+"AQ Server Stats"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/wareffort.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_3=new Array(bulletImg+"Obsidian Destroyers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/raiddungeons/ahnqiraj/obsidian.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_4=new Array(bulletImg+"Moam"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/raiddungeons/ahnqiraj/moam.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_5=new Array(bulletImg+"Anubisaths"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/raiddungeons/ahnqiraj/anubisath.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_6=new Array(bulletImg+"Ossirian"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/raiddungeons/ahnqiraj/ossirian.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_6=new Array(bulletImg+"Naxxaramas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#naxx",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_7=new Array(bulletImg+"Outdoor"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidarea.html#outdoor",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_5_3=new Array(bulletImg+"BC Raid Areas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/bcraidarea.html",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_1=new Array(bulletImg+"Magtheridon's Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/hellfire-citadel.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_2=new Array(bulletImg+"Serpentshrine Cavern"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/coilfang-reservoir.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_3=new Array(bulletImg+"Tempest Keep: The Eye"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tempest-keep.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_4=new Array(bulletImg+"Gruul's Lair"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/gruuls-lair.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_5=new Array(bulletImg+"The Battle for Mount Hyjal"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/caverns-of-time.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_6_5_3_6=new Array(bulletImg+"Black Temple"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/black-temple.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_6_5_3_7=new Array(bulletImg+"Karazhan"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/karazhan.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_8=new Array(bulletImg+"Zul'Aman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/zulaman.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_9=new Array(bulletImg+"Doom Lord Kazzak"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/doom-lord-kazzak.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_10=new Array(bulletImg+"Doomwalker"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/dungeons/doomwalker.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			
	Menu1_6_6=new Array(bulletImg+"Major Cities"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_1=new Array(bulletImg+"Darnassus"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#darnassus",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_2=new Array(bulletImg+"Ironforge"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#ironforge",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_3=new Array(bulletImg+"Orgrimmar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#orgrimmar",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_4=new Array(bulletImg+"Stormwind"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#stormwind",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_5=new Array(bulletImg+"Thunder Bluff"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#thunderbluff",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_6=new Array(bulletImg+"Undercity"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/cities.html#undercity",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		
	Menu1_6_7=new Array(bulletImg+"In-Game Events"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html",menuBg,18,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_1=new Array(bulletImg+"Events Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/calendar/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_2=new Array(bulletImg+"New Year&#39;s Eve"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/newyears/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_3=new Array(bulletImg+"Lunar Festival"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/lunarnewyears/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_4=new Array(bulletImg+"Love is in the Air"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_5=new Array(bulletImg+"Noblegarden"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#noblegarden",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_6=new Array(bulletImg+"Children&#39;s Week"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/childrensweek/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_7=new Array(bulletImg+"Midsummer Fire Festival"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/midsummer/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_8=new Array(bulletImg+"Harvest Festival"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/harvestfestival/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_9=new Array(bulletImg+"Hallow&#39;s End"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/hallowsend/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_10=new Array(bulletImg+"Winter Veil"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/winterveil/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_11=new Array(bulletImg+"AQ War Effort"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_12=new Array(bulletImg+"Battlegrounds Holiday"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#calltoarms",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_13=new Array(bulletImg+"Darkmoon Faire Event"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/darkmoon/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_14=new Array(bulletImg+"Elemental Invasions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#elemental",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_15=new Array(bulletImg+"Fishing Extravaganza"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/fishing/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_16=new Array(bulletImg+"Gurubashi Arena"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/ingameevents.html#gurubashi",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_17=new Array(bulletImg+"Scourge Invasion"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/scourgeinvasion/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_18=new Array(bulletImg+"Brewfest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/brewfest/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		



Menu1_7=new Array(bulletImg+"Transportation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#transportation",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_7_1=new Array(bulletImg+"Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/index.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
  		Menu1_7_1_1=new Array(bulletImg+"Racial Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/index.html#racial",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_1=new Array(bulletImg+"Horses"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/horses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_2=new Array(bulletImg+"Kodos"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/kodos.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_3=new Array(bulletImg+"Mechanostriders"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/mechanostriders.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_4=new Array(bulletImg+"Nightsabers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/nightsabers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_5=new Array(bulletImg+"Rams"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/rams.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_6=new Array(bulletImg+"Raptors"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/raptors.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_7=new Array(bulletImg+"Skeletal Horses"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/skeletalhorses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_8=new Array(bulletImg+"Wolves"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/wolves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_9=new Array(bulletImg+"Elekks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/elekks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_10=new Array(bulletImg+"Hawkstriders"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/hawkstriders.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_2=new Array(bulletImg+"Class Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/index.html#class",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_2_1=new Array(bulletImg+"Paladin Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/paladin.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_2_2=new Array(bulletImg+"Warlock Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/warlock.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_3=new Array(bulletImg+"Alterac Valley Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#av",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_4=new Array(bulletImg+"PvP Reward Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#pvp",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_5=new Array(bulletImg+"Talbuks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_6=new Array(bulletImg+"Special Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#misc",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_7=new Array(bulletImg+"Flying Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/flying.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_7_2=new Array(bulletImg+"Public Transportation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_1=new Array(bulletImg+"Gryphons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#gryphons",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_2=new Array(bulletImg+"Hippogryphs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#hippogryphs",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_3=new Array(bulletImg+"Deeprun Tram"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#deepruntram",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_4=new Array(bulletImg+"Wyverns"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#wyverns",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_5=new Array(bulletImg+"Vampire Bats"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#bats",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_6=new Array(bulletImg+"Goblin Zeppelin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#zeppelin",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_7=new Array(bulletImg+"Boats"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/publictransportation.html#boats",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		
	Menu1_7_3=new Array(bulletImg+"Transportation FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/transportation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");




Menu1_8=new Array(bulletImg+"Player Interaction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#playerinteraction",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
  
  	Menu1_8_1=new Array(bulletImg+"Guilds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guilds.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_1=new Array(bulletImg+"Joining Guilds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/joiningguilds.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_2=new Array(bulletImg+"Guild Management"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guildtab.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_3=new Array(bulletImg+"Guild Leadership"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guildleadership.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_4=new Array(bulletImg+"Guild Banks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/guildbanks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
  	Menu1_8_2=new Array(bulletImg+"Parties/Raids"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/parties.html",menuBg,9,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_1=new Array(bulletImg+"Roles"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partyroles.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_2=new Array(bulletImg+"Find a Party"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partygrouping.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_3=new Array(bulletImg+"Looking for Group"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/lookingforgroup.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_4=new Array(bulletImg+"Etiquette"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partyrules.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_5=new Array(bulletImg+"Party Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partytips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_6=new Array(bulletImg+"Pulling"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partiespulling.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_7=new Array(bulletImg+"Crowd Control"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/partycrowdcontrol.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_8=new Array(bulletImg+"Raid Groups"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidgroups.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_9=new Array(bulletImg+"Raid Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/raidtips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_8_3=new Array(bulletImg+"How to Be Nice"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/benice.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_8_4=new Array(bulletImg+"Controls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/controls.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_1=new Array(bulletImg+"Voice Chat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/voicechat.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_2=new Array(bulletImg+"Chat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_1=new Array(bulletImg+"Overview"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-overview.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_2=new Array(bulletImg+"Customization"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-customization.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_3=new Array(bulletImg+"Other"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-other.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_4=new Array(bulletImg+"Q&A"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-qna.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_5=new Array(bulletImg+"Command Glossary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/chat-commandglossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_3=new Array(bulletImg+"Emotes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/emotes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_4=new Array(bulletImg+"Dancing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_5=new Array(bulletImg+"Macros"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/macros.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_5_1=new Array(bulletImg+"Macro Guide I"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/macroguide-one.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_6=new Array(bulletImg+"Slash Commands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/slashcommands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu1_9=new Array(bulletImg+"Player vs Player"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/index.html",menuBg,11,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_1=new Array(bulletImg+"Arena"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/arena/index.xml.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_1_1=new Array(bulletImg+"Arena Tournament"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Farena-tournament.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_1_2=new Array(bulletImg+"Arena Intro"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/arena/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_1_3=new Array(bulletImg+"Inside Areas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/insider/11/arena.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_1_4=new Array(bulletImg+"Armory Listing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fpvprewards.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_2=new Array(bulletImg+"Honor System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honorguide.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_2_1=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honor-system-faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_2_2=new Array(bulletImg+"Ranks"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/ranks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_3=new Array(bulletImg+"Honor vs. Arena"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honorvsarena.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_4=new Array(bulletImg+"PvP Combat"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/pvpcombat.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_5=new Array(bulletImg+"Surviving PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/survivingpvp.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_9_6=new Array(bulletImg+"Battlegrounds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/index.html",menuBg,8,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_1=new Array(bulletImg+"General Info"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_2=new Array(bulletImg+"Queue System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/battlegrounds-queue-system.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_3=new Array(bulletImg+"Battlegroups"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/battlegroups/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_4=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_5=new Array(bulletImg+"Alterac Valley"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info-alteracvalley.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_1=new Array(bulletImg+"Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/quests-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_2=new Array(bulletImg+"Enemies"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/enemies-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_3=new Array(bulletImg+"Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/map-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_4=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/alterac/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_5=new Array(bulletImg+"Score Screen"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/scores-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_6=new Array(bulletImg+"Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/tips-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_6=new Array(bulletImg+"Arathi Basin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info-arathi.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_6_1=new Array(bulletImg+"Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/map-arathi.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_6_2=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/arathi/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_6_3=new Array(bulletImg+"Score Screen"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/scores-arathi.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_7=new Array(bulletImg+"Warsong Gulch"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/info-warsong.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_7_1=new Array(bulletImg+"Power-Ups"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/powerups-warsong.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_7_2=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/warsong/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_7_3=new Array(bulletImg+"Score Screen"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/scores-warsong.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_8=new Array(bulletImg+"Eye of the Storm"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/eyeofthestorm/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_7=new Array(bulletImg+"Horde vs Alliance FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/hordevalliance.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_9_8=new Array(bulletImg+"Azeroth Outdoor PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/outdoorpvp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_9=new Array(bulletImg+"Outland Outdoor PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_10=new Array(bulletImg+"Halaa PvP Tips"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/halaa-tips.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_11=new Array(bulletImg+"Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fpvprewards.xml&reason=external-or-uncollected-resource",menuBg,13,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_1=new Array(bulletImg+"Armory Listing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fpvprewards.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_9_11_2=new Array(bulletImg+"General Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/rewards-general.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");			
	        Menu1_9_11_3=new Array(bulletImg+"Vindicator Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/rewards-vindicators-armor.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_4=new Array(bulletImg+"Level 60 and 70 Weapons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/rewards-weapons.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_5=new Array(bulletImg+"Armor Sets"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/items/armorsets/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_6=new Array(bulletImg+"Mounts"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/special.html#pvp",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_7=new Array(bulletImg+"Alterac Valley Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/alterac/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_8=new Array(bulletImg+"Arathi Basin Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/arathi/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_9=new Array(bulletImg+"Warsong Gulch Rewards"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/warsong/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_10=new Array(bulletImg+"Hellfire PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/hellfire/hellfire-tokens.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	    	Menu1_9_11_11=new Array(bulletImg+"Zangarmarsh PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/zangarmarsh/zangarpvp.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_12=new Array(bulletImg+"Bone Wastes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/bonewastes/bonewastes.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_13=new Array(bulletImg+"Nagrand PvP"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/halaa/halaa.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		
		

Menu1_10=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/index.html",menuBg,29,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_1=new Array(bulletImg+"General FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/general.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 	Menu1_10_2=new Array(bulletImg+"Battlegrounds"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_3=new Array(bulletImg+"Blizzard Downloader"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/blizzarddownloader.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_4=new Array(bulletImg+"Character"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/characters.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_5=new Array(bulletImg+"Classes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/classes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_6=new Array(bulletImg+"Dungeons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/dungeons.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_7=new Array(bulletImg+"Gameplay"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/gameplay.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_8=new Array(bulletImg+"Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/guide.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_9=new Array(bulletImg+"Honor System"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/honor-system-faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_10=new Array(bulletImg+"Horde vs Alliance"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/hordevalliance.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_11=new Array(bulletImg+"Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/items.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_12=new Array(bulletImg+"NPCs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/npcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_10_13=new Array(bulletImg+"Paid Character Transfer"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl02008p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_14=new Array(bulletImg+"Parental Controls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl01917p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_15=new Array(bulletImg+"Patches"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/patches.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_16=new Array(bulletImg+"PTR"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/ptr.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_17=new Array(bulletImg+"Recruit-A-Friend"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl01997p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_18=new Array(bulletImg+"Scroll of Resurrection"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl02140p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_19=new Array(bulletImg+"Quests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/quests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_20=new Array(bulletImg+"Races"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/races.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_21=new Array(bulletImg+"Realms"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/realms.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_22=new Array(bulletImg+"Skills"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/skills.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_23=new Array(bulletImg+"Spells"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_24=new Array(bulletImg+"Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/support.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_25=new Array(bulletImg+"Technology"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/technology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_26=new Array(bulletImg+"Transportation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/transportation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_27=new Array(bulletImg+"World"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/world.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_28=new Array(bulletImg+"Burning Crusade"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_29=new Array(bulletImg+"Wrath of Lich King"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/faq.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");



Menu1_11=new Array(bulletImg+"Story"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/index.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_1=new Array(bulletImg+"Encyclopedia"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/encyclopedia/index.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_2=new Array(bulletImg+"Timeline"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/timeline.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_3=new Array(bulletImg+"History"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/timeline.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_1=new Array(bulletImg+"Chapter 1"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter1.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_2=new Array(bulletImg+"Chapter 2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_3=new Array(bulletImg+"Chapter 3"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter3.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_4=new Array(bulletImg+"Chapter 4"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter4.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_5=new Array(bulletImg+"Chapter 5"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter5.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_6=new Array(bulletImg+"Chapter 6"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/chapter6.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_4=new Array(bulletImg+"Lore"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/index.html#lore",menuBg,9,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_1=new Array(bulletImg+"The Murlocs"+underLine,"/WOW-Encyclopedia-Deployable-Archive/misc/murloclore/murlocs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_2=new Array(bulletImg+"Road to Damnation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/underdev/1p11/roadtodamnation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_3=new Array(bulletImg+"Shifting Sands"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/shiftingsands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
		Menu1_11_4_4=new Array(bulletImg+"The Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/index.html",menuBg,13,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_11_4_4_1=new Array(bulletImg+"History 1"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/history.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_11_4_4_2=new Array(bulletImg+"History 2"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/history2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_11_4_4_3=new Array(bulletImg+"Biology"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/biology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_4=new Array(bulletImg+"Trivia"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/trollsandnightelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_5=new Array(bulletImg+"Forest Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/foresttrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_6=new Array(bulletImg+"Forest Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/foresttribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_7=new Array(bulletImg+"Jungle Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/jungletrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_8=new Array(bulletImg+"Jungle Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/jungletribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_9=new Array(bulletImg+"Ice Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/icetrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_10=new Array(bulletImg+"Ice Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/icetribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_11=new Array(bulletImg+"Sand Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/sandtrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_12=new Array(bulletImg+"Sand Troll Tribes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/sandtribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_13=new Array(bulletImg+"Other Trolls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/troll/othertrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_5=new Array(bulletImg+"Undead Plague"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/undeadplague.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_6=new Array(bulletImg+"The Story So Far"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/story.html#top",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_7=new Array(bulletImg+"Shaman/Paladins"+underLine,"/WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/classcombo.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_8=new Array(bulletImg+"Unbroken"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/story/unbroken/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_9=new Array(bulletImg+"Rise of Lich King"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wrath/features/story/story.xml.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");





Menu1_12=new Array(bulletImg+"About Game Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/guide.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_1=new Array(bulletImg+"Archived News"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/archivednews.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_2=new Array(bulletImg+"Content Index"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/content-index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_3=new Array(bulletImg+"Credits"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_4=new Array(bulletImg+"Report Errors"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/guide.html#errors",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_5=new Array(bulletImg+"General Links"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/basics/general-links.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
