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
                                '"bot_task" TEXT,'
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
            return self.cursor.execute('INSERT INTO "bots" ("bot_task", "proxy", '
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

    def get_account_info(self, account_type: str, account_id: int):
        with self.connection:
            return self.cursor.execute(f'SELECT * FROM "{account_type}" WHERE "id" = ?',
                                       (account_id,)).fetchone()

    def count_managers_by_head(self, account_chat_id: int):
        with self.connection:
            return self.cursor.execute('SELECT COUNT(*) FROM "users" WHERE "head_user_id" = ?',
                                       (account_chat_id,)).fetchone()[0]


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
                                '"recipient_chat_id" INTEGER,'  # == [CHAT_ID]
                                '"recipient_chat_type" TEXT)')

    def add_project(self, name: str):
        with self.connection:
            return self.cursor.execute('INSERT INTO "projects" ("project_name") '
                                       'VALUES (?)', (name,))

    def add_project_managers(self, name: str, manager: str):
        with self.connection:
            current_managers = self.cursor.execute('SELECT "managers_list" FROM "projects" '
                                                   'WHERE "project_name" = ?', (project_name,)).fetchone()[0]
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
                                       '"source_chat_type", "recipient_chat_id", '
                                       '"recipient_chat_type") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                       company_attributes)

    def change_company_name(self, old_name: str, new_name: str):
        with self.connection:
            return self.cursor.execute('UPDATE "companies" SET "company_name" = ? WHERE "company_name" = ?',
                                       (new_name, old_name))

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

    def get_company_attributes(self, company_name: str):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "companies" WHERE "company_name" = ?',
                                       (company_name,)).fetchone()


# class CompaniesDatabase:
#     def __init__(self, project_name: str):
#         db_file = f"files/{project_name}_companies_database.db"
#         # Получаем абсолютный путь к файлу базы данных относительно этого файла
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         absolute_path = os.path.join(base_dir, db_file)
#
#         self.connection = sqlite3.connect(absolute_path)
#         self.cursor = self.connection.cursor()
#
#     def create_table(self, company_name: str):
#         with self.connection:
#             self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {company_name} ('
#                                 '"id" INTEGER PRIMARY KEY,')

