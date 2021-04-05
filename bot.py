#!venv/bin/python
from aiogram import executor
from load_all import bot
from database import create_db
from config import admin_id


async def on_startup(dp):
    await create_db()
    await bot.send_message(admin_id, "Я запущен!")


if __name__ == "__main__":
    from handlers import dp
    from admin_panel import dp

    # Запуск бота
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

