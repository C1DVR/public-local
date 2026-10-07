kubectl get pod migrationjob-336939a0f3020fc4-driver \
  -n spark-ap91055-dev-ae4d7e92 \
  -o yaml | grep -i -E "ssl|truststore|keystore|javax.net.ssl|certificate" -C 3

kubectl get pod migrationjob-336939a0f3020fc4-driver \
  -n spark-ap91055-dev-ae4d7e92 \
  -o yaml | grep -i -E "javaOptions|extraJavaOptions|JAVA_TOOL_OPTIONS|SPARK_SUBMIT_OPTS" -C 3
  
  kubectl get secret dh-hadoop-conf \
  -n spark-ap91055-dev-ae4d7e92 \
  -o jsonpath='{.data.core-site\.xml}' | base64 -d
  
  kubectl get secret secret-hdfs-site-ap91055 \
  -n spark-ap91055-dev-ae4d7e92 \
  -o jsonpath='{.data.hdfs-site\.xml}' | base64 -d
  