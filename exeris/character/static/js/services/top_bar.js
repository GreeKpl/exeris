FRAGMENTS.top_bar = (function($) {

    $.subscribe("character:activity_participation_changed", function () {
        Sijax.request("update_top_bar", [])
    });

    $.subscribe("character:state_changed", function () {
        Sijax.request("update_top_bar", [])
    });

    return {
        after_update_top_bar: function(code) {
            $("#top_bar").replaceWith(code);
        }
    };
})(jQuery);

$(function() {
    $.publish("character:activity_participation_changed");
});