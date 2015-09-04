FRAGMENTS.entities = (function($) {

    $.subscribe("entities:refresh_list", function () {
        Sijax.request("entities_refresh_list", []);
    });
    
    return {
        after_refresh_list: function (entity_names) {
            $.each(entity_names, function(idx, item_info) {
                $("#entities_list > ol").append(item_info);
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
        }
    }
})(jQuery);

$(function () {
    $.publish("entities:refresh_list");
});

$(document).on("click", ".entity-action", function (event) {
    var target = $(event.target);
    console.log(target);
    var endpoint = target.data("action");
    var entity_id = target.data("entity");
    Sijax.request(endpoint, [entity_id]);
});