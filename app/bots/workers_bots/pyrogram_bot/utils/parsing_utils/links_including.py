from pyrogram import types
from bot.services.logs.logging import logger


async def parse_with_links(entities: list, text_or_caption: str):
    try:
        result = text_or_caption
        if entities:
            result = ''
            last_offset = 0
            for entity in entities:
                print(entity.type)
                if str(entity.type) == "MessageEntityType.TEXT_LINK":
                    # Добавление текста перед ссылкой
                    result += text_or_caption[last_offset:entity.offset]
                    # Добавление ссылки
                    result += f'<a href="{entity.url}">{text_or_caption[entity.offset:entity.offset + entity.length]}</a>'
                    last_offset = entity.offset + entity.length
            # Добавление текста после последней ссылки
            result += text_or_caption[last_offset:]
        return result
    except Exception as e:
        logger.error("Возникла ошибка в parse_with_links: %s", e)

