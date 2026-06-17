import os
from pathlib import Path

if not os.getenv("BANKING_PIPELINE_USE_EXTERNAL_SPARK_HOME"):
    os.environ.pop("SPARK_HOME", None)

if os.getenv("HADOOP_HOME") and not Path(os.environ["HADOOP_HOME"]).exists():
    os.environ.pop("HADOOP_HOME", None)

from pyspark.sql import SparkSession


def create_spark_session(app_name="Banking Raw To Standardized"):
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
