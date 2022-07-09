var audio = new Audio('/assets/flip_sound.mp3');

function initiateHitOrPass() {
    audio.play()
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/start_hit_or_pass', true);

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Inadequate Balance"){
                alert("Your balance is insufficient you will be redirected to the deposit page.")
                document.location = "/make-deposit"
            }
            document.getElementById("betting").style.display = "none"
            window.gameID = this.responseText
            document.getElementById("game-div").style.display = "block";
            startHitOrPass();
        }
    }
    xhr.send("&bet_amount=" + document.getElementById("bet_amount").value);
}

function startHitOrPass(){
    getBalance();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/init_hit_or_pass', true);

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            cards = document.getElementsByClassName("card")
            for(i = 0; i < this.responseText.split("&").length; i++){
                cards[i].innerHTML = "<center style='width: 100%; margin-top: 125px'>" + this.responseText.split("&")[i] + "x</center>"
                cards[i].style.border = "1px solid gray"
                cards[i].style.fontSize = "2rem"
                if(parseFloat(this.responseText.split("&")[i]) >= 2){
                    cards[i].style.backgroundColor = "#ff4e00"
                    cards[i].style.backgroundImage = "linear-gradient(315deg, #ff4e00 0%, #ec9f05 74%)"
                    cards[i].style.color = "white"
                }
                else if(parseFloat(this.responseText.split("&")[i]) >= 1){
                    cards[i].style.backgroundColor = "#20bf55"
                    cards[i].style.backgroundImage = "linear-gradient(315deg, #20bf55 0%, #01baef 74%);"
                    cards[i].style.color = "white"
                }
            }
        }
    }
    xhr.send("&game_id=" + window.gameID);
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


function hitHitOrPass(){
    audio.play();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/hit_hit_or_pass', true);

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "End Game"){
                window.location = "/finish_hit_or_pass/" + window.gameID
            }
            cards = document.getElementsByClassName("card")
            for(i = 0; i < this.responseText.split("&").length; i++){
                cards[i].innerHTML = "<center style='width: 100%; margin-top: 125px'>" + this.responseText.split("&")[i] + "x</center>"
                cards[i].style.border = "1px solid gray"
                cards[i].style.fontSize = "2rem"
                if(parseFloat(this.responseText.split("&")[i]) >= 2){
                    cards[i].style.backgroundColor = "#ff4e00"
                    cards[i].style.backgroundImage = "linear-gradient(315deg, #ff4e00 0%, #ec9f05 74%)"
                    cards[i].style.color = "white"
                }
                else if(parseFloat(this.responseText.split("&")[i]) >= 1){
                    cards[i].style.backgroundColor = "#20bf55"
                    cards[i].style.backgroundImage = "linear-gradient(315deg, #20bf55 0%, #01baef 74%);"
                    cards[i].style.color = "white"
                }
            }
        }
    }
    xhr.send("&game_id=" + window.gameID);
}

function finishHitOrPass(){
    window.location = "/finish_hit_or_pass/" + window.gameID
}

getBalance();
