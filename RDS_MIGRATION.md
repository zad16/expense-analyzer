# AWS RDS PostgreSQL Migration: End-to-End Guide

This document is a comprehensive, end-to-end guide on how the Expense Analyzer application was migrated from a local SQLite database to an Amazon RDS PostgreSQL database, and exactly how an EC2 instance is connected securely to an RDS instance.

---

## 1. AWS RDS Setup & Network Connection (Console Steps)

To allow an EC2 instance to talk to an RDS database, they must both exist in the same AWS Region (e.g., `eu-north-1` Stockholm) and their Security Groups (firewalls) must allow the traffic. 

The following steps were taken in the AWS Console to provision the database and automate the network connection:

1. **Create Database:** Navigated to the Amazon RDS dashboard and clicked "Create database".
2. **Configuration:** 
   - Selected **Standard create**.
   - Selected **PostgreSQL** as the engine.
   - Chose the **Free tier** or **Dev/Test** template.
   - Set the master username (e.g., `postgres`) and a master password.
3. **EC2 Integration (The Magic Step):** 
   - Under the "Connectivity" section, selected **"Connect to an EC2 compute resource"**.
   - Selected the specific EC2 instance running the app from the dropdown.
   - *Why this is important:* AWS automatically creates and configures the **Security Groups** for you. It modifies the RDS Security Group to add an "Inbound Rule" allowing traffic on Port 5432 (PostgreSQL) *only* from the EC2 instance's specific Security Group.
4. **Security:** "Public access" was set to **No**. The database is not exposed to the public internet. It can only be accessed internally by the connected EC2 instance over AWS's private network.

---

## 2. Server Configuration (.env Setup via SSH)

Because the app runs as a background service (systemd) on the EC2 instance, it requires the database credentials to be stored as environment variables. We do not hardcode passwords in the code.

The following commands were executed to configure the server:

**Step 1: SSH into the EC2 instance**
```bash
# Replace the IP with your actual EC2 IP address
ssh ubuntu@13.60.221.207
```

**Step 2: Navigate to the application directory**
```bash
cd ~/expense_analyzer_mobile
```

**Step 3: Edit the Environment File**
The `.env` file holds all the secrets. We open it using the `nano` text editor:
```bash
nano .env
```

**Step 4: Add the Database Variables**
We appended the following 5 database variables to the bottom of the `.env` file (leaving existing keys like `APP_PIN` untouched). The `DB_HOST` is the endpoint URL provided by AWS RDS after the database was created.
```ini
DB_HOST=expense-analyser-db.cdicoqa8053d.eu-north-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=postgres
DB_NAME=postgres
DB_PASSWORD=<the-master-password>
```
*(To save and exit in `nano`: Press `Ctrl + O`, `Enter`, then `Ctrl + X`)*

---

## 3. Application Code Changes

### Dependencies
The `requirements.txt` file was updated to include `psycopg2-binary`. This is the required Python adapter (driver) to allow Python to communicate with PostgreSQL.

### Code Updates (`app.py`)
The original SQLite code was preserved but **commented out**. New PostgreSQL logic was added:

1. **Switch Driver:** `sqlite3` imports were changed to `psycopg2` and `psycopg2.extras`.
2. **Updated `query_db()`:** The database connection function was rewritten to connect securely using the `os.getenv()` credentials from the `.env` file:
   ```python
   conn = psycopg2.connect(
       host=os.getenv("DB_HOST"),
       port=os.getenv("DB_PORT", 5432),
       dbname=os.getenv("DB_NAME", "postgres"),
       user=os.getenv("DB_USER", "postgres"),
       password=os.getenv("DB_PASSWORD")
   )
   ```
3. **Update SQL Dialect:** 
   - SQLite uses `?` for parameter placeholders. PostgreSQL uses `%s`. The code dynamically replaces them: `query = query.replace('?', '%s')`.
   - SQLite date functions like `date(t.date_created, 'unixepoch')` were rewritten to the PostgreSQL equivalent: `to_char(to_timestamp(t.date_created), 'YYYY-MM-DD')`.

---

## 4. Data Migration Process

To populate the empty PostgreSQL RDS instance with the existing user data from the local SQLite backup, an automated migration process was established:

1. **Migration Script (`migrate_data.py`):** A custom Python script was created. It dynamically reads the schemas for the `wallets`, `categories`, and `transactions` tables from the old `.sql` SQLite file, translates the column types to PostgreSQL (e.g., `REAL` to `DOUBLE PRECISION`), creates the tables in RDS, and bulk-inserts all the historical records.
2. **Automated Execution (CI/CD):** 
   - The GitHub Actions pipeline (`.github/workflows/deploy_ec2.yml`) was updated.
   - During deployment, the pipeline automatically executes `python migrate_data.py` directly on the EC2 instance right before restarting the application service. 
   - Because the script executes from inside the EC2 instance, it has access to the `.env` credentials and can freely communicate with the RDS database over the secure private network, bypassing the firewall entirely.
