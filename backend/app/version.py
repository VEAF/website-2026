import os
from pathlib import Path


def _read_version() -> str:
    env_version = os.environ.get("APP_VERSION")
    if env_version:
        return env_version
    for path in [Path(__file__).resolve().parent.parent / "VERSION", Path("/app/VERSION")]:
        if path.is_file():
            return path.read_text().strip()
    return "dev"


APP_VERSION = _read_version()
