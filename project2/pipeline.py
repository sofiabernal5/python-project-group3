import logging
import sys
from datetime import datetime
from pathlib import Path

from api_client import fetch_all_cities, CITIES
from storage import save_all

# ── Logging setup ─
LOG_DIR  = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("pipeline")


def run_pipeline(cities: list[dict] = CITIES) -> int:
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("=" * 60)
    logger.info("Pipeline run started at %s", run_ts)
    logger.info("=" * 60)

    all_records, failed_cities = fetch_all_cities(cities)

    print(f"\n{'─'*50}")
    print(f"Cities processed : {len(cities) - len(failed_cities)}/{len(cities)}")
    if failed_cities:
        print(f"Failed cities    : {', '.join(failed_cities)}")
    print(f"Total records    : {len(all_records):,}")

    if all_records:
        print("\nSample records (first 3):")
        for rec in all_records[:3]:
            print(" ", rec)

    print("\nSaving data...")
    save_all(all_records)

    logger.info("Pipeline run complete. %d records saved.", len(all_records))
    return len(all_records)


def main():
    total = run_pipeline()
    if total == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()