from collections.abc import Generator
from contextlib import contextmanager
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class FrozenModel(BaseModel):
    """A frozen Pydantic model."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True, arbitrary_types_allowed=True, extra="forbid"
    )

    @classmethod
    @contextmanager
    def _unfrozen(cls) -> Generator[None, None, None]:
        original_frozen = cls.model_config["frozen"]
        cls.model_config["frozen"] = False
        try:
            yield
        finally:
            cls.model_config["frozen"] = original_frozen
