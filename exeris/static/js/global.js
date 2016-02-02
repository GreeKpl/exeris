FRAGMENTS.global = (function($, socket) {

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

    socket.on("$.publish", function() {
        $.publish.apply(this, Array.prototype.slice.call(arguments));
    });

    $.subscribe("show_error", function(message) {
        $.notify({
            message: message
        }, {
            type: "danger",
            delay: 0
        });
    });

    $.subscribe("show_success", function(message) {
        $.notify({
            message: message
        }, {
            type: "success",
            delay: 0
        });
    });

    $.subscribe("show_notification", function(message, notification_id) {
        $.notify({
            message: message,
            url: "show_notification/" + notification_id
        }, {
            type: "info",
            delay: 0
        });
    });

    $.subscribe("get_notifications_list", function() {
        socket.emit("get_notifications_list", [], function(notifications) {
            $(".alert-info").remove();
            for (var i = 0; i < notifications.length; i++) {
                var title = notifications[i].title;
                var notification_id = notifications[i].notification_id;
                $.publish("show_notification", title, notification_id);
            }
        });
    });

    $(document).on("click", "a[href^='show_notification']", function(event) {
        event.preventDefault();
        var clicked = $(event.target);
        var parts = /show_notification\/(\d+)/.exec(clicked.attr("href"));
        if (parts) {
            socket.emit("show_notification_dialog", [parts[1]], function(notification_modal) {
                $("#notification_modal").remove();
                $(document.body).append(notification_modal);
                $("#notification_modal").modal();
            });
        }
    });

    return {};
})(jQuery, socket);
