FRAGMENTS.entities = (function($) {

    $.subscribe("entities:refresh_list", function () {
        Sijax.request("entities_refresh_list", []);
    });
    
    $(document).on("click", ".expand", function(event) {
        var entity_node = $(event.target).closest(".entity_wrapper");
        var entity_id = entity_node.data("entity");

        Sijax.request("entities_get_sublist", [entity_id, null]);
    });

    $(document).on("click", ".subtree-collapse", function(event) {
        var entity_id = $(event.target).closest(".entity_wrapper").data("entity");

        Sijax.request("collapse_entity", [entity_id]);
    });
    
    $(document).on("click", "#confirm_edit_readable", function(event) {
        var new_text = $("#edit_readable_text").val();
        var entity_id = $(event.target).data("entity");
        Sijax.request("edit_readable", [entity_id, new_text]);

        $("#edit_readable_modal, #readable_modal").modal("hide");
    });

    $(document).on("click", ".entity-action", function (event) {
        var target = $(event.target);

        var endpoint = target.data("action");
        var entity_id = target.data("entity");
        Sijax.request(endpoint, [entity_id]);
    });

    $(document).on("click", "#readable_edit", function(event) {
        var entity_id = $(event.target).data("entity");

        $("#edit_readable_modal").modal();
    });

    $(document).on("click", "#add_to_activity_confirm", function(event) {
        var entity_to_add = $("#add_to_activity").data("entity_to_add");
        var amount = +$("#add_to_activity_amount").val();
        var activity_id = $("#selected_activity").find(":selected").val();

        Sijax.request("add_item_to_activity", [entity_to_add, amount, activity_id]);
    });

    return {
        after_refresh_list: function (entities) {
            $("#entities_list > ol").empty();
            $.each(entities, function(idx, entity_info) {
                var html = $(entity_info.html);
                if (entity_info.has_children) {
                    html.append(' <span class="expand">(+)</span>');
                }
                $("#entities_list > ol").append(html);
            });
        },
        after_entities_get_sublist: function(parent_id, entities) {
            var list = $("<ol></ol>");
            $.each(entities, function(idx, entity_info) {
                var html = $(entity_info.html);
                if (entity_info.has_children) {
                    html.append(' <span class="expand">(+)</span>');
                }
                list.append(html);
            });
            var parent = $("li[data-entity='" + parent_id + "']");
            parent.find(".expand").replaceWith(' <span class="subtree-collapse">(-)</span>');
            parent.append(list);
        },
        after_collapse_entity: function(entity_id) {
            var parent = $("li[data-entity='" + entity_id + "']");
            parent.find("ol").remove();
            parent.find(".subtree-collapse").replaceWith(' <span class="expand">(+)</span>');
        },
        before_eat: function (entity_id, max_amount) {
            var amount = +prompt("amount to eat", max_amount);
            if (amount) {
                Sijax.request("eat", [entity_id, amount]);
            }
        },
        after_eat: function (entity_id, amount) {
            $.publish("show_success", "eaten " + amount + " of " + entity_id);
        },
        after_move_to_location: function(loc_id) {
            $.publish("location_changed");
            $.publish("entities:refresh_list");
        },
        after_open_readable_contents: function(modal_dialog) {
            $("#readable_modal, #edit_readable_modal").remove();
            $(document.body).append(modal_dialog);
            $("#readable_modal").modal();
        },
        after_edit_readable: function(entity_d) {
            alert("text updated!");
        },
        after_form_add_item_to_activity: function(modal_dialog) {
            $("#add_to_activity").remove();
            $(document.body).append(modal_dialog);
            $("#add_to_activity").modal();
        },
        after_add_item_to_activity: function() {
            $("#add_to_activity").modal("hide");
            $.publish("entities:refresh_list");
        }
    }
})(jQuery);

$(function () {
    $.publish("entities:refresh_list");
});
