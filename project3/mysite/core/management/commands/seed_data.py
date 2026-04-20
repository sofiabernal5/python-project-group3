import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import AirQualityRecord, DataRun, Location

DEFAULT_CSV = Path(__file__).resolve().parents[5] / "project1" / "data" / "raw" / "us_pollution.csv"

FIELD_MAP = {
    "O3 Mean":           "o3_mean",
    "O3 1st Max Value":  "o3_1st_max_value",
    "O3 1st Max Hour":   "o3_1st_max_hour",
    "O3 AQI":            "o3_aqi",
    "CO Mean":           "co_mean",
    "CO 1st Max Value":  "co_1st_max_value",
    "CO 1st Max Hour":   "co_1st_max_hour",
    "CO AQI":            "co_aqi",
    "SO2 Mean":          "so2_mean",
    "SO2 1st Max Value": "so2_1st_max_value",
    "SO2 1st Max Hour":  "so2_1st_max_hour",
    "SO2 AQI":           "so2_aqi",
    "NO2 Mean":          "no2_mean",
    "NO2 1st Max Value": "no2_1st_max_value",
    "NO2 1st Max Hour":  "no2_1st_max_hour",
    "NO2 AQI":           "no2_aqi",
}


def _float(value):
    value = value.strip()
    return float(value) if value else None


def _int(value):
    value = value.strip()
    return int(float(value)) if value else None


class Command(BaseCommand):
    help = "Load the Project 1 air quality CSV into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=str(DEFAULT_CSV),
            help="Path to the CSV file.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing AirQualityRecords before seeding.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Stop after loading this many rows (useful for testing).",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["file"])
        if not csv_path.exists():
            raise CommandError(
                f"CSV file not found: {csv_path}\n"
                f"Pass the correct path with --file <path>."
            )

        if options["clear"]:
            deleted, _ = AirQualityRecord.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing records."))

        run = DataRun.objects.create(source="csv", notes=f"Seeded from {csv_path.name}")

        created_count = 0
        updated_count = 0
        error_count   = 0
        limit         = options["limit"]

        self.stdout.write(f"Reading {csv_path} ...")

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            with transaction.atomic():
                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break

                    try:
                        if row["Date"].strip() < "2022-01-01":
                            continue

                        location, _ = Location.objects.get_or_create(
                            address=row["Address"].strip(),
                            city=row["City"].strip(),
                            state=row["State"].strip(),
                            defaults={"county": row["County"].strip()},
                        )

                        pollutant_fields = {}
                        for csv_col, model_field in FIELD_MAP.items():
                            raw = row.get(csv_col, "")
                            if model_field.endswith("_aqi") or model_field.endswith("_hour"):
                                pollutant_fields[model_field] = _int(raw)
                            else:
                                pollutant_fields[model_field] = _float(raw)

                        _, created = AirQualityRecord.objects.update_or_create(
                            location=location,
                            date=row["Date"].strip(),
                            defaults={"source": "csv", "data_run": run, **pollutant_fields},
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    except Exception as exc:
                        error_count += 1
                        self.stderr.write(f"  Row {i + 2} skipped -- {exc}")

        run.records_created = created_count
        run.records_updated = updated_count
        run.notes += f" | errors: {error_count}"
        run.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone!  {created_count} created, {updated_count} updated, {error_count} errors."
            )
        )