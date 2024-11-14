from app.services.logs.logging import logger


def with_entities_including(text: str, entities: str):
    try:
        entities_list = entities.split(';')

        for entity in entities_list:
            entity_objects = entity.split(', ')
            entity_type = entity_objects[0].split(':')[1].strip()
            entity_offset = int(entity_objects[1].split(':')[1].strip())
            entity_length = int(entity_objects[2].split(':')[1].strip())

            before_entity = text[:entity_offset]
            with_entity = text[entity_offset:(entity_offset + entity_length)]
            after_entity = text[(entity_offset + entity_length):]

            if entity_type == "MessageEntityType.BOLD":
                entity_part = '<b>' + with_entity + '</b>'
            elif entity_type == "MessageEntityType.ITALIC":
                entity_part = '<i>' + with_entity + '</i>'
            elif entity_type == "MessageEntityType.UNDERLINE":
                entity_part = '<u>' + with_entity + '</u>'
            elif entity_type == "MessageEntityType.STRIKETHROUGH":
                entity_part = '<s>' + with_entity + '</s>'
            elif entity_type == "MessageEntityType.SPOILER":
                entity_part = '<span class="tg-spoiler">' + with_entity + '</span>'
            elif entity_type == "MessageEntityType.CODE":
                entity_part = '<code>' + with_entity + '</code>'
            elif entity_type == "MessageEntityType.PRE":
                entity_part = '<pre>' + with_entity + '</pre>'
            elif entity_type == "MessageEntityType.BLOCKQUOTE":
                entity_part = '<blockquote>' + with_entity + '</blockquote>'
            elif entity_type == "MessageEntityType.TEXT_LINK":
                entity_url = entity_objects[3].split(':')[1].strip()
                entity_part = f'<a href="{entity_url}">' + with_entity + '</a>'
            else:
                logger.warning("Unknowing entity_type: %s", entity_type)
                continue

            text = before_entity + entity_part + after_entity
    except Exception as e:
        logger.error("Возникла ошибка в entities_including: %s", e)
    finally:
        return text


