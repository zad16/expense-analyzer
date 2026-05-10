# Version: 1.0.2 - Enhanced Sync & Threading
import threading
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from openai import OpenAI
# import sqlite3
import psycopg2
import psycopg2.extras
import json
import os
import glob
from datetime import datetime, date
from dotenv import load_dotenv

# Load .env explicitly with absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
APP_PIN = os.getenv("APP_PIN", "1234")  # Default PIN is 1234 if not set
APP_VARIANT = os.getenv("APP_VARIANT", "desktop").strip().lower()

# If a specific PIN behavior is needed for mobile, it should be set via the .env file.
# The APP_PIN variable is already loaded from the environment above.


def is_mobile_variant():
    return APP_VARIANT == "mobile"


def is_mobile_path(path):
    return str(path or "").startswith("/m")


def use_mobile_ui(path=None):
    return is_mobile_variant() or is_mobile_path(path or request.path)


def login_endpoint_for(path=None):
    return "mobile_login" if use_mobile_ui(path) else "login"


def home_endpoint_for(path=None):
    return "mobile_index" if use_mobile_ui(path) else "index"


def login_template_for(path=None):
    return "mobile_login.html" if use_mobile_ui(path) else "login.html"

@app.before_request
def require_login():
    # Only allow these static routes or the login route itself without auth
    if request.endpoint in ['login', 'mobile_login', 'static'] or request.path.startswith('/static/'):
        return
    if not session.get('authenticated'):
        if request.path.startswith('/api/') or request.path == '/chat':
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for(login_endpoint_for(request.path)))

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_mobile_variant():
        return redirect(url_for("mobile_login"))
    return handle_login(is_mobile=False)


@app.route("/m/login", methods=["GET", "POST"])
def mobile_login():
    return handle_login(is_mobile=True)


def handle_login(is_mobile=False):
    if request.method == "POST":
        if request.form.get("pin") == APP_PIN:
            session['authenticated'] = True
            # Start sync immediately on login to avoid delay in dashboard
            # threading.Thread(target=get_latest_db).start()
            return redirect(url_for('mobile_index' if is_mobile else home_endpoint_for()))
        return render_template("mobile_login.html" if is_mobile else login_template_for(), error="Invalid PIN")
    return render_template("mobile_login.html" if is_mobile else login_template_for())

@app.route("/logout")
def logout():
    session.pop('authenticated', None)
    return redirect(url_for(login_endpoint_for()))


@app.route("/m/logout")
def mobile_logout():
    session.pop('authenticated', None)
    return redirect(url_for("mobile_login"))

# ── Configuration ────────────────────────────────────────────────────────────

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GROQ_API_KEY is missing! Check your .env file.")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

BACKUP_DIR = os.getenv("BACKUP_DIR", r"G:\My Drive\cashew_backup")
CC_WALLET_ID = 'c43a7127-daab-4b0c-a47f-f150130d4e41'

# ── Database Logic ──────────────────────────────────────────────────────────

import logging

