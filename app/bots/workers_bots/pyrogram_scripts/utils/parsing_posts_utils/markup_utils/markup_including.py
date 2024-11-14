from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from app.services.logs.logging import logger


def re_parse_markup(markup_string: str):
    try:
        """""
        Распарсиваем строку. Убираем в начале и в конце квадратные скобки
        Далее поэлементно парсим кнопки:
            для начала сплитуем по правой квадратной скобке, каждый элемент - кнопка
            у каждой кнопки удаляем лишнюю левую квадратную скобку в начале
            сплитуем кнопку(подстроку) по атрибутам
            каждый атрибут сплитуем, чтобы обратиться только к значению, пропуская название
        """""
        markup = InlineKeyboardBuilder()

        markup_parsing_string = markup_string[1:len(markup_string) - 1].split(']')
        for pre_button in markup_parsing_string:
            button_data = pre_button[1:].split(', ')
            text = button_data[0].split(': ')[1]

            button_type = button_data[1].split(': ')[1]
            optional_field = button_data[2].split(': ')[1]
            if button_type == "callback_data":
                markup.button(text=text, callback_data=optional_field)
            elif button_type == "url":
                markup.button(text=text, url=optional_field)
            else:
                markup.button(text=text, web_app=WebAppInfo(url=optional_field))

        return markup
    except Exception as e:
        logger.error("Возникла ошибка в parse_markup: %s", e)
