val cod_pra_hash_mapped_df =
  spark.read.parquet(conformedPath("t_ctr_codpra_decifr"))
    .select("cod_pra", "cod_pra_decifr")
    
val cod_clt_hash_mapped_df =
  spark.read.parquet(conformedPath("t_clt_codclt_decifr"))
    .select("cod_clt", "cod_clt_decifr")
    
    