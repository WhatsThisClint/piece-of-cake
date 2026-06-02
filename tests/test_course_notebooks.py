from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest


NOTEBOOK_DIR = Path(__file__).resolve().parents[1] / "course" / "notebooks"


@pytest.fixture(scope="module", autouse=True)
def _require_geo_dependencies():
    pytest.importorskip("rasterio")
    pytest.importorskip("geopandas")
    pytest.importorskip("IPython")


def _notebooks() -> list[Path]:
    return sorted(NOTEBOOK_DIR.glob("[0-9][0-9]_*.ipynb"))


def test_course_has_fifteen_numbered_notebooks():
    notebooks = _notebooks()

    assert len(notebooks) == 15
    assert [path.name[:2] for path in notebooks] == [f"{idx:02d}" for idx in range(1, 16)]


@pytest.mark.parametrize("notebook_path", _notebooks(), ids=lambda path: path.name)
def test_course_notebook_structure(notebook_path: Path):
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    markdown = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "markdown"
    )
    code = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )

    assert markdown.lstrip().startswith("# ")
    assert "Learning objective:" in markdown
    assert "piece_of_cake" in code
    assert "course_outputs" in code or "export_scene" in code


@pytest.mark.parametrize("notebook_path", _notebooks(), ids=lambda path: path.name)
def test_course_notebook_executes(notebook_path: Path, tmp_path: Path, monkeypatch):
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    helper_path = NOTEBOOK_DIR / "course_helpers.py"
    shutil.copy2(helper_path, tmp_path / "course_helpers.py")
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    namespace = {"__name__": "__main__"}

    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        exec(compile(source, str(notebook_path), "exec"), namespace)

    html_files = sorted((tmp_path / "course_outputs").glob("*.html"))
    assert html_files, f"{notebook_path.name} did not export any HTML"
    combined_html = "\n".join(path.read_text(encoding="utf-8") for path in html_files)
    assert "piece-of-cake-map" in combined_html
    assert "plotly_click" in combined_html
