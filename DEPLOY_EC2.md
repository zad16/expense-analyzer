# Deployment Guide: Mobile Vault on EC2

This guide deploys the minimalist mobile version of the app to an EC2 instance while leaving the desktop deployment on GCP unchanged.

## App mode

The app now supports two UI variants:

- `APP_VARIANT=desktop` for the existing desktop dashboard
- `APP_VARIANT=mobile` for the minimalist mobile-first UI

On EC2, set:

```env
APP_VARIANT=mobile
```

## 1. Prepare the EC2 instance

Recommended instance:

- Ubuntu 22.04 or 24.04
- Security group allowing:
  - `22` for SSH
  - `80` for HTTP
  - `443` for HTTPS if you add TLS

Connect:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

## 2. Install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx git -y
```

## 3. Create the project directory

```bash
mkdir -p ~/expense_analyzer_mobile
cd ~/expense_analyzer_mobile
```

## 4. Upload the code

You can use `git clone`, `scp`, or rsync.

If the repo is private or you want a direct copy from your machine:

```bash
scp -i your-key.pem -r . ubuntu@YOUR_EC2_IP:/home/ubuntu/expense_analyzer_mobile
```

## 5. Create a virtual environment

```bash
cd ~/expense_analyzer_mobile
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 6. Configure environment variables

Create `.env`:

```bash
nano .env
```

Example:

```env
SECRET_KEY=change-me
APP_PIN=1234
GROQ_API_KEY=your_key_here
BACKUP_DIR=/home/ubuntu/expense_analyzer_mobile/db
APP_VARIANT=mobile
```

If your SQL snapshots are copied to the server, place them in `db/`.

## 7. Test the app

```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 app:app
```

Then open:

```text
http://YOUR_EC2_IP
```

## 8. Install the systemd service

Run:

```bash
chmod +x setup_mobile_service.sh
./setup_mobile_service.sh
```

This creates a dedicated `vault-mobile` service.

## 9. Configure nginx

Create:

```bash
sudo nano /etc/nginx/sites-available/vault-mobile
```

Paste:

```nginx
server {
    listen 80;
    server_name YOUR_EC2_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/vault-mobile /etc/nginx/sites-enabled/vault-mobile
sudo nginx -t
sudo systemctl restart nginx
```

## 10. Useful commands

```bash
sudo systemctl status vault-mobile
sudo systemctl restart vault-mobile
journalctl -u vault-mobile -f
```

## Notes

- The desktop GCP deployment can keep using the default `desktop` variant.
- The EC2 server should use `APP_VARIANT=mobile`.
- If you want a subdomain later, point something like `m.example.com` to the EC2 instance.
