import asyncio
from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import build_companies_markup, \
    create_company_settings_markup, create_back_to_settings_markup, create_edit_company_markup, \
    create_collect_comments_markup
from app.bots.aiogram_admin_panel.state.state_init import EditCompanyAttributes
from app.bots.aiogram_admin_panel.utils.create_message_text.create_company_info import create_text
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()

router = Router()


@router.callback_query(EditCompanyAttributes.delete_company)
async def delete_company(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        if call.data.startswith("accept_deleting"):
            projects_db.delete_company(company_name=company_name)
            await bot.edit_message_text(text="Компания успешно удалена!",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id)
        else:
            await bot.edit_message_text(text="Удаление компании отменено!",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id)

        await asyncio.sleep(2)

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)

        await bot.edit_message_text(text=create_text(company_attributes=company_attributes),
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_company_settings_markup(
                                        company_name=company_name,
                                        company_status=company_attributes[15]),
                                    parse_mode="html", disable_web_page_preview=True
                                    )
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в delete_company: %s", e)


@router.message(EditCompanyAttributes.add_recipient_channel)
async def add_recipient_channel(message: types.ChatShared | types.Message, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        company_name = state_data['company_name']

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        if message.chat_shared:
            request_id = message.chat_shared.request_id
            if request_id == 2:
                recp_chat_type = "channel"
            elif request_id == 3:
                recp_chat_type = "group"
            else:
                recp_chat_type = "forum"

            current_chat_type = projects_db.get_company_attribute(attribute="recipient_chat_type",
                                                                  company_name=company_name)

            if current_chat_type == recp_chat_type:
                projects_db.add_recp_channel(company_name=company_name,
                                             recp_channel=str(message.chat_shared.chat_id))
                sent_msg = await bot.send_message(text="Чат успешно добавлен!",
                                                  chat_id=message.chat.id,
                                                  reply_markup=ReplyKeyboardRemove())
            else:
                sent_msg = await bot.send_message(text="Данный чат не совпадает с типом чата-назначения!\n"
                                                       "Добавление невозможно!",
                                                  chat_id=message.chat.id,
                                                  reply_markup=ReplyKeyboardRemove())
        else:
            sent_msg = await bot.send_message(text="Возвращаемся в меню...",
                                              chat_id=message.chat.id,
                                              reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(2)

        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=sent_msg.message_id)

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)

        await bot.send_message(text=create_text(company_attributes=company_attributes),
                               chat_id=message.chat.id,
                               reply_markup=create_company_settings_markup(
                                   company_name=company_attributes[1],
                                   company_status=company_attributes[15]),
                               parse_mode="html",
                               disable_web_page_preview=True)
    except Exception as e:
        logger.error("Возникла ошибка в add_recipient_channel: %s", e)


@router.message(EditCompanyAttributes.delete_recipient_channel)
async def delete_recipient_channel(message: types.ChatShared | types.Message, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        company_name = state_data['company_name']

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        if message.chat_shared:
            projects_db.delete_recp_channel(company_name=company_name,
                                            recp_channel=str(message.chat_shared.chat_id))
            sent_msg = await bot.send_message(text="Удаление выполнено успешно!",
                                              chat_id=message.chat.id)
        else:
            sent_msg = await bot.send_message(text="Возвращаемся в меню...",
                                              chat_id=message.chat.id,
                                              reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(2)

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)

        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=sent_msg.message_id)

        await bot.send_message(text=create_text(company_attributes=company_attributes),
                               chat_id=message.chat.id,
                               reply_markup=create_company_settings_markup(
                                   company_name=company_attributes[1],
                                   company_status=company_attributes[15]),
                               parse_mode="html",
                               disable_web_page_preview=True)
    except Exception as e:
        logger.error("Возникла ошибка в delete_recipient_channel: %s", e)


