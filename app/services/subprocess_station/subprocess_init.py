import subprocess
import os
from app.services.logs.logging import logger


class SubprocessStation:
    def __init__(self):
        self.default_env = os.environ.copy()
        self.script_path = None
        self.input_data = None

    def set_env_vars(self, env_vars):
        env = self.default_env.copy()
        env.update(env_vars)

    def set_script_path(self, script_type: str, script_name: str):
        curr_dir = os.path.dirname(os.path.dirname(os.getcwd()))
        self.script_path = os.path.join(
            curr_dir, f"bots/workers_bots/{script_type}_scripts", script_name
        )

    def set_input_data(self, data: str):
        if data.endswith(".session"):
            curr_dir = os.path.dirname(os.path.dirname(os.getcwd()))
            self.input_data = os.path.join(
                curr_dir,
                "bots/workers_bots/pyrogram_scripts/sessions", data
            )
        else:
            self.input_data = data  # == bot_token

    def run_script(self, script_name: str):
        # input_data = bot_token or path to *.session file
        try:
            if not self.script_path:
                logger.error("No script_path was given")
                return

            if not self.input_data:
                logger.error("No input_data was given")
                return

            curr_dir = os.path.dirname(os.getcwd())
            path_to_logs_file = os.path.join(
                curr_dir, "logs/files",
                f"{script_name.split('.')[0]}.log"
            )

            command = ["python", self.script_path, self.input_data]

            with open(path_to_logs_file, "w") as logs_file:
                subprocess.Popen(
                            command,
                            stdout=logs_file,
                            stderr=logs_file,
                            env=self.default_env,
                            close_fds=True
                        )
        except Exception as e:
            logger.error("Возникла ошибка в run_script: %s", e)
