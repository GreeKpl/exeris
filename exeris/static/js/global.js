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

    socket.on("global.show_error", function(error_message) {
        $.publish("global/show_error", error_message);
    });


    $.subscribe("global/show_error", function(message) {
        $.notify({
            message: message
        }, {
            type: "danger",
            delay: 0
        });
    });

    $.subscribe("global/show_success", function(message) {
        $.notify({
            message: message
        }, {
            type: "success",
            delay: 0
        });
    });

    $.subscribe("global/show_notification", function(message, notification_id, show_close_on_popup) {
        var show_close_on_popup = typeof show_close_on_popup !== 'undefined' ? show_close_on_popup : false;
        $.notify({
            message: message,
            url: "show_notification/" + notification_id
        }, {
            type: "info",
            delay: 0,
            allow_dismiss: show_close_on_popup
        });
    });

    $(document).on("click", "a[href^='show_notification']", function(event) {
        event.preventDefault();
        var clicked = $(event.target);
        var parts = /show_notification\/(\d+)/.exec(clicked.attr("href"));
        if (parts) {
            socket.emit("notification.show_modal", parts[1], function(notification_modal) {
                $("#notification_modal").remove();
                $(document.body).append(notification_modal);
                $("#notification_modal").modal();
            });
        }
    });

    $(document).on("click", ".notification_option", function(event) {
        var button = $(event.target);
        var args_list = [button.data("endpoint")].concat(button.data("params")).concat([
            function() { // delete from UI if the selected option was accepted by the server
                var notification_id = $("#notification_modal").data("notification_id");
                $("a[href='show_notification/" + notification_id + "'").closest("div.alert").remove();
                $("#notification_modal").modal("hide");
            }]);
        socket.emit.apply(socket, args_list);
    });

    $(document).on("click", "button.close", function(event) { // request to remove notification on server when X clicked
        var closeButton = $(event.target);
        var notificationUrl = closeButton.siblings("a[data-notify='url']").attr("href");
        var parts = /show_notification\/(\d+)/.exec(notificationUrl);
        if (parts) {
            var notification_id = parts[1];
            socket.emit("notification.close", notification_id);
        }
    });

    return {};
})(jQuery, socket);
