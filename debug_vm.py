import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("--- VM Debugging Script ---")

# 1. Check Internet Connectivity
try:
    requests.get("https://google.com", timeout=5)
    print("✅ Internet: Reachable")
except Exception as e:
    print(f"❌ Internet: Unreachable ({e})")

# 2. Check Groq API Connectivity
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ API Key: Missing from .env")
else:
    print(f"✅ API Key: Found (ends in ...{api_key[-4:]})")
    try:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "hi"}],
            timeout=10
        )
        print("✅ Groq API: Success")
    except Exception as e:
        print(f"❌ Groq API: Failed ({e})")

# 3. Check DB Path
backup_dir = os.getenv("BACKUP_DIR")
print(f"🔍 DB Path Setting: {backup_dir}")
if backup_dir and os.path.exists(backup_dir):
    print(f"✅ DB Path: Exists")
    import glob
    sqls = glob.glob(os.path.join(backup_dir, "*.sql"))
    print(f"📊 DB Files: {len(sqls)} found")
else:
    print(f"❌ DB Path: Not found or invalid")

print("\n--- Next Steps ---")
print("1. If Groq API failed, check if your VM has outbound access to api.groq.com.")
print("2. Run 'tail -n 50 app.log' to see the detailed error logs from the Flask app.")
print("3. Run 'journalctl -u expense -n 50' for systemd logs.")
