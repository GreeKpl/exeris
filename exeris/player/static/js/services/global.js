FRAGMENTS.player = (function($, socket) {

    $.subscribe("player/pull_notifications_initial", function() {
        socket.emit("player.pull_notifications_initial");
    });

    socket.on("player.new_notification", function(notification) {

        // hide previous version of this notification
        $("[href='show_notification/" + notification.notification_id + "']").parent().remove();

        var title = notification.title + (notification.count > 1 ? " (" + notification.count + "x)" : "");
        var notification_id = notification.notification_id;
        $.publish("global/show_notification", title, notification_id);
    });

})(jQuery, socket);

$(function() {
    $.publish("player/pull_notifications_initial");
});
