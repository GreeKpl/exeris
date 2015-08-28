FRAGMENTS.people_list_small = (function($, EVENTS) {

    $(EVENTS).on("people_list_small:refresh_list", function() {
            Sijax.request("people_list_small_refresh", []);
    });

    $(function() {
        EVENTS.trigger("people_list_small:refresh_list");
    });
    return {
        build: function(code) {
            $("#people_list_small_dock").html(code);
        }
    };
})(jQuery, EVENTS);