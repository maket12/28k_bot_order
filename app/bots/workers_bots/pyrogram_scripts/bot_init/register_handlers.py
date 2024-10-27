from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
# from app.bots.pyrogram_scripts.handlers.get_all_channels import get_all_channels
from app.bots.workers_bots.pyrogram_scripts.handlers.process_editing import process_editing_channel


def register_handlers(app: Client):
    # app.add_handler(MessageHandler(get_all_channels, filters.regex(r"^/get_channels=.*")))

    app.add_handler(MessageHandler(process_editing_channel, filters.channel))
    return app

