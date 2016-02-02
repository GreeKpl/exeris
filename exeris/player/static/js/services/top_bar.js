FRAGMENTS.player_top_bar = (function($, socket) {

    var after_update_player_top_bar = function(code) {
        $("#player_top_bar").replaceWith(code);
    };

    $.subscribe("player/character_added", function() {
        $.publish("player/character_list_changed");
    });

    $.subscribe("player/character_list_changed", function () {
        socket.emit("player.update_top_bar", [CURRENT_CHARACTER_ID], after_update_player_top_bar);
    });

})(jQuery, socket);

$(function() {
    $.publish("player/character_list_changed");
});
