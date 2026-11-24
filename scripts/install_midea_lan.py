"""Install midea-lan declared by the integration manifest.json."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

MANIFEST_PATH = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "midea_ac_lan"
    / "manifest.json"
)


def _requirements() -> list[str]:
    """Return validated PEP 508 requirements from the integration manifest.

    Returns:
        The manifest's requirement strings.

    Raises:
        ValueError: If the manifest requirements field is not a string list.

    """
    manifest: dict[str, Any] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    requirements = manifest.get("requirements", [])
    if not isinstance(requirements, list) or not all(
        isinstance(item, str) for item in requirements
    ):
        raise ValueError(f"Invalid requirements in {MANIFEST_PATH}")
    return requirements


def main() -> None:
    """Install manifest requirements into the active Python environment."""
    requirements = _requirements()
    if not requirements:
        return

    command = [
        "uv",
        "pip",
        "install",
        "--python",
        sys.executable,
        "--reinstall-package",
        "midea-lan",
        *requirements,
    ]
    subprocess.run(command, check=True)
    subprocess.run(
        ["uv", "pip", "check", "--python", sys.executable],
        check=True,
    )


if __name__ == "__main__":
    main()
