echo "============================================================"
echo "=============== PRE SPARK-SUBMIT DIAGNOSTICS ==============="
echo "============================================================"

echo
echo "----- 1. BASIC VALUES -----"
echo "SPARK_SUBMIT=<$SPARK_SUBMIT>"
echo "SPARK_MASTER_URL=<$SPARK_MASTER_URL>"
echo "SPARK_NAME=<$SPARK_NAME>"
echo "JAR_FILE=<$JAR_FILE>"
echo "INIFILE=<$INIFILE>"
echo "DAT_COMP=<$DAT_COMP>"
echo "HOME_PROPERTIES=<$HOME_PROPERTIES>"
echo "HADOOP_CONF_SECRET=<$HADOOP_CONF_SECRET>"
echo "HADOOP_CONF_MOUNT_PATH=<$HADOOP_CONF_MOUNT_PATH>"
echo "ENV_OUTPUT_PATHS=<$ENV_OUTPUT_PATHS>"
echo "SPARK_HOME=<$SPARK_HOME>"
echo "PATH=<$PATH>"

echo
echo "----- 2. DEPENDENCY ENV VARS -----"
env | grep '^ENV_DEP_' || true

echo
echo "----- 3. GENERATED DEP_ENV_CONF -----"
printf '%s\n' "$DEP_ENV_CONF"

echo
echo "----- 4. SPARK CONFIG BLOCKS -----"

echo "### SPARK_CONF_TENANT"
printf '%s\n' "$SPARK_CONF_TENANT"

echo "### SPARK_CONF_SQL"
printf '%s\n' "$SPARK_CONF_SQL"

echo "### SPARK_CONF_COS"
printf '%s\n' "$SPARK_CONF_COS"

echo "### SPARK_EXTRA_JAVA_OPTIONS"
printf '%s\n' "$SPARK_EXTRA_JAVA_OPTIONS"

echo
echo "----- 5. SPARK-SUBMIT RESOLUTION -----"
echo "command -v spark-submit:"
command -v spark-submit || true

echo "type -a spark-submit:"
type -a spark-submit || true

echo "/usr/local/bin/spark-submit:"
ls -l /usr/local/bin/spark-submit 2>&1 || true

echo "/opt/spark/bin/spark-submit:"
ls -l /opt/spark/bin/spark-submit 2>&1 || true

echo
echo "----- 6. SPARK-SUBMIT WRAPPER CONTENT -----"
cat /usr/local/bin/spark-submit 2>&1 || true

echo
echo "----- 7. SPARK_HOME -----"
echo "SPARK_HOME=<$SPARK_HOME>"
ls -la "${SPARK_HOME:-/opt/spark}" 2>&1 || true
ls -la "${SPARK_HOME:-/opt/spark}/bin" 2>&1 || true

echo
echo "----- 8. SPARK DEFAULTS / CONFIG -----"

for f in \
    "${SPARK_HOME:-/opt/spark}/conf/spark-defaults.conf" \
    "/opt/spark/conf/spark-defaults.conf" \
    "/usr/local/spark/conf/spark-defaults.conf"
do
    echo "### CHECKING $f"
    if [ -f "$f" ]; then
        cat "$f"
    else
        echo "NOT FOUND"
    fi
done

echo
echo "----- 9. HADOOP CONF -----"
echo "HADOOP_CONF_DIR=<$HADOOP_CONF_DIR>"
echo "HADOOP_CONF_MOUNT_PATH=<$HADOOP_CONF_MOUNT_PATH>"

if [ -n "$HADOOP_CONF_DIR" ]; then
    ls -la "$HADOOP_CONF_DIR" 2>&1 || true
fi

if [ -n "$HADOOP_CONF_MOUNT_PATH" ]; then
    ls -la "$HADOOP_CONF_MOUNT_PATH" 2>&1 || true
fi

echo
echo "----- 10. RELEVANT ENVIRONMENT -----"
env | sort | grep -Ei \
'SPARK|HADOOP|KRB|KERBEROS|JAVA|CLASSPATH|JAR|CERT|SSL|TRUST|KEYSTORE|KEYTAB' \
|| true

echo
echo "----- 11. SEARCH FOR LOCAL FILE REFERENCES -----"
env | sort | grep -Ei \
'file:|/tmp|/opt|/usr|/var|/home|/etc|\.jar|\.jks|\.pem|\.crt|\.key|keytab|krb5|archives|files' \
|| true

echo
echo "----- 12. SHELL VARIABLES RELATED TO SPARK/HADOOP -----"
set | grep -Ei \
'^(SPARK|HADOOP|KRB|KERBEROS|JAVA|CLASSPATH|DEP_|ENV_DEP_|.*CERT|.*SSL|.*TRUST|.*KEYSTORE|.*KEYTAB)' \
|| true

echo
echo "----- 13. CHECK EACH GENERATED SPARK ARGUMENT FOR LOCAL FILES -----"

for conf_block in \
    "$SPARK_CONF_TENANT" \
    "$SPARK_CONF_SQL" \
    "$SPARK_CONF_COS" \
    "$DEP_ENV_CONF"
do
    printf '%s\n' "$conf_block" | \
    grep -Ei 'file:|/tmp|/opt|/usr|/var|/home|/etc|\.jar|\.jks|\.pem|\.crt|\.key|keytab|krb5|archives|files' \
    || true
done

echo
echo "----- 14. APPLICATION FILE ARGUMENTS -----"
echo "JAR_FILE=$JAR_FILE"
echo "INIFILE=$INIFILE"

echo
echo "----- 15. IMPORTANT SPARK K8S PROPERTIES -----"
env | grep -Ei \
'spark.kubernetes.file.upload.path|spark.jars|spark.files|spark.archives|spark.submit.pyFiles' \
|| true

echo
echo "============================================================"
echo "=============== END PRE-SUBMIT DIAGNOSTICS ================="
echo "============================================================"

set -x