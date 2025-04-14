#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Variables
APP_NAME="BatchProcessorApp"

# Use the directory to define the relative path to the log file
LOG_FILE="$DIR/logs/spark_submit_batch_processor.log"
SPARK_APP_PATH="$DIR/src/main/batch_processor_app.py"

# Additional jars and packages if necessary
PYSPARK_PACKAGES=""
PYSPARK_JARS=""

# Spark submit command
spark-submit \
    --name $APP_NAME \
    --master yarn \
    --deploy-mode client \
    --executor-memory 2G \
    --num-executors 2 \
    --executor-cores 2 \
    --driver-memory 2G \
    --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/path/to/log4j.properties" \
    --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:/path/to/log4j.properties" \
    --packages $PYSPARK_PACKAGES \
    --jars $PYSPARK_JARS \
    $SPARK_APP_PATH 2>&1 | tee -a $LOG_FILE
