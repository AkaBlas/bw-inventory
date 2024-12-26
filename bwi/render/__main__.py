from pathlib import Path
from pprint import pprint

from jinja2 import FileSystemLoader, StrictUndefined

from bwi.models import Item

from .._utils.jinja2 import RelImportEnvironment

ROOT = Path(__file__).parent


def main() -> None:
    items = Item.load_all_from_drive()
    pprint(items)

    environment = RelImportEnvironment(
        loader=FileSystemLoader(ROOT / "_template"),
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=StrictUndefined,
    )
    (Path.cwd() / "index.html").write_text(
        environment.get_template("index.j2").render(
            items=items, template_path=(ROOT / "_template").as_posix()
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
