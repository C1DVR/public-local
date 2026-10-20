
val archivo = Archivio("peointermediari", iniconf, competenza)

val peoIntermediariDf = archivo.mapped_df

val mapping = archivo.iniconfArchivio.mappingNomi

val tieneColumna = peoIntermediariDf.columns.exists(
  _.equalsIgnoreCase("COD_NDG_DECIFR")
)

if (!tieneColumna) {
  throw new IllegalStateException(
    "[RISKDB_MAPPING_ERROR] " +
    "INI_PATH=" + iniconf.inifilePath +
    " | MAPPING=" + mapping.toString +
    " | RAW_COLUMNS=" + archivo.raw_df.columns.mkString(",") +
    " | MAPPED_COLUMNS=" + peoIntermediariDf.columns.mkString(",")
  )
}
