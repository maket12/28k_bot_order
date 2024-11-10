from pyrogram import types
from app.services.logs.logging import logger


def parse_markup(markup: types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup):
    try:
        text = ""
        if markup.keyboard:
            text += "Type: Reply, Buttons: ["

            row_counter = 0
            for button_row in markup.keyboard:
                if row_counter:
                    text += ", "
                row_counter += 1

                text += "["

                button_counter = 0
                for button in button_row:
                    if button_counter:
                        text += ", "
                    button_counter += 1

                    text += f"[Text: {button.text}]"

                text += "]"

            text += "]"
        elif markup.inline_keyboard:
            text += "Type: Inline, Buttons: ["

            row_counter = 0
            for button in markup.inline_keyboard:
                if row_counter:
                    text += ", "
                row_counter += 1

                text += "["

                text += f"[Text: {button[]}"
    except Exception as e:
        logger.error("Возникла ошибка в parse_markup: %s", e)
