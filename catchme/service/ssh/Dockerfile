FROM debian:latest
RUN apt update && apt install -y openssh-server

# Create user
RUN useradd -m heals && echo "heals:aIPOLLWn" | chpasswd
RUN useradd -m seeks && echo "seeks:2661DWdb" | chpasswd

# Configure SSH
RUN mkdir /var/run/sshd

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]