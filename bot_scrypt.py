from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
#importing bot 
from create_bot import bot, dp
#importing all database functions 
from db import sql_start, add_value, add_user, add_order, print_products, get_info, checker, receive_method, add_suggestion, pay_method_db, add_check, get_check, delete_check
#importing all keyboards
from markups import order_markup, main_markup, basket_markup, pick_method_markup, buy_markup, pay_method, cash_markup, menu_markup, basket_main_markup, pay_menu
#importing all admon functions
from admin import send_order, send_question
#importing qiwip2p for payment
from pyqiwip2p import QiwiP2P
import random

#some necessary variables
choices = []
rent_price = 0
deposit_price = 0
final_price = 0
offset = 0
limit = 5
showed = limit
message_def = ""
name = ""
remove_check = []

p2p = QiwiP2P(auth_key = "")

#adds some states for user
class Address(StatesGroup):
    address = State()
class Suggestion(StatesGroup):
    suggestion = State()
class Ask(StatesGroup):
    question = State()

#start function
@dp.message_handler(commands = ["start"])
async def begin(message: types.Message):
    global name
    #defines user
    user_info = await bot.get_chat_member(message.chat.id, message.from_user.id)
    #gets username
    name = user_info["user"]["username"]
    #sets user username to database
    sql_start()
    add_user(name)
    #greeting photo
    await bot.send_photo(message.chat.id, photo=open("ui/img/greeting_photo.png", "rb"), reply_markup = main_markup)

#show basket info by command
@dp.message_handler(commands = ["basket"])
async def basket_show(message: types.Message):
    global choices
    basket_games = "\n\n🎲 ".join(choices)
    #if basket is not empty
    if choices != []:
        await bot.send_message(message.chat.id, "<b>Корзина: </b>\n\n🎲 {games}\n\n<b>Сумма аренды:</b> {rent}\n\n<b>Сумма залога:</b> {deposit_price}\n\n<b>Общая сумма:</b> {final_price} ".format(games=basket_games, rent=rent_price, final_price=final_price, deposit_price=deposit_price), 
                        parse_mode="html", reply_markup = basket_markup)
    #if basket is empty
    elif choices == []:
        await bot.send_message(message.chat.id, "🕸 Корзина пуста")

#home menu by command
@dp.message_handler(commands = ["home"])
async def basket_show(message: types.Message):
    #if basket is not empty
    if choices == []:
        await bot.send_message(message.chat.id, "<b>Вы вышли в главное меню</b>", parse_mode="html", reply_markup = main_markup)
    #if basket is empty
    elif choices != []:
        await bot.send_message(message.chat.id, "<b>Вы вышли в главное меню</b>", parse_mode="html", reply_markup = basket_main_markup)

#choose game by command
@dp.message_handler(commands = ["choose"])
async def choose_game(message: types.Message):
    global offset, limit, showed,message_def
    offset = 0
    showed = limit
    #checks in db if any games are available and returns number
    sql_start()
    check = checker()
    message_def = message
    #checks if any games are available
    if check is not None:
        await bot.send_message(message.chat.id, "🎮 Игры в наличии:", reply_markup = order_markup)
        #prints all games from db (connector.py function)
        await print_products(message, offset, limit, showed)
        offset += limit
        showed += limit
    else:
        await bot.send_message(message.chat.id, "📭 Игр в наличии нет")

