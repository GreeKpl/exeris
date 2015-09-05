FRAGMENTS.people_short = (function($) {

    var SELECTED_SPEAKER = "#say_to_all";

    var change_listener = function (new_speaker_selector) {
        console.log("ROBIE TO DLA " + new_speaker_selector);
        $(SELECTED_SPEAKER).removeClass("btn-primary").addClass("btn-default");
        SELECTED_SPEAKER = new_speaker_selector;
        $(SELECTED_SPEAKER).removeClass("btn-default").addClass("btn-primary");
    };

    $.subscribe("people_short:refresh_list", function() {
        Sijax.request("people_short_refresh_list", []);
    });

    $(document).on("click", ".character", function(event) {
        var character = $(event.target);
        var new_name = prompt("select new name");
        Sijax.request("rename_entity", [FRAGMENTS.character.get_id(character), new_name]);
    });

    $(document).on("click", ".select-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "SAY_TO_SOMEBODY", character_id);
        change_listener(".id_" + character_id + " ~ .select-listener");
    });

    $(document).on("click", ".select-whisper-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "WHISPER", character_id);
        change_listener(".id_" + character_id + " ~ .select-whisper-listener");
    });

    $(document).on("click", "#say_to_all", function(event) {
        $.publish("speaking:change_listener", "PUBLIC");
        change_listener("#say_to_all");
    });


    $(function() {
        $.publish("people_short:refresh_list");
    });

    return {
        after_refresh_list: function(code) {
            $("#people_short_dock").html(code);
            change_listener(SELECTED_SPEAKER);
        }
    };
})(jQuery);