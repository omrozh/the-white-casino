from payments import create_user_wallet, make_payment, get_btc_wallet_balance, make_payment_btc, create_btc_wallet
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import requests
import random
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, current_user, UserMixin, logout_user
import flask
from datetime import datetime, timedelta
from flask_qrcode import QRcode
import json

app = flask.Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "IwouldnotdothisifIwerentdesperate"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

qr = QRcode(app)

games_and_descriptions = {
    "wheel": "In this the white casino original you place a  bet and turn the wheel. "
             "You either double your money or leave empty handed.",
    "up_or_down": "In this The White Casino original you try to guess if the next number is going to be higher or "
                  "lower then the displayed number. For every correct guess get 10% compounded every time. In this "
                  "game we do not have a statistical edge a correct strategy and a strong will can even give you the "
                  "advantage.",
    "limbo": "In this The White Casino original you try to guess the multiplier of your bet. If you guess it too low "
             "you lose on your potential earnings since you will only receive the multiplier you anticipated however "
             "if you guess higher then the actual multiplier you lose it all.",
    "slots": "In this version of this classic casino game player tries to match two or three symbols in the slot "
             "machine. 2 bananas or 2 melons equals 0.5x, 2 Diamonds, 3 bananas, 3 melons or 2 golds equals 2x, "
             "3 golds equals 3x and 3 diamonds equals 4x.",
    "multiplier": "In this The White Casino original you choose one of the five cards and receive the multiplier"
                  " written on their front. Four of them are going to make you lose money and one will triple it",
    "hit_or_pass": "In this The White Casino original player decides to get a new multiplier or withdraw with the "
                   "existing ones. One you open a new card there is no going back when you withdraw all of your "
                   "multipliers are multiplied and your wins are calculated. ",
    "max_money": "Drawn daily and the player that bets the highest amount wins all the money",
    "double": "Double or nothing is a The White Casino original with high adrenalin. "
                         "In this high stakes game you either lose all your money or double it in each round you can go"
                         "as long as you want and there is unlimited earnings potential.",
    "divo": "In this The White Casino original you divide your bet into different sections and only one of them wins. "
            "Create your own play style according to your risk tolerance.",
    "horse_races": "In the White Casino version of the horse race betting all the bets are pooled into a prize pool "
                   "and "
                   "distributed equally between winners. Each bet is 5$,"
                   " make riskier bets to split the prize with fewer people."
}


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    account_balance = db.Column(db.Float)
    usdt_wallet = db.Column(db.String)
    btc_wallet = db.Column(db.String)
    referrer = db.Column(db.String)
    received_first_time_bonus = db.Column(db.Boolean, default=False)
    won_max_money_yesterday = db.Column(db.Boolean, default=False)
    latest_ip = db.Column(db.String)
    account_currency = db.Column(db.String, default="usdt")
    is_admin = db.Column(db.Boolean, default=False)


class UserWallet(db.Model):
    id = db.Column(db.String, primary_key=True)
    private_key = db.Column(db.String)
    public_key = db.Column(db.String)
    xprivate_key = db.Column(db.String)
    xpublic_key = db.Column(db.String)
    address = db.Column(db.String)
    wif = db.Column(db.String)
    xpublic_key_prime = db.Column(db.String)


class ShortenAffiliateLink(db.Model):
    id = db.Column(db.String, primary_key=True)
    real_cont = db.Column(db.String)


class UpOrDown(db.Model):
    id = db.Column(db.String, primary_key=True)
    current_number = db.Column(db.Integer)
    current_offer = db.Column(db.Float)
    minimum_number = db.Column(db.Integer)
    maximum_number = db.Column(db.Integer)


class Affiliate(db.Model):
    id = db.Column(db.String, primary_key=True)
    usdt_wallet = db.Column(db.String)
    master_affiliate = db.Column(db.String)
    amount_wagered = db.Column(db.Float)
    connected_account = db.Column(db.String)


class Statistics(db.Model):
    id = db.Column(db.String, primary_key=True)
    total_amount_wagered = db.Column(db.Float)
    number_of_bets = db.Column(db.Integer)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    bet_loss = db.Column(db.Float)


class HitOrPass(db.Model):
    id = db.Column(db.String, primary_key=True)
    multipliers = db.Column(db.String, default="")
    bet_amount = db.Column(db.Float)


