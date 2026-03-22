import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_etl(input_path: str, output_path: str) -> None:
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, expr, when, log1p
    except ImportError:
        logger.warning("PySpark not available - skipping ETL")
        return

    spark = SparkSession.builder.appName("sales-etl").getOrCreate()

    try:
        # -------------------------
        # Extract
        # -------------------------
        logger.info(f"Reading data from {input_path}")
        df = spark.read.option("header", "true").csv(input_path)

        # -------------------------
        # Validate schema (basic)
        # -------------------------
        required_cols = ["quantity", "unit_price", "category"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # -------------------------
        # Transform
        # -------------------------

        # Cast types
        df = df.withColumn("quantity", col("quantity").cast("int"))
        df = df.withColumn("unit_price", col("unit_price").cast("double"))

        # Filter low quantity (e.g., remove <= 0)
        df = df.filter(col("quantity") > 0)

        # Add discount logic (example: 10% off if quantity >= 10)
        df = df.withColumn(
            "discount",
            when(col("quantity") >= 10, col("unit_price") * 0.1).otherwise(0.0)
        )

        # Compute total with discount applied
        df = df.withColumn(
            "total_amount",
            (col("quantity") * (col("unit_price") - col("discount")))
        )

        # Log revenue (log transform for analytics)
        df = df.withColumn("log_revenue", log1p(col("total_amount")))

        # -------------------------
        # Aggregate
        # -------------------------
        agg = (
            df.groupBy("category")
              .sum("total_amount")
              .withColumnRenamed("sum(total_amount)", "revenue")
        )

        # Log aggregated results
        logger.info("Sample aggregated data:")
        agg.show(5)

        # -------------------------
        # Load
        # -------------------------
        logger.info(f"Writing aggregated data to {output_path}")
        agg.write.mode("overwrite").parquet(output_path)

    except Exception as e:
        logger.error(f"ETL failed: {e}", exc_info=True)
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    import sys
    run_etl(sys.argv[1], sys.argv[2])




# added transformation 'log revenue'