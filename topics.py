from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import pandas as pd
import random

topics_router = Router()
df = pd.read_excel("questions.xlsx")
user_topic_sessions = {}
chapter_index_map = []

@topics_router.message(Command("tema"))
async def choose_topic(message: Message):
    global chapter_index_map
    chapters = df["Глава ПДД"].dropna().unique().tolist()
    if not chapters:
        await message.answer("⚠️ Темы не найдены. Проверь файл questions.xlsx.")
        return

    chapters.sort()
    chapter_index_map = chapters
    builder = InlineKeyboardBuilder()
    for i, chapter in enumerate(chapters):
        builder.button(text=chapter[:20], callback_data=f"topic_id:{i}")
    builder.adjust(1)
    await message.answer("📚 Выберите тему:", reply_markup=builder.as_markup())

@topics_router.callback_query(F.data.startswith("topic_id:"))
async def send_topic_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    index_str = callback.data.split(":", 1)[1]
    try:
        chapter = chapter_index_map[int(index_str)]
    except (IndexError, ValueError):
        await callback.message.answer("⚠️ Ошибка выбора темы.")
        await callback.answer()
        return

    topic_df = df[df["Глава ПДД"] == chapter]
    if topic_df.empty:
        await callback.message.answer("❗ В этой теме пока нет вопросов.")
        await callback.answer()
        return

    row = topic_df.sample().iloc[0]
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
        await callback.message.answer("⚠ Проблема с вопросом.")
        await callback.answer()
        return

    user_topic_sessions[user_id] = {
        "correct_index": correct_index,
        "correct_text": variants[correct_index - 1]
    }

    text = f"📘 Тема: {chapter}\n\n❓ {question_text}\n\n" + "\n".join([f"{i + 1}. {v}" for i, v in enumerate(variants)])
    builder = InlineKeyboardBuilder()
    for i in range(len(variants)):
        builder.button(text=str(i + 1), callback_data=f"topic_answer:{i + 1}")
    builder.adjust(2)

    image_url = row.get("Ссылка на изображение")
    if pd.notna(image_url) and isinstance(image_url, str) and image_url.startswith("http"):
        await callback.message.answer_photo(photo=image_url, caption=text, reply_markup=builder.as_markup())
    else:
        await callback.message.answer(text, reply_markup=builder.as_markup())
    await callback.answer()

@topics_router.callback_query(F.data.startswith("topic_answer:"))
async def check_topic_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    session = user_topic_sessions.get(user_id)
    if not session:
        await callback.answer("Сессия не найдена.")
        return

    answer_index = int(callback.data.split(":")[1])
    if answer_index == session["correct_index"]:
        await callback.message.answer("✅ Верно!")
    else:
        await callback.message.answer(f"❌ Неверно. Правильный ответ: {session['correct_text']}")
    await callback.answer()