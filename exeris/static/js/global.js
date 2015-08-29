FRAGMENTS.global = (function($) {
    return {
        get_id: function(element) {
            var classes = element.attr("class").split(/\s+/);
            for (var i = 0; i < classes.length; i++) {
                var class_name = /^id_(.*)$/.exec(classes[i]);
                if (class_name) {
                    return +class_name[1];
                }
            }
            return null;
        },
        alter_entity: function(entity_id, new_data) {
            $(".id_" + entity_id).replaceWith(new_data);
        }
    };
})(jQuery);

$(EVENTS).on("refresh_entity", function(event, entity_id) {
    Sijax.request("get_entity_tag", [entity_id]);
});