class MaxMoneyBet(db.Model):
    id = db.Column(db.String, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    bet_amount = db.Column(db.Float)
    associated_user = db.Column(db.String)


class DoubleOrNothing(db.Model):
    id = db.Column(db.String, primary_key=True)
    current_offer = db.Column(db.Float)


class HorseRace(db.Model):
    id = db.Column(db.String, primary_key=True)
    date = db.Column(db.String)
    horses = db.Column(db.String)
    country = db.Column(db.String)
    time = db.Column(db.String)
    winner = db.Column(db.String, default="To be determined")


class HorseRaceBet(db.Model):
    id = db.Column(db.String, primary_key=True)
    associated_user = db.Column(db.String)
    horse = db.Column(db.String)
    race = db.Column(db.String)


def authorize_affiliate_bonus(request_val):
    real_ip = request_val["HTTP_X_FORWARDED_FOR"]
    if User.query.filter_by(latest_ip=real_ip).first():
        return False
    else:
        return True


def create_wallet_instance():
    new_wallet = create_user_wallet()
    new_user_wallet = UserWallet(id=str(uuid4()), private_key=new_wallet["private_key"],
                                 public_key=new_wallet["public_key"], address=new_wallet["base58check_address"])
    db.session.add(new_user_wallet)
    db.session.commit()
    return new_user_wallet


def create_btc_wallet_instance():
    new_wallet = create_btc_wallet()
    new_user_wallet = UserWallet(id=str(uuid4()), private_key=new_wallet["private_key"],
                                 public_key=new_wallet["public_key"], address=new_wallet["address"])
    db.session.add(new_user_wallet)
    db.session.commit()
    return new_user_wallet


def get_balance(address, token_symbol="USDT"):
    url = "https://apilist.tronscan.org/api/account"
    payload = {
        "address": address,
    }
    res = requests.get(url, params=payload)
    trc20token_balances = json.loads(res.text)["trc20token_balances"]
    token_balance = next((item for item in trc20token_balances if item["tokenAbbr"] == token_symbol), None)
    if token_balance == None:
        return 0
    else:
        return int(token_balance["balance"])


@app.route("/update_account_balance")
@login_required
def update_balance():
    user_wallet = UserWallet.query.get(current_user.usdt_wallet)
    user_wallet2 = UserWallet.query.get(current_user.btc_wallet)

    address = user_wallet.address
    balance = get_balance(address)

    current_user.usdt_wallet = create_wallet_instance().id
    current_user.account_balance += int(balance) / 1000000
    current_user.account_balance += int(get_btc_wallet_balance(user_wallet2.private_key)) * 100000000

    db.session.commit()
    return flask.redirect("/")


# Requires an update for first time bonus


def generate_limbo_options():
    options = []
    for i in range(100, 5000):
        for c in range(int(((100 / i) ** 2) * 100)):
            options.append(i / 100)

    return options


def update_stats_and_affiliate(amount, user_ref):
    amount = float(amount)
    User.query.get(Affiliate.query.get(current_user.referrer).connected_account).account_balance += float(amount / 200)
    reflect_bet_loss(float(amount / 200))
    this_month_statistic = \
        Statistics.query.filter_by(month=datetime.now().month).filter_by(year=datetime.now().year).first()
    this_month_statistic.total_amount_wagered += float(amount)
    this_month_statistic.number_of_bets += 1

    current_user_affiliate = Affiliate.query.get(user_ref.referrer)

    current_user_affiliate.amount_wagered += float(amount)

    db.session.commit()


def reflect_bet_loss(amount):
    this_month_statistic = \
        Statistics.query.filter_by(month=datetime.now().month).filter_by(year=datetime.now().year).first()
    this_month_statistic.bet_loss += amount
    db.session.commit()


@app.route("/aff=<affiliate_id>")
def affiliate_redirect(affiliate_id):
    return flask.redirect(ShortenAffiliateLink.query.get(affiliate_id).real_cont)


# 127.0.0.1:5000/aff=168f8b3a-1bc4-4656-8258-8a8cdaf49e50 - Link format / Remember to use shorten url id not user id


@app.route("/signup-post", methods=["POST", "GET"])
def signup_post():
    if flask.request.method == "POST":
        values = flask.request.values

        affiliate_ref = Affiliate.query.get(values["affiliate_ref"])

        reference_affiliate = affiliate_ref if affiliate_ref is not None else Affiliate.query.first()

        new_user = User(id=str(uuid4()), username=values["username"], email=values["email"],
                        password=bcrypt.generate_password_hash(values["password"]),
                        account_balance=0.0, referrer=reference_affiliate.id,
                        received_first_time_bonus=authorize_affiliate_bonus(flask.request.headers))

        user_affilate_account = Affiliate(id=str(uuid4()), amount_wagered=0, connected_account=new_user.id,
                                          master_affiliate=reference_affiliate.id)

        add_shorten_affiliate_link = ShortenAffiliateLink(id=str(uuid4()),
                                                          real_cont=f"/signup?affiliate_ref={user_affilate_account.id}")
        db.session.add(add_shorten_affiliate_link)
        db.session.add(user_affilate_account)
        new_user.usdt_wallet = create_wallet_instance().id
        new_user.btc_wallet = create_btc_wallet_instance().id
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return "Successful Account Creation"


@app.route("/signup")
def signup():
    return flask.render_template("signup.html")


@app.route("/signin", methods=["POST", "GET"])
def signin():
    if flask.request.method == "POST":
        values = flask.request.values
        user = User.query.filter_by(email=values["email"]).first()

        if bcrypt.check_password_hash(user.password, values["password"]):
            login_user(user)
            return flask.redirect("/")

    return flask.render_template("signin.html")


@app.route("/")
def home():
    balance = current_user.account_balance if current_user.is_authenticated else 0
    return flask.render_template("home.html", is_authenticated=current_user.is_authenticated,
                                 balance="{:.2f}".format(balance))


@app.route("/wheel")
@login_required
def wheel():
    return flask.render_template("roulette.html")


@app.route("/current_account_balance")
@login_required
def current_account_balance():
    return str("{:.2f}".format(current_user.account_balance))


@app.route("/play-wheel", methods=["POST", "GET"])
@login_required
def play_wheel():
    if flask.request.method == "POST":
        values = flask.request.values
        try:
            bet_amount = float(values["betting_amount"])
        except ValueError:
            bet_amount = 0
        if current_user.account_balance < float(bet_amount):
            return "Inadequate Balance"
        current_user.account_balance -= float(bet_amount)

        update_stats_and_affiliate(bet_amount, current_user)

        random_number = random.randint(1, 5)
        if random_number == 5:
            random_number = 1

        if random_number == 2 or random_number == 3:
            reflect_bet_loss(float(bet_amount) * 2)
            current_user.account_balance += float(bet_amount) * 2

        db.session.commit()

        return str(random_number)


@app.route("/start_up_or_down", methods=["POST", "GET"])
@login_required
def start_up_or_down():
    if flask.request.method == "POST":
        values = flask.request.values
        if current_user.account_balance < float(values["bet_amount"]):
            return "Inadequate Balance"
        bet_amount = float(values["bet_amount"])
        current_user.account_balance -= bet_amount

        update_stats_and_affiliate(values["bet_amount"], current_user)

        minimum_number = random.randint(0, 50)
        maximum_number = random.randint(100, 250)

        new_up_or_down_game = UpOrDown(id=str(uuid4()), current_number=random.randint(minimum_number, maximum_number),
                                       current_offer=bet_amount - (bet_amount / 100), minimum_number=minimum_number,
                                       maximum_number=maximum_number)

        db.session.add(new_up_or_down_game)
        db.session.commit()
        return new_up_or_down_game.id


@app.route("/get_number_up_or_down/<game_id>")
@login_required
def get_number_up_or_down(game_id):
    return flask.jsonify(
        {
            "current_number": UpOrDown.query.get(game_id).current_number,
            "current_offer": "{:.2f}".format(UpOrDown.query.get(game_id).current_offer),
        }
    )


@app.route("/play_up_or_down/<game_id>", methods=["POST", "GET"])
@login_required
def play_up_or_down(game_id):
    if flask.request.method == "POST":
        values = flask.request.values
        current_game = UpOrDown.query.get(game_id)
        direction = values["choosen_direction"] == "up"

        new_val = random.randint(current_game.minimum_number, current_game.maximum_number)

        win = False

        total_boundary = current_game.maximum_number - current_game.minimum_number

        upper_win = float(abs(current_game.minimum_number - current_game.current_number) / 100) * 1.1
        lower_win = float(abs(current_game.maximum_number - current_game.current_number) / 100) * 1.1

        if lower_win < 1:
            lower_win = 1.1
        if upper_win < 1:
            upper_win = 1.1

        if direction and new_val > current_game.current_number:
            current_game.current_offer = current_game.current_offer * upper_win
            win = True
        elif not direction and new_val < current_game.current_number:
            current_game.current_offer = current_game.current_offer * lower_win
            win = True
        else:
            db.session.delete(current_game)

        current_game.current_number = new_val

        db.session.commit()

        return str(win)


@app.route("/lose_up_or_down")
@login_required
def lose_up_or_down():
    return flask.render_template("lose_up_or_down.html")


@app.route("/win_up_or_down/<game_id>")
@login_required
def win_up_or_down(game_id):
    total_win = UpOrDown.query.get(game_id).current_offer
    current_user.account_balance += round(total_win, 2)
    reflect_bet_loss(round(total_win, 2))

    db.session.delete(UpOrDown.query.get(game_id))
    db.session.commit()
    return flask.render_template("win_up_or_down.html", winnings="{:.2f}".format(total_win))


@app.route("/up_or_down")
@login_required
def up_or_down():
    return flask.render_template("up_or_down.html")


@app.route("/static/<filename>")
def static_host(filename):
    return flask.send_file("static/" + filename)


@app.route("/assets/<filename>")
def asset_host(filename):
    return flask.send_file("assets/" + filename)


@app.route("/limbo")
@login_required
def limbo():
    return flask.render_template("limbo.html")


@app.route("/limbo_guess_multiplier", methods=["POST", "GET"])
@login_required
def limbo_guess_multiplier():
    if flask.request.method == "POST":
        values = flask.request.values
        if current_user.account_balance < float(values["bet_amount"]):
            return "Inadequate Balance"
        options = generate_limbo_options()

        multiplier_choice = random.choice(options)

        update_stats_and_affiliate(values["bet_amount"], current_user)

        if float(values["multiplier"]) <= multiplier_choice:

            current_user.account_balance -= float(values["bet_amount"])
            if not current_user.received_first_time_bonus:
                current_user.account_balance += float(values["bet_amount"]) * \
                                                ((float(values["multiplier"]) - 1) * 5) + 1
            else:
                current_user.account_balance += float(values["bet_amount"]) * float(values["multiplier"])
            reflect_bet_loss(float(values["bet_amount"]) * float(values["multiplier"]))
        else:
            current_user.account_balance -= float(values["bet_amount"])

        current_user.received_first_time_bonus = True

        db.session.commit()

        return str(multiplier_choice)


@app.route("/multiplier")
@login_required
def multiplier():
    return flask.render_template("multiplier.html")


@app.route("/multiplier_post", methods=["POST", "GET"])
@login_required
def multiplier_post():
    if flask.request.method == "POST":
        values = flask.request.values
        if current_user.account_balance < float(values["bet_amount"]):
            return "Inadequate Balance"
        outcomes = ["0.2", "0.2", str("{:.2f}".format(random.random())), str("{:.2f}".format(random.random())), "3"]
        random.shuffle(outcomes)

        current_user.account_balance -= float(values["bet_amount"])

        update_stats_and_affiliate(float(values["bet_amount"]), current_user)

        if not current_user.received_first_time_bonus:
            reflect_bet_loss(float(values["bet_amount"]) * float(outcomes[int(values["choosen_number"])]) * 5)
            current_user.account_balance += float(values["bet_amount"]) * \
                                            float(outcomes[int(values["choosen_number"])] * 5)
        else:
            reflect_bet_loss(float(values["bet_amount"]) * float(outcomes[int(values["choosen_number"])]))
            current_user.account_balance += float(values["bet_amount"]) * float(outcomes[int(values["choosen_number"])])

        current_user.received_first_time_bonus = True

        db.session.commit()

        return "&".join(outcomes)


# Connect to frontend


@app.route("/game/<game_title>")
@login_required
def play_game(game_title):
    return flask.render_template("game.html", game_title=str.capitalize(game_title.replace("_", " ")),
                                 game_description=games_and_descriptions.get(game_title), game_url=game_title)


@app.route("/sub_affiliate_registration", methods=["POST", "GET"])
@login_required
def affiliate_registration():
    if flask.request.method == "POST":
        values = flask.request.values
        master_ref = Affiliate.query.get(values["master_ref"])
        master_affiliate = master_ref if master_ref else Affiliate.query.get("house")
        new_affiliate = Affiliate(id=str(uuid4()), amount_wagered=0, master_affiliate=master_affiliate.id)
        db.session.add(new_affiliate)
    return flask.render_template("")


# Affiliate link format:
# https://www.thewhitecasino.com/signup?affiliate_ref=81398b1b-e4f4-4b67-a208-b381dd4bfa6d

@app.route("/logout")
def logout():
    logout_user()
    return flask.redirect("/")


@app.route("/game_banners/<filename>")
def game_banner(filename):
    return flask.send_file(f"game_banners/{filename}")


@app.route("/play_slots", methods=["POST", "GET"])
@login_required
def play_slots():
    if flask.request.method == "POST":
        values = flask.request.values
        if current_user.account_balance < float(values["bet_amount"]):
            return "Inadequate Balance"
        current_user.account_balance -= float(values["bet_amount"])
        slots_pick = [random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)]

        update_stats_and_affiliate(float(values["bet_amount"]), current_user)

        if slots_pick.count(1) == 2 or slots_pick.count(2) == 2:
            current_user.account_balance += float(values["bet_amount"]) / 2
            reflect_bet_loss(float(values["bet_amount"]) / 2)
        elif slots_pick.count(3) == 2 or slots_pick.count(4) == 2 or slots_pick.count(1) == 3 or slots_pick.count(
                2) == 3:
            current_user.account_balance += float(values["bet_amount"]) * 2
            reflect_bet_loss(float(values["bet_amount"]) * 2)
        elif slots_pick.count(3) == 3:
            current_user.account_balance += float(values["bet_amount"]) * 3
            reflect_bet_loss(float(values["bet_amount"]) * 3)
        elif slots_pick.count(4) == 3:
            current_user.account_balance += float(values["bet_amount"]) * 4
            reflect_bet_loss(float(values["bet_amount"]) * 4)

        db.session.commit()

        return "&".join(map(str, slots_pick))


