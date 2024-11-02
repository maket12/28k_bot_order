from app.services.logs.logging import logger


def create_text(company_attributes: tuple):
    try:
        if company_attributes[3] == "grabbing":
            parsing_regime = "Парсинг истории чата"
            company_additional_data = f"Парсинг: {company_attributes[10]}"
        else:
            parsing_regime = "Прослушка чата"
            company_additional_data = f"События: <b>{"Есть" if company_attributes[11] else "не установлены"}</b>"

        if company_attributes[7] == "channel":
            source_type = "Канал"
        elif company_attributes[7] == "group":
            source_type = "Группа"
        else:
            source_type = "Форум"

        if company_attributes[9] == "channel":
            recp_type = "Канал"
        elif company_attributes[9] == "group":
            recp_type = "Группа"
        else:
            recp_type = "Форум"

        text = (f"Проект: <b>{company_attributes[2]}</b>\n"
                 f"Компания: <b>{company_attributes[1]}</b>\n"
                 f"Формат: <b>{parsing_regime}</b>\n"
                 f"Агент: <b>{company_attributes[4]}</b>\n"
                 f"Отправитель: <b>{company_attributes[5]}</b>\n"
                 f"Источник: <b>{source_type}</b>\n"
                 f"ID источника: <b>{company_attributes[6]}</b>\n"
                 f"Назначение: <b>{recp_type}</b>\n"
                 f"ID назначения: <b>{company_attributes[8].replace(' ', ' | ')}</b>\n"
                 f"{company_additional_data}\n"
                 f"Комментарии: <b>{company_attributes[14] if company_attributes[14] else "Не собираются"}</b>\n"
                 f"Секретарь для комментариев: <b>{company_attributes[13] if company_attributes[13] else "Не выбран"}</b>\n"
                 f"Личка: <b>{"Да" if company_attributes[12] else "Нет"}</b>")
        return text
    except Exception as e:
        logger.error("Возникла ошибка в create_text: %s", e)

