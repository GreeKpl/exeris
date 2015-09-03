FRAGMENTS.entities = (function($) {

    $.subscribe("entities:refresh_list", function () {
        Sijax.request("entities_refresh_list", []);
    });
    
    return {
        after_refresh_list: function (entity_names) {
            $.each(entity_names, function(idx, item_info) {
                $("#entities_list > ol").append(item_info);
            });
        }
    }
})(jQuery);

$(function () {
    $.publish("entities:refresh_list");
});