import json
from pyrogram import Client
from app.services.logs.logging import logger


def create_client_from_json(json_file: str) -> Client:
    try:
        # """
        # Создает и возвращает клиент Pyrogram на основе данных из JSON-файла.
        #
        # :param json_file: Путь к JSON-файлу с данными аккаунта.
        # :return: Объект клиента Pyrogram.
        # """
        # # Загрузка данных из JSON-файла
        # with open(json_file, 'r') as file:
        #     data = json.load(file)
        #
        # # Извлечение данных из JSON-файла
        # session_file = data.get("session_file")
        # phone_number = data.get("phone")
        # app_id = data.get("app_id")
        # app_hash = data.get("app_hash")
        # app_version = data.get("app_version")
        # device_model = data.get("device")
        # system_version = data.get("sdk")
        # lang_code = data.get("lang_code")
        # two_fa_password = data.get("twoFA")
        # ipv6 = data.get("ipv6")
        # proxy = data.get("proxy")
        #
        # # Прокси
        # if proxy:
        #     proxy_dict = {
        #         "hostname": proxy[1],
        #         "port": proxy[2],
        #         "username": proxy[4] if len(proxy) > 4 else None,
        #         "password": proxy[5] if len(proxy) > 5 else None,
        #     }
        # else:
        #     proxy_dict = None

        # Создание клиента Pyrogram
        client = Client(
            f"sessions/{json_file}",
            api_id=25136287,
            api_hash="8fd85eac818848998b1886d0abd7765c",
            phone_number="+7 925 767 3299"
        )

        return client
    # except FileNotFoundError as e:
    #     logger.error(f"Файл не найден: {e}")
    except Exception as e:
        logger.error(f"Произошла ошибка при создании клиента: {e}")
    return
