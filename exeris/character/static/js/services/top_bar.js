FRAGMENTS.character_top_bar = (function($, socket) {

    var after_update_character_top_bar = function(code) {
        $("#character_top_bar").replaceWith(code);
    };

    $.subscribe("character:intent_state_changed", function () {
        socket.emit("character.update_top_bar", ENDPOINT_NAME, after_update_character_top_bar);
    });

    $.subscribe("character:state_changed", function () {
        socket.emit("character.update_top_bar", ENDPOINT_NAME, after_update_character_top_bar);
    });

})(jQuery, socket);

$(function() {
    $.publish("character:state_changed");
});
