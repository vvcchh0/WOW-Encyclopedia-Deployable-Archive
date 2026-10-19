
    window.onload = init;
    document.getElementsByTagName("body")[0].className = (topList_conf_vars[0] != "") ? topList_conf_vars[0] : "wide";
    $('intro').innerHTML = introText;
    $('browseAll').getElementsByTagName("span")[0].innerHTML = labelBrowseGlobal;
    $("browseAll").style.display = (topList_conf_vars[2] > 1) ? "inline" : "none";;
    $('numTablesSelector').firstChild.innerHTML = labelNumberOfDays;
    $('searchContainer').firstChild.innerHTML = labelSearch;
