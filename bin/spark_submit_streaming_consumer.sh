#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Variables
APP_NAME="StreamingConsumerApp"

# Use the directory to define the relative path to the log file
LOG_FILE="$DIR/logs/spark_submit_streaming_consumer.log"
SPARK_APP_PATH="$DIR/src/main/streaming_consumer_app.py"

# Additional jars and packages if necessary (e.g. Kafka and parquet dependencies)
PYSPARK_PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2,org.apache.spark:spark-sql_2.12:3.1.2"
PYSPARK_JARS=""

# Spark submit command
spark-submit \
    --name $APP_NAME \
    --master yarn \
    --deploy-mode client \
    --executor-memory 2G \
    --num-executors 3 \
    --executor-cores 2 \
    --driver-memory 2G \
    --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/path/to/log4j.properties" \
    --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:/path/to/log4j.properties" \
    --packages $PYSPARK_PACKAGES \
    --jars $PYSPARK_JARS \
    $SPARK_APP_PATH 2>&1 | tee -a $LOG_FILE
