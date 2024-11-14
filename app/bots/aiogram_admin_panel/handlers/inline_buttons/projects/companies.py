import asyncio
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from app.bots.aiogram_admin_panel.keyboard.reply_keyboard.buttons import skip_action_markup, reply_back_markup, \
    request_chat_markup, create_bots_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_after_company_markup, \
    create_company_settings_markup, create_edit_dest_channels_markup, create_choose_events_markup, \
    create_collect_data_markup, create_back_to_settings_markup
from app.bots.aiogram_admin_panel.keyboard.inline_keyboard.buttons import create_accepting_delete_markup, \
    create_edit_company_markup
from app.bots.aiogram_admin_panel.state.state_init import GetCompanyAttributes, EditCompanyAttributes
from app.bots.aiogram_admin_panel.utils.create_message_text.create_company_info import create_text
from app.services.database.database_code import ProjectsDatabase, AccountsDatabase
from app.services.logs.logging import logger
from app.services.subprocess_station.subprocess_init import SubprocessStation

router = Router()

projects_db = ProjectsDatabase()
accounts_db = AccountsDatabase()

subprocess_station = SubprocessStation()


@router.callback_query(F.data.startswith("add_company"))
async def add_company(call: types.CallbackQuery | types.Message, state: FSMContext, bot: Bot):
    try:
        if isinstance(call, types.CallbackQuery):
            project_name = ''.join(call.data.split('_')[2:])
            await state.update_data(project_name=project_name)

            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        await bot.send_message(text="Введите имя компании пересылки:",
                               chat_id=call.from_user.id,
                               reply_markup=skip_action_markup)

        await state.set_state(GetCompanyAttributes.get_company_name)
    except Exception as e:
        logger.error("Возникла ошибка в add_company: %s", e)


@router.callback_query(F.data.startswith("choose_company"))
async def choose_company(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split("_")[2:])
        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)

        await bot.edit_message_text(text=create_text(company_attributes=company_attributes),
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_after_company_markup(
                                        project_name=company_attributes[2],
                                        company_name=company_attributes[1]),
                                    parse_mode="html",
                                    disable_web_page_preview=True)
    except Exception as e:
        logger.error("Возникла ошибка в choose_company: %s", e)


@router.callback_query(F.data.startswith("settings_company"))
async def settings_company(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        company_status = projects_db.get_company_attribute(attribute="company_status",
                                                           company_name=company_name)

        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_company_settings_markup(
                                                company_name=company_name,
                                                company_status=company_status
                                            ))
    except Exception as e:
        logger.error("Возникла ошибка в settings_company: %s", e)


@router.callback_query(F.data.startswith("launch_company"))
async def launch_company(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        collecting_way = projects_db.get_company_attribute(attribute="history",
                                                           company_name=company_name)
        if not collecting_way:
            await call.answer(text="Выберите режим парсинга!",
                              show_alert=True)
            return

        if collecting_way == "all":
            script_name = "collect_all.py"
        elif collecting_way.startswith("https"):
            script_name = "collect_by_links.py"
        else:
            script_name = "collect_for_period.py"

        projects_db.set_company_status(company_name=company_name,
                                       status="active")

        agent_account = projects_db.get_company_attribute(attribute="receiver_account",
                                                          company_name=company_name)

        subprocess_station.set_script_path(script_type="pyrogram",
                                           script_name=f"channel_scripts/{script_name}")
        subprocess_station.set_input_data(data=f"{agent_account}.session")
        subprocess_station.set_company_name(company=company_name)
        subprocess_station.run_script(script_name="channel_posts_collecting.py")

        await call.answer(text="Компания успешно запущена!",
                          show_alert=True)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_company_settings_markup(
                                                company_name=company_name,
                                                company_status="active"
                                            ))
    except Exception as e:
        logger.error("Возникла ошибка в launch_company: %s", e)


@router.callback_query(F.data.startswith("halt_company"))
async def halt_company(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        projects_db.annulling_all_company_statuses()

        await call.answer(text="Компания успешно остановлена!",
                          show_alert=True)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_company_settings_markup(
                                                company_name=company_name,
                                                company_status="inactive"
                                            ))
    except Exception as e:
        logger.error("Возникла ошибка в halt_company: %s", e)


