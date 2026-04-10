import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from api_client import fetch_all_cities, CITIES
from storage import save_all

# Set up logging for the pipeline
LOG_DIR  = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure logging to write to both a file and the console, with a specific format
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
    """Run the data fetching and saving pipeline for the specified list of cities."""

    # Log the start of the pipeline run with a timestamp
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("=" * 60)
    logger.info("Pipeline run started at %s", run_ts)
    logger.info("=" * 60)

    # Fetch weather data for all cities and keep track of any that failed
    all_records, failed_cities = fetch_all_cities(cities)

    # Print a summary of the results, including how many cities were processed successfully and which ones failed
    print(f"\n{'─'*50}")
    print(f"Cities processed : {len(cities) - len(failed_cities)}/{len(cities)}")
    if failed_cities:
        print(f"Failed cities    : {', '.join(failed_cities)}")
        logger.warning("The following cities could not be fetched: %s", ", ".join(failed_cities))
    print(f"Total records    : {len(all_records):,}")

    # If there are any successful records, print a sample of the first few to give an idea of the data structure
    if all_records:
        print("\nSample records (first 3):")
        for rec in all_records[:3]:
            print(" ", rec)

    print("\nSaving data...")
    # Attempt to save all the fetched records, and log any errors that occur during saving
    try:
        save_all(all_records)
    except Exception as e:
        logger.error("Data could not be saved. Reason: %s", e)
        print(f"\n  Something went wrong while saving: {e}")
        print("  No data was written this run.")
        return 0

    # Log the successful completion of the pipeline run and how many records were saved
    logger.info("Pipeline run complete. %d records saved.", len(all_records))
    return len(all_records)


def main():
    """Main function to parse command-line arguments and run the pipeline."""

    # Set up an argument parser to allow users to specify which cities to fetch data for, 
    # or default to all cities if none are specified
    parser = argparse.ArgumentParser(description="Fetch weather data for one or more cities.")
    parser.add_argument(
        "--cities",
        nargs="+",
        metavar="CITY",
        help="One or more city names to fetch (must match a name in CITIES). Defaults to all cities.",
    )
    args = parser.parse_args()

    # If specific cities were provided, filter the CITIES list to include only those
    if args.cities:
        selected = [c for c in CITIES if c["name"].lower() in {n.lower() for n in args.cities}]
        unknown = [n for n in args.cities if n.lower() not in {c["name"].lower() for c in CITIES}]
        # Warn about any unknown city names that were provided
        if unknown:
            print(f"Warning: these cities are not in the list and will be skipped: {', '.join(unknown)}")
        # If none of the provided city names were recognized, print the available cities and exit
        if not selected:
            print("None of the provided city names were recognized. Available cities:")
            for c in CITIES:
                print(f"  {c['name']}")
            sys.exit(1)
    else:
        selected = CITIES

    # Run the pipeline with the selected cities and check if any records were saved. If not, exit with an error code.
    total = run_pipeline(selected)
    if total == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()