from aiogram import Router, types
from aiogram.filters import CommandStart
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import main_menu_markup
from app.services.logs.logging import logger

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    try:
        await message.answer(text="Добро пожаловать в главное меню бота!",
                             reply_markup=main_menu_markup)
    except Exception as e:
        logger.error("Возникла ошибка в start: %s", e)
