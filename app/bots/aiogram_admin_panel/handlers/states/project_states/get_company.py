import asyncio
from datetime import datetime
from aiogram import types, Router, Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.projects import add_project
from app.bots.aiogram_admin_panel.state.state_init import GetCompanyAttributes
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import parsing_regime_markup, create_receivers_markup, \
    request_chat_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_after_company_markup
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.companies import add_company
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()

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
            await asyncio.sleep(1.5)
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

        await bot.send_message(text="Отлично! Теперь выберите бота-слушателя из предложенных",
                               chat_id=message.chat.id, reply_markup=create_receivers_markup())

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

        await bot.send_message(text="Теперь выберите бота-отправителя из предложенных: ",
                               chat_id=message.chat.id, reply_markup=create_receivers_markup())  # Заменить!

        await state.set_state(GetCompanyAttributes.get_sender)
    except Exception as e:
        logger.error("Возникла ошибка в get_receiver: %s", e)


@router.message(GetCompanyAttributes.get_sender)
async def get_sender(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if message.text == "Назад":
            await bot.send_message(text="Отлично! Теперь выберите бота-слушателя из предложенных",
                                   chat_id=message.chat.id, reply_markup=create_receivers_markup())

            await state.set_state(GetCompanyAttributes.get_receiver)
            return

        sender_account = message.text
        await state.update_data(sender_account=sender_account)

        await bot.send_message(text="Теперь отправьте чат-источник\n"
                                    "Важно, чтобы бот-слушатель имел к нему доступ!",
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
                await bot.send_message(text="Теперь выберите бота-отправителя из предложенных: ",
                                       chat_id=message.chat.id, reply_markup=create_receivers_markup())  # Заменить!

                await state.set_state(GetCompanyAttributes.get_sender)
                return

            await bot.send_message(text="Нажмите на кнопку: 'Отправить канал'!",
                                   chat_id=message.chat.id)
            return

        await state.update_data(source_chat_id=source_chat_id)
        await state.update_data(source_chat_type=source_chat_type)

        await bot.send_message(text="Теперь выберите чат назначения!\n"
                                    "Важно, чтобы бот-отправитель имел к нему доступ!",
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
            
            await bot.send_message(text="Нажмите на кнопку: 'Отправить канал'!",
                                   chat_id=message.chat.id)
            return

        state_data = await state.get_data()

        attributes = [state_data['company_name'], state_data['project_name'],
                      state_data['parsing_regime'], state_data['receiver_account'],
                      state_data['sender_account'], state_data['source_chat_id'],
                      state_data['source_chat_type'], recipient_chat_id, recipient_chat_type]

        projects_db.add_company(company_attributes=attributes)

        await state.clear()
        await bot.send_message(text="Компания успешно добавлена!",
                               chat_id=message.chat.id,
                               reply_markup=ReplyKeyboardRemove())
        await bot.send_message(text="Выберите действие:",
                               chat_id=message.chat.id,
                               reply_markup=create_after_company_markup(
                                   project_name=state_data['project_name'],
                                   company_name=state_data['company_name']
                               ))
    except Exception as e:
        logger.error("Возникла ошибка в get_recipient_channel: %s", e)
