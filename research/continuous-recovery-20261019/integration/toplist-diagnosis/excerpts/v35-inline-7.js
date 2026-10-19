
var lang = category = "";
var query = window.location.search.substring(1);
var vars = query.split("&");
for (var i = 0;i < vars.length; i++) {
    var pair = vars[i].split(",");
}
if (pair[0] != "") { lang = pair[0] };
if (pair[1] != "") { category = pair[1] };

if(is_opera) document.write('<link rel="stylesheet" type="text/css" href="/WOW-Encyclopedia-Deployable-Archive/toplist/includes-client/css/additional_opera.css" media="screen, projection" />');
