FRAGMENTS.global = (function($) {

    var EVENTS = $({});

    $.publish = function() {
        var event_name = arguments[0];
        var args = Array.prototype.slice.call(arguments, 1);
        EVENTS.trigger.call(EVENTS, event_name, args);
    };

    $.subscribe = function(event_name, handler) {
        EVENTS.on(event_name, function() {
            var args_without_event = Array.prototype.slice.call(arguments, 1);
            handler.apply(EVENTS, args_without_event);
        });
    };

    /*
        It's a very simple event bus

        > How to register for CUSTOM_EVENT
        $.subscribe("CUSTOM_EVENT", function(arg0, arg1) {
            ...
        });

        > How to publish CUSTOM_EVENT:
        $.publish("CUSTOM_EVENT", arg0, arg1);

     */

    $.subscribe("show_error", function(message) {
            $.notify({
                message: message
            },{
                type: "danger",
                delay: 0
            });
        });

    return {
    };
})(jQuery);
