# Railway Quick Start (TL;DR)

## 5-Minute Setup

### 1. Get Your Bot Token
- Discord Developer Portal → Your Bot → Copy Token

### 2. Create GitHub Account
- Go to github.com, sign up (takes 2 mins)

### 3. Create GitHub Repository
- Click **+** → **New Repository**
- Name: `discord-broadcast-bot`
- Check "Add README"
- Create!

### 4. Add Files to GitHub

Click **Add file** → **Create new file**, then:

**File 1: `discord_broadcast_bot.py`**
- Copy-paste the bot code

**File 2: `requirements.txt`**
```
discord.py==2.3.2
python-dotenv==1.0.0
```

**File 3: `Procfile`**
```
worker: python discord_broadcast_bot.py
```

**File 4: `.gitignore`**
```
broadcast_config.json
permissions.json
*.pyc
__pycache__/
.env
```

(Commit each one)

### 5. Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click **New Project**
3. Click **Deploy from GitHub**
4. Select `discord-broadcast-bot` repository
5. Railway deploys automatically!

### 6. Add Your Bot Token

In Railway dashboard:
1. Click your project
2. Click **Variables**
3. Click **New Variable**
4. Name: `DISCORD_BOT_TOKEN`
5. Value: Paste your token
6. Done! Bot starts automatically

### 7. Test It

1. Go to Discord
2. Type `/broadcast test`
3. ✅ It works!

---

## That's It! 🚀

Your bot now runs **24/7 for free**. No computer needed!

---

## Need More Details?
Read `RAILWAY_SETUP.md` for the full guide with screenshots and troubleshooting.
