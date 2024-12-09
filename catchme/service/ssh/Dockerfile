FROM debian:latest
RUN apt update && apt install -y openssh-server

# Create user
RUN useradd -m heals && echo "heals:aIPOLLWn" | chpasswd
RUN chmod 700 /home/heals
RUN useradd -m swans && echo "swans:Vb3279fn" | chpasswd
RUN chmod 700 /home/swans
RUN useradd -m kulan && echo "kulan:3OlUDr7b" | chpasswd
RUN chmod 700 /home/kulan
RUN useradd -m furzy && echo "furzy:vfaVEF8s" | chpasswd
RUN chmod 700 /home/furzy


# Configure SSH
RUN mkdir /var/run/sshd

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]