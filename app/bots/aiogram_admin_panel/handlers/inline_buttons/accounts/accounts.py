from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import accounts_users_markup, proxy_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_accounts_markup, create_acc_settings_markup, create_acc_pre_delete_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_acc_delete_markup, create_back_to_spec_acc_button, bot_task_markup
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import request_contact_markup
from app.bots.aiogram_admin_panel.state.state_init import GetUser, GetBot
from app.bots.aiogram_admin_panel.utils.create_message_text.create_account_info import create_text
from app.services.database.database_code import AccountsDatabase, ProjectsDatabase
from app.services.logs.logging import logger

router = Router()

accounts_db = AccountsDatabase()

projects_db = ProjectsDatabase()


@router.callback_query(F.data == "accounts_users")
async def accounts_users(call: types.CallbackQuery | types.Message | types.Contact, bot: Bot):
    try:
        if isinstance(call, types.CallbackQuery):
            await bot.edit_message_text(
                text="Вы перешли в раздел 'Пользовательские аккаунты'\n"
                     "Для навигации используйте соответствующие кнопки:",
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                reply_markup=accounts_users_markup
                )
        else:
            await bot.send_message(
                text="Вы перешли в раздел 'Пользовательские аккаунты'\n"
                     "Для навигации используйте соответствующие кнопки:",
                chat_id=call.from_user.id,
                reply_markup=accounts_users_markup
                )
    except Exception as e:
        logger.error("Возникла ошибка в accounts_users: %s", e)


@router.callback_query(F.data == "accounts_bots")
async def accounts_bots(call: types.CallbackQuery | types.Message, bot: Bot):
    try:
        if isinstance(call, types.CallbackQuery):
            await bot.edit_message_text(
                text="Вы перешли в раздел 'Аккаунты-расходники'\n"
                     "Для навигации используйте соответствующие кнопки:",
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                reply_markup=bot_task_markup
            )
        else:
            await bot.send_message(
                text="Вы перешли в раздел 'Аккаунты-расходники'\n"
                     "Для навигации используйте соответствующие кнопки:",
                chat_id=call.from_user.id,
                reply_markup=bot_task_markup
            )
    except Exception as e:
        logger.error("Возникла ошибка в accounts_bots: %s", e)


@router.callback_query(F.data == "accounts_team_leads")
async def accounts_team_leads(call: types.CallbackQuery, bot: Bot):
    try:
        accounts_ids = accounts_db.get_all_accounts_ids(account_type="users",
                                                        account_role="team-lead")
        await bot.edit_message_text(
            text="Вы перешли в раздел 'Тим-лиды'\n"
                 "Для навигации используйте соответствующие кнопки ниже:",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_accounts_markup(
                accounts_ids=accounts_ids,
                account_type="users",
                account_role="team-lead"
            )
        )
    except Exception as e:
        logger.error("Возникла ошибка в accounts_team_leads: %s", e)


@router.callback_query(F.data == "accounts_managers")
async def accounts_managers(call: types.CallbackQuery, bot: Bot):
    try:
        accounts_ids = accounts_db.get_all_accounts_ids(account_type="users",
                                                        account_role="manager")
        await bot.edit_message_text(
            text="Вы перешли в раздел 'Менеджеры'\n"
                 "Для навигации используйте соответствующие кнопки ниже:",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_accounts_markup(
                accounts_ids=accounts_ids,
                account_type="users",
                account_role="manager"
            )
        )
    except Exception as e:
        logger.error("Возникла ошибка в accounts_managers: %s", e)


@router.callback_query(F.data == "bot_task_posts")
async def accounts_secretary_posts(call: types.CallbackQuery, bot: Bot):
    try:
        accounts_ids = accounts_db.get_all_accounts_ids(account_type="bots",
                                                        account_role="posts")
        await bot.edit_message_text(
            text=f"Вы перешли в раздел 'Секретари для постов'\n"
                 "Для навигации используйте соответствующие кнопки ниже:",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_accounts_markup(
                accounts_ids=accounts_ids,
                account_type="bots",
                account_role="posts"
            )
        )
    except Exception as e:
        logger.error("Возникла ошибка в accounts_secretary_posts: %s", e)


