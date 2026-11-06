def letturaTabellaConformed(table: String): DataFrame = {
  val df = spark.read.parquet(conformedPath(table))




    
    