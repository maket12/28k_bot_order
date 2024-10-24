from app.config import bot_token
from app.bots.aiogram_admin_panel.aiogram_model import aiogram_bot_start

if __name__ == "__main__":
    aiogram_bot_start(bot_token=bot_token)
