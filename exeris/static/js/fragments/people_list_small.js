FRAGMENTS.people_list_small = (function($) {

    $(EVENTS).on("people_list_small:refresh_list", function() {
            Sijax.request("people_list_small_refresh", []);
    });

    $(document).on("click", ".character", function(event) {
        var character = $(event.target);
        var new_name = prompt("select new name");
        Sijax.request("rename_entity", [FRAGMENTS.global.get_id(character), new_name]);
    });

    $(function() {
        EVENTS.trigger("people_list_small:refresh_list");
    });
    return {
        build: function(code) {
            $("#people_list_small_dock").html(code);
        }
    };
})(jQuery);