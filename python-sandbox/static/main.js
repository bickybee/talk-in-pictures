"use strict";

var recognition;
var modal;
var span;

var iconModal;
var iconSpan;

var iconSlider;
var fontSlider;
var baseIconSize = 200; // in px

var currIdx = 0;

var currPhraseNum = 0;

/* Format and send JSON to the server */
function sendParse(sentence, phraseNum){
    $.ajax({
        url: '/phrases/' + phraseNum,
        dataType: 'json',
        type: 'put',
        contentType: 'application/json',
        data: JSON.stringify( {"input": sentence}),
        success: function(res) {
            handleParse(res, phraseNum);   // render the response
        }
    })
}

/* Format and render JSON received from the server */
function handleParse(raw, phraseNum) {
    // If this phrase already has a div, update that div:


    // If this is a new phrase, create a new div:
    

    $('#output').html('');  // empty the field

    var phrase = raw["phrase"];
    for (var i in phrase) {
        // Ignore the grim reaper:
        if (phrase[i]["word"].trim() != "") {
            var id = "" + currIdx + "-" + phrase[i]["word"];

            // Create new container:
            var new_item = '<div class="tkn-container" id="' + id + '">' +
                '<div class="tkn-img"><img src="' + phrase[i]["img"] + '"></img></div>' +
                '<div class="tkn-caption">' + phrase[i]["word"] + '</div>' +
                '</div>';

            currIdx++;  // generate unique id for this token (#-word, where # = currIdx)

            $('#output').append(new_item);
            $(('#' + id)).click(displayAlternatives);
            // scrollRight();
        }
    }
}

function displayAlternatives() {
    // Display the modal window:
    $("#iconModal").css("display", "block");

    // Popula
    $("#alternativeIcons").html(this.id);
}

function scrollRight() {
    var targetElement = $('.container');
    var speed = 1000;

    var scrollWidth = $(targetElement).get(0).scrollWidth;
    var clientWidth = $(targetElement).get(0).clientWidth;
    $(targetElement).animate({ scrollLeft: scrollWidth - clientWidth },
    {
        duration: speed
    });
};

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

    // Set up modal window variables:
    modal = document.getElementById('myModal');
    span = document.getElementById("modalClose");

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // Set up modal window variables:
    iconModal = document.getElementById('iconModal');
    iconSpan = document.getElementById("iconModalClose");

    // When the user clicks on <span> (x), close the modal
    iconSpan.onclick = function() {
        iconModal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        } else if (event.target == iconModal) {
            iconModal.style.display = "none";
        }
    }

    // Set up sliders:
    iconSlider = document.getElementById("iconRange");
    fontSlider = document.getElementById("fontRange");

    iconSlider.oninput = function() {
        var newVal = baseIconSize * this.value / 100;
        var images = $(".tkn-img");

        for (var i in images) {
            ($(images[i])).css("width", newVal);
            ($(images[i])).css("height", newVal);
        }
    }

    fontSlider.oninput = function() {
        var captions = $(".tkn-caption");

        for (var i in captions) {
            ($(captions[i])).css("fontSize", "" + this.value + "px");
        }
    }
})

$(document).on("keypress", function (e) {
    switch(e.keyCode) {
        // enter
        case 13:
            scrollRight();
            break;

        // space
        case 32:
            e.preventDefault();

            if (iconModal.style.display == "block") { 
                iconModal.style.display = "none";
            }

            if (modal.style.display == "block") {
                modal.style.display = "none";
            } else {
                modal.style.display = "block";
            }

            break;

        default:
            return;
    }
})