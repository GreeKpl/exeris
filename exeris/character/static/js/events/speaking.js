FRAGMENTS.speaking = (function($) {

    var message = "";
    var speak_type = "PUBLIC";
    var target = null;

    $(document).on("click", "#speaking_button", function(event) {
        event.preventDefault();
        var message = $("#message");
        var message_text = message.val().trim();
        if (message_text) {
            if (speak_type == "PUBLIC") {
                Sijax.request("say_aloud", [message_text]);
            } else if (speak_type == "SAY_TO_SOMEBODY") {
                Sijax.request("say_to_somebody", [target, message_text]);
            } else if (speak_type == "WHISPER") {
                Sijax.request("whisper", [target, message_text]);
            }
            message.val("");
        }
    });

    $.subscribe("speaking:change_listener", function(type, id) {
        speak_type = type;
        target = id;

        $.publish("speaking:form_refresh");
    });

    $.subscribe("speaking:form_refresh", function() {
        Sijax.request("speaking_form_refresh", [speak_type, target]);
    });

    return {
        after_speaking_form_refresh: function (code) {
            var message = $("#message").val();
            $("#speaking_form_dock").html(code);

            $("#message").val(message).focus();
        },
        after_say_aloud: function() {
            $.publish("events:refresh_list");
        },
        after_say_to_somebody: function() {
            $.publish("events:refresh_list");
        },
        after_whisper: function() {
            $.publish("events:refresh_list");
        }
    };
})(jQuery);

$(function() {
    $.publish("speaking:form_refresh");
});
