// awb512-119-u
	var linkClass="subMenuLink";//defines initial css class of the links
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
	var UnfoldDelay2=200;			// delay before sub builds
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
						// when your BaseHref= "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.MyDomain%2F&reason=external-or-uncollected-resource" and a link in the menu is "subdir/MyFile.htm",
						// the script renders to: "/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.MyDomain%2Fsubdir%2FMyFile.htm&reason=external-or-uncollected-resource"
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



	
Menu1=new Array("WoW Main","/","/WOW-Encyclopedia-Deployable-Archive/shared/wow-com/images/subnav/button_bg.gif",8,15,110,"","","","","","",-1,-1,-1,"","");

	Menu1_1=new Array(bulletImg+"News"+underLine,"/","",2,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_1_1=new Array(bulletImg+"Current News"+underLine,"/","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_1_2=new Array(bulletImg+"Guide News"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
	
	Menu1_2=new Array(bulletImg+"Account"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2F&reason=external-or-uncollected-resource","",16,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_1=new Array(bulletImg+"Account Creation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fsignup.worldofwarcraft.com%2F&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_2=new Array(bulletImg+"Account Summary"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2F&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_3=new Array(bulletImg+"Change Password"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fchange-password.html&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_4=new Array(bulletImg+"Change Contact Info"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcontactinfo.html&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_5=new Array(bulletImg+"Setup Subscription"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fsubscription.html&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_6=new Array(bulletImg+"Add Game Time Code"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fgamecard.html&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_7=new Array(bulletImg+"Payment History"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fpayment-history.html&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_8=new Array(bulletImg+"Account Name Retrieval"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Floginsupport%2Faccount-name.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_9=new Array(bulletImg+"Password Retrieval"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Floginsupport%2Fpassword.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");

                Menu1_2_10=new Array(bulletImg+"Paid Name Change"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-namechange-intro.html&reason=external-or-uncollected-resource","",3,15,120,"","","","","","",-1,-1,-1,"","");
			Menu1_2_10_1=new Array(bulletImg+"Change Name"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-namechange-intro.html&reason=external-or-uncollected-resource","",0,15,120,"","","","","","",-1,-1,-1,"","");
			Menu1_2_10_2=new Array(bulletImg+"Transactions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-namechange-status.html&reason=external-or-uncollected-resource","",0,15,120,"","","","","","",-1,-1,-1,"","");
			Menu1_2_10_3=new Array(bulletImg+"F.A.Q."+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fus.blizzard.com%2Fsupport%2Farticle.xml%3FarticleId%3D21532&reason=external-or-uncollected-resource","",0,15,120,"","","","","","",-1,-1,-1,"","");
		Menu1_2_11=new Array(bulletImg+"Paid Char Transfer"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-transfer-intro.html&reason=external-or-uncollected-resource","",3,15,120,"","","","","","",-1,-1,-1,"","");
			Menu1_2_11_1=new Array(bulletImg+"Move Characters"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-transfer.html&reason=external-or-uncollected-resource","",0,15,120,"","","","","","",-1,-1,-1,"","");
			Menu1_2_11_2=new Array(bulletImg+"Transactions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-transfer-status.html&reason=external-or-uncollected-resource","",0,15,120,"","","","","","",-1,-1,-1,"","");
            Menu1_2_11_3=new Array(bulletImg+"F.A.Q."+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F%3Fid%3Dabl02008p&reason=external-or-uncollected-resource","",0,15,120,"","","","","","",-1,-1,-1,"","");
        Menu1_2_12=new Array(bulletImg+"Character Move"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-move.html&reason=invalid-overlay-or-uncollected-site-resource","",3,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_2_12_1=new Array(bulletImg+"Move a Character"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-move.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");		
			Menu1_2_12_2=new Array(bulletImg+"Eligible Realms"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-move-eligible-realms.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");		
			Menu1_2_12_3=new Array(bulletImg+"Character Move Status"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fcharacter-move-history-list.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");		
		Menu1_2_13=new Array(bulletImg+"PTR Character Copy"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Ftest.worldofwarcraft.com%2Fptr%2F&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_14=new Array(bulletImg+"Parental Controls"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fparental-control-schedule.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_15=new Array(bulletImg+"Recruit-a-Friend"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Frecruit-a-friend.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_2_16=new Array(bulletImg+"Scroll of Resurr."+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2Fresurrect-a-friend.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");



	Menu1_3=new Array(bulletImg+"Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html","",10,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_1=new Array(bulletImg+"Game Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_2=new Array(bulletImg+"Introduction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#introduction","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_3=new Array(bulletImg+"Getting Started"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#gettingstarted","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_4=new Array(bulletImg+"Character"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#character","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_5=new Array(bulletImg+"Items"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#items","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_6=new Array(bulletImg+"World Locations"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#world","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_7=new Array(bulletImg+"Transportation"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#transportation","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_8=new Array(bulletImg+"Player Interaction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#playerinteraction","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_9=new Array(bulletImg+"Player vs Player"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/index.html#pvp","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_3_10=new Array(bulletImg+"FAQ"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/faq/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
				
	Menu1_4=new Array(bulletImg+"Workshop"+underLine,"/","",7,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_4_1=new Array(bulletImg+"PvP Rankings"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_4_2=new Array(bulletImg+"Talent Calculators"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/classes/talent-index/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_4_3=new Array(bulletImg+"Events Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/events/calendar/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_4_4=new Array(bulletImg+"Raid Calendar"+underLine,"/WOW-Encyclopedia-Deployable-Archive/calendar/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_4_5=new Array(bulletImg+"World Map"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/flashmap/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_4_6=new Array(bulletImg+"PvP Minisite"+underLine,"/WOW-Encyclopedia-Deployable-Archive/pvp/flash-rewards/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_4_7=new Array(bulletImg+"War Effort Ranking"+underLine,"/WOW-Encyclopedia-Deployable-Archive/wareffort/servers.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			
	Menu1_5=new Array(bulletImg+"Forums"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2F&reason=invalid-overlay-or-uncollected-site-resource","",22,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_1=new Array(bulletImg+"Forums Introduction"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fforums%2Fintro.shtml&reason=external-or-uncollected-resource","",6,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_1_1=new Array(bulletImg+"Code of Conduct"+underLine,"/WOW-Encyclopedia-Deployable-Archive/policy/forum-coc.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_1_2=new Array(bulletImg+"Getting Started"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fforums%2Fgettingstarted.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_1_3=new Array(bulletImg+"Forum Features"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fforums%2Ffeatures.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_1_4=new Array(bulletImg+"Forum Icons"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fforums%2Ficoninfo.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_1_5=new Array(bulletImg+"BML"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fforums%2Fbml.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_1_6=new Array(bulletImg+"Report Forum Violators"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fforums%2Freportforumviolators.shtml&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_2=new Array(bulletImg+"Complete List"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2F&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_3=new Array(bulletImg+"Realm Status"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11113%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_4=new Array(bulletImg+"Technical Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11110%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_5=new Array(bulletImg+"Customer Service"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11112%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_6=new Array(bulletImg+"UI & Macros"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11114%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_7=new Array(bulletImg+"Bug Reports"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10023%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_8=new Array(bulletImg+"Public Test Realm"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11572%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_9=new Array(bulletImg+"Classes"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2F&reason=invalid-overlay-or-uncollected-site-resource","",9,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_1=new Array(bulletImg+"Druid"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10015%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_2=new Array(bulletImg+"Hunter"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10016%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_3=new Array(bulletImg+"Mage"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10017%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_4=new Array(bulletImg+"Rogue"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10020%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_5=new Array(bulletImg+"Shaman"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10021%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_6=new Array(bulletImg+"Paladin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10018%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_7=new Array(bulletImg+"Priest"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10019%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_8=new Array(bulletImg+"Warrior"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10022%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_5_9_9=new Array(bulletImg+"Warlock"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10014%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_10=new Array(bulletImg+"Professions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11116%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_11=new Array(bulletImg+"PvP Discussion"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11117%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_12=new Array(bulletImg+"Quest Discussion"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11118%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_13=new Array(bulletImg+"Realm Forums"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fchild-forum.html%3FforumId%3D11119%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_14=new Array(bulletImg+"Off-Topic"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11121%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_15=new Array(bulletImg+"Guild Recruitment"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11123%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_16=new Array(bulletImg+"Guild Relations"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11124%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_17=new Array(bulletImg+"Blizzard Archive"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11120%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_18=new Array(bulletImg+"Suggestions"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11122%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_19=new Array(bulletImg+"Role-Playing"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11125%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_20=new Array(bulletImg+"Raid and Dungeon Discussion"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D11126%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_21=new Array(bulletImg+"Trading Card Game"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fentertainment.upperdeck.com%2Fwow%2Fcommunity%2Fforums%2Fdefault.aspx&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_5_22=new Array(bulletImg+"General Discussion"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2Fboard.html%3FforumId%3D10001%26sid%3D1&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");

	Menu1_6=new Array(bulletImg+"Community"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/index.html","",11,15,110,"","","","","","",-1,-1,-1,"",""); 
		Menu1_6_1=new Array(bulletImg+"Forums"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fforums.worldofwarcraft.com%2F&reason=invalid-overlay-or-uncollected-site-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_2=new Array(bulletImg+"Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics.html","",25,15,110,"","","","","","",-1,-1,-1,"","");
		    Menu1_6_2_1=new Array(bulletImg+"April, 2008 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2008-04.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_2=new Array(bulletImg+"March, 2008 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2008-03.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_3=new Array(bulletImg+"February, 2008 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2008-02.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_4=new Array(bulletImg+"January, 2008 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2008-01.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_5=new Array(bulletImg+"December, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-12.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_6=new Array(bulletImg+"November, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-11.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		    Menu1_6_2_7=new Array(bulletImg+"October, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-10.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		    Menu1_6_2_8=new Array(bulletImg+"September, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-09.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		 	Menu1_6_2_9=new Array(bulletImg+"August, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-08.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_10=new Array(bulletImg+"July, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-07.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		    Menu1_6_2_11=new Array(bulletImg+"June, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-06.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_12=new Array(bulletImg+"May, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-05.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_13=new Array(bulletImg+"April, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-04.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_14=new Array(bulletImg+"March, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-03.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_15=new Array(bulletImg+"February, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-02.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_16=new Array(bulletImg+"January, 2007 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2007-01.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_17=new Array(bulletImg+"December, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-12.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_18=new Array(bulletImg+"November, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-11.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_19=new Array(bulletImg+"October, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-10.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_20=new Array(bulletImg+"September, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-09.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_21=new Array(bulletImg+"August, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-08.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_22=new Array(bulletImg+"July, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-07.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_23=new Array(bulletImg+"June, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-06.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_24=new Array(bulletImg+"May, 2006 Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/comics/2006-05.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_2_25=new Array(bulletImg+"PA Comics"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/pa-comics.html","",0,15,110,"","","","","","",-1,-1,-1,"","");	
			
		Menu1_6_3=new Array(bulletImg+"Community Spotlight"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/communitylinks.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_4=new Array(bulletImg+"Contests"+underLine,"/WOW-Encyclopedia-Deployable-Archive/contests/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_5=new Array(bulletImg+"Machinima"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/machinima/index.html","",3,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_1=new Array(bulletImg+"Welcome"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/machinima/welcome.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_2=new Array(bulletImg+"Fair-Use Guide"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/machinima/letter.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_5_3=new Array(bulletImg+"Movies"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/machinima/movies.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6=new Array(bulletImg+"Guild Relations"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/guildrelations.html","",1,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_6_1=new Array(bulletImg+"Guild Nexus"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/guildnexus.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_7=new Array(bulletImg+"Player Stories"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/stories/index.xml.html","",3,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_7_1=new Array(bulletImg+"Current Stories"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/stories/stories.xml.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_7_2=new Array(bulletImg+"Story Archive"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/stories/archive.xml.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_7_3=new Array(bulletImg+"Submit a Story"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/stories/submit.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_8=new Array(bulletImg+"Real-Life Events"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/reallifeevents.html","",3,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_8_1=new Array(bulletImg+"Blizzard Regionals"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/tournaments/euregionals/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_8_2=new Array(bulletImg+"Lanwar '06"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/tournaments/lanwar.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_6_8_3=new Array(bulletImg+"CPL '06"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/tournaments/cpl.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_9=new Array(bulletImg+"Fan Art"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fus%2Finblizz%2Ffanart%2FScreenShot.html&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_10=new Array(bulletImg+"Fan Wallpapers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/wallpapers/fan-wallpapers/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_6_11=new Array(bulletImg+"Fan Sites"+underLine,"/WOW-Encyclopedia-Deployable-Archive/community/fansites.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		
	Menu1_7=new Array(bulletImg+"Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowindex%2F&reason=external-or-uncollected-resource","",8,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_1=new Array(bulletImg+"Support News"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowindex%2F&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_2=new Array(bulletImg+"Account Admin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowaa%2F&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_3=new Array(bulletImg+"Billing & Account"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowbilling%2F&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_4=new Array(bulletImg+"Technical Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwow%2F&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_5=new Array(bulletImg+"In-Game Support"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowgm%2F&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_6=new Array(bulletImg+"Policies"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwowgm%2F%3Fid%3Dagm01712p&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_7=new Array(bulletImg+"Blizzard Store"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fmarket.shtml&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_7_8=new Array(bulletImg+"Support Tools"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fwww.blizzard.com%2Fsupport%2Fwow%2F%3Fid%3Daww01669p&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");

	Menu1_8=new Array(bulletImg+"Media"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/index.html","",9,15,110,"","","","","","",-1,-1,-1,"",""); 
		Menu1_8_1=new Array(bulletImg+"Complete List"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_8_2=new Array(bulletImg+"Screenshots"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/ssotd/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");				        
		Menu1_8_3=new Array(bulletImg+"Movies"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/movies.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_8_4=new Array(bulletImg+"Music"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/sounds.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_8_5=new Array(bulletImg+"Wallpapers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/wallpapers.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_8_6=new Array(bulletImg+"Fan Wallpapers"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/wallpapers/fan-wallpapers/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_8_7=new Array(bulletImg+"Other Downloads"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/other-downloads.html","",6,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_8_7_1=new Array(bulletImg+"Lords of the Dance"+underLine,"/WOW-Encyclopedia-Deployable-Archive/info/races/dancing.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_8_7_2=new Array(bulletImg+"Media Player Skin"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/other-downloads.html#skins","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_8_7_3=new Array(bulletImg+"Desktop Theme"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/other-downloads.html#themes","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_8_7_4=new Array(bulletImg+"Custom UI Toolkit"+underLine,"/WOW-Encyclopedia-Deployable-Archive/ui/index.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_8_7_5=new Array(bulletImg+"Language Pack"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/languagepack-en.xml.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
			Menu1_8_7_6=new Array(bulletImg+"Paquete de Idiomas"+underLine,"/WOW-Encyclopedia-Deployable-Archive/downloads/languagepack-es.xml.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_8_8=new Array(bulletImg+"Gadgetzan Times"+underLine,"/WOW-Encyclopedia-Deployable-Archive/gadgetzan/archives.html","",0,15,110,"","","","","","",-1,-1,-1,"","");
		Menu1_8_9=new Array(bulletImg+"BlizzCast"+underLine,"/WOW-Encyclopedia-Deployable-Archive/__offline/empty.js?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fshared%2Fwow-com%2Fincludes-client%2Fnavtree-main.js&requested=http%3A%2F%2Fus.blizzard.com%2Fblizzcast%2F&reason=external-or-uncollected-resource","",0,15,110,"","","","","","",-1,-1,-1,"","");


