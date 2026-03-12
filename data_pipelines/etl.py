import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_etl(input_path: str, output_path: str) -> None:
    """Run a simple PySpark ETL job: read CSV, aggregate, write Parquet."""
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, expr
    except ImportError:
        logger.warning("PySpark not available - skipping ETL")
        return

    spark = SparkSession.builder.appName("sales-etl").getOrCreate()

    logger.info(f"Reading data from {input_path}")
    df = spark.read.option("header", "true").csv(input_path)

    # Basic transformation: cast numeric types and compute total
    df = df.withColumn("quantity", col("quantity").cast("int"))
    df = df.withColumn("unit_price", col("unit_price").cast("double"))
    df = df.withColumn("total_amount", expr("quantity * unit_price"))

    # Aggregate by category
    agg = df.groupBy("category").sum("total_amount").withColumnRenamed("sum(total_amount)", "revenue")

    logger.info(f"Writing aggregated data to {output_path}")
    agg.write.mode("overwrite").parquet(output_path)

    spark.stop()


if __name__ == "__main__":
    input_path = os.environ.get("ETL_INPUT", "data/sample_sales.csv")
    output_path = os.environ.get("ETL_OUTPUT", "data/output_parquet")
    run_etl(input_path, output_path)

# added transformation 'add discount'%