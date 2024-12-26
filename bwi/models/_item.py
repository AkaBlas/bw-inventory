import tomllib
from pathlib import Path
from typing import Annotated, Any, Self

import tomlkit
from pydantic import BeforeValidator, Field

from .._utils.models import FrozenModel
from .._utils.types import PathLike
from ..config import INVENTORY_SETTINGS
from ..constants import ItemDecision
from ._itemcomment import ItemComment
from ._itemname import ItemName


def _ensure_path(value: Any) -> Any:
    if isinstance(value, str):
        return Path(value)
    return value


class Item(FrozenModel):
    name: ItemName
    description: str
    photos: tuple[Annotated[Path, BeforeValidator(_ensure_path)], ...] = Field(
        default_factory=tuple
    )
    comments: tuple[ItemComment, ...] = Field(default_factory=tuple)
    decision: ItemDecision = ItemDecision.UNDECIDED

    @property
    def slug(self) -> str:
        return self.name.slug

    @property
    def uid(self) -> str:
        return self.name.uid

    @classmethod
    def from_drive(cls, directory: PathLike) -> Self:
        item_name = ItemName.from_string(Path(directory).name)
        file_name = item_name.to_string("toml")
        return cls(**tomllib.loads((Path(directory) / file_name).read_text(encoding="utf-8")))

    @classmethod
    def load_all_from_drive(
        cls, root: PathLike = INVENTORY_SETTINGS.inventory_path
    ) -> tuple[Self, ...]:
        items: list[Self] = []
        for path in Path(root).iterdir():
            if not path.is_dir():
                continue
            items.append(cls.from_drive(path))
        return tuple(items)

    def get_directory(self, root: PathLike = INVENTORY_SETTINGS.inventory_path) -> Path:
        return Path(root) / self.name.to_string(None)

    def write_to_file(self, root: PathLike = INVENTORY_SETTINGS.inventory_path) -> Path:
        directory = self.get_directory(root)
        file_name = self.name.to_string("toml")
        (directory / file_name).write_text(
            tomlkit.dumps(self.model_dump(mode="json")), encoding="utf-8"
        )
        return directory / file_name

    def add_photo(
        self,
        file_name: PathLike,
        file_content: bytes,
        root: PathLike = INVENTORY_SETTINGS.inventory_path,
    ) -> None:
        directory = self.get_directory(root)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / file_name).write_bytes(file_content)
        with self._unfrozen():
            self.photos += (Path(file_name),)

    def add_comment(self, comment: ItemComment) -> None:
        with self._unfrozen():
            self.comments += (comment,)
