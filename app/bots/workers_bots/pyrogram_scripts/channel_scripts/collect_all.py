import asyncio
import sys
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


async def parsing_process(session_path: str, source_chat_id: str, source_chat_type: str):
    try:
        app = get_client(session_path=session_path)
        if not app:
            return

        logger.debug(f"Процесс сбора постов с канала {source_chat_id} начался!")
        await app.start()

        app.get_dialogs()  # refresh session data

        await app.join_chat(chat_id=source_chat_id)

        chat_db = ChatDatabase(chat_type=source_chat_type, chat_id=int(source_chat_id))
        chat_db.create_tables(chat_type=source_chat_type)

        messages_counter = 0
        async for message in app.get_chat_history(chat_id=source_chat_id):
            messages_counter += 1
            if (messages_counter % 100) == 0:
                await asyncio.sleep(20)

            post_data = await post_parsing(message=message)

            if any(attribute for attribute in post_data):
                chat_db.add_post(post_data=post_data)

            await asyncio.sleep(5)

        all_chats_db.add_chat(chat_id=int(source_chat_id), chat_type=source_chat_type)

        logger.debug(f"Парсинг канала {source_chat_id} успешно завершён!")
        await app.stop()
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

        sender_username = projects_db.get_company_attribute(attribute="sender_account",
                                                            company_name=company_name)
        sender_token = accounts_db.get_attribute_by_username(attribute="bot_token",
                                                             username=sender_username)

        chat_existing = all_chats_db.check_chat_existing(chat_id=source_chat_id)

        if not chat_existing:
            await parsing_process(session_path=session_path,
                                  source_chat_id=source_chat_id,
                                  source_chat_type=source_chat_type)

        subprocess_station.set_script_path(script_type="aiogram",
                                           script_name="channel_scripts/copy_all.py")
        subprocess_station.set_input_data(data=sender_token)
        subprocess_station.set_company_name(company=company_name)
        subprocess_station.run_script(script_name="copy_all.py")
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