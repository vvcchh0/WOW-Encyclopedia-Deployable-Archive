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
						// when your BaseHref= "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
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



Menu1=new Array("Game Guide","/info/","/shared/wow-com/images/subnav/button_bg.gif",12,15,125,"transparent","","","","transparent","",-1,-1,-1,"","");

Menu1_1=new Array(bulletImg+"Introduction"+underLine,"/info/#introduction",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_1=new Array(bulletImg+"Intro to WoW"+underLine,"/info/beginners/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_2=new Array(bulletImg+"What is WoW"+underLine,"/info/basics/guide.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_3=new Array(bulletImg+"Features"+underLine,"/features/index.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_1_3_1=new Array(bulletImg+"WoW Classic"+underLine,"/misc/features.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_1_3_2=new Array(bulletImg+"Burning Crusade"+underLine,"/info/burningcrusade/index.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_1_3_3=new Array(bulletImg+"Wrath"+underLine,"/wrath/features.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_4=new Array(bulletImg+"Look & Feel"+underLine,"/info/beginners/index.html#lookAndFeel",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_5=new Array(bulletImg+"Story"+underLine,"/info/story/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_1_6=new Array(bulletImg+"Awards"+underLine,"/misc/awards.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_7=new Array(bulletImg+"FAQ"+underLine,"/info/faq/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_8=new Array(bulletImg+"System Req."+underLine,"/info/faq/technology.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_8_1=new Array(bulletImg+"Classic System Req."+underLine,"/info/faq/technology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu1_1_8_2=new Array(bulletImg+"BC System Req."+underLine,"/burningcrusade/faq.html#sys",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 Menu1_1_9=new Array(bulletImg+"Free Trials"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fburningcrusade%2Ftrial%2Findex.html%3Freferrer%3DWORLDOFWARCRAFT%26source%3Dwowhome%26promo%3D1&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_10=new Array(bulletImg+"Credits"+underLine,"/info/basics/classic-credits.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
 Menu1_1_10_1=new Array(bulletImg+"Classic Credits"+underLine,"/info/basics/classic-credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_1_10_2=new Array(bulletImg+"BC Credits"+underLine,"/info/basics/bc-credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");




Menu1_2=new Array(bulletImg+"Getting Started"+underLine,"/info/#gettingstarted",menuBg,15,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_1=new Array(bulletImg+"Quick Start"+underLine,"/info/basics/gettingstarted.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_2=new Array(bulletImg+"Realm Types"+underLine,"/info/basics/realmtypes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_3=new Array(bulletImg+"First Few Levels"+underLine,"/info/basics/firstfewlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_4=new Array(bulletImg+"Character Attributes"+underLine,"/info/basics/characters.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_5=new Array(bulletImg+"Character Titles"+underLine,"/info/basics/titles.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_6=new Array(bulletImg+"Controls"+underLine,"/info/basics/controls.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_1=new Array(bulletImg+"Chat"+underLine,"/info/basics/chat.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_1=new Array(bulletImg+"Overview"+underLine,"/info/basics/chat-overview.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_2=new Array(bulletImg+"Customization"+underLine,"/info/basics/chat-customization.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_3=new Array(bulletImg+"Other"+underLine,"/info/basics/chat-other.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_4=new Array(bulletImg+"Q and A"+underLine,"/info/basics/chat-qna.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_2_6_1_5=new Array(bulletImg+"Command Glossary"+underLine,"/info/basics/chat-commandglossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_2=new Array(bulletImg+"Emotes"+underLine,"/info/basics/emotes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_3=new Array(bulletImg+"Dancing"+underLine,"/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_4=new Array(bulletImg+"High-End Content"+underLine,"/info/basics/highleveloptions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_5=new Array(bulletImg+"Macros"+underLine,"/info/basics/macros.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6_6=new Array(bulletImg+"Slash Commands"+underLine,"/info/basics/slashcommands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_2_7=new Array(bulletImg+"Combat"+underLine,"/info/basics/combat.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_1=new Array(bulletImg+"Death System"+underLine,"/info/basics/death.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_2=new Array(bulletImg+"Duels"+underLine,"/info/basics/duels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_3=new Array(bulletImg+"Resistances"+underLine,"/info/basics/resistances.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7_4=new Array(bulletImg+"Spells & Abilities"+underLine,"/info/basics/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_2_8=new Array(bulletImg+"Quests"+underLine,"/info/basics/quests.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_1=new Array(bulletImg+"Basics"+underLine,"/info/basics/questbasics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_2=new Array(bulletImg+"Levels"+underLine,"/info/basics/questlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_3=new Array(bulletImg+"Management"+underLine,"/info/basics/questmanagement.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8_4=new Array(bulletImg+"Daily Quests"+underLine,"/info/basics/dailyquests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_2_9=new Array(bulletImg+"Combat Pets"+underLine,"/info/basics/combatpets.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_10=new Array(bulletImg+"Small Pets"+underLine,"/info/basics/smallpets.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_11=new Array(bulletImg+"Items"+underLine,"/info/items/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_12=new Array(bulletImg+"Monster Basics"+underLine,"/info/basics/monsterbasics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_13=new Array(bulletImg+"NPCs"+underLine,"/info/basics/npcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_14=new Array(bulletImg+"Rest System"+underLine,"/info/basics/resting.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_2_15=new Array(bulletImg+"Glossary"+underLine,"/info/basics/glossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");



Menu1_3=new Array(bulletImg+"Character"+underLine,"/info/#character",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
  		Menu1_3_1=new Array(bulletImg+"Races"+underLine,"/info/races/index.html",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_1=new Array(bulletImg+"Draenei"+underLine,"/info/races/draenei.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_2=new Array(bulletImg+"Dwarves"+underLine,"/info/races/dwarves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_3=new Array(bulletImg+"Gnomes"+underLine,"/info/races/gnomes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_4=new Array(bulletImg+"Humans"+underLine,"/info/races/humans.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_5=new Array(bulletImg+"Night Elves"+underLine,"/info/races/nightelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_6=new Array(bulletImg+"Blood Elves"+underLine,"/info/races/bloodelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_7=new Array(bulletImg+"Orcs"+underLine,"/info/races/orcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_8=new Array(bulletImg+"Tauren"+underLine,"/info/races/tauren.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_9=new Array(bulletImg+"Trolls"+underLine,"/info/races/trolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1_10=new Array(bulletImg+"Undead"+underLine,"/info/races/undead.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

	

  Menu1_3_2=new Array(bulletImg+"Classes"+underLine,"/info/classes/index.html","",10,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_1=new Array(bulletImg+"Druid"+underLine,"/info/classes/druid/","",4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_1=new Array(bulletImg+"Druid Spells"+underLine,"/info/classes/druid/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_2=new Array(bulletImg+"Druid Shape Shifting"+underLine,"/info/classes/druid/shapeshifting.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_3=new Array(bulletImg+"Druid Tips"+underLine,"/info/classes/druid/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_1_4=new Array(bulletImg+"Talents"+underLine,"/info/classes/druid/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_2=new Array(bulletImg+"Hunter"+underLine,"/info/classes/hunter/","",4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_1=new Array(bulletImg+"Hunter Spells"+underLine,"/info/classes/hunter/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_2=new Array(bulletImg+"Hunter Pets"+underLine,"/info/classes/hunter/pets.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_3=new Array(bulletImg+"Hunter Tips"+underLine,"/info/classes/hunter/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_2_4=new Array(bulletImg+"Talents"+underLine,"/info/classes/hunter/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_3=new Array(bulletImg+"Mage"+underLine,"/info/classes/mage/","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_3_1=new Array(bulletImg+"Mage Spells"+underLine,"/info/classes/mage/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_3_2=new Array(bulletImg+"Mage Tips"+underLine,"/info/classes/mage/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_3_3=new Array(bulletImg+"Talents"+underLine,"/info/classes/mage/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_4=new Array(bulletImg+"Paladin"+underLine,"/info/classes/paladin/","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_4_1=new Array(bulletImg+"Paladin Spells"+underLine,"/info/classes/paladin/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_4_2=new Array(bulletImg+"Paladin Tips"+underLine,"/info/classes/paladin/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_4_3=new Array(bulletImg+"Talents"+underLine,"/info/classes/paladin/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_5=new Array(bulletImg+"Priest"+underLine,"/info/classes/priest/","",2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_5_1=new Array(bulletImg+"Priest Spells"+underLine,"/info/classes/priest/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	 	Menu1_3_2_5_2=new Array(bulletImg+"Talents"+underLine,"/info/classes/priest/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_6=new Array(bulletImg+"Rogue"+underLine,"/info/classes/rogue/","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_6_1=new Array(bulletImg+"Rogue Spells"+underLine,"/info/classes/rogue/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_6_2=new Array(bulletImg+"Rogue Tips"+underLine,"/info/classes/rogue/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_6_3=new Array(bulletImg+"Talents"+underLine,"/info/classes/rogue/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_7=new Array(bulletImg+"Shaman"+underLine,"/info/classes/shaman/","",4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_1=new Array(bulletImg+"Shaman Spells"+underLine,"/info/classes/shaman/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_2=new Array(bulletImg+"Shaman Totems"+underLine,"/info/classes/shaman/totems.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_3=new Array(bulletImg+"Shaman Tips"+underLine,"/info/classes/shaman/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_7_4=new Array(bulletImg+"Talents"+underLine,"/info/classes/shaman/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_8=new Array(bulletImg+"Warlock"+underLine,"/info/classes/warlock/","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_8_1=new Array(bulletImg+"Warlock Spells"+underLine,"/info/classes/warlock/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_8_2=new Array(bulletImg+"Warlock Tips"+underLine,"/info/classes/warlock/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_8_3=new Array(bulletImg+"Talents"+underLine,"/info/classes/warlock/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_9=new Array(bulletImg+"Warrior"+underLine,"/info/classes/warrior/","",3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_9_1=new Array(bulletImg+"Warrior Spells"+underLine,"/info/classes/warrior/spells.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_9_2=new Array(bulletImg+"Warrior Tips"+underLine,"/info/classes/warrior/tips.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2_9_3=new Array(bulletImg+"Talents"+underLine,"/info/classes/warrior/talents.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_2_10=new Array(bulletImg+"Class Links"+underLine,"/info/classes/classlinks.html","",0,15,125,"","","","","","",-1,-1,-1,"","");

	  
	Menu1_3_3=new Array(bulletImg+"Talents"+underLine,"/info/classes/talent-index/",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
	    Menu1_3_3_1=new Array(bulletImg+"Talent Basics"+underLine,"/info/basics/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_2=new Array(bulletImg+"Druid"+underLine,"/info/classes/druid/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_3=new Array(bulletImg+"Hunter"+underLine,"/info/classes/hunter/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_4=new Array(bulletImg+"Mage"+underLine,"/info/classes/mage/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_5=new Array(bulletImg+"Paladin"+underLine,"/info/classes/paladin/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_6=new Array(bulletImg+"Priest"+underLine,"/info/classes/priest/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_7=new Array(bulletImg+"Rogue"+underLine,"/info/classes/rogue/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_8=new Array(bulletImg+"Shaman"+underLine,"/info/classes/shaman/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_9=new Array(bulletImg+"Warlock"+underLine,"/info/classes/warlock/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3_10=new Array(bulletImg+"Warrior"+underLine,"/info/classes/warrior/talents.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

  	Menu1_3_4=new Array(bulletImg+"Professions"+underLine,"/info/professions/index.html",menuBg,16,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_1=new Array(bulletImg+"Introduction"+underLine,"/info/professions/intro.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_2=new Array(bulletImg+"Basics"+underLine,"/info/professions/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_3=new Array(bulletImg+"Alchemy"+underLine,"/info/professions/alchemy.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_4=new Array(bulletImg+"Blacksmithing"+underLine,"/info/professions/blacksmithing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_5=new Array(bulletImg+"Cooking"+underLine,"/info/professions/cooking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_6=new Array(bulletImg+"Enchanting"+underLine,"/info/professions/enchanting.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_7=new Array(bulletImg+"Engineering"+underLine,"/info/professions/engineering.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_8=new Array(bulletImg+"First Aid"+underLine,"/info/professions/firstaid.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_9=new Array(bulletImg+"Fishing"+underLine,"/info/professions/fishing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_10=new Array(bulletImg+"Herbalism"+underLine,"/info/professions/herbalism.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_11=new Array(bulletImg+"Leatherworking"+underLine,"/info/professions/leatherworking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_12=new Array(bulletImg+"Mining"+underLine,"/info/professions/mining.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_13=new Array(bulletImg+"Skinning"+underLine,"/info/professions/skinning.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_14=new Array(bulletImg+"Tailoring"+underLine,"/info/professions/tailoring.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_15=new Array(bulletImg+"Jewelcrafting"+underLine,"/info/professions/jewelcrafting.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_3_4_15_1=new Array(bulletImg+"Socketed Items"+underLine,"/info/items/socketeditems.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4_16=new Array(bulletImg+"Profession Links"+underLine,"/info/professions/professionlinks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		

	
	Menu1_3_5=new Array(bulletImg+"Dancing"+underLine,"/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_3_6=new Array(bulletImg+"High-End Content"+underLine,"/info/basics/highleveloptions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
Menu1_4=new Array(bulletImg+"Reputations"+underLine,"/info/basics/reputation.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_1=new Array(bulletImg+"Basics"+underLine,"/info/basics/reputation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_2=new Array(bulletImg+"Classic"+underLine,"/info/basics/factions/",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_1=new Array(bulletImg+"Argent Dawn"+underLine,"/info/basics/factions/argent/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_2=new Array(bulletImg+"Brood of Nozdormu"+underLine,"/info/basics/factions/broodofnozdormu/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_3=new Array(bulletImg+"Cenarion Circle"+underLine,"/info/basics/factions/cenarion/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_4=new Array(bulletImg+"Darkmoon Faire"+underLine,"/info/basics/factions/darkmoon/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_4_1=new Array(bulletImg+"Rewards"+underLine,"/info/basics/factions/darkmoon/rewards.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_4_2=new Array(bulletImg+"Fortune Teller"+underLine,"/info/basics/factions/darkmoon/buffs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_5=new Array(bulletImg+"Thorium Brotherhood"+underLine,"/info/basics/factions/thorium/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_6=new Array(bulletImg+"Timbermaw Hold"+underLine,"/info/basics/factions/timbermaw/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2_7=new Array(bulletImg+"Zandalar Tribe"+underLine,"/info/basics/factions/zandalar/index.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_7_1=new Array(bulletImg+"Vendor Rewards"+underLine,"/info/basics/factions/zandalar/vendor.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_4_2_7_2=new Array(bulletImg+"Class Quest Rewards"+underLine,"/info/basics/factions/zandalar/quests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
/* New Factions */
	Menu1_4_3=new Array(bulletImg+"Burning Crusade"+underLine,"/info/basics/reputation.html#BC",menuBg,21,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_1=new Array(bulletImg+"Hellfire Peninsula"+underLine,"/info/basics/factions/hellfire/hellfire.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_2=new Array(bulletImg+"Hellfire PvP"+underLine,"/info/basics/factions/hellfire/hellfire-tokens.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_4_3_3=new Array(bulletImg+"Cenarion Expedition"+underLine,"/info/basics/factions/cenarionxp/cenarionxp.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_4=new Array(bulletImg+"Sporeggar"+underLine,"/info/basics/factions/sporeggar/sporeggar.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_5=new Array(bulletImg+"Zangarmarsh PvP"+underLine,"/info/basics/factions/zangarmarsh/zangarpvp.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_4_3_6=new Array(bulletImg+"Aldor and Scryers"+underLine,"/info/basics/factions/aldorscryers/aldor-scryers.xml",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");6
		Menu1_4_3_6_1=new Array(bulletImg+"Inscriptions"+underLine,"/info/basics/factions/aldorscryers/aldor-scryers-tokens.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_7=new Array(bulletImg+"Lower City"+underLine,"/info/basics/factions/lowercity/lowercity.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_4_3_8=new Array(bulletImg+"The Consortium"+underLine,"/info/basics/factions/consortium/consortium.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_9=new Array(bulletImg+"Bone Wastes"+underLine,"/info/basics/factions/bonewastes/bonewastes.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_10=new Array(bulletImg+"The Sha'tar"+underLine,"/info/basics/factions/shatar/shatar.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_11=new Array(bulletImg+"Keepers of Time"+underLine,"/info/basics/factions/keepers/keepers.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_12=new Array(bulletImg+"Scale of the Sands"+underLine,"/info/basics/factions/keepers/scale.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_13=new Array(bulletImg+"Nagrand"+underLine,"/info/basics/factions/nagrand/nagrand.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_14=new Array(bulletImg+"Nagrand PvP"+underLine,"/info/basics/factions/halaa/halaa.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_15=new Array(bulletImg+"Violet Eye"+underLine,"/info/basics/factions/violeteye/violeteye.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_16=new Array(bulletImg+"Violet Eye Rings"+underLine,"/info/basics/factions/violeteye/violeteyerings.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_17=new Array(bulletImg+"Ogri'la"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1038%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_17_1=new Array(bulletImg+"Ogri'la Tips"+underLine,"/info/basics/factions/ogrila-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_18=new Array(bulletImg+"Sha'tari Skyguard"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1031%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_3_18_1=new Array(bulletImg+"Sha'tari Skyguard Tips"+underLine,"/info/basics/factions/skyguard-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_19=new Array(bulletImg+"Netherwing"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1015%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_3_19_1=new Array(bulletImg+"Netherwing Tips"+underLine,"/info/basics/factions/netherwing-tips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_20=new Array(bulletImg+"Ashtongue"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fsearch.xml%3Ffl%5Bsource%5D%3Dreputation%26fl%5Bfaction%5D%3D1012%26searchType%3Ditems&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_3_21=new Array(bulletImg+"Badges of Justice"+underLine,"/info/basics/factions/badgesofjustice/badges-of-justice.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_4_3_21_1=new Array(bulletImg+"Badges of Justice 2"+underLine,"/info/basics/factions/badgesofjustice/badges-of-justice2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_4_4=new Array(bulletImg+"Armory Listing"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Ffactions.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

	
Menu1_5=new Array(bulletImg+"Items"+underLine,"/info/#items",menuBg,12,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_1=new Array(bulletImg+"Basics"+underLine,"/info/items/basics.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_2=new Array(bulletImg+"Item Database"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fitem-search.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_3=new Array(bulletImg+"Item Management"+underLine,"/info/items/management.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_4=new Array(bulletImg+"Bags"+underLine,"/info/basics/bags.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_5=new Array(bulletImg+"Socketed Items"+underLine,"/info/items/socketeditems.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_6=new Array(bulletImg+"Banking"+underLine,"/info/basics/banking.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_7=new Array(bulletImg+"Dressing Room"+underLine,"/info/items/dressingroom/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_8=new Array(bulletImg+"Merchants"+underLine,"/info/basics/merchants.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_9=new Array(bulletImg+"Mail"+underLine,"/info/basics/mail.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_10=new Array(bulletImg+"Trading"+underLine,"/info/basics/trading.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_5_10_1=new Array(bulletImg+"Auction Houses"+underLine,"/info/basics/auctionhouses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_5_10_2=new Array(bulletImg+"Auction House Tips"+underLine,"/info/basics/auctionhousetips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_5_10_3=new Array(bulletImg+"Chat Auctions"+underLine,"/info/basics/chatauctions.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
  Menu1_5_11=new Array(bulletImg+"Food/Drink"+underLine,"/info/basics/food.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  Menu1_5_12=new Array(bulletImg+"High Level Armor Sets"+underLine,"/info/items/armorsets/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  



Menu1_6=new Array(bulletImg+"The World"+underLine,"/info/#world",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_1=new Array(bulletImg+"World Map"+underLine,"/info/flashmap/",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_1_1=new Array(bulletImg+"Outland Map"+underLine,"/burningcrusade/townhall/outlandmap.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_2=new Array(bulletImg+"Exploring the Map"+underLine,"/info/basics/map.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_3=new Array(bulletImg+"Regions"+underLine,"/info/basics/",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_3_1=new Array(bulletImg+"Region Levels"+underLine,"/info/basics/regionlevels.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_3_2=new Array(bulletImg+"Silithus Intro"+underLine,"/info/story/shiftingsands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_6_4=new Array(bulletImg+"Dungeons"+underLine,"/info/basics/dungeons.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_1=new Array(bulletImg+"Instancing"+underLine,"/info/basics/instancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_2=new Array(bulletImg+"Dungeon Tips"+underLine,"/info/basics/dungeontips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_3=new Array(bulletImg+"Classic Dungeons"+underLine,"/info/basics/worlddungeons.html","",19,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_1=new Array(bulletImg+"Blackfathom Deeps"+underLine,"/info/basics/worlddungeons.html#Blackfathom Deeps",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_2=new Array(bulletImg+"Blackrock Depths"+underLine,"/info/basics/worlddungeons.html#Blackrock Depths",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_3=new Array(bulletImg+"Blackrock Spire"+underLine,"/info/basics/worlddungeons.html#Blackrock Spire",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_4=new Array(bulletImg+"Deadmines"+underLine,"/info/basics/worlddungeons.html#Deadmines",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_5=new Array(bulletImg+"Dire Maul"+underLine,"/info/basics/worlddungeons.html#Dire Maul",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_6=new Array(bulletImg+"Gnomeregan"+underLine,"/info/basics/worlddungeons.html#Gnomeregan",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_7=new Array(bulletImg+"Maraudon"+underLine,"/info/basics/worlddungeons.html#Maraudon",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_8=new Array(bulletImg+"Ragefire Chasm"+underLine,"/info/basics/worlddungeons.html#Ragefire Chasm",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_9=new Array(bulletImg+"Razorfen Downs"+underLine,"/info/basics/worlddungeons.html#Razorfen Downs",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_10=new Array(bulletImg+"Razorfen Kraul"+underLine,"/info/basics/worlddungeons.html#Razorfen Kraul",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_11=new Array(bulletImg+"Scholomance"+underLine,"/info/basics/worlddungeons.html#Scholomance",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_12=new Array(bulletImg+"Shadowfang Keep"+underLine,"/info/basics/worlddungeons.html#Shadowfang Keep",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_13=new Array(bulletImg+"Stratholme"+underLine,"/info/basics/worlddungeons.html#Stratholme",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_14=new Array(bulletImg+"Scarlet Monastery"+underLine,"/info/basics/worlddungeons.html#The Scarlet Monastery",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_15=new Array(bulletImg+"The Stockades"+underLine,"/info/basics/worlddungeons.html#The Stockades",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_16=new Array(bulletImg+"The Sunken Temple"+underLine,"/info/basics/worlddungeons.html#The Sunken Temple",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_17=new Array(bulletImg+"Uldaman"+underLine,"/info/basics/worlddungeons.html#Uldaman",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_18=new Array(bulletImg+"Wailing Caverns"+underLine,"/info/basics/worlddungeons.html#Wailing Caverns",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_3_19=new Array(bulletImg+"Zul&#39;Farrak"+underLine,"/info/basics/worlddungeons.html#ZulFarrak",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4_4=new Array(bulletImg+"BC Dungeons"+underLine,"/info/basics/bcworlddungeons.html","",5,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_1=new Array(bulletImg+"Hellfire Citadel"+underLine,"/info/dungeons/hellfire-citadel.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_2=new Array(bulletImg+"Coilfang Reservoir"+underLine,"/info/dungeons/coilfang-reservoir.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_3=new Array(bulletImg+"Auchindoun"+underLine,"/info/dungeons/auchindoun.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_4=new Array(bulletImg+"Caverns of Time"+underLine,"/info/dungeons/caverns-of-time.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_4_4_5=new Array(bulletImg+"Tempest Keep"+underLine,"/info/dungeons/tempest-keep.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
				
		
		
			
	Menu1_6_5=new Array(bulletImg+"Raid Areas"+underLine,"/info/basics/raidarea.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_5_1=new Array(bulletImg+"Raid Calendar"+underLine,"/calendar/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_5_2=new Array(bulletImg+"Classic Raid Areas"+underLine,"/info/basics/raidarea.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_1=new Array(bulletImg+"Blackwing Lair"+underLine,"/info/basics/raidarea.html#bwl",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_2=new Array(bulletImg+"Molten Core"+underLine,"/info/basics/raidarea.html#mc",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_3=new Array(bulletImg+"Onyxia&#39;s Lair"+underLine,"/info/basics/raidarea.html#onx",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_4=new Array(bulletImg+"Zul&#39;Gurub"+underLine,"/info/basics/raidarea.html#ZG",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_5=new Array(bulletImg+"Ahn&#39;Qiraj"+underLine,"/info/basics/raidarea.html#aq20",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_1=new Array(bulletImg+"AQ Ranking"+underLine,"/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_2=new Array(bulletImg+"AQ Server Stats"+underLine,"/wareffort/wareffort.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_3=new Array(bulletImg+"Obsidian Destroyers"+underLine,"/info/raiddungeons/ahnqiraj/obsidian.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_4=new Array(bulletImg+"Moam"+underLine,"/info/raiddungeons/ahnqiraj/moam.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_5=new Array(bulletImg+"Anubisaths"+underLine,"/info/raiddungeons/ahnqiraj/anubisath.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
				Menu1_6_5_2_5_6=new Array(bulletImg+"Ossirian"+underLine,"/info/raiddungeons/ahnqiraj/ossirian.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_6=new Array(bulletImg+"Naxxaramas"+underLine,"/info/basics/raidarea.html#naxx",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2_7=new Array(bulletImg+"Outdoor"+underLine,"/info/basics/raidarea.html#outdoor",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_5_3=new Array(bulletImg+"BC Raid Areas"+underLine,"/info/basics/bcraidarea.html",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_1=new Array(bulletImg+"Magtheridon's Lair"+underLine,"/info/dungeons/hellfire-citadel.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_2=new Array(bulletImg+"Serpentshrine Cavern"+underLine,"/info/dungeons/coilfang-reservoir.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_3=new Array(bulletImg+"Tempest Keep: The Eye"+underLine,"/info/dungeons/tempest-keep.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_4=new Array(bulletImg+"Gruul's Lair"+underLine,"/info/dungeons/gruuls-lair.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_5=new Array(bulletImg+"The Battle for Mount Hyjal"+underLine,"/info/dungeons/caverns-of-time.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_6_5_3_6=new Array(bulletImg+"Black Temple"+underLine,"/info/dungeons/black-temple.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_6_5_3_7=new Array(bulletImg+"Karazhan"+underLine,"/info/dungeons/karazhan.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_8=new Array(bulletImg+"Zul'Aman"+underLine,"/info/dungeons/zulaman.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_9=new Array(bulletImg+"Doom Lord Kazzak"+underLine,"/info/dungeons/doom-lord-kazzak.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3_10=new Array(bulletImg+"Doomwalker"+underLine,"/info/dungeons/doomwalker.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			
	Menu1_6_6=new Array(bulletImg+"Major Cities"+underLine,"/info/basics/cities.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_1=new Array(bulletImg+"Darnassus"+underLine,"/info/basics/cities.html#darnassus",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_2=new Array(bulletImg+"Ironforge"+underLine,"/info/basics/cities.html#ironforge",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_3=new Array(bulletImg+"Orgrimmar"+underLine,"/info/basics/cities.html#orgrimmar",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_4=new Array(bulletImg+"Stormwind"+underLine,"/info/basics/cities.html#stormwind",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_5=new Array(bulletImg+"Thunder Bluff"+underLine,"/info/basics/cities.html#thunderbluff",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_6=new Array(bulletImg+"Undercity"+underLine,"/info/basics/cities.html#undercity",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		
	Menu1_6_7=new Array(bulletImg+"In-Game Events"+underLine,"/community/ingameevents.html",menuBg,18,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_1=new Array(bulletImg+"Events Calendar"+underLine,"/info/events/calendar/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_2=new Array(bulletImg+"New Year&#39;s Eve"+underLine,"/info/events/newyears/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_3=new Array(bulletImg+"Lunar Festival"+underLine,"/info/events/lunarnewyears/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_4=new Array(bulletImg+"Love is in the Air"+underLine,"/info/events/loveisintheair/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_5=new Array(bulletImg+"Noblegarden"+underLine,"/community/ingameevents.html#noblegarden",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_6=new Array(bulletImg+"Children&#39;s Week"+underLine,"/info/events/childrensweek/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_7=new Array(bulletImg+"Midsummer Fire Festival"+underLine,"/info/events/midsummer/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_8=new Array(bulletImg+"Harvest Festival"+underLine,"/info/events/harvestfestival/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_9=new Array(bulletImg+"Hallow&#39;s End"+underLine,"/info/events/hallowsend/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_10=new Array(bulletImg+"Winter Veil"+underLine,"/info/events/winterveil/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_11=new Array(bulletImg+"AQ War Effort"+underLine,"/wareffort/servers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_12=new Array(bulletImg+"Battlegrounds Holiday"+underLine,"/community/ingameevents.html#calltoarms",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_13=new Array(bulletImg+"Darkmoon Faire Event"+underLine,"/info/basics/factions/darkmoon/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_14=new Array(bulletImg+"Elemental Invasions"+underLine,"/community/ingameevents.html#elemental",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_15=new Array(bulletImg+"Fishing Extravaganza"+underLine,"/info/events/fishing/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_16=new Array(bulletImg+"Gurubashi Arena"+underLine,"/community/ingameevents.html#gurubashi",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_17=new Array(bulletImg+"Scourge Invasion"+underLine,"/info/events/scourgeinvasion/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7_18=new Array(bulletImg+"Brewfest"+underLine,"/info/events/brewfest/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		



Menu1_7=new Array(bulletImg+"Transportation"+underLine,"/info/#transportation",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_7_1=new Array(bulletImg+"Mounts"+underLine,"/info/basics/mounts/index.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
  		Menu1_7_1_1=new Array(bulletImg+"Racial Mounts"+underLine,"/info/basics/mounts/index.html#racial",menuBg,10,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_1=new Array(bulletImg+"Horses"+underLine,"/info/basics/mounts/horses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_2=new Array(bulletImg+"Kodos"+underLine,"/info/basics/mounts/kodos.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_3=new Array(bulletImg+"Mechanostriders"+underLine,"/info/basics/mounts/mechanostriders.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_4=new Array(bulletImg+"Nightsabers"+underLine,"/info/basics/mounts/nightsabers.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_5=new Array(bulletImg+"Rams"+underLine,"/info/basics/mounts/rams.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_6=new Array(bulletImg+"Raptors"+underLine,"/info/basics/mounts/raptors.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_7=new Array(bulletImg+"Skeletal Horses"+underLine,"/info/basics/mounts/skeletalhorses.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_8=new Array(bulletImg+"Wolves"+underLine,"/info/basics/mounts/wolves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_9=new Array(bulletImg+"Elekks"+underLine,"/info/basics/mounts/elekks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_1_10=new Array(bulletImg+"Hawkstriders"+underLine,"/info/basics/mounts/hawkstriders.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_2=new Array(bulletImg+"Class Mounts"+underLine,"/info/basics/mounts/index.html#class",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_2_1=new Array(bulletImg+"Paladin Mounts"+underLine,"/info/basics/mounts/paladin.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_7_1_2_2=new Array(bulletImg+"Warlock Mounts"+underLine,"/info/basics/mounts/warlock.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_3=new Array(bulletImg+"Alterac Valley Mounts"+underLine,"/info/basics/mounts/special.html#av",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_4=new Array(bulletImg+"PvP Reward Mounts"+underLine,"/info/basics/mounts/special.html#pvp",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_5=new Array(bulletImg+"Talbuks"+underLine,"/info/basics/mounts/special.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_6=new Array(bulletImg+"Special Mounts"+underLine,"/info/basics/mounts/special.html#misc",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1_7=new Array(bulletImg+"Flying Mounts"+underLine,"/info/basics/mounts/flying.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_7_2=new Array(bulletImg+"Public Transportation"+underLine,"/info/basics/publictransportation.html",menuBg,7,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_1=new Array(bulletImg+"Gryphons"+underLine,"/info/basics/publictransportation.html#gryphons",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_2=new Array(bulletImg+"Hippogryphs"+underLine,"/info/basics/publictransportation.html#hippogryphs",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_3=new Array(bulletImg+"Deeprun Tram"+underLine,"/info/basics/publictransportation.html#deepruntram",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_4=new Array(bulletImg+"Wyverns"+underLine,"/info/basics/publictransportation.html#wyverns",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_5=new Array(bulletImg+"Vampire Bats"+underLine,"/info/basics/publictransportation.html#bats",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_6=new Array(bulletImg+"Goblin Zeppelin"+underLine,"/info/basics/publictransportation.html#zeppelin",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2_7=new Array(bulletImg+"Boats"+underLine,"/info/basics/publictransportation.html#boats",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		
	Menu1_7_3=new Array(bulletImg+"Transportation FAQ"+underLine,"/info/faq/transportation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");




Menu1_8=new Array(bulletImg+"Player Interaction"+underLine,"/info/#playerinteraction",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
  
  	Menu1_8_1=new Array(bulletImg+"Guilds"+underLine,"/info/basics/guilds.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_1=new Array(bulletImg+"Joining Guilds"+underLine,"/info/basics/joiningguilds.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_2=new Array(bulletImg+"Guild Management"+underLine,"/info/basics/guildtab.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_3=new Array(bulletImg+"Guild Leadership"+underLine,"/info/basics/guildleadership.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_1_4=new Array(bulletImg+"Guild Banks"+underLine,"/info/basics/guildbanks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
  	Menu1_8_2=new Array(bulletImg+"Parties/Raids"+underLine,"/info/basics/parties.html",menuBg,9,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_1=new Array(bulletImg+"Roles"+underLine,"/info/basics/partyroles.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_2=new Array(bulletImg+"Find a Party"+underLine,"/info/basics/partygrouping.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_3=new Array(bulletImg+"Looking for Group"+underLine,"/burningcrusade/townhall/lookingforgroup.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_4=new Array(bulletImg+"Etiquette"+underLine,"/info/basics/partyrules.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_5=new Array(bulletImg+"Party Tips"+underLine,"/info/basics/partytips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_6=new Array(bulletImg+"Pulling"+underLine,"/info/basics/partiespulling.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_7=new Array(bulletImg+"Crowd Control"+underLine,"/info/basics/partycrowdcontrol.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_8=new Array(bulletImg+"Raid Groups"+underLine,"/info/basics/raidgroups.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2_9=new Array(bulletImg+"Raid Tips"+underLine,"/info/basics/raidtips.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_8_3=new Array(bulletImg+"How to Be Nice"+underLine,"/info/basics/benice.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_8_4=new Array(bulletImg+"Controls"+underLine,"/info/basics/controls.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_1=new Array(bulletImg+"Voice Chat"+underLine,"/info/basics/voicechat.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_2=new Array(bulletImg+"Chat"+underLine,"/info/basics/chat.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_1=new Array(bulletImg+"Overview"+underLine,"/info/basics/chat-overview.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_2=new Array(bulletImg+"Customization"+underLine,"/info/basics/chat-customization.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_3=new Array(bulletImg+"Other"+underLine,"/info/basics/chat-other.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_4=new Array(bulletImg+"Q&A"+underLine,"/info/basics/chat-qna.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_2_5=new Array(bulletImg+"Command Glossary"+underLine,"/info/basics/chat-commandglossary.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_3=new Array(bulletImg+"Emotes"+underLine,"/info/basics/emotes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_4=new Array(bulletImg+"Dancing"+underLine,"/info/races/dancing.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_5=new Array(bulletImg+"Macros"+underLine,"/info/basics/macros.html",menuBg,1,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_8_4_5_1=new Array(bulletImg+"Macro Guide I"+underLine,"/info/basics/macroguide-one.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4_6=new Array(bulletImg+"Slash Commands"+underLine,"/info/basics/slashcommands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");

Menu1_9=new Array(bulletImg+"Player vs Player"+underLine,"/pvp/",menuBg,11,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_1=new Array(bulletImg+"Arena"+underLine,"/pvp/arena/index.xml",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_1_1=new Array(bulletImg+"Arena Tournament"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Farena-tournament.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_1_2=new Array(bulletImg+"Arena Intro"+underLine,"/pvp/arena/index.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_1_3=new Array(bulletImg+"Inside Areas"+underLine,"/insider/11/arena.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_1_4=new Array(bulletImg+"Armory Listing"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fpvprewards.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_2=new Array(bulletImg+"Honor System"+underLine,"/pvp/honorguide.html",menuBg,2,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_2_1=new Array(bulletImg+"FAQ"+underLine,"/pvp/honor-system-faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_2_2=new Array(bulletImg+"Ranks"+underLine,"/pvp/ranks.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_3=new Array(bulletImg+"Honor vs. Arena"+underLine,"/pvp/honorvsarena.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_4=new Array(bulletImg+"PvP Combat"+underLine,"/info/basics/pvpcombat.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_5=new Array(bulletImg+"Surviving PvP"+underLine,"/info/basics/survivingpvp.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	
	Menu1_9_6=new Array(bulletImg+"Battlegrounds"+underLine,"/pvp/battlegrounds/",menuBg,8,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_1=new Array(bulletImg+"General Info"+underLine,"/pvp/battlegrounds/info.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_2=new Array(bulletImg+"Queue System"+underLine,"/pvp/battlegrounds/battlegrounds-queue-system.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_3=new Array(bulletImg+"Battlegroups"+underLine,"/pvp/battlegrounds/battlegroups/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_4=new Array(bulletImg+"FAQ"+underLine,"/pvp/battlegrounds/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_5=new Array(bulletImg+"Alterac Valley"+underLine,"/pvp/battlegrounds/info-alteracvalley.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_1=new Array(bulletImg+"Quests"+underLine,"/pvp/battlegrounds/quests-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_2=new Array(bulletImg+"Enemies"+underLine,"/pvp/battlegrounds/enemies-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_3=new Array(bulletImg+"Map"+underLine,"/pvp/battlegrounds/map-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_4=new Array(bulletImg+"Rewards"+underLine,"/info/basics/factions/alterac/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_5=new Array(bulletImg+"Score Screen"+underLine,"/pvp/battlegrounds/scores-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_5_6=new Array(bulletImg+"Tips"+underLine,"/pvp/battlegrounds/tips-alterac.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_6=new Array(bulletImg+"Arathi Basin"+underLine,"/pvp/battlegrounds/info-arathi.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_6_1=new Array(bulletImg+"Map"+underLine,"/pvp/battlegrounds/map-arathi.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_6_2=new Array(bulletImg+"Rewards"+underLine,"/info/basics/factions/arathi/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_6_3=new Array(bulletImg+"Score Screen"+underLine,"/pvp/battlegrounds/scores-arathi.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_7=new Array(bulletImg+"Warsong Gulch"+underLine,"/pvp/battlegrounds/info-warsong.html",menuBg,3,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_7_1=new Array(bulletImg+"Power-Ups"+underLine,"/pvp/battlegrounds/powerups-warsong.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_7_2=new Array(bulletImg+"Rewards"+underLine,"/info/basics/factions/warsong/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_6_7_3=new Array(bulletImg+"Score Screen"+underLine,"/pvp/battlegrounds/scores-warsong.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_9_6_8=new Array(bulletImg+"Eye of the Storm"+underLine,"/pvp/battlegrounds/eyeofthestorm/index.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_7=new Array(bulletImg+"Horde vs Alliance FAQ"+underLine,"/info/faq/hordevalliance.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_9_8=new Array(bulletImg+"Azeroth Outdoor PvP"+underLine,"/pvp/outdoorpvp.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_9=new Array(bulletImg+"Outland Outdoor PvP"+underLine,"/pvp/worldpvp/index.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_10=new Array(bulletImg+"Halaa PvP Tips"+underLine,"/pvp/worldpvp/halaa-tips.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_9_11=new Array(bulletImg+"Rewards"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.wowarmory.com%2Fpvprewards.xml&reason=external-or-uncollected-resource",menuBg,13,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_1=new Array(bulletImg+"Armory Listing"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Farmory.worldofwarcraft.com%2Fpvprewards.xml&reason=invalid-overlay-or-uncollected-site-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_9_11_2=new Array(bulletImg+"General Rewards"+underLine,"/pvp/rewards-general.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");			
	        Menu1_9_11_3=new Array(bulletImg+"Vindicator Rewards"+underLine,"/pvp/rewards-vindicators-armor.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_4=new Array(bulletImg+"Level 60 and 70 Weapons"+underLine,"/pvp/rewards-weapons.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_5=new Array(bulletImg+"Armor Sets"+underLine,"/info/items/armorsets/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_6=new Array(bulletImg+"Mounts"+underLine,"/info/basics/mounts/special.html#pvp",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_7=new Array(bulletImg+"Alterac Valley Rewards"+underLine,"/info/basics/factions/alterac/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_8=new Array(bulletImg+"Arathi Basin Rewards"+underLine,"/info/basics/factions/arathi/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_9=new Array(bulletImg+"Warsong Gulch Rewards"+underLine,"/info/basics/factions/warsong/index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_10=new Array(bulletImg+"Hellfire PvP"+underLine,"/info/basics/factions/hellfire/hellfire-tokens.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	    	Menu1_9_11_11=new Array(bulletImg+"Zangarmarsh PvP"+underLine,"/info/basics/factions/zangarmarsh/zangarpvp.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_12=new Array(bulletImg+"Bone Wastes"+underLine,"/info/basics/factions/bonewastes/bonewastes.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_9_11_13=new Array(bulletImg+"Nagrand PvP"+underLine,"/info/basics/factions/halaa/halaa.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		
		

Menu1_10=new Array(bulletImg+"FAQ"+underLine,"/info/faq/",menuBg,29,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_1=new Array(bulletImg+"General FAQ"+underLine,"/info/faq/general.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
 	Menu1_10_2=new Array(bulletImg+"Battlegrounds"+underLine,"/pvp/battlegrounds/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_3=new Array(bulletImg+"Blizzard Downloader"+underLine,"/info/faq/blizzarddownloader.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_4=new Array(bulletImg+"Character"+underLine,"/info/faq/characters.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_5=new Array(bulletImg+"Classes"+underLine,"/info/faq/classes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_6=new Array(bulletImg+"Dungeons"+underLine,"/info/faq/dungeons.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_7=new Array(bulletImg+"Gameplay"+underLine,"/info/faq/gameplay.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_8=new Array(bulletImg+"Guide"+underLine,"/info/faq/guide.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_9=new Array(bulletImg+"Honor System"+underLine,"/pvp/honor-system-faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_10=new Array(bulletImg+"Horde vs Alliance"+underLine,"/info/faq/hordevalliance.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_11=new Array(bulletImg+"Items"+underLine,"/info/faq/items.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_12=new Array(bulletImg+"NPCs"+underLine,"/info/faq/npcs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
    Menu1_10_13=new Array(bulletImg+"Paid Character Transfer"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl02008p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_14=new Array(bulletImg+"Parental Controls"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl01917p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_15=new Array(bulletImg+"Patches"+underLine,"/info/faq/patches.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_16=new Array(bulletImg+"PTR"+underLine,"/info/faq/ptr.html","",0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_17=new Array(bulletImg+"Recruit-A-Friend"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl01997p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_18=new Array(bulletImg+"Scroll of Resurrection"+underLine,"/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl02140p&reason=external-or-uncollected-resource",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_19=new Array(bulletImg+"Quests"+underLine,"/info/faq/quests.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_20=new Array(bulletImg+"Races"+underLine,"/info/faq/races.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_21=new Array(bulletImg+"Realms"+underLine,"/info/faq/realms.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_22=new Array(bulletImg+"Skills"+underLine,"/info/faq/skills.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_23=new Array(bulletImg+"Spells"+underLine,"/info/faq/spells.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_24=new Array(bulletImg+"Support"+underLine,"/info/faq/support.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_25=new Array(bulletImg+"Technology"+underLine,"/info/faq/technology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_26=new Array(bulletImg+"Transportation"+underLine,"/info/faq/transportation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
  	Menu1_10_27=new Array(bulletImg+"World"+underLine,"/info/faq/world.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_28=new Array(bulletImg+"Burning Crusade"+underLine,"/burningcrusade/faq.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_10_29=new Array(bulletImg+"Wrath of Lich King"+underLine,"/wrath/faq.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");



Menu1_11=new Array(bulletImg+"Story"+underLine,"/info/story/index.html",menuBg,4,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_1=new Array(bulletImg+"Encyclopedia"+underLine,"/info/encyclopedia/index.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_2=new Array(bulletImg+"Timeline"+underLine,"/info/story/timeline.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_3=new Array(bulletImg+"History"+underLine,"/info/story/timeline.html",menuBg,6,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_1=new Array(bulletImg+"Chapter 1"+underLine,"/info/story/chapter1.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_2=new Array(bulletImg+"Chapter 2"+underLine,"/info/story/chapter2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_3=new Array(bulletImg+"Chapter 3"+underLine,"/info/story/chapter3.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_4=new Array(bulletImg+"Chapter 4"+underLine,"/info/story/chapter4.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_5=new Array(bulletImg+"Chapter 5"+underLine,"/info/story/chapter5.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_3_6=new Array(bulletImg+"Chapter 6"+underLine,"/info/story/chapter6.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_11_4=new Array(bulletImg+"Lore"+underLine,"/info/story/index.html#lore",menuBg,9,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_1=new Array(bulletImg+"The Murlocs"+underLine,"/misc/murloclore/murlocs.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_2=new Array(bulletImg+"Road to Damnation"+underLine,"/info/underdev/1p11/roadtodamnation.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_3=new Array(bulletImg+"Shifting Sands"+underLine,"/info/story/shiftingsands.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
		Menu1_11_4_4=new Array(bulletImg+"The Trolls"+underLine,"/info/story/troll/",menuBg,13,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_11_4_4_1=new Array(bulletImg+"History 1"+underLine,"/info/story/troll/history.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_11_4_4_2=new Array(bulletImg+"History 2"+underLine,"/info/story/troll/history2.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");	
			Menu1_11_4_4_3=new Array(bulletImg+"Biology"+underLine,"/info/story/troll/biology.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_4=new Array(bulletImg+"Trivia"+underLine,"/info/story/troll/trollsandnightelves.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_5=new Array(bulletImg+"Forest Trolls"+underLine,"/info/story/troll/foresttrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_6=new Array(bulletImg+"Forest Troll Tribes"+underLine,"/info/story/troll/foresttribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_7=new Array(bulletImg+"Jungle Trolls"+underLine,"/info/story/troll/jungletrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_8=new Array(bulletImg+"Jungle Troll Tribes"+underLine,"/info/story/troll/jungletribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_9=new Array(bulletImg+"Ice Trolls"+underLine,"/info/story/troll/icetrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_10=new Array(bulletImg+"Ice Troll Tribes"+underLine,"/info/story/troll/icetribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_11=new Array(bulletImg+"Sand Trolls"+underLine,"/info/story/troll/sandtrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_12=new Array(bulletImg+"Sand Troll Tribes"+underLine,"/info/story/troll/sandtribes.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
			Menu1_11_4_4_13=new Array(bulletImg+"Other Trolls"+underLine,"/info/story/troll/othertrolls.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_5=new Array(bulletImg+"Undead Plague"+underLine,"/info/story/undeadplague.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_6=new Array(bulletImg+"The Story So Far"+underLine,"/burningcrusade/townhall/story.html#top",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_7=new Array(bulletImg+"Shaman/Paladins"+underLine,"/burningcrusade/townhall/classcombo.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_8=new Array(bulletImg+"Unbroken"+underLine,"/info/story/unbroken/",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
		Menu1_11_4_9=new Array(bulletImg+"Rise of Lich King"+underLine,"/wrath/features/story/story.xml",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");





Menu1_12=new Array(bulletImg+"About Game Guide"+underLine,"/info/faq/guide.html",menuBg,5,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_1=new Array(bulletImg+"Archived News"+underLine,"/info/archivednews.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_2=new Array(bulletImg+"Content Index"+underLine,"/info/basics/content-index.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_3=new Array(bulletImg+"Credits"+underLine,"/info/credits.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_4=new Array(bulletImg+"Report Errors"+underLine,"/info/faq/guide.html#errors",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
	Menu1_12_5=new Array(bulletImg+"General Links"+underLine,"/info/basics/general-links.html",menuBg,0,15,125,"","","","","","",-1,-1,-1,"","");
