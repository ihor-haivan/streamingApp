from pyspark.sql import SparkSession
from pyhocon import ConfigFactory
import logging


class ProducerApp:
    def __init__(
        self, config_path="configs/application.conf", log_path="logs/producer_app.log"
    ):
        self.logger = self.setup_logging(log_path)
        self.spark = SparkSession.builder.appName("ProducerApp").getOrCreate()
        self.conf = ConfigFactory.parse_file(config_path)

        self.bootstrap_servers = self.conf.get_string("kafka.bootstrap.servers", None)
        self.kafka_topic = self.conf.get_string("kafka.topic", None)

        if not all([self.bootstrap_servers, self.kafka_topic]):
            self.logger.error("Required configuration not found in config file!")
            raise ValueError("Missing configuration data")

    def setup_logging(self, log_path):
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger()

    def create_sample_data(self):
        xml_data = [
            (
                "<book><title>Harry Potter</title><author><fname>J.K.</fname><lname>Rowling</lname></author></book>",
            ),
            (
                "<book><title>Lord of the Rings</title><author><fname>J.R.R.</fname><lname>Tolkien</lname></author></book>",
            ),
        ]
        return self.spark.createDataFrame(xml_data, ["xml_content"])

    def stream_to_kafka(self):
        try:
            df = self.create_sample_data()
            df.writeStream.format("kafka").trigger(processingTime="10 seconds").option(
                "kafka.bootstrap.servers", self.bootstrap_servers
            ).option("topic", self.kafka_topic).start().awaitTermination()

            self.logger.info("Data streamed to Kafka successfully!")
        except Exception as e:
            self.logger.error(f"Error streaming to Kafka: {e}")


if __name__ == "__main__":
    app = ProducerApp(
        config_path="configs/application.conf", log_path="logs/producer_app.log"
    )
    app.stream_to_kafka()
