FRAGMENTS.combat = (function($, socket) {

    $.subscribe("character:update_combat", function() {
        $.publish("combat:show_combat");
    });

    $.subscribe("combat:show_combat", function(combat_id) {
        if ($("#combat_dock")) {
            socket.emit("character.combat_refresh_box", combat_id, function(rendered) {
                $("#combat_dock").html(rendered);
            });
        }
    });

    $(document).on("click", ".combat_stance", function(event) {
        socket.emit("character.combat_change_stance", $(event.target).val(), function() {
            $.publish("character:update_combat");
        });
    });

    $(document).on("click", ".combat_join", function(event) {
        var combat_id = $("#combat-box").data("id");
        var side_to_join = $(event.target).val();
        socket.emit("combat.join_side", combat_id, side_to_join, function() {
            $.publish("character:update_combat");
        });
    });

    return {};
})(jQuery, socket);

$(function() {
    $.publish("character:update_combat");
});
