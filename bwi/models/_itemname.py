from typing import ClassVar, Self

import shortuuid
from pathvalidate import sanitize_filename
from pydantic import Field

from .._utils.models import FrozenModel

_short_uuid = shortuuid.ShortUUID()


def random_uid() -> str:
    return _short_uuid.uuid()


class ItemName(FrozenModel):
    slug: str
    uid: str = Field(default_factory=random_uid)

    SEPARATOR: ClassVar[str] = "."

    def __post_init__(self) -> None:
        if self.SEPARATOR in self.slug:
            raise ValueError(f"slug must not contain {self.SEPARATOR!r}")

    @classmethod
    def from_string(cls, string: str) -> Self:
        string = string.removesuffix(".toml")
        try:
            slug, uid = string.split(cls.SEPARATOR)
        except ValueError as exc:
            raise ValueError(f"invalid filename: {string!r}") from exc

        return cls(slug=slug, uid=uid)

    def to_string(self, extension: str | None) -> str:
        parts = [self.slug, self.uid]
        if extension:
            parts.append(extension)
        return sanitize_filename(self.SEPARATOR.join(parts))
