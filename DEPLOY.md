# Deployment Guide: Google VM (Compute Engine)

Follow these steps to deploy your Expense Analyzer app to a Google Cloud VM.

## 1. Prepare your VM
1.  Go to **GCP Console > Compute Engine > VM Instances**.
2.  Create an instance (e.g., `e2-small` with Ubuntu 22.04 LTS).
3.  In **Networking**, check **Allow HTTP traffic**.
4.  Once created, click **SSH** to open the terminal.

## 2. Set up the Environment
Run these commands in your VM terminal:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Create project directory
mkdir ~/expense_analyzer
cd ~/expense_analyzer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

## 3. Upload Files
You can use `git clone` if your code is on GitHub, or use the **Upload File** button in the SSH window to upload your files to `~/expense_analyzer`.

Make sure you have:
- `app.py`
- `requirements.txt`
- `templates/`
- `.env` (Create this manually or upload it)
- Your `.sql` database files (Upload them to a `db/` folder)
  *   **Note**: The app expects these `.sql` files to be **SQLite database files**, not SQL scripts.

## 4. Connect Google Drive (rclone mount)
To access your latest `.sql` files directly from Google Drive:

1.  **Install rclone & FUSE**:
    - **Ubuntu/Debian**: `sudo apt install rclone fuse3 -y`
    - **CentOS/RHEL**: `sudo yum install epel-release -y && sudo yum install rclone fuse3 -y`
    - **Universal Script (Recommended)**: `sudo -v ; curl https://rclone.org/install.sh | sudo bash`
2.  **Configure rclone**:
    ```bash
    rclone config
    ```
    - Choose `n` for New remote.
    - Name it `gdrive`.
    - Choose `drive` (Google Drive).
    - Leave Client ID/Secret blank.
    - Choose scope `1` (Full access).
    - When it asks for **Use auto config?**, say `n` (since you are on a remote VM).
    - Follow the instructions to authorize on your local machine and paste the code back.

3.  **Create Mount Point**:
    *(Use absolute paths to be safe)*
    ```bash
    mkdir -p /home/your_username/expense_analyzer/db
    ```

4.  **Mount the Drive**:
    ```bash
    rclone mount gdrive:cashew_backup /home/your_username/expense_analyzer/db --vfs-cache-mode writes &
    ```
    *(Replace `cashew_backup` with the actual folder name in your Drive)*.

## 5. Configure Environment Variables
```bash
pip install -r requirements.txt
pip install gunicorn
```

## 5. Configure Environment Variables
Create or edit the `.env` file on the VM:
```bash
nano .env
```
Add your keys and set the `BACKUP_DIR` to the folder on the VM where you uploaded your `.sql` files:
```env
GROQ_API_KEY=your_key_here
BACKUP_DIR=/home/your_username/expense_analyzer/db
```

## 6. Run with Gunicorn
To test if it works:
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```
*Note: You may need to open port 5000 in the GCP Firewall (VPC Network > Firewall).*

## 7. Keep it running (Systemd)
To make the app run automatically even after you logout:
```bash
sudo nano /etc/systemd/system/expense.service
```
Paste this configuration (replace `your_username`):
```ini
[Unit]
Description=Gunicorn instance to serve Expense Analyzer
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/home/your_username/expense_analyzer
Environment="PATH=/home/your_username/expense_analyzer/venv/bin"
ExecStart=/home/your_username/expense_analyzer/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```
Then start it:
```bash
sudo systemctl start expense
sudo systemctl enable expense
```

## 8. Firewall (If port 5000 is not working)
1. Go to **VPC Network > Firewall**.
2. Create a rule:
   - Name: `allow-flask`
   - Targets: `All instances in the network`
   - Source IP ranges: `0.0.0.0/0`
   - Protocols/ports: `tcp:5000`