@app.route("/hit_or_pass")
@login_required
def hit_or_pass():
    return flask.render_template("hit_or_pass.html")


# Connect to front-end


@app.route("/start_hit_or_pass", methods=["POST", "GET"])
@login_required
def start_hit_or_pass():
    if flask.request.method == "POST":
        values = flask.request.values
        if current_user.account_balance < float(values["bet_amount"]):
            return "Inadequate Balance"
        current_user.account_balance -= float(values["bet_amount"])
        update_stats_and_affiliate(float(values["bet_amount"]), current_user)

        multiplier_n = random.uniform(0, 6)

        if multiplier_n > 3.1:
            multiplier_n = random.uniform(0, 0.8)

        multiplier_n2 = random.uniform(0, 6)

        if multiplier_n2 > 3.1:
            multiplier_n2 = random.uniform(0, 0.8)

        multiplier_n3 = random.uniform(0, 6)

        if multiplier_n3 > 3.1:
            multiplier_n3 = random.uniform(0, 0.8)

        multiplier_str = f"{round(multiplier_n, 2)}&{round(multiplier_n2, 2)}&{round(multiplier_n3, 2)}"
        new_hit_or_pass = HitOrPass(id=str(uuid4()), multipliers=multiplier_str,
                                    bet_amount=float(values["bet_amount"]))
        db.session.add(new_hit_or_pass)
        db.session.commit()
        return new_hit_or_pass.id


