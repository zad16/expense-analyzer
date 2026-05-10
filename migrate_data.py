import sqlite3
import psycopg2
import psycopg2.extras
import os
import glob
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def get_latest_sqlite_db():
    local_dir = os.path.join(basedir, 'local_db')
    if os.path.exists(local_dir):
        files = glob.glob(os.path.join(local_dir, "*.sql"))
        if files:
            return max(files, key=os.path.getmtime)
            
    # Fallback to checking db folder
    db_dir = os.path.join(basedir, 'db')
    if os.path.exists(db_dir):
        files = glob.glob(os.path.join(db_dir, "*.sql"))
        if files:
            return max(files, key=os.path.getmtime)
            
    # Check if backup dir is specified
    target_dir = os.getenv("BACKUP_DIR")
    if target_dir and os.path.exists(target_dir):
        files = glob.glob(os.path.join(target_dir, "*.sql"))
        if files:
            return max(files, key=os.path.getmtime)
            
    return None

def migrate():
    sqlite_path = get_latest_sqlite_db()
    if not sqlite_path:
        print("Error: Could not find any local SQLite database (.sql) to migrate from!")
        print("Please make sure the old rclone sync fetched at least one database.")
        return

    print(f"Found latest SQLite database: {sqlite_path}")

    # Connect to SQLite
    sl_conn = sqlite3.connect(sqlite_path)
    sl_conn.row_factory = sqlite3.Row
    sl_cur = sl_conn.cursor()

    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432),
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )
        pg_cur = pg_conn.cursor()
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        return

    tables = ['wallets', 'categories', 'transactions']

    for table in tables:
        print(f"\nMigrating table: {table}...")
        
        # Get schema from sqlite
        sl_cur.execute(f"PRAGMA table_info({table})")
        columns = sl_cur.fetchall()
        
        # Create table in pg
        create_cols = []
        col_names = []
        for col in columns:
            col_name = col['name']
            col_type = col['type'].upper()
            if 'REAL' in col_type:
                pg_type = 'DOUBLE PRECISION'
            elif 'INT' in col_type:
                pg_type = 'BIGINT'
            elif 'TEXT' in col_type:
                pg_type = 'TEXT'
            else:
                pg_type = 'TEXT'
            
            # handle primary key
            pk = "PRIMARY KEY" if col['pk'] else ""
            create_cols.append(f"{col_name} {pg_type} {pk}")
            col_names.append(col_name)
            
        create_stmt = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(create_cols)});"
        print(f"Creating table in PostgreSQL...")
        pg_cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        pg_cur.execute(create_stmt)
        
        # Fetch data
        sl_cur.execute(f"SELECT * FROM {table}")
        rows = sl_cur.fetchall()
        print(f"Found {len(rows)} rows to migrate.")
        
        if rows:
            # Insert into pg
            placeholders = ','.join(['%s'] * len(col_names))
            insert_stmt = f"INSERT INTO {table} ({','.join(col_names)}) VALUES ({placeholders})"
            
            data = [tuple(row) for row in rows]
            psycopg2.extras.execute_batch(pg_cur, insert_stmt, data)
            print("Rows inserted successfully.")
            
    pg_conn.commit()
    print("\nMigration complete! All data has been transferred to AWS RDS.")
    pg_conn.close()
    sl_conn.close()

if __name__ == '__main__':
    migrate()