from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("BronzeToSilver").getOrCreate()
df = spark.read.format("delta").load("/data/bronze")
df = df.filter("status = 'active'")
df.write.mode("overwrite").format("delta").save("/data/silver")
