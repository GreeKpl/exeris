FRAGMENTS.entities = (function($) {

    $.subscribe("entities:refresh_list", function () {
        Sijax.request("entities_refresh_list", []);
    });
    
    return {
        after_refresh_list: function (entity_names) {
            $.each(entity_names, function(idx, entity_name) {
                $("#entities_list > ol").append("<li>" + entity_name + "</li>");
            });
        }
    }
})(jQuery);

$(function () {
    $.publish("entities:refresh_list");
});