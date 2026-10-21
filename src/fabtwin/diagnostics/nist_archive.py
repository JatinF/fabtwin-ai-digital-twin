"""Read the committed NIST SEM metrics archive.

The Dice means are copied from the NIST CSV files. FabTwin does not run the
U-Net that produced them.
"""

from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from pathlib import Path

from fabtwin.paths import nist_dir

SOURCE = "https://doi.org/10.18434/mds2-3838"
ACCESSED = "2026-10-21"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def global_dice(archive: Path | None = None) -> list[dict]:
    zip_path = nist_dir() / "metrics_sets.zip" if archive is None else archive
    rows = []
    with zipfile.ZipFile(zip_path) as bundle:
        names = sorted(name for name in bundle.namelist() if name.endswith("dice-coef-global.csv"))
        for name in names:
            text = bundle.read(name).decode("utf-8")
            record = next(csv.DictReader(io.StringIO(text)))
            rows.append(
                {
                    "path": name,
                    "arithmetic_mean": float(record["ARITHMETIC-MEAN"]),
                    "standard_deviation": float(record["STANDARD-DEVIATION"]),
                    "evidence_class": "SPEC",
                    "source": SOURCE,
                    "accessed": ACCESSED,
                    "unet_executed_by_fabtwin": False,
                }
            )
    return rows


def archive_manifest() -> dict:
    folder = nist_dir()
    readme = folder / "README.txt"
    metrics = folder / "metrics_sets.zip"
    return {
        "doi": SOURCE,
        "accessed": ACCESSED,
        "readme_bytes": readme.stat().st_size,
        "readme_sha256": file_sha256(readme),
        "metrics_zip_bytes": metrics.stat().st_size,
        "metrics_zip_sha256": file_sha256(metrics),
        "global_dice": global_dice(metrics),
        "intensity_sets_zip": "not-downloaded",
        "aimodel_sets_zip": "not-downloaded",
        "unet_executed_by_fabtwin": False,
    }
