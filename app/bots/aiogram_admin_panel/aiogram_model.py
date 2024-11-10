import asyncio
from aiogram import Dispatcher, Bot
from app.services.database.database_code import AccountsDatabase, ProjectsDatabase
from app.bots.aiogram_admin_panel.main_router.include_routers import include_all_routers

accounts_db = AccountsDatabase()

projects_db = ProjectsDatabase()

dp = Dispatcher()


def aiogram_bot_start(bot_token: str):
    accounts_db.create_tables()
    projects_db.create_tables()
    projects_db.annulling_all_company_statuses()
    include_all_routers(dp=dp)
    asyncio.run(dp.start_polling(Bot(bot_token)))

