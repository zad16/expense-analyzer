# Gunicorn Server Setup Guide

This document explains how to set up `gunicorn` to serve your Flask or Python web application using systemd on a Linux server (EC2, GCP, Ubuntu, CentOS, etc.).

## 1. Prepare your Environment
Navigate to your project directory. Ensure that you have a virtual environment set up.

```bash
cd ~/your_project
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Gunicorn
While your virtual environment is active, install gunicorn along with your other requirements.

```bash
pip install -r requirements.txt
pip install gunicorn
```

## 3. Test Gunicorn Manually
Before creating the service, ensure that gunicorn can start your app.

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```
*(You may need to change `app:app` depending on the name of your Python file and your Flask instance variable. For example, if your file is `main.py` and the variable is `server`, use `main:server`)*

If it starts without errors, exit by pressing `Ctrl+C`.

## 4. Setup Systemd Service
To ensure Gunicorn runs in the background and restarts automatically if the server reboots or the app crashes, we create a systemd service.

Create a new service file:
```bash
sudo nano /etc/systemd/system/myapp.service
```

Add the following configuration (replace `your_username` and `your_project` with your actual paths):

```ini
[Unit]
Description=Gunicorn instance to serve my app
After=network.target

[Service]
User=your_username
Group=your_username
WorkingDirectory=/home/your_username/your_project
EnvironmentFile=/home/your_username/your_project/.env
Environment="PATH=/home/your_username/your_project/venv/bin"
ExecStart=/home/your_username/your_project/venv/bin/gunicorn --workers 3 --threads 4 --timeout 180 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

**Note:** If you are using a proxy like Nginx (recommended), you can change `--bind 0.0.0.0:5000` to `--bind 127.0.0.1:5000` so the application isn't exposed directly to the internet.

## 5. Enable and Start the Service
Reload systemd so it knows about the new service file:
```bash
sudo systemctl daemon-reload
```

Start the service and enable it to start on boot:
```bash
sudo systemctl start myapp
sudo systemctl enable myapp
```

Check the status to ensure it's running:
```bash
sudo systemctl status myapp
```

If it failed to start, check the logs for details:
```bash
sudo journalctl -xeu myapp.service
```

## 6. Restarting the App
If you make changes to your Python code or update your application, simply restart the service:
```bash
sudo systemctl restart myapp
```
