FROM debian:latest
RUN apt update && apt install -y vsftpd

COPY ./vsftpd.conf /etc/vsftpd.conf
COPY ./.userlist /srv/ftp/.userlist

#RUN mkdir /var/run/vsftpd
#RUN chmod 755 /var/run/vsftpd
#RUN mkdir /var/run/vsftpd/empty
#RUN chmod 755 /var/run/vsftpd/empty

# Restart FTP server
CMD ["vsftpd"]
