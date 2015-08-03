var activeTabCaptures = {};

chrome.browserAction.onClicked.addListener(function(tab) {
     if (activeTabCaptures.hasOwnProperty(tab.id)) {
        activeTabCaptures[tab.id].stream.stop();
        exportWAV(2, activeTabCaptures[tab.id].buffers, activeTabCaptures[tab.id].recordedLength,  activeTabCaptures[tab.id].sampleRate);
        delete activeTabCaptures[tab.id];
    } else {
         chrome.tabCapture.capture({
                 audio: true,
                 video: false
             },
             function(audioStream) {
                 activeTabCaptures[tab.id] = {stream: audioStream, buffers: [[],[]], recordedLength: 0,
                 sampleRate: 0};

                 // Continue playing the audio back on that tab.
                var audio = new Audio(window.URL.createObjectURL(audioStream));
                audio.play();

                // Record bits to a buffer.
                audioContext = window.AudioContext || window.webkitAudioContext;
                context = new audioContext();
                sampleRate = context.sampleRate;
                activeTabCaptures[tab.id].sampleRate = sampleRate;
                volume = context.createGain();
                audioInput = context.createMediaStreamSource(audioStream);
                audioInput.connect(volume);

                 /* From the spec: This value controls how frequently the audioprocess event is
                 dispatched and how many sample-frames need to be processed each call.
                 Lower values for buffer size will result in a lower(better) latency.
                 Higher values will be necessary to avoid audio breakup and glitches */
                var bufferSize = 4096;
                var recorder = context.createScriptProcessor(bufferSize, 2, 2);
                recorder.onaudioprocess = function(e) {
                    var left = e.inputBuffer.getChannelData(0);
                    var right = e.inputBuffer.getChannelData(1);
                    // we clone the samples
                    activeTabCaptures[tab.id].buffers[0].push(new Float32Array(left));
                    activeTabCaptures[tab.id].buffers[1].push(new Float32Array(right));
                    activeTabCaptures[tab.id].recordedLength += left.length;
                }

                volume.connect(recorder);
                recorder.connect(context.destination);
             }
         );
     }
});