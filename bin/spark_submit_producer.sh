#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Variables
APP_NAME="ProducerApp"

# Use the directory to define the relative path to the log file
LOG_FILE="$DIR/logs/spark_submit_producer.log"
SPARK_APP_PATH="$DIR/src/main/producer_app.py"

# Additional jars and packages if necessary (e.g. Kafka dependencies)
PYSPARK_PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2"
PYSPARK_JARS=""

# Spark submit command
spark-submit \
    --name $APP_NAME \
    --master yarn \
    --deploy-mode client \
    --executor-memory 1G \
    --num-executors 2 \
    --executor-cores 2 \
    --driver-memory 1G \
    --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/path/to/log4j.properties" \
    --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:/path/to/log4j.properties" \
    --packages $PYSPARK_PACKAGES \
    --jars $PYSPARK_JARS \
    $SPARK_APP_PATH 2>&1 | tee -a $LOG_FILE
