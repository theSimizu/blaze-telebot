from blaze_bot.blaze_data import BlazeDoubleCrawler
from blaze_bot.database import Users
from blaze_bot.telegram_bot import bot, format_strategy
from threading import Thread

blaze_data = BlazeDoubleCrawler().run()

def verify_strategies(data):
    strategies = Users.get_users_from_strategy(data)

    for strategy in strategies:
        seq = format_strategy(strategy[2])
        res = format_strategy(strategy[3])
        user_id = strategy[5]
        user = Users.filter_by('id', user_id)
        message = f'Padrao encontrado!!!\
                    \n{seq}\
                    \nJogue no {res}'
        bot.send_message(user.telegram, message)

    print(strategies)

def run_data(blaze_data):
    for data in blaze_data:
        print(data)
        verify_strategies(data)

def run_app():
    data_thread = Thread(target=run_data, args=[blaze_data])
    telegram_thread = Thread(target=bot.infinity_polling)
    
    data_thread.start()
    telegram_thread.start()
    
    data_thread.join()
    telegram_thread.join()



