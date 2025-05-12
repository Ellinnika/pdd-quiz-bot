from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import pandas as pd
import random

quiz_router = Router()
df = pd.read_excel("questions.xlsx")

user_sessions = {}
MAX_QUESTIONS = 10

@quiz_router.message(Command("start"))
async def start_quiz(message: Message):
    user_id = message.from_user.id
    user_sessions[user_id] = {
        "score": 0,
        "total": 0,
        "asked": [],
        "mode": "quiz"
    }
    await send_question(message, user_id)

async def send_question(message: Message, user_id: int):
    session = user_sessions[user_id]
    available = df[~df["Вопрос"].isin(session["asked"])]
    if available.empty:
        await message.answer("❗ Вопросы закончились.")
        return

    row = available.sample().iloc[0]
    session["asked"].append(row["Вопрос"])

    question_text = str(row["Вопрос"])
    correct = str(row["Правильный ответ"]).strip()

    variants = []
    correct_index = None
    for i, col in enumerate(["Вариант 1", "Вариант 2", "Вариант 3", "Вариант 4"], start=1):
        val = row.get(col)
        if pd.notna(val):
            val_str = str(val).strip()
            if val_str:
                variants.append(val_str)
                if str(i) == correct:
                    correct_index = len(variants)

    if not variants or correct_index is None:
        await message.answer("⚠ Проблема с вопросом. Пропускаем.")
        return await send_question(message, user_id)

    session["current"] = {
        "correct_index": correct_index,
        "correct_text": variants[correct_index - 1],
        "variants": variants
    }

    text = f"❓ {question_text}\n\n" + "\n".join([f"{i + 1}. {v}" for i, v in enumerate(variants)])
    builder = InlineKeyboardBuilder()
    for i in range(len(variants)):
        builder.button(text=str(i + 1), callback_data=f"answer:{i + 1}")
    builder.adjust(2)

    image_url = row.get("Ссылка на изображение")
    if pd.notna(image_url) and isinstance(image_url, str) and image_url.startswith("http"):
        await message.answer_photo(photo=image_url, caption=text, reply_markup=builder.as_markup())
    else:
        await message.answer(text, reply_markup=builder.as_markup())

@quiz_router.callback_query(F.data.startswith("answer:"))
async def answer_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        await callback.answer("Сессия не найдена.")
        return

    answer_index = int(callback.data.split(":")[1])
    correct_index = session["current"]["correct_index"]
    correct_text = session["current"]["correct_text"]

    if answer_index == correct_index:
        session["score"] += 1
        await callback.message.answer("✅ Верно!")
    else:
        await callback.message.answer(f"❌ Неверно. Правильный ответ: {correct_text}")

    session["total"] += 1
    if session["total"] >= MAX_QUESTIONS:
        await callback.message.answer(f"🏁 Опрос завершён. Правильных: {session['score']} из {session['total']}")
    else:
        await send_question(callback.message, user_id)

    await callback.answer()