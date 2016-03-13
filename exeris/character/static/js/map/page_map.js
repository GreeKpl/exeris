FRAGMENTS.events = (function($, socket) {

    $(document).on("click", ".travel_go", function(event) {

        var travel_direction = $(".travel_direction").val();

        socket.emit("character.travel_in_direction", travel_direction, function() {
            $.publish("character:state_changed");
        });
    });

    $(document).on("click", ".travel_stop", function(event) {
        socket.emit("character.stop_travel", function() {
            $.publish("character:state_changed");
        });
    });

})(jQuery, socket);