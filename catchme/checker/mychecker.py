#!/usr/bin/env python3

from ctf_gameserver import checkerlib
import logging
import http.client
import socket
import ssl
from urllib.parse import urlparse
import dns.resolver
import dns.exception
from ftplib import FTP
from ftplib import error_perm, error_temp, error_reply
import paramiko
import hashlib
#FTP variables
PORT_FTP = 21
FTPUSER = 'seeks'
FTPPASSWD = '2661DWdb'
FTPPATH = '/home/seeks/.sshusers'
#WEB variables
PORT_WEB = 80
URL1 = 'http://www.catch.me'
WEBSTATE1 = 301
URL2 = 'http://intranet.catch.me'
WEBSTATE2 = 401
PORT_WEBS = 443
URLS1 = 'https://www.catch.me'
URLS2 = 'https://intranet.catch.me'
WEBCONF = '/usr/local/apache2/conf/httpd.conf'
WEBCONFEXTRA = '/usr/local/apache2/conf/extra/httpd-vhosts.conf'
WEBWWW = '/usr/local/apache2/htdocs/www/index.html'
WEBINTRANET = '/usr/local/apache2/htdocs/intranet/index.html'
WEBHTACCESS = '/usr/local/apache2/htdocs/intranet-old/.htaccess'
WEBHTPASSWD = '/usr/local/apache2/htdocs/intranet-old/.htpasswd'
WEBFTPUSERS = '/usr/local/apache2/htdocs/intranet-old/.ht-ftpusers'
#SSH variables
PORT_SSH = 23
SSHUSER = 'heals'
SSHPASSWD = 'aIPOLLWn'

def ssh_connect():
    def decorator(func):
        def wrapper(*args, **kwargs):
            # SSH connection setup
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            rsa_key = paramiko.RSAKey.from_private_key_file(f'/keys/team{args[0].team}-sshkey')
            client.connect(args[0].ip, username = 'root', pkey=rsa_key)

            # Call the decorated function with the client parameter
            args[0].client = client
            result = func(*args, **kwargs)

            # SSH connection cleanup
            client.close()
            return result
        return wrapper
    return decorator

