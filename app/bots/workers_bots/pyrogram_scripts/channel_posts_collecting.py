import asyncio
import sys
import os
from pyrogram import Client, types
from app.bots.workers_bots.pyrogram_scripts.utils.parsing_posts_utils.entities_parsing import parse_entities
from app.bots.workers_bots.pyrogram_scripts.utils.parsing_posts_utils.markup_parsing import parse_markup
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


def get_download_path(file_id: str, content_type: str, document_ending=None):
    try:
        if content_type == "photo":
            ending = "png"
        elif content_type == "video" or content_type == "video_note" or content_type == "animation":
            ending = "mp4"
        elif content_type == "document":
            ending = document_ending
        elif content_type == "audio" or content_type == "voice":
            ending = "mp3"
        else:
            ending = "webp"

        curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        path = os.path.join(curr_dir, f"media/{file_id}.{ending}")
        return path
    except Exception as e:
        logger.error("Возникла ошибка в download_file: %s", e)


async def collect_post(message: types.Message) :
    post_data = [None, None, None, None, None, None, None, None, None, None,
                 None, None, None, None, None, None, None]
    try:

        logger.info(f"Сбор поста {message.id}")

        if message.text:
            post_data[0] = message.text
            post_data[14] = "text"
        else:
            if message.caption:
                post_data[0] = message.caption

            if message.photo:
                post_data[1] = message.photo.file_id
                post_data[14] = "photo"
                await message.download(file_name=get_download_path(
                    file_id=message.photo.file_id,
                    content_type=post_data[14]
                ))
            elif message.video:
                post_data[2] = message.video.file_id
                post_data[14] = "video"
                await message.download(file_name=get_download_path(
                    file_id=message.video.file_id,
                    content_type=post_data[14]
                ))
            elif message.audio:
                post_data[3] = message.audio.file_id
                post_data[14] = "audio"
                await message.download(file_name=get_download_path(
                    file_id=message.audio.file_id,
                    content_type=post_data[14]
                ))
            elif message.document:
                post_data[4] = message.document.file_id
                post_data[14] = "document"
                await message.download(file_name=get_download_path(
                    file_id=message.document.file_id,
                    content_type=post_data[14],
                    document_ending=message.document.mime_type
                ))
            elif message.video_note:
                post_data[5] = message.video_note.file_id
                post_data[14] = "video_note"
                await message.download(file_name=get_download_path(
                    file_id=message.video_note.file_id,
                    content_type=post_data[14]
                ))
            elif message.voice:
                post_data[6] = message.voice.file_id
                post_data[14] = "voice"
                await message.download(file_name=get_download_path(
                    file_id=message.voice.file_id,
                    content_type=post_data[14]
                ))
            elif message.sticker:
                post_data[7] = message.sticker.file_id
                post_data[14] = "sticker"
                await message.download(file_name=get_download_path(
                    file_id=message.sticker.file_id,
                    content_type=post_data[14]
                ))
            elif message.location:
                post_data[8] = f"latitude: {message.location.latitude}, longitude: {message.location.longitude}"
                post_data[14] = "location"
            elif message.contact:
                post_data[9] = f"phone: {message.contact.phone_number}, first_name: {message.contact.first_name}"
                post_data[14] = "contact"
            elif message.poll:
                answers = []
                for ans in message.poll.options:
                    answers.append(ans.text)

                post_data[10] = (f"question: {message.poll.question}, answers: {answers}, "
                                 f"anonymous: {message.poll.is_anonymous}, type: {message.poll.type}, "
                                 f"multiply_answers: {message.poll.allows_multiple_answers}, "
                                 f"correct_option_id: {message.poll.correct_option_id}, "
                                 f"explanation: {message.poll.explanation}, "
                                 f"open_period: {message.poll.open_period}")
                post_data[14] = "poll"
            elif message.animation:
                post_data[11] = message.animation.file_id
                post_data[14] = "animation"
                await message.download(file_name=get_download_path(
                    file_id=message.animation.file_id,
                    content_type=post_data[14]
                ))
            else:
                logger.warning("Unknowing message object: %s", message.link)
                return
        if message.reply_markup:
            if message.reply_markup.inline_keyboard:
                post_data[12] = parse_markup(message.reply_markup)

        if message.entities:
            post_data[13] = parse_entities(entities=message.entities)

        post_data[15] = message.media_group_id
        post_data[16] = message.id
    except Exception as e:
        logger.error("Возникла ошибка в collect_post: %s", e)
    finally:
        return post_data


async def parsing_process_links(session_path: str, source_chat_id: str, source_chat_type: str, links: str):
    try:
        app = get_client(session_path=session_path)
        if not app:
            return
        logger.debug(f"Процесс сбора постов с канала {source_chat_id} начался!")
        await app.start()

        async for chat in app.get_dialogs():
            logger.info(f"Чат агента: {chat.chat.username}, {chat.chat.id}")

        chat_db = ChatDatabase(chat_type=source_chat_type, chat_id=int(source_chat_id))
        chat_db.create_tables()

        messages_ids = []

        links_list = links.split('|')
        for link in links_list:
            messages_ids.append(int(link.split('/')[-1]))

        all_posts = await app.get_messages(chat_id=source_chat_id,
                                           message_ids=messages_ids)

        for message in all_posts:
            post_data = await collect_post(message=message)

            chat_db.add_post(post_data=post_data)

        all_chats_db.add_chat(chat_id=int(source_chat_id), chat_type=source_chat_type)
    except Exception as e:
        logger.error("Возникла ошибка в parsing_process_links: %s", e)


async def parsing_process_all(session_path: str, source_chat_id: str, source_chat_type: str):
    try:
        app = get_client(session_path=session_path)
        if not app:
            return

        logger.debug(f"Процесс сбора постов с канала {source_chat_id} начался!")
        await app.start()

        async for chat in app.get_dialogs():
            logger.info(f"Чат агента: {chat.chat.username}, {chat.chat.id}")

        # await app.join_chat(chat_id=source_chat_id)
        # chat = await app.get_chat(chat_id=source_chat_id)

        chat_db = ChatDatabase(chat_type=source_chat_type, chat_id=int(source_chat_id))
        chat_db.create_tables()

        messages_counter = 0
        async for message in app.get_chat_history(chat_id=source_chat_id):
            messages_counter += 1
            if (messages_counter % 100) == 0:
                await asyncio.sleep(20)

            post_data = await collect_post(message=message)

            if any(attribute for attribute in post_data):
                chat_db.add_post(post_data=post_data)

            await asyncio.sleep(5)

        all_chats_db.add_chat(chat_id=int(source_chat_id), chat_type=source_chat_type)

        logger.debug(f"Парсинг чата {source_chat_id} успешно завершён!")
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

        (source_chat_id, source_chat_type,
         recipient_chat_id, recipient_chat_type) = projects_db.get_chat_ids_by_company(
            company_name=company_name
        )

        get_history_collecting_way = projects_db.get_company_attribute(attribute="history",
                                                                       company_name=company_name)

        sender_username = projects_db.get_company_attribute(attribute="sender_account",
                                                            company_name=company_name)
        sender_token = accounts_db.get_attribute_by_username(attribute="bot_token",
                                                             username=sender_username)

        chat_existing = all_chats_db.check_chat_existing(chat_id=source_chat_id)

        if not chat_existing:
            if get_history_collecting_way == "all":
                await parsing_process_all(session_path=session_path, source_chat_id=source_chat_id,
                                          source_chat_type=source_chat_type)

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

