import asyncio
from aiogram import types, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_accounts_markup
from app.bots.aiogram_admin_panel.state.state_init import GetUser
from app.bots.aiogram_admin_panel.handlers.inline_buttons.accounts.accounts import accounts_users, accounts_managers, accounts_team_leads
from app.services.database.database_code import AccountsDatabase
from app.services.logs.logging import logger

accounts_db = AccountsDatabase()

router = Router()


@router.message(GetUser.get_chat_id)
async def get_chat_id(message: types.Message | types.Contact, state: FSMContext, bot: Bot):
    try:
        state_data = await state.get_data()
        account_role = state_data["acc_type"]

        if message.text:
            if message.text.isdigit():
                user_id = int(message.text)
            elif message.text == "Назад":
                await bot.send_message(text="Возвращение в меню...",
                                       chat_id=message.from_user.id,
                                       reply_markup=ReplyKeyboardRemove())

                await asyncio.sleep(3)

                if account_role == "manager":
                    accounts_ids = accounts_db.get_all_accounts_ids(account_type="users",
                                                                    account_role="manager")
                    await bot.send_message(
                        text="Вы перешли в раздел 'Менеджеры'\n"
                             "Для навигации используйте соответствующие кнопки ниже:",
                        chat_id=message.from_user.id,
                        reply_markup=create_accounts_markup(
                            accounts_ids=accounts_ids,
                            account_type="users",
                            account_role="manager"
                        )
                    )
                else:
                    accounts_ids = accounts_db.get_all_accounts_ids(account_type="users",
                                                                    account_role="team-lead")
                    await bot.send_message(
                        text="Вы перешли в раздел 'Тим-лиды'\n"
                             "Для навигации используйте соответствующие кнопки ниже:",
                        chat_id=message.from_user.id,
                        reply_markup=create_accounts_markup(
                            accounts_ids=accounts_ids,
                            account_type="users",
                            account_role="team-lead"
                        )
                    )
                await state.clear()
                return
            else:
                await message.answer(text="Отправьте chat_id либо контакт!")
                return
        elif message.user_shared:
            user_id = message.user_shared.user_id
        else:
            await message.answer(text="Отправьте chat_id либо контакт!")
            return

        try:
            chat_object = await bot.get_chat(chat_id=user_id)
            username = chat_object.username
        except TelegramBadRequest:
            logger.warning("Попытка добавить пользователя, который не контактировал с ботом ранее!")
            await bot.send_message(text="Данный пользователь не контактировал с ботом.\n"
                                        "Добавление невозможно!",
                                   chat_id=message.from_user.id)

            await asyncio.sleep(3)

            await accounts_users(call=message, bot=bot)
            await state.clear()
            return

        if account_role == "manager":
            head_user_id = message.from_user.id
        else:
            head_user_id = None

        res = accounts_db.add_user_account(user_id=user_id, username=username,
                                           role=account_role, head_user_id=head_user_id)
        if not res:
            await message.answer(text="Данный пользователь уже существует в базе!\n"
                                      "Добавление невозможно!")
        else:
            await message.answer(text=f"Аккаунт {user_id} успешно добавлен как {account_role}",
                                 reply_markup=ReplyKeyboardRemove())
        await accounts_users(call=message, bot=bot)
        await state.clear()
    except Exception as e:
        logger.error("Возникла ошибка в get_chat_id: %s", e)

