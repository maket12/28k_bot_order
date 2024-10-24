from aiogram import Router, F, types, Bot
from app.bots.aiogram_admin_panel.handlers.inline_buttons.accounts.accounts import accounts_users, accounts_bots, account_info
from app.bots.aiogram_admin_panel.handlers.inline_buttons.accounts.accounts import accounts_managers, accounts_team_leads
from app.bots.aiogram_admin_panel.handlers.reply_buttons.accounts import accounts
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import main_menu_markup
from app.services.logs.logging import logger

router = Router()


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_menu(call: types.CallbackQuery, bot: Bot):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(text="Добро пожаловать в главное меню бота!",
                               chat_id=call.from_user.id, reply_markup=main_menu_markup)
    except Exception as e:
        logger.error("Возникла ошибка в back_to_menu: %s", e)


@router.callback_query(F.data.startswith("back_to_accounts"))
async def back_to_accounts(call: types.CallbackQuery, bot: Bot):
    try:
        value = call.data.split('_')[-1]
        if value == "main":
            await accounts(message=call, bot=bot)
        elif value == "users":
            await accounts_users(call=call, bot=bot)
        elif value == "team-lead":
            await accounts_team_leads(call=call, bot=bot)
        elif value == "manager":
            await accounts_managers(call=call, bot=bot)
        else:
            await accounts_bots(call=call, bot=bot)
    except Exception as e:
        logger.error("Возникла ошибка в back_to_accounts_main: %s", e)


@router.callback_query(F.data.startswith("back_to_spec_account"))
async def back_to_spec_account(call: types.CallbackQuery, bot: Bot):
    try:
        await account_info(call=call, bot=bot)
    except Exception as e:
        logger.error("Возникла ошибка в back_to_spec_account: %s", e)
