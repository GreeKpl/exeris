FRAGMENTS.people_short = (function($) {

    $.subscribe("people_short:refresh_list", function() {
        Sijax.request("people_short_refresh_list", []);
    });

    $(document).on("click", ".character", function(event) {
        var character = $(event.target);
        var new_name = prompt("select new name");
        Sijax.request("rename_entity", [FRAGMENTS.global.get_id(character), new_name]);
    });

    $(document).on("click", ".select-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "SAY_TO_SOMEBODY", character_id);
    });

    $(document).on("click", ".select-whisper-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "WHISPER", character_id);
    });

    $(function() {
        $.publish("people_short:refresh_list");
    });

    return {
        after_refresh_list: function(code) {
            $("#people_short_dock").html(code);
        }
    };
})(jQuery);