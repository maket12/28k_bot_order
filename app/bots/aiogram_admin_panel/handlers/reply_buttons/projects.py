from aiogram import Router, types, F
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import projects_main_markup
from app.services.logs.logging import logger

router = Router()


@router.message(F.text == "📊Проекты📊")
async def projects(message: types.Message):
    try:
        await message.answer(text="Выберите необходимый раздел меню '📊Проекты📊':",
                             reply_markup=projects_main_markup)
    except Exception as e:
        logger.error("Возникла ошибка в accounts: %s", e)
