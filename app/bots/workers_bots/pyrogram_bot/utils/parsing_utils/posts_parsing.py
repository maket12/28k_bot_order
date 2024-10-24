from bot.pyrogram_bot.utils.parsing_utils.links_including import parse_with_links
from bot.services.database.database_code import Database
from bot.services.logs.logging import logger

db = Database()


async def parsing_posts(channel_id: int, donor_posts):
    try:
        logger.debug("Начинаем сбор постов из канала-донора")

        async for donor_post in donor_posts:
            # Определение медиагруппы
            media_group_id = donor_post.media_group_id

            # Данные о посте для БД
            data_to_insert = [None, None, None, None, None, media_group_id]

            if donor_post.caption:
                result = await parse_with_links(entities=donor_post.caption_entities,
                                                text_or_caption=donor_post.caption)
                data_to_insert[0] = result
            if donor_post.text:
                result = await parse_with_links(entities=donor_post.entities,
                                                text_or_caption=donor_post.text)
                data_to_insert[0] = result
                data_to_insert[4] = 'text'
            elif donor_post.photo:
                data_to_insert[1] = donor_post.photo.file_id
                data_to_insert[4] = 'photo'
            elif donor_post.video:
                data_to_insert[2] = donor_post.video.file_id
                data_to_insert[4] = 'video'
            elif donor_post.document:
                data_to_insert[3] = donor_post.document.file_id
                data_to_insert[4] = 'document'
            else:
                continue

            db.add_post_to_channels_table(channel_id=channel_id, posts_data=data_to_insert)
        logger.info("Сбор постов из канала-донора закончился")
    except Exception as e:
        logger.error("Возникла ошибка в parsing_post: %s", e)
