from aiogram.fsm.state import State, StatesGroup


class GetUser(StatesGroup):
    get_chat_id = State()


class GetBot(StatesGroup):
    get_bot_task = State()
    get_proxy_type = State()
    get_proxy_data = State()
    get_token = State()  # only for aiogram bot
    get_phone_number = State()  # only for pyrogram bot
    get_api_id = State()  # only for pyrogram bot
    get_api_hash = State()  # only for pyrogram bot
    get_auth_code = State()  # only for pyrogram bot
    get_auth_pass = State()  # only for pyrogram bot


class GetProjectAttributes(StatesGroup):
    get_project_name = State()
    change_project_name = State()
    delete_project = State()


class GetCompanyAttributes(StatesGroup):
    get_company_name = State()
    get_parsing_regime = State()
    get_receiver = State()
    get_sender = State()
    get_source_channel = State()
    get_recipient_channel = State()
    change_company_name = State()
    delete_company = State()
