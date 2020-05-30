FROM ubuntu:20.04
RUN \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install joe rsync zbackup python3 python3-pip openssh-client cron && \
    pip3 install toml && \
    mkdir config
WORKDIR /srv
COPY rsync_backup.py .
COPY config config
RUN \
    ln -s /srv/config/cron-backup /etc/cron.d/ && \
    chmod +x /srv/rsync_backup.py

CMD ["cron","-f"]
