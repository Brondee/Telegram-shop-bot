from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
import sys
#importing bot
sys.path.append("/telegram_bot")
from create_bot import bot, dp
#importing functions related to db
sys.path.append("/telegram_bot/db")
from connector import sql_start, add_game, add_value, del_game
#importing all markups from file
sys.path.append("/telegram_bot/markups")
from markups import admin_markup, sub_res_markup

ID = None

class AddGame(StatesGroup):
    name = State()
    price_day = State()
    price_week = State()
    deposit = State()
    photo = State()
class SetAvailable(StatesGroup):
    game_name = State()
class DeleteGame(StatesGroup):
    game_name_del = State()

game_info = {}

#admin panel activation
@dp.message_handler(lambda message: "Админ панель" in message.text, is_chat_admin = True)
async def admin_panel(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, "📟 Админ панель, выберите действие:", reply_markup = admin_markup)
    await message.delete()

#add new game begining
@dp.message_handler(lambda message: "🎲 Добавить новую игру" in message.text, state = None)
async def adm_start(message: types.Message):
    if message.from_user.id == ID:
        await AddGame.name.set()
        await bot.send_message(message.chat.id, "📖 Введи название игры")

#asserts game's name to state
@dp.message_handler(state = AddGame.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await AddGame.next()
        await bot.send_message(message.chat.id, "💸 Теперь введи цену аренды за сутки")

#asserts game's price per day to state
@dp.message_handler(state = AddGame.price_day)
async def load_price_day(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['day_price'] = message.text
        await AddGame.next()
        await bot.send_message(message.chat.id, "💵 Теперь введи цену аренды за неделю")

#asserts game's price per week to state
@dp.message_handler(state = AddGame.price_week)
async def load_price_week(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data["week_price"] = message.text
        await AddGame.next()
        await bot.send_message(message.chat.id, "💰 Теперь введи сумму залога")

#asserts game's deposit price to state
@dp.message_handler(state = AddGame.deposit)
async def load_deposit(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data["deposit"] = message.text
        await AddGame.next()
        await bot.send_message(message.chat.id, "🏞 Теперь загрузи фото игры")

#asserts game's photo to state
@dp.message_handler(content_types = ["photo"], state = AddGame.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        global game_info
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        async with state.proxy() as data:
            await bot.send_message(message.chat.id, "📋 Введенная информация:", reply_markup = sub_res_markup)
            await bot.send_message(message.chat.id, f"Название: {data['name']}\nЦена за день: {data['day_price']}\nЦена за  неделю: {data['week_price']}\nЗалог: {data['deposit']}")
            game_info = data
        await state.finish()

#adds all info about a new game to db
@dp.message_handler(lambda message: "✅ Добавить" in message.text)
async def add_games(message: types.Message):
    if message.from_user.id == ID:
        global game_info
        if game_info != {}:
            sql_start()
            await add_game(game_info['name'], game_info['day_price'], game_info['week_price'], game_info['deposit'], game_info['photo'])
            await bot.send_message(message.chat.id, "🟢 Игра добавлена в базу данных", reply_markup = admin_markup)
        elif game_info == {}:
            await bot.send_message(message.chat.id, "🔴 Сначала введите данные новой игры")

#if text message = reset, resets all info 
@dp.message_handler(lambda message: "🗯 Сбросить" in message.text)
async def reset_info(message: types.Message):
    if message.from_user.id == ID:
        await bot.send_message(message.chat.id, "📂 Изменения сброшены", reply_markup = admin_markup)

#if message text = delete game
@dp.message_handler(lambda message: "💥 Удалить игру" in message.text)
async def delete_game(message: types.Message):
    await DeleteGame.game_name_del.set()
    await bot.send_message(message.chat.id, "⌨️ Введи название игры, котороую нужно удалить")

#deletes a game from db
@dp.message_handler(state = DeleteGame.game_name_del)
async def delete_game_db(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        game_name = message.text
        sql_start()
        await del_game(game_name)
        await bot.send_message(message.chat.id, f"☄️ Игра '{game_name}' удалена из базы данных")
        await state.finish()

#if message text = set avalailable
@dp.message_handler(lambda message: "📪 Вернуть в наличие" in message.text)
async def set_av_name(message: types.Message):
    if message.from_user.id == ID:
        await SetAvailable.game_name.set()
        await bot.send_message(message.chat.id, "🏷 Введи название игры, которой нужно вернуть статус 'В наличие'")

#gets game's name and sets it available
@dp.message_handler(state = SetAvailable.game_name)
async def set_av(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as name:
            name['game_name'] = message.text
            sql_start()
            add_value(name["game_name"], 1)
            await bot.send_message(message.chat.id, f"🎉 Игра '{name['game_name']}' теперь снова в наличии!")
        await state.finish()