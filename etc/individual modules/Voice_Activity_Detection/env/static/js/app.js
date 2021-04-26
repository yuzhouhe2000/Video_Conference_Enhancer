URL = window.URL || window.webkitURL;

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");


recordButton.addEventListener("click", startlive);
stopButton.addEventListener("click", stoplive);


function waiting(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

function startlive() {
    
    recordButton.disabled = true;
    stopButton.disabled = false;

    var xhr=new XMLHttpRequest();
    xhr.onload=function(e) {
        if(this.readyState === 4) {
            console.log("Server returned: ",e.target.responseText);
        }
    };
    xhr.open("POST","/live",true);
    xhr.send("fight on!");
}

function stoplive() {
    stopButton.disabled = true;
    recordButton.disabled = false;

    var xhr=new XMLHttpRequest();
    xhr.onload=function(e) {
        if(this.readyState === 4) {
            console.log("Server returned: ",e.target.responseText);
        }
    };
    xhr.open("POST","/endlive",true);
    xhr.send("fight off!");
}

