def set_hook():
    import asyncio
    from config import HEROKU_APP_NAME, WEBHOOK_URL, TOKEN
    from aiogram import Bot
    bot = Bot(token=TOKEN)

    async def hook_set():
        if not HEROKU_APP_NAME:
            print('You have forgot to set HEROKU_APP_NAME')
            quit()
        await bot.set_webhook(WEBHOOK_URL)
        print(await bot.get_webhook_info())

    asyncio.run(hook_set())
    bot.close()


if __name__ == "__main__":
    from bot import main
    main()