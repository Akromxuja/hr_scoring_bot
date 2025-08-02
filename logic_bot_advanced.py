
import json
import csv
import os
TOKEN = os.getenv('7838540871:AAFTB87rxsV-BnoMW04YajEEnrttdCZdVLQ')
from datetime import datetime, time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    JobQueue,
)
import random

# 🔐 Вставь сюда свой токен
TOKEN = '7838540871:AAFTB87rxsV-BnoMW04YajEEnrttdCZdVLQ'

# Загрузка задач
with open("tasks.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

# Ответы пользователей
DATA_FILE = "data.csv"

# Состояние: последние задачи по пользователю
user_last_task = {}

# Клавиатура
keyboard = [['🧠 Получить задачу'], ['📊 Мой рейтинг']]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def load_answers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_answer(row):
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Добро пожаловать в HR Scoring Bot!"

Выберите действие:",
        reply_markup=markup,
    )

def get_task(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    name = update.message.from_user.full_name
    task = random.choice(tasks)
    user_last_task[user_id] = {"task": task, "answered": False}
    update.message.reply_text(
        f"🧠 Задача:
{task['text_ru']}

🧠 Savol:
{task['text_uz']}"
    )

def handle_answer(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    name = update.message.from_user.full_name
    user_input = update.message.text.strip()

    if user_id not in user_last_task or user_last_task[user_id]["answered"]:
        update.message.reply_text("❗ Сначала получите задачу командой.")
        return

    task = user_last_task[user_id]["task"]
    keywords = task["answer_keywords"]
    is_correct = all(k.lower() in user_input.lower() for k in keywords)

    row = {
        "user_id": user_id,
        "name": name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": task["text_ru"],
        "answer": user_input,
        "result": "Правильно" if is_correct else "Неправильно",
        "score": 1 if is_correct else 0,
    }
    save_answer(row)
    user_last_task[user_id]["answered"] = True

    update.message.reply_text("✅ Ответ принят!" if is_correct else "❌ Неправильно. Ответ записан.")

def show_score(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    answers = load_answers()
    score = sum(int(r["score"]) for r in answers if int(r["user_id"]) == user_id)
    update.message.reply_text(f"📊 Ваш счёт: {score} баллов.")

def export(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not user or not str(user.id).startswith("78"):  # Ограничь доступ по ID (замени на свой ID)
        update.message.reply_text("⛔ Только для HR.")
        return

    if not os.path.exists(DATA_FILE):
        update.message.reply_text("Файл данных пока пуст.")
    else:
        with open(DATA_FILE, "rb") as f:
            update.message.reply_document(f)

def send_daily_task(context: CallbackContext):
    for chat_id in user_last_task.keys():
        task = random.choice(tasks)
        user_last_task[chat_id] = {"task": task, "answered": False}
        context.bot.send_message(
            chat_id=chat_id,
            text=f"📅 Сегодняшняя задача:
{task['text_ru']}

🧠 Savol:
{task['text_uz']}"
        )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("score", show_score))
    dp.add_handler(CommandHandler("export", export))
    dp.add_handler(MessageHandler(Filters.regex("🧠 Получить задачу"), get_task))
    dp.add_handler(MessageHandler(Filters.regex("📊 Мой рейтинг"), show_score))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_answer))

    # Рассылка задачи в 10:00
    job_queue: JobQueue = updater.job_queue
    job_queue.run_daily(send_daily_task, time(hour=10, minute=0))

    updater.start_polling()
    print("HR Scoring Bot запущен.")
    updater.idle()

if __name__ == "__main__":
    main()
