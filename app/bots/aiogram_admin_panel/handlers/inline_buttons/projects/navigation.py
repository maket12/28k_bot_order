from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext

from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.companies import choose_company
from app.bots.aiogram_admin_panel.handlers.reply_buttons.projects import projects
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import build_companies_markup, build_projects_markup
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.projects import see_projects
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

router = Router()

projects_db = ProjectsDatabase()


@router.callback_query(F.data.startswith("navigation_projects"))
async def navigation_projects(call: types.CallbackQuery, bot: Bot):
    try:
        page = call.data.split('_')[-1]
        if page == "current":
            await call.answer(text="Это ваша текущая страница.", show_alert=True)
            return

        projects_list = projects_db.get_projects()

        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=build_projects_markup(projects=projects_list,
                                                                               current_page=int(page)))
    except Exception as e:
        logger.error("Возникла ошибка в navigation_projects: %s", e)


@router.callback_query(F.data == "back_to_projects_menu")
async def back_to_projects_menu(call: types.CallbackQuery, bot: Bot):
    try:
        await projects(message=call, bot=bot)
    except Exception as e:
        logger.error("Возникла ошибка в back_to_projects_menu: %s", e)


@router.callback_query(F.data.startswith("navigation_companies"))
async def navigation_companies(call: types.CallbackQuery, bot: Bot):
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
        logger.error("Возникла ошибка в navigation_companies: %s", e)


@router.callback_query(F.data == "back_to_projects")
async def back_to_projects(call: types.CallbackQuery, bot: Bot):
    try:
        await see_projects(call=call, bot=bot)
    except Exception as e:
        logger.error("Возникла ошибка в back_to_projects: %s", e)


@router.callback_query(F.data.startswith("back_to_settings_company"))
async def back_to_settings_company(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await choose_company(call=call, bot=bot)
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в back_to_settings_company: %s", e)
