FRAGMENTS.events = (function($) {

    var _last_event = 0;

    $.subscribe("events:refresh_list", function() {
        Sijax.request("get_new_events", [_last_event]);
    });

    return {
        update_list: function(new_events, last_event) {
            for (var i = 0; i < new_events.length; i++) {
                new_events[i] = "<li>" + new_events[i].replace(/(\*+[^*]+\*+)/g, "<b>$1</b>") + "</li>";
            }
            $(".events_list_contents > ol").prepend(new_events.reverse());
            _last_event = last_event;
        }
    };
})(jQuery);


FRAGMENTS.people_short = (function($) {

    var SELECTED_SPEAKER = "#say_to_all";

    var change_listener = function (new_speaker_selector) {
        console.log("ROBIE TO DLA " + new_speaker_selector);
        $(SELECTED_SPEAKER).removeClass("btn-primary").addClass("btn-default");
        SELECTED_SPEAKER = new_speaker_selector;
        $(SELECTED_SPEAKER).removeClass("btn-default").addClass("btn-primary");
    };

    $.subscribe("people_short:refresh_list", function() {
        Sijax.request("people_short_refresh_list", []);
    });

    $(document).on("click", ".select-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "SAY_TO_SOMEBODY", character_id);
        change_listener(".id_" + character_id + " ~ .select-listener");
    });

    $(document).on("click", ".select-whisper-listener", function(event) {
        var character_id = $(event.target).closest("li").data("id");
        $.publish("speaking:change_listener", "WHISPER", character_id);
        change_listener(".id_" + character_id + " ~ .select-whisper-listener");
    });

    $(document).on("click", "#say_to_all", function(event) {
        $.publish("speaking:change_listener", "PUBLIC");
        change_listener("#say_to_all");
    });


    $(function() {
        $.publish("people_short:refresh_list");
    });

    return {
        after_refresh_list: function(code) {
            $("#people_short_dock").html(code);
            change_listener(SELECTED_SPEAKER);
        }
    };
})(jQuery);


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

    var event_refresher = function() {
        $.publish("events:refresh_list");
        setTimeout(event_refresher, 20000);
    };
    event_refresher();
});
