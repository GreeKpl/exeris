FRAGMENTS.events = (function($) {

    var _last_event = 0; // to jest prywatne

    var speak_type = "public";
    var target = null;

    $.subscribe("events:refresh_list", function() {
        Sijax.request("get_new_events", [_last_event]);
    });

    $(document).on("click", "#speaking_button", function(event) {
        event.preventDefault();
        var message = $("#message");
        var message_text = message.val().trim();
        if (message_text) {
            if (speak_type == "public") {
                Sijax.request("say_aloud", [message_text]);
            } else if (speak_type == "speak_to") {
                Sijax.request("speak_to_somebody", [target, message_text]);
            } else {
                Sijax.request("whisper", [target, message_text]);
            }
            message.val("");
        }
    });

    $.subscribe("speaking:change_listener", function(type, id) {
        console.log("changing receiver", arguments);
        if (type == "public") {
            $("#speaking_button").text("say to everyone");
        } else if (type == "whisper") {
            $("#speaking_button").text("whisper to somebody");
        } else {
            $("#speaking_button").text("speak to somebody");
        }
        speak_type = type;
        target = id;
    });

    return {
        update_list: function(new_events, last_event) {
            for (var i = 0; i < new_events.length; i++) {
                new_events[i] = "<li>" + new_events[i].replace(/(\*+[^*]+\*+)/g, "<b>$1</b>") + "</li>";
            }
            $(".events_list_contents > ol").prepend(new_events.reverse());
            _last_event = last_event;
        },
        after_say_aloud: function() {
            this.update_list();
        },
        after_say_to_somebody: function() {
            this.update_list();
        },
        after_whisper: function() {
            this.update_list();
        }
    };
})(jQuery);

$(function() {

    var event_refresher = function() {
        $.publish("events:refresh_list");

        setTimeout(event_refresher, 5000);
    };

    event_refresher();
});