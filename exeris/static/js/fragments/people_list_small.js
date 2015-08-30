FRAGMENTS.people_list_small = (function($) {

    $.subscribe("people_list_small:refresh_list", function() {
        console.log(arguments);
            Sijax.request("people_short_refresh_list", []);
    });

    $(document).on("click", ".character", function(event) {
        var character = $(event.target);
        var new_name = prompt("select new name");
        Sijax.request("rename_entity", [FRAGMENTS.global.get_id(character), new_name]);
    });

    $(document).on("click", ".select-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "speak_to", character_id);
    });

    $(document).on("click", ".select-whisper-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "whisper", character_id);
    });

    $(function() {
        $.publish("people_list_small:refresh_list");
    });

    return {
        after_refresh_list: function(code) {
            $("#people_list_small_dock").html(code);
        }
    };
})(jQuery);