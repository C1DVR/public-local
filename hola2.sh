Hi team,

I have been investigating the SSL handshake / PKIX issue affecting the Migration Job in PREPROD. Since I don’t currently have access to the PREPROD Kubernetes pods/logs, I reproduced the checks from the DEV Spark environment to understand the expected configuration.

In DEV I confirmed the following:

* The hostname s01vl9901237.fr.net.intra resolves correctly to 10.244.215.142.
* Port 8443 is reachable from the Spark pod.
* The TLS handshake completes successfully.
* The server certificate matches s01vl9901237.fr.net.intra.
* Certificate verification succeeds without using curl -k.
* The certificate presented by the server is issued by 2014-2029 BNPP Applications.
* Java 17 is using the default cacerts truststore, resolved to /etc/ssl/certs/java/cacerts.
* The DEV Java truststore contains both:
    * 2014-2029bnppapplications
    * 2014-2044bnpproot

Therefore, the DEV environment already trusts the certificate chain used by this endpoint.

Since the actual SSLHandshakeException / PKIX path building failed occurs in PREPROD, our current hypothesis is that the Java truststore available to the Migration Job in PREPROD may not contain the same CA certificates, or that the PREPROD JVM is using a different truststore/configuration.

Could OPS please check this directly inside the PREPROD Migration Job driver pod?
keytool -list \
  -keystore /etc/ssl/certs/java/cacerts \
  -storepass changeit 2>/dev/null \
  | grep -i -E "BNPP|Applications|2014-2029"

java -XshowSettings:properties -version 2>&1 \
  | grep -i -E "trustStore|keyStore|java.home"

readlink -f /usr/lib/jvm/java-17-openjdk/lib/security/cacerts

The goal is to compare the PREPROD Java trust configuration with DEV and confirm whether 2014-2029 BNPP Applications / 2014-2044 BNPP Root are available there.

If they are missing in PREPROD, that would be consistent with the PKIX error and would also explain why we were provided with the .crt certificate. In that case, we can then determine the correct persistent way to make the certificate available to the Migration Job rather than manually modifying an ephemeral pod.

At this point, connectivity, DNS and TLS to the endpoint have been successfully validated from DEV, so I would first verify the PREPROD Java truststore before making further changes to the application configuration.



