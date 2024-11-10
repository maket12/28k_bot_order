import asyncio
import sys
import os
from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder
from app.services.database.database_code import ProjectsDatabase, AccountsDatabase, ChatDatabase
from app.services.database.database_code import AllChatsDatabase
from app.services.subprocess_station.subprocess_init import SubprocessStation
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()
accounts_db = AccountsDatabase()
all_chats_db = AllChatsDatabase()

subprocess_station = SubprocessStation()


def get_bot(token: str):
    try:
        bot = Bot(token=token)
        return bot
    except Exception as e:
        logger.error("Возникла ошибка при инициализации клиента: %s", e)
        return False


def get_full_media_path(file_id: str):
    try:
        curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        target_dir = os.path.join(curr_dir, f"media")

        logger.debug(f"File_id: {file_id}")

        # Ищем файл, начинающийся с file_id
        file_path = None
        for file_name in os.listdir(target_dir):
            logger.debug(f"Found file: {file_name}")
            # Проверяем, начинается ли имя файла с file_id
            if file_name.startswith(file_id):
                file_path = os.path.join(target_dir, file_name)
                break  # Останавливаемся при нахождении первого совпадения
        return file_path
    except Exception as e:
        logger.error("Возникла ошибка в get_full_media_path: %s", e)


async def main(token: str | None, company_name: str | None):
    try:
        logger.debug("Начинаем копирование")
        if not token:
            logger.critical("Токен бота не был передан!")
            return
        if not company_name:
            logger.critical("Имя компании не было передано!")
            return

        bot = get_bot(token=token)
        if not bot:
            return

        source_chat_id, source_chat_type, recipient_chat_id, recipient_chat_type = projects_db.get_chat_ids_by_company(
            company_name=company_name)

        chat_db = ChatDatabase(chat_type=source_chat_type, chat_id=source_chat_id)

        all_posts = chat_db.get_all_posts()

        media_group = MediaGroupBuilder()

        last_media_group_id = 0

        for post in all_posts:
            logger.info("Тут копируем...")
            if last_media_group_id:
                if post[16] != last_media_group_id:
                    await bot.send_media_group(media=media_group.build(), chat_id=recipient_chat_id)
                    media_group = MediaGroupBuilder()

                if post[1]:
                    if not media_group.caption:
                        media_group.caption = post[1]
                if post[15] == "photo":
                    media_group.add_photo(media=get_full_media_path(file_id=post[2]))
                elif post[15] == "video":
                    media_group.add_video(media=get_full_media_path(post[3]))
                elif post[15] == "audio":
                    media_group.add_audio(media=get_full_media_path(post[4]))
                elif post[15] == "document":
                    media_group.add_document(media=get_full_media_path(post[5]))
            else:
                if post[15] == "text":
                    await bot.send_message(text=post[1], chat_id=recipient_chat_id)
                elif post[15] == "photo":
                    await bot.send_photo(photo=get_full_media_path(post[2]),
                                         chat_id=recipient_chat_id)
                elif post[15] == "video":
                    await bot.send_video(video=get_full_media_path(post[3]),
                                         chat_id=recipient_chat_id)
                elif post[15] == "audio":
                    await bot.send_audio(audio=get_full_media_path(post[4]),
                                         chat_id=recipient_chat_id)
                elif post[15] == "document":
                    path = get_full_media_path(post[5])
                    if path:
                        await bot.send_document(document=path,
                                                chat_id=recipient_chat_id)
                elif post[15] == "video_note":
                    await bot.send_video_note(video_note=get_full_media_path(post[6]),
                                              chat_id=recipient_chat_id)
                elif post[15] == "voice":
                    await bot.send_voice(voice=get_full_media_path(post[7]),
                                         chat_id=recipient_chat_id)
                elif post[15] == "sticker":
                    await bot.send_sticker(sticker=get_full_media_path(post[8]),
                                           chat_id=recipient_chat_id)
                elif post[15] == "location":
                    continue
                    # await bot.send_location(latitude=, lon)
                elif post[15] == "contact":
                    continue
                    # await bot.send_contact(phone_number=, first_name=)
                else:
                    continue
                    # await bot.send_poll()

            last_media_group_id = post[16]
            await asyncio.sleep(5)
        logger.debug("Закончили копировать!")

    except Exception as e:
        logger.error("Возникла ошибка в copy_channel: %s", e)


if __name__ == "__main__":
    # Получаем аргументы из sys.argv
    bot_token = company_nm = None

    # Проходим по аргументам вручную
    args = sys.argv[1:]  # Пропускаем первый элемент, так как это имя скрипта
    for i in range(len(args)):
        if args[i] == "--bot_token" and i + 1 < len(args):
            bot_token = args[i + 1]
        elif args[i] == "--company_name" and i + 1 < len(args):
            company_nm = args[i + 1]

    # Передаем аргументы в основную функцию
    asyncio.run(main(token=bot_token, company_name=company_nm))
