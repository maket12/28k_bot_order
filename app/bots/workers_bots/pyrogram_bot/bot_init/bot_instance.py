from app.bots.workers_bots.pyrogram_bot.utils.client_from_json.get_data_from_json import create_client_from_json
from app.services.logs.logging import logger


def init_apps():
    try:
        app = create_client_from_json(json_file='leech')

        apps = (app,)
        return apps
    except Exception as e:
        logger.error(f"Ошибка во время работы приложения: {e}")
