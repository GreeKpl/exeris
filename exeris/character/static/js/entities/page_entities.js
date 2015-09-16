FRAGMENTS.entities = (function($) {

    $.subscribe("entities:refresh_list", function () {
        Sijax.request("entities_refresh_list", []);
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

    return {
        after_refresh_list: function (entity_names) {
            $("#entities_list > ol").empty();
            $.each(entity_names, function(idx, item_info) {
                if (Array.isArray(item_info)) {
                    var loc_name = item_info.shift();
                    var loc = $(loc_name).css("border", "#ccc solid 1px");
                    var inner_list = $("<ol></ol>");
                    $.each(item_info, function(idx, inner_info) {
                        inner_list.append(inner_info);
                    });
                    loc.append(inner_list);
                    $("#entities_list > ol").append(loc);
                } else {
                    $("#entities_list > ol").append(item_info);
                }
            });
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
        }
    }
})(jQuery);

$(function () {
    $.publish("entities:refresh_list");
});