@router.callback_query(F.data == "bot_task_comments")
async def accounts_secretary_comments(call: types.CallbackQuery, bot: Bot):
    try:
        accounts_ids = accounts_db.get_all_accounts_ids(account_type="bots",
                                                        account_role="comments")
        await bot.edit_message_text(
            text=f"Вы перешли в раздел 'Секретари для комментариев'\n"
                 "Для навигации используйте соответствующие кнопки ниже:",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_accounts_markup(
                accounts_ids=accounts_ids,
                account_type="bots",
                account_role="comments"
            )
        )
    except Exception as e:
        logger.error("Возникла ошибка в accounts_secretary_comments: %s", e)


@router.callback_query(F.data == "bot_task_agent")
async def accounts_agent_bot(call: types.CallbackQuery, bot: Bot):
    try:
        accounts_ids = accounts_db.get_all_accounts_ids(account_type="bots",
                                                        account_role="agent")
        await bot.edit_message_text(
            text=f"Вы перешли в раздел 'Аккаунты-агенты'\n"
                 "Для навигации используйте соответствующие кнопки ниже:",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_accounts_markup(
                accounts_ids=accounts_ids,
                account_type="bots",
                account_role="agent"
            )
        )
    except Exception as e:
        logger.error("Возникла ошибка в accounts_agent_bot: %s", e)


@router.callback_query(F.data.startswith("add_account"))
async def add_account(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        account_type, account_role = call.data.split('_')[-2], call.data.split('_')[-1]

        if account_type == "users":
            await bot.delete_message(chat_id=call.from_user.id,
                                     message_id=call.message.message_id)
            await bot.send_message(
                text="Отправьте пользователя, которому необходимо выдать доступ.\n"
                     "Нажмите на кнопку 'Отправить контакт' или отправьте его chat_id:",
                chat_id=call.from_user.id,
                reply_markup=request_contact_markup
            )
            await state.set_state(GetUser.get_chat_id)
            await state.update_data(acc_type=account_role)
        else:
            await bot.edit_message_text(text="Теперь выберите тип прокси:",
                                        chat_id=call.from_user.id,
                                        message_id=call.message.message_id,
                                        reply_markup=proxy_markup)
            await state.set_state(GetBot.get_proxy_type)
            await state.update_data(bot_task=account_role)
    except Exception as e:
        logger.error("Возникла ошибка в add_account: %s", e)


@router.callback_query(F.data.startswith("account_info"))
async def account_info(call: types.CallbackQuery, bot: Bot):
    try:
        account_type = call.data.split('_')[-2]
        account_id = call.data.split('_')[-1]
        acc_info = accounts_db.get_account_info(account_type=account_type, account_id=int(account_id))

        counters = [0, 0, 0]

        if account_type == "users":
            acc_role = acc_info[3]
            if acc_info[3] == "team-lead":
                counters[0], counters[1] = projects_db.count_all()
                counters[2] = accounts_db.count_managers_by_head(account_chat_id=acc_info[1])
        else:
            acc_role = acc_info[1]

        msg_text = create_text(account_type=account_type,
                               acc_info=acc_info,
                               counters=counters)
        await bot.edit_message_text(text=msg_text, chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_acc_settings_markup(account_type=account_type,
                                                                            account_id=int(account_id),
                                                                            account_role=acc_role))
    except Exception as e:
        logger.error("Возникла ошибка в account_info: %s", e)


@router.callback_query(F.data.startswith("account_settings"))
async def account_settings(call: types.CallbackQuery, bot: Bot):
    try:
        account_type, account_role, account_id = call.data.split('_')[2:]

        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_acc_pre_delete_markup(account_type=account_type,
                                                      account_id=account_id)
        )
    except Exception as e:
        logger.error("Возникла ошибка в account_settings: %s", e)


@router.callback_query(F.data.startswith("pre_delete_account"))
async def pre_delete_account(call: types.CallbackQuery, bot: Bot):
    try:
        data = call.data.split('_')
        account_type = data[-2]
        account_id = data[-1]

        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_acc_delete_markup(account_type=account_type,
                                                  account_id=int(account_id))
        )
    except Exception as e:
        logger.error("Возникла ошибка в pre_delete_account: %s", e)


@router.callback_query(F.data.startswith("delete_account"))
async def delete_account(call: types.CallbackQuery, bot: Bot):
    try:
        data = call.data.split('_')
        account_type = data[-2]
        account_id = int(data[-1])

        accounts_db.delete_account(account_type=account_type, account_id=account_id)

        await call.answer(text="Аккаунт удалён успешно!", show_alert=True)

        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_back_to_spec_acc_button(account_type=account_type)
        )
    except Exception as e:
        logger.error("Возникла ошибка в delete_account: %s", e)



