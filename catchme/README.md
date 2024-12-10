# Service definition:
- We have four dockers on a Debian 12 machine: 
1. An SSH server (OpenSSH, listening on port 23), which contains the flag. It is located in heals user's home directories (/home/heals). Besides, there are other three users: furcy, kulan and swans. Each user has its own home directory, and despite they can move through the whole system and they can list the four directories under /home, as they have 700 permissions, only the owners can go inside and list/see the content (so, the flag is only accessible for heals user).
2. A DNS server (bind9, listening on port 53 UDP), which resolves www.catch.me and intranet.catch.me domain names into the Debian 12 machine's IP address (10.0.x.101, being x the team number).
3. An HTTP/HTTPS server (apache2, listening on ports 80 & 443), with two websites (VirtualHosts): www.catch.me and intranet.catch.me, both listening on 80 (HTTP) and 443 (HTTPS) ports:
  3.a. http://www.catch.me HTTP website requests redirect to https://www.catch.me. The HTTPS website is located on /usr/local/apache2/htdocs/www/ directory. For accessing the site, a certificate warning appears, because it is an autosigned certificate, and should be accepted in order to view the main webpage (index.html). It is a very simple website, that informs you where you are (www.catch.me website) and with a link to https://intranet.catch.me.
  3.b. https://intranet.catch.me HTTPS website is located on /usr/local/apache2/htdocs/intranet/ directory. For accessing the site, a certificate warning appears, because it is an autosigned certificate, and should be accepted in order to view the main webpage (index.html). It is a very simple website, that informs you where you are (intranet.catch.me website) and with a link to https://www.catch.me.
  3.c. http://intranet.catch.me HTTP website requests DO NOT to https://intranet.catch.me. The HTTP website is located on /usr/local/apache2/htdocs/intranet-old/ directory. When trying to access, a login prompt appears for accessing using user and password. This access does not work, but the file that is normally used in these situations (.htaccess) is accesible due to a configuration error (.ht* files aren't accessible by default on Apache2 servers). .htaccess file points to another file (.htpasswd) in which a list of 20 users/passwords appears. Besides, a commentary is written on the last line, recommending to check another file (.ht-ftpusers) in which another list of 21 users/passwords appears.
4. An FTP server (vsftpd, listening on port 21 and using port 20 for data transfer), with anonymous access enabled (user anonymous with no password). Anonymous user falls on /srv/ftp directory and it is jailed in it (so, it cannot see the whole system file). A hidden file (.userlist) is located on /srv/ftp directory in which a list of 20 users/passwords appears. Four local users (avoid, gleds, seeks and spuds) can also access to the FTP server. They fall on their respective home directory but they are not jailed there. Despite they can move through the whole system and they can list the four directories under /home, as they have 700 permissions, only the owners can go inside and list/see/download the content. A hidden file (.sshusers) is located on /home/seeks directory in which a list of 20 users/passwords appears.


# Service implementation:
dns docker is configured to install bind9 and to take a copy of the following files from the host machine and letting them in the specified location:
- named.conf.local --> /etc/bind/named.conf.local (the zone definition file, which contains the definition of catch.me zone and points to the zone resolution file, which is /etc/bind/db.catch.me)
- db.catch.me --> /etc/bind/db.catch.me (the zone resolution file for catch.me zone)
Finally, it sarts the server through named daemon.

ftp docker is configured to install vsftpd and to take a copy of the following files from the host machine and letting them in the specified location:
- vsftpd.conf --> /etc/vsftpd.conf (the vsftpd configuration file)
- .userlist --> /srv/ftp/.userlist (a fake user/password list, leading to a dead end)
- .sshusers --> /home/seeks/.sshusers (the user/password list to be used on SSH server)
It is also configured for creating /var/run/vsftpd/empty directory not to give an access error.
Besides, it must create 4 users and change the permissions of their respective home directories to 700.
Finally, it sarts the server through vsftpd daemon.
*Notice that in docker-compose.yml file "restart: unless-stopped" have been stated because ftp docker wasn't stable and went down several times without any apparent reason (normally, just after closing a connection, but not always). So, unless we manually execute "docker stop catchme_ftp_1", it will automatically start again.
*TIP: Maybe would be a good idea to apply this parameter to all the dokcers.

