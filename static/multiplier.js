var audio = new Audio('/assets/flip_sound.mp3');

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


function initiateMultiplier(){
    document.getElementById("betting").style.display = "none";
    document.getElementById("game-div").style.display = "block";
}


function refresh(){
    window.location.reload()
}


function playMultiplier(choosen_number, element){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/multiplier_post', true);

    element.style.boxShadow = "box-shadow: 0 1px 2px 0 rgba(90,164,97,.3),0 2px 6px 2px rgba(90,164,97,.15);"

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Inadequate Balance"){
                alert("Your balance is insufficient you will be redirected to the deposit page.")
                document.location = "/make-deposit"
            }
            var cards = document.getElementsByClassName("card-div")
            for(i = 0; i < cards.length; i++){
                if(parseFloat(this.responseText.split("&")[i])  === 3){
                    cards[i].style.backgroundColor = "#ff4e00"
                    cards[i].style.backgroundImage = "linear-gradient(315deg, #ff4e00 0%, #ec9f05 74%)"
                    cards[i].style.color = "white"
                }
                cards[i].innerHTML = "<center style='width: 100%; margin-top: 125px'>" + this.responseText.split("&")[i] + "x</center>"
                cards[i].style.border = "1px solid gray"
                cards[i].style.fontSize = "2rem"

                getBalance();

                setTimeout(refresh, 2000)
            }
        }
    }
    xhr.send("choosen_number=" + choosen_number + "&bet_amount=" + document.getElementById("bet_amount").value);
}