#reply buttons funcrions
@dp.message_handler(content_types = ['text'])
async def text(message: types.Message):
    global offset, limit, showed, message_def, name, choices, remove_check

    #if message text = choose game
    if message.text == "🎮 Выбрать игру":
        offset = 0
        showed = limit
        #checks in db if any games are available and returns number
        sql_start()
        check = checker()
        message_def = message
        #checks if any games are available
        if check is not None:
            await bot.send_message(message.chat.id, "🎮 Игры в наличии:", reply_markup = order_markup)
            #prints all games from db (connector.py function)
            await print_products(message, offset, limit, showed)
            offset += limit
            showed += limit
        else:
            await bot.send_message(message.chat.id, "📭 Игр в наличии нет")

    #if message text = basket
    elif message.text == "🗑 Корзина":
        basket_games = "\n\n🎲 ".join(choices)
        #if basket is not empty
        if choices != []:
            await bot.send_message(message.chat.id, "<b>Корзина: </b>\n\n🎲 {games}\n\n<b>Сумма аренды:</b> {rent}\n\n<b>Сумма залога:</b> {deposit_price}\n\n<b>Общая сумма:</b> {final_price} ".format(games=basket_games, rent=rent_price, final_price=final_price, deposit_price=deposit_price), 
                            parse_mode="html", reply_markup = basket_markup)
        #if basket is empty
        elif choices == []:
            await bot.send_message(message.chat.id, "🕸 Корзина пуста")

    #if message text = home
    elif message.text == "🏠 Главное меню":
        #if basket is not empty
        if choices == []:
            await bot.send_message(message.chat.id, "<b>Вы вышли в главное меню</b>", parse_mode="html", reply_markup = main_markup)
        #if basket is empty
        elif choices != []:
            await bot.send_message(message.chat.id, "<b>Вы вышли в главное меню</b>", parse_mode="html", reply_markup = basket_main_markup)

    elif message.text == "🌀 О нас":
        await bot.send_message(message.chat.id, "📘 <b>Borent</b> - это новый сервис, предоставляющий настольные игры в аренду на день и на неделю.\n\n🌟 Ассортимент игр постоянно увеличивается\n\n🎯 Прислушиваемся к вашим предложениям и идеям\n\n🤗 Ждем каждого в нашем сервисе!", parse_mode="html")
    
    elif message.text == "⭐️ FAQ":
        await bot.send_message(message.chat.id, "🏮 Ответы на популярные вопросы\n\n🔷 <b>Как мне забрать мой заказ?</b>\n🔹 Вы можете заказать доставку вашего заказа (платно), либо забрать его по адресу(бесплатно).\n\n🔷 <b>Как проходит оплата заказа?</b>\n🔹 После того, как вы оформили заказ, вы можете выбрать способ оплаты: банковская карта, наличные. Оплата наличными принимается только при самовывозе. Вы сможете оплатить заказ банковской картой по ссылке, полученной от бота.\n\n🔷 <b>Как мне вернуть заказ?</b>\n🔹Возврат заказа происходит по адресу:\n\n🔷 <b>Продавец долго не отвечает, что делать?</b>\n🔹 Свяжитесь с ним напрямую, ссылка на чат в телеграмме\n\n", parse_mode="html")
    
    #if message text = price
    elif message.text == "🖌 Спросить":
        await Ask.question.set()
        await bot.send_message(message.chat.id, "📋 Введите интересующий вас вопрос", parse_mode="html")
    
    #if message text = remove from basket
    elif message.text == "✂️ Убрать из корзины":
        #creating variable for indexing choices values
        choices_ind = 0
        #creating remove from basket markup
        remove_markup = InlineKeyboardMarkup(resize_keyboard = True)
        #for each item in basket
        for item in choices:
            #checks for how long user is going to rent a game
            rent_check = item[-6:]
            #gets game's name
            game_name = item.split(" -")[0]
            #if the game is rented for one day
            if rent_check == "1 день":
                #adds remove buttons to markup
                rem_day_button = InlineKeyboardButton(f"Убрать '{game_name}'", callback_data = f"rem_day_{game_name}i{choices_ind}")
                remove_markup.add(rem_day_button)
                remove_check.append(game_name)
            #if the game is rented for one week
            elif rent_check == "7 дней":
                #adds remove buttons to markup
                rem_week_button = InlineKeyboardButton(f"Убрать '{game_name}'", callback_data = f"rem_week_{game_name}i{choices_ind}")
                remove_markup.add(rem_week_button)
                remove_check.append(game_name)
            #equals index of value in choices
            choices_ind += 1
        await bot.send_message(message.chat.id, "Что убрать?", reply_markup= remove_markup)
    
    #if message text = formalize
    elif message.text == "🟢 Оформить":
        #defines user
        user_info = await bot.get_chat_member(message.chat.id, message.from_user.id)
        #defines username
        name = user_info["user"]["username"]
        #asserts basket games to a string
        order_games = ", ".join(choices)

        #adds order's info to db
        sql_start()
        add_order(1, order_games, 0, rent_price, final_price, name)

        await bot.send_message(message.chat.id, "🎯 Выберите метод получения заказа", reply_markup = pick_method_markup)    
    
    #if message text = pickup
    elif message.text == "🚶🏻 Самовывоз":
        await receive_method("Самовывоз", 0, name)
        await bot.send_message(message.chat.id, "🗺 Самовывоз с адреса:\n<b></b>", parse_mode="html", reply_markup= buy_markup)
    
    #if message text = delivery
    elif message.text == "🚗 Доставка":
        await Address.address.set()
        await bot.send_message(message.chat.id, "🔥 Доставка от <b>200</b> рублей\n(оплачивается отдельно)\n\nВведите адрес доставки:", parse_mode="html", )      
    
    #if message text = pay
    elif message.text == "💰 Оплатить":
        await bot.send_message(message.chat.id, "Выберите способ оплаты:", reply_markup = pay_method)

    #if message text = credit card
    elif message.text == "💳 Банковская карта":
        #adds credit card payment method to db
        sql_start()
        await pay_method_db("Банковская карта", name)
        #comment for qiwi bill
        comment = name + "_" + str(random.randint(1000, 9999))
        #bill config
        bill = p2p.bill(amount = int(final_price), lifetime = 15, comment = comment)
        #adds bill to db
        add_check(name, bill.bill_id)
        await bot.send_message(message.chat.id, f"Ваш счет на оплату сформирован: {bill.pay_url}\n На сумму: {final_price} рублей", reply_markup = pay_menu(url=bill.pay_url, bill = bill.bill_id))

    #if message text = cash
    elif message.text == "💵 Наличными":
        await bot.send_message(message.chat.id, "❗️ Оплата наличными только при самовывозе", reply_markup = cash_markup)    
        sql_start()
        await pay_method_db("Наличными", name)

    #if message text = submit
    elif message.text == "✅ Подтвердить":
        await bot.send_message(message.chat.id, "❇️ Ваш заказ принят, скоро с вами свяжется продавец", reply_markup= menu_markup)
        #sends username to a function to order_functions.py which sends the order info to admin chat
        await send_order(name)
        #removes all games from basket
        choices = []

    #if message text = change payment method
    elif message.text == "🖌 Изменить метод оплаты": 
        await bot.send_message(message.chat.id, "Выберите способ оплаты:", reply_markup = pay_method)

    #if message text = suggest a new game
    elif message.text == "✉️ Предложить игру":
        #activates state for saving suggestion from user
        await Suggestion.suggestion.set()
        await bot.send_message(message.chat.id, "⌨️ Введите названия игр, которые хотели бы увидеть у нас в сервисе")
    
