function getBalance(){
    function reqListenerMoney () {
      document.getElementById("account_balance").innerHTML = this.responseText
    }

    var oReqMoney = new XMLHttpRequest();
    oReqMoney.addEventListener("load", reqListenerMoney);
    oReqMoney.open("GET", "/current_account_balance");
    oReqMoney.send();
}

getBalance();

function playSlot(){
    var bgPosVertical1 = 0;
    var bgPosVertical2 = 0;
    var bgPosVertical3 = 0;

    const fullRotation = 2484;
    var directives = {
        1: 75, // banana
        2: 275, // melon
        3: 420, // gold
        4: 570 // diamond

    }

    var r1 = 1;
    var r2 = 1;
    var r3 = 1;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/play_slots', true);

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Inadequate Balance"){
                alert("Your balance is insufficient you will be redirected to the deposit page.")
                document.location = "/make-deposit"
            }
            r1 = this.responseText.split("&")[0]
            r2 = this.responseText.split("&")[1]
            r3 = this.responseText.split("&")[2]
        }
    }
    xhr.send("bet_amount=" + document.getElementById("bet_amount").value);

    function rotateSlot1(){
        document.getElementById("slot1").style.backgroundPositionY = bgPosVertical1 + "px";
        bgPosVertical1 += 25
        if(bgPosVertical1 > directives[r1] + fullRotation){

            clearInterval(slot1_interval)
        }
    }

    function rotateSlot2(){
        document.getElementById("slot2").style.backgroundPositionY = bgPosVertical2 + "px";
        bgPosVertical2 += 25
        if(bgPosVertical2 > directives[r2] + fullRotation){
            clearInterval(slot2_interval)
            getBalance();
        }
    }

    function randomIntFromInterval(min, max) {
      return Math.floor(Math.random() * (max - min + 1) + min)
    }

    function rotateSlot3(){
        document.getElementById("slot3").style.backgroundPositionY = bgPosVertical3 + "px";
        bgPosVertical3 += 25
        if(bgPosVertical3 > directives[r3] + fullRotation){
            clearInterval(slot3_interval)
        }
    }
    var slot1_interval = setInterval(rotateSlot1, 10);
    var slot2_interval = setInterval(rotateSlot2, 10);
    var slot3_interval = setInterval(rotateSlot3, 10);
}