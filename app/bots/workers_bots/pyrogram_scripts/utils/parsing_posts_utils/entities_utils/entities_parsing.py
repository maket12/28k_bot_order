from pyrogram import types
from app.services.logs.logging import logger


def parse_entities(entities: list[types.MessageEntity]):
    result = ""
    try:
        for entity in entities:
            result += f"Type: {entity.type}, Offset: {entity.offset}, Length: {entity.length}"

            if entity.url:
                result += f", Url: {entity.url}"

            result += ";"
    except Exception as e:
        logger.error("Возникла ошибка в parse_with_entities: %s", e)
    finally:
        return result
