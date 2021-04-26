URL = window.URL || window.webkitURL;

var gumStream;                     
var rec;                          
var input;              

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext;

var liveButton = document.getElementById("liveButton");
var stopLive = document.getElementById("stopLive");

liveButton.addEventListener("click", startlive);
stopLive.addEventListener("click", stoplive);

function startlive() {
    
    stopLive.disabled = false;
    liveButton.disabled = true;

    var xhr=new XMLHttpRequest();
    xhr.onload=function(e) {
        if(this.readyState === 4) {
            console.log("Server returned: ",e.target.responseText);
        }
    };
    xhr.open("POST","/output_audio",true);
    xhr.send("fight on!");
    xhr.open("POST","/volume",true);
    xhr.send("fight on!");
    
    var xhr=new XMLHttpRequest();
    xhr.onload=function(e) {
        if(this.readyState === 4) {
            console.log("Server returned: ",e.target.responseText);
        }
    };
    xhr.open("POST","/live",true);
    xhr.send("fight on!");
    document.getElementById("status").innerHTML = "denoiser on";
}

function stoplive() {
    stopLive.disabled = true;
    liveButton.disabled = false;
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



