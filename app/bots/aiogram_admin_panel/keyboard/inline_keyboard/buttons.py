from math import ceil
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


# Клавиатура после создания компании/настройки компании

def create_after_company_markup(project_name: str, company_name: str):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Настройки компании", callback_data=f"settings_company_{company_name}")
        ],
        [
            InlineKeyboardButton(text="К проекту", callback_data=f"choose_project_{project_name}")
        ]
    ])
    return markup


# Функция создания клавиатуры с выбором проекта

def create_projects_buttons(projects: list):
    buttons = []
    for project in projects:
        buttons.append(InlineKeyboardButton(text=project[0], callback_data=f"choose_project_{project[0]}"))
    return buttons


# Функция навигация по проектам(меню с кнопками перемещения и выбора проекта)

def build_projects_markup(projects: list, current_page: int):
    markup = InlineKeyboardBuilder()

    if len(projects) == 0:
        first = prev = last = nxt = "current"
        last_page = "1"
    else:
        buttons_list = create_projects_buttons(projects=projects)

        last_page = str(ceil(len(buttons_list) / 4))

        if buttons_list:
            for button_ind in range(4 * (current_page - 1), (current_page - 1) * 4 + 4):
                if button_ind >= len(buttons_list):
                    break

                markup.row(buttons_list[button_ind])

        if current_page == 1:
            first = "current"
            prev = "current"
        else:
            first = 1
            prev = current_page - 1

        if current_page == ceil(len(buttons_list) / 4):
            last = "current"
            nxt = "current"
        else:
            last = ceil(len(buttons_list) / 4)
            nxt = current_page + 1

    markup.row(InlineKeyboardButton(text="1", callback_data=f"navigation_projects_{first}"),
               InlineKeyboardButton(text="<", callback_data=f"navigation_projects_{prev}"),
               InlineKeyboardButton(text=str(current_page), callback_data="navigation_projects_current"),
               InlineKeyboardButton(text=">", callback_data=f"navigation_projects_{nxt}"),
               InlineKeyboardButton(text=last_page,
                                    callback_data=f"navigation_projects_{last}"))
    markup.row(InlineKeyboardButton(text="Назад", callback_data="back_to_projects_menu"))
    return markup.as_markup()


# Функция создания кнопок с выбором компании

def create_companies_buttons(companies: list):
    buttons = []
    for company in companies:
        buttons.append(InlineKeyboardButton(text=company[0], callback_data=f"choose_company_{company[0]}"))
    return buttons


# Функция навигация по компаниям(меню с кнопками перемещения и выбора компании)

def build_companies_markup(companies: list, project_name: str, current_page: int):
    markup = InlineKeyboardBuilder()

    if len(companies) == 0:
        first = prev = last = nxt = "current"
        last_page = "1"
    else:
        buttons_list = create_companies_buttons(companies=companies)

        last_page = str(ceil(len(buttons_list) / 4))

        if buttons_list:
            for button_ind in range(4 * (current_page - 1), (current_page - 1) * 4 + 4):
                if len(buttons_list) == button_ind:
                    break

                markup.row(buttons_list[button_ind])

        if current_page == 1:
            first = "current"
            prev = "current"
        else:
            first = 1
            prev = current_page - 1

        if current_page == ceil(len(buttons_list) / 4):
            last = "current"
            nxt = "current"
        else:
            last = ceil(len(buttons_list) / 4)
            nxt = current_page + 1

    markup.row(InlineKeyboardButton(text="1", callback_data=f"navigation_companies_{first}"),
               InlineKeyboardButton(text="<", callback_data=f"navigation_companies_{prev}"),
               InlineKeyboardButton(text=str(current_page), callback_data="navigation_companies_current"),
               InlineKeyboardButton(text=">", callback_data=f"navigation_companies_{nxt}"),
               InlineKeyboardButton(text=last_page,
                                    callback_data=f"navigation_companies_{last}"))
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
            InlineKeyboardButton(text="Добавить компанию", callback_data=f"add_company_{project_name}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"choose_project_{project_name}")
        ]
    ])
    return markup


# Функция создания клавиатуры настроек компании

