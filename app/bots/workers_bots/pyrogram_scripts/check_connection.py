from pyrogram import Client, types
from pyrogram.errors import SessionPasswordNeeded
from app.services.logs.logging import logger


async def check_pyrogram_connection(phone_number: str, api_id: str, api_hash: str, proxy: str):
    try:
        app = Client(name=phone_number,
                     api_id=api_id,
                     api_hash=api_hash,
                     phone_number=phone_number)
        await app.connect()
        sent_code_info = await app.send_code(phone_number=phone_number)
        return app, sent_code_info
    except Exception as e:
        logger.error("Возникла ошибка в инициализации pyrogram клиента: ", e)
        return False


async def check_pyrogram_code(app: Client, auth_code: str, code_info: types.SentCode):
    try:
        await app.sign_in(phone_number=app.phone_number, phone_code=auth_code,
                          phone_code_hash=code_info.phone_code_hash)
        info = await app.get_me()
        return info.first_name, info.username
    except SessionPasswordNeeded:
        return "password needed", app
    except Exception as e:
        logger.error("Возникла ошибка в check_pyrogram_code:", e)
        return False
