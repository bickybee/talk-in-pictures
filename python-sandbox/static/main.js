"use strict";

$(document).ready(function() {
    /*  Monitor changes to the input field.
    This is a temporary function to make sure the POST call work. */
    $('#input').bind('input propertychange', function() {
        $.ajax({
            url: '/parse',
            dataType: 'json',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify( {"input": $(this).val()}),
            success: function(res) {
                handleParse(res);   // render the response
            }
        })
    })
})

/* 
    BEGIN SOCKETIO AUDIO RECORDING CODE 
    ----
    Based off code from Miguel Grinberg's SocketIO-Examples:
      https://github.com/miguelgrinberg/socketio-examples/tree/master/audio
*/

// Set up:
window.AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext();
var recording = false;
var socketio = io.connect('http://' + document.domain + ':' + location.port);

// Called by sandbox.py's end_recording():
socketio.on('add-transcription', function(url) {
    console.log("hello");
});

// Enable microphone input:
function initAudio() {
    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then(handleSuccess);
}

var handleSuccess = function(stream) {
    var context = new AudioContext();
    var source = context.createMediaStreamSource(stream);
    var processor = context.createScriptProcessor(1024, 1, 1);

    source.connect(processor);
    processor.connect(context.destination);

    processor.onaudioprocess = function(e) {
        if (recording) {
            var input = e.inputBuffer.getChannelData(0);

            // convert float audio data to 16-bit PCM
            var buffer = new ArrayBuffer(input.length * 2)
            var output = new DataView(buffer);
            for (var i = 0, offset = 0; i < input.length; i++, offset += 2) {
                var s = Math.max(-1, Math.min(1, input[i]));
                output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
            }
            socketio.emit('write-audio', buffer);
        }
    };
};

// Toggle WAV file generation:
function toggleRecording(e) {
    if (e.classList.contains('recording')) {
        // Stop recording:
        e.classList.remove('recording');
        recording = false;
        socketio.emit('end-recording');
    } else {
        // Start recording:
        e.classList.add('recording');
        recording = true;
        socketio.emit('start-recording', {numChannels: 1, bps: 16, fps: parseInt(audioContext.sampleRate)});
    }
}

// Start up microphone input upon load:
window.addEventListener('load', initAudio );

/* END SOCKETIO AUDIO RECORDING CODE */


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

function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition')) {
        var recognition = new webkitSpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.lang = "en-US";
        recognition.start();

        recognition.onresult = function(e) {
            console.log(e.results);
            console.log(e.results[0][0].transcript);

            // Fake continuous recognition:
            recognition.start();
            // recognition.stop();
        };

        recognition.onerror = function(e) {
            recognition.stop();
            console.log(e.error);
        };
    }
}