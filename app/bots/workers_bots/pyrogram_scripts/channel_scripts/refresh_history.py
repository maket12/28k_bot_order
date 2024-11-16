import asyncio
import sys
from datetime import datetime
from pyrogram import Client
from app.bots.workers_bots.pyrogram_scripts.utils.collect_post import post_parsing
from app.services.database.database_code import ProjectsDatabase, AccountsDatabase, ChatDatabase
from app.services.database.database_code import AllChatsDatabase
from app.services.subprocess_station.subprocess_init import SubprocessStation
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()
accounts_db = AccountsDatabase()
all_chats_db = AllChatsDatabase()
all_chats_db.create_table()

subprocess_station = SubprocessStation()


def get_client(session_path: str):
    try:
        app = Client(session_path.split('.')[0])  # because pyrogram automatically add .session in the end
        return app
    except Exception as e:
        logger.error("Возникла ошибка при инициализации клиента: %s", e)
        return False


async def refreshing_process(session_path: str, source_chat_id: str, source_chat_type: str, events: list):
    try:
        pass
    except Exception as e:
        logger.error("Возникла ошибка в refreshing_process: %s", e)


async def main(session_path: str, company_name: str):
    try:
        if not session_path:
            logger.critical("Путь к сессии не был передан!")
            return
        if not company_name:
            logger.critical("Имя компании не было передано!")
            return

        logger.info(f"Компания {company_name} запущена.")

        (source_chat_id, source_chat_type,
         recipient_chat_id, recipient_chat_type) = projects_db.get_chat_ids_by_company(
            company_name=company_name
        )

        sender_username = projects_db.get_company_attribute(attribute="sender_account",
                                                            company_name=company_name)
        sender_token = accounts_db.get_attribute_by_username(attribute="bot_token",
                                                             username=sender_username)
    except Exception as e:
        logger.error("Возникла ошибка в main: %s", e)


if __name__ == "__main__":
    # Получаем аргументы из sys.argv
    ses_path = company_nm = None

    # Проходим по аргументам вручную
    args = sys.argv[1:]  # Пропускаем первый элемент, так как это имя скрипта
    for i in range(len(args)):
        if args[i] == "--session_path" and i + 1 < len(args):
            ses_path = args[i + 1]
        elif args[i] == "--company_name" and i + 1 < len(args):
            company_nm = args[i + 1]

    # Передаем аргументы в основную функцию
    asyncio.run(main(session_path=ses_path, company_name=company_nm))
