from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
#create bot
TOKEN = ""
bot = Bot(token = TOKEN)
dp = Dispatcher(bot, storage = storage)
