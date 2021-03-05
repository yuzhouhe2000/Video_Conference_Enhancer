URL = window.URL || window.webkitURL;

var gumStream;                     
var rec;                          
var input;              

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext;

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");
var playButton = document.getElementById("playButton");
var liveButton = document.getElementById("liveButton");
var stopLive = document.getElementById("stopLive");
var cameraButton = document.getElementById("cameraButton");



playButton.addEventListener("click", playRecording);  
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

liveButton.addEventListener("click", startlive);
stopLive.addEventListener("click", stoplive);
cameraButton.addEventListener("click", cameraon);

function startRecording() {
    
    var constraints = { audio: true, video:false }
    recordButton.disabled = true;
    stopButton.disabled = false;
    pauseButton.disabled = false;
    playButton.disabled = true;

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        audioContext = new AudioContext();
        document.getElementById("status").innerHTML = "recording ...";
        // document.getElementById("formats").innerHTML="Format: 1 channel pcm @ "+audioContext.sampleRate/1000+"kHz"

        gumStream = stream;

        input = audioContext.createMediaStreamSource(stream);
        rec = new Recorder(input,{numChannels:1})

        rec.record()

    }).catch(function(err) {
        recordButton.disabled = false;
        stopButton.disabled = true;
        pauseButton.disabled = true
    });

}

function pauseRecording(){
    if (rec.recording){
        rec.stop();
        document.getElementById("status").innerHTML = "Paused";
        pauseButton.innerHTML="Resume";
    }else{
        rec.record()
        pauseButton.innerHTML="Pause";
        document.getElementById("status").innerHTML = "recording ...";

    }
}

function stopRecording() {

    stopButton.disabled = true;
    recordButton.disabled = false;
    pauseButton.disabled = true;
    playButton.disabled = false;
    pauseButton.innerHTML="Pause";
    rec.stop();
    gumStream.getAudioTracks()[0].stop();
    rec.exportWAV(post_to_server);
    document.getElementById("status").innerHTML = "Welcome to EE434 Project Demo";
}


function startlive() {
    
    recordButton.disabled = true;
    stopButton.disabled = true;
    pauseButton.disabled = true;
    stopLive.disabled = false;
    liveButton.disabled = true;
    playButton.disabled = true;

    var xhr=new XMLHttpRequest();
    xhr.onload=function(e) {
        if(this.readyState === 4) {
            console.log("Server returned: ",e.target.responseText);
        }
    };
    xhr.open("POST","/live",true);
    xhr.send("fight on!");
    xhr.open("POST","/VAD",true);
    xhr.send("fight on!");
    document.getElementById("status").innerHTML = "denoiser on";
}

function stoplive() {
    stopButton.disabled = true;
    recordButton.disabled = false;
    pauseButton.disabled = true;
    stopLive.disabled = true;
    liveButton.disabled = false;
    playButton.disabled = false;

    var xhr=new XMLHttpRequest();
    xhr.onload=function(e) {
        if(this.readyState === 4) {
            console.log("Server returned: ",e.target.responseText);
        }
    };
    xhr.open("POST","/endlive",true);
    xhr.send("fight off!");
    document.getElementById("status").innerHTML = "denoiser off";
}

function cameraon() {
    if (document.getElementById("cameraButton").innerHTML == "Camera On"){
        document.getElementById("cameraButton").innerHTML = "Camera Off"
    }
    else{
        document.getElementById("cameraButton").innerHTML = "Camera On"
    }
    var xhr=new XMLHttpRequest();
        xhr.onload=function(e) {
            if(this.readyState === 4) {
                console.log("Server returned: ",e.target.responseText);
            }
        };
    xhr.open("POST","/camera_control",true);
    xhr.send("switch!");
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



function playSound(path) {
    if (typeof window.Audio === 'function') {
      var audioElem = new Audio();
      audioElem.src = path;
      audioElem.play();
    }
}

function playRecording() {
    var count = document.getElementById('count').getAttribute('num')
    var audio_file = '/sound/enhanced' + count + ".wav";
    playSound(audio_file);
}






