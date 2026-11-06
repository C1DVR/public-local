val clt = spark.read.parquet(
  conformedPath("t_clt")
)


val clt_2 = spark.read.parquet(
  conformedPath("t_clt")
)

def letturaTabellaConformed(table: String): DataFrame = {
  val df = spark.read.parquet(conformedPath(table))
    .withColumn(
      "cod_clt_decifr",
      coalesce(
        col("cod_clt_decifr"),
        lit("999999999999999")
      ).cast("bigint")
    )
    .withColumn(
      "cod_pra_decifr",
      col("cod_pra_decifr").cast("bigint")
    )
    .select("cod_pra_decifr", "cod_clt_decifr")

  df
}




    
    