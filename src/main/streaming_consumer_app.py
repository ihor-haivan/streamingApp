from pyspark.sql import SparkSession
from pyhocon import ConfigFactory
from pyspark.sql.types import StringType
from pyspark.sql.functions import udf, current_timestamp, year, month, dayofmonth, hour
import logging
from src.helpers.parse_xml import parse_xml
from src.helpers.flatten_xml import flatten_xml


class StreamingConsumerApp:
    def __init__(
        self,
        config_path="configs/application.conf",
        log_path="logs/streaming_consumer_app.log",
    ):
        self.logger = self.setup_logging(log_path)
        self.spark = SparkSession.builder.appName("StreamingConsumerApp").getOrCreate()
        self.conf = ConfigFactory.parse_file(config_path)

        self.bootstrap_servers = self.conf.get_string("kafka.bootstrap.servers", None)
        self.kafka_topic = self.conf.get_string("kafka.topic", None)
        self.starting_offsets = self.conf.get_string("kafka.startingOffsets", None)
        self.hdfs_raw_zone_path = self.conf.get_string("hdfs.raw-zone-path", None)
        self.checkpoint_location = self.conf.get_string("checkpoint.location", None)

        self.parse_xml_udf = udf(parse_xml, StringType())

        if not all(
            [
                self.bootstrap_servers,
                self.kafka_topic,
                self.starting_offsets,
                self.hdfs_raw_zone_path,
                self.checkpoint_location,
            ]
        ):
            self.logger.error("Required configuration not found in config file!")
            raise ValueError("Missing configuration data")

    def setup_logging(self, log_path):
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger()

    def get_kafka_stream(self):
        stream = (
            self.spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", self.bootstrap_servers)
            .option("subscribe", self.kafka_topic)
            .option("startingOffsets", self.starting_offsets)
            .load()
        )

        # Add a timestamp column
        if "processing_time" not in stream.columns:
            stream = stream.withColumn("processing_time", current_timestamp())

        return stream

    def process_kafka_stream(self, kafka_df):
        kafka_df_with_watermark = kafka_df.withWatermark("processing_time", "1 hour")

        processed_df = (
            kafka_df_with_watermark.selectExpr("CAST(value AS STRING)")
            .withColumn("xml_content", self.parse_xml_udf("value"))
            .select(flatten_xml("xml_content"))
            .dropDuplicates()
        )

        return processed_df

    def kafka_to_hdfs(self):
        try:
            kafka_df = self.get_kafka_stream()
            processed_df = self.process_kafka_stream(kafka_df)

            # Extract year, month, day, hour from processing_time using built-in Spark functions
            processed_df = (
                processed_df.withColumn("year", year("processing_time"))
                .withColumn("month", month("processing_time"))
                .withColumn("day", dayofmonth("processing_time"))
                .withColumn("hour", hour("processing_time"))
            )

            # Streaming to HDFS with checkpointing for fault tolerance
            query = (
                processed_df.writeStream.format("parquet")
                .outputMode("overwrite")
                .option("path", self.hdfs_raw_zone_path)
                .option("checkpointLocation", self.checkpoint_location)
                .partitionBy("year", "month", "day", "hour")
                .start()
            )

            query.awaitTermination()
            self.logger.info("Data from Kafka written to HDFS RAW zone successfully!")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    app = StreamingConsumerApp()
    app.kafka_to_hdfs()
