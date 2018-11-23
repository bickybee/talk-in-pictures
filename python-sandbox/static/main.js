"use strict";

var recognition;

/* Format and send JSON to the server */
function sendParse(sentence, phraseNum){
    $.ajax({
        url: '/parse',
        dataType: 'json',
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify( {"input": sentence, "phrase_num": phraseNum}),
        success: function(res) {
            handleParse(res);   // render the response
        }
    })
}

/* Format and render JSON received from the server */
function handleParse(raw) {
    $('#output').html('');  // empty the field

    var tokens = raw["tokens"];
    for (var i in tokens) {
        // Ignore the grim reaper:
        if (tokens[i]["word"].trim() != "") {
            // Create new container:
            var new_item = '<div class="tkn-container">' +
                '<div class="tkn-img"><img src="' + tokens[i]["img"] + '"></img></div>' +
                '<div class="tkn-caption">' + tokens[i]["word"] + '</div>' +
                '</div>';

            $('#output').append(new_item);
        }
    }
}

/* Handles WebkitSpeechRecognition event  */
function handleRecognitionResult(event) {
    var transcript = "";
    console.log(event)
    for (var i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript;
    }
    console.log(transcript)
    sendParse(transcript, event.resultIndex)
}

/* Handles WebkitSpeechRecognition error */
function handleRecognitionError(event) {
    this.stop();
    console.log(event.error);

    if ($("#mic").hasClass("recording-active")) {
        toggleRecording();
    }
}

function toggleRecording() {
    $("#mic").toggleClass("recording-inactive");
    $("#mic").toggleClass("recording-active");
}

// API:
// https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition/interimResults
function startDictation() {
    toggleRecording();

    if ($("#mic").hasClass("recording-active")) {
        console.log("start speech rec");

        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.lang = "en-US";
        recognition.start();

        // This thing doesn't stop at the moment:
        recognition.onresult = handleRecognitionResult;
        recognition.onerror = handleRecognitionError;
    } else {
        recognition.stop();
    }
}

$(document).ready(function() {
    if (window.hasOwnProperty('webkitSpeechRecognition')) {
        recognition = new webkitSpeechRecognition();
    } else {
        console.log("no speech recognition!");
    }

    /*  Monitor changes to the input field.
    This is a temporary function to make sure the POST call work. */
    $('#input').bind('input propertychange', function() {
        sendParse($(this).val());
    })
})

