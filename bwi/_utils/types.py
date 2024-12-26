from pathlib import Path
from typing import Any

from telegram.ext import CallbackContext, ExtBot

from ..config import InventorySettings

ADict = dict[Any, Any]
CONTEXT_TYPE = CallbackContext[ExtBot[Any], ADict, ADict, InventorySettings]
PathLike = str | Path
