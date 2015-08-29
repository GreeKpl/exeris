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
        }
    };
})(jQuery);