FRAGMENTS.activity = (function($) {

    $.subscribe("activity:changed_participation", function () {
        Sijax.request("get_current_activity", [])
    });

    return {
        after_join: function () {
            $.publish("activity:changed_participation")
        },
        after_get_current_activity: function(code) {
            $("#current_activity").html(code);
        }
    };
})(jQuery);

$(function () {
    $.publish("activity:changed_participation");
});

$(document).on("click", ".join_activity", function(event) {
    var button = $(event.target);
    var activity_id = +button.data("activity");
    Sijax.request("join_activity", [activity_id]);
});
