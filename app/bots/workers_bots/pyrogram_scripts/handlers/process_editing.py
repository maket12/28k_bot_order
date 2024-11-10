from datetime import datetime
import asyncio
from pyrogram import Client, types
# from bot.pyrogram_scripts.utils.parsing_posts_utils.posts_parsing import parsing_posts
# from bot.pyrogram_scripts.utils.replacing_utils.replacing_process import replace_posts
# from bot.pyrogram_scripts.utils.parsing_posts_utils.date_amount_posts_to_edit import get_parameters_for_edit
from app.services.database.database_code import AccountsDatabase
from app.services.logs.logging import logger

db = AccountsDatabase()


async def process_editing_channel(client: Client, message: types.Message):
    try:
        from_channel_id = -1001070404049
        to_channel_id = -1002441266158
        if message.chat.id != from_channel_id:
            return
        # chat = await client.get_chat(chat_id=to_channel_id)

        # channel_history = client.get_chat_history(chat_id=from_channel_id, limit=2)

        # async for message in channel_history:
        try:
            await client.copy_message(from_chat_id=from_channel_id, chat_id=to_channel_id,
                                      message_id=message.id)
            await asyncio.sleep(3)
        except Exception as e:
            print(e)


        # parameters = message.text[message.text.find("=")+1:].split("║")
        # after_date = datetime.strptime(parameters[2], "%d.%m.%Y %H:%M")
        #
        # # Получаем инфо о постах, которые нужно отредактировать
        # posts_to_edit = client.get_chat_history(chat_id=parameters[0])
        # edit_parameters = await get_parameters_for_edit(posts_to_edit=posts_to_edit,
        #                                                 after_date=after_date)
        # edit_correct_posts = edit_parameters
        #
        # await asyncio.sleep(1)  # 10  # Пауза перед следующим запросом
        #
        # # Получаем донорские посты и заносим их в БД
        # posts_existing = db.get_posts_existing(channel_id=parameters[1])
        # if not posts_existing:
        #     donor_posts = client.get_chat_history(chat_id=parameters[1])
        #     await parsing_posts(channel_id=parameters[1], donor_posts=donor_posts)
        #
        # await asyncio.sleep(1)  # 10  # Пауза перед следующим запросом
        #
        # # Заменяем посты на донорские
        # await replace_posts(client=client, posts_to_replace=edit_correct_posts,
        #                     channel_id=parameters[1])

    except Exception as e:
        logger.error("Возникла ошибка в process_editing_channel: %s", e)
