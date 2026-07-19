import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
ADMIN_IDS = [int(id) for id in os.environ.get("ADMIN_IDS", "1498663781981491322").split(",")]
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.db")
