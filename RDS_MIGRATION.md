# AWS RDS PostgreSQL Migration

This document outlines the steps and configuration required to migrate the Expense Analyzer application from using a local/rclone-synced SQLite database to an Amazon RDS PostgreSQL database.

## 1. AWS RDS Setup & Network Connection

The following steps were taken in the AWS Console to provision the database and connect it to the EC2 instance:

1. **Provisioning:** A standard **Amazon RDS for PostgreSQL** instance was created in the `eu-north-1` (Stockholm) region to match the location of the existing EC2 instance.
2. **EC2 Integration (Crucial Step):** During database creation, under the "Connectivity" section, the **"Connect to an EC2 compute resource"** option was selected. 
   - *Why this matters:* By selecting the EC2 instance here, AWS automatically configured the Security Group (firewall) rules. It allowed inbound traffic on port 5432 (PostgreSQL) from the EC2 instance to the RDS instance.
3. **Security:** "Public access" was set to **No**. The database is not exposed to the internet. It can only be accessed internally by the EC2 instance.

## 2. Server Configuration (.env Setup via SSH)

Because the app runs as a background service on the EC2 instance, it requires the database credentials to be stored as environment variables.

The following actions were taken to configure the server:
1. Logged into the EC2 instance via SSH: `ssh ubuntu@13.60.221.207`
2. Navigated to the application directory: `cd ~/expense_analyzer_mobile`
3. Edited the existing `.env` file using the `nano` editor.
4. Appended the following 5 database variables to the bottom of the `.env` file (leaving existing keys like `APP_PIN` and `GROQ_API_KEY` untouched):

```ini
DB_HOST=<database-endpoint-url.eu-north-1.rds.amazonaws.com>
DB_PORT=5432
DB_USER=postgres
DB_NAME=postgres
DB_PASSWORD=<the-master-password>
```

## 3. Application Code Changes

### Dependencies
The `requirements.txt` file was updated to include `psycopg2-binary`. This is the Python driver required to connect to a PostgreSQL database.

### Code Updates (`app.py`)
The original SQLite and `rclone` sync code was preserved but **commented out**. New PostgreSQL logic was added below the commented sections:

1. **Remove `rclone` logic:** The background threads calling `get_latest_db()` were disabled.
2. **Switch Driver:** `sqlite3` imports were commented out, and `psycopg2` was introduced.
3. **Updated `query_db()`:** The function was rewritten to connect to the RDS instance securely using the `os.getenv()` credentials from the `.env` file.
4. **Update SQL Dialect:** 
   - SQLite `?` parameter placeholders were replaced with PostgreSQL `%s` placeholders.
   - Date functions like `date(t.date_created, 'unixepoch')` were replaced with PostgreSQL equivalent `to_char(to_timestamp(t.date_created), 'YYYY-MM-DD')`.
   - The history query timezone modifier `+05:30` was updated to `AT TIME ZONE 'Asia/Kolkata'`.
