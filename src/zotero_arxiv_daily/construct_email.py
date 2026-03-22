from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from html import escape
import json

from .protocol import Paper


_STYLE = """
:root {
  --bg: #f5f7fb;
  --surface: #ffffff;
  --surface-alt: #eef2f9;
  --text: #182230;
  --muted: #5d6b82;
  --accent: #0f766e;
  --border: #d5deec;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Source Sans 3", "Segoe UI", sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at 20% 10%, #d9f0e8 0%, rgba(217, 240, 232, 0) 45%),
    radial-gradient(circle at 80% 0%, #e7edf9 0%, rgba(231, 237, 249, 0) 35%),
    var(--bg);
}
.container {
  max-width: 980px;
  margin: 0 auto;
  padding: 32px 16px 64px;
}
.header {
  margin-bottom: 18px;
}
.header h1 {
  margin: 0;
  font-size: 2rem;
  letter-spacing: 0.01em;
}
.header p {
  margin: 6px 0 0;
  color: var(--muted);
}
.nav {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.nav a {
  text-decoration: none;
  color: var(--accent);
  font-weight: 600;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: 0 8px 22px rgba(10, 40, 60, 0.06);
}
.card h2 {
  margin: 0;
  font-size: 1.08rem;
  line-height: 1.35;
}
.card .meta {
  color: var(--muted);
  margin-top: 8px;
  font-size: 0.95rem;
}
.card .tldr {
  margin-top: 10px;
}
.card .links {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.card .links a {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
}
.score {
  font-weight: 700;
}
.empty {
  background: var(--surface-alt);
  border: 1px dashed var(--border);
  border-radius: 14px;
  padding: 24px;
  color: var(--muted);
  font-size: 1.05rem;
}
.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.history-list li {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}
.footer {
  margin-top: 26px;
  color: var(--muted);
  font-size: 0.9rem;
}
@media (max-width: 720px) {
  .container { padding: 20px 12px 48px; }
  .header h1 { font-size: 1.55rem; }
  .history-list li { flex-direction: column; align-items: flex-start; }
}
"""


def _safe(value: str | None, fallback: str = "Unknown") -> str:
    if not value:
        return fallback
    return escape(value)


def _author_text(authors: list[str]) -> str:
    if len(authors) <= 5:
        return ", ".join(authors)
    return ", ".join(authors[:3] + ["..."] + authors[-2:])


def _affiliation_text(affiliations: list[str] | None) -> str:
    if not affiliations:
        return "Unknown affiliation"
    result = ", ".join(affiliations[:5])
    if len(affiliations) > 5:
        return result + ", ..."
    return result


def _paper_to_dict(paper: Paper) -> dict:
    return {
        "source": paper.source,
        "title": paper.title,
        "authors": list(paper.authors),
        "abstract": paper.abstract,
        "url": paper.url,
        "pdf_url": paper.pdf_url,
        "tldr": paper.tldr,
        "affiliations": list(paper.affiliations) if paper.affiliations else [],
        "score": paper.score,
    }


def _render_paper_card(paper: Paper) -> str:
    title = _safe(paper.title)
    authors = _safe(_author_text(paper.authors), "Unknown authors")
    affiliations = _safe(_affiliation_text(paper.affiliations))
    tldr = _safe(paper.tldr, _safe(paper.abstract))
    score = "Unknown" if paper.score is None else f"{paper.score:.1f}"
    source = _safe(paper.source)
    paper_url = _safe(paper.url)
    pdf_url = _safe(paper.pdf_url or paper.url)
    return f"""
<article class=\"card\">
  <h2>{title}</h2>
  <div class=\"meta\">{authors}<br><i>{affiliations}</i></div>
  <div class=\"meta\">Source: {source} | Relevance: <span class=\"score\">{score}</span></div>
  <p class=\"tldr\">{tldr}</p>
  <div class=\"links\">
    <a href=\"{paper_url}\" target=\"_blank\" rel=\"noopener noreferrer\">Paper</a>
    <a href=\"{pdf_url}\" target=\"_blank\" rel=\"noopener noreferrer\">PDF</a>
  </div>
</article>
"""


