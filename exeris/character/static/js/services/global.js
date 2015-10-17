FRAGMENTS.entity = (function($) {

    $(document).on("click", ".character", function(event) {
        var character = $(event.target);
        var new_name = prompt("select new name");
        Sijax.request("rename_entity", [FRAGMENTS.entity.get_id(character), new_name]);
    });

    $(document).on("click", ".root_location", function(event) {
        var loc = $(event.target);
        var new_name = prompt("select new name");
        Sijax.request("rename_entity", [FRAGMENTS.entity.get_id(loc), new_name]);
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
})(jQuery);


FRAGMENTS.character = (function($) {

    $.subscribe("refresh_entity", function(entity_id) {
        Sijax.request("get_entity_tag", [entity_id]);
    });

    return {
        show_error: function(message) {
            $.notify({
                message: message
            }, {
                type: "danger"
            });
        },
        after_rename_entity: function(entity_id) {
            $.publish("refresh_entity", entity_id);
        },
        after_get_entity_tag: function(entity_id, new_data) {
            $(".id_" + entity_id).replaceWith(new_data);
        }
    };
})(jQuery);