# Configure logging to a file
logging.basicConfig(
    filename=os.path.join(basedir, 'app.log'),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

_db_cache = {"path": None, "expiry": 0}
sync_lock = threading.Lock()

# def get_latest_db():
#     global _db_cache, _query_cache
#     import time
#     import shutil
#     now = time.time()
#     
#     # Fast path: check cache first without lock
#     if _db_cache["path"] and now < _db_cache["expiry"]:
#         return _db_cache["path"]
# 
#     with sync_lock:
#         # Double-check cache inside lock
#         if _db_cache["path"] and now < _db_cache["expiry"]:
#             return _db_cache["path"]
# 
#         try:
#             # Resolve path to be Linux-friendly if needed
#             target_dir = BACKUP_DIR
#             if os.name != 'nt' and target_dir.startswith('G:\\'):
#                 # If on Linux but path is Windows-style, check for local 'db' first
#                 target_dir = os.path.join(basedir, 'db')
#                 
#             logging.debug(f"Scanning for DB in: {target_dir}")
#             files = glob.glob(os.path.join(target_dir, "*.sql"))
#             if not files and target_dir != os.path.join(basedir, 'db'):
#                 files = glob.glob(os.path.join(basedir, 'db', '*.sql'))
#                 
#             if not files:
#                 logging.warning("No .sql files found in target directories.")
#                 return _db_cache["path"] # Return old path if available even if expired
#                 
#             latest_remote = max(files, key=os.path.getmtime)
#             logging.debug(f"Latest Remote DB found: {latest_remote}")
# 
#             # --- Local Sync Logic (New) ---
#             local_dir = os.path.join(basedir, 'local_db')
#             if not os.path.exists(local_dir): os.makedirs(local_dir)
#             
#             local_path = os.path.join(local_dir, os.path.basename(latest_remote))
#             
#             # Only copy if local doesn't exist or is older than remote
#             if not os.path.exists(local_path) or os.path.getmtime(latest_remote) > os.path.getmtime(local_path):
#                 logging.info(f"Syncing {latest_remote} to local storage...")
#                 shutil.copy2(latest_remote, local_path)
#                 logging.info("Sync complete.")
#                 
#                 # Clear query cache when a new database is detected and synced
#                 _query_cache.clear()
#                 logging.info("Cleared query cache due to new database sync.")
#             
#             # Use the local path for queries
#             latest = local_path
#             # --- End Local Sync Logic ---
#             
#             # Cache for 5 minutes
#             _db_cache = {"path": latest, "expiry": now + 300}
#             return latest
#         except Exception as e:
#             logging.error(f"Error in get_latest_db: {e}")
#             return _db_cache["path"] # Fallback to cached even if expired
# 
# def query_db(query, params=()):
#     db_path = get_latest_db()
#     if not db_path: return []
#     conn = None
#     try:
#         # Use a timeout to prevent hanging on locked databases
#         conn = sqlite3.connect(f"file:{db_path}?mode=ro&nolock=1", uri=True, timeout=10)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
#         cursor.execute(query, params)
#         rows = [dict(row) for row in cursor.fetchall()]
#         return rows
#     except Exception as e:
#         logging.error(f"SQL Error: {e} | Query: {query}")
#         return []
#     finally:
#         if conn: conn.close()

def query_db(query, params=()):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432),
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Convert SQLite ? placeholders to PostgreSQL %s
        query = query.replace('?', '%s')
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows] if rows else []
        conn.close()
        return result
    except Exception as e:
        import logging
        logging.error(f"SQL Error: {e} | Query: {query}")
        return []


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_category_filter(category_name):
    if not category_name: return None
    c = str(category_name).lower().strip()
    if "food" in c or "meal" in c or "grocer" in c: return ["Meals", "Groceries"]
    if "transport" in c or "transit" in c: return ["Transit"]
    if "cloth" in c or "shirt" in c or "pant" in c or "shopping" in c or "grooming" in c or "lifestyle" in c: 
        return ["Shopping", "Self-care & Grooming", "Lifestyle & Discretionary Spending"]
    if "balance correction" in c: return ["Balance Correction"]
    return [category_name]

def build_where_clause(ts_start, ts_end, tx_type="expense", category=None, keyword=None):
    where = "WHERE t.paid = 1 AND t.date_created BETWEEN ? AND ?"
    params = [ts_start, ts_end]
    where += f" AND t.wallet_fk != '{CC_WALLET_ID}'"
    
    if tx_type == "expense": where += " AND t.amount < 0"
    elif tx_type == "income": where += " AND t.amount > 0"
    
    # Logic: 
    # 1. If keyword is present, PRIORITIZE it. It's the most specific thing the user asked for.
    # 2. If category is present, filter by it.
    # 3. If both are present, we look for transactions that match the keyword AND (optionally) the category.
    # Actually, to be safe, if a keyword is provided, we should just search by that keyword first.
    
    # Join categories for both main category (c) and subcategory (sc)
    join_clause = "LEFT JOIN categories c ON t.category_fk = c.category_pk LEFT JOIN categories sc ON t.sub_category_fk = sc.category_pk"
    
    if keyword and category:
        cats = get_category_filter(category)
        placeholders = ",".join(["?"] * len(cats))
        where += f" AND (c.name IN ({placeholders}) OR sc.name IN ({placeholders})) AND (t.name LIKE ? OR c.name LIKE ? OR sc.name LIKE ? OR t.note LIKE ?)"
        params.extend(cats)
        params.extend(cats)
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    elif keyword:
        where += " AND (t.name LIKE ? OR c.name LIKE ? OR sc.name LIKE ? OR t.note LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    elif category:
        cats = get_category_filter(category)
        placeholders = ",".join(["?"] * len(cats))
        where += f" AND (c.name IN ({placeholders}) OR sc.name IN ({placeholders}))"
        params.extend(cats)
        params.extend(cats)
        
    return where, params, join_clause

# ── Unified Tool Logic ───────────────────────────────────────────────────────

_query_cache = {}

