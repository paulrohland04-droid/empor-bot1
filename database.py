import sqlite3
import datetime
import hashlib
import os
import config

def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            duration TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'unused',
            hwid TEXT,
            created_at TEXT NOT NULL,
            activated_at TEXT,
            expires_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_key():
    raw = os.urandom(16)
    key_hash = hashlib.sha256(raw).hexdigest()[:20].upper()
    formatted = f"EMPOR-{key_hash[:5]}-{key_hash[5:10]}-{key_hash[10:15]}-{key_hash[15:20]}"
    return formatted

def create_license(duration):
    if duration not in ("1day", "7days", "30days", "lifetime"):
        return None
    key = generate_key()
    now = datetime.datetime.utcnow().isoformat()
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO licenses (license_key, duration, status, created_at) VALUES (?, ?, 'unused', ?)",
            (key, duration, now)
        )
        conn.commit()
        return key
    except sqlite3.IntegrityError:
        return create_license(duration)
    finally:
        conn.close()

def calculate_expiry(duration):
    if duration == "lifetime":
        return None
    days = {"1day": 1, "7days": 7, "30days": 30}
    return (datetime.datetime.utcnow() + datetime.timedelta(days=days[duration])).isoformat()

def verify_license(key, hwid):
    conn = get_db()
    row = conn.execute("SELECT * FROM licenses WHERE license_key = ?", (key,)).fetchone()
    conn.close()

    if not row:
        return {"success": False, "error": "Invalid key"}

    if row["status"] == "banned":
        return {"success": False, "error": "Key is banned"}

    if row["status"] == "expired":
        return {"success": False, "error": "Key expired"}

    if row["status"] == "unused":
        if row["duration"] == "lifetime":
            expires_at = None
        else:
            expires_at = calculate_expiry(row["duration"])
        activated_at = datetime.datetime.utcnow().isoformat()
        conn = get_db()
        conn.execute(
            "UPDATE licenses SET status='active', hwid=?, activated_at=?, expires_at=? WHERE license_key=?",
            (hwid, activated_at, expires_at, key)
        )
        conn.commit()
        conn.close()
        return {
            "success": True,
            "duration": row["duration"],
            "expires_at": expires_at,
            "message": "Key activated"
        }

    if row["status"] == "active":
        if row["hwid"] != hwid:
            return {"success": False, "error": "Key already activated on another PC"}
        if row["duration"] != "lifetime":
            expires = datetime.datetime.fromisoformat(row["expires_at"])
            if expires < datetime.datetime.utcnow():
                conn = get_db()
                conn.execute("UPDATE licenses SET status='expired' WHERE license_key=?", (key,))
                conn.commit()
                conn.close()
                return {"success": False, "error": "Key expired"}
            remaining = (expires - datetime.datetime.utcnow()).days
            return {
                "success": True,
                "duration": row["duration"],
                "expires_at": row["expires_at"],
                "remaining_days": remaining,
                "message": f"Key valid, {remaining} days remaining"
            }
        return {
            "success": True,
            "duration": "lifetime",
            "expires_at": None,
            "message": "Lifetime key valid"
        }

    return {"success": False, "error": "Unknown error"}

def get_all_licenses():
    conn = get_db()
    rows = conn.execute("SELECT * FROM licenses ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_license(key):
    conn = get_db()
    conn.execute("DELETE FROM licenses WHERE license_key = ?", (key,))
    conn.commit()
    conn.close()

def reset_license(key):
    conn = get_db()
    conn.execute("UPDATE licenses SET status='unused', hwid=NULL, activated_at=NULL, expires_at=NULL WHERE license_key=?", (key,))
    conn.commit()
    conn.close()

init_db()
