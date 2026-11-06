val t_ctr_codpra_decifr =
  spark.read.parquet(conformedPath("t_ctr_codpra_decifr"))
    .filter(col("cod_contr").isin(1, 2))
    .select("COD_PRA", "COD_PRA_DECIFR")
    

override def leggiConformedDf: DataFrame = {

  val path = conformedPath(iniConf.conformedTableName)

  try {
    val conformedDf = spark.read.parquet(path)
    normalizzaCampi(conformedDf, conformedDf.schema)

  } catch {
    case _: AnalysisException =>
      // Inicializar el conformed vacío
      // con el esquema específico de TEveMvtcont
  }
}

override def scriviConformed(): Unit = {
  finalDf
    .repartition(2)
    .write
    .mode("append")
    .parquet(conformedPath(iniConf.conformedTableName))
}

