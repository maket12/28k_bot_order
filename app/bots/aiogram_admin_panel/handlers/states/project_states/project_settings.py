import asyncio
from aiogram import types, Router, Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_project_settings_markup
from app.bots.aiogram_admin_panel.state.state_init import GetProjectAttributes
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()

router = Router()


@router.message(GetProjectAttributes.change_project_name)
async def change_project_name(message: types.Message, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        old_name = state_data["old_name"]

        if message.text == "Назад":
            sent_msg = await bot.send_message(text=f"Возвращаемся в настройки проекта {old_name}...",
                                              chat_id=message.chat.id, reply_markup=ReplyKeyboardRemove())
            current_name = old_name
        else:
            projects_db.change_project_name(old_name=old_name, new_name=message.text)
            sent_msg = await bot.send_message(text="Название проекта успешно изменено!",
                                              chat_id=message.chat.id,
                                              reply_markup=ReplyKeyboardRemove())
            current_name = message.text

        await asyncio.sleep(2)

        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=sent_msg.message_id)
        await bot.send_message(text=f"Настройки проекта '{current_name}'",
                                    chat_id=message.from_user.id,
                                    reply_markup=create_project_settings_markup(
                                        project_name=current_name))
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в change_project_name: %s", e)
