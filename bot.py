#!venv/bin/python
import logging

from aiogram import executor
from aiogram.utils.executor import start_webhook
from handlers import dp
from admin_panel import dp
from load_all import bot
from database import create_db
from config import admin_id, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL


async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await create_db()
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


def main():
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


if __name__ == "__main__":
    from handlers import dp
    from admin_panel import dp

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
