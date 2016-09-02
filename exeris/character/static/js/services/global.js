FRAGMENTS.entity = (function($, socket) {

    $(document).on("click", ".character", function(event) {
        var character_node = $(event.target);
        var character_id = FRAGMENTS.entity.get_id(character_node);
        socket.emit("character.get_info", character_id, function(modal_dialog) {
            $("#character_info_modal").remove();
            $(document.body).append(modal_dialog);
            $("#character_info_modal").modal();
        });
    });


    return {
        get_id: function(element) {
            var classes = element.attr("class").split(/\s+/);
            for (var i = 0; i < classes.length; i++) {
                var class_name = /^id_(.*)$/.exec(classes[i]);
                if (class_name) {
                    return class_name[1];
                }
            }
            return null;
        }
    }
})(jQuery, socket);


FRAGMENTS.character = (function($, socket) {

    $(document).on("click", ".character_info-rename-confirm", function() {
        var character_rename_field = $(".character_info-rename-field");
        var new_remembered_name = character_rename_field.val();
        var character_id = character_rename_field.data("character-id");
        socket.emit("rename_entity", character_id, new_remembered_name, function() {
            $.publish("refresh_entity", character_id);
        });
    });

    $(document).on("click", ".character_info-show_combat", function(event) {
        var combat_id = $(event.target).val();
        socket.emit("character.combat_refresh_box", combat_id, function(rendered) {
            $("#combat_dock").html(rendered);
            $("#character_info_modal").modal("hide");
        });
    });

    $.subscribe("refresh_entity", function(entity_id) {
        socket.emit("get_entity_tag", entity_id, function(entity_id, new_data) {
            $(".id_" + entity_id).replaceWith(new_data);
        });
    });

})(jQuery, socket);