@app.route("/init_hit_or_pass", methods=["POST", "GET"])
@login_required
def init_hit_or_pass():
    if flask.request.method == "POST":
        values = flask.request.values
        current_game = HitOrPass.query.get(values["game_id"])
        return current_game.multipliers


@app.route("/hit_hit_or_pass", methods=["POST", "GET"])
@login_required
def hit_hit_or_pass():
    if flask.request.method == "POST":
        values = flask.request.values
        current_game = HitOrPass.query.get(values["game_id"])
        if len(current_game.multipliers.split("&")) == 6:
            return "End Game"

        multiplier_n = random.uniform(0, 6)

        if multiplier_n > 3.1:
            multiplier_n = random.uniform(0, 0.8)

        current_game.multipliers += "&" + str(round(multiplier_n, 2))
        db.session.commit()
        return current_game.multipliers


@app.route("/finish_hit_or_pass/<game_id>")
@login_required
def finish_hit_or_pass(game_id):
    current_game = HitOrPass.query.get(game_id)
    total_win = 1
    for i in current_game.multipliers.split("&"):
        total_win *= float(i)

    if not current_user.received_first_time_bonus:
        current_user.account_balance += current_game.bet_amount * total_win * 5
        reflect_bet_loss(current_game.bet_amount * total_win * 5)

    else:
        current_user.account_balance += current_game.bet_amount * total_win
        reflect_bet_loss(current_game.bet_amount * total_win)

    db.session.delete(current_game)
    current_user.received_first_time_bonus = True
    db.session.commit()

    return flask.render_template("hit_or_pass_finish.html",
                                 winnings="{:.2f}".format(current_game.bet_amount * total_win))


