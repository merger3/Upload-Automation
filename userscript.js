// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://gazellegames.net/upload.php*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=for-blake.com
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_deleteValue
// @grant        GM_listValues
// @grant        GM_addStyle
// @require      https://code.jquery.com/jquery-3.1.0.min.js
// ==/UserScript==


//$(this).data("value"))

(function() {
    'use strict';
    if (window.location.hostname == "gazellegames.net") {
        add_search_buttons()
    }

})();

function fillData(data, textStatus) {
    $("#release_desc")[0].value = data.val;
}

function processResult (data, textStatus) {
    //const obj = JSON.parse(data);
	console.log(data);
	//alert(data.val);
    if ($('#games_returned').length) {
       $("#games_returned").replaceWith(data.val);
    } else {
        $("#torrent_file").append(data.val);
    }

    $(".game_selection>*").css("border: 1px solid #0088ff; border-collapse: collapse; padding: 5px; font-family:Verdana;font-size:12px; text-align: left;");
    $(".select_game").click(function () {
       $.post("http://192.168.0.33:5000/details", {"id": $(this).data("value")}, fillData)
       //$("#release_desc")[0].value = desc;
       //alert($(this).data("value"))
    });

}


function add_search_buttons() {
    $("#announce_uri td:nth-child(2)").css({"width": "5px"});
    $("#torrent_file td:nth-child(2)").css({"vertical-align": "top"});
    $("#announce_uri").append('<tr><td><input id="ask_redump" type="text" value=""/><input id="search" type="button" style="background-color:coral;color:black" value="Fill form"/><input type="checkbox" id="NoPost"  title="Check this to delay uploading" /input></td></tr>');


    $("#search").click(function () {
       $.post("http://192.168.0.33:5000/data", {"name": $("#ask_redump").val()}, processResult)
    });
}