@router.callback_query(F.data.startswith("rename_company"))
async def rename_company(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        await bot.send_message(text="Введите новое имя компании:",
                               chat_id=call.from_user.id,
                               reply_markup=reply_back_markup)

        await state.set_state(EditCompanyAttributes.edit_company_name)
        await state.update_data(old_company_name=company_name)
    except Exception as e:
        logger.error("Возникла ошибка в rename_company: %s", e)


@router.callback_query(F.data.startswith("edit_company"))
async def edit_company(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        parsing_regime = projects_db.get_company_attribute(attribute="parsing_regime",
                                                           company_name=company_name)

        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_edit_company_markup(
                                                company_name=company_name,
                                                parsing_regime=parsing_regime
                                            ))
    except Exception as e:
        logger.error("Возникла ошибка в rename_company: %s", e)


@router.callback_query(F.data.startswith("delete_company"))
async def delete_company(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[2:])

        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_accepting_delete_markup(name=company_name))
        await state.set_state(EditCompanyAttributes.delete_company)
    except Exception as e:
        logger.error("Возникла ошибка в delete_company: %s", e)


@router.callback_query(F.data.startswith("edit_dest_channels"))
async def edit_dest_channels(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[3:])

        recp_chat_ids = projects_db.get_company_attribute(
            attribute="recipient_chat_id",
            company_name=company_name)

        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_edit_dest_channels_markup(
                company_name=company_name,
                amount_of_channels=len(recp_chat_ids.split(' '))))
    except Exception as e:
        logger.error("Возникла ошибка в edit_dest_channels: %s", e)


@router.callback_query(F.data.startswith("add_recp_channel"))
async def add_recp_channel(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[3:])

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        await bot.send_message(text="Отправьте чат назначения:\n"
                                    "Важно, чтобы бот-секретарь был в роли админа в нём!",
                               chat_id=call.from_user.id, reply_markup=request_chat_markup)

        await state.set_state(EditCompanyAttributes.add_recipient_channel)
        await state.update_data(company_name=company_name)
    except Exception as e:
        logger.error("Возникла ошибка в add_recp_channel: %s", e)


@router.callback_query(F.data.startswith("del_recp_channel"))
async def del_recp_channel(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[3:])

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        await bot.send_message(text="Отправьте чат-источник для удаления:",
                               chat_id=call.from_user.id, reply_markup=request_chat_markup)

        await state.set_state(EditCompanyAttributes.delete_recipient_channel)
        await state.update_data(company_name=company_name)
    except Exception as e:
        logger.error("Возникла ошибка в del_recp_channel: %s", e)


@router.callback_query(F.data.startswith("edit_history_collecting"))
async def edit_history_collecting(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[3:])

        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_collect_data_markup(
                                                company_name=company_name,
                                                data_to_collect="history",
                                                comments_acc_existing=True  # just skip it(wrong way, i know)
                                            )
                                            )
    except Exception as e:
        logger.error("Вознилка ошибка в edit_history_collecting: %s", e)


@router.callback_query(F.data.startswith("edit_comments_collecting"))
async def edit_comments_collecting(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[3:])

        parsing_regime = projects_db.get_company_attribute(attribute="parsing_regime",
                                                           company_name=company_name)
        if parsing_regime == "refresh":
            await call.answer(text="У вас выбран режим прослушки!\nСоздайте новую компанию.",
                              show_alert=True)
            return

        comments_account = projects_db.get_company_attribute(attribute="comments_account",
                                                             company_name=company_name)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_collect_data_markup(
                                                company_name=company_name,
                                                data_to_collect="comments",
                                                comments_acc_existing=bool(comments_account)
                                            )
                                            )
    except Exception as e:
        logger.error("Возникла ошибка в edit_comments_collecting: %s", e)


@router.callback_query(F.data.startswith("collecting_way_all_history"))
async def collecting_way_all_comments(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[4:])

        projects_db.change_company_attribute(company_name=company_name,
                                             attribute_name="history",
                                             value="all")
        msg = await bot.edit_message_text(text="Настройки успешно изменены!",
                                          chat_id=call.from_user.id,
                                          message_id=call.message.message_id)

        await asyncio.sleep(2)

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)
        await bot.edit_message_text(text=create_text(company_attributes=company_attributes),
                                    chat_id=call.from_user.id,
                                    message_id=msg.message_id,
                                    reply_markup=create_edit_company_markup(company_name=company_name,
                                                                            parsing_regime="grabbing"),
                                    parse_mode="html",
                                    disable_web_page_preview=True)
    except Exception as e:
        logger.error("Возникла ошибка в collecting_way_all: %s", e)


