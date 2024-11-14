import sqlite3
import os
from app.services.logs.logging import logger


class AccountsDatabase:
    def __init__(self, db_file="files/accounts_database.db"):
        # Получаем абсолютный путь к файлу базы данных относительно этого файла
        base_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_path = os.path.join(base_dir, db_file)

        # Получаем директорию, в которой будет храниться файл базы данных
        db_directory = os.path.dirname(absolute_path)

        # Проверяем, существует ли папка для базы данных
        if not os.path.exists(db_directory):
            # Создаем папку, если она не существует
            os.makedirs(db_directory)

        # Теперь создаем файл базы данных (если он не существует)
        if not os.path.isfile(absolute_path):
            with open(absolute_path, 'w'):  # Создаём файл, если он не существует
                pass

        self.connection = sqlite3.connect(absolute_path)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        with self.connection:
            self.cursor.execute('CREATE TABLE IF NOT EXISTS "users" ('
                                '"id" INTEGER PRIMARY KEY,'
                                '"user_id" INTEGER UNIQUE,'
                                '"username" TEXT,'
                                '"role" TEXT,'
                                '"head_user_id" INTEGER)')

            self.cursor.execute('CREATE TABLE IF NOT EXISTS "bots" ('
                                '"id" INTEGER PRIMARY KEY,'
                                '"role" TEXT,'
                                '"proxy" TEXT,'
                                '"bot_token" TEXT,'
                                '"phone_number" TEXT,'  # only for aiogram_admin_panel
                                '"api_id" TEXT,'  # only for pyrogram bot
                                '"api_hash" TEXT,'  # only for pyrogram bot
                                '"bot_name" TEXT,'
                                '"bot_username" TEXT,'
                                '"status" TEXT DEFAULT "inactive")')

    def add_user_account(self, user_id: int, username: str, role: str, head_user_id: int):
        with self.connection:
            try:
                checker = self.cursor.execute('SELECT COUNT(1) FROM "users" WHERE "user_id" = ?',
                                              (user_id,)).fetchone()[0]
                if not checker:
                    return self.cursor.execute('INSERT INTO "users" ("user_id", "username", '
                                               '"role", "head_user_id") '
                                               'VALUES (?, ?, ?, ?)',
                                               (user_id, username, role, head_user_id))
                else:
                    logger.warning(f"Попытка добавить уже существующего в БД пользователя: {user_id}")
                    return False
            except Exception as e:
                logger.warning(f"Возникла ошибка при попытке добавить пользователя в БД: ", e)
                return False

    def add_bot_account(self, values: list):
        with self.connection:
            return self.cursor.execute('INSERT INTO "bots" ("role", "proxy", '
                                       '"bot_token", "phone_number", "api_id", '
                                       '"api_hash", "bot_name", "bot_username") '
                                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                       values)

    def delete_account(self, account_type: str, account_id: int):
        with self.connection:
            return self.cursor.execute(f'DELETE FROM "{account_type}" WHERE "id" = ?',
                                       (account_id,))

    def get_all_accounts_ids(self, account_type: str, account_role: str):  # means table name
        with self.connection:
            return self.cursor.execute(f'SELECT "id" FROM "{account_type}" WHERE "role" = ?',
                                       (account_role,)).fetchall()

    def get_all_accounts_usernames(self, task=None):  # for bots
        with self.connection:
            if not task:
                return self.cursor.execute('SELECT "bot_username" FROM "bots"').fetchall()
            else:
                return self.cursor.execute('SELECT "bot_username" FROM "bots" WHERE "role" = ?',
                                           (task,)).fetchall()

    def get_account_info(self, account_type: str, account_id: int):
        with self.connection:
            return self.cursor.execute(f'SELECT * FROM "{account_type}" WHERE "id" = ?',
                                       (account_id,)).fetchone()

    def count_managers_by_head(self, account_chat_id: int):
        with self.connection:
            return self.cursor.execute('SELECT COUNT(*) FROM "users" WHERE "head_user_id" = ?',
                                       (account_chat_id,)).fetchone()[0]

    def get_attribute_by_username(self, attribute: str, username: str):
        with self.connection:
            return self.cursor.execute(f'SELECT "{attribute}" FROM "bots" WHERE "bot_username" = ?',
                                       (username,)).fetchone()[0]

    def get_username_by_phone(self, phone_number: str):
        with self.connection:
            return self.cursor.execute('SELECT "bot_username" FROM "bots" WHERE "phone_number" = ?',
                                       (phone_number,)).fetchone()[0]

    def get_username_by_token(self, bot_token: str):
        with self.connection:
            return self.cursor.execute('SELECT "bot_username" FROM "bots" WHERE "bot_token" = ?',
                                       (bot_token,)).fetchone()[0]


