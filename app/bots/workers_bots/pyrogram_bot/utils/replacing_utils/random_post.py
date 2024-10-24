import random
from bot.services.logs.logging import logger


async def get_random_media_group(media_groups: list):
    try:
        picked_media_group = random.choice(media_groups)
        media_groups.remove(picked_media_group)

        return picked_media_group, media_groups
    except Exception as e:
        logger.error("Возникла ошибка в get_random_media_group: %s", e)


async def get_random_single_post(single_posts: list, condition: str):
    try:
        if condition == "text":
            correct_posts = [single_post for single_post in single_posts if single_post[5] == "text"]
        elif condition == "media":
            correct_posts = [single_post for single_post in single_posts if single_post[5] in ["photo", "video"]]
        else:
            correct_posts = [single_post for single_post in single_posts if single_post[5] == "document"]

        if not correct_posts:
            return None

        picked_post = random.choice(correct_posts)
        single_posts.remove(picked_post)

        return picked_post, single_posts
    except Exception as e:
        logger.error("Возникла ошибка в get_random_single_post: %s", e)
