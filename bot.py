import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ВСТАВЬ СВОЙ ТОКЕН СЮДА
TOKEN = "8796643561:AAGBtBS9k7woEACDgShpvnnH7d52uu0xRGc"

# Включаем логирование (чтобы видеть ошибки)
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь для хранения задач пользователей (в памяти)
# В реальном проекте используй базу данных
user_tasks = {}

# ---------- КОМАНДА /start ----------
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! 👋\n\n"
        "Я бот-помощник. Вот что я умею:\n\n"
        "📝 /todo - список дел\n"
        "➕ /add [задача] - добавить задачу\n"
        "✅ /done [номер] - отметить задачу выполненной\n"
        "🗑 /clear - очистить все задачи\n"
        "❓ /help - показать все команды\n\n"
        "Просто напиши /add Купить молоко и я сохраню!"
    )

# ---------- КОМАНДА /help ----------
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📋 **Мои команды:**\n\n"
        "/start - приветствие\n"
        "/todo - показать список дел\n"
        "/add [текст] - добавить задачу\n"
        "/done [номер] - отметить задачу выполненной\n"
        "/clear - удалить все задачи\n"
        "/help - это сообщение\n\n"
        "📌 **Примеры:**\n"
        "/add Позвонить маме\n"
        "/done 1\n\n"
        "🤖 **Совет:** Нажми на команду в списке, чтобы не печатать вручную!",
        parse_mode="Markdown"
    )

# ---------- ПОКАЗАТЬ ВСЕ ЗАДАЧИ ----------
@dp.message(Command("todo"))
async def show_tasks(message: types.Message):
    user_id = message.from_user.id
    tasks = user_tasks.get(user_id, [])
    
    if not tasks:
        await message.answer("🎉 У тебя нет задач! Отдыхай или добавь новую через /add")
        return
    
    # Формируем красивый список
    task_list = "📝 **Твой список дел:**\n\n"
    for i, task in enumerate(tasks, 1):
        task_list += f"{i}. {task}\n"
    task_list += f"\n✅ Выполненные задачи удаляй через /done {i}"
    
    await message.answer(task_list, parse_mode="Markdown")

# ---------- ДОБАВИТЬ ЗАДАЧУ ----------
@dp.message(Command("add"))
async def add_task(message: types.Message):
    user_id = message.from_user.id
    
    # Получаем текст задачи (всё, что после /add)
    task_text = message.text.replace("/add", "").strip()
    
    if not task_text:
        await message.answer("❌ Ты не написал задачу!\nПример: `/add Купить хлеб`", parse_mode="Markdown")
        return
    
    # Добавляем задачу в список пользователя
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    user_tasks[user_id].append(task_text)
    
    task_number = len(user_tasks[user_id])
    await message.answer(f"✅ Задача добавлена!\n\n{task_number}. {task_text}\n\nОтметь её как готовую: /done {task_number}")

# ---------- ОТМЕТИТЬ ЗАДАЧУ ВЫПОЛНЕННОЙ ----------
@dp.message(Command("done"))
async def done_task(message: types.Message):
    user_id = message.from_user.id
    
    # Получаем номер задачи
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Укажи номер задачи!\nПример: `/done 2`", parse_mode="Markdown")
        return
    
    try:
        task_num = int(parts[1]) - 1  # Превращаем в индекс (пользователи видят с 1, Python считает с 0)
    except ValueError:
        await message.answer("❌ Номер должен быть числом!\nПример: `/done 2`")
        return
    
    tasks = user_tasks.get(user_id, [])
    if task_num < 0 or task_num >= len(tasks):
        await message.answer(f"❌ Задачи с номером {parts[1]} не существует!\nПосмотри список: /todo")
        return
    
    # Удаляем выполненную задачу
    completed_task = tasks.pop(task_num)
    await message.answer(f"✅ Молодец! Задача выполнена:\n«{completed_task}»\n\nОсталось задач: {len(tasks)}")
    
    # Если задач больше нет, удаляем запись пользователя
    if not tasks and user_id in user_tasks:
        del user_tasks[user_id]

# ---------- ОЧИСТИТЬ ВСЕ ЗАДАЧИ ----------
@dp.message(Command("clear"))
async def clear_tasks(message: types.Message):
    user_id = message.from_user.id
    task_count = len(user_tasks.get(user_id, []))
    
    if user_id in user_tasks:
        del user_tasks[user_id]
        await message.answer(f"🗑 Удалено {task_count} задач. Твой список дел пуст!")
    else:
        await message.answer("📭 У тебя и так нет задач!")

# ---------- ЗАПУСК БОТА ----------
async def main():
    print("🤖 Бот запущен! Нажми Ctrl+C для остановки")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())