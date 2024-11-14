import subprocess
import os
from datetime import datetime
from app.services.logs.logging import logger


class SubprocessStation:
    def __init__(self, venv_path="/root/28k_bot_order/myenv"):
        self.default_env = os.environ.copy()
        self.script_path = None
        self.input_data = None
        self.company_name = None
        self.additional_data = None
        self.venv_python = os.path.join(venv_path, "bin", "python")
        self.processes = {}  # Словарь для хранения запущенных процессов с их PID

    def set_env_vars(self, env_vars):
        env = self.default_env.copy()
        env.update(env_vars)

    def set_script_path(self, script_type: str, script_name: str):
        curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.script_path = os.path.join(
            curr_dir, f"bots/workers_bots/{script_type}_scripts/", script_name
        )

    def set_input_data(self, data: str):
        if data.endswith(".session"):
            curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.input_data = os.path.join(
                curr_dir,
                "bots/workers_bots/pyrogram_scripts/sessions/", data
            )
        else:
            self.input_data = data  # == bot_token

    def set_company_name(self, company: str):
        self.company_name = company

    def set_additional_data(self, data: str):
        self.additional_data = data

    def run_script(self, script_name: str):
        try:
            if not self.script_path:
                logger.error("No script_path was given")
                return

            if not self.input_data:
                logger.error("No input_data was given")
                return

            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

            logs_dir = os.path.join(root_dir, "app/services/logs/files")
            os.makedirs(logs_dir, exist_ok=True)

            now = datetime.now()

            path_to_logs_file = os.path.join(
                logs_dir, f"{now.date()} {now.time()}.log"
            )

            command = [self.venv_python, self.script_path]

            if self.input_data.endswith(".session"):
                command += ["--session_path", self.input_data]
            else:
                command += ["--bot_token", self.input_data]

            command += ["--company_name", self.company_name]

            if self.additional_data:
                command += ["--additional_data", self.additional_data]

            with open(path_to_logs_file, "w") as logs_file:
                process = subprocess.Popen(
                    command,
                    stdout=logs_file,
                    stderr=logs_file,
                    env=self.default_env,
                    close_fds=True
                )
                # Сохраняем процесс с его PID как ключ
                self.processes[process.pid] = process
                logger.info(f"Процесс {process.pid} запущен для {script_name}")
        except Exception as e:
            logger.error("Возникла ошибка в run_script: %s", e)

    def terminate_process_by_pid(self, pid: int):
        """
        Завершает процесс по его PID, если он находится в списке запущенных процессов.
        """
        process = self.processes.get(pid)
        if process:
            process.terminate()  # Отправка сигнала завершения
            process.wait()  # Ожидание завершения для освобождения ресурсов
            del self.processes[pid]  # Удаляем из словаря процессов
            logger.info(f"Процесс {pid} завершён и удалён из списка")
        else:
            logger.warning(f"Процесс с PID {pid} не найден среди запущенных")

    def terminate_all_processes(self):
        for pid, process in list(self.processes.items()):
            process.terminate()
            process.wait()
            logger.info(f"Процесс {pid} завершён")
        self.processes.clear()
