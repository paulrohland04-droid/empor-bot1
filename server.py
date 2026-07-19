from flask import Flask, request, jsonify
import threading
import os
import sys
import database

app = Flask(__name__)

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    key = data.get("key", "").upper().strip()
    hwid = data.get("hwid", "").strip()
    if not key or not hwid:
        return jsonify({"success": False, "error": "Missing key or hwid"}), 400
    result = database.verify_license(key, hwid)
    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

def start_bot():
    import config
    if not config.DISCORD_TOKEN:
        print("[BOT] No DISCORD_TOKEN set, bot not starting")
        return
    try:
        import bot
        bot.client.run(config.DISCORD_TOKEN)
    except Exception as e:
        print(f"[BOT] Error: {e}")

if __name__ == "__main__":
    print("[API] Starting Flask...")
    port = int(os.environ.get("PORT", 8080))

    # Start Discord bot in background thread
    t = threading.Thread(target=start_bot, daemon=True)
    t.start()

    # Run Flask in main thread
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
