from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Кнопки раздела "Аккаунты"

accounts_main_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Пользовательские аккаунты",
                             callback_data=f"accounts_users")
    ],
    [
        InlineKeyboardButton(text="Аккаунты-расходники",
                             callback_data=f"accounts_bots")
    ],
    [
        InlineKeyboardButton(text="Назад",
                             callback_data="back_to_main_menu")
    ]
])


# Кнопки раздела "Пользовательские аккаунты"

accounts_users_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Тим-лиды", callback_data="accounts_team_leads"),
        InlineKeyboardButton(text="Менеджеры", callback_data="accounts_managers")
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data="back_to_accounts_main")
    ]
])


# Кнопки раздела "Аккаунты-расходники"


bot_task_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Секретарь для постов", callback_data="bot_task_posts"),
        InlineKeyboardButton(text="Секретарь для комментариев", callback_data="bot_task_comments")
    ],
    [
        InlineKeyboardButton(text="Аккаунт-агент", callback_data="bot_task_agent"),
        InlineKeyboardButton(text="Назад", callback_data="back_to_accounts_main")
    ]
])


# Функция создания кнопок для выбора аккаунта

def create_accounts_markup(accounts_ids: list, account_type: str, account_role: str):
    markup = InlineKeyboardBuilder()
    buttons = []

    for k in range(1, len(accounts_ids) + 1):
        buttons.append(InlineKeyboardButton(
            text=f"Аккаунт {k}",
            callback_data=f"account_info_{account_type}_{accounts_ids[k-1][0]}")
        )
        if k % 2 == 0:
            markup.row(*buttons)
            buttons = []
    if buttons:
        markup.row(*buttons)

    markup.row(
        InlineKeyboardButton(
            text="Добавить",
            callback_data=f"add_account_{account_type}_{account_role}"
        ),
        InlineKeyboardButton(
            text="Назад",
            callback_data=f"back_to_accounts_{account_type}"
        )
    )

    return markup.as_markup()


# Функция генерации кнопок при выборе определённого аккаунта
def create_acc_settings_markup(account_type: str, account_role: str, account_id: int):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"back_to_accounts_{account_role}"
            ),
            InlineKeyboardButton(
                text="Настройки",
                callback_data=f"account_settings_{account_type}_{account_role}_{account_id}"
            )
        ]
    ])
    return markup


def create_acc_pre_delete_markup(account_type: str, account_id: int):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Удалить",
                callback_data=f"pre_delete_account_{account_type}_{account_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"back_to_spec_account_{account_type}_{account_id}"
            )
        ]
    ])
    return markup


def create_acc_delete_markup(account_type: str, account_id: int):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=f"delete_account_{account_type}_{account_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"back_to_spec_account_{account_type}_{account_id}"
            )
        ]
    ])
    return markup


def create_back_to_spec_acc_button(account_type: str):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"back_to_accounts_{account_type}"
            )
        ]
    ])
    return markup


# Кнопки выбора прокси

proxy_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="HTTP IPV4", callback_data="proxy_http"),
        InlineKeyboardButton(text="Без прокси", callback_data="proxy_none")
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data="proxy_back_bots")
    ]
])


# Отдельная кнопка Назад во время регистрации аккаунта-расходника

single_back_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Назад", callback_data="back")
    ]
])


# Кнопки раздела "Проекты"

projects_main_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Добавить проект", callback_data="add_project")
    ],
    [
        InlineKeyboardButton(text="Проекты", callback_data="see_projects")
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
    ]
])


# Клавиатура после создания компании

def create_after_company_markup(project_name: str, company_name: str):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="К проекту", callback_data=f"choose_project_{project_name}")
        ],
        [
            InlineKeyboardButton(text="Настройки компании", callback_data=f"choose_company_{company_name}")
        ]
    ])
    return markup


# Функция создания клавиатуры с выбором проекта

def create_projects_markup(projects: list):
    markup = InlineKeyboardBuilder()
    buttons = []
    for project in projects:
        buttons.append(InlineKeyboardButton(text=project[0], callback_data=f"choose_project_{project[0]}"))
    markup.add(*buttons)
    return markup.adjust(2).as_markup()


# Функция создания кнопок с выбором компании

def create_companies_buttons(companies: list):
    buttons = []
    for company in companies:
        buttons.append(InlineKeyboardButton(text=company[0], callback_data=f"choose_company_{company[0]}"))
    return buttons


# Функция навигация по компаниям(меню с кнопками перемещения и выбора компании)

def build_companies_markup(companies: list, project_name: str, current_page: int):
    markup = InlineKeyboardBuilder()

    buttons_list = create_companies_buttons(companies=companies)

    if buttons_list:
        for button_ind in range(4 * (current_page - 1), (current_page - 1) + 4):
            if len(buttons_list) == button_ind:
                break

            markup.row(buttons_list[button_ind])

    if current_page == 1:
        first = "current"
        prev = "current"
    else:
        first = 1
        prev = current_page - 1

    if current_page == ((len(buttons_list) // 4) + len(buttons_list) % 4):
        last = "current"
        nxt = "current"
    else:
        last = (len(buttons_list) // 4) + len(buttons_list) % 4
        nxt = current_page + 1

    markup.row(InlineKeyboardButton(text="1", callback_data=f"navigation_project_{first}"),
               InlineKeyboardButton(text="<", callback_data=f"navigation_project_{prev}"),
               InlineKeyboardButton(text=str(current_page), callback_data="navigation_project_current"),
               InlineKeyboardButton(text=">", callback_data=f"navigation_project_{nxt}"),
               InlineKeyboardButton(text=str(((len(buttons_list) // 4) + len(buttons_list) % 4)),
                                    callback_data=f"navigation_project_{last}"))
    markup.row(InlineKeyboardButton(text="Настройки", callback_data=f"settings_project_{project_name}"))
    markup.row(InlineKeyboardButton(text="Назад", callback_data="back_to_projects"))
    return markup.as_markup()


# Функция создания клавиатуры настроек проекта

def create_project_settings_markup(project_name: str):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить название",
                                 callback_data=f"change_project_name_{project_name}")
        ],
        [
            InlineKeyboardButton(text="Удалить", callback_data=f"delete_project_{project_name}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"choose_project_{project_name}")
        ]
    ])
    return markup