class MyChecker(checkerlib.BaseChecker):

    def __init__(self, ip, team):
        checkerlib.BaseChecker.__init__(self, ip, team)
        self._baseurl = f'http://[{self.ip}]:{PORT_WEB}'
        logging.info(f"URL: {self._baseurl}")

    @ssh_connect()
    def place_flag(self, tick):
        flag = checkerlib.get_flag(tick)
        creds = self._add_new_flag(self.client, flag)
        if not creds:
            return checkerlib.CheckResult.FAULTY
        logging.info('created')
        checkerlib.store_state(str(tick), creds)
        checkerlib.set_flagid(str(tick))
        return checkerlib.CheckResult.OK

    def check_service(self):
        # check if DNS service is active and working (answering all the requests):
          # www.catch.me --> 10.0.x.101
          # intranet.catch.me --> 10.0.x.101
        if not self._check_dns(self.ip):
            return checkerlib.CheckResult.FAULTY
        
        # check if FTP server is working, anonymous user can access and seeks user can access
        if not self._check_ftp(self.ip, FTPUSER, FTPPASSWD):
            return checkerlib.CheckResult.FAULTY
          # check if .sshusers file on /home/seeks/ of FTP server hasn't been changed using its hash
        if not self._check_ftp_filehash(FTPPATH):
            return checkerlib.CheckResult.FAULTY
        
        # check that SSH server is listening on port 23 and that user heals can connect
        if not self._check_ssh(self.ip, PORT_SSH, SSHUSER, SSHPASSWD):
            return checkerlib.CheckResult.FAULTY

        # check if HTTP/HTTPS server is Apache 2.4.50
        if not self._check_apache_version():
            return checkerlib.CheckResult.FAULTY
        # check if HTTP/HTTPS server is available and working well
          # check that http://www.catch.me redirects (301)
        if not self._check_web(self.ip, URL1, PORT_WEB, WEBSTATE1):
            return checkerlib.CheckResult.FAULTY
          # check that http://intranet.catch.me asks for a login (401)
        if not self._check_web(self.ip, URL2, PORT_WEB, WEBSTATE2):
            return checkerlib.CheckResult.FAULTY
          # check that https://www.catch.me is available
        if not self._check_websecure(self.ip, URLS1, PORT_WEBS):
            return checkerlib.CheckResult.FAULTY
          # check that https://intranet.catch.me is available
        if not self._check_websecure(self.ip, URLS2, PORT_WEBS):
            return checkerlib.CheckResult.FAULTY
          # check if HTTP/HTTPS config files haven't been changed using their hash
        if not self._check_webconf(WEBCONF):
            return checkerlib.CheckResult.FAULTY
        if not self._check_webconfextra(WEBCONFEXTRA):
            return checkerlib.CheckResult.FAULTY
          # check if /usr/local/apache2/htdocs/www/index.html file hasn't been changed using its hash
        if not self._check_webwww(WEBWWW):
            return checkerlib.CheckResult.FAULTY
          # check if /usr/local/apache2/htdocs/intranet/index.html file hasn't been changed using its hash
        if not self._check_webintranet(WEBINTRANET):
            return checkerlib.CheckResult.FAULTY
          # check if /usr/local/apache2/htdocs/intranet-old/.htaccess file hasn't been changed using its hash
        if not self._check_webhtaccess(WEBHTACCESS):
            return checkerlib.CheckResult.FAULTY
          # check if /usr/local/apache2/htdocs/intranet-old/.htpasswd file hasn't been changed using its hash
        if not self._check_webhtpasswd(WEBHTPASSWD):
            return checkerlib.CheckResult.FAULTY
          # check if /usr/local/apache2/htdocs/intranet-old/.ht-ftpusers file hasn't been changed using its hash
        if not self._check_webftpusers(WEBFTPUSERS):
            return checkerlib.CheckResult.FAULTY


        # if all the services are OK          
        return checkerlib.CheckResult.OK
    

    def check_flag(self, tick):
        if not self.check_service():
            return checkerlib.CheckResult.FAULTY
        flag = checkerlib.get_flag(tick)
        #creds = checkerlib.load_state("flag_" + str(tick))
        # if not creds:
        #     logging.error(f"Cannot find creds for tick {tick}")
        #     return checkerlib.CheckResult.FLAG_NOT_FOUND
        flag_present = self._check_flag_present(flag)
        if not flag_present:
            return checkerlib.CheckResult.FLAG_NOT_FOUND
        return checkerlib.CheckResult.OK
        
    
    
    
    
  
    # Private Funcs - Return False if error
    def _add_new_flag(self, ssh_session, flag):
        # Execute the file creation command in the container
        command = f"docker exec catchme_ssh_1 sh -c 'echo {flag} >> /home/heals/flag.txt'"
        stdin, stdout, stderr = ssh_session.exec_command(command)

        # Check if the command executed successfully
        if stderr.channel.recv_exit_status() != 0:
            return False
        
        # Return the result
        return {'flag': flag}

    @ssh_connect()
    def _check_flag_present(self, flag):
        ssh_session = self.client
        command = f"docker exec catchme_ssh_1 sh -c 'grep {flag} /home/heals/flag.txt'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False

        output = stdout.read().decode().strip()
        return flag == output



    def _check_dns(self, ip):
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [ip]
            answerwww = resolver.resolve('www.catch.me')
            answerintranet = resolver.resolve('intranet.catch.me')
            www = False
            for ipaddress in answerwww:
                www = www or (ipaddress.to_text() == ip)
            intranet = False
            for ipaddress in answerintranet:
                intranet = intranet or (ipaddress.to_text() == ip)
            return www and intranet
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException) as e:
            return False

    def _check_ftp(self, ip, ftpuser, ftppasswd):
        try:
            ftpconn = FTP()
            ftpconn.connect(ip, 21)
            ftpconn.login('anonymous','')           
            ftpconn.quit()
            ftpconn = FTP()
            ftpconn.connect(ip, 21)
            ftpconn.login(ftpuser, ftppasswd)           
            ftpconn.quit()
            return True
        except (error_perm, error_temp, error_reply) as e:
            print(f"Exception: {e}")
            return False
            
    @ssh_connect()
    def _check_ftp_filehash(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_ftp_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == 'b5e980d39d9236678edd943a7aafcec7'

    def _check_ssh(self, host, port, user, passwd):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(host, port, user, passwd)
            return True
        except paramiko.AuthenticationException:
            return False
        except paramiko.SSHException as e:
            return False
        except Exception as e:
            return False
        finally:
            ssh_client.close()
    
    @ssh_connect()
    def _check_apache_version(self):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'httpd -v | grep \"Apache/2.4.50\'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stdout:
            return True
        else:
            return False

    def _check_web(self, ip, url, port, state):
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [ip]
        answer = resolver.resolve(host, 'A')
        ip_address = answer[0].to_text()
        try:
            conn = http.client.HTTPConnection(ip_address, port, timeout=5)
            conn.request("GET", "/", headers={'Host': host})
            response = conn.getresponse()          
            #return True
            return response.status == state
        except (http.client.HTTPException, socket.error) as e:
            print(f"Exception: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def _check_websecure(self, ip, url, port):
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [ip]
        answer = resolver.resolve(host, 'A')
        ip_address = answer[0].to_text()
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((ip_address, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as secure_sock:            
                    return True
        except ssl.SSLError as e:
            return False
        except Exception as e:
            return False    

    @ssh_connect()
    def _check_webconf(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == '8f2c783e646ebbd9d66a2388b254620f'
    
    @ssh_connect()
    def _check_webconfextra(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == '2b41a2fbe194b4ddf857274ecfc46025'

    @ssh_connect()
    def _check_webwww(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == 'c74fcb9904a61e23fab4150567c9bcad'

    @ssh_connect()
    def _check_webintranet(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == '17fb24bc09456a804b24618d8b7e951b'

    @ssh_connect()
    def _check_webhtaccess(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == 'aeea405c63889b842b91677be7f4799f'

    @ssh_connect()
    def _check_webhtpasswd(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == 'd262026f177c1b4d0e73105b1037da11'

    @ssh_connect()
    def _check_webftpusers(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == '8d28dab82d38bf9b95e82b7c58de6d31'




    
if __name__ == '__main__':
    checkerlib.run_check(MyChecker)




