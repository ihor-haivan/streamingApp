from pyspark.sql.functions import col, trim
from pyspark.sql.types import StructType, StructField, StringType
import logging


def validate_and_format(df, expected_schema=None):
    """
    Function to validate and format the dataframe.
    """
    try:
        # Schema Validation
        if expected_schema:
            if not isinstance(expected_schema, StructType):
                raise TypeError("Expected schema should be of type StructType")

            actual_columns = set(df.columns)
            expected_columns = set(expected_schema.fieldNames())

            missing_columns = expected_columns - actual_columns
            extra_columns = actual_columns - expected_columns
            if missing_columns:
                raise ValueError(
                    f"Missing columns in the dataframe: {', '.join(missing_columns)}"
                )
            if extra_columns:
                logging.warning(
                    f"Extra columns in the dataframe: {', '.join(extra_columns)}"
                )

            # Data Type Validation
            for field in expected_schema:
                assert isinstance(
                    field, StructField
                ), "Each field in the expected schema should be of type StructField"
                actual_dtype = df.schema[field.name].dataType
                expected_dtype = field.dataType
                if actual_dtype != expected_dtype:
                    raise TypeError(
                        f"Column '{field.name}' has datatype {actual_dtype}, but {expected_dtype} was expected"
                    )

        # Data formatting
        # Filter only string columns
        string_columns = [
            f.name for f in df.schema.fields if isinstance(f.dataType, StringType)
        ]

        # Apply trim to string columns using a list comprehension
        trimmed_cols = [
            trim(col(column_name)).alias(column_name)
            if column_name in string_columns
            else col(column_name)
            for column_name in df.columns
        ]

        # Use select to apply all transformations
        df = df.select(*trimmed_cols)

        logging.info("Data validated and formatted successfully.")
        return df

    except Exception as e:
        logging.error(f"Error during validation and formatting: {e}")
        raise e  # Rethrow the exception to be caught/handled at a higher level if necessary
