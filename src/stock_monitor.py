import asyncio
import json
import logging
from datetime import datetime
from src.roblox_manager import RobloxManager
from src.discord_notifier import DiscordNotifier
from src.utils import setup_logging, load_config, load_accounts, save_accounts
import requests
from time import sleep

class StockMonitor:
    def __init__(self):
        self.config = load_config()
        self.accounts = load_accounts()
        self.notifier = DiscordNotifier(
            self.config["discord"]["webhook_url"],
            self.config["discord"]["channel_id"],
            self.config["discord"]["bot_token"]
        )
        self.roblox_manager = RobloxManager(
            self.config["roblox"]["ram_path"],
            self.config["roblox"]["lua_script_path"],
            self.config["roblox"]["game_id"]
        )
        setup_logging(self.config["logging"]["log_file"], self.config["logging"]["log_level"])
        self.logger = logging.getLogger(__name__)

    def check_stock(self):
        try:
            url = self.config["monitoring"]["stock_api_url"].format(game_id=self.config["roblox"]["game_id"])
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            in_stock = data.get("bug_egg", {}).get("in_stock", False)
            self.logger.info(f"Stock check: Bug egg {'in stock' if in_stock else 'out of stock'}")
            return in_stock
        except requests.RequestException as e:
            self.logger.error(f"Stock check failed: {e}")
            return False

    async def process_account(self, account):
        self.logger.info(f"Processing account: {account['username']}")
        try:
            success = self.roblox_manager.trigger_action(account)
            if success:
                account["last_used"] = datetime.utcnow().isoformat()
                save_accounts(self.accounts)
                await self.notifier.send_message(
                    f"✅ Account {account['username']} successfully purchased and placed bug egg!"
                )
            else:
                await self.notifier.send_message(
                    f"❌ Failed to process account {account['username']}."
                )
        except Exception as e:
            self.logger.error(f"Error processing account {account['username']}: {e}")
            await self.notifier.send_message(
                f"❌ Error processing account {account['username']}: {str(e)}"
            )

    async def monitor(self):
        self.logger.info("Starting stock monitoring")
        await self.notifier.send_message("🟢 Stock monitoring started")
        while True:
            if self.check_stock():
                self.logger.info("Bug egg in stock! Processing accounts")
                for account in self.accounts:
                    await self.process_account(account)
                    sleep(5)  # Avoid rate limiting
            else:
                self.logger.debug("Bug egg out of stock")
            await asyncio.sleep(self.config["monitoring"]["check_interval"])

    async def run(self):
        try:
            await asyncio.gather(self.notifier.start_bot(), self.monitor())
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            await self.notifier.send_message(f"❌ Fatal error: {str(e)}")

if __name__ == "__main__":
    monitor = StockMonitor()
    asyncio.run(monitor.run())
