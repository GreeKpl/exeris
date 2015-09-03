FRAGMENTS.events = (function($) {

    var _last_event = 0;

    $.subscribe("events:refresh_list", function() {
        Sijax.request("get_new_events", [_last_event]);
    });

    return {
        update_list: function(new_events, last_event) {
            for (var i = 0; i < new_events.length; i++) {
                new_events[i] = "<li>" + new_events[i].replace(/(\*+[^*]+\*+)/g, "<b>$1</b>") + "</li>";
            }
            $(".events_list_contents > ol").prepend(new_events.reverse());
            _last_event = last_event;
        }
    };
})(jQuery);

$(function() {

    var event_refresher = function() {
        $.publish("events:refresh_list");

        setTimeout(event_refresher, 20000);
    };

    event_refresher();
});