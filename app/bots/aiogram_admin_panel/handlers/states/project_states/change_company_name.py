import asyncio
from aiogram import types, Router, Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_company_settings_markup
from app.bots.aiogram_admin_panel.state.state_init import GetCompanyAttributes
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()

router = Router()


@router.message(GetCompanyAttributes.change_company_name)
async def change_company_name(message: types.Message, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        old_name = state_data["old_company_name"]
        company_attributes = projects_db.get_company_attributes(company_name=old_name)

        if message.text == "Назад":
            current_name = old_name
            msg = await bot.send_message(text="Возвращаемся к компании...",
                                         chat_id=message.chat.id,
                                         reply_markup=ReplyKeyboardRemove())
        else:
            current_name = message.text
            projects_db.change_company_name(old_name=old_name, new_name=current_name)
            msg = await bot.send_message(text="Название компании успешно изменено!",
                                         chat_id=message.chat.id,
                                         reply_markup=ReplyKeyboardRemove())

        await asyncio.sleep(1.5)
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=msg.message_id)
        await bot.send_message(text=f"Проект: {company_attributes[2]}\n"
                                     f"Компания: {current_name}\n"
                                     f"Формат: {company_attributes[3]}\n"
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
                                    chat_id=message.chat.id,
                                    reply_markup=create_company_settings_markup(
                                        company_name=company_attributes[1],
                                        project_name=company_attributes[2],
                                    ))
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в change_company_name: %s", e)
