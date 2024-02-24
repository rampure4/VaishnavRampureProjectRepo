FROM p5-base

WORKDIR /spark-3.5.0-bin-hadoop3

CMD ./sbin/start-master.sh && sleep infinity
