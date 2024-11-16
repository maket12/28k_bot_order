import asyncio
import sys
import os
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from app.bots.workers_bots.pyrogram_scripts.utils.parsing_posts_utils.entities_utils.entities_including import with_entities_including
from app.bots.workers_bots.pyrogram_scripts.utils.parsing_posts_utils.markup_utils.markup_including import re_parse_markup
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
        session = AiohttpSession()
        bot = Bot(token=token, session=session)
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
            # Проверяем, начинается ли имя файла с file_id
            if file_name.startswith(file_id):
                logger.debug(f"Found file: {file_name}")
                file_path = os.path.join(target_dir, file_name)
                break  # Останавливаемся при нахождении первого совпадения
        return file_path
    except Exception as e:
        logger.error("Возникла ошибка в get_full_media_path: %s", e)


async def main(token: str | None, company_name: str | None):
    try:
        logger.info(f"Компания {company_name} запущена.")

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
        media_group_length = 0

        logger.debug("Начинаем копирование")

        for post in reversed(all_posts):
            try:
                if last_media_group_id == 0:
                    last_media_group_id = post[17]

                if last_media_group_id:
                    if post[17] != last_media_group_id:
                        await bot.send_media_group(media=media_group.build(),
                                                   chat_id=recipient_chat_id)
                        media_group = MediaGroupBuilder()
                        media_group_length = 0

                    if post[1]:
                        if not media_group.caption:
                            media_group.caption = with_entities_including(post[1],
                                                                          entities=post[14])

                    if post[15] == "photo":
                        media_group.add_photo(media=FSInputFile(get_full_media_path(post[2])),
                                              parse_mode="html")
                        media_group_length += 1
                    elif post[15] == "video":
                        media_group.add_video(media=FSInputFile(get_full_media_path(post[3])),
                                              parse_mode="html")
                        media_group_length += 1
                    elif post[15] == "audio":
                        media_group.add_audio(media=FSInputFile(get_full_media_path(post[4])),
                                              parse_mode="html")
                        media_group_length += 1
                    elif post[15] == "document":
                        media_group.add_document(media=FSInputFile(get_full_media_path(post[5])),
                                                 parse_mode="html")
                        media_group_length += 1
                else:
                    if post[13]:
                        inline_keyboard = re_parse_markup(markup_string=post[13]).as_markup()
                    else:
                        inline_keyboard = None

                    if post[15] == "text":
                        await bot.send_message(text=with_entities_including(post[1],
                                                                            entities=post[14]),
                                               chat_id=recipient_chat_id,
                                               reply_markup=inline_keyboard,
                                               parse_mode="html")
                    elif post[15] == "photo":
                        await bot.send_photo(photo=FSInputFile(get_full_media_path(post[2])),
                                             caption=with_entities_including(post[1], entities=post[14]),
                                             chat_id=recipient_chat_id,
                                             reply_markup=inline_keyboard,
                                             parse_mode="html")
                    elif post[15] == "video":
                        await bot.send_video(video=FSInputFile(get_full_media_path(post[3])),
                                             caption=with_entities_including(post[1], entities=post[14]),
                                             chat_id=recipient_chat_id,
                                             reply_markup=inline_keyboard,
                                             parse_mode="html")
                    elif post[15] == "audio":
                        await bot.send_audio(audio=FSInputFile(get_full_media_path(post[4])),
                                             caption=with_entities_including(post[1], entities=post[14]),
                                             chat_id=recipient_chat_id,
                                             reply_markup=inline_keyboard,
                                             parse_mode="html")
                    elif post[15] == "document":
                        continue
                        # path = get_full_media_path(post[5])
                        # if path:
                        #     await bot.send_document(document=FSInputFile(path),
                        #                             caption=post[1],
                        #                             chat_id=recipient_chat_id,
                        #                             reply_markup=inline_keyboard,
                        #                             parse_mode="html")
                    elif post[15] == "video_note":
                        await bot.send_video_note(video_note=FSInputFile(get_full_media_path(post[6])),
                                                  chat_id=recipient_chat_id,
                                                  reply_markup=inline_keyboard)
                    elif post[15] == "voice":
                        await bot.send_voice(voice=FSInputFile(get_full_media_path(post[7])),
                                             caption=with_entities_including(post[1], entities=post[14]),
                                             chat_id=recipient_chat_id,
                                             reply_markup=inline_keyboard,
                                             parse_mode="html")
                    elif post[15] == "sticker":
                        await bot.send_sticker(sticker=FSInputFile(get_full_media_path(post[8])),
                                               chat_id=recipient_chat_id,
                                               reply_markup=inline_keyboard)
                    elif post[15] == "location":
                        location_data = post[9].split(', ')
                        latitude = location_data[0].split(': ')[1]
                        longitude = location_data[1].split(': ')[1]
                        await bot.send_location(latitude=latitude, longitude=longitude,
                                                chat_id=recipient_chat_id,
                                                reply_markup=inline_keyboard,)
                    elif post[15] == "contact":
                        contact_data = post[10].split(', ')
                        phone = contact_data[0].split(': ')[1]
                        first_name = contact_data[1].split(': ')[1]
                        await bot.send_contact(phone_number=phone, first_name=first_name,
                                               chat_id=recipient_chat_id,
                                               reply_markup=inline_keyboard,)
                    elif post[15] == "poll":
                        poll_data = post[11].split(', ')
                        question = poll_data[0].split(': ')[1]

                        answers_string = poll_data[1].split(': ')[1]
                        answers = answers_string[1:len(poll_data[1]) - 1].split(', ')

                        anonymous = poll_data[2].split(': ')[1]
                        if anonymous == "True":
                            anonymous = True
                        else:
                            anonymous = False

                        poll_type = poll_data[3].split(': ')[1]
                        if poll_type == "None":
                            poll_type = None

                        multiply_answers = poll_data[4].split(': ')[1]
                        if multiply_answers == "True":
                            multiply_answers = True
                        else:
                            multiply_answers = False

                        correct_option_id = poll_data[5].split(': ')[1]
                        if correct_option_id == "None":
                            correct_option_id = None
                        else:
                            correct_option_id = int(correct_option_id)

                        explanation = poll_data[6].split(': ')[1]
                        if explanation == "None":
                            explanation = None

                        open_period = poll_data[7].split(': ')[1]
                        if open_period == "None":
                            open_period = None
                        else:
                            open_period = int(open_period)

                        await bot.send_poll(question=question, options=answers, is_anonymous=anonymous,
                                            type=poll_type, allows_multiple_answers=multiply_answers,
                                            correct_option_id=correct_option_id,
                                            explanation=explanation,
                                            open_period=open_period,
                                            chat_id=recipient_chat_id,
                                            reply_markup=inline_keyboard)
                    elif post[15] == "animation":
                        await bot.send_animation(animation=FSInputFile(get_full_media_path(post[12])),
                                                 caption=with_entities_including(post[1], entities=post[14]),
                                                 chat_id=recipient_chat_id,
                                                 reply_markup=inline_keyboard,
                                                 parse_mode="html")

                last_media_group_id = post[17]
                await asyncio.sleep(5)
            except Exception as e:
                logger.error("Возникла ошибка в copy_channel: %s", e)
                continue
        if media_group_length:
            await bot.send_media_group(media=media_group.build(),
                                       chat_id=recipient_chat_id)

        await bot.session.close()
        logger.debug("Копирование канала успешно завершено!")
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
