import logging
import colorlog


# Форматтер для цветного консольного вывода
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

# Создание обработчика файла
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s [line:%(lineno)d]')


# Настройка логгера
logger = colorlog.getLogger()
logger.setLevel(logging.DEBUG)

# Добавление цветного обработчика и обработчика файла
console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)
logger.addHandler(console_handler)


logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("aiogram").setLevel(logging.ERROR)
logging.getLogger('sqlite3').setLevel(logging.ERROR)
logging.getLogger('pyrogram').setLevel(logging.ERROR)
