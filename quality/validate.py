import os
import logging
from great_expectations.core import ExpectationSuite
from great_expectations.checkpoint import SimpleCheckpoint
from great_expectations.data_context import DataContext

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_data(data_path: str) -> bool:
    """Run Great Expectations validation on sales data CSV."""
    context_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "great_expectations"))
    context = DataContext(context_root)

    suite_name = "sales_suite"
    # create checkpoint dynamically
    checkpoint = SimpleCheckpoint(
        name="sales_checkpoint",
        data_context=context,
        validations=[
            {
                "batch_request": {
                    "datasource_name": "default",
                    "data_connector_name": "default_runtime_data_connector",
                    "data_asset_name": "sales",
                    "runtime_parameters": {"path": data_path},
                    "batch_identifiers": {"default_identifier_name": "default_identifier"},
                },
                "expectation_suite_name": suite_name,
            }
        ],
    )

    result = checkpoint.run()
    # result.result is a dictionary with nested results; check overall success
    success = result.success
    if success:
        logger.info("Validation passed")
    else:
        logger.warning("Validation failed")
    return success


if __name__ == "__main__":
    data_path = os.environ.get("GE_DATA", "data/sample_sales.csv")
    validate_data(data_path)
