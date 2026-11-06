val cod_pra_hash_mapped_df =
  spark.read.parquet(conformedPath("t_ctr_df"))
    .select("cod_pra", "cod_pra_decifr", "cod_mast_ori_decifr")
    
    val cod_ndg_hash_mapped_df =
  spark.read.parquet(conformedPath("t_sup_codndg_decifr"))
    .select("cod_ndg", "cod_ndg_decifr")
    
    