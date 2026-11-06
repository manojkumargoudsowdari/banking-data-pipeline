import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from spark.utils.spark_session import create_spark_session


def main():
    spark = create_spark_session("Lab 01 - Spark Architecture")

    try:
        context = spark.sparkContext

        print("Application name:", context.appName)
        print("Application ID:", context.applicationId)
        print("Spark master:", context.master)
        print("Default parallelism:", context.defaultParallelism)
        print("Spark UI:", context.uiWebUrl)
        print(
            "Shuffle partitions:",
            spark.conf.get("spark.sql.shuffle.partitions"),
        )

        # Step 1: Define the input path.
        customers_path = (
            PROJECT_ROOT
            / "data"
            / "standardized"
            / "customers"
            / "load_date=2026-06-16"
            / "customers.parquet"
        )

        print("\nCustomer input path:", customers_path)

        # Step 2: Create the source DataFrame.
        customers_df = spark.read.parquet(str(customers_path))

        print("Customer columns:", customers_df.columns)
        print("Customer partitions:", customers_df.rdd.getNumPartitions())

        # Step 3: Define a lazy filter transformation.
        active_customers_df = customers_df.filter(
            customers_df.customer_status == "ACTIVE"
        )

        print("\nActive customer filter created.")
        print("The active customer count has not been requested yet.")

        input(
            "\nInspect the Jobs tab before count(). "
            "Press Enter to execute count()..."
        )

        # Step 4: Trigger execution with the count action.
        active_customer_count = active_customers_df.count()

        print("\nActive customer count:", active_customer_count)

        input(
            "\nCount completed. Inspect Jobs and Stages. "
            "Press Enter to continue to the grouped aggregation..."
        )

        # Step 5: Define a grouped aggregation.
        status_counts_df = customers_df.groupBy("customer_status").count()

        print("\nCustomer status aggregation plan:")
        status_counts_df.explain("formatted")

        print(
            "\nThe aggregation DataFrame and its plan now exist, "
            "but show() has not executed yet."
        )

        input(
            "\nInspect the Jobs and SQL tabs before show(). "
            "Press Enter to execute show()..."
        )

        # Step 6: Trigger the grouped aggregation.
        print("\nCustomer counts by status:")

        status_counts_df.orderBy("customer_status").show(
            truncate=False
        )

        input(
            "\nGrouped aggregation completed. "
            "Inspect Jobs, Stages, and SQL/DataFrame tabs. "
            "Press Enter to stop Spark..."
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()