private def readTable(name: String): DataFrame = {
  val table_df = spark.read.parquet(conformedPath(name))
  logging.log.debug(s"Count $name: ${table_df.count()}")
  table_df
}




    
    