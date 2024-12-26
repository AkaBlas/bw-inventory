from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["BOT_SETTINGS", "INVENTORY_SETTINGS", "BotSettings", "InventorySettings"]


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str


class InventorySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    inventory_path: Path = Path(__file__).parent.parent.parent / "inventory"
    default_author: str


BOT_SETTINGS = BotSettings()  # type: ignore[call-arg]
INVENTORY_SETTINGS = InventorySettings()  # type: ignore[call-arg]
