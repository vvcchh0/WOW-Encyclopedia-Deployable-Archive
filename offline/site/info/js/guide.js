// Game Guide Generic JS

current_ss = 0; total_ss = 5; 
function shotnav(val)
{ current_ss += (val)?-1:1; if(current_ss > total_ss) { current_ss = 1 } if(current_ss <= 0){current_ss = total_ss} 
zpair = (current_ss < 10)?"0":"";  
ss = document.getElementById("scrnshot")
ss.getElementsByTagName("a")[0].href = "";
ss.getElementsByTagName("img")[0].src = "../images/screenshots/"+current_dungeon+"_" + zpair + current_ss + "_thumb.jpg";
document.getElementById("ss_output").innerHTML = current_ss + " of " + total_ss
}

function wingchange(targ,num)
{ // alert(targ.parentNode.parentNode.className)
 //alert(targ.parentNode.parentNode.getElementsByTagName('span').length);
 spns = targ.parentNode.parentNode.getElementsByTagName('span')
 for(i=0;i<spns.length;i++){ spns[i].style.display = "none" } spns[num-1].style.display = "block" 
	}