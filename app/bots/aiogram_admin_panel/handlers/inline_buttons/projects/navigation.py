from aiogram import Router, F, types, Bot
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import build_companies_markup
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.projects import see_projects
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

router = Router()

projects_db = ProjectsDatabase()


@router.callback_query(F.data.startswith("navigation_project"))
async def project_navigation(call: types.CallbackQuery, bot: Bot):
    try:
        page = call.data.split('_')[-1]
        if page == "current":
            await call.answer(text="Это ваша текущая страница.", show_alert=True)
            return

        project_name = call.message.text[call.message.text.find('проекта ') + 8:-1]
        companies = projects_db.get_companies(project_name=project_name)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=build_companies_markup(
                                                companies=companies,
                                                project_name=project_name,
                                                current_page=int(page)
                                            ))
    except Exception as e:
        logger.error("Возникла ошибка в project_navigation: %s", e)


@router.callback_query(F.data == "back_to_projects")
async def back_to_projects(call: types.CallbackQuery, bot: Bot):
    try:
        await see_projects(call=call, bot=bot)
    except Exception as e:
        logger.error("Возникла ошибка в back_to_projects: %s", e)