#saves address from message
@dp.message_handler(state = Address.address)
async def load_address(message: types.Message, state: Address.address):
    address = message.text
    await bot.send_message(message.chat.id, "✅ Адрес записан", reply_markup = buy_markup)
    #adds address to db
    await receive_method(address, 1, name)
    await state.finish()

#saves suggestion from user
@dp.message_handler(state = Suggestion.suggestion)
async def load_suggestion(message: types.Message, state: Suggestion.suggestion):
    suggestion = message.text
    await bot.send_message(message.chat.id, "📤 Спасибо, ваше предложение сохранено", reply_markup = main_markup)
    #adds suggestion to db
    sql_start()
    await add_suggestion(suggestion, name)
    await state.finish()

#saves question from user
@dp.message_handler(state = Ask.question)
async def load_suggestion(message: types.Message, state: Suggestion.suggestion):
    global name
    question = message.text
    await bot.send_message(message.chat.id, "✳️ Ваш вопрос сохранен и отправлен продавцу", reply_markup = main_markup)
    #adds question to db
    await send_question(name, question)
    await state.finish()

#payment check
@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def check(callback: types.CallbackQuery):
    global choices, name
    #gets bill id from callback query
    bill = str(callback.data[6:])
    #checks if bill is in db
    all_info = get_check(bill)
    #if bill is in db
    if all_info != False:
        #if bill is paid
        if str(p2p.check(bill_id = bill).status) == "PAID":
            await bot.send_message(callback.from_user.id, "❇️ Ваш заказ принят, скоро с вами свяжется продавец", reply_markup= menu_markup)
            #sends username to a function to order_functions.py
            await send_order(name)
            #removes all games from basket
            choices = []
            #deletes check
            delete_check(name)
        else:
            await bot.send_message(callback.from_user.id, "🔒 Вы не оплатили заказ", reply_markup = pay_menu(False, bill= bill))
    else:
        await bot.send_message(callback.from_user.id, "❔ Счет не найден")

