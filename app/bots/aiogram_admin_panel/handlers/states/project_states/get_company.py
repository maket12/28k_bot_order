import asyncio
from datetime import datetime
from aiogram import types, Router, Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.projects import add_project
from app.bots.aiogram_admin_panel.state.state_init import GetCompanyAttributes
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import parsing_regime_markup, \
    request_chat_markup, create_bots_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_after_company_markup, \
    create_company_settings_markup
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.companies import add_company
from app.bots.aiogram_admin_panel.utils.create_message_text.create_company_info import create_text
from app.services.database.database_code import ProjectsDatabase, AccountsDatabase
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()

accounts_db = AccountsDatabase()

router = Router()


@router.message(GetCompanyAttributes.get_company_name)
async def get_company_name(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if message.text == "Назад":
            state_data = await state.get_data()
            project_name = state_data['project_name']
            projects_db.delete_project(name=project_name)

            await add_project(call=message, state=state, bot=bot)
            return
        if message.text == "Пропустить":
            company_name = datetime.now().strftime("%H:%M:%S")
        else:
            company_name = message.text
        await state.update_data(company_name=company_name)

        await bot.send_message(text="Теперь выберите режим пересылки:", chat_id=message.chat.id,
                               reply_markup=parsing_regime_markup)

        await state.set_state(GetCompanyAttributes.get_parsing_regime)
    except Exception as e:
        logger.error("Возникла ошибка в get_chat_id: %s", e)


@router.message(GetCompanyAttributes.get_parsing_regime)
async def get_parsing_regime(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if message.text == "Назад":
            sent_msg = await bot.send_message(text="Возвращаемся к созданию компании...",
                                              chat_id=message.from_user.id)
            await asyncio.sleep(2)
            await bot.delete_message(chat_id=message.from_user.id, message_id=sent_msg.message_id)
            await add_company(call=message, state=state, bot=bot)
            return

        if message.text == "Парсинг истории чата":
            parsing_regime = "grabbing"
        elif message.text == "Прослушка чата":
            parsing_regime = "refresh"
        else:
            await bot.send_message(text="Выберите вариант ответа из предложенных!",
                                   chat_id=message.chat.id,
                                   reply_markup=parsing_regime_markup)
            return
        await state.update_data(parsing_regime=parsing_regime)

        usernames = accounts_db.get_all_accounts_usernames(task="agent")
        await bot.send_message(text="Отлично! Теперь выберите бота-слушателя из предложенных",
                               chat_id=message.chat.id,
                               reply_markup=create_bots_markup(
                                   account_usernames=usernames)
                               )

        await state.set_state(GetCompanyAttributes.get_receiver)
    except Exception as e:
        logger.error("Возникла ошибка в get_parsing_regime: %s", e)


@router.message(GetCompanyAttributes.get_receiver)
async def get_receiver(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if message.text == "Назад":
            await bot.send_message(text="Теперь выберите режим пересылки:", chat_id=message.chat.id,
                                   reply_markup=parsing_regime_markup)

            await state.set_state(GetCompanyAttributes.get_parsing_regime)
            return

        receiver_account = message.text
        await state.update_data(receiver_account=receiver_account)

        usernames = accounts_db.get_all_accounts_usernames(task="posts")
        await bot.send_message(text="Теперь выберите бота-отправителя из предложенных: ",
                               chat_id=message.chat.id,
                               reply_markup=create_bots_markup(
                                   account_usernames=usernames)
                               )

        await state.set_state(GetCompanyAttributes.get_sender)
    except Exception as e:
        logger.error("Возникла ошибка в get_receiver: %s", e)


@router.message(GetCompanyAttributes.get_sender)
async def get_sender(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if message.text == "Назад":
            usernames = accounts_db.get_all_accounts_usernames(task="agent")
            await bot.send_message(text="Отлично! Теперь выберите бота-слушателя из предложенных",
                                   chat_id=message.chat.id,
                                   reply_markup=create_bots_markup(
                                       account_usernames=usernames)
                                   )

            await state.set_state(GetCompanyAttributes.get_receiver)
            return

        sender_account = message.text
        await state.update_data(sender_account=sender_account)

        await bot.send_message(text="Теперь отправьте чат-источник.\n"
                                    "Используйте кнопку или отправьте chat_id + chat_type.\n"
                                    "Пример: -10000000000 channel.",
                               chat_id=message.chat.id,
                               reply_markup=request_chat_markup)
        await state.set_state(GetCompanyAttributes.get_source_channel)
    except Exception as e:
        logger.error("Возникла ошибка в get_sender: %s", e)


@router.message(GetCompanyAttributes.get_source_channel)
async def get_source_channel(message: types.ChatShared | types.Message, state: FSMContext, bot: Bot):
    try:
        if message.chat_shared:
            source_chat_id = message.chat_shared.chat_id

            request_id = message.chat_shared.request_id
            if request_id == 2:
                source_chat_type = "channel"
            elif request_id == 3:
                source_chat_type = "group"
            else:
                source_chat_type = "forum"
        else:
            if message.text == "Назад":
                usernames = accounts_db.get_all_accounts_usernames(task="posts")
                await bot.send_message(text="Теперь выберите бота-отправителя из предложенных: ",
                                       chat_id=message.chat.id,
                                       reply_markup=create_bots_markup(
                                           account_usernames=usernames
                                       ))

                await state.set_state(GetCompanyAttributes.get_sender)
                return
            message_split = message.text.split(' ')
            if len(message_split) == 2 and message_split[0].startswith('-'):
                source_chat_id, source_chat_type = message_split
            else:
                await bot.send_message(text="Отправьте корректные данные!",
                                       chat_id=message.chat.id)
                return

        await state.update_data(source_chat_id=source_chat_id)
        await state.update_data(source_chat_type=source_chat_type)

        await bot.send_message(text="Теперь выберите чат назначения!\n"
                                    "Используйте кнопку или отправьте chat_id + chat_type.\n"
                                    "Пример: -10000000000 forum.",
                               chat_id=message.chat.id, reply_markup=request_chat_markup)

        await state.set_state(GetCompanyAttributes.get_recipient_channel)
    except Exception as e:
        logger.error("Возникла ошибка в get_source_channel: %s", e)


@router.message(GetCompanyAttributes.get_recipient_channel)
async def get_recipient_channel(message: types.ChatShared | types.Message, state: FSMContext, bot: Bot):
    try:
        if message.chat_shared:
            recipient_chat_id = message.chat_shared.chat_id

            request_id = message.chat_shared.request_id
            if request_id == 2:
                recipient_chat_type = "channel"
            elif request_id == 3:
                recipient_chat_type = "group"
            else:
                recipient_chat_type = "forum"
        else:
            if message.text == "Назад":
                await bot.send_message(text="Теперь отправьте канал-источник\n"
                                            "Важно, чтобы бот-слушатель имел к нему доступ!",
                                       chat_id=message.chat.id,
                                       reply_markup=request_chat_markup)
                await state.set_state(GetCompanyAttributes.get_source_channel)
                return
            message_split = message.text.split(' ')
            if len(message_split) == 2 and message_split[0].startswith('-'):
                recipient_chat_id, recipient_chat_type = message_split
            else:
                await bot.send_message(text="Отправьте корректные данные!",
                                       chat_id=message.chat.id)
                return

        state_data = await state.get_data()

        attributes = [state_data['company_name'], state_data['project_name'],
                      state_data['parsing_regime'], state_data['receiver_account'],
                      state_data['sender_account'], state_data['source_chat_id'],
                      state_data['source_chat_type'], recipient_chat_id, recipient_chat_type]

        projects_db.add_company(company_attributes=attributes)

        await bot.send_message(text="Компания успешно добавлена!",
                               chat_id=message.chat.id,
                               reply_markup=ReplyKeyboardRemove())
        await bot.send_message(text="Выберите действие:",
                               chat_id=message.chat.id,
                               reply_markup=create_after_company_markup(
                                   project_name=state_data['project_name'],
                                   company_name=state_data['company_name']
                               ))

        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_recipient_channel: %s", e)


@router.message(GetCompanyAttributes.get_comments_account)
async def get_comments_account(message: types.Message, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        company_name = state_data["company_name"]
        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)

        if message.text == "Назад":
            await bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id)
        else:
            projects_db.change_company_attribute(company_name=company_name,
                                                 attribute_name="comments_account",
                                                 value=message.text)
            await bot.send_message(text="Секретарь успешно установлен!",
                                   chat_id=message.chat.id,
                                   reply_markup=ReplyKeyboardRemove())

        await bot.send_message(text=create_text(company_attributes=company_attributes),
                               chat_id=message.chat.id,
                               reply_markup=create_company_settings_markup(
                                   company_name=company_name,
                                   company_status=company_attributes[15]),
                               parse_mode="html",
                               disable_web_page_preview=True)
    except Exception as e:
        logger.error("Возникла ошибка в get_comments_account: %s", e)
    finally:
        await state.clear()
