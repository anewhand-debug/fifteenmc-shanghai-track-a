from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .paths import ProjectPaths


def _as_text_list(items: list[Any]) -> str:
    rendered: list[str] = []
    for item in items:
        if isinstance(item, dict):
            rendered.extend(f"{key}: {value}" for key, value in item.items())
        else:
            rendered.append(str(item))
    return "; ".join(rendered)


def load_data_sources(project_root: Path) -> dict[str, Any]:
    with (project_root / "config" / "data_sources.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_data_catalog(paths: ProjectPaths) -> pd.DataFrame:
    cfg = load_data_sources(paths.project_root)
    rows: list[dict[str, Any]] = []
    for dataset in cfg["datasets"]:
        local_key = dataset.get("local_path_key")
        local_path = paths.raw(local_key) if local_key in paths.config["raw_paths"] else None
        rows.append(
            {
                "dataset_id": dataset["id"],
                "title": dataset["title"],
                "source": dataset["source"],
                "collection_date": dataset["collection_date"],
                "local_path": str(local_path) if local_path else "",
                "exists": bool(local_path and local_path.exists()),
                "fields": _as_text_list(dataset.get("fields", [])),
                "cleaning": _as_text_list(dataset.get("cleaning", [])),
                "limitations": _as_text_list(dataset.get("limitations", [])),
            }
        )
    return pd.DataFrame(rows)


def write_catalog_markdown(catalog: pd.DataFrame, path: Path) -> Path:
    lines = [
        "# Data Dictionary",
        "",
        "This file is generated from `config/data_sources.yaml` and the local data inventory.",
        "",
    ]
    for row in catalog.to_dict("records"):
        lines.extend(
            [
                f"## {row['title']}",
                "",
                f"- Dataset ID: `{row['dataset_id']}`",
                f"- Source: {row['source']}",
                f"- Collection date: {row['collection_date']}",
                f"- Local path: `{row['local_path']}`",
                f"- Exists locally: `{row['exists']}`",
                f"- Fields: {row['fields']}",
                f"- Cleaning steps: {row['cleaning']}",
                f"- Limitations: {row['limitations']}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