def _build_page(title: str, subtitle: str, nav_html: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <style>{_STYLE}</style>
</head>
<body>
  <main class=\"container\">
    <header class=\"header\">
      <h1>{escape(title)}</h1>
      <p>{escape(subtitle)}</p>
      <nav class=\"nav\">{nav_html}</nav>
    </header>
    {body_html}
    <footer class=\"footer\">Generated automatically by zotero-arxiv-daily.</footer>
  </main>
</body>
</html>
"""


def _render_daily_page(
    papers: list[Paper],
    site_title: str,
    day_text: str,
    empty_message: str,
  latest_href: str,
  history_href: str | None,
) -> str:
  nav_parts = [f'<a href="{escape(latest_href)}">Latest</a>']
  if history_href:
    nav_parts.append(f'<a href="{escape(history_href)}">History</a>')
    nav_html = "".join(nav_parts)

    if not papers:
        body_html = f'<section class="empty">{escape(empty_message)}</section>'
    else:
        body_html = "\n".join(_render_paper_card(p) for p in papers)

    return _build_page(
        title=site_title,
        subtitle=f"Daily recommendations for {day_text}",
        nav_html=nav_html,
        body_html=body_html,
    )


def _render_history_page(history: list[dict], site_title: str) -> str:
    items = []
    for item in history:
        day = _safe(item["date"])
        papers = int(item.get("paper_count", 0))
        href = _safe(item["href"])
        items.append(
      f'<li><a href="../{href}">{day}</a><span>{papers} paper(s)</span></li>'
        )

    body = "\n".join(items) if items else '<section class="empty">No history available yet.</section>'
    if items:
        body = f'<ul class="history-list">{body}</ul>'
    return _build_page(
        title=f"{site_title} - History",
        subtitle="Archived daily snapshots",
      nav_html='<a href="../">Latest</a>',
        body_html=body,
    )


def write_site(
    papers: list[Paper],
    output_dir: str,
    site_title: str,
    empty_message: str,
    keep_days: int,
) -> dict:
    output_root = Path(output_dir)
    days_dir = output_root / "days"
    data_dir = output_root / "data"
    history_dir = output_root / "history"
    output_root.mkdir(parents=True, exist_ok=True)
    days_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    latest_html = _render_daily_page(
        papers=papers,
        site_title=site_title,
        day_text=today,
        empty_message=empty_message,
      latest_href="./",
      history_href="history/",
    )
    daily_html = _render_daily_page(
      papers=papers,
      site_title=site_title,
      day_text=today,
      empty_message=empty_message,
      latest_href="../",
      history_href="../history/",
    )

    daily_html_path = days_dir / f"{today}.html"
    latest_path = output_root / "index.html"
    daily_json_path = data_dir / f"{today}.json"
    history_json_path = data_dir / "history.json"
    history_html_path = history_dir / "index.html"

    daily_html_path.write_text(daily_html, encoding="utf-8")
    latest_path.write_text(latest_html, encoding="utf-8")
    daily_json_path.write_text(
        json.dumps(
            {
                "date": today,
                "paper_count": len(papers),
                "papers": [_paper_to_dict(p) for p in papers],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    history: list[dict] = []
    if history_json_path.exists():
        history = json.loads(history_json_path.read_text(encoding="utf-8"))
    history = [h for h in history if h.get("date") != today]
    history.insert(0, {"date": today, "paper_count": len(papers), "href": f"days/{today}.html"})
    if keep_days > 0:
        history = history[:keep_days]

    keep_dates = {h["date"] for h in history}
    for file in days_dir.glob("*.html"):
        if file.stem not in keep_dates:
            file.unlink()
    for file in data_dir.glob("*.json"):
        if file.name != "history.json" and file.stem not in keep_dates:
            file.unlink()

    history_json_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    history_html_path.write_text(_render_history_page(history, site_title=site_title), encoding="utf-8")

    return {
        "latest_page": str(latest_path),
        "daily_page": str(daily_html_path),
        "history_page": str(history_html_path),
    }
