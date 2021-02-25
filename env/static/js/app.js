URL = window.URL || window.webkitURL;

var gumStream;                     
var rec;                          
var input;              

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext;

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");

recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);



function startRecording() {
    console.log("recordButton clicked");
    
    var constraints = { audio: true, video:false }

    recordButton.disabled = true;
    stopButton.disabled = false;
    pauseButton.disabled = false;

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        audioContext = new AudioContext();
        document.getElementById("status").innerHTML = "recording ...";
        // document.getElementById("formats").innerHTML="Format: 1 channel pcm @ "+audioContext.sampleRate/1000+"kHz"

        gumStream = stream;

        input = audioContext.createMediaStreamSource(stream);
        rec = new Recorder(input,{numChannels:1})

        rec.record()

    }).catch(function(err) {
        //enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
        pauseButton.disabled = true
    });

}

function pauseRecording(){
    console.log("pauseButton clicked rec.recording=",rec.recording );
    if (rec.recording){
        //pause
        rec.stop();
        document.getElementById("status").innerHTML = "Paused";
        pauseButton.innerHTML="Resume";
    }else{
        //resume
        rec.record()
        pauseButton.innerHTML="Pause";
        document.getElementById("status").innerHTML = "recording ...";

    }
}

function stopRecording() {
    console.log("stopButton clicked");


    stopButton.disabled = true;
    recordButton.disabled = false;
    pauseButton.disabled = true;

    pauseButton.innerHTML="Pause";
    rec.stop();
    gumStream.getAudioTracks()[0].stop();
    rec.exportWAV(post_to_server);
    document.getElementById("status").innerHTML = "click start recording";
}




function post_to_server(blob){
    var url = URL.createObjectURL(blob);
    var filename = new Date().toISOString();
    filename = filename + ".wav"

    var xhr=new XMLHttpRequest();
    xhr.onload=function(e) {
        if(this.readyState === 4) {
            console.log("Server returned: ",e.target.responseText);
        }
    };
    var fd=new FormData();
    fd.append("audio_data",blob, filename);
    xhr.open("POST","/",true);
    xhr.send(fd);
}