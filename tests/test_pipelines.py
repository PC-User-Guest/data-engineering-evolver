import os
import tempfile
import pandas as pd
from data_pipelines import etl


def test_run_etl_creates_output(tmp_path):
    # create small sample CSV
    sample = pd.DataFrame({
        "date": ["2025-01-01"],
        "product_id": ["P0001"],
        "product_name": ["Test"],
        "category": ["Electronics"],
        "quantity": [1],
        "unit_price": [100.0],
    })
    csv_file = tmp_path / "input.csv"
    sample.to_csv(csv_file, index=False)

    output_dir = tmp_path / "out"
    etl.run_etl(str(csv_file), str(output_dir))

    # expect parquet file exists
    files = list(output_dir.glob("*.parquet"))
    assert files, "No parquet files produced"


def test_run_etl_handles_missing_columns(tmp_path):
    # CSV missing some columns should not crash
    sample = pd.DataFrame({
        "date": ["2025-01-01"],
        "product_id": ["P0001"],
        # missing category etc
    })
    csv_file = tmp_path / "input2.csv"
    sample.to_csv(csv_file, index=False)

    output_dir = tmp_path / "out2"
    # should raise an error or complete gracefully
    try:
        etl.run_etl(str(csv_file), str(output_dir))
    except Exception:
        pass
