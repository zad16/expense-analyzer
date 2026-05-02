# Rclone Google Drive Setup Guide

This document explains how to set up `rclone` to mount a Google Drive folder as a local file system on a Linux server (like EC2 or GCP).

## 1. Install Dependencies
You need `rclone` and `fuse` (Filesystem in Userspace) to mount cloud storage.

On Amazon Linux / CentOS / RHEL:
```bash
sudo yum install -y fuse fuse3 unzip
curl https://rclone.org/install.sh | sudo bash
```

On Ubuntu / Debian:
```bash
sudo apt update
sudo apt install -y rclone fuse3 unzip
```

## 2. Configure Rclone
Create the configuration directory:
```bash
mkdir -p ~/.config/rclone
```

Create or upload your `rclone.conf` file to `~/.config/rclone/rclone.conf`.
If you are generating a new token, run:
```bash
rclone config
```
- Type `n` for New remote.
- Name it `gdrive`.
- Choose `drive` for Google Drive.
- Leave Client ID and Secret blank.
- Choose scope `1` (Full access).
- Follow the prompt to authenticate via your web browser.

## 3. Test the Connection
Verify rclone can see your files:
```bash
rclone ls gdrive:cashew_backup | head -n 5
```

## 4. Setup Systemd Service for Auto-Mount
To ensure the drive mounts automatically on boot and stays mounted in the background, create a systemd service.

Create a file `/etc/systemd/system/rclone-mount.service`:
```bash
sudo nano /etc/systemd/system/rclone-mount.service
```

Add the following configuration (adjust paths and user as necessary):
```ini
[Unit]
Description=Rclone mount for Google Drive
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=ec2-user
Group=ec2-user
ExecStart=/usr/bin/rclone mount gdrive:cashew_backup /home/ec2-user/expense_analyzer_mobile/db \
    --config /home/ec2-user/.config/rclone/rclone.conf \
    --vfs-cache-mode writes \
    --allow-non-empty
ExecStop=/bin/fusermount -u /home/ec2-user/expense_analyzer_mobile/db
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 5. Enable and Start the Service
Create the mount directory if it doesn't exist:
```bash
mkdir -p /home/ec2-user/expense_analyzer_mobile/db
```

Reload systemd and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rclone-mount
sudo systemctl start rclone-mount
```

Verify it's running:
```bash
sudo systemctl status rclone-mount
ls -la /home/ec2-user/expense_analyzer_mobile/db
```