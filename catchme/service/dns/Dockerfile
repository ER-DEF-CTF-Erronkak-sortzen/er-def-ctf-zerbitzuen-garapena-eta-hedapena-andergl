FROM debian:latest
RUN apt update && apt install -y bind9

COPY ./named.conf.local /etc/bind/named.conf.local
COPY ./db.catch.me /etc/bind/db.catch.me


CMD ["/usr/sbin/named", "-g", "-c", "/etc/bind/named.conf"]