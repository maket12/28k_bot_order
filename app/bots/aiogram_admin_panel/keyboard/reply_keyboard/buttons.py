from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser
from aiogram.types import KeyboardButtonRequestChat
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Кнопки главного меню

main_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="👤Аккаунты👤"),
        KeyboardButton(text="📊Проекты📊")
    ],
    [
        KeyboardButton(text="📝Парсинг📝")
    ]
])


# Кнопка запроса контакта

request_contact_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="Отправить контакт",
                       request_user=KeyboardButtonRequestUser(request_id=1))
    ],
    [
        KeyboardButton(text="Назад")
    ]
])

# Кнопка запроса канала

request_chat_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="Отправить канал",
                       request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=True))
    ],
    [
        KeyboardButton(text="Отправить группу",
                       request_chat=KeyboardButtonRequestChat(request_id=3, chat_is_channel=False,
                                                              chat_is_forum=False))
    ],
    [
        KeyboardButton(text="Отправить форум",
                       request_chat=KeyboardButtonRequestChat(request_id=4, chat_is_channel=False,
                                                              chat_is_forum=True))
    ],
    [
        KeyboardButton(text="Назад")
    ]
])

# Кнопка пропуска ввода чего-либо

skip_action_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="Пропустить")
     ],
    [
        KeyboardButton(text="Назад")
    ]
])

# Отдельная кнопка Назад

reply_back_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="Назад")
    ]
])

# Кнопки выбора режима парсинга

parsing_regime_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="Парсинг истории чата")
    ],
    [
        KeyboardButton(text="Прослушка чата")
    ],
    [
        KeyboardButton(text="Назад")
    ]
])


# Функция создания кнопок выбора аккаунта-бота

def create_bots_markup(account_usernames: list):
    markup = ReplyKeyboardBuilder()

    for username in account_usernames:
        markup.row(KeyboardButton(text=username[0]))

    markup.row(KeyboardButton(text="Назад"))

    return markup.as_markup()
