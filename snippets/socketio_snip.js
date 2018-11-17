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