import sqlite3
import psycopg2
import psycopg2.extras
import os
import glob
import logging
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Set up logging for sync
logging.basicConfig(
    filename=os.path.join(basedir, 'sync.log'),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def get_latest_sqlite_db():
    search_dirs = [
        os.path.join(basedir, 'db'),
        os.getenv("BACKUP_DIR", ""),
        os.path.join(basedir, 'local_db')
    ]
    
    all_files = []
    for d in search_dirs:
        if d and os.path.exists(d):
            all_files.extend(glob.glob(os.path.join(d, "*.sql")))
            
    if all_files:
        return max(all_files, key=os.path.getmtime)
    return None

def sync():
    sqlite_path = get_latest_sqlite_db()
    if not sqlite_path:
        logging.warning("No SQLite database found to sync.")
        return

    # Check if we already synced this file
    last_sync_file = os.path.join(basedir, '.last_sync')
    if os.path.exists(last_sync_file):
        with open(last_sync_file, 'r') as f:
            last_synced_path = f.read().strip()
        if last_synced_path == sqlite_path:
            logging.info("Latest database is already synced. Skipping.")
            return

    logging.info(f"New database found: {sqlite_path}. Starting sync...")

    # Connect to SQLite
    try:
        sl_conn = sqlite3.connect(sqlite_path)
        sl_conn.row_factory = sqlite3.Row
        sl_cur = sl_conn.cursor()
    except Exception as e:
        logging.error(f"Failed to connect to SQLite: {e}")
        return

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
        logging.error(f"Failed to connect to PostgreSQL: {e}")
        return

    tables = ['wallets', 'categories', 'transactions']

    try:
        for table in tables:
            logging.info(f"Syncing table: {table}...")
            
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
                
                pk = "PRIMARY KEY" if col['pk'] else ""
                create_cols.append(f'"{col_name}" {pg_type} {pk}')
                col_names.append(f'"{col_name}"')
                
            create_stmt = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(create_cols)});"
            pg_cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            pg_cur.execute(create_stmt)
            
            # Fetch data
            sl_cur.execute(f"SELECT * FROM {table}")
            rows = sl_cur.fetchall()
            
            if rows:
                placeholders = ','.join(['%s'] * len(col_names))
                insert_stmt = f"INSERT INTO {table} ({','.join(col_names)}) VALUES ({placeholders})"
                
                data = [tuple(row) for row in rows]
                psycopg2.extras.execute_batch(pg_cur, insert_stmt, data)
                
        pg_conn.commit()
        logging.info("Sync complete! Data transferred to AWS RDS.")
        
        # Mark as synced
        with open(last_sync_file, 'w') as f:
            f.write(sqlite_path)
            
    except Exception as e:
        pg_conn.rollback()
        logging.error(f"Sync failed during table processing: {e}")
    finally:
        pg_conn.close()
        sl_conn.close()

if __name__ == '__main__':
    sync()
