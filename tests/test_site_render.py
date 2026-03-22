import json
from pathlib import Path

import pytest

from zotero_arxiv_daily.construct_email import write_site
from zotero_arxiv_daily.protocol import Paper


@pytest.fixture
def papers() -> list[Paper]:
    paper = Paper(
        source="arxiv",
        title="Test Paper",
        authors=["Test Author", "Test Author 2"],
        abstract="Test Abstract",
        url="https://arxiv.org/abs/2512.04296",
        pdf_url="https://arxiv.org/pdf/2512.04296",
        full_text="Test Full Text",
        tldr="Test TLDR",
        affiliations=["Test Affiliation", "Test Affiliation 2"],
        score=0.5,
    )
    return [paper] * 3


def test_write_site_generates_pages(tmp_path: Path, papers: list[Paper]):
    output_dir = tmp_path / "site"
    result = write_site(
        papers=papers,
        output_dir=str(output_dir),
        site_title="Zotero arXiv Daily",
        empty_message="No papers today.",
        keep_days=30,
    )

    latest = Path(result["latest_page"])
    daily = Path(result["daily_page"])
    history = Path(result["history_page"])

    assert latest.exists()
    assert daily.exists()
    assert history.exists()

    latest_html = latest.read_text(encoding="utf-8")
    daily_html = daily.read_text(encoding="utf-8")
    history_html = history.read_text(encoding="utf-8")
    assert 'href="history/"' in latest_html
    assert 'href="../history/"' in daily_html
    assert 'href="../"' in history_html

    history_json = output_dir / "data" / "history.json"
    assert history_json.exists()
    data = json.loads(history_json.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["paper_count"] == 3


def test_write_site_retains_history_across_runs(tmp_path: Path, papers: list[Paper]):
    output_dir = tmp_path / "site"
    write_site(
        papers=papers,
        output_dir=str(output_dir),
        site_title="Zotero arXiv Daily",
        empty_message="No papers today.",
        keep_days=30,
    )

    history_json = output_dir / "data" / "history.json"
    history_data = json.loads(history_json.read_text(encoding="utf-8"))
    assert len(history_data) == 1

    yesterday = "2026-03-16"
    history_data.append({"date": yesterday, "paper_count": 5, "href": f"days/{yesterday}.html"})
    history_json.write_text(json.dumps(history_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "days" / f"{yesterday}.html").write_text("old", encoding="utf-8")
    (output_dir / "data" / f"{yesterday}.json").write_text("{}", encoding="utf-8")

    write_site(
        papers=papers,
        output_dir=str(output_dir),
        site_title="Zotero arXiv Daily",
        empty_message="No papers today.",
        keep_days=30,
    )

    new_history_data = json.loads(history_json.read_text(encoding="utf-8"))
    assert len(new_history_data) == 2
    assert any(item["date"] == yesterday for item in new_history_data)


def test_write_site_empty_page(tmp_path: Path):
    output_dir = tmp_path / "site"
    msg = "No papers today. Take a rest!"
    result = write_site(
        papers=[],
        output_dir=str(output_dir),
        site_title="Zotero arXiv Daily",
        empty_message=msg,
        keep_days=30,
    )

    latest = Path(result["latest_page"])
    content = latest.read_text(encoding="utf-8")
    assert msg in content
