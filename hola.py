# ============================================================
# DIRECT SPARK-SUBMIT TEST
# Bypass /usr/local/bin/spark-submit wrapper
# ============================================================

REAL_SPARK_SUBMIT="/opt/spark/bin/spark-submit"

echo
echo "========== DIRECT SPARK-SUBMIT TEST =========="
echo "Configured SPARK_SUBMIT=<$SPARK_SUBMIT>"
echo "REAL_SPARK_SUBMIT=<$REAL_SPARK_SUBMIT>"
echo

echo "========== FINAL VALUES =========="
printf 'JAR_FILE=[%q]\n' "$JAR_FILE"
printf 'INIFILE=[%q]\n' "$INIFILE"
printf 'DAT_COMP=[%q]\n' "$DAT_COMP"
printf 'ENV_OUTPUT_PATHS=[%q]\n' "$ENV_OUTPUT_PATHS"
echo "=================================="

if [ ! -x "$REAL_SPARK_SUBMIT" ]; then
    echo "ERROR: $REAL_SPARK_SUBMIT does not exist or is not executable"
    ls -la /opt/spark/bin/spark-submit 2>&1 || true
    exit 1
fi

$REAL_SPARK_SUBMIT \
    --master "$SPARK_MASTER_URL" \
    --deploy-mode cluster \
    --name "$SPARK_NAME" \
    --driver-cores "$DRIVER_CORES" \
    --driver-memory "$DRIVER_MEMORY" \
    --num-executors "$NUM_EXECUTORS" \
    --executor-cores "$EXECUTORS_CORE" \
    --executor-memory "$EXECUTORS_MEMORY" \
    --class it.findomestic.rio.Main \
    ${SPARK_CONF_TENANT} \
    --conf "spark.executor.extraJavaOptions=${SPARK_EXTRA_JAVA_OPTIONS}" \
    --conf "spark.driver.extraJavaOptions=${SPARK_EXTRA_JAVA_OPTIONS}" \
    $DEP_ENV_CONF \
    --conf "spark.kubernetes.driverEnv.ENV_OUTPUT_PATHS=$ENV_OUTPUT_PATHS" \
    --conf "spark.kubernetes.driverEnv.INI_FILE=$INIFILE" \
    --conf "spark.kubernetes.driverEnv.DAT_COMP=$DAT_COMP" \
    "$JAR_FILE"

exit_code=$?

echo "DIRECT SPARK-SUBMIT EXIT CODE=$exit_code"

rm -rf spark-submit-tmp-*

exit $exit_code




