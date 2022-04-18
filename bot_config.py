from create_bot import dp
from aiogram import executor


from admin import admin_panel
import bot_scrypt

executor.start_polling(dp)