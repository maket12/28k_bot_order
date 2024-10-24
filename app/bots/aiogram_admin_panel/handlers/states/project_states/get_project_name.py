import asyncio
from datetime import datetime
from aiogram import types, Router, Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.handlers.reply_buttons.projects import projects
from app.bots.aiogram_admin_panel.state.state_init import GetProjectAttributes
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.companies import add_company
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()

router = Router()


@router.message(GetProjectAttributes.get_project_name)
async def get_project_name(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if message.text == "Назад":
            await bot.send_message(text="Создание проекта отменено!",
                                   chat_id=message.chat.id,
                                   reply_markup=ReplyKeyboardRemove())
            await projects(message=message)
            await state.clear()
            return
        elif message.text == "Пропустить":
            project_name = datetime.now().strftime("%Y.%m.%d")
        else:
            project_name = message.text

        projects_db.add_project(name=project_name)

        sent_msg = await bot.send_message(text="Проект успешно создан!", chat_id=message.from_user.id,
                                          reply_to_message_id=message.message_id)
        await state.clear()
        await state.update_data(project_name=project_name)
        await asyncio.sleep(1.5)

        await bot.delete_message(chat_id=message.from_user.id, message_id=sent_msg.message_id)
        await add_company(call=message, state=state, bot=bot)
    except Exception as e:
        logger.error("Возникла ошибка в get_chat_id: %s", e)

