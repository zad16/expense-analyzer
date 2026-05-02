# EC2 Mobile App Deployment Instructions

This document outlines all the steps taken to manually provision, configure, and host the `vault-mobile` app on the EC2 instance (Amazon Linux 2023).

## 1. Initial Setup & Permissions

The EC2 instance required basic packages to be installed, including `git`, `python3-venv`, and `python3-pip`. A `.github/workflows/deploy_ec2.yml` GitHub Actions workflow was created to automatically clone the code and restart the background service on every push to `main`.

Since the server uses Amazon Linux, it enforces strict security policies via **SELinux**. We adjusted SELinux to permissive mode so that background services (`systemd`) and Nginx could interact with the application freely.

## 2. Environment Variables

The application secrets are never committed to GitHub. An `.env` file was manually created in `/home/ec2-user/expense_analyzer_mobile/.env` containing:
- `SECRET_KEY`: Used by Flask for secure session management.
- `APP_PIN`: The 4-digit login pin.
- `GROQ_API_KEY`: Authentication key for the AI functionality.
- `BACKUP_DIR`: Configured to point to the Google Drive mount directory (`/home/ec2-user/expense_analyzer_mobile/db`).
- `APP_VARIANT`: Set to `mobile` to enforce the minimalist UI.

## 3. Data Retrieval (Google Drive Sync via Rclone)

To synchronize your SQLite database backups continuously exactly like the GCP deployment:
1. **Installed dependencies**: `fuse` and `fuse3` were installed to support mounting cloud drives.
2. **Installed Rclone**: The official `rclone` Linux binary was downloaded and installed.
3. **Configured Authentication**: The `rclone.conf` file containing the Google Drive OAuth tokens was copied to `~/.config/rclone/rclone.conf`.
4. **Systemd Mount Service**: A dedicated background service (`rclone-mount.service`) was created to ensure Google Drive automatically mounts to `~/expense_analyzer_mobile/db` whenever the server boots up. The main `app.py` logic automatically copies the latest `.sql` database from this mount into its own `local_db` directory to prevent database locking issues.

## 4. Application Server (Gunicorn & Systemd)

The application itself is served by `gunicorn`, a robust production WSGI server for Python.
1. The `setup_mobile_service.sh` script was executed to configure a systemd service (`vault-mobile.service`).
2. This service ensures `gunicorn` is always running on port `5000` locally and will restart the app if it crashes or if the server reboots.

## 5. Web Server / Reverse Proxy (Nginx)

To allow the application to be accessible via the default HTTP port (`80`) without needing to type `:5000`:
1. Apache (`httpd`) was stopped and disabled as it was conflicting with port 80.
2. **Nginx** was installed via the package manager (`yum`).
3. A custom configuration was placed in `/etc/nginx/conf.d/vault-mobile.conf` telling Nginx to listen on port `80` and proxy all incoming traffic to `http://127.0.0.1:5000` (where Gunicorn is running).
4. The Nginx service was enabled and started.

## Summary

The entire stack is now automated and resilient to restarts:
- **Rclone** handles syncing your Google Drive database updates.
- **Systemd** ensures both the database mount and the Python application stay running.
- **Nginx** securely routes internet traffic to the application.
- **GitHub Actions** automatically redeploys any new code updates pushed to the `main` branch.