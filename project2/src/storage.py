import logging
import sqlite3
from pathlib import Path

import pandas as pd

# Sets up the directory for processed data and ensures it exists
DATA_DIR = Path("data/processed")
DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = DATA_DIR / "weather_data.csv"
DB_PATH  = DATA_DIR / "weather_data.db"
TABLE    = "weather"

# Set up logging for the storage module
logger = logging.getLogger(__name__)
logging.getLogger("storage").addHandler(logging.NullHandler())

# Helper function to convert a list of dictionaries into a pandas DataFrame
def _to_dataframe(records: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(records)


def save_csv(df: pd.DataFrame) -> None:
    """Save the DataFrame to a CSV file, appending if the file already exists."""
    first_run = not CSV_PATH.exists()
    df.to_csv(CSV_PATH, mode="a", index=False, header=first_run)
    logger.info(
        "%s %d rows to %s.",
        "Wrote" if first_run else "Appended",
        len(df),
        CSV_PATH,
    )
    print(f"  CSV  → {CSV_PATH}  ({len(df)} rows {'written' if first_run else 'appended'})")


def save_sqlite(df: pd.DataFrame) -> None:
    """Save the DataFrame to an SQLite database, appending if the table already exists."""
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(TABLE, conn, if_exists="append", index=False)
    logger.info("Appended %d rows to SQLite table '%s' at %s.", len(df), TABLE, DB_PATH)
    print(f"  SQLite → {DB_PATH}  (table: {TABLE}, {len(df)} rows appended)")


def save_all(records: list[dict]) -> None:
    """Save all records to both CSV and SQLite. If no records are provided, log a warning and do nothing."""
    if not records:
        logger.warning("save_all called with no records - nothing to save.")
        print("  No records to save.")
        return

    df = _to_dataframe(records)
    logger.info("Saving %d records...", len(df))

    save_csv(df)
    save_sqlite(df)