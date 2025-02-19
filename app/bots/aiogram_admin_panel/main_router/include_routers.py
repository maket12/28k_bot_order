from aiogram import Dispatcher
from app.bots.aiogram_admin_panel.handlers.commands.start import router as start_router
from app.bots.aiogram_admin_panel.handlers.reply_buttons.accounts import router as reply_accounts_router
from app.bots.aiogram_admin_panel.handlers.reply_buttons.projects import router as reply_projects_router
from app.bots.aiogram_admin_panel.handlers.inline_buttons.accounts.accounts import router as inline_accounts_router
from app.bots.aiogram_admin_panel.handlers.states.account_states.get_user import router as get_user_router
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.projects import router as projects_router
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.companies import router as companies_router
from app.bots.aiogram_admin_panel.handlers.states.project_states.get_project import router as get_project_name_router
from app.bots.aiogram_admin_panel.handlers.states.project_states.get_company import router as get_company_router
from app.bots.aiogram_admin_panel.handlers.inline_buttons.accounts.navigation import router as navigation_router
from app.bots.aiogram_admin_panel.handlers.states.account_states.get_bot import router as get_bot_router
from app.bots.aiogram_admin_panel.handlers.inline_buttons.projects.navigation import router as projects_navigation_router
from app.bots.aiogram_admin_panel.handlers.states.project_states.project_settings import router as change_project_name_router
from app.bots.aiogram_admin_panel.handlers.states.project_states.company_settings import router as company_settings_router
# from app.bots.aiogram_admin_panel.handlers.
# from app.bots.aiogram_admin_panel.handlers.DD


def include_all_routers(dp: Dispatcher):
    routers = [start_router, reply_accounts_router, reply_projects_router,
               inline_accounts_router, get_user_router, projects_router, companies_router,
               get_project_name_router, get_company_router, navigation_router,
               get_bot_router, projects_navigation_router, change_project_name_router,
               company_settings_router]

    dp.include_routers(*routers)
