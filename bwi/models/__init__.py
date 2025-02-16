__all__ = [
    "Item",
    "ItemComment",
    "ItemCommentInput",
    "ItemCommentInputs",
    "ItemName",
    "load_all",
    "merge_comment_inputs_into_inventory",
    "update_decisions",
]

from pathlib import Path

from .._utils.types import PathLike
from ._item import Item
from ._itemcomment import ItemComment
from ._itemcommentinput import ItemCommentInput, ItemCommentInputs
from ._itemname import ItemName


def load_all() -> tuple[Item, ...]:
    return Item.load_all_from_drive()


def merge_comment_inputs_into_inventory(path: PathLike) -> None:
    ItemCommentInputs.from_drive(Path(path)).merge_into_inventory()


def update_decisions() -> None:
    for item in load_all():
        item.update_decision()
        item.write_to_file()
