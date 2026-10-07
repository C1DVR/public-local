kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf \
-n spark-ap91055-dev-ae4d7e92 -- \
sh -c 'ls -l /usr/lib/jvm/java-17-openjdk/lib/security/cacerts; readlink -f /usr/lib/jvm/java-17-openjdk/lib/security/cacerts'


