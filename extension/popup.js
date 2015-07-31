document.addEventListener('DOMContentLoaded', function() {
    var ws_url = 'ws://127.0.0.1:9999';
    var ws;
    var mediaRecorder;
    var translateButton = document.getElementById('translate-button');
    translateButton.addEventListener('click', function() {
        chrome.tabs.getSelected(null, function(tab) {
            chrome.tabCapture.capture({audio: true, video: false}, function(stream) {
                mediaRecorder = new MediaStreamRecorder(stream);
                mediaRecorder.mimeType = 'audio/wav';
                mediaRecorder.audioChannels = 2;
                var audio = new Audio(window.URL.createObjectURL(stream));
                audio.play();
                ws = new WebSocket(ws_url);
                ws.onopen = function() {
                    ws.send('START');
                    mediaRecorder.start(150);
                }
                ws.onmessage = function(event) {
                    console.log(event);
                }
                mediaRecorder.ondataavailable = function (blob) {
                    console.log(blob);
                    ws.send(blob);
                };
            });
        });
    });
    var stopButton = document.getElementById('stop-button');
    stopButton.addEventListener('click', function() {
        mediaRecorder.stop();
        ws.send('STOP');
        ws.close();
    });
});