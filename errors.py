from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def fallback(message: Message):
    await message.answer("❗ Я не понял команду. Попробуй ещё раз или нажми /start.")
