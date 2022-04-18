import sys
sys.path.append("/telegram_bot")
from create_bot import bot
sys.path.append("/telegram_bot/db")
from connector import sql_start, get_order

async def send_order(username):
    #gets order's info
    sql_start()
    order_info = await get_order(username)
    await bot.send_message("", "🔥 <b>Новый заказ:</b>", parse_mode="html")
    #if order should be delivered
    if order_info[0][5] == 1:
        #sends order's info to admin's chat
        await bot.send_message("", f"👱‍♂️ <b>Пользователь:</b>\n{order_info[0][0]}\n\n🏵 <b>Заказ:</b>\n{order_info[0][1]}\n\n💵 <b>Цена аренды:</b> {order_info[0][2]}\n\n💰 <b>Цена заказа:</b> {order_info[0][3]}\n\n📦 <b>Метод получения заказа:</b>\n🚗 Доставка\n\n🗺 <b>Адрес:</b>\n{order_info[0][4]}\n\n💸 <b>Метод оплаты:</b>\n{order_info[0][6]}\n\n", parse_mode="html")
    #if order shouldnt be delivered
    elif order_info[0][5] == 0:
        #sends order's info to admin's chat
        await bot.send_message("", f"👱‍♂️ <b>Пользователь:</b>\n{order_info[0][0]}\n\n🏵 <b>Заказ:</b>\n{order_info[0][1]}\n\n💵 <b>Цена аренды:</b> {order_info[0][2]}\n\n💰 <b>Цена заказа:</b> {order_info[0][3]}\n\n📦 <b>Метод получения заказа:</b>\n🚶🏻 Самовывоз\n\n💸 <b>Метод оплаты:</b>\n{order_info[0][6]}\n\n", parse_mode="html")

async def send_question(username, question):
    await bot.send_message("", f"❓<b>Вопрос от {username}:</b>\n{question}", parse_mode="html")