@app.route("/slots")
@login_required
def slots():
    return flask.render_template("slots.html")


@app.route("/partners")
def partners():
    partners_link = f"https://www.thewhitecasino.com/aff="
    if current_user.is_authenticated:
        aff_id = Affiliate.query.filter_by(connected_account=current_user.id).first().id
        short_aff = ShortenAffiliateLink.query.filter_by(real_cont="/signup?affiliate_ref=" + aff_id).first().id
        partners_link += short_aff
    return flask.render_template("partnership.html", affiliate_link=partners_link)


@app.route("/make-deposit")
@login_required
def make_deposit():
    wallet_address = UserWallet.query.get(current_user.usdt_wallet).address
    return flask.render_template("make_deposit.html", wallet_address=wallet_address)


@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    horse_race_bets = HorseRaceBet.query.filter_by(associated_user=current_user.id).all()
    if flask.request.method == "POST":
        if bcrypt.check_password_hash(current_user.password, flask.request.values["password"]):
            if flask.request.values["wallet_address"][0] == "T" and len(flask.request.values["wallet_address"]) > 20:
                platform_wallet = UserWallet.query.get("platform-usdt")
                platform_btc_wallet = UserWallet.query.get("platform-btc")
                make_payment(wallet_transfer_from=platform_wallet,
                             wallet_transfer_to=flask.request.values["wallet_address"],
                             amount=current_user.account_balance, transfer_type="direct_address")
                make_payment_btc(wallet_transfer_from=platform_btc_wallet,
                                 wallet_transfer_to=flask.request.values["wallet_address"],
                                 amount=current_user.account_balance, transfer_type="direct_address")
                current_user.account_balance = 0
                db.session.commit()
            else:
                return '''
                    <script>
                        alert('Cannot validate address')
                        document.location = '/profile'
                    </script>
                '''

        else:
            return '''
                <script>
                    alert('Incorrect password')
                    document.location = '/profile'
                </script>
            '''
    all_daily_bets = MaxMoneyBet.query.filter_by(year=datetime.now().year). \
        filter_by(month=datetime.now().month).filter_by(day=datetime.now().day). \
        filter_by(associated_user=current_user.id).all()

    return flask.render_template("profile.html", user=current_user,
                                 wallet_address=UserWallet.query.get(current_user.usdt_wallet).address,
                                 all_daily_bets=all_daily_bets, horse_race_bets=horse_race_bets)


