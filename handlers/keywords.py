from aiogram import Router, F
from aiogram.types import Message
import pandas as pd

router = Router()

try:
    df = pd.read_excel("keywords.xlsx").fillna("")
except Exception as e:
    print(f"[keywords] Ошибка загрузки keywords.xlsx: {e}")
    df = pd.DataFrame()

def build_response(row):
    parts = []

    if row.get("Определение"):
        parts.append(f"🧾 *Определение:*\n{row['Определение']}")
    if row.get("Примеры"):
        parts.append(f"🔄 *Примеры:*\n{row['Примеры']}")
    if row.get("Правила ПДД"):
        parts.append(f"📘 *Правила ПДД:*\n{row['Правила ПДД']}")
    if row.get("Можно"):
        parts.append(f"{row['Можно']}")
    if row.get("Нельзя"):
        parts.append(f"{row['Нельзя']}")
    if row.get("Ответственность"):
        parts.append(f"⚖️ *Ответственность:*\n{row['Ответственность']}")
    if row.get("Авторский комментарий"):
        parts.append(f"💬 *Комментарий:*\n{row['Авторский комментарий']}")
    if row.get("Ссылка на материалы"):
        parts.append(f"📎 [Материалы]({row['Ссылка на материалы']})")

    return "\n\n".join(parts)

@router.message(F.text)
async def keyword_lookup(message: Message):
    text = message.text.lower()

    matched = []

    for _, row in df.iterrows():
        keys = [k.strip().lower() for k in row.get("Ключевые слова", "").split(",") if k.strip()]
        if any(k in text for k in keys):
            matched.append(row)
        else:
            topics = [t.strip().lower() for t in row.get("Тематика", "").split(",") if t.strip()]
            if any(t in text for t in topics):
                matched.append(row)

    if not matched:
        return

    for row in matched[:3]:
        response = build_response(row)
        image = row.get("Изображение (ссылка)", "").strip()
        if image.startswith("http"):
            try:
                await message.answer_photo(photo=image, caption=response)
            except:
                await message.answer(response)
        else:
            await message.answer(response)