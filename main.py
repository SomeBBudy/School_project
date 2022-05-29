import telebot
from telebot import types
from config import TOKEN, secret, key, BreadID, SomeBBudyID
from datetime import datetime
import os
import json
import pandas as pd
import requests
import time
import plotly.graph_objects as go
from client import FtxClient
import string


bot = telebot.TeleBot(TOKEN)


ftx_client = FtxClient(
    api_key=key,
    api_secret=secret
)
open_ord = ftx_client.get_open_orders()
endpoint_url = 'https://ftx.com/api/markets'
base_currency = 'TONCOIN'
base_currency1 = 'BTC'
base_currency2 = 'ETH'
quote_currency = 'USD'


request_url = f'{endpoint_url}/{base_currency}/{quote_currency}'
market = requests.get(request_url).json()
market_ask1 = market['result']['ask']

request_url = f'{endpoint_url}/{base_currency1}/{quote_currency}' 
market = requests.get(request_url).json()
market_ask2 = market['result']['ask']

request_url = f'{endpoint_url}/{base_currency2}/{quote_currency}'
market = requests.get(request_url).json()
market_ask3 = market['result']['ask']

def change(now, then):
    ch=((float(now) - float(then))/float(then))*100.0
    return ch
def okr(numObj, digits=0):
    return f"{numObj:.{digits}f}"

users = [SomeBBudyID, BreadID]


@bot.message_handler(func=lambda message: message.chat.id not in users, commands=['sell', 'cancel_order', 'buy', 'modify_cancel', 'order_list', 'sell_ton', 'sell_eth', 'sell_btc', 'buy_ton', 'buy_btc', 'buy_eth'])
def block(message):
    bot.send_message(message.chat.id, 'У Вас нет прав на выполнение данной команды')

@bot.message_handler(commands=['help'])
def commands_list(message):
    bot.send_message(message.chat.id, 'Команды доступные для бота:'
                                      '\n/help - Список всех команд'
                                      '\n/price - Цена доступных криптовалют'
                                      '\n/sell - Выставление ордера на продажу'
                                      '\n/cancel_order - Отмена ордеров'
                                      '\n/balance - Вывод баланса')

@bot.message_handler(commands=['balance'])
def balance(message):
    balance = ftx_client.get_balances()

    for i in range(4):
        bot.send_message(message.chat.id, f"{balance[i]['coin']} - {balance[i]['total']}")