def query_finance_data(request_type, start_date, end_date, search_term=None, sort="DESC", limit=None):
    category = None
    keyword = None
    if search_term:
        search_term_str = str(search_term).strip()
        import re
        # Check for any kind of quotes (straight or curly) around the whole string
        match = re.match(r"^(['\"‘“])(.*)(['\"’”])$", search_term_str)
        if match:
            keyword = match.group(2).strip()
            logging.debug(f"Search identified as KEYWORD: {keyword}")
        else:
            category = search_term_str
            logging.debug(f"Search identified as CATEGORY: {category}")

    global _query_cache
    import time
    cache_key = f"{request_type}-{start_date}-{end_date}-{category}-{keyword}-{sort}-{limit}"
    now = time.time()
    if cache_key in _query_cache:
        data, expiry = _query_cache[cache_key]
        if now < expiry:
            logging.debug(f"Cache HIT for {cache_key}")
            return data

    try:
        from datetime import timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        
        ts_start = int(datetime.strptime(str(start_date).strip(), "%Y-%m-%d").replace(tzinfo=ist).timestamp())
        ts_end = int(datetime.strptime(str(end_date).strip(), "%Y-%m-%d").replace(tzinfo=ist).timestamp()) + 86399
        logging.debug(f"Query period: {start_date} to {end_date} | TS: {ts_start} to {ts_end}")
        
        # Increase default limit to avoid mismatches between total_spent and listed items
        if limit:
            limit_val = int(limit)
        else:
            limit_val = 100 # Standard default for all list queries to ensure comprehensive breakdowns

        res_data = None
        if request_type == "transactions": request_type = "list"
        # 1. Summary Type
        if request_type == "summary":
            where, params, join_clause = build_where_clause(ts_start, ts_end, tx_type="all", category=category, keyword=keyword)
            rows = query_db(f"SELECT SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as income, SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as expenses FROM transactions t {join_clause} {where}", tuple(params))
            res = rows[0] if rows else {}
            res_data = {"expenses": round(res.get('expenses') or 0, 2), "income": round(res.get('income') or 0, 2), "currency": "INR (₹)"}

        # 2. List Type
        elif request_type == "list":
            where, params, join_clause = build_where_clause(ts_start, ts_end, tx_type="expense", category=category, keyword=keyword)
            order_by = "ABS(t.amount) DESC" if "AMOUNT" in str(sort) else "t.date_created DESC"
            if "ASC" in str(sort): order_by = order_by.replace("DESC", "ASC")
            # rows = query_db(f"SELECT t.name as transaction_name, t.note as note, ABS(t.amount) as amount, date(t.date_created, 'unixepoch') as date, c.name as main_category, sc.name as sub_category FROM transactions t {join_clause} {where} ORDER BY {order_by} LIMIT ?", tuple(params + [limit_val]))
            rows = query_db(f"SELECT t.name as transaction_name, t.note as note, ABS(t.amount) as amount, to_char(to_timestamp(t.date_created), 'YYYY-MM-DD') as date, c.name as main_category, sc.name as sub_category FROM transactions t {join_clause} {where} ORDER BY {order_by} LIMIT %s", tuple(params + [limit_val]))
            
            # Also calculate the total for this specific list/filter
            total_rows = query_db(f"SELECT SUM(ABS(t.amount)) as total FROM transactions t {join_clause} {where}", tuple(params))
            total_spent = total_rows[0]['total'] if total_rows and total_rows[0]['total'] else 0
            
            res_data = {"results": rows, "total_spent": round(total_spent, 2)}

        # 3. Daily Analysis
        elif request_type == "daily":
            order_dir = "ASC" if "ASC" in str(sort) else "DESC"
            where, params, join_clause = build_where_clause(ts_start, ts_end, tx_type="expense", category=category, keyword=keyword)
            
            # For daily, we need a modified WHERE clause because we are grouping by day.
            # Actually, we can use the same WHERE clause if we are careful.
            
            rows = query_db(f"""
#                 SELECT stats.day, stats.daily_total_spent, max_items.transaction_name, max_items.note, max_items.amount
#                 FROM (
#                     SELECT date(t.date_created, 'unixepoch') as day, ROUND(SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END), 2) as daily_total_spent
#                     FROM transactions t {join_clause}
#                     {where}
#                     GROUP BY day HAVING daily_total_spent > 0
#                 ) stats
#                 LEFT JOIN (
#                     SELECT date(t.date_created, 'unixepoch') as sub_day, t.name as transaction_name, t.note as note, ABS(t.amount) as amount, MAX(ABS(t.amount))
#                     FROM transactions t {join_clause}
#                     {where}
#                     GROUP BY sub_day
#                 ) max_items ON stats.day = max_items.sub_day
#                 ORDER BY stats.daily_total_spent {order_dir} LIMIT ?
                SELECT stats.day, stats.daily_total_spent, max_items.transaction_name, max_items.note, max_items.amount
                FROM (
                    SELECT to_char(to_timestamp(t.date_created), 'YYYY-MM-DD') as day, ROUND(SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END), 2) as daily_total_spent
                    FROM transactions t {join_clause}
                    {where}
                    GROUP BY day HAVING SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) > 0
                ) stats
                LEFT JOIN (
                    SELECT sub_day, transaction_name, note, amount
                    FROM (
                        SELECT to_char(to_timestamp(t.date_created), 'YYYY-MM-DD') as sub_day, t.name as transaction_name, t.note as note, ABS(t.amount) as amount,
                               ROW_NUMBER() OVER(PARTITION BY to_char(to_timestamp(t.date_created), 'YYYY-MM-DD') ORDER BY ABS(t.amount) DESC) as rn
                        FROM transactions t {join_clause} {where}
                    ) ranked
                    WHERE rn = 1
                ) max_items ON stats.day = max_items.sub_day
                ORDER BY stats.daily_total_spent {order_dir} LIMIT %s
            """, tuple(params + params + [limit_val]))
            res_data = {"results": rows}

        if res_data is not None:
            # Cache for 5 minutes
            _query_cache[cache_key] = (res_data, now + 300)
            return res_data

        return {"error": "Invalid request type"}
    except Exception as e:
        logging.error(f"Error in query_finance_data: {e}")
        return {"error": str(e)}