def create_company_settings_markup(company_name: str, company_status: str):
    if company_status == "inactive":
        status_button = InlineKeyboardButton(text="Запустить", callback_data=f"launch_company_{company_name}")
    else:
        status_button = InlineKeyboardButton(text="Остановить", callback_data=f"halt_company_{company_name}")

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            status_button
        ],
        [
            InlineKeyboardButton(text="Переименовать", callback_data=f"rename_company_{company_name}")
        ],
        [
            InlineKeyboardButton(text="Редактировать", callback_data=f"edit_company_{company_name}")
        ],
        [
            InlineKeyboardButton(text="Удалить", callback_data=f"delete_company_{company_name}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"choose_company_{company_name}")
        ]
    ])
    return markup


# Клавиатура редактирования компании

def create_edit_company_markup(company_name: str, parsing_regime: str):
    if parsing_regime == "refresh":
        button = InlineKeyboardButton(text="События на источнике",
                                      callback_data=f"edit_source_events_{company_name}")
    else:
        button = InlineKeyboardButton(text="Сбор истории",
                                      callback_data=f"edit_history_collecting_{company_name}")

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Каналы назначения",
                                 callback_data=f"edit_dest_channels_{company_name}")
        ],
        [
            InlineKeyboardButton(text="Сбор обсуждения",
                                 callback_data=f"edit_comments_collecting_{company_name}")
        ],
        [
            button
        ],
        [
            InlineKeyboardButton(text="Назад",
                                 callback_data=f"settings_company_{company_name}")
        ]
    ])
    return markup


# Отдельная кнопка назад для возврата к настройкам

def create_back_to_settings_markup(company_name: str):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад",
                                 callback_data=f"back_settings_{company_name}")
        ]
    ])
    return markup


# Клавиатура раздела "Каналы назначения"

def create_edit_dest_channels_markup(company_name: str, amount_of_channels: int):
    markup = InlineKeyboardBuilder()
    markup.button(text="Добавить канал назначения",
                  callback_data=f"add_recp_channel_{company_name}")

    if amount_of_channels > 1:
        markup.button(text="Удалить канал назначения",
                      callback_data=f"del_recp_channel_{company_name}")

    markup.button(text="Назад",
                  callback_data=f"edit_company_{company_name}")
    return markup.adjust(1).as_markup()


# Клавиатура выбора способа сбора источника и обсуждения

def create_collect_data_markup(company_name: str, data_to_collect: str, comments_acc_existing: bool):
    buttons = [
        [
            InlineKeyboardButton(text="За всё время",
                                 callback_data=f"collecting_way_all_{data_to_collect}_{company_name}")
        ],
        [
            InlineKeyboardButton(text="По выбору периода",
                                 callback_data=f"collecting_way_period_{data_to_collect}_{company_name}")
        ],
        [
            InlineKeyboardButton(text="По ссылкам",
                                 callback_data=f"collecting_way_links_{data_to_collect}_{company_name}")
        ]
    ]

    if not comments_acc_existing and data_to_collect == "comments":
        buttons.append(
            [
                InlineKeyboardButton(text="Добавить секретаря",
                                     callback_data=f"add_comments_secretary_{company_name}")
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(text="Назад",
                                 callback_data=f"edit_company_{company_name}")
        ]
    )

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


# Клавиатура выбора событий для отслеживания

def create_choose_events_markup(company_name: str, current_events: list):
    pin = delete = edit = "❌"

    for event in current_events:
        if event == "pin":
            pin = "✅"
        elif event == "delete":
            delete = "✅"
        elif event == "edit":
            edit = "✅"

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Закрепеление поста" + pin,
                                 callback_data=f"choose_event_pin_{company_name}")
        ],
        [
            InlineKeyboardButton(text="Удаление поста" + delete,
                                 callback_data=f"choose_event_delete_{company_name}")
        ],
        [
            InlineKeyboardButton(text="Редактирование поста" + edit,
                                 callback_data=f"choose_event_edit_{company_name}")
        ],
        [
            InlineKeyboardButton(text="Назад",
                                 callback_data=f"edit_company_{company_name}")
        ]
    ])
    return markup


# Кнопки подтверждения/отклонения удаления проекта/компании

def create_accepting_delete_markup(name: str):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data=f"accept_deleting_{name}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"reject_deleting_{name}")
        ]
    ])
    return markup
