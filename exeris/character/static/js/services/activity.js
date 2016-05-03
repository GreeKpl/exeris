FRAGMENTS.activity = (function($, socket) {

    $(document).on("click", ".join_activity", function(event) {
        var button = $(event.target);
        var activity_id = button.data("activity");
        socket.emit("join_activity", activity_id, function() {
            $.publish("character:intent_state_changed")
        });
    });

    return {};
})(jQuery, socket);