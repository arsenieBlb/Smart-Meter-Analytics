from __future__ import annotations

import argparse

try:
    from .clean_data import clean_dataset, validate_dataset
    from .config import Settings
    from .generate_synthetic_data import generate_synthetic_data
    from .load_to_postgres import load_csvs_to_postgres
    from .utils import ensure_directories, summarize_dataset, write_dataframes_to_csv
except ImportError:  # pragma: no cover
    from clean_data import clean_dataset, validate_dataset  # type: ignore
    from config import Settings  # type: ignore
    from generate_synthetic_data import generate_synthetic_data  # type: ignore
    from load_to_postgres import load_csvs_to_postgres  # type: ignore
    from utils import ensure_directories, summarize_dataset, write_dataframes_to_csv  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Smart Meter Analytics data pipeline.")
    parser.add_argument("--load-postgres", action="store_true", help="Load generated CSVs into PostgreSQL after export.")
    parser.add_argument("--sample-size", type=int, default=250, help="Rows to export into data/sample_exports for each table.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings()
    ensure_directories(settings.raw_data_dir, settings.processed_data_dir, settings.sample_export_dir)

    synthetic = generate_synthetic_data(settings)
    cleaned = clean_dataset(synthetic.datasets)
    written_paths = write_dataframes_to_csv(
        cleaned,
        settings.processed_data_dir,
        settings.sample_export_dir,
        sample_size=args.sample_size,
    )
    validation_results = validate_dataset(cleaned)
    summary = summarize_dataset(cleaned, synthetic.metadata["duplicate_records_created"])

    should_load = args.load_postgres or settings.load_to_postgres
    if should_load:
        load_csvs_to_postgres(settings.processed_data_dir, settings)

    print("\nSmart Meter Analytics pipeline complete")
    print("-" * 60)
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value:,}")
    print(f"Validation Checks Passed: {(validation_results['status'] == 'PASS').sum()} / {len(validation_results)}")
    failed_checks = validation_results[validation_results["status"] != "PASS"]
    if not failed_checks.empty:
        print("Validation Findings:")
        for row in failed_checks.itertuples(index=False):
            print(f"- {row.check_name}: {row.failed_records:,} records")
        print("Note: the synthetic generator intentionally creates a small number of quality issues for demo purposes.")
    print(f"Loaded To PostgreSQL: {'Yes' if should_load else 'No'}")
    print("\nOutput files:")
    for name, path in written_paths.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
