FRAGMENTS.player = (function() {

    $(document).on("click", "#create_character").click(function() {
        var char_name = $("#char_name").val();
        Sijax.request("create_character", [char_name]);
    });

    return {
        after_create_character: function() {

        }
    };
})();
