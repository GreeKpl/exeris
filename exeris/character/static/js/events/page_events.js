FRAGMENTS.events = (function($, socket) {

    var convertEventToText = function(event_text, event_id) {
        return "<li data-event-id='" + event_id + "'>" +
            event_text.replace(/(\*+[^*]+\*+)/g, "<b>$1</b>") + "</li>";
    };

    $.subscribe("events/refresh_list", function() {
        socket.emit("character.pull_events_initial", function(new_events) {
            for (var i = 0; i < new_events.length; i++) {
                new_events[i] = convertEventToText(new_events[i].text, new_events[i].id);
            }
            $(".events_list_contents > ol").prepend(new_events.reverse());
        });
    });

    socket.on("character.new_event", function(event_id, event_text) {
        $(".events_list_contents > ol").prepend(convertEventToText(event_text, event_id));
    });

})(jQuery, socket);


FRAGMENTS.people_short = (function($, socket) {

    var SELECTED_SPEAKER = "#say_to_all";

    var change_listener = function(new_speaker_selector) {
        $(SELECTED_SPEAKER).removeClass("btn-primary").addClass("btn-default");
        SELECTED_SPEAKER = new_speaker_selector;
        $(SELECTED_SPEAKER).removeClass("btn-default").addClass("btn-primary");
    };

    $.subscribe("people_short:refresh_list", function() {
        socket.emit("people_short_refresh_list", function(code) {
            $("#people_short_dock").html(code);
            change_listener(SELECTED_SPEAKER);
        });
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

})(jQuery, socket);


FRAGMENTS.speaking = (function($, socket) {

    var message = "";
    var speak_type = "PUBLIC";
    var target = null;

    $(document).on("click", "#speaking_button", function(event) {
        event.preventDefault();
        var message = $("#message");
        var message_text = message.val().trim();
        if (message_text) {
            if (speak_type == "PUBLIC") {
                socket.emit("say_aloud", message_text, function() {
                });
            } else if (speak_type == "SAY_TO_SOMEBODY") {
                socket.emit("say_to_somebody", target, message_tex, function() {
                });
            } else if (speak_type == "WHISPER") {
                socket.emit("whisper", target, message_text, function() {
                });
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
        socket.emit("speaking_form_refresh", speak_type, target, function(code) {
            var message = $("#message").val();
            $("#speaking_form_dock").html(code);

            $("#message").val(message).focus();
        });
    });

})(jQuery, socket);

$(function() {
    $.publish("speaking:form_refresh");

    $.publish("events/refresh_list");
});
