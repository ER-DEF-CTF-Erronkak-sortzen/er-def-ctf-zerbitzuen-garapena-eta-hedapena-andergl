#!/usr/bin/env bash

docker stop catchme_dns_1 
docker stop catchme_ftp_1
docker stop catchme_ssh_1 
docker stop catchme_web_1
docker rm catchme_dns_1 
docker rm catchme_ftp_1
docker rm catchme_ssh_1 
docker rm catchme_web_1