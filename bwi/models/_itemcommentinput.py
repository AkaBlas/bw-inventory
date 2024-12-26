import tomllib
from pathlib import Path
from typing import Self

from .._utils.models import FrozenModel
from .._utils.types import PathLike
from ..config import INVENTORY_SETTINGS
from ..constants import ItemDecision
from . import Item, ItemComment


class ItemCommentInput(FrozenModel):
    uid: str
    author: str
    content: str
    recommendation: ItemDecision


class ItemCommentInputs(FrozenModel):
    comments: tuple[ItemCommentInput, ...]

    def get_comment_for_item(self, item_uid: str) -> ItemComment | None:
        for comment in self.comments:
            if comment.uid == item_uid:
                data = comment.model_dump()
                data.pop("uid")
                return ItemComment(**data)
        return None

    @classmethod
    def from_drive(cls, path: PathLike) -> Self:
        return cls(**tomllib.loads(Path(path).read_text(encoding="utf-8")))

    def merge_into_inventory(self, root: PathLike = INVENTORY_SETTINGS.inventory_path) -> None:
        for item in Item.load_all_from_drive():
            comment = self.get_comment_for_item(item.uid)
            if comment is None:
                continue

            # check if author already commented
            existing_comment = item.get_comment_by_author(comment.author)
            if not existing_comment:
                item.add_comment(comment)
            else:
                existing_comment.set_recommendation(comment.recommendation)
                existing_comment.set_content(comment.content)

            item.write_to_file(root)
