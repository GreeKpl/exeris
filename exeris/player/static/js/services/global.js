FRAGMENTS.player = (function($, socket) {

    $.subscribe("player/pull_notifications_initial", function() {
        socket.emit("player.pull_notifications_initial");
    });

    socket.on("player.new_notification", function(notification) {
        var title = notification.title;
        var notification_id = notification.notification_id;
        $.publish("global/show_notification", title, notification_id);
    });

})(jQuery, socket);

$(function() {
    $.publish("player/pull_notifications_initial");
});
