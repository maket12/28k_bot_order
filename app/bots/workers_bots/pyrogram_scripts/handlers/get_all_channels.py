from pyrogram import Client, types
from app.bots.workers_bots.pyrogram_scripts import aiogram_bot_uid
from bot.services.logs.logging import logger


async def get_all_channels(client: Client, message: types.Message):
    try:
        user_id = message.text.split("=")[1]
        print(message.chat.type)
        if str(message.chat.type) == "ChatType.BOT":
            channels_dict = {}
            dialogs = client.get_dialogs()
            async for dialog in dialogs:
                if str(dialog.chat.type) == "ChatType.CHANNEL":
                    channels_dict[dialog.chat.title] = dialog.chat.id
            # Отправляем боту готовый результат
            await client.send_message(chat_id=aiogram_bot_uid, text=f"channels={user_id}║{str(channels_dict)}")
    except Exception as e:
        logger.error("Возникла ошибка в start_editing_channel: %s", e)
