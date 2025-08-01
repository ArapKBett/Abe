import subprocess
import logging
import os

class RobloxManager:
    def __init__(self, ram_path, lua_script_path, game_id):
        self.ram_path = ram_path
        self.lua_script_path = lua_script_path
        self.game_id = game_id
        self.logger = logging.getLogger(__name__)

    def trigger_action(self, account):
        if not os.path.exists(self.ram_path):
            self.logger.error(f"RAM executable not found at {self.ram_path}")
            return False
        if not os.path.exists(self.lua_script_path):
            self.logger.error(f"Lua script not found at {self.lua_script_path}")
            return False

        try:
            # Use Wine to run the Windows executable on Linux
            cmd = [
                "wine",  # Invoke Wine
                self.ram_path,
                "--account", account["username"],
                "--password", account["password"],
                "--game", self.game_id,
                "--script", self.lua_script_path
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "WINEDEBUG": "-all"}  # Suppress Wine debug output
            )
            self.logger.info(f"RAM output for {account['username']}: {result.stdout}")
            if result.returncode == 0:
                return True
            self.logger.error(f"RAM error for {account['username']}: {result.stderr}")
            return False
        except subprocess.SubprocessError as e:
            self.logger.error(f"Subprocess error for {account['username']}: {e}")
            return False
