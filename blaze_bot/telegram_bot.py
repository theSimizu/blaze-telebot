from dotenv import load_dotenv
from blaze_bot.database import Users
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import telebot
import re
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')

email_re = '[a-z0-9._{3,}]*[@][a-z]{3,}[.][a-z.*]*[.br]*'

bot = telebot.TeleBot(TOKEN)

############################################################ Functions ############################################################
# Options Keyboard
def keyboard(key_type='normal'):
    markup = ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
    if key_type == 'register':
        row = [KeyboardButton('SIM'), KeyboardButton('NAO')]
        markup.add(*row)
    elif key_type == 'terminate':
        markup = telebot.types.ReplyKeyboardRemove()
    return markup

def get_user(message):
    try:
        return Users.filter_by('telegram', message.from_user.id)
    except:
        return None 

def strategies_list(strategies):
    strategy_list = []
    for strategy in strategies:
        strat_name = strategy[0]
        strat_seq = format_strategy(strategy[1])
        choice = format_strategy(strategy[2])
        strategy_list.append((strat_name, strat_seq, choice))
    return strategy_list

def strategies_formater(strategy_list):
    strat = ''
    for strategy in strategy_list:
        strat_name = strategy[0]
        strat_seq = strategy[1]
        choice = strategy[2]
        strat += f"{strat_name} --> {strat_seq} = {choice}\n"
    return strat

def format_strategy(strategy):
    return strategy.replace('P', '⬛️').\
                    replace('B', '⬜️').\
                    replace('V', '🟥')

############################################################ Message Handlers ############################################################
# Start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Comandos:\n/register\n/create_strategy\n/my_strategies')

@bot.message_handler(commands=['register'])
def register(message):
    if get_user(message):
        bot.send_message(message.from_user.id, 'Telegram ja cadastrado. Deseja adicionar um email?', reply_markup=keyboard('register'))
    else:
        name = message.from_user.first_name
        telegram = message.from_user.id
        Users.create_user(name, telegram)
        bot.send_message(message.from_user.id, 'Telegram adicionado. Deseja adicionar um email?', reply_markup=keyboard('register'))
    bot.register_next_step_handler(message, register_email)

@bot.message_handler(commands=['create_strategy'])
def create_strategy(message):
    bot.send_message(message.from_user.id, 'De um nome para sua estrategia')
    bot.register_next_step_handler(message, register_strategy)

@bot.message_handler(commands=['my_strategies'])
def my_strategies(message):
    user = get_user(message)
    strategies = strategies_list(user.get_strategies())
    strat = strategies_formater(strategies)
    bot.send_message(message.from_user.id, strat)

@bot.message_handler(commands=['remove_strategy'])
def remove_strategy(message):
    user = get_user(message)
    strategies = strategies_list(user.get_strategies())
    strat = strategies_formater(strategies)
    bot.send_message(message.from_user.id, 'Qual estrategia voce quer remover? (Digite /cancel para canelar a acao)')
    bot.send_message(message.from_user.id, strat)
    bot.register_next_step_handler(message, delete_strategy, strategies)


############################################################ Next Steps ############################################################

# Email
def register_email(message):
#======================================== Callbacks ========================================
    def update_user_email(message):
        user = get_user(message)
        if re.search('[a-z0-9._{3,}]*[@][a-z]{3,}[.][a-z.*]*[.br]*', message.text):
            user.add_email(message.text)
            bot.send_message(message.from_user.id, 'Email registrado com sucesso!!!')
        else:
            bot.send_message(message.from_user.id, 'Email Invalido')
#============================================================================================
    if message.text == 'SIM':
        bot.send_message(message.from_user.id, 'Digite o email', reply_markup=keyboard('terminate'))
        bot.register_next_step_handler(message, update_user_email)

    if message.text == 'NAO':
        bot.send_message(message.from_user.id, 'Telegram registrado', reply_markup=keyboard('terminate'))


# Strategy
def register_strategy(message):
#======================================== Callbacks ========================================
    def save_sequence(message, strategy_name):
        seq = message.text.upper()
        if len(seq) > 20 or not tuple(sorted(set(seq + 'BPV'))) == ('B', 'P', 'V'):
            bot.reply_to(message, 'Sequencia invalida Por favor tente novamente.\
                                   \nLembre-se de usar apenas as letras P, V e B no maximo 20 vezes')
            bot.register_next_step_handler(message, save_sequence, strategy_name)
        else:
            strategy = {'name': strategy_name, 'strategy': seq}
            bot.reply_to(message, 'O que voce quer jogar quando ocorrer essa sequencia? (P, V, B)')
            bot.register_next_step_handler(message, save_play, strategy)

    def save_play(message, strategy: dict):
        choice = message.text.upper()
        if len(message.text) != 1 or choice not in ('B', 'P', 'V'):
            bot.reply_to(message, 'Valor invalido. Tente novamente (P, V, B)')
            bot.register_next_step_handler(message, save_play, strategy)
        else:
            user = get_user(message)
            strategy_name = strategy['name']
            strategy = strategy['strategy']
            user.create_strategy(strategy_name, strategy, choice)
            bot.reply_to(message, 'Estrategia registrada')
#============================================================================================
    strategy_name = message.text
    if not strategy_name.isalnum():
        bot.send_message(message.from_user.id, 'Nome invalido. Por favor use apenas letras e numeros')
        bot.register_next_step_handler(message, register_strategy)

    bot.send_message(message.from_user.id, 'Agora digite a sequencia da estrategia usando as letras P, V e B no maximo 20 vezes\
                                            \nP=Preto\nV=Vermelho\nB=Branco\
                                            \nExemplo:\
                                            \nPBBVVVVPVPPP = ⬛️⬜️⬜️🟥🟥🟥🟥⬛️🟥⬛️⬛️⬛️')
    bot.register_next_step_handler(message, save_sequence, strategy_name)

# Delete
def delete_strategy(message, strategies):
    if message.text == '/cancel':
        bot.send_message(message.from_user.id, 'Acao cancelada')
        return
    user = get_user(message)
    for strategy in strategies:
        if message.text == strategy[0]:
            user.delete_strategies(message)
            bot.send_message(message.from_user.id, 'Estrategia removida')
            return
    bot.send_message(message.from_user.id, 'Estrategia nao encontrada. Por favor tente novamente')
    bot.register_next_step_handler(message, delete_strategy, strategies)
    
    
            