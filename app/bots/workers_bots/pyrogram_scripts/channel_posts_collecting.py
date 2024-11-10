import asyncio
import sys
from pyrogram import Client
from app.bots.workers_bots.pyrogram_scripts.utils.parsing_posts_utils.entities_parsing import parse_entities
from app.services.database.database_code import ProjectsDatabase, AccountsDatabase, ChatDatabase
from app.services.database.database_code import AllChatsDatabase
from app.services.subprocess_station.subprocess_init import SubprocessStation
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()
accounts_db = AccountsDatabase()
all_chats_db = AllChatsDatabase()

subprocess_station = SubprocessStation()


def get_client(session_path: str):
    try:
        app = Client(session_path.split('.')[0])  # because pyrogram automatically add .session in the end
        return app
    except Exception as e:
        logger.error("Возникла ошибка при инициализации клиента: %s", e)
        return False


async def main(session_path: str | None, company_name: str | None):
    try:
        if not session_path:
            logger.critical("Путь к сессии не был передан!")
            return
        if not company_name:
            logger.critical("Имя компании не было передано!")
            return

        app = get_client(session_path=session_path)
        if not app:
            return

        logger.debug("Начинаем сбор.")
        logger.debug("session: %s", session_path)
        await app.start()

        logger.info(f"Company: {company_name}")

        sender_username = projects_db.get_company_attribute(attribute="sender_account",
                                                            company_name=company_name)
        sender_token = accounts_db.get_attribute_by_username(attribute="bot_token",
                                                             username=sender_username)

        logger.info(f"Username: {sender_username}")

        source_chat_id, source_chat_type, recipient_chat_id, recipient_chat_type = projects_db.get_chat_ids_by_company(company_name=company_name)

        await app.join_chat(chat_id=source_chat_id)
        chat = await app.get_chat(chat_id=source_chat_id)

        logger.info(chat.type)

        chat_db = ChatDatabase(chat_type=source_chat_type, chat_id=source_chat_id)

        post_data = [None, None, None, None, None, None, None, None, None, None,
                     None, None, None, None, None, None, None]
        messages_counter = 0
        async for message in app.get_chat_history(chat_id=source_chat_id):
            logger.info("Тут сбор...")
            messages_counter += 1
            if (messages_counter % 100) == 0:
                await asyncio.sleep(8)

            if message.text:
                post_data[0] = message.text
                post_data[14] = "text"
            else:
                if message.caption:
                    post_data[0] = message.caption

                if message.photo:
                    post_data[1] = message.photo.file_id
                    post_data[14] = "photo"
                elif message.video:
                    post_data[2] = message.video.file_id
                    post_data[14] = "video"
                elif message.audio:
                    post_data[3] = message.audio.file_id
                    post_data[14] = "audio"
                elif message.document:
                    post_data[4] = message.document.file_id
                    post_data[14] = "document"
                elif message.video_note:
                    post_data[5] = message.video_note.file_id
                    post_data[14] = "video_note"
                elif message.voice:
                    post_data[6] = message.voice.file_id
                    post_data[14] = "voice"
                elif message.sticker:
                    post_data[7] = message.sticker.file_id
                    post_data[14] = "sticker"
                elif message.location:
                    post_data[8] = f"latitude: {message.location.latitude}, longitude: {message.location.longitude}"
                    post_data[14] = "location"
                elif message.contact:
                    post_data[9] = f"phone: {message.contact.phone_number}, first_name: {message.contact.first_name}"
                    post_data[14] = "contact"
                elif message.poll:
                    post_data[10] = str(message.poll)
                    post_data[14] = "poll"
                elif message.animation:
                    post_data[11] = message.animation.file_id
                    post_data[14] = "animation"
                else:
                    logger.warning("Unknowing message object: %s", message.t)
                    continue
            if message.reply_markup:
                if message.reply_markup.keyboard:
                    post_data[12] = str(message.reply_markup.keyboard)
                elif message.reply_markup.inline_keyboard:
                    post_data[12] = str(message.reply_markup.inline_keyboard)

            if message.entities:
                post_data[13] = parse_entities(entities=message.entities)

            post_data[15] = message.media_group_id
            post_data[16] = message.id
            # message.

            chat_db.add_post(post_data=post_data)

        all_chats_db.add_chat(chat_id=source_chat_id, chat_type=source_chat_type)

        logger.debug("Закончили сбор")
        await app.stop()

        subprocess_station.set_script_path(script_type="aiogram", script_name="copy_channel.py")
        subprocess_station.set_input_data(data=sender_token)
        subprocess_station.set_company_name(company=company_name)
        subprocess_station.run_script(script_name="copy_channel.py")
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
