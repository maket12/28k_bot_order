from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.utils.token import TokenValidationError


async def check_aiogram_connection(bot_token: str, proxy: str | None):
    try:
        async with AiohttpSession(proxy=proxy) as session:
            bot = Bot(token=bot_token, session=session)
            bot_data = await bot.get_me()
            await session.close()
            return bot_data.first_name, bot_data.username
    except TelegramUnauthorizedError:
        return 0
    except TokenValidationError:
        return 0
    except Exception as e:
        print(e)
