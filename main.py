import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import register_all

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    register_all(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())