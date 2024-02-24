FROM p5-base

WORKDIR /spark-3.5.0-bin-hadoop3

CMD ./sbin/start-worker.sh spark://boss:7077 -c 1 -m  512M && sleep infinity