class ProjectsDatabase:
    def __init__(self, db_file="files/projects_database.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_path = os.path.join(base_dir, db_file)

        db_directory = os.path.dirname(absolute_path)

        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

        if not os.path.isfile(absolute_path):
            with open(absolute_path, 'w'):  # Создаём файл, если он не существует
                pass

        self.connection = sqlite3.connect(absolute_path)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        with self.connection:
            self.cursor.execute('CREATE TABLE IF NOT EXISTS "projects" ('
                                '"id" INTEGER PRIMARY KEY,'
                                '"project_name" TEXT,'  # == channel_name
                                '"managers_list" TEXT)')

            self.cursor.execute('CREATE TABLE IF NOT EXISTS "companies" ('
                                '"id" INTEGER PRIMARY KEY,'
                                '"company_name" TEXT,'
                                '"by_project_name" TEXT,'
                                '"parsing_regime" TEXT,'
                                '"receiver_account" INTEGER,'  # == CHAT_ID
                                '"sender_account" INTEGER,'  # == CHAT_ID
                                '"source_chat_id" INTEGER,'  # == CHAT_ID
                                '"source_chat_type" TEXT,'
                                '"recipient_chat_id" TEXT,'  # == [CHAT_ID]
                                '"recipient_chat_type" TEXT,'
                                '"history" TEXT,'  # parsing way(period, all, link to post)
                                '"company_events" TEXT DEFAULT "",'  # chat_events (edit, pin, delete)
                                '"person_link_enable" INTEGER,'
                                '"comments_account" INTEGER,'  # == CHAT_ID
                                '"comments_format" TEXT,'
                                '"company_status" TEXT DEFAULT "inactive")')

    def add_project(self, name: str):
        with self.connection:
            return self.cursor.execute('INSERT INTO "projects" ("project_name") '
                                       'VALUES (?)', (name,))

    def add_project_managers(self, name: str, manager: str):
        with self.connection:
            current_managers = self.cursor.execute('SELECT "managers_list" FROM "projects" '
                                                   'WHERE "project_name" = ?', (name,)).fetchone()[0]
            if current_managers:
                current_managers += '|' + manager
            else:
                current_managers += manager

            return self.cursor.execute('UPDATE "projects" SET "managers_list" = ? WHERE "project_name" = ?',
                                       (current_managers, name))

    def change_project_name(self, old_name: str, new_name: str):
        with self.connection:
            self.cursor.execute('UPDATE "projects" SET "project_name" = ? WHERE "project_name" = ?',
                                (new_name, old_name))
            return self.cursor.execute('UPDATE "companies" SET "by_project_name" = ? WHERE "by_project_name" = ?',
                                       (new_name, old_name))

    def delete_project(self, name: str):
        with self.connection:
            self.cursor.execute('DELETE FROM "projects" WHERE "project_name" = ?',
                                (name,))
            return self.cursor.execute('DELETE FROM "companies" WHERE "by_project_name" = ?',
                                       (name,))

    def add_company(self, company_attributes: list):
        with self.connection:
            return self.cursor.execute('INSERT INTO "companies" '
                                       '("company_name", "by_project_name", "parsing_regime", '
                                       '"receiver_account", "sender_account", "source_chat_id", '
                                       '"source_chat_type", "recipient_chat_id",'
                                       '"recipient_chat_type") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                       company_attributes)

    def change_company_attribute(self, company_name: str, attribute_name: str, value: str | int):
        with self.connection:
            return self.cursor.execute(f'UPDATE "companies" SET "{attribute_name}" = ? WHERE "company_name" = ?',
                                       (value, company_name))

    def add_recp_channel(self, company_name: str, recp_channel: str):
        with self.connection:
            current_channels = self.cursor.execute('SELECT "recipient_chat_id" FROM "companies" '
                                                   'WHERE "company_name" = ?', (company_name,)).fetchone()[0]

            new_value = current_channels + " " + recp_channel

            return self.cursor.execute(f'UPDATE "companies" SET "recipient_chat_id" = ? '
                                       f'WHERE "company_name" = ?', (new_value.strip(), company_name,))

    def delete_recp_channel(self, company_name: str, recp_channel: str):
        with (self.connection):
            current_channels = self.cursor.execute('SELECT "recipient_chat_id" FROM '
                                                   '"companies" WHERE "company_name" = ?',
                                                   (company_name,)).fetchone()[0]

            return self.cursor.execute('UPDATE "companies" SET "recipient_chat_id" = ? '
                                       'WHERE "company_name" = ?',
                                       (current_channels.replace(recp_channel, '').strip(), company_name))

    def change_company_event(self, company_name: str, event: str):
        with self.connection:
            current_events = self.cursor.execute('SELECT "company_events" FROM "companies" WHERE "company_name" = ?',
                                                 (company_name,)).fetchone()[0]
            if event in current_events:
                current_events = current_events.replace(event, '').strip().replace('  ', ' ')
                if current_events == ' ':
                    current_events = ''
            else:
                if current_events:
                    current_events += ' '
                current_events += event

            self.cursor.execute('UPDATE "companies" SET "company_events" = ? WHERE "company_name" = ?',
                                (current_events, company_name))
            return current_events

    def set_company_status(self, company_name: str, status: str):
        with self.connection:
            return self.cursor.execute('UPDATE "companies" SET "company_status" = ? '
                                       'WHERE "company_name" = ?',
                                       (status, company_name))

    def annulling_all_company_statuses(self):
        with self.connection:
            return self.cursor.execute('UPDATE "companies" SET "company_status" = "inactive"')

    def delete_company(self, company_name: str):
        with self.connection:
            return self.cursor.execute('DELETE FROM "companies" WHERE "company_name" = ?',
                                       (company_name,))

    def get_projects(self):
        with self.connection:
            return self.cursor.execute('SELECT "project_name" FROM "projects"').fetchall()

    def get_companies(self, project_name: str):
        with self.connection:
            return self.cursor.execute('SELECT "company_name", "by_project_name" '
                                       'FROM "companies" WHERE "by_project_name" = ?',
                                       (project_name,)).fetchall()

    def get_company_recp_channels(self, company_name: str):
        with self.connection:
            return self.cursor.execute('SELECT "recipient_chat_id" FROM "companies" '
                                       'WHERE "company_name" = ?',
                                       (company_name,)).fetchone()

    def get_company_attribute(self, attribute: str, company_name: str):
        with self.connection:
            return self.cursor.execute(f'SELECT "{attribute}" FROM "companies" '
                                       f'WHERE "company_name" = ?',
                                       (company_name,)).fetchone()[0]

    def get_all_company_attributes(self, company_name: str):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "companies" WHERE "company_name" = ?',
                                       (company_name,)).fetchone()

    def get_chat_ids_by_company(self, company_name: str):
        with self.connection:
            return self.cursor.execute('SELECT "source_chat_id", "source_chat_type", '
                                       '"recipient_chat_id", "recipient_chat_type" FROM "companies" '
                                       'WHERE "company_name" = ?', (company_name,)).fetchone()

    def get_token_by_chat_id(self, source_chat_id: int):
        with self.connection:
            return self.cursor.execute('SELECT ""')

    def count_bot_companies(self, bot_task: str, account_id: int):
        with self.connection:
            return self.cursor.execute(f'SELECT COUNT(*) FROM "companies" WHERE {bot_task} = ?',
                                       (account_id,)).fetchone()[0]

    def count_manager_projects(self, account_id: int):
        with self.connection:
            return self.cursor.execute(f'SELECT COUNT(*) FROM "projects" WHERE "managers_list" LIKE %{account_id}%').fetchone()[0]

    def count_all(self):  # only for team-leads
        with self.connection:
            project_counter = self.cursor.execute('SELECT COUNT(*) FROM "projects"').fetchone()[0]
            companies_counter = self.cursor.execute('SELECT COUNT(*) FROM "companies"').fetchone()[0]
            return project_counter, companies_counter


class AllChatsDatabase:
    def __init__(self):
        db_file = "files/chats/all_chats_database.db"

        # Определение абсолютного пути к файлу базы данных
        base_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_path = os.path.join(base_dir, db_file)

        # Создание всех директорий в пути, если они не существуют
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        # Подключение к базе данных
        self.connection = sqlite3.connect(absolute_path)
        self.cursor = self.connection.cursor()

    def create_table(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS "all_chats" ('
                                       '"id" INTEGER PRIMARY KEY,'
                                       '"chat_id" INTEGER,'
                                       '"chat_type" TEXT)')

    def add_chat(self, chat_id: int, chat_type: str):
        with self.connection:
            return self.cursor.execute('INSERT INTO "all_chats" ("chat_id", "chat_type") '
                                       'VALUES (?, ?)', (chat_id, chat_type))

    def check_chat_existing(self, chat_id: int):
        with self.connection:
            result = self.cursor.execute('SELECT 1 FROM "all_chats" WHERE "chat_id" = ?',
                                       (chat_id,)).fetchone()
            if not result:
                return
            return result[0]


class ChatDatabase:
    def __init__(self, chat_type: str, chat_id: int):
        db_file = f"files/chats/{chat_type}/{chat_id}.db"

        base_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_path = os.path.join(base_dir, db_file)

        # Создание всех директорий в пути, если они не существуют
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        self.connection = sqlite3.connect(absolute_path)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        with self.connection:
            self.cursor.execute('CREATE TABLE IF NOT EXISTS "all_posts" ('
                                '"id" INTEGER PRIMARY KEY,'
                                '"text" TEXT,'
                                '"photo" TEXT,'
                                '"video" TEXT,'
                                '"audio" TEXT,'
                                '"document" TEXT,'
                                '"video_note" TEXT,'
                                '"voice_message" TEXT,'
                                '"sticker" TEXT,'
                                '"location" TEXT,'
                                '"contact" TEXT,'
                                '"poll" TEXT,'
                                '"animation" TEXT,'
                                '"markup" TEXT,'
                                '"entities" TEXT,'
                                '"post_type" TEXT,'
                                '"post_media_group_id" INTEGER,'
                                '"post_message_id" INTEGER)')  # message_id в канале-источнике

            self.cursor.execute('CREATE TABLE IF NOT EXISTS "all_comments" ('
                                '"id" INTEGER PRIMARY KEY,'
                                '"text" TEXT,'
                                '"username" TEXT,'
                                '"comment_message_id" INTEGER)')
            return

    def add_post(self, post_data: list):
        with self.connection:
            return self.cursor.execute('INSERT INTO "all_posts" ("text", "photo", "video", '
                                       '"audio", "document", "video_note", "voice_message", '
                                       '"sticker", "location", "contact", '
                                       '"poll", "animation", "markup", "entities", '
                                       '"post_type", "post_media_group_id", "post_message_id") '
                                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                       post_data)

    def add_comment(self, comment_data: list):
        with self.connection:
            return self.cursor.execute('INSERT INTO "all_comments" ("text", "username", "comment_message_id") '
                                       'VALUES (?, ?, ?)', comment_data)

    def get_all_posts(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "all_posts"').fetchall()

    def get_posts_by_ids(self, messages_ids: list):
        with self.connection:
            result = []
            for msg_id in messages_ids:
                post_data = self.cursor.execute('SELECT * FROM "all_posts" WHERE "post_message_id" = ?',
                                                (int(msg_id),)).fetchone()
                logger.warning(str(post_data))
                if post_data:
                    result.append(post_data)
            return result

    def get_all_comments(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "all_comments"').fetchall()

