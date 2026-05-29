import os
from pathlib import Path


def logging_tmp_dir(app_name: str) -> Path:
    tmp_dir = Path(
        os.getenv(
            "LOGGING_TMP_DIR",
            os.getenv(
                "TMPDIR",
                str(Path.home() / ".cache" / app_name / "tmp"),
            ),
        )
    )

    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def app_logging_file(app_name: str, name: str) -> str:
    return str(logging_tmp_dir(app_name) / name)
