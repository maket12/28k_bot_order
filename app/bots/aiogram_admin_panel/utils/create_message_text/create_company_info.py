from app.services.logs.logging import logger


def create_text(attributes: tuple):
    try:
        msg_text = (f"Название компании: {attributes[1]}\n"
                    f"Проект: {attributes[2]}\n"
                    f"Режим парсинга: {attributes[3]}\n"
                    f"Аккаунт-слушатель: {attributes[4]}\n"
                    f"Аккаунт-отправитель: {attributes[5]}\n"
                    f"Канал-донор: {attributes[6]}\n"
                    f"Канал-приёмник: {attributes[7]}")
    except Exception as e:
        logger.error("Возникла ошибка в create_text: %s", e)

