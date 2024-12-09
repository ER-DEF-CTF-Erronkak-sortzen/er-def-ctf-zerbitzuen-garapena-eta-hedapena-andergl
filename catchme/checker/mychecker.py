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
#PORT_DNS = 53
PORT_FTP = 21
PORT_WEB = 80
URL1 = 'http://www.catch.me'
WEBSTATE1 = 301
URL2 = 'http://intranet.catch.me'
WEBSTATE2 = 401
PORT_WEBS = 443
URLS1 = 'https://www.catch.me'
URLS2 = 'https://intranet.catch.me'
PORT_SSH = 23
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
        # check if DNS service is working (active and answiring all the requests)
        if not self._check_dns(self.ip):
            return checkerlib.CheckResult.FAULTY
        # check if FTP server is working and anonymous user can access
        if not self._check_ftp(self.ip):
            return checkerlib.CheckResult.FAULTY
        #
        # check if server is Apache 2.4.50
        if not self._check_apache_version():
            return checkerlib.CheckResult.FAULTY
        if not self._check_web(self.ip, URL1, PORT_WEB, WEBSTATE1):
            return checkerlib.CheckResult.FAULTY
        if not self._check_web(self.ip, URL2, PORT_WEB, WEBSTATE2):
            return checkerlib.CheckResult.FAULTY
        if not self._check_websecure(self.ip, URLS1, PORT_WEBS):
            return checkerlib.CheckResult.FAULTY
        if not self._check_websecure(self.ip, URLS2, PORT_WEBS):
            return checkerlib.CheckResult.FAULTY
        #if not self._check_port_ssh(self.ip, PORT_SSH):
        #    return checkerlib.CheckResult.FAULTY
        #else
        
        # check if dev1 user exists in pasapasa_ssh docker
        #if not self._check_ssh_user('heals'):
        #    return checkerlib.CheckResult.FAULTY
        #file_path_web = '/usr/local/apache2/htdocs/index.html'
        # check if index.hmtl from pasapasa_web has been changed by comparing its hash with the hash of the original file
        #if not self._check_web_integrity(file_path_web):
        #    return checkerlib.CheckResult.FAULTY            
        #file_path_ssh = '/etc/ssh/sshd_config'
        # check if /etc/sshd_config from pasapasa_ssh has been changed by comparing its hash with the hash of the original file
        #if not self._check_ssh_integrity(file_path_ssh):
        #    return checkerlib.CheckResult.FAULTY            
        return checkerlib.CheckResult.OK
    
    def check_flag(self, tick):
        if not self.check_service():
            return checkerlib.CheckResult.DOWN
        flag = checkerlib.get_flag(tick)
        #creds = checkerlib.load_state("flag_" + str(tick))
        # if not creds:
        #     logging.error(f"Cannot find creds for tick {tick}")
        #     return checkerlib.CheckResult.FLAG_NOT_FOUND
        flag_present = self._check_flag_present(flag)
        if not flag_present:
            return checkerlib.CheckResult.FLAG_NOT_FOUND
        return checkerlib.CheckResult.OK
        
    @ssh_connect()
    #Function to check if an user exists
    def _check_ssh_user(self, username):
        ssh_session = self.client
        command = f"docker exec catchme_ssh_1 sh -c 'id {username}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        return True
      
    @ssh_connect()
    def _check_web_integrity(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        
        output = stdout.read().decode().strip()
        return hashlib.md5(output.encode()).hexdigest() == 'a4ed71eb4f7c89ff868088a62fe33036'
    
    @ssh_connect()
    def _check_ssh_integrity(self, path):
        ssh_session = self.client
        command = f"docker exec catchme_ssh_1 sh -c 'cat {path}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        print (hashlib.md5(output.encode()).hexdigest())

        return hashlib.md5(output.encode()).hexdigest() == '39cff490d2bf197588ad0d0f9f24f906'
  
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
        command = f"docker exec catchme_ssh_1 sh -c 'grep {flag} /home/seeks/flag.txt'"
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

    def _check_ftp(self, ip):
        try:
            ftpconn = FTP()
            ftpconn.connect(ip, 21)
            ftpconn.login('anonymous','')           
            ftpconn.quit()
            return True
        except (error_perm, error_temp, error_reply) as e:
            print(f"Exception: {e}")
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


    def _check_port_ssh(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, port))
            return result == 0
        except socket.error as e:
            print(f"Exception: {e}")
            return False
        finally:
            sock.close()

    @ssh_connect()
    def _check_apache_version(self):
        ssh_session = self.client
        command = f"docker exec catchme_web_1 sh -c 'httpd -v | grep \"Apache/2.4.50\'"
        stdin, stdout, stderr = ssh_session.exec_command(command)

        if stdout:
            return True
        else:
            return False
  
if __name__ == '__main__':
    checkerlib.run_check(MyChecker)




