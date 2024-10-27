import asyncio
from aiogram import types, Router, Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_project_settings_markup, \
    build_companies_markup
from app.bots.aiogram_admin_panel.state.state_init import GetCompanyAttributes
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

projects_db = ProjectsDatabase()

router = Router()


@router.callback_query(GetCompanyAttributes.delete_company)
async def delete_company(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        project_name = state_data["project_name"]
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

        await asyncio.sleep(1.5)

        all_companies = projects_db.get_companies(project_name=project_name)

        await bot.edit_message_text(text=f"Вы перешли в меню проекта {project_name}.",
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=build_companies_markup(
                                        companies=all_companies,
                                        project_name=project_name, current_page=1
                                    )
                                    )
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в delete_company: %s", e)
