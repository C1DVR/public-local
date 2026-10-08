DEV certificate / Java truststore investigation – steps followed

The purpose of these checks was to understand why the Migration Job works correctly in DEV with SSL enabled, and to identify where the Java trust relationship is coming from.

1. Connect to the DEV Kubernetes cluster / namespace

After IBM login and loading the DEV Spark context, verify the current namespace:

echo $K8SNAMESPACE

In DEV this was:

spark-ap91055-dev-ae4d7e92


2. List the pods in the DEV Spark namespace

kubectl get pods -n spark-ap91055-dev-ae4d7e92

This allowed us to identify an old Migration Job driver pod that had completed successfully:

migrationjob-336939a0f3020fc4-driver


3. Inspect the successful Migration Job pod

kubectl describe pod migrationjob-336939a0f3020fc4-driver -n spark-ap91055-dev-ae4d7e92

From this we confirmed several mounted configurations, including:

/hadoop-conf
/opt/spark/hadoop-conf-dh
/opt/spark/ssl

The pod was also using the Spark image and Java environment used by the Migration Job.


4. Check the logs of the successful Migration Job

kubectl logs migrationjob-336939a0f3020fc4-driver -n spark-ap91055-dev-ae4d7e92 | tail -100

The logs confirmed that the job really completed successfully:

JOB STARTED !!
...
Hive DB: hist_risk_db_prod
...
JOB SUCCESS!!

The connection parameters used by the job included:

host=s01vl9901237.fr.net.intra
port=8443
ssl=true
transportMode=http
httpPath=gateway/default/hive


5. Check DNS resolution from a running Spark pod

A running Spark UI pod was used only for connectivity tests:

sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf

DNS check:

kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- getent hosts s01vl9901237.fr.net.intra

Result:

s01vl9901237.fr.net.intra resolved correctly to 10.244.215.142


6. Check TCP connectivity to port 8443

kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- nc -vz s01vl9901237.fr.net.intra 8443

Result:

s01vl9901237.fr.net.intra (10.244.215.142:8443) open

This confirmed that DNS and network connectivity were working correctly from DEV.


7. Check the TLS handshake and certificate validation

First, the endpoint was tested with curl:

kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- curl -v --connect-timeout 10 https://s01vl9901237.fr.net.intra:8443/

The important result was:

SSL certificate verify ok.

The certificate hostname matched:

s01vl9901237.fr.net.intra

The certificate issuer was:

2014-2029 BNPP Applications

The HTTP response was 404, which is expected when calling "/" directly and is not relevant for the TLS validation itself.


8. Check which Java installation is being used

kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- sh -c 'java -XshowSettings:properties -version 2>&1 | grep -i -E "trustStore|keyStore|java.home"'

Result:

java.home = /usr/lib/jvm/java-17-openjdk

No custom javax.net.ssl.trustStore was shown, so Java appears to be using its default truststore.


9. Locate the default Java cacerts truststore

kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- sh -c 'ls -l /usr/lib/jvm/java-17-openjdk/lib/security/cacerts; readlink -f /usr/lib/jvm/java-17-openjdk/lib/security/cacerts'

Result:

/usr/lib/jvm/java-17-openjdk/lib/security/cacerts -> /etc/ssl/certs/java/cacerts

So the Java default truststore used in DEV is:

/etc/ssl/certs/java/cacerts


10. Check whether the BNPP CA certificates are already present in Java cacerts

kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- sh -c 'keytool -list -keystore /etc/ssl/certs/java/cacerts -storepass changeit 2>/dev/null | grep -i -E "BNPP|Applications|2014-2029|2014-2044"'

Result:

2014-2029bnppapplications, ..., trustedCertEntry
2014-2044bnpproot, ..., trustedCertEntry


Conclusion

The DEV environment does not appear to use an application-specific Java truststore for the Hive JDBC connection.

Java 17 is using the default cacerts truststore:

/etc/ssl/certs/java/cacerts

That truststore already contains the BNPP CA certificates required to validate the certificate presented by:

s01vl9901237.fr.net.intra:8443

In particular:

2014-2029bnppapplications
2014-2044bnpproot

This explains why the Migration Job can connect successfully in DEV without explicitly configuring a custom truststore in the DAG, spark-submit, or application code.

The next logical comparison is to perform the same checks in PREPROD/PROD and verify whether those environments have the same CA certificates provisioned in their default Java cacerts.