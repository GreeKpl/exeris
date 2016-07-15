FRAGMENTS.map = (function($, socket) {

    $.subscribe("character:movement_info_changed", function() {
        socket.emit("character.get_movement_info", function(ret) {
            $("#control-movement-dock").html(ret);
        });
        $.publish("character:state_changed");
    });

    $(document).on("click", ".control-movement-direction-confirm", function(event) {
        var movement_direction = $(".control-movement-direction").val();

        socket.emit("character.move_in_direction", movement_direction, function() {
            $.publish("character:movement_info_changed");
        });
    });

    $(document).on("click", ".control-movement-stop", function(event) {
        socket.emit("character.stop_movement", function() {
            $.publish("character:movement_info_changed");
        });
    });

})(jQuery, socket);

$.publish("character:movement_info_changed");
