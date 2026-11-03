"""CSV file access used by the repository layer.

The name describes the data access boundary; this prototype does not open a
database connection. The supplied CSV files remain the source of truth.
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


class CsvDataSource:
    """Read records from a fixed set of challenge CSV files."""

    ALLOWED_FILES = {
        "categories.csv",
        "customers.csv",
        "order_items.csv",
        "orders.csv",
        "products.csv",
        "promotions.csv",
    }

    def __init__(self, data_dir: Path = DEFAULT_DATA_DIR) -> None:
        self.data_dir = data_dir

    def read(self, filename: str) -> list[dict[str, str]]:
        if filename not in self.ALLOWED_FILES:
            raise ValueError(f"Unsupported data file: {filename}")
        path = self.data_dir / filename
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
