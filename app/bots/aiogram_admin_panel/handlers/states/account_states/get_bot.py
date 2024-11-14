import asyncio

from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.state.state_init import GetBot
from app.bots.aiogram_admin_panel.handlers.reply_buttons.accounts import accounts
from app.bots.aiogram_admin_panel.handlers.inline_buttons.accounts.accounts import accounts_bots
from app.bots.aiogram_admin_panel.handlers.inline_buttons.accounts.accounts import accounts_secretary_posts, accounts_secretary_comments, accounts_agent_bot
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import proxy_markup, single_back_markup
from app.bots.workers_bots.aiogram_scripts.check_connection import check_aiogram_connection
from app.bots.workers_bots.pyrogram_scripts.check_connection import check_pyrogram_connection, check_pyrogram_code, \
    check_pyrogram_password
from app.services.database.database_code import AccountsDatabase
from app.services.logs.logging import logger

router = Router()

accounts_db = AccountsDatabase()


@router.callback_query(GetBot.get_proxy_type)
async def get_proxy_type(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        proxy_type = call.data.split('_')[1]

        state_data = await state.get_data()
        bot_task = state_data["bot_task"]

        if proxy_type == "back":
            if bot_task == "agent":
                await accounts_agent_bot(call=call, bot=bot)
            elif bot_task == "posts":
                await accounts_secretary_posts(call=call, bot=bot)
            else:
                await accounts_secretary_comments(call=call, bot=bot)

            await state.clear()
            return
        elif proxy_type == "none":
            if bot_task == "posts" or bot_task == "comments":
                await bot.edit_message_text(text="Теперь отправьте токен бота от @BotFather:",
                                            chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=single_back_markup)
                await state.set_state(GetBot.get_token)
                await state.update_data(api_id=None)
                await state.update_data(api_hash=None)
            else:
                await bot.edit_message_text(text="Теперь отправьте номер телефона от аккаунта-агента:",
                                            chat_id=call.from_user.id,
                                            message_id=call.message.message_id)
                await state.set_state(GetBot.get_phone_number)
            await state.update_data(proxy=None)
        else:
            await bot.edit_message_text(text="Отправьте прокси в следующем формате:\n"
                                        "ip:port или ip:port:login:password",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        reply_markup=single_back_markup)
            await state.set_state(GetBot.get_proxy_data)

        await state.update_data(proxy_type=proxy_type)
    except Exception as e:
        logger.error("Возникла ошибка в get_proxy_type: %s", e)
        await state.clear()


@router.callback_query(GetBot.get_proxy_data)
async def get_proxy_data_call(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if call.data == "back":
            await bot.edit_message_text(text="Теперь выберите тип прокси:",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        reply_markup=proxy_markup)
            await state.set_state(GetBot.get_proxy_type)
        else:
            await call.answer(text="Undefined action!", show_alert=True)
            await accounts_bots(call=call, bot=bot)
            await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_proxy_data_call: %s", e)
        await state.clear()


@router.message(GetBot.get_proxy_data)
async def get_proxy_data(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if ':' in message.text:
            await state.update_data(proxy_data=message.text)

            state_data = await state.get_data()
            bot_task = state_data["bot_task"]

            if bot_task == "posts" or bot_task == "comments":
                await bot.edit_message_text(text="Теперь отправьте токен бота от @BotFather:",
                                            chat_id=message.from_user.id,
                                            message_id=message.message_id,
                                            reply_markup=single_back_markup)
                await state.set_state(GetBot.get_token)
            else:
                await bot.edit_message_text(text="Теперь отправьте номер телефона бота\n"
                                                 "Номер может начинаться с '+'",
                                            chat_id=message.from_user.id,
                                            message_id=message.message_id,
                                            reply_markup=single_back_markup)
                await state.set_state(GetBot.get_phone_number)
        else:
            await bot.send_message(text="Отправьте прокси в корректном формате!\n"
                                        "ip:port или ip:port:login:password",
                                   chat_id=message.from_user.id,
                                   reply_markup=single_back_markup)
            return
    except Exception as e:
        logger.error("Возникла ошибка в get_proxy_data: %s", e)
        await state.clear()


@router.callback_query(GetBot.get_token)
async def get_bot_token_call(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if call.data == "back":
            await bot.edit_message_text(text="Теперь выберите тип прокси:",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        reply_markup=proxy_markup)
            await state.set_state(GetBot.get_proxy_type)
        else:
            await call.answer(text="Undefined action", show_alert=True)
            await accounts_bots(call=call, bot=bot)
            await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_bot_token_call", e)
        await state.clear()


@router.message(GetBot.get_token)
async def get_bot_token(message: types.Message, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        bot_task = state_data["bot_task"]
        proxy = state_data["proxy"]
        bot_token = message.text
        api_id = state_data["api_id"]
        api_hash = state_data["api_hash"]

        checker = await check_aiogram_connection(bot_token=bot_token, proxy=proxy)

        if not checker:
            logger.warning("Был передан некорректный токен: %s", bot_token)
            await bot.send_message(text="Был отправлен неправильный токен!\n"
                                        "Проверьте корректность вводимых значений и повторите ещё раз!",
                                   chat_id=message.from_user.id)
            await accounts(message=message, bot=bot)
            await state.clear()
            return

        name, username = checker

        values_to_add = [bot_task, proxy, bot_token, None, api_id, api_hash, name, username]
        accounts_db.add_bot_account(values=values_to_add)

        await bot.send_message(text=f"Аккаунт успешно добавлен как {bot_task}",
                               chat_id=message.chat.id)

        await asyncio.sleep(2)

        await accounts_bots(call=message, bot=bot)
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_bot_token: %s", e)
        await state.clear()


@router.callback_query(GetBot.get_phone_number)
async def get_phone_number_call(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if call.data == "back":
            await bot.edit_message_text(text="Теперь выберите тип прокси:",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        reply_markup=proxy_markup)
            await state.set_state(GetBot.get_proxy_type)
        else:
            await call.answer(text="Undefined action", show_alert=True)
            await accounts_bots(call=call, bot=bot)
            await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_phone_number_call: %s", e)
        await state.clear()


@router.message(GetBot.get_phone_number)
async def get_phone_number(message: types.Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(phone_number=message.text.replace(' ', ''))
        await bot.send_message(
            text="Теперь введите данные от приложения: api_id и api_hash.\n"
                 "Их можно получить, создав приложение на <a href='https://my.telegram.org'>сайте</a>.",
            chat_id=message.chat.id, parse_mode='html')
        await bot.send_message(text="Введите api_id:",
                               chat_id=message.chat.id,
                               reply_markup=single_back_markup)
        await state.set_state(GetBot.get_api_id)
    except Exception as e:
        logger.error("Возникла ошибка в get_phone_number: %s", e)
        await state.clear()


@router.callback_query(GetBot.get_api_id)
async def get_api_id_call(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if call.data == "back":
            await bot.edit_message_text(text="Теперь отправьте номер телефона бота\n"
                                             "Номер может начинаться с '+'",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        reply_markup=single_back_markup)
            await state.set_state(GetBot.get_phone_number)
        else:
            await call.answer(text="Undefined action", show_alert=True)
            await accounts_bots(call=call, bot=bot)
            await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_api_id_call: %s", e)
        await state.clear()


@router.message(GetBot.get_api_id)
async def get_api_id(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if message.text.isdigit():
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            await bot.send_message(text="Теперь введите api_hash:",
                                        chat_id=message.chat.id,
                                        reply_markup=single_back_markup)
            await state.update_data(api_id=message.text)
            await state.set_state(GetBot.get_api_hash)
        else:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            await bot.send_message(text="Api_id некорректен! Попробуйте ещё раз:",
                                   chat_id=message.chat.id,
                                   reply_markup=single_back_markup)
    except Exception as e:
        logger.error("Возникла ошибка в get_api_id: %s", e)
        await state.clear()


@router.callback_query(GetBot.get_api_hash)
async def get_api_hash_call(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if call.data == "back":
            await bot.send_message(text="Введите api_id:",
                                   chat_id=call.from_user.id,
                                   reply_markup=single_back_markup)
            await state.set_state(GetBot.get_api_id)
        else:
            await call.answer(text="Undefined action", show_alert=True)
            await accounts_bots(call=call, bot=bot)
            await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_api_hash_call: %s", e)
        await state.clear()


@router.message(GetBot.get_api_hash)
async def get_api_hash(message: types.Message, state: FSMContext, bot: Bot):
    try:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id-1)
        state_data = await state.get_data()
        phone = state_data["phone_number"].replace(' ', '')
        api_id = state_data["api_id"]
        api_hash = message.text
        pyrogram_client_info = await check_pyrogram_connection(phone_number=phone,
                                                               api_id=api_id, api_hash=api_hash,
                                                               proxy="")  # add proxy logic
        if pyrogram_client_info:
            pyrogram_client, sent_code_info = pyrogram_client_info

            await state.update_data(api_hash=message.text)
            await state.update_data(pyrogram_client=pyrogram_client)
            await state.update_data(sent_code_info=sent_code_info)

            await bot.send_message(text="Введите код авторизации, который вам отправил Telegram через точку\n"
                                        "Пример: 125.45",
                                   chat_id=message.chat.id)
            await state.set_state(GetBot.get_auth_code)
        else:
            await bot.send_message(text="Возникла ошибка при создании сессии!\n"
                                        "Проверьте валидность введённых данных!",
                                   chat_id=message.chat.id)
            await accounts_bots(call=message, bot=bot)
            await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_api_hash: %s", e)
        await state.clear()


@router.message(GetBot.get_auth_code)
async def get_auth_code(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if '.' in message.text:
            state_data = await state.get_data()
            pyrogram_client = state_data["pyrogram_client"]
            sent_code_info = state_data["sent_code_info"]
            auth_code = message.text.replace('.', '')

            pyrogram_client_info = await check_pyrogram_code(app=pyrogram_client, auth_code=auth_code,
                                                             code_info=sent_code_info)
            if isinstance(pyrogram_client_info, tuple) and pyrogram_client_info[0] == "password needed":
                await bot.send_message(text="Требуется пароль 2FA, введите его, добавив пробел между буквами в любое место.\n"
                                            "Пример: pass word",
                                       chat_id=message.chat.id)
                await state.update_data(pyrogram_client=pyrogram_client_info[1])
                await state.set_state(GetBot.get_auth_pass)
                return
            else:
                if pyrogram_client_info:
                    data_to_add = [state_data['bot_task'], state_data['proxy'], None,
                                   state_data['phone_number'], state_data['api_id'],
                                   state_data['api_hash'], pyrogram_client_info[0],
                                   pyrogram_client_info[1]]
                    accounts_db.add_bot_account(values=data_to_add)

                    await bot.send_message(text=f"Аккаунт успешно добавлен как {state_data['bot_task']}",
                                                 chat_id=message.chat.id)
                else:
                    await bot.send_message(text="Возникла ошибка при инициализации клиента!\n"
                                                      "Проверьте валидность введённых данных!",
                                                 chat_id=message.chat.id)
        else:
            await bot.send_message(text="Некорректная запись кода!",
                                         chat_id=message.chat.id)
        await asyncio.sleep(2)
        await accounts_bots(call=message, bot=bot)
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_auth_code: %s", e)
        await state.clear()


@router.message(GetBot.get_auth_pass)
async def get_auth_pass(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if ' ' in message.text:
            state_data = await state.get_data()
            pyrogram_client = state_data["pyrogram_client"]
            password = message.text.replace(' ', '')

            pyrogram_client_info = await check_pyrogram_password(app=pyrogram_client,
                                                                 password=password)

            if pyrogram_client_info:
                data_to_add = [state_data['bot_task'], state_data['proxy'], None,
                               state_data['phone_number'], state_data['api_id'],
                               state_data['api_hash'], pyrogram_client_info[0],
                               pyrogram_client_info[1]]
                accounts_db.add_bot_account(values=data_to_add)

                await bot.send_message(text=f"Аккаунт успешно добавлен как {state_data['bot_task']}",
                                       chat_id=message.chat.id)
            else:
                await bot.send_message(text="Возникла ошибка при инициализации клиента!\n"
                                            "Проверьте валидность пароля!",
                                       chat_id=message.chat.id)
        else:
            await bot.send_message(text="Неверная запись пароля!",
                                   chat_id=message.chat.id)
        await asyncio.sleep(2)
        await accounts_bots(call=message, bot=bot)
    except Exception as e:
        logger.error("Возникла ошибка в get_auth_code: %s", e)
    finally:
        await state.clear()
