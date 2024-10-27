from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import skip_action_markup, reply_back_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_after_company_markup, create_company_settings_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_accepting_delete_markup
from app.bots.aiogram_admin_panel.state.state_init import GetCompanyAttributes
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

router = Router()

projects_db = ProjectsDatabase()


@router.callback_query(F.data == "add_company")
async def add_company(call: types.CallbackQuery | types.Message, state: FSMContext, bot: Bot):
    try:
        if isinstance(call, types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        await bot.send_message(text="Введите имя компании пересылки:",
                               chat_id=call.from_user.id,
                               reply_markup=skip_action_markup)

        await state.set_state(GetCompanyAttributes.get_company_name)
    except Exception as e:
        logger.error("Возникла ошибка в add_company: %s", e)


@router.callback_query(F.data.startswith("choose_company"))
async def choose_company(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split("_")[2:])
        company_attributes = projects_db.get_company_attributes(company_name=company_name)
        if company_attributes[3] == "grabbing":
            parsing_regime = "Парсинг истории чата"
        else:
            parsing_regime = "Прослушка чата"
        await bot.edit_message_text(text=f"Проект: {company_attributes[2]}\n"
                                         f"Компания: {company_attributes[1]}\n"
                                         f"Формат: {parsing_regime}\n"
                                         f"Агент: {company_attributes[4]}\n"
                                         f"Отправитель: {company_attributes[5]}\n"
                                         f"Источник: {company_attributes[7]}\n"
                                         f"ID источника: {company_attributes[6]}\n"
                                         f"Назначение: {company_attributes[9]}\n"
                                         f"ID назначения: {company_attributes[8]}\n"
                                         f"Парсинг: \n"
                                         f"Обсуждения: \n"
                                         f"Секретарь для комментариев: \n"
                                         f"Личка: \n"
                                         f"Обсуждение: ",
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_after_company_markup(
                                        project_name=company_attributes[2],
                                        company_name=company_attributes[1]
                                    ))
    except Exception as e:
        logger.error("Возникла ошибка в choose_company: %s", e)


@router.callback_query(F.data.startswith("settings_company"))
async def settings_company(call: types.CallbackQuery, bot: Bot):
    try:
        msg_text = call.message.text
        company_name = ''.join(call.data.split('_')[2:])
        project_name = msg_text[msg_text.find(' '):msg_text.find('\n')]

        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_company_settings_markup(
                                                company_name=company_name,
                                                project_name=project_name
                                            ))
    except Exception as e:
        logger.error("Возникла ошибка в settings_company: %s", e)


@router.callback_query(F.data.startswith("rename_company"))
async def rename_company(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        await bot.send_message(text="Введите новое имя компании:",
                               chat_id=call.from_user.id,
                               reply_markup=reply_back_markup)

        await state.set_state(GetCompanyAttributes.change_company_name)
        await state.update_data(old_company_name=company_name)
    except Exception as e:
        logger.error("Возникла ошибка в rename_company: %s", e)


@router.callback_query(F.data.startswith("delete_company"))
async def delete_company(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        msg_text = call.message.text
        company_name = ''.join(call.data.split('_')[2:])
        project_name = msg_text[msg_text.find(' '):msg_text.find('\n')]

        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_accepting_delete_markup(name=company_name))
        await state.set_state(GetCompanyAttributes.delete_company)
        logger.warning(f"Имя проекта: {project_name}")
        await state.update_data(project_name=project_name)
    except Exception as e:
        logger.error("Возникла ошибка в delete_company: %s", e)
