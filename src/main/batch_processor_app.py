from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date, year, month, dayofmonth
from pyhocon import ConfigFactory
import logging
import time
from src.helpers.validate_and_format import validate_and_format


class BatchProcessorApp:
    def __init__(
        self,
        config_path="configs/application.conf",
        log_path="logs/batch_processor_app.log",
    ):
        self.logger = self.setup_logging(log_path)
        self.spark = SparkSession.builder.appName("BatchProcessorApp").getOrCreate()
        self.conf = ConfigFactory.parse_file(config_path)
        self.raw_zone_path = self.conf.get_string("hdfs.raw-zone-path", None)
        self.processed_zone_path = self.conf.get_string(
            "hdfs.processed-zone-path", None
        )
        self.xml_schema = self.conf.get_config("data.xml_schema")

        if not all([self.raw_zone_path, self.processed_zone_path]):
            self.logger.error("Required configuration not found in config file!")
            raise ValueError("Missing configuration data")

    def setup_logging(self, log_path):
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger()

    def raw_to_processed(self):
        start_time = time.time()  # for performance monitoring

        try:
            # Validate configurations
            self.validate_config_paths()

            # Extract today's year, month, and day to filter the specific partition
            today = current_date()
            current_year = year(today)
            current_month = month(today)
            current_day = dayofmonth(today)

            # Reading specific partition from HDFS RAW zone corresponding to today's date
            partition_path = f"{self.raw_zone_path}/year={current_year}/month={current_month}/day={current_day}"
            raw_df = self.spark.read.parquet(partition_path)

            # Schema validation, type validation, and formatting
            validated_df = validate_and_format(raw_df, self.xml_schema)

            # Processing logic
            processed_df = validated_df.withColumn("date_partition", today)

            num_partitions = 8

            # Repartition using coalesce before writing
            processed_df = processed_df.coalesce(num_partitions)

            # Writing to the Processed Zone, partitioned by date
            processed_df.write.option("partitionOverwriteMode", "dynamic").parquet(
                self.processed_zone_path, partitionBy="date_partition"
            )

            end_time = time.time()
            self.logger.info(
                f"Data transferred from RAW to Processed Zone successfully in {end_time - start_time:.2f} seconds!"
            )

        except Exception as e:
            # Handle exceptions
            self.logger.error(f"Error during raw to processed transformation: {e}")

    def validate_config_paths(self):
        """Validate that provided paths in the config are valid."""
        fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(
            self.spark._jsc.hadoopConfiguration()
        )
        if not (
            fs.exists(self.spark._jvm.org.apache.hadoop.fs.Path(self.raw_zone_path))
            and fs.exists(
                self.spark._jvm.org.apache.hadoop.fs.Path(self.processed_zone_path)
            )
        ):
            self.logger.error("Invalid path(s) provided in configuration!")
            raise ValueError("Invalid path(s) in configuration")


if __name__ == "__main__":
    app = BatchProcessorApp()
    app.raw_to_processed()
