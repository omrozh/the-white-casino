from app import Statistics, db, Affiliate, User, UserWallet, MaxMoneyBet, reflect_bet_loss
from sys import argv
from uuid import uuid4
from app import bcrypt
from datetime import datetime
from payments import create_user_wallet, create_btc_wallet

if argv[1] == "init-app":
    db.drop_all()
    db.create_all()
    first_user = User(username="house", email="house@twc.com", password=bcrypt.generate_password_hash("house@twc.2004"),
                      account_balance=1000, referrer="house", id="house", received_first_time_bonus=True, is_admin=True)
    new_wallet = create_user_wallet()
    new_btc_wallet = create_btc_wallet()
    first_wallet = UserWallet(id="platform-usdt", private_key=new_wallet["private_key"],
                              public_key=new_wallet["public_key"], address=new_wallet["base58check_address"])
    btc_first_wallet = UserWallet(id="platform-btc", private_key=new_btc_wallet["private_key"],
                                  public_key=new_btc_wallet["public_key"],
                                  address=new_btc_wallet["address"])
    db.session.add(first_wallet)
    first_user.usdt_wallet = first_wallet.id
    first_user.btc_wallet = btc_first_wallet.id
    db.session.add(first_user)
    db.session.add(btc_first_wallet)
    db.session.add(first_wallet)
    first_affiliate = Affiliate(id="house", amount_wagered=0, connected_account=first_user.id)
    new_stat = Statistics(id=str(uuid4()), total_amount_wagered=0, number_of_bets=0, year=datetime.now().year,
                          month=datetime.now().month,
                          bet_loss=0)
    db.session.add(new_stat)
    db.session.add(first_affiliate)

if argv[1] == "add-affiliate":
    first_user = User(username="house", email="house@twc.com", password=bcrypt.generate_password_hash("house@twc.2004"),
                      account_balance=0, referrer="house", id="house", received_first_time_bonus=True)
    new_wallet = create_user_wallet()
    first_wallet = UserWallet(id=str(uuid4()), private_key=new_wallet["private_key"],
                              public_key=new_wallet["public_key"], address=new_wallet["base58check_address"])
    db.session.add(first_wallet)
    first_user.usdt_wallet = first_wallet.id
    db.session.add(first_user)
    db.session.add(first_wallet)
    first_affiliate = Affiliate(id="house", amount_wagered=0, connected_account=first_user.id)
    db.session.add(first_affiliate)

if argv[1] == "add-statistic":
    new_stat = Statistics(id=str(uuid4()), total_amount_wagered=0, number_of_bets=0, year=argv[2], month=argv[3],
                          bet_loss=0)
    db.session.add(new_stat)

if argv[1] == "view-statistics":
    all_statistics = Statistics.query.all()
    for i in all_statistics:
        house_edge = "{:.2f}".format(((i.total_amount_wagered - i.bet_loss) / i.total_amount_wagered) * 100)
        print(f"Date: {i.month}/{i.year} | Number of Bets: {i.number_of_bets} | "
              f"Amount Wagered: {'{:.2f}'.format(i.total_amount_wagered)}, Bet Loss: {'{:.2f}'.format(i.bet_loss)} "
              f"| Margin: {house_edge}%")

if argv[1] == "distribute-max-money":
    all_bets = MaxMoneyBet.query.filter_by(year=datetime.now().year). \
        filter_by(month=datetime.now().month).filter_by(day=datetime.now().day)
    current_max_bet = all_bets.first()
    total_bets = 0
    for i in all_bets.all():
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

    print("Completed")

if argv[1] == "view-affiliate":
    for i in Affiliate.query.all():
        print(f"Amount Wagered: {i.amount_wagered}")

if argv[1] == "distribute-affiliate-earnings":
    this_month_statistic = \
        Statistics.query.filter_by(month=datetime.now().month).filter_by(year=datetime.now().year).first()
    profit = this_month_statistic.total_amount_wagered - this_month_statistic.bet_loss

    if profit < 0:
        exit()

    distributed_affiliate_profit = (profit / 100) * 60
    master_affiliate_profit = (profit / 100) * 5

    for i in Affiliate.query.all():
        current_profit_for_affiliate = \
            distributed_affiliate_profit * (i.amount_wagered / this_month_statistic.total_amount_wagered)

        total_wagered_master = 0

        User.query.get(i.connected_account).account_balance += float(current_profit_for_affiliate)

        for c in Affiliate.query.filter_by(master_affiliate=i.master_affiliate).all():
            total_wagered_master += c.amount_wagered

        current_profit_for_master = \
            master_affiliate_profit * (total_wagered_master / this_month_statistic.total_amount_wagered)

        i.amount_wagered = 0

        if i.master_affiliate:
            User.query.get(Affiliate.query.get(i.master_affiliate).connected_account).account_balance \
                += float(current_profit_for_master)

db.session.commit()
