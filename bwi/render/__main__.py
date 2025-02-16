import datetime as dtm
import zoneinfo
from collections import defaultdict
from pathlib import Path
from typing import Literal

from jinja2 import FileSystemLoader, StrictUndefined

from bwi.constants import ItemDecision
from bwi.models import Item, update_decisions

from .._utils.jinja2 import RelImportEnvironment

ROOT = Path(__file__).parent


def main(template: Literal["comments", "consolidated"]) -> None:
    update_decisions()
    items = Item.load_all_from_drive()
    grouped_items = defaultdict(list)
    for item in items:
        grouped_items[item.decision].append(item)

    environment = RelImportEnvironment(
        loader=FileSystemLoader(ROOT / f"_template_{template}"),
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=StrictUndefined,
    )
    timezone = zoneinfo.ZoneInfo("Europe/Berlin")
    (Path.cwd() / "index.html").write_text(
        environment.get_template("index.j2").render(
            grouped_items=grouped_items,
            template_path=(ROOT / f"_template_{template}").as_posix(),
            item_decision=ItemDecision,
            now=dtm.datetime.now(timezone),
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main("consolidated")
