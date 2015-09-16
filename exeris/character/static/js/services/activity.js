FRAGMENTS.activity = (function($) {

    $(document).on("click", ".join_activity", function(event) {
        var button = $(event.target);
        var activity_id = +button.data("activity");
        Sijax.request("join_activity", [activity_id]);
    });

    return {
        after_join: function () {
            $.publish("character:activity_participation_changed")
        }
    };
})(jQuery);