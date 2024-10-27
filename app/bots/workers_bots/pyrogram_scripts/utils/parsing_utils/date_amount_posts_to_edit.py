from datetime import datetime
from bot.services.logs.logging import logger


async def get_parameters_for_edit(posts_to_edit, after_date: datetime):
    try:
        logger.debug("Начинаем подсчёт постов для замены")

        edit_correct_posts = []

        async for edit_post in posts_to_edit:
            if edit_post.date >= after_date:
                edit_correct_posts.append(edit_post)

        logger.debug("Конец подсчёта")
        return edit_correct_posts
    except Exception as e:
        logger.error("Возникла ошибка в get_parameters_for_edit: %s", e)

