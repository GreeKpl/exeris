FRAGMENTS.player = (function($) {

    $(document).on("click", "#create_character", function() {
        var char_name = $("#char_name").val();
        socket.emit("create_character", [char_name], function() {
            $.publish("player/character_added");
        });
    });

})(jQuery);
