from pyrogram import types
from app.services.logs.logging import logger


def parse_markup(markup: types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup):
    text = ""
    try:
        # if markup.keyboard:
        #     text += "Type: Reply, Buttons: ["
        #
        #     row_counter = 0
        #     for button_row in markup.keyboard:
        #         if row_counter:
        #             text += ", "
        #         row_counter += 1
        #
        #         text += "["
        #
        #         button_counter = 0
        #         for button in button_row:
        #             if button_counter:
        #                 text += ", "
        #             button_counter += 1
        #
        #             text += f"[Text: {button.text}]"
        #
        #         text += "]"
        #
        #     text += "]"
        if markup.inline_keyboard:
            # text += "Type: Inline, Buttons: ["
            text = "["

            row_counter = 0
            for button_row in markup.inline_keyboard:
                if row_counter:
                    text += ", "
                row_counter += 1

                text += "["

                button_counter = 0
                for button in button_row:
                    if button_counter:
                        text += ", "
                    button_counter += 1

                    button_type = None
                    if button.callback_data:
                        callback_data = f"callback_data: {button.callback_data}"
                        button_type = "callback_data"
                    else:
                        callback_data = None

                    if button.url:
                        url = f"url: {button.url}"
                        button_type = "url"
                    else:
                        url = None

                    if button.web_app:
                        web_app = f"web_app: {button.web_app.url}"
                        button_type = "web_app"
                    else:
                        web_app = None

                    text += f"[Text: {button.text}, type: {button_type}"
                    if callback_data:
                        text += ", " + callback_data
                    elif url:
                        text += ", " + url
                    elif web_app:
                        text += ", " + web_app
                    text += "]"
                text += "]"
    except Exception as e:
        logger.error("Возникла ошибка в parse_markup: %s", e)
    finally:
        return text
