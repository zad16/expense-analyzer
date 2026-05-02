#!/bin/bash

set -e

APP_NAME="vault-mobile"
USER_NAME=${SUDO_USER:-$(whoami)}
GROUP_NAME=$(id -gn "$USER_NAME")
PROJECT_DIR=$(realpath .)
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"

echo "Setting up $APP_NAME service for user $USER_NAME in $PROJECT_DIR..."

if [ ! -f "$VENV_DIR/bin/pip" ]; then
    echo "Error: virtual environment not found at $VENV_DIR"
    exit 1
fi

"$VENV_DIR/bin/pip" install gunicorn --quiet

ENV_LINE=""
if [ -f "$PROJECT_DIR/.env" ]; then
    ENV_LINE="EnvironmentFile=$PROJECT_DIR/.env"
fi

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Gunicorn instance for Vault Mobile
After=network.target

[Service]
User=$USER_NAME
Group=$GROUP_NAME
WorkingDirectory=$PROJECT_DIR
$ENV_LINE
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 2 --threads 4 --timeout 180 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart "$APP_NAME" || sudo systemctl start "$APP_NAME"
sudo systemctl enable "$APP_NAME"

echo "----------------------------------------"
sudo systemctl status "$APP_NAME" --no-pager
echo "----------------------------------------"
echo "Vault Mobile is now running."
