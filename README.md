# EmporSync Discord Bot + Auth System

## How It Works

- **Discord Bot** – Create/Manage license keys via Slash-Commands
- **HTTP API** – The cheat sends key + HWID to verify
- **Railway.app** – Hosts bot + API 24/7, free

## Deploy to Railway

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway

### Step 2: Create Discord Bot Token
1. Go to https://discord.com/developers/applications
2. "New Application" → Name: `EmporSync`
3. "Bot" tab → "Reset Token" → **Copy the token**
4. Save it somewhere safe
5. "OAuth2" → "URL Generator" → Scopes: `bot` + `applications.commands`
6. Bot Permissions: `Send Messages`, `Read Messages`
7. Open generated URL → Add bot to your server

### Step 3: Deploy
1. Create a GitHub repository
2. Upload the `discord_bot/` folder contents to it
3. In Railway: "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Go to "Variables" tab → Add:
   - `DISCORD_TOKEN` = your bot token
   - `ADMIN_IDS` = `1498663781981491322`
6. Go to "Settings" → "Generate Domain"
7. Copy the URL (looks like `https://something.up.railway.app`)

### Step 4: Update Cheat
1. Open `auth.h` in the cheat source
2. Find the line: `std::string host = "empor-bot.up.railway.app";`
3. Replace with your actual Railway URL

### Step 5: Test
1. On Discord: `/createkey 7d` → Bot responds with key
2. Start cheat → Enter key → Should verify

## Discord Commands

| Command | Description | Who |
|---------|-------------|-----|
| `/createkey 1d` | Create 1-day key | Admin |
| `/createkey 7d` | Create 7-day key | Admin |
| `/createkey 30d` | Create 30-day key | Admin |
| `/createkey lifetime` | Create lifetime key | Admin |
| `/keys` | List all keys | Admin |
| `/deletekey KEY` | Delete a key | Admin |
| `/resetkey KEY` | Reset key to unused | Admin |

## Files

| File | Purpose |
|------|---------|
| `bot.py` | Discord Bot (Slash Commands) |
| `server.py` | HTTP API (Key verification endpoint) + Bot runner |
| `database.py` | SQLite key database |
| `config.py` | Configuration (token, admin IDs) |
| `requirements.txt` | Python packages |
| `Procfile` | Railway start command |
| `keys.db` | Auto-created SQLite database |
