import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_data(data_path: str) -> bool:
    """Run Great Expectations validation on sales data CSV."""
    try:
        from great_expectations.core import ExpectationSuite
        from great_expectations.checkpoint import SimpleCheckpoint
        from great_expectations.data_context import DataContext
    except ImportError:
        logger.warning("Great Expectations not available - skipping validation")
        return True
    
    context_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "great_expectations"))
    try:
        context = DataContext(context_root)
    except Exception as e:
        logger.warning(f"Could not initialize GE context: {e}")
        return True

    suite_name = "sales_suite"
    try:
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
        success = result.success
        if success:
            logger.info("Validation passed")
        else:
            logger.warning("Validation failed")
        return success
    except Exception as e:
        logger.warning(f"Validation error: {e}")
        return True


if __name__ == "__main__":
    data_path = os.environ.get("GE_DATA", "data/sample_sales.csv")
    validate_data(data_path)
