import xarray as xr
import pandas as pd
import h3
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, DoubleType, StructType, StructField

# 1. Convert NetCDF climate file to Parquet with H3 spatial indexing
def netcdf_to_h3_parquet(nc_file_path: str, output_parquet_path: str):
    # Load dataset using xarray
    ds = xr.open_dataset(nc_file_path)
    df = ds.to_dataframe().reset_index().dropna()
    
    # Initialize PySpark
    spark = SparkSession.builder \
        .appName("ClimateH3Indexer") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

    # Define H3 UDF
    @udf(returnType=StringType())
    def get_h3_index(lat, lon):
        try:
            return h3.geo_to_h3(float(lat), float(lon), resolution=7)
        except Exception:
            return None

    # Load into Spark DataFrame
    spark_df = spark.createDataFrame(df)
    
    # Add H3 Indexing column
    indexed_df = spark_df.withColumn("h3_index", get_h3_index("lat", "lon"))
    
    # Save partitioned Parquet file for fast querying
    indexed_df.write.mode("overwrite").partitionBy("h3_index").parquet(output_parquet_path)
    print(f"Successfully processed and indexed climate data to {output_parquet_path}")

if __name__ == "__main__":
    # Example execution (replace with path to your sample netCDF file)
    # netcdf_to_h3_parquet("data/sample_climate.nc", "data/processed_climate.parquet")
    pass