def get_history():
    try:
        # Using '+05:30' modifier so transactions are grouped by their Indian Standard Time month
        # rows = query_db(f"SELECT strftime('%Y-%m', datetime(date_created, 'unixepoch', '+05:30')) as month, SUM(amount) as savings FROM transactions WHERE paid = 1 AND wallet_fk != '{CC_WALLET_ID}' AND date_created <= strftime('%s', 'now') GROUP BY month ORDER BY month DESC LIMIT 12")
        rows = query_db(f"SELECT to_char(to_timestamp(date_created) AT TIME ZONE 'Asia/Kolkata', 'YYYY-MM') as month, SUM(amount) as savings FROM transactions WHERE paid = 1 AND wallet_fk != '{CC_WALLET_ID}' AND date_created <= extract(epoch from now()) GROUP BY month ORDER BY month DESC LIMIT 12")
        if not rows: return []
        return [{"month": datetime.strptime(r['month'], "%Y-%m").strftime("%B %Y"), "savings": round(r['savings'] or 0, 2), "is_positive": (r['savings'] or 0) >= 0} for r in rows]
    except Exception as e:
        logging.error(f"Error in get_history: {e}")
        return []

# ── API & Chat ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if is_mobile_variant():
        return redirect(url_for("mobile_index"))
    # # Background pre-sync to speed up initial load
    # import threading
    # threading.Thread(target=get_latest_db).start()
    return render_template("index.html")


@app.route("/m")
def mobile_index():
    # import threading
    # threading.Thread(target=get_latest_db).start()
    return render_template("mobile.html")

@app.route("/api/summary")
def api_summary():
    # 1. Get Monthly Stats
    # Use IST explicitly so server timezone doesn't shift the current day/month
    from datetime import timezone, timedelta
    ist = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(ist)
    start_str = today.replace(day=1).strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")
    res = query_finance_data("summary", start_str, end_str)

    # 2. Calculate Total Savings (Income minus expenses for this month, excluding CC)
    total_savings = round(res.get('income', 0) - res.get('expenses', 0), 2)
    history = get_history()
    
    # db_path = get_latest_db()
    # db_name = os.path.basename(db_path) if db_path else "No DB"
    # db_date = ""
    # if db_path:
    #     import re
    #     # Filename example: cashew-2026-03-24-14-52-13-799971.sql
    #     match = re.search(r"(\d{4}-\d{2}-\d{2})", db_name)
    #     if match:
    #         try:
    #             # Format to a readable date
    #             dt_obj = datetime.strptime(match.group(1), "%Y-%m-%d")
    #             db_date = dt_obj.strftime("%B %d, %Y")
    #         except:
    #             db_date = match.group(1)
    #     else:
    #         db_date = datetime.fromtimestamp(os.path.getmtime(db_path)).strftime("%B %d, %Y")
    
    db_name = "RDS PostgreSQL"
    db_date = "Live"

    return jsonify({
        "current": {"savings": total_savings},
        "history": history,
        "db_info": {"name": db_name, "date": db_date}
    })

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_finance_data",
            "description": "Unified tool for all financial queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request_type": {"type": "string", "enum": ["summary", "list", "daily"], "description": "summary for totals, list for transactions, daily for spending days."},
                    "start_date": {"type": "string"}, "end_date": {"type": "string"},
                    "search_term": {"type": "string", "description": "A SINGLE item or category. If the user wrapped their search in quotes, YOU MUST PRESERVE the quotes in your JSON output by escaping them (e.g., if user asks for \"rice\", output '\\\"rice\\\"'). Do NOT strip the user's quotes."},
                    "sort": {"type": "string", "enum": ["DESC", "ASC", "AMOUNT_DESC", "AMOUNT_ASC"]},
                    "limit": {"type": "integer", "description": "Number of records to return. Default is 100 for keywords, 10 otherwise."}
                },
                "required": ["request_type", "start_date", "end_date"]
            }
        }
    }
]

