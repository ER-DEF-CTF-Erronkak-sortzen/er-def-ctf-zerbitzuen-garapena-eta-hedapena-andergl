FROM debian:latest
RUN apt update && apt install -y openssh-server

# Create user
RUN useradd -m dev1 && echo "dev1:w3ar3h4ck3r2" | chpasswd

# Configure SSH
RUN mkdir /var/run/sshd

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]