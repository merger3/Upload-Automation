// ==UserScript==
// @name         Upload-Automator
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

// Set to the ip:port of the flask server
const server = "http://localhost:5000";

(function() {
    'use strict';
    if (window.location.hostname == "gazellegames.net") {
        add_search_buttons()
    }

})();

function processFile(data, textStatus) {
    if (data.status == 1) {
        alert(data.msg);
    } else {
        $("#release_desc")[0].value = data.description;
        if (!$('#remaster').prop('checked')) {
            $("#remaster").click();
        }
        $("#remaster_year")[0].value = data.year;
        $("#remaster_title")[0].value = "No-Intro";
        $("#ripsrc_home").click();
        $("#release_title")[0].value = data.name;
        $("#miscellaneous")[0].value = "ROM";
        $("#region")[0].value = "ROM";
        $("#region")[0].value = data.region;
        $("#language")[0].value = data.lang;
    }

    if ($('#games_returned').length) {
        $("#games_returned").replaceWith(data.val);
    } else {
        $("#torrent_file").append(data.val);
    }

    $(".game_selection>*").css("border: 1px solid #0088ff; border-collapse: collapse; padding: 5px; font-family:Verdana;font-size:12px; text-align: left;");
    $(".select_game").click(function () {
        $.post(server + "/details", {"id": $(this).data("value")}, fillData)
    });
}

function fillData(data, textStatus) {
    if (data.status == 1) {
        alert(data.msg);
    } else {
        $("#release_desc")[0].value = data.description;
        if (!$('#remaster').prop('checked')) {
            $("#remaster").click();
        }
        $("#remaster_year")[0].value = data.year;
        $("#remaster_title")[0].value = "No-Intro";
        $("#ripsrc_home").click();
        $("#release_title")[0].value = data.name;
        $("#miscellaneous")[0].value = "ROM";
        $("#region")[0].value = "ROM";
        $("#region")[0].value = data.region;
        $("#language")[0].value = data.lang;
    }
}

function processResult (data, textStatus) {
    if ($('#games_returned').length) {
        $("#games_returned").replaceWith(data.val);
    } else {
        $("#torrent_file").append(data.val);
    }

    $(".game_selection>*").css("border: 1px solid #0088ff; border-collapse: collapse; padding: 5px; font-family:Verdana;font-size:12px; text-align: left;");
    $(".select_game").click(function () {
        $.post(server + "/details", {"id": $(this).data("value")}, fillData)
    });
}


function add_search_buttons() {
    $("#announce_uri td:nth-child(2)").css({"width": "5px"});
    $("#torrent_file td:nth-child(2)").css({"vertical-align": "top"});
    $("#announce_uri").append('<tr><td><input id="ask_redump" type="text" value=""/><input id="search" type="button" style="background-color:coral;color:black" value="Search"/><input id="torrent_fill" type="button" style="background-color:CornflowerBlue;color:black" value="Use Torrent"/><input type="checkbox" id="NoPost"  title="Check this to delay uploading" /input></td></tr>');

    $("#torrent_fill").click(function () {
        if ($("#file")[0].value == "") {
            alert("Upload a torrent file first!");
        } else {
            $.post(server + "/file", {"name": $("#file")[0].value}, processFile)
        }
    });

    $("#search").click(function () {
        $.post(server + "/data", {"name": $("#ask_redump").val()}, processResult)
    });
}