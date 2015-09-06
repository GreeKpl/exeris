FRAGMENTS.actions = (function() {

    $.subscribe("actions:update_actions_list", function() {
        Sijax.request("update_actions_list", []);
    });

    $(document).on("click", ".recipe", function(event) {
        var recipe = $(event.target);
        var recipe_id = recipe.data("recipe");
        Sijax.request("create_activity_from_recipe", [recipe_id]);
    });

    return {
        after_update_actions_list: function(actions) {
            $.each(actions, function(idx, action) {
                $("#actions_list > ol").append("<li class='recipe' data-recipe='" + action.id + "'>" +  action.name +  "</li>");
            });
        },
        after_create_activity_from_recipe: function() {
            alert("activity started!");
        }
    }
})();

$(function() {
    $.publish("actions:update_actions_list");
});