@app.route("/max_money", methods=["POST", "GET"])
@login_required
def max_money():
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_bets = MaxMoneyBet.query.filter_by(year=yesterday.year).filter_by(month=yesterday.month). \
        filter_by(day=yesterday.day).all()
    today_bets = MaxMoneyBet.query.filter_by(year=datetime.now().year).filter_by(month=datetime.now().month). \
        filter_by(day=datetime.now().day).all()
    total_daily_bets = round((sum([i.bet_amount for i in today_bets]) / 100) * 99, 2)
    try:
        winnings = round((sum([i.bet_amount for i in yesterday_bets]) / 100) * 99, 2)
        highest_bet = max([i.bet_amount for i in yesterday_bets])
        winner_username = None
        for i in yesterday_bets:
            if i.bet_amount == highest_bet:
                winner_username = User.query.get(i.associated_user).username
    except ValueError:
        winner_username = None
        winnings = 0
        highest_bet = 0

    if flask.request.method == "POST":
        if current_user.account_balance < float(flask.request.values["bet_amount"]) \
                or float(flask.request.values["bet_amount"]) < 0:
            return '''
                <script>
                    alert('Insufficient Balance')
                    document.location = '/make-deposit'
                </script>
            '''
        new_max_money_bet = MaxMoneyBet(id=str(uuid4()), associated_user=current_user.id, year=datetime.now().year,
                                        day=datetime.now().day, month=datetime.now().month,
                                        bet_amount=float(flask.request.values["bet_amount"]))
        db.session.add(new_max_money_bet)
        current_user.account_balance -= new_max_money_bet.bet_amount
        db.session.commit()
        update_stats_and_affiliate(new_max_money_bet.bet_amount, current_user)
        return flask.render_template("success_saving.html")
    return flask.render_template("max_money.html", winnings=winnings, highest_bet=highest_bet,
                                 winner_username=winner_username, total_daily_bets=total_daily_bets)