@router.callback_query(F.data.startswith("collecting_way_all_comments"))
async def collecting_way_all_comments(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[4:])

        projects_db.change_company_attribute(company_name=company_name,
                                             attribute_name="comments_format",
                                             value="all")
        msg = await bot.edit_message_text(text="Настройки успешно изменены!",
                                          chat_id=call.from_user.id,
                                          message_id=call.message.message_id)

        await asyncio.sleep(2)

        company_attributes = projects_db.get_all_company_attributes(company_name=company_name)
        await bot.edit_message_text(text=create_text(company_attributes=company_attributes),
                                    chat_id=call.from_user.id,
                                    message_id=msg.message_id,
                                    reply_markup=create_edit_company_markup(company_name=company_name,
                                                                            parsing_regime="grabbing"),
                                    parse_mode="html",
                                    disable_web_page_preview=True)
    except Exception as e:
        logger.error("Возникла ошибка в collecting_way_all: %s", e)


@router.callback_query(F.data.startswith("collecting_way_period"))
async def collecting_way_period(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        call_data = call.data.split('_')
        data_to_collect = call_data[3]
        company_name = ''.join(call_data[4:])

        await bot.edit_message_text(text=call.message.text +
                                         "\n➖➖➖➖➖➖➖➖➖\n"
                                         "Отправьте период в формате <b>день.месяц.год - день.месяц.год</b>:",
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_back_to_settings_markup(company_name=company_name),
                                    parse_mode="html")

        await state.set_state(EditCompanyAttributes.edit_collecting_period)
        await state.update_data(company_name=company_name)
        await state.update_data(data_to_collect=data_to_collect)
    except Exception as e:
        logger.error("Возникла ошибка в collecting_way_period: %s", e)


@router.callback_query(F.data.startswith("collecting_way_links"))
async def collecting_way_links(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        call_data = call.data.split('_')
        data_to_collect = call_data[3]
        company_name = ''.join(call_data[4:])

        await bot.edit_message_text(text=call.message.text + "\n➖➖➖➖➖➖➖➖➖\n"
                                                             "Отправьте ссылку(ссылки) на пост.\n"
                                                             "В качестве разделителя используйте '|'",
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_back_to_settings_markup(company_name=company_name),
                                    parse_mode="html")

        await state.set_state(EditCompanyAttributes.edit_collecting_links)
        await state.update_data(company_name=company_name)
        await state.update_data(data_to_collect=data_to_collect)
    except Exception as e:
        logger.error("Возникла ошибка в collecting_way_links: %s", e)


@router.callback_query(F.data.startswith("add_comments_secretary"))
async def add_comments_secretary(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[3:])

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)

        usernames = accounts_db.get_all_accounts_usernames(task="comments")
        await bot.send_message(text="Выберите бота из предложенных в качестве секретаря для комментариев:",
                               chat_id=call.from_user.id,
                               reply_markup=create_bots_markup(
                                   account_usernames=usernames)
                               )

        await state.set_state(GetCompanyAttributes.get_comments_account)
        await state.update_data(company_name=company_name)
    except Exception as e:
        logger.error("Возникла ошибка в add_comments_secretary: %s", e)


@router.callback_query(F.data.startswith("edit_source_events"))
async def edit_source_events(call: types.CallbackQuery, bot: Bot):
    try:
        company_name = ''.join(call.data.split('_')[3:])

        parsing_regime = projects_db.get_company_attribute(attribute="parsing_regime",
                                                           company_name=company_name)
        if parsing_regime == "grabbing":
            await call.answer(text="У вас выбран формат 'Парсинг истории'."
                                   "\nСоздайте новую компанию!",
                              show_alert=True)
            return

        current_events = projects_db.get_company_attribute(attribute="company_events",
                                                           company_name=company_name).strip().split(' ')
        await bot.edit_message_text(text=call.message.text,
                                    chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=create_choose_events_markup(
                                        company_name=company_name,
                                        current_events=current_events)
                                    )
    except Exception as e:
        logger.error("Возникла ошибка в edit_source_events: %s", e)


@router.callback_query(F.data.startswith("choose_event"))
async def choose_event(call: types.CallbackQuery, bot: Bot):
    try:
        call_data = call.data.split('_')
        company_name = ''.join(call_data[3:])
        event = call_data[2]

        current_events = projects_db.change_company_event(company_name=company_name,
                                                          event=event).split(' ')
        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=create_choose_events_markup(
                                                company_name=company_name,
                                                current_events=current_events
                                            ))
    except Exception as e:
        logger.error("Возникла ошибка в choose_event: %s", e)
