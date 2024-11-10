import asyncio
import sys
from aiogram import Bot, Dispatcher
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

                if post[0]:
                    if not media_group.caption:
                        media_group.caption = post[0]
                if post[15] == "photo":
                    media_group.add_photo(media=post[1])
                elif post[15] == "video":
                    media_group.add_video(media=post[2])
                elif post[15] == "audio":
                    media_group.add_audio(media=post[3])
                elif post[15] == "document":
                    media_group.add_document(media=post[4])
            else:
                if post[15] == "text":
                    await bot.send_message(text=post[0], chat_id=recipient_chat_id)
                elif post[15] == "photo":
                    await bot.send_photo(photo=post[1], chat_id=recipient_chat_id)
                elif post[15] == "video":
                    await bot.send_video(video=post[2], chat_id=recipient_chat_id)
                elif post[15] == "audio":
                    await bot.send_audio(audio=post[3], chat_id=recipient_chat_id)
                elif post[15] == "document":
                    await bot.send_document(document=post[4], chat_id=recipient_chat_id)
                elif post[15] == "video_note":
                    await bot.send_video_note(video_note=post[5], chat_id=recipient_chat_id)
                elif post[15] == "voice":
                    await bot.send_voice(voice=post[6], chat_id=recipient_chat_id)
                elif post[15] == "sticker":
                    await bot.send_sticker(sticker=post[7], chat_id=recipient_chat_id)
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
        logger.debug("Закончили копировать.")

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
