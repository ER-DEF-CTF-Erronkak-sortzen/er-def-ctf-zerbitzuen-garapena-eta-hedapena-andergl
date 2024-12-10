FROM debian:latest
RUN apt update && apt install -y vsftpd

COPY ./vsftpd.conf /etc/vsftpd.conf

RUN mkdir /var/run/vsftpd
RUN chmod 755 /var/run/vsftpd
RUN mkdir /var/run/vsftpd/empty
RUN chmod 755 /var/run/vsftpd/empty

COPY ./.userlist /srv/ftp/.userlist

RUN useradd -m seeks && echo "seeks:2661DWdb" | chpasswd
RUN chmod 700 /home/seeks
COPY ./.sshusers /home/seeks/.sshusers
RUN useradd -m spuds && echo "spuds:IMREUUxi" | chpasswd
RUN chmod 700 /home/spuds
RUN useradd -m gleds && echo "gleds:O1SSX8TS" | chpasswd
RUN chmod 700 /home/gleds
RUN useradd -m avoid && echo "avoid:lVQVwQTM" | chpasswd
RUN chmod 700 /home/avoid


# Restart FTP server
CMD ["vsftpd"]
