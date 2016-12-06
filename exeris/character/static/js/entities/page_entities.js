FRAGMENTS.entities = (function($, socket) {

    $.subscribe("entities:refresh_list", function() {
        socket.emit("entities_refresh_list", entities_to_show, function(locations) {
            var entities_root = $("#entities_root > ol");
            entities_root.empty();
            $.each(locations, function(idx, location_info) {
                entities_root.append($("<li></li>").append(location_info.html));
            });

            $("#entities_root .entity_info").first().find("button.expand_subtree").click();
        });
    });

    $.subscribe("entities:refresh_entity_info", function(entity_id) {
        socket.emit("refresh_entity_info", entity_id, function(entity_info) {
            var old_entity_info = $("div[data-entity='" + entity_id + "']");
            if (entity_info) {
                old_entity_info.replaceWith(entity_info.html);
            } else {
                old_entity_info.parent().remove();
            }
        });
    });

    $(document).on("click", ".expand_subtree", function(event) {
        var entity_node = $(event.target).closest(".entity_info");
        var entity_id = entity_node.data("entity");
        if (entity_node.data("other-side")) {
            entity_id = entity_node.data("other-side");
        }

        var entity_parent = entity_node.parent().closest(".entity_info");
        socket.emit("entities_get_sublist", entity_id, entity_parent.data("entity"), function(parent_id, entities) {
            var list = $("<ol></ol>");
            $.each(entities, function(idx, entity_info) {
                list.append($("<li>" + entity_info.html + "</li>"));
            });
            var parent = $("div[data-entity='" + parent_id + "']");
            if (parent.length == 0) { // todo handling other-side
                parent = $("div[data-other-side='" + parent_id + "']");
            }
            parent.append(list);
            parent.children(".expand_subtree").text("/\\").addClass("collapse_subtree").removeClass("expand_subtree");
        });
    });

    $(document).on("click", ".collapse_subtree", function(event) {
        var entity_id = $(event.target).closest(".entity_info").data("entity");

        socket.emit("collapse_entity", entity_id, function(entity_id) {
            var parent = $("div[data-entity='" + entity_id + "']");
            parent.find("ol").remove();
            parent.children(".collapse_subtree").text("\\/").addClass("expand_subtree").removeClass("collapse_subtree");
        });
    });

    $(document).on("click", "#confirm_edit_readable", function(event) {
        var new_text = $("#edit_readable_text").val();
        var entity_id = $(event.target).data("entity");
        socket.emit("edit_readable", entity_id, new_text);

        $("#edit_readable_modal, #readable_modal").modal("hide");
    });

    $(document).on("click", ".entity_action", function(event) {
        var target = $(event.target);

        var endpoint = target.data("action");
        var entity_id = target.data("entity");
        socket.emit(endpoint, entity_id);
    });

    $(document).on("click", "#readable_edit", function(event) {
        var entity_id = $(event.target).data("entity");

        $("#edit_readable_modal").modal();
    });

    $(document).on("click", "#add_to_activity_confirm", function(event) {
        var entity_to_add = $("#add_to_activity").data("entity_to_add");
        var amount = +$("#add_to_activity_amount").val();
        var activity_id = $("#selected_activity").find(":selected").val();

        socket.emit("add_item_to_activity", entity_to_add, amount, activity_id, function() {
            $("#add_to_activity").modal("hide");
            $.publish("entities:refresh_list");
        });
    });

    socket.on("before_take_item", function(item_id, max_amount) {
        var amount = +prompt("amount to take", max_amount);
        if (amount) {
            socket.emit("character.take_item", item_id, amount);
        }
    });

    socket.on("after_take_item", function(item_id) {
        $.publish("entities:refresh_entity_info", item_id);
    });

    socket.on("before_drop_item", function(item_id, max_amount) {
        var amount = +prompt("amount to drop", max_amount);
        if (amount) {
            socket.emit("inventory.drop_item", item_id, amount);
        }
    });

    socket.on("after_drop_item", function(item_id) {
        $.publish("entities:refresh_entity_info", item_id);
    });

    socket.on("before_eat", function(entity_id, max_amount) {
        var amount = +prompt("amount to eat", max_amount);
        if (amount) {
            socket.emit("eat", entity_id, amount);
        }
    });

    socket.on("after_move_to_location", function(loc_id) {
        $.publish("location_changed");
        $.publish("entities:refresh_list");
    });

    socket.on("after_open_readable_contents", function(modal_dialog) {
        $("#readable_modal, #edit_readable_modal").remove();
        $(document.body).append(modal_dialog);
        $("#readable_modal").modal();
    });

    socket.on("after_edit_readable", function(entity_id) {
        alert("text updated!");
    });

    socket.on("after_form_add_item_to_activity", function(modal_dialog) {
        $("#add_to_activity").remove();
        $(document.body).append(modal_dialog);
        $("#add_to_activity").modal();
    });

    socket.on("after_toggle_closeable", function(entity_id) {
        $.publish("entities:refresh_entity_info", entity_id);
    });

    socket.on("after_attack_character", function(entity_id) {
        $.publish("character:intent_state_changed");
    });
})
(jQuery, socket);

$(function() {
    $.publish("entities:refresh_list");
});