web docker is configured to use httpd 2.4.50 and to take a copy of the following files from the host machine and letting them in the specified location: 
- conf/httpd.conf --> /usr/local/apache2/conf/httpd.conf (main configuration file of httpd)
- conf/extra/httpd-vhosts.conf --> /usr/local/apache2/conf/extra/httpd-vhosts.conf (VirtualHost configuration file of httpd, where the four virtual hosts are defined)
- conf/www.catch.me.key --> /usr/local/apache2/conf/www.catch.me.key (the private key of https://www.catch.me)
- conf/www.catch.me.crt --> /usr/local/apache2/conf/www.catch.me.crt (the public certificate of https://www.catch.me)
- conf/intranet.catch.me.key --> /usr/local/apache2/conf/intranet.catch.me.key (the private key of https://intranet.catch.me)
- conf/intranet.catch.me.crt --> /usr/local/apache2/conf/intranet.catch.me.crt (the public certificate of https://intranet.catch.me)
Additionally, the directories for https://www.catch.me, https://intranet.catch.me and http://intranet.catch.me must be created and the correspondent files copied to that directories:
- www/index.html /usr/local/apache2/htdocs/www/index.html (https://www.catch.me website)
- intranet/index.html /usr/local/apache2/htdocs/intranet/index.html (https://intranet.catch.me website)
- intranet-old/index.html /usr/local/apache2/htdocs/intranet-old/index.html (http://intranet.catch.me website)
- intranet-old/.htaccess /usr/local/apache2/htdocs/intranet-old/.htaccess (a hidden file on http://intranet.catch.me website)
- intranet-old/.htpasswd /usr/local/apache2/htdocs/intranet-old/.htpasswd (a hidden file on http://intranet.catch.me website)
- intranet-old/.ht-ftpusers /usr/local/apache2/htdocs/intranet-old/.ht-ftpusers (a hidden file on http://intranet.catch.me website)

ssh docker is configured to install openssh-server and:
Create four users and to change the permissions of their respective home directories to 700.
Create /var/run/sshd directory to work.
Finally, it sarts the server through sshd daemon.

-Flag: 
    Flag will be stored in 'catchme_ssh_1' docker's '/home/heals/flags.txt' file. 


# Checker checks:
- DNS server is active and working. Working means:
  - Resolves 'www.catch.me' domain name into 10.0.x.101 IP address, being x the attacked team number.
  - Resolves 'intranet.catch.me' domain name into 10.0.x.101 IP address, being x the attacked team number.
If not, service's status becomes FAULTY.
* Checks done:
  * Stop the container on 10.0.1.101 ('root@debian:~# docker stop catchme_dns_1'): service's status of Team1 becomes FAULTY.
  * Change the ip parameter by '10.0.1.101' value on mychecker.py script: service's status of Team2 becomes FAULTY.

- FTP server is active and working. Working means:
  - anonymous user can login to FTP server
  - seeks user can login to FTP server
- /home/seeks/.sshusers file on FTP server hasn't been changed using its hash
If not, service's status becomes FAULTY.
* Checks done:
  * Stop the container on 10.0.1.102 ('root@debian:~# docker stop catchme_ftp_1'): service's status of Team2 becomes DOWN (this is very strange, it should be FAULTY, becauyse I haven't define any situation in which a service status becomes DOWN).
  * Change the password of seeks user on the container on 10.0.1.101: service's status of Team1 becomes FAULTY.
  * Change /home/seeks/.sshusers file content on the container on 10.0.1.101: service's status of Team1 becomes FAULTY.

- SSH server is active and working. Working means:
  - listens on port 23
  - heals user can login to SSH server
* Checks done:
  * Stop the container on 10.0.1.101 ('root@debian:~# docker stop catchme_ftp_1'): service's status of Team1 becomes FAULTY.
  * Change the password of heals user on the container on 10.0.1.102: service's status of Team2 becomes FAULTY.
  * Delete the flag file (/home/heals/flag.txt) on SSH container on 10.0.1.101: service's status of Team1 becomes RECOVERING during 5/6 Ticks (the time needed to refill the flag file with 5 new flags) and Team1 loses about 6 points. Once there are 5 flags in the file, status becomes UP again.
  
- WEB server is active and working. Working means:
  - HTTP/HTTPS server is Apache 2.4.50
  - http://www.catch.me redirects (301)
  - http://intranet.catch.me asks for a login (401)
  - https://www.catch.me is available
  - https://intranet.catch.me is available
  - HTTP/HTTPS config files (httpd.conf and extra/httpd-vhosts.conf) haven't been changed using their hash
  - HTTP/HTTPS content files haven't been changed using their hash:
    - /usr/local/apache2/htdocs/www/index.html
    - /usr/local/apache2/htdocs/intranet/index.html
    - /usr/local/apache2/htdocs/intranet-old/.htaccess
    - /usr/local/apache2/htdocs/intranet-old/.htpasswd
    - /usr/local/apache2/htdocs/intranet-old/.ht-ftpusers
* Checks done:
  * Stop the container on 10.0.1.102 ('root@debian:~# docker stop catchme_web1'): service's status of Team2 becomes FAULTY.
  * Modify /usr/local/apache2/conf/httpd.conf config file on container on 10.0.1.101 docker: service's status of Team1 becomes FAULTY.
  * Modify /usr/local/apache2/htdocs/intranet-old/.htaccess file on container on 10.0.1.101 docker: service's status of Team1 becomes FAULTY.

Every time a service falls in FAULTY status, the team will be losing SLa points. 
 

# The attack step by step
Information provided to the attacker:
- There is a DNS server on 10.0.x.101, being x the attacked team number
- There is a domain name: www.catch.me

The attacker must set its default DNS server on attacked machine (10.0.x.101, being x the attacked team number), so it can get the same IP address as an answer for both www.catch.me and intranet.catch.me domain names.

The attacker has access to https://www.catch.me web page (with this URL directly or redirected from http://www.catch.me or redirected from http://10.0.x.101). They can surf between https://www.catch.me and https://intranet.catch.me, using the links on both websites, but they won't find anything interesting.
NOTE: As both HTTPS websites use self-signed certificates, the certificates must be trusted and an exception added in order to access the websites.

In order to access the website we are interested in (http://intranet.catch.me), an HTTP connection must be forced to intranet.catch.me (notice that HTTP connections to the IP address will lead you to http://www.catch.me, and consequently, to http://www.catch.me).

Once the promt for user/password login appears, attacker should try to access the file that is normally forbidden (.htaccess), which will be accessible. Reading this file, they will open .htpasswd, skipping the list of 20 users/passwords (that will lead to a dead end) and reading the commentary on the last line of this file, they will open .ht-ftpusers file, which contains another list of 21 users/passwords (including anonymous user).

The list of users/passwords in .ht-ftpusers file should be checked on the FTP server. The result will be:
- anonymous user can log in and can see a hidden file (.userlist), which contains a list of 20 users/passwords that leads to a dead end.
- 16 users and passwords are not valid in any server.
- 3 users (avoid, gleds and spuds) can access the FTP server, they can see their respective home directory but they cannot go ahead. The only thing is that they can see the list of directories in /home so they can guess which users have access and which ones haven't access to the FTP server.
- Finally, seeks user ('2661DWdb' password) can also access the FTP server, and will find a hidden file (.sshusers) on its home directory (/home/seeks), which contains a list of 20 users/passwords.

The list of users/passwords in .sshusers file should be checked on the SSH server (remember that the port of this SSH server is 23, because port 22 is occupied for infrastructure purposes). The result will be:
- 16 users and passwords are not valid.
- 3 users (furcy, kulan and swans) can access the SSH server, they can see their respective home directory but they cannot go ahead. The only thing is that they can see the list of directories in /home so they can guess which users have access and which ones haven't access to the SSH server.
- Finally, heals user ('aIPOLLWn' password) can also access the SSH server, and will find the flag in its home directory (/home/heals/flag.txt).

Attacker has to let the flag in his T-Submission machine, in a file with .flag extension located at /root directory (as, for example, /root/flag.flag). 


# The attack - result
* Team1 captures the flag (in fact, the last 5 flags) from Team2: Team1 gets 10 points (2 per flag) and Team2 loses 5 points (1 per flag and attacker). The final command has been, from Team1's T-Submission machine (10.0.1.1):
  * root@debian:~# scp -P 23 heals@10.0.2.101:/home/heals/flag.txt ./flag.flag
  * Brief explanation: via scp (SSH), using heals:aIPOLLWn credentials, the current flag (/home/heals/flag.txt) of Team2 is copied on /root directory as xx.flag (the name is not important but the extension is) so the checker can count it for the scoreboard.


# The attack using an exploit:
We assume that:
- The attacker has accessed all the attacked machines using SSH, so the fingerprint of all 10.0.x.101 machines is already stored on T-Submission machine. If not, attacker must access manually each teams service machine for the first time before using the exploit script.
- "sshpass" package must be installed first on T-Submission machine (apt install sshpass).

The exploit is very simple, consists on a shell script that is a loop, from 1 to the last team's number, and executes the following command for all the attacked teams:
  sshpass 'aIPOLLWn' scp -P 23 heals@10.0.$i.101:/home/heals/flag.txt /root/flag$i.flag
So, for each team, copies their respective flag in the correct directory and with a correct name, one name per attacked team, so a flag does not overwrite the previous one.

In order to make the attack persistent, a periodical command must be placed in crontab (crontab -e), to be executed once for each Tick. For example, if the Tick value is 1 minute and the exploit is located at /root/exploit.sh (remember that must have execution permissions 'chmod +x'), the crontab line should be the following:
* * * * * /root/exploit.sh

The attacker will earn 2 points per flag (in each Tick) and defender will lose 1 point per flag (in each Tick).

     


# License notes
Parts from:
https://github.com/kristianvld/SQL-Injection-Playground



