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


    /**
        It's a very simple event bus

        How to register for CUSTOM_EVENT
        $.subscribe("CUSTOM_EVENT", function(arg0, arg1) {
            ...
        });

        How to publish CUSTOM_EVENT:
        $.publish("CUSTOM_EVENT", arg0, arg1);
    */

    var FRAGMENTS = {};

    $.subscribe("refresh_entity", function(entity_id) {
        Sijax.request("get_entity_tag", [entity_id]);
    });

    return {
        get_id: function(element) {
            var classes = element.attr("class").split(/\s+/);
            for (var i = 0; i < classes.length; i++) {
                var class_name = /^id_(.*)$/.exec(classes[i]);
                if (class_name) {
                    return +class_name[1];
                }
            }
            return null;
        },
        alter_entity: function(entity_id, new_data) {
            $(".id_" + entity_id).replaceWith(new_data);
        }
    };
})(jQuery);
