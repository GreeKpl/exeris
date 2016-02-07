FRAGMENTS.entity = (function($, socket) {

    $(document).on("click", ".dynamic_nameable", function(event) {
        var loc = $(event.target);
        var new_name = prompt("select new name");
        if (new_name) {
            socket.emit("rename_entity", [FRAGMENTS.entity.get_id(loc), new_name], function(entity_id) {
                $.publish("refresh_entity", entity_id);
            });
        }
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

    $.subscribe("refresh_entity", function(entity_id) {
        socket.emit("get_entity_tag", [entity_id], function(entity_id, new_data) {
            $(".id_" + entity_id).replaceWith(new_data);
        });
    });

})(jQuery, socket);
