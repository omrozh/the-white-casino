function reqListener () {
  document.getElementById("account_balance").innerHTML = this.responseText
}

var oReq = new XMLHttpRequest();
oReq.addEventListener("load", reqListener);
oReq.open("GET", "/current_account_balance");
oReq.send();

function executeRoulette(){
    var current_rotation = 0;
    document.getElementsByClassName("roulette-wheel")[0].style.transform = 'rotate(' + 0 + 'deg)'

    var number_of_rotations = 0

    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/play-roulette', true);

    var roulette_number = document.getElementById("choice").value

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Inadequate Balance"){
                alert("Your balance is insufficient you will be redirected to the deposit page.")
                document.location = "/make-deposit"
            }
            roulette_number = this.responseText;
        }
    }

    var map_dict = {
        26: 1,
        3: 3,
        35: 5,
        12: 7,
        28: 9,
        7: 11,
        29: 13,
        18: 15,
        22: 17,
        9: 19,
        31: 21,
        14: 23,
        20: 25,
        1: 27,
        33: 29,
        16: 31,
        24: 33,
        5: 35,
        10: 36,
        23: 37,
        8: 40,
        30: 42,
        11: 44,
        36: 46,
        13: 48,
        27: 50,
        6: 52,
        34: 54,
        17: 56,
        25: 58,
        2: 60,
        21: 62,
        4: 64,
        19: 66,
        15: 68,
        32: 70,
        0: 72
    }

    xhr.send("bet=" + document.getElementById("choice").value +
        "&bet_type=" + document.getElementById("bet_type").value +
        "&betting_amount=" + document.getElementById("betting_amount").value);

    const black = [15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20, 31, 22, 29, 28, 35, 3, 26]
    const red = [32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14, 9, 18, 7, 12, 3]
    const green = [0]

    function rotate_wheel(){
        current_rotation += 5
        document.getElementsByClassName("roulette-wheel")[0].style.transform = 'rotate(' + current_rotation + 'deg)'
        number_of_rotations += 1
        if(number_of_rotations > 144){
            if(number_of_rotations - 144 === map_dict[roulette_number]){
                function reqListener () {
                  document.getElementById("account_balance").innerHTML = this.responseText
                }

                var oReq = new XMLHttpRequest();
                oReq.addEventListener("load", reqListener);
                oReq.open("GET", "/current_account_balance");
                oReq.send();

                var result = document.getElementById("result");
                result.innerHTML = roulette_number

                if(red.includes(parseInt(roulette_number))){
                    result.style.backgroundColor = "red"
                }
                else if (black.includes(parseInt(roulette_number))){
                    result.style.backgroundColor = "black"
                }
                else{
                    result.style.backgroundColor = "green"
                }
                clearInterval(interval_id)
            }
        }
    }

    var interval_id = setInterval(rotate_wheel, 5)
}