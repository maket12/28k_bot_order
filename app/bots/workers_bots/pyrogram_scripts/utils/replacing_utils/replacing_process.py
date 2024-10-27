import asyncio
from pyrogram import Client, types
from pyrogram.errors import MessageNotModified
from pyrogram.types.input_media import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from bot.pyrogram_bot.utils.replacing_utils.random_post import get_random_single_post, get_random_media_group
from bot.services.database.database_code import Database
from bot.services.logs.logging import logger

db = Database()


async def get_post_type(post: types.Message):
    try:
        if post.text:
            post_type = 'text'
        elif post.photo or post.video:
            post_type = 'media'
        else:
            post_type = 'document'
        return post_type
    except Exception as e:
        logger.error("Возникла ошибка в get_post_type: %s", e)


async def replacing_media_groups_process(client: Client, last_media_group_to_edit_id: int,
                                         current_post_to_edit: types.Message | None,
                                         messages_to_edit: list, donor_media_groups: list):
    try:
        logger.warning(current_post_to_edit.id if current_post_to_edit else None)

        # Если ещё не было ни одной медиагруппы
        if not last_media_group_to_edit_id:
            last_media_group_to_edit_id = current_post_to_edit.media_group_id

        # Если началась новая медиагруппа
        if not current_post_to_edit or current_post_to_edit.media_group_id != last_media_group_to_edit_id:
            random_media_group, donor_media_groups = await get_random_media_group(media_groups=donor_media_groups)
            random_media_group_edited = list(reversed(random_media_group))  # Чтобы начать с первого поста группы

            for message_to_edit in list(reversed(messages_to_edit)):
                # Если у медиагруппы-донора закончились посты
                if not len(random_media_group_edited):
                    await client.delete_messages(chat_id=message_to_edit.chat.id,
                                                 message_ids=message_to_edit.id)
                    await asyncio.sleep(7)
                    continue

                if random_media_group_edited[0][2]:
                    media_to_replace = InputMediaPhoto(media=random_media_group_edited[0][2],
                                                       caption=random_media_group_edited[0][1])
                else:
                    media_to_replace = InputMediaVideo(media=random_media_group_edited[0][3],
                                                       caption=random_media_group_edited[0][1])

                try:
                    await client.edit_message_media(chat_id=message_to_edit.chat.id,
                                                    message_id=message_to_edit.id,
                                                    media=media_to_replace)
                except MessageNotModified:
                    logger.warning("Найдено такое же сообщение, замена невозможна")

                # Удаляем, чтобы не было повторений
                random_media_group_edited.pop(0)

                await asyncio.sleep(2)  # 7

            # # Удаляем из постов-доноров использованную медиагруппу
            # donor_media_groups.remove(random_media_group)
            # Очищаем список медиагруппы для редактирования
            messages_to_edit = [current_post_to_edit]
            # Обновляем инфо о последней медиагруппе
            if current_post_to_edit:
                last_media_group_to_edit_id = current_post_to_edit.media_group_id
            else:
                last_media_group_to_edit_id = None
        else:
            # Добавляем в текущую медиагруппу для редактирования её составляющую
            messages_to_edit.append(current_post_to_edit)

        return last_media_group_to_edit_id, messages_to_edit, donor_media_groups
    except Exception as e:
        logger.error("Возникла ошибка в replacing_media_groups_process: %s", e)
        return


async def replacing_single_process(client: Client, post_to_replace: types.Message,
                                   donor_post: tuple, post_type: str):
    try:
        channel_chat_id = post_to_replace.chat.id
        if post_type == 'text':
            try:
                await client.edit_message_text(chat_id=channel_chat_id,
                                               message_id=post_to_replace.id,
                                               text=donor_post[1])
            except MessageNotModified:
                logger.warning("Найдено такое же сообщение, замена невозможна")
        elif post_type == 'media':
            if donor_post[2]:
                media_to_insert = InputMediaPhoto(media=donor_post[2],
                                                  caption=donor_post[1])
            else:
                media_to_insert = InputMediaVideo(media=donor_post[3],
                                                  caption=donor_post[1])

            try:
                await client.edit_message_media(chat_id=channel_chat_id,
                                                message_id=post_to_replace.id,
                                                media=media_to_insert)
            except MessageNotModified:
                logger.warning("Найдено такое же сообщение, замена невозможна")
        else:
            document_to_insert = InputMediaDocument(media=donor_post[4],
                                                    caption=donor_post[1])
            try:
                await client.edit_message_media(chat_id=channel_chat_id,
                                                message_id=post_to_replace.id,
                                                media=document_to_insert)
            except MessageNotModified:
                logger.warning("Найдено такое же сообщение, замена невозможна")
    except Exception as e:
        logger.error("Возникла ошибка в replacing_process: %s", e)


async def replace_posts(client: Client, posts_to_replace: list, channel_id: int):
    try:
        logger.debug("Начинаем замену постов")
        media_groups = db.get_all_media_groups(channel_id=channel_id)
        single_posts = db.get_all_single_posts(channel_id=channel_id)

        last_media_group_id = 0
        messages_to_edit = []
        for post_to_replace in posts_to_replace:
            if post_to_replace.media_group_id:
                result = await replacing_media_groups_process(client=client,
                                                     last_media_group_to_edit_id=last_media_group_id,
                                                     current_post_to_edit=post_to_replace,
                                                     messages_to_edit=messages_to_edit,
                                                     donor_media_groups=media_groups)
                last_media_group_id = result[0]
                messages_to_edit = result[1]
                media_groups = result[2]
            else:
                # Получаем тип одиночного поста
                single_post_type = await get_post_type(post=post_to_replace)

                # Получаем рандомный пост-донор и удаляем его из списка одиночных постов-доноров
                single_data = await get_random_single_post(single_posts=single_posts,
                                                           condition=single_post_type)
                if single_data:
                    random_post, single_posts = single_data[0], single_data[1]
                    # Редактируем пост
                    await replacing_single_process(client=client, post_to_replace=post_to_replace,
                                                   donor_post=random_post, post_type=single_post_type)

            await asyncio.sleep(2)  # 10 # Пауза перед следующим запросом

            # Завершение обработки последней медиагруппы, если она осталась незавершенной
        if messages_to_edit:
            logger.info("Завершение обработки последней медиагруппы после завершения цикла")
            await replacing_media_groups_process(client=client,
                                                 last_media_group_to_edit_id=last_media_group_id,
                                                 current_post_to_edit=None,
                                                 messages_to_edit=messages_to_edit,
                                                 donor_media_groups=media_groups)
        logger.debug("Закончили замену постов")
    except Exception as e:
        logger.error("Возникла ошибка в replace_posts: %s", e)
