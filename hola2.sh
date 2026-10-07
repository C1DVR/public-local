kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf \
-n spark-ap91055-dev-ae4d7e92 -- \
sh -c 'keytool -list -keystore /etc/ssl/certs/java/cacerts -storepass changeit 2>/dev/null | grep -i -E "BNPP|Applications|2014-2029"'


