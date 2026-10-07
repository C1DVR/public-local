kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf \
-n spark-ap91055-dev-ae4d7e92 -- \
sh -c 'java -XshowSettings:properties -version 2>&1 | grep -i -E "trustStore|keyStore|java.home"'