@router.message(EditCompanyAttributes.edit_company_name)
async def edit_company_name(message: types.Message, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        old_name = state_data["old_company_name"]

        if message.text == "Назад":
            current_name = old_name
            msg = await bot.send_message(text="Возвращаемся к компании...",
                                         chat_id=message.chat.id,
                                         reply_markup=ReplyKeyboardRemove())
        else:
            current_name = message.text
            projects_db.change_company_attribute(company_name=old_name, attribute_name="company_name",
                                                 value=current_name)
            msg = await bot.send_message(text="Название компании успешно изменено!",
                                         chat_id=message.chat.id,
                                         reply_markup=ReplyKeyboardRemove())

        await asyncio.sleep(2)
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=msg.message_id)

        company_attributes = projects_db.get_all_company_attributes(company_name=current_name)

        await bot.send_message(text=create_text(company_attributes=company_attributes),
                               chat_id=message.chat.id,
                               reply_markup=create_company_settings_markup(
                                   company_name=company_attributes[1],
                                   company_status=company_attributes[15]),
                               parse_mode="html",
                               disable_web_page_preview=True)
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в edit_company_name: %s", e)


@router.callback_query(EditCompanyAttributes.edit_collecting_period)
async def edit_collecting_period_callback(message: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        company_name = state_data["company_name"]

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)
        await bot.edit_message_text(text=create_text(company_attributes=company_attributes),
                                    chat_id=message.from_user.id,
                                    message_id=message.message.message_id,
                                    reply_markup=create_collect_comments_markup(
                                        company_name=company_name,
                                        comments_acc_existing=bool(company_attributes[13])),
                                    parse_mode="html",
                                    disable_web_page_preview=True)

        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в edit_collecting_period_callback: %s", e)


@router.message(EditCompanyAttributes.edit_collecting_period)
async def edit_collecting_period_message(message: types.Message, state: FSMContext, bot: Bot):
    try:
        # Проверка на корректность формата (примерная)
        if not (message.text[0].isdigit() and message.text.count('.') == 4 and ':' in message.text):
            await bot.send_message(text="Отправьте период в корректном формате!\n"
                                        "<b>день.месяц.год - день.месяц.год</b>",
                                   chat_id=message.chat.id,
                                   parse_mode="html")
            return

        state_data = await state.get_data()
        company_name = state_data["company_name"]

        projects_db.change_company_attribute(company_name=company_name,
                                             attribute_name="comments_format",
                                             value=message.text)

        msg = await bot.send_message(text="Настройки успешно изменены!",
                                     chat_id=message.chat.id)

        await asyncio.sleep(2)

        await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)
        await bot.send_message(text=create_text(company_attributes=company_attributes),
                               chat_id=message.chat.id,
                               reply_markup=create_company_settings_markup(
                                   company_name=company_name,
                                   company_status=company_attributes[15]),
                               parse_mode="html",
                               disable_web_page_preview=True)
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в edit_collecting_period_message: %s", e)


@router.callback_query(EditCompanyAttributes.edit_collecting_links)
async def edit_collecting_links_callback(message: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        company_name = state_data["company_name"]

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)
        await bot.edit_message_text(text=create_text(company_attributes=company_attributes),
                                    chat_id=message.from_user.id,
                                    message_id=message.message.message_id,
                                    reply_markup=create_collect_comments_markup(
                                        company_name=company_name,
                                        comments_acc_existing=bool(company_attributes[13])),
                                    parse_mode="html",
                                    disable_web_page_preview=True)

        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в edit_collecting_links_callback: %s", e)


@router.message(EditCompanyAttributes.edit_collecting_links)
async def edit_collecting_links_message(message: types.Message, state: FSMContext, bot: Bot):
    try:
        # Проверка на корректность формата (примерная)
        if not (message.text.startswith("https")):
            await bot.send_message(text="Отправьте ссылку(и) в корректном формате!\n"
                                        "<b>Ссылка должна начинаться с 'https://'</b>",
                                   chat_id=message.chat.id,
                                   parse_mode="html")
            return

        state_data = await state.get_data()
        company_name = state_data["company_name"]

        projects_db.change_company_attribute(company_name=company_name,
                                             attribute_name="comments_format",
                                             value=message.text.replace(' ', '').replace('|', ' '))

        msg = await bot.send_message(text="Настройки успешно изменены!",
                                     chat_id=message.chat.id)

        await asyncio.sleep(2)

        await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)
        await bot.send_message(text=create_text(company_attributes=company_attributes),
                               chat_id=message.chat.id,
                               reply_markup=create_company_settings_markup(
                                   company_name=company_name,
                                   company_status=company_attributes[15]),
                               parse_mode="html",
                               disable_web_page_preview=True)
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в edit_collecting_links_message: %s", e)
