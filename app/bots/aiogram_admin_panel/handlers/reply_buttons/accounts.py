from aiogram import Router, types, F, Bot
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import accounts_main_markup
from app.services.logs.logging import logger

router = Router()


@router.message(F.text == "👤Аккаунты👤")
async def accounts(message: types.Message | types.CallbackQuery, bot: Bot):
    try:
        if isinstance(message, types.Message):
            await message.answer(text="Вы выбрали раздел '👤Аккаунты👤'\n"
                                      "Для перемещения используйте соответствующие кнопки\n"
                                      "Выберите тип аккаунта:",
                                 reply_markup=accounts_main_markup)
        else:
            await bot.edit_message_text(
                text="Вы выбрали раздел '👤Аккаунты👤'\n"
                     "Для перемещения используйте соответствующие кнопки\n"
                     "Выберите тип аккаунта:",
                chat_id=message.from_user.id, message_id=message.message.message_id,
                reply_markup=accounts_main_markup
            )
    except Exception as e:
        logger.error("Возникла ошибка в accounts: %s", e)
