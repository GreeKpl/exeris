FRAGMENTS.player = (function($) {

    $(document).on("click", "#create_character", function() {
        var char_name = $("#char_name").val();
        Sijax.request("create_character", [char_name]);
    });

    $.subscribe("refresh_character_list", function() {
        window.location.reload();
    });

    return {
        after_create_character: function() {
            $.publish("refresh_character_list");
        },
        after_refresh_character_list: function() {
            // not sijax call yet, so not used
        }
    };
})(jQuery);
