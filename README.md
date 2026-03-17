<p align="center">
  <img width="180" height="180" src="assets/logo.svg" alt="zotero-arxiv-daily logo">
</p>

<h2 align="center">Zotero arXiv Daily (GitHub Pages Edition)</h2>

<p align="center">
  Recommend new papers daily from your Zotero interest profile,
  and publish results as a static website on GitHub Pages.
</p>

## Fork Notice

This repository is a fork and modification of:

https://github.com/TideDra/zotero-arxiv-daily

Core statement:

1. This project is based on the upstream implementation and keeps attribution to the original author/repository.
2. This fork changes the delivery mode from email to GitHub Pages static site publishing.
3. This fork remains under GNU Affero General Public License Version 3 and keeps the license notice.

## License Compliance Statement (AGPLv3)

This repository declares that it does not violate the original GNU Affero General Public License Version 3 requirements.

Compliance actions in this fork:

1. Keep the AGPLv3 license in the repository.
2. Keep source code available for the modified work.
3. Keep clear attribution to upstream project and modification origin.
4. Preserve and publish modification history through Git commits.

## What This Project Does

The workflow runs daily and performs:

1. Read your Zotero library as interest corpus.
2. Retrieve new papers from arXiv/bioRxiv/medRxiv.
3. Rerank papers by semantic relevance.
4. Generate TLDR and affiliations with LLM.
5. Build static pages and deploy to GitHub Pages.

## Key Differences from Upstream

1. No SMTP email sending.
2. Output is a static website (latest page + history archive).
3. Deployment uses GitHub Pages artifact workflow.

## Features

1. Daily automatic updates via GitHub Actions.
2. Static site output for easy browsing and sharing.
3. Multi-source retrieval: arXiv, bioRxiv, medRxiv.
4. Reranking with local or API embedding backends.
5. Optional LLM-enriched TLDR and affiliations.
6. History retention with per-day snapshots.

## Quick Start

1. Fork this repository.
2. Enable GitHub Pages in your repository settings.
3. Configure repository secrets and variables.
4. Trigger workflow manually once to validate setup.
5. Visit the deployed Pages URL.

## Required Secrets

| Key | Description |
| :--- | :--- |
| ZOTERO_ID | Your Zotero user ID (numeric ID, not username). |
| ZOTERO_KEY | Zotero read-access API key. |
| OPENAI_API_KEY | LLM API key used for TLDR/affiliation generation. |
| OPENAI_API_BASE | LLM API base URL. |

## Required Repository Variable

Create repository variable CUSTOM_CONFIG and set YAML content.

Minimal example:

```yaml
zotero:
  user_id: ${oc.env:ZOTERO_ID}
  api_key: ${oc.env:ZOTERO_KEY}
  include_path: null

pages:
  output_dir: site
  site_title: Zotero arXiv Daily
  keep_days: 180
  generate_empty_page: true
  empty_message: No papers today. Take a rest!

source:
  arxiv:
    category: ["cs.AI", "cs.CV", "cs.LG", "cs.CL"]
    include_cross_list: false

llm:
  api:
    key: ${oc.env:OPENAI_API_KEY}
    base_url: ${oc.env:OPENAI_API_BASE}
  generation_kwargs:
    model: gpt-4o-mini

executor:
  debug: false
  source: ["arxiv"]
  reranker: local
```

## Configuration Reference

Main sections:

1. zotero: Zotero credentials and corpus path filters.
2. source: paper source-specific categories.
3. pages: static output behavior and history retention.
4. llm: model endpoint and generation settings.
5. reranker: local or API embedding reranker.
6. executor: pipeline switches and paper count limits.

Important runtime knobs:

1. executor.max_paper_num: maximum displayed/enriched papers.
2. pages.keep_days: number of days preserved in history.
3. pages.generate_empty_page: whether to render empty-day page.

## Workflow and Deployment

Daily workflow:

1. Build static site into site directory.
2. Upload Pages artifact.
3. Deploy with GitHub Pages deploy action.

Default schedule is in .github/workflows/main.yml.

## Local Run

Use uv to run locally:

```bash
cd zotero-arxiv-daily
uv run src/zotero_arxiv_daily/main.py
```

Before local run, export required environment variables or provide equivalent values in config.

## Limitations

1. Recommendation algorithm is still heuristic and may not fully represent user preference.
2. Large executor.max_paper_num increases runtime and API usage.
3. Upstream API/network instability can impact daily generation.

## Contribution

Issues and pull requests are welcome.

When contributing:

1. Keep upstream attribution intact.
2. Keep AGPLv3 compliance intact.
3. Prefer small, reviewable PRs with tests.

## Acknowledgements

1. Upstream project: https://github.com/TideDra/zotero-arxiv-daily
2. pyzotero: https://github.com/urschrei/pyzotero
3. arxiv.py: https://github.com/lukasschwab/arxiv.py
4. sentence-transformers: https://github.com/UKPLab/sentence-transformers

## License

Distributed under GNU Affero General Public License Version 3.

This fork keeps and follows AGPLv3 requirements and includes full source for modifications.
