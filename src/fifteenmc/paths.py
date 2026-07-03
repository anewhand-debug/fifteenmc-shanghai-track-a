from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def _project_root_from_file() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    project_root: Path
    raw_data_root: Path
    config: dict[str, Any]

    def project(self, *parts: str) -> Path:
        return self.project_root.joinpath(*parts)

    def raw(self, key: str) -> Path:
        rel = self.config["raw_paths"][key]
        return self.raw_data_root / rel

    def output(self, key: str) -> Path:
        rel = self.config["outputs"][key]
        return self.project_root / rel

    def directory(self, key: str) -> Path:
        rel = self.config["directories"][key]
        return self.project_root / rel


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_project_paths(project_root: str | Path | None = None) -> ProjectPaths:
    root = Path(project_root).resolve() if project_root else _project_root_from_file()
    config = load_yaml(root / "config" / "paths.yaml")
    raw_env = config.get("raw_data_root_env", "FIFTEENMC_RAW_DATA_ROOT")
    raw_root = Path(os.getenv(raw_env, config["default_raw_data_root"])).resolve()
    return ProjectPaths(project_root=root, raw_data_root=raw_root, config=config)
