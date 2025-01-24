import logging
from typing import Any

from telegram import BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from telegram.ext import Application, CallbackContext, ContextTypes, Defaults, ExtBot

from .._utils.types import ADict
from ..config import BOT_SETTINGS, InventorySettings
from ._add_item import ADD_ITEM_CONV

__all__ = ["build_application"]

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def _post_init(application: Application[Any, Any, Any, Any, Any, Any]) -> None:
    await application.bot.delete_my_commands()
    await application.bot.delete_my_commands(BotCommandScopeAllPrivateChats())
    await application.bot.delete_my_commands(BotCommandScopeAllGroupChats())
    await application.bot.set_my_commands(
        [
            ("add_item", "Add a new item to the inventory."),
            ("done", "Finish a step while adding new item."),
        ]
    )


def build_application(
    token: str = BOT_SETTINGS.bot_token,
) -> Application[
    ExtBot[None],
    CallbackContext[ExtBot[Any], ADict, ADict, InventorySettings],
    ADict,
    ADict,
    InventorySettings,
    None,
]:
    app = (
        Application.builder()
        .token(token)
        .job_queue(None)
        .context_types(ContextTypes(bot_data=InventorySettings))
        .post_init(_post_init)
        .defaults(Defaults(do_quote=False))
        .build()
    )
    app.add_handler(ADD_ITEM_CONV)
    return app