@bot.message_handler(commands=['price'])
def crypto_pricelist(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_TON = types.InlineKeyboardButton(text='TonCoin', callback_data='ton')
    item_BTC = types.InlineKeyboardButton(text='BitCoin', callback_data='btc')
    item_ETH = types.InlineKeyboardButton(text='Ethereum', callback_data='eth')

    markup_inline.add(item_TON, item_BTC, item_ETH)
    bot.send_message(message.chat.id, 'Выберите интересующую вас криптовалюту:',
                     reply_markup = markup_inline
                     )

@bot.message_handler(commands=['sell'])
def set_order_sell(message):
    markup_inline_sell = types.InlineKeyboardMarkup()
    sell_TON = types.InlineKeyboardButton(text='TonCoin', callback_data='sell_ton')
    sell_BTC = types.InlineKeyboardButton(text='BitCoin', callback_data='sell_btc')
    sell_ETH = types.InlineKeyboardButton(text='Ethereum', callback_data='sell_eth')

    markup_inline_sell.add(sell_TON, sell_BTC, sell_ETH)
    bot.send_message(message.chat.id, 'Выберите криптовалюту на продажу:',
                     reply_markup = markup_inline_sell
                     )


@bot.message_handler(commands=['buy'])
def set_order_buy(message):
    markup_inline_buy = types.InlineKeyboardMarkup()
    buy_TON = types.InlineKeyboardButton(text='TonCoin', callback_data='buy_ton')
    buy_BTC = types.InlineKeyboardButton(text='BitCoin', callback_data='buy_btc')
    buy_ETH = types.InlineKeyboardButton(text='Ethereum', callback_data='buy_eth')

    markup_inline_buy.add(buy_TON, buy_BTC, buy_ETH)
    bot.send_message(message.chat.id, 'Выберите криптовалюту на закуп:',
                     reply_markup = markup_inline_buy
                     )

@bot.callback_query_handler(func= lambda call: True)
def answer_sell(call):
    if call.data == 'sell_ton':
        bot.send_message(call.message.chat.id, 'Введите команду /sell_ton')
    elif call.data == 'sell_btc':
        bot.send_message(call.message.chat.id, 'Введите команду /sell_btc')
    elif call.data == 'sell_eth':
        bot.send_message(call.message.chat.id, 'Введите команду /sell_eth')
    elif call.data == 'ton':
        bot.send_message(call.message.chat.id, f'Стоимость криптовалюты: {market_ask1}$')
    elif call.data == 'btc':
        bot.send_message(call.message.chat.id, f'Стоимость криптовалюты: {market_ask2}$')
    elif call.data == 'eth':
        bot.send_message(call.message.chat.id, f'Стоимость криптовалюты: {market_ask3}$')
    elif call.data == 'buy_ton':
        bot.send_message(call.message.chat.id, 'Введите команду /buy_ton')
    elif call.data == 'buy_btc':
        bot.send_message(call.message.chat.id, 'Введите команду /buy_btc')
    elif call.data == 'buy_eth':
        bot.send_message(call.message.chat.id, 'Введите команду /buy_eth')
    elif call.data == 'delete_orders':
        try:
            co_result = ftx_client.cancel_orders()
            bot.send_message(call.message.chat.id, 'Все ордеры удалены')
        except Exception as e:
            bot.send_message(call.message.chat.id, 'Ошибка при удалении ордера: {e}')
    elif call.data == 'cancel_delete':
        bot.send_message(call.message.chat.id, 'Не надо, так не надо')
    elif call.data == '6hours':
        hstPrices = ftx_client.get_historical_prices(market=f"{base_currency}/{quote_currency}")
        n = 6 * 12
        now = hstPrices[-1]['high']
        then = hstPrices[-n - 1]['high']
        if change(now, then) > 0:
            bot.send_message(call.message.chat.id, f"Изменение цены за 6 часов: +{okr(change(now, then), 2)}%")
        else:
            bot.send_message(call.message.chat.id, f"Изменение цены за 6 часов: {okr(change(now, then), 2)}%")
    elif call.data == '24hours':
        hstPrices = ftx_client.get_historical_prices(market=f"{base_currency}/{quote_currency}")
        n = 24 * 12
        now = hstPrices[-1]['high']
        then = hstPrices[-n - 1]['high']
        if change(now, then) > 0:
            bot.send_message(call.message.chat.id, f"Изменение цены за 24 часов: +{okr(change(now, then), 2)}%")
        else:
            bot.send_message(call.message.chat.id, f"Изменение цены за 24 часов: {okr(change(now, then), 2)}%")

    elif call.data == '96hours':
        hstPrices = ftx_client.get_historical_prices(market=f"{base_currency}/{quote_currency}")
        n = 96 * 12
        now = hstPrices[-1]['high']
        then = hstPrices[-n - 1]['high']
        if change(now, then) > 0:
            bot.send_message(call.message.chat.id, f"Изменение цены за 4 дня: +{okr(change(now, then), 2)}%")
        else:
            bot.send_message(call.message.chat.id, f"Изменение цены за 4 дня: {okr(change(now, then), 2)}%")



@bot.message_handler(commands=['sell_ton'])
def ton_sell1(message):
    msg = bot.send_message(message.chat.id, 'Введите количество криптовалюты на продажу:')
    bot.register_next_step_handler(msg, ton_sell2)

def ton_sell2(message):
    amount = message.text
    try:
        bo_result = ftx_client.place_order(
            market=f"{base_currency}/{quote_currency}",
            side="sell",
            price=market_ask1 * 20,
            size=amount
        )
        print(bo_result)
        bot.send_message(message.chat.id, 'Ордер успешно выставлен')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при выставлении ордера: {e}')

@bot.message_handler(commands=['sell_btc'])
def btc_sell1(message):
    msg = bot.send_message(message.chat.id, 'Введите количество криптовалюты на продажу:')
    bot.register_next_step_handler(msg, ton_sell2)

def btc_sell2(message):
    amount = message.text
    try:
        bo_result = ftx_client.place_order(
            market=f"{base_currency}/{quote_currency}",
            side="sell",
            price=market_ask2 * 20,
            size=amount
        )
        print(bo_result)
        bot.send_message(message.chat.id, 'Ордер успешно выставлен')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при выставлении ордера: {e}')

@bot.message_handler(commands=['sell_btc'])
def eth_sell1(message):
    msg = bot.send_message(message.chat.id, 'Введите количество криптовалюты на продажу:')
    bot.register_next_step_handler(msg, ton_sell2)

def eth_sell2(message):
    amount = message.text
    try:
        bo_result = ftx_client.place_order(
            market=f"{base_currency}/{quote_currency}",
            side="sell",
            price=market_ask3 * 20,
            size=amount
        )
        print(bo_result)
        bot.send_message(message.chat.id, 'Ордер успешно выставлен')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при выставлении ордера: {e}')

@bot.message_handler(commands=['buy_ton'])
def ton_buy1(message):
    msg = bot.send_message(message.chat.id, 'Введите количество криптовалюты на покупку:')
    bot.register_next_step_handler(msg, ton_buy2)

def ton_buy2(message):
    amount = message.text
    try:
        bo_result = ftx_client.place_order(
            market=f"{base_currency}/{quote_currency}",
            side="buy",
            price=market_ask1 * 0.002,
            size=amount
        )
        print(bo_result)
        bot.send_message(message.chat.id, 'Ордер успешно выставлен')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при выставлении ордера: {e}')

@bot.message_handler(commands=['buy_btc'])
def btc_buy1(message):
    msg = bot.send_message(message.chat.id, 'Введите количество криптовалюты на покупку:')
    bot.register_next_step_handler(msg, btc_buy2)

def btc_buy2(message):
    amount = message.text
    try:
        bo_result = ftx_client.place_order(
            market=f"{base_currency}/{quote_currency}",
            side="buy",
            price=market_ask2 * 0.002,
            size=amount
        )
        print(bo_result)
        bot.send_message(message.chat.id, 'Ордер успешно выставлен')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при выставлении ордера: {e}')

@bot.message_handler(commands=['buy_btc'])
def eth_buy1(message):
    msg = bot.send_message(message.chat.id, 'Введите количество криптовалюты на покупку:')
    bot.register_next_step_handler(msg, ton_buy2)

def eth_buy2(message):
    amount = message.text
    try:
        bo_result = ftx_client.place_order(
            market=f"{base_currency}/{quote_currency}",
            side="buy",
            price=market_ask3 * 0.002,
            size=amount
        )
        print(bo_result)
        bot.send_message(message.chat.id, 'Ордер успешно выставлен')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при выставлении ордера: {e}')

@bot.message_handler(commands=['cancel_order'])
def cancel_orders(message):
    markup_inline_cancel_order = types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton(text='Да', callback_data='delete_orders')
    item_no = types.InlineKeyboardButton(text='Нет', callback_data='cancel_delete')

    markup_inline_cancel_order.add(item_yes, item_no)
    bot.send_message(message.chat.id, 'Вы действительно хотите удалить ВСЕ ордеры?',
                     reply_markup=markup_inline_cancel_order
                     )

@bot.message_handler(commands=['order_list'])
def order_list(message):
    open_ord = ftx_client.get_open_orders()
    n = len(open_ord)
    for i in range(n):
        bot.send_message(message.chat.id, f"  Ордер #{i + 1}  маркет: {open_ord[i]['market']} Количество: {open_ord[i]['size']} Цена: {open_ord[i]['price']}$ Операция: {open_ord[i]['side']}")

@bot.message_handler(commands=['modify_cancel'])
def modify_cancel(message):
    open_ord = ftx_client.get_open_orders()
    n = len(open_ord)
    bot.send_message(message.chat.id, 'Список всех ордеров:\n')
    for i in range(n):
        msg = bot.send_message(message.chat.id, f"  Ордер #{i + 1}  Mаркет: {open_ord[i]['market']} Количество: {open_ord[i]['size']} Цена: {open_ord[i]['price']}$ Операция: {open_ord[i]['side']}")
        bot.register_next_step_handler(msg, modify_cancel1)
    bot.send_message(message.chat.id, 'Введите номер ордера, который надо удалить:')


def modify_cancel1(message):
    a = int(message.text)
    open_ord = ftx_client.get_open_orders()

    co_result = ftx_client.cancel_order(
        order_id=open_ord[a - 1]['id']
    )

    bot.send_message(message.chat.id, f'Успешно удалили ордер #{a}')



@bot.message_handler(commands=['change'])
def change1(message):
    markup_inline_change1 = types.InlineKeyboardMarkup()
    item_6 = types.InlineKeyboardButton(text='6 часов', callback_data='6hours')
    item_24 = types.InlineKeyboardButton(text='24 часа', callback_data='24hours')
    item_96 = types.InlineKeyboardButton(text='4 дня', callback_data='96hours')

    markup_inline_change1.add(item_6,item_24,item_96)
    bot.send_message(message.chat.id, 'За какой период вы хотите посмотреть изменение цены TonCoin?',
                     reply_markup=markup_inline_change1
                     )






if __name__ == '__main__':
    bot.infinity_polling()




