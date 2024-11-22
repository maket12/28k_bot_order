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


async def parsing_process(session_path: str, source_chat_id: str, source_chat_type: str, period: str):
    try:
        if '-' not in period:
            logger.error("Неккоректный формат периода!")
            return

        app = get_client(session_path=session_path)
        if not app:
            return

        logger.debug(f"Процесс сбора постов с канала {source_chat_id} начался!")
        await app.start()

        app.get_dialogs()  # refresh session data

        await app.join_chat(chat_id=source_chat_id)

        chat_db = ChatDatabase(chat_type=source_chat_type, chat_id=int(source_chat_id))
        chat_db.create_tables(chat_type=source_chat_type)

        starting_date, ending_date = period.split('-')
        starting_date_dt = datetime.strptime(starting_date, "%d%m%y")
        ending_date_dt = datetime.strptime(ending_date, "%d%m%y")

        messages_ids = []
        async for message in app.get_chat_history(chat_id=source_chat_id, offset_date=ending_date_dt):
            if not (message.date >= starting_date_dt):
                break

            post_existing = bool(chat_db.get_posts_by_ids(messages_ids=[message.id]))
            if not post_existing:
                post_data = await post_parsing(message=message)
                chat_db.add_post(post_data=post_data)

            messages_ids.append(str(message.id))

        all_chats_db.add_chat(chat_id=int(source_chat_id), chat_type=source_chat_type)

        return messages_ids
    except Exception as e:
        logger.error("Возникла ошибка в parsing_process: %s", e)


async def main(session_path: str | None, company_name: str | None):
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

        period = projects_db.get_company_attribute(attribute="history",
                                                   company_name=company_name)

        sender_username = projects_db.get_company_attribute(attribute="sender_account",
                                                            company_name=company_name)
        sender_token = accounts_db.get_attribute_by_username(attribute="bot_token",
                                                             username=sender_username)

        messages_ids = await parsing_process(session_path=session_path,
                                             source_chat_id=source_chat_id,
                                             source_chat_type=source_chat_type,
                                             period=period)
        add_data = ",".join(messages_ids)

        subprocess_station.set_script_path(script_type="aiogram",
                                           script_name="channel_scripts/copy_period.py")
        subprocess_station.set_input_data(data=sender_token)
        subprocess_station.set_company_name(company=company_name)
        subprocess_station.set_additional_data(data=add_data)
        subprocess_station.run_script(script_name="copy_period.py")
    except Exception as e:
        logger.error("Возникла ошибка в channel_posts_collecting: %s", e)


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