@app.route("/double")
@login_required
def double_or_nothing():
    return flask.render_template("double_or_nothing.html")


@app.route("/create_double_or_nothing", methods=["POST", "GET"])
@login_required
def create_double_or_nothing():
    if flask.request.method == "POST":
        new_game = DoubleOrNothing(id=str(uuid4()), current_offer=float(flask.request.values["bet_amount"]))
        update_stats_and_affiliate(new_game.current_offer, current_user)
        if current_user.account_balance >= new_game.current_offer:
            current_user.account_balance -= new_game.current_offer
            db.session.add(new_game)
        else:
            return "Inadequate Balance"
        db.session.commit()
        return new_game.id


@app.route("/double_double_or_nothing", methods=["POST", "GET"])
@login_required
def double_double_or_nothing():
    if flask.request.method == "POST":
        current_dn_game = DoubleOrNothing.query.get(flask.request.values["game_id"])
        if random.randint(0, 100) > 51:
            current_dn_game.current_offer *= 2
            db.session.commit()
            return "Double"
        else:
            db.session.delete(current_dn_game)
            db.session.commit()
            return "Nothing"


@app.route("/win_double_or_nothing/<game_id>")
@login_required
def win_double_or_nothing(game_id):
    current_game = DoubleOrNothing.query.get(game_id)
    current_user.account_balance += current_game.current_offer
    reflect_bet_loss(current_game.current_offer)
    db.session.commit()
    return flask.render_template("win_double_or_nothing.html", winnings=current_game.current_offer)


@app.route("/divo")
@login_required
def divo():
    return flask.render_template("divo.html")


@app.route("/play_divo", methods=["POST", "GET"])
@login_required
def play_divo():
    if flask.request.method == "POST":
        bets = [float(i) if not i == '' else 0 for i in flask.request.values["bets"].split("/")]
        if sum(bets) > current_user.account_balance:
            return "Inadequate Balance"
        multipliers = [0, 0, 0, 4, 0]
        random.shuffle(multipliers)
        total_value = 0
        for i in range(len(multipliers)):
            total_value += bets[i] * multipliers[i]
        current_user.account_balance += total_value

        current_user.account_balance -= sum(bets)

        update_stats_and_affiliate(sum(bets), current_user)
        reflect_bet_loss(total_value)

        multipliers = [str(i) for i in multipliers]

        return "&".join(multipliers)


@app.route("/lose_double_or_nothing")
def lose_double_or_nothing():
    return flask.render_template("lose_double_or_nothing.html")


