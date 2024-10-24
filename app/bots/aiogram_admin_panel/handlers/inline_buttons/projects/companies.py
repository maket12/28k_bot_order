from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import skip_action_markup
from app.bots.aiogram_admin_panel.state.state_init import GetCompanyAttributes
from app.services.database.database_code import ProjectsDatabase
from app.services.logs.logging import logger

router = Router()

projects_db = ProjectsDatabase()


@router.callback_query(F.data == "add_company")
async def add_company(call: types.CallbackQuery | types.Message, state: FSMContext, bot: Bot):
    try:
        if isinstance(call, types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        await bot.send_message(text="Введите имя компании пересылки:",
                               chat_id=call.from_user.id,
                               reply_markup=skip_action_markup)

        await state.set_state(GetCompanyAttributes.get_company_name)
    except Exception as e:
        logger.error("Возникла ошибка в add_company: %s", e)


@router.callback_query(F.data.startswith("company"))
async def choose_company(call: types.CallbackQuery, bot: Bot):
    try:
        company_id = call.data.split("_")[1]
        company_attributes = projects_db.get_company_attributes(company_id=company_id)


    except Exception as e:
        logger.error("Возникла ошибка в choose_company: %s", e)

