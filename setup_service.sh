#!/bin/bash

# Configuration
APP_NAME="expense"
# Detect the actual user if running with sudo, otherwise use current user
USER_NAME=${SUDO_USER:-$(whoami)}
GROUP_NAME=$(id -gn $USER_NAME)
# Use realpath to get the full absolute path
PROJECT_DIR=$(realpath .)
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"

echo "Setting up $APP_NAME service for user $USER_NAME (group $GROUP_NAME) in $PROJECT_DIR..."

# 1. Ensure gunicorn is installed in the venv
if [ -f "$VENV_DIR/bin/pip" ]; then
    echo "Ensuring gunicorn is installed..."
    $VENV_DIR/bin/pip install gunicorn --quiet
else
    echo "Error: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# 2. Create the systemd service file
echo "Creating systemd service file at $SERVICE_FILE..."
ENV_LINE=""
if [ -f "$PROJECT_DIR/.env" ]; then
    ENV_LINE="EnvironmentFile=$PROJECT_DIR/.env"
fi

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Gunicorn instance to serve Expense Analyzer
After=network.target

[Service]
User=$USER_NAME
Group=$GROUP_NAME
WorkingDirectory=$PROJECT_DIR
$ENV_LINE
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 1 --timeout 180 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
EOF

# 3. Reload systemd and start the service
echo "Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl start $APP_NAME
sudo systemctl enable $APP_NAME

# 4. Check status
echo "------------------------------------------------"
echo "Setup complete! Checking service status..."
sudo systemctl status $APP_NAME --no-pager
echo "------------------------------------------------"
echo "Your app is now running persistently."
echo "To stop it: sudo systemctl stop $APP_NAME"
echo "To restart it: sudo systemctl restart $APP_NAME"
echo "To view logs: journalctl -u $APP_NAME -f"
