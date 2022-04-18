import sqlite3
import sys
sys.path.append("/telegram_bot")
from create_bot import bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
sys.path.append("/telegram_bot/markups")
from markups_file import load_markup

#connects to database and create table with two columns
def sql_start():
    global base, cursor
    base = sqlite3.connect("db/database.db")
    cursor = base.cursor()

#adds values to database's columns
def add_value(name, available):
    cursor.execute("UPDATE game_checker SET available == ? WHERE game_name == ?", (available, name))
    base.commit()
    print(name + " Updated successfully")

#adds new user
def add_user(username):
    cursor.execute("INSERT OR IGNORE INTO users(username_tg) VALUES(?)", (username,))
    base.commit()

#sends order's info to db 
def add_order(ordered, order_text, order_paid, rent_price, order_price, username):
    cursor.execute("UPDATE users SET ordered == ?, order_text == ?, order_paid == ?, rent_price == ?, order_price == ? WHERE username_tg == ?", (ordered, order_text, order_paid, rent_price, order_price, username))
    base.commit()

#checks if any games are available
def checker():
    check = cursor.execute("SELECT * FROM game_checker WHERE available == 1 LIMIT 1").fetchone()
    base.commit()
    return check

#sends message with each game
async def print_products(message, offset, limit, showed):
    for obj in cursor.execute(f"SELECT * FROM game_checker WHERE available == 1 LIMIT {limit} OFFSET {offset}").fetchall():
        #adds inline markup for adding to basket
        add_markup = InlineKeyboardMarkup(resize_keyboard = True, row_width = 1)
        day_btn = InlineKeyboardButton(f"Арендовать '{obj[0]}' на день", callback_data = f"add_day_{obj[0]}")
        week_btn = InlineKeyboardButton(f"Арендовать '{obj[0]}' на неделю", callback_data = f"add_week_{obj[0]}")
        add_markup.add(day_btn, week_btn)
        #sends all info about each product with button to order
        await bot.send_photo(message.chat.id, obj[5] , f'‎\n🥏 <b>{obj[0]}</b>\n\n🔹 Цена за день: {obj[2]}\n\n🔹 Цена за неделю: {obj[3]}\n\n🔹 Залог: {obj[4]}', parse_mode="html", reply_markup = add_markup)
    #counts how many games are in db
    row_counter = cursor.execute("SELECT COUNT(*) FROM game_checker WHERE available == 1").fetchone()
    counter = row_counter[0]
    #cheks if it is ok to show load more button
    if counter > showed and counter != showed:
        await bot.send_message(message.chat.id, f"Показано <b>{showed}</b> игр из <b>{counter}</b>", parse_mode='html', reply_markup = load_markup)
    elif counter < showed:
        await bot.send_message(message.chat.id, f"Показано <b>{counter}</b> игр из <b>{counter}</b>", parse_mode='html')    
    else:
        await bot.send_message(message.chat.id, f"Показано <b>{showed}</b> игр из <b>{counter}</b>", parse_mode='html')

#gets paricular game's info
async def get_info(name):
    product = cursor.execute("SELECT game_name, price_day, price_week, deposit FROM game_checker WHERE game_name == ?", (name,)).fetchmany()
    base.commit()
    return product

#updates user's address in db
async def receive_method(adress, is_delivery, username):
    cursor.execute("UPDATE users SET user_adress == ?, delivery == ? WHERE username_tg == ?", (adress, is_delivery, username))
    base.commit()

#sets payment method to db
async def pay_method_db(method, username):
    cursor.execute("UPDATE users SET pay_method == ? WHERE username_tg == ?", (method, username))
    base.commit()

#adds user's suggestion to db
async def add_suggestion(text, username):
    cursor.execute("UPDATE users SET suggestion == ? WHERE username_tg == ?", (text, username))
    base.commit()

#gets order's info from db
async def get_order(username):
    order = cursor.execute("SELECT username_tg, order_text, rent_price, order_price, user_adress, delivery, pay_method FROM users WHERE username_tg == ?", (username,)).fetchmany()
    base.commit()
    return order

#inserts a new game into db
async def add_game(name, day_price, week_price, deposit, photo):
    cursor.execute("INSERT INTO game_checker(game_name, price_day, price_week, deposit, photo) VALUES(?,?,?,?,?)", (name, day_price, week_price, deposit, photo, ))
    base.commit()

#deletes a game from db
async def del_game(game_name):
    cursor.execute("DELETE FROM game_checker WHERE game_name == ?", (game_name, ))
    base.commit()

#adds a check to db
def add_check(username, bill_id):
    cursor.execute("UPDATE users SET bill_id == ? WHERE username_tg == ?", (bill_id, username, ))
    base.commit()
    
#checks if a bill is in db
def get_check(bill_id):
    check = cursor.execute("SELECT * FROM users WHERE bill_id == ?", (bill_id, )).fetchone()
    base.commit()
    if not bool(len(check)):
        return False
    else:
        return check[0]

#deletes a bill from db
def delete_check(username):
    cursor.execute("UPDATE users SET bill_id == ? WHERE username_tg == ?", ("no bill yet", username, ))
    base.commit()
