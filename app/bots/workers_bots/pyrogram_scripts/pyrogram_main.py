from aiogram import Dispatcher
from app.bots.workers_bots.pyrogram_scripts.bot_init.bot_instance import init_apps
from app.bots.workers_bots.pyrogram_scripts.bot_init.register_handlers import register_handlers
from app.services.database.database_code import AccountsDatabase


dp = Dispatcher()

db = AccountsDatabase()


if __name__ == "__main__":
    apps = init_apps()

    for app in apps:
        try:
            if app:
                # Регистрируем фильтры в user ботах (Pyrogram)
                app = register_handlers(app)

                app.run()

        except Exception as e:
            print(e)


