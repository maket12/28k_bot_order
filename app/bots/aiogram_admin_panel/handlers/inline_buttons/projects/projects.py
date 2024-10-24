import asyncio
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_projects_markup, build_companies_markup, create_project_settings_markup
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import skip_action_markup
from app.bots.aiogram_admin_panel.state.state_init import GetProjectAttributes
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

router = Router()

projects_db = ProjectsDatabase()


@router.callback_query(F.data == "add_project")
async def add_project(call: types.CallbackQuery | types.Message, state: FSMContext, bot: Bot):
    try:
        if isinstance(call, types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id,
                                     message_id=call.message.message_id)
        else:
            sent_msg = await bot.send_message(text="Возвращаемся к созданию проекта...",
                                              chat_id=call.from_user.id)
            await asyncio.sleep(3)
            await bot.delete_message(chat_id=call.from_user.id, message_id=sent_msg.message_id)

        await bot.send_message(chat_id=call.from_user.id,
                               text="Хорошо, введите название проекта:",
                               reply_markup=skip_action_markup)
        await state.set_state(GetProjectAttributes.get_project_name)
    except Exception as e:
        logger.error("Возникла ошибка в add_project: %s", e)


@router.callback_query(F.data.startswith("choose_project"))
async def choose_project(call: types.CallbackQuery, bot: Bot):
    try:
        project_name = ''.join(call.data.split('_')[-1])
        all_companies = projects_db.get_companies(project_name=project_name)
        await bot.edit_message_text(text=f"Вы перешли в меню проекта {project_name}.",
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=build_companies_markup(
                                        companies=all_companies,
                                        project_name=project_name, current_page=1
                                        )
                                    )
    except Exception as e:
        logger.error("Возникла ошибка в choose_project: %s", e)


@router.callback_query(F.data == "see_projects")
async def see_projects(call: types.CallbackQuery, bot: Bot):
    try:
        projects = projects_db.get_projects()

        if not projects:
            msg_text = "На данный момент в этом проекте не создано ни одной компании!"
        else:
            msg_text = "Выберите нужный проект:"

        await bot.edit_message_text(text=msg_text, chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_projects_markup(projects=projects))
    except Exception as e:
        logger.error("Возникла ошибка в see_projects: %s", e)


@router.callback_query(F.data.startswith("settings_project"))
async def settings_project(call: types.CallbackQuery, bot: Bot):
    try:
        project_name = ''.join(call.data.split('_')[2:])
        await bot.edit_message_text(text=f"Настройки проекта '{project_name}'",
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_project_settings_markup(project_name=project_name))
    except Exception as e:
        logger.error("Возникла ошибка в settings_project: %s", e)


@router.callback_query(F.data.startswith("delete_project"))
async def delete_project(call: types.CallbackQuery, bot: Bot):
    try:
        project_name = ''.join(call.data.split('_')[2:])
    except Exception as e:
        logger.error("Возникла ошибка в delete_project: %s", e)
