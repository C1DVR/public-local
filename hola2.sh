kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- getent hosts s0lv19901237.fr.net.intra

kubectl exec -it sparkui-ap91055-dev-ae4d7e92-spark-ui-df4dbc98b-n54bf -n spark-ap91055-dev-ae4d7e92 -- sh -c 'echo | openssl s_client -connect s0lv19901237.fr.net.intra:8443 -servername s0lv19901237.fr.net.intra -showcerts 2>/dev/null'