def get_system_prompt():
    return f"""Today: {date.today().strftime('%A, %B %d, %Y')}. Currency: INR (₹).
You are Zaid's elite financial analyst. Use the query_finance_data tool for ALL queries.
Mappings: food->'food', transport->'transport', clothing->'clothing'.
Rules:
1. Default Period: {date.today().year} if none mentioned.
2. ALWAYS pass the user's search term EXACTLY. If the user used quotes (e.g., 'rice' or "rice"), YOU MUST PRESERVE THEM in the `search_term` parameter (e.g., pass "'rice'" or "\"rice\""). This is critical for distinguishing category searches (no quotes) from keyword searches (quotes). NEVER pass multiple items with 'or'/'and' in a single call.
3. If listing transactions, ALWAYS format them as a valid Markdown table with 'date', 'transaction_name', 'amount', 'main_category', and 'sub_category' columns. If 'note' is same as 'transaction_name', you can omit 'note' or combine them.
4. When asked for 'all' records or a specific search_term, ensure you retrieve a comprehensive list (the tool defaults to 100 for keywords, which is usually enough).
5. For semantic variations like "how much I spent on X" or "list my spending on X", always provide both the total aggregate AND the list of transactions to be most helpful.
6. Handle 'Balance Corrections': This is a category named 'Balance Correction'. If the user asks for corrections, use search_term='balance correction'.
7. Zero Result Strategy: If a specific search returns 0 results, try a broader term.
8. Always use the term 'Savings' or 'Net Savings' instead of 'Balance'.
9. ONLY report an anomaly inside `<anomaly>...</anomaly>` tags at the end of your response if you find a transaction that is categorized under a parent category but is NOT assigned to any subcategory. Do NOT report any other type of anomaly.
"""

conversation_history = []

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.json
    if not data: return jsonify({"reply": "No data received."}), 400
    if data.get("reset"): conversation_history = []; return jsonify({"reply": "Reset."})

    user_input = data.get("message", "")
    logging.info(f"User Request: {user_input}")

    conversation_history.append({"role": "user", "content": user_input})
    # Keep history from growing too large (last 10 turns)
    if len(conversation_history) > 20: conversation_history = conversation_history[-20:]

    messages = [{"role": "system", "content": get_system_prompt()}] + conversation_history    
    try:
        logging.debug("Calling Groq API (first pass)...")
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, tools=TOOLS, tool_choice="auto")
        ai_msg = response.choices[0].message
        
        if ai_msg.tool_calls:
            logging.debug(f"Tool calls detected: {len(ai_msg.tool_calls)}")
            tool_msg = ai_msg.model_dump(exclude_unset=True)
            messages.append(tool_msg)
            conversation_history.append(tool_msg)
            
            for tc in ai_msg.tool_calls:
                logging.debug(f"Executing tool: {tc.function.name} with args: {tc.function.arguments}")
                res = query_finance_data(**json.loads(tc.function.arguments))
                tool_res = {"role": "tool", "tool_call_id": tc.id, "content": json.dumps(res)}
                messages.append(tool_res)
                conversation_history.append(tool_res)
            
            logging.debug("Calling Groq API (final pass)...")
            final_res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
            reply = final_res.choices[0].message.content or "I couldn't generate a response."
        else:
            reply = ai_msg.content or "I'm not sure how to answer that."
            
        logging.info(f"AI Response: {reply[:100]}...")
        conversation_history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})
        
    except Exception as e:
        logging.exception("Chat logic failed:")
        return jsonify({"reply": f"I encountered an error: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
