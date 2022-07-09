var audio = new Audio('/assets/up_or_down_sound.mp3');

function chooseUpOrDown(direction) {
    audio.play();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/play_up_or_down/' + window.gameID, true);

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            updateNumberAndOffer();
            if(this.responseText == "False"){
                window.location = "/lose_up_or_down"
            }
        }
    }
    xhr.send("&choosen_direction=" + direction);
}


function finishUpOrDown() {
    document.location = "/win_up_or_down/" + window.gameID
}

function initiateUpOrDown() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/start_up_or_down', true);

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Inadequate Balance"){
                alert("Your balance is insufficient you will be redirected to the deposit page.")
                document.location = "/make-deposit"
            }
            document.getElementById("betting_amount").style.display = "none"
            document.getElementById("betting").style.display = "none"
            window.gameID = this.responseText
            document.getElementById("game").style.display = "block";
            updateNumberAndOffer();
        }
    }
    xhr.send("&bet_amount=" + document.getElementById("betting_amount").value);
}

function getBalance(){
    function reqListenerMoney () {
      document.getElementById("account_balance").innerHTML = this.responseText
    }

    var oReqMoney = new XMLHttpRequest();
    oReqMoney.addEventListener("load", reqListenerMoney);
    oReqMoney.open("GET", "/current_account_balance");
    oReqMoney.send();
}

function updateNumberAndOffer(){
    getBalance();

    function reqListener () {

        document.getElementById("number").innerHTML = JSON.parse(this.responseText)["current_number"]
        document.getElementById("offer").innerHTML = JSON.parse(this.responseText)["current_offer"]
    }

    var oReq = new XMLHttpRequest();
    oReq.addEventListener("load", reqListener);
    oReq.open("GET", "/get_number_up_or_down/" + window.gameID);
    oReq.send();
}

getBalance();
