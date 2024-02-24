FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y wget unzip bash

COPY count.sh /count.sh
RUN chmod u+x /count.sh

CMD ["/count.sh"]

