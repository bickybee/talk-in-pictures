"use strict";

/* Format and send JSON to the server */
function sendParse(sentence){
    $.ajax({
        url: '/parse',
        dataType: 'json',
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify( {"input": sentence}),
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
        // Create new container:
        var new_item = '<div class="tkn-container">' +
            '<div class="tkn-img"><img src="' + tokens[i]["img"] + '"></img></div>' +
            '<div class="tkn-caption">' + tokens[i]["word"] + '</div>' +
            '</div>';

        $('#output').append(new_item);
    }
}

/* Handles WebkitSpeechRecognition event  */
function handleRecognitionResult(event) {
    var transcript = "";
    for (var i = event.resultIndex; i < event.results.length; ++i) { // why can't it be a normal loop :/
        if (event.results[i].isFinal) {
            // Can do something different here...
        } 
        transcript += event.results[i][0].transcript;
    }
    // console.log(transcript)
    sendParse(transcript)
}

/* Handles WebkitSpeechRecognition error */
function handleRecognitionError(event) {
    this.stop();
    console.log(e.error);
}

// API:
// https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition/interimResults
function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition')) {
        console.log("start speech rec");
        var recognition = new webkitSpeechRecognition();

        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.lang = "en-US";
        recognition.start();

        // This thing doesn't stop at the moment:
        recognition.onresult = handleRecognitionResult;
        recognition.onerror = handleRecognitionError;
            
        };
    } else {
        console.log("no speech recognition!");
    }
}

$(document).ready(function() {
    /*  Monitor changes to the input field.
    This is a temporary function to make sure the POST call work. */
    $('#input').bind('input propertychange', function() {
        sendParse($(this).val());
    })
})

