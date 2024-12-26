from .._utils.models import FrozenModel
from ..constants import ItemDecision


class ItemComment(FrozenModel):
    author: str
    content: str = ""
    recommendation: ItemDecision = ItemDecision.UNDECIDED

    def set_recommendation(self, recommendation: ItemDecision) -> None:
        with self._unfrozen():
            self.recommendation = recommendation

    def set_content(self, content: str) -> None:
        with self._unfrozen():
            self.content = content