#add to basket functions
@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def add_to_basket(callback: types.CallbackQuery):

    global rent_price, final_price, deposit_price, offset, limit, showed

    #adds game's price per day and info to basket  
    if callback.data.startswith("add_day_"):
        #if game is not in basket
        if callback.data.replace("add_day_", "") not in choices:
            #gets game's info from db
            sql_start()
            product = await get_info(callback.data.replace("add_day_", ""))
            #alerts that game is in basket 
            await callback.answer(text=f"Игра '{product[0][0]}' добавлена в корзину")

            #appends game's name and rental period to basket list
            choices.append(product[0][0] + " - 📅 1 день")
            #summarise game's prices with basket variables
            final_price += int(product[0][1]) + int(product[0][3])
            rent_price += int(product[0][1])
            deposit_price += int(product[0][3])

            #sets that a game is unavailable
            add_value(product[0][0], 0)
    
    #adds game's price per week and info to basket  
    elif callback.data.startswith("add_week_"):
        #if game is not in basket
        if callback.data.replace("add_week_", "") not in choices:
            #gets game's info from db
            sql_start()
            product = await get_info(callback.data.replace("add_week_", ""))
            #alerts that game is in basket 
            await callback.answer(text=f"Игра '{product[0][0]}' добавлена в корзину")
            
            #appends game's name and rental period to basket lis
            choices.append(product[0][0] + " - 📅 7 дней")
            #summarise game's prices with basket variables
            final_price += int(product[0][2]) + int(product[0][3])
            rent_price += int(product[0][2])
            deposit_price += int(product[0][3])

            #sets that a game is unavailable
            add_value(product[0][0], 0)
    
#remove from basket functions
@dp.callback_query_handler(lambda c: c.data.startswith("rem_"))
async def remove_from_basket(callback: types.CallbackQuery):

    global rent_price, final_price, deposit_price, offset, limit, showed
    
    #removes one day game rental from basket
    if callback.data.startswith("rem_day_"):
        basket_name = callback.data.replace("rem_day_", "")
        #getting the name of a game and game's index in choices list
        game_name_ind = basket_name.split(" -")[0]
        #getting game's index in choices list
        choices_index = game_name_ind.split("i")[1]
        #getting game's name
        game_name = game_name_ind.split("i")[0]
        #if game is in basket
        if game_name in remove_check:

            #gets game's info from db
            sql_start()
            product = await get_info(game_name)
            #alerts that game has been removed from basket
            await callback.answer(text=f"Игра '{game_name}' убрана из корзины")

            #removes game's name from remove basket(special variable, which contains only names of games)
            remove_check.remove(game_name)
            #removes game from basket
            choices.pop(int(choices_index))
            #subtracts game's prices from basket variables
            final_price -= int(product[0][1]) + int(product[0][3])
            rent_price -= int(product[0][1])
            deposit_price -= int(product[0][3])

            #sets that game is available
            add_value(game_name, 1)

    #removes one week game rental from basket
    elif callback.data.startswith("rem_week_"):
        basket_name = callback.data.replace("rem_week_", "")
        #getting the name of a game and game's index in choices list
        game_name_ind = basket_name.split(" -")[0]
        #getting game's index in choices list
        choices_index = game_name_ind.split("i")[1]
        #getting game's name
        game_name = game_name_ind.split("i")[0]
        #if game is in basket
        if game_name in remove_check:

            #gets game's info from db
            sql_start()
            product = await get_info(game_name)
            #alerts that game has been removed from basket
            await callback.answer(text=f"Игра '{game_name}' убрана из корзины")

            #removes game's name from remove basket(special variable, which contains only names of games)
            remove_check.remove(game_name)
            #removes game from basket
            choices.pop(int(choices_index))
            #subtracts game's prices from basket variables
            final_price -= int(product[0][2]) + int(product[0][3])
            rent_price -= int(product[0][2])
            deposit_price -= int(product[0][3])

            #sets that game is available
            add_value(game_name, 1)

#load more function
@dp.callback_query_handler(lambda c: c.data)
async def load_more(callback: types.CallbackQuery):
    global message_def, offset, limit, showed
    #load_more function
    if callback.data == "load_more":
        await print_products(message_def, offset, limit, showed)
        #appending offset for db
        offset += limit
        #counting showed games
        showed += limit