@app.route("/horse_race_bet/<race_id>", methods=["POST", "GET"])
@login_required
def horse_race_bet(race_id):
    horses = HorseRace.query.get(race_id).horses.split("&")
    bets = HorseRaceBet.query.filter_by(race=race_id)
    all_bets_per_horse = []
    total_bets = len(bets.all())
    for i in horses:
        bet_per_horse = len(bets.filter_by(horse=i).all())
        all_bets_per_horse.append(round((bet_per_horse / total_bets) * 100, 2))

    output_horses = []
    for i in range(len(horses)):
        output_horses.append((horses[i], all_bets_per_horse[i]))

    return flask.render_template("horse_race_bet.html", horses=output_horses, race_id=race_id)


@app.route("/place_horse_bet/<race_id>/<horse>")
@login_required
def play_horse_bet(race_id, horse):
    if current_user.account_balance >= 5 and current_user.account_currency == "usdt":
        current_user.account_balance -= 5
    else:
        return "Only USDT accounts can bet on horse races with a minimum bet of 5$"

    new_horse_race_bet = HorseRaceBet(associated_user=current_user.id, id=str(uuid4()),
                                      race=race_id, horse=horse)
    db.session.add(new_horse_race_bet)
    db.session.commit()
    return '''
        <script>
            alert('Bet placed')
            document.location = '/horse_races'
        </script>
    '''


@app.route("/horse_races")
@login_required
def horse_races():
    all_races = HorseRace.query.\
        filter_by(date=f"{datetime.now().day}-{datetime.now().month}-{datetime.now().year}").all()
    return flask.render_template("horse_races.html", all_races=all_races)


@app.route("/admin", methods=["POST", "GET"])
@login_required
def new_horse_race():
    existing_races = HorseRace.query.\
        filter_by(date=f"{datetime.now().day}-{datetime.now().month}-{datetime.now().year}").all()
    races_processed = [{
        "horses": i.horses.split("&"),
        "id": i.id,
        "country": i.country,
        "time": i.time,
        "date": i.date
    } for i in existing_races]
    if current_user.is_admin:
        if flask.request.method == "POST":
            values = flask.request.values
            add_horse_race = HorseRace(id=str(uuid4()), date=values["date"], horses=values["horses"],
                                       country=values["country"], time=values["time"])
            db.session.add(add_horse_race)
            db.session.commit()
        return flask.render_template("add_horse_race.html", existing_races=races_processed)


@app.route("/set_winner/<horse>/<race_id>")
@login_required
def set_winner(horse, race_id):
    if current_user.is_admin:
        HorseRace.query.get(race_id).winner = horse
        db.session.commit()
        return flask.redirect("/horse_race_admin")


@app.route("/distribute_daily_race_earnings")
@login_required
def distribute_daily_race_earnings():
    if current_user.is_admin:
        daily_races = HorseRace.query. \
            filter_by(date=f"{datetime.now().day}-{datetime.now().month}-{datetime.now().year}").all()
        for i in daily_races:
            winners = HorseRaceBet.query.filter_by(horse=i.winner).all()
            all_bets = HorseRaceBet.query.filter_by(race=i.id).all()
            winnings = len(all_bets) * 5
            winning_per_user = ((winnings / len(winners)) / 100) * 96
            for c in winners:
                User.query.get(c.associated_user).account_balance += winning_per_user
        db.session.commit()
        return flask.redirect("/")


@app.route("/distribute_max_money")
@login_required
def distribute_max_money():
    if current_user.is_admin:
        all_bets_max_money = MaxMoneyBet.query.filter_by(year=datetime.now().year). \
            filter_by(month=datetime.now().month).filter_by(day=datetime.now().day)
        current_max_bet = all_bets_max_money.first()
        total_bets = 0
        for i in all_bets_max_money.all():
            total_bets += i.bet_amount
            if i.bet_amount > current_max_bet.bet_amount:
                current_max_bet = i
        for i in User.query.filter_by(won_max_money_yesterday=True):
            i.won_max_money_yesterday = False

        winner = User.query.get(current_max_bet.associated_user)
        winner.won_max_money_yesterday = True
        winner.account_balance += round((total_bets / 100) * 99, 2)
        reflect_bet_loss(round((total_bets / 100) * 99, 2))
        db.session.commit()
        return flask.redirect("/")

@app.route("/favicon.ico")
def favicon():
    return flask.send_file("favicon.png")


@app.errorhandler(500)
def page_not_found(e):
    return flask.redirect("/")


@app.errorhandler(401)
def page_not_found(e):
    return flask.redirect("/signup")
