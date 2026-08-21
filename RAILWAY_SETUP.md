# Deploy Discord Bot to Railway (Complete Guide)

Railway will run your bot **24/7 for free** so it's always online!

---

## Step 1: Prepare Your Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click your application
3. Go to **Bot** section
4. Under **TOKEN**, click **Copy**
5. **Save this token somewhere secure** - you'll need it soon!

---

## Step 2: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **Sign Up** (top right)
3. Use GitHub to sign up (easiest method)
4. Authorize Railway to access your GitHub

---

## Step 3: Create a GitHub Repository

Railway deploys from GitHub. Here's how to set it up:

### Option A: Using GitHub Web (Easiest)

1. Go to [github.com](https://github.com) and log in
2. Click **+** icon (top right) → **New repository**
3. Name it: `discord-broadcast-bot`
4. Set to **Public**
5. Check "Add a README file"
6. Click **Create repository**

### Option B: Using Command Line

```bash
# Create folder
mkdir discord-broadcast-bot
cd discord-broadcast-bot

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Connect to GitHub (create empty repo on github.com first, then run):
git remote add origin https://github.com/YOUR_USERNAME/discord-broadcast-bot.git
git branch -M main
git push -u origin main
```

---

## Step 4: Add Your Bot Code to GitHub

### If Using GitHub Web:

1. In your repository, click **Add file** → **Create new file**
2. Name it: `discord_bot.py`
3. Copy-paste the bot code into it
4. Click **Commit changes**

5. Repeat for `requirements.txt`:
```
discord.py==2.3.2
python-dotenv==1.0.0
```

6. Repeat for `.gitignore`:
```
broadcast_config.json
permissions.json
*.pyc
__pycache__/
.env
```

### If Using Command Line:

In your `discord-broadcast-bot` folder:

```bash
# Create files
echo "discord.py==2.3.2
python-dotenv==1.0.0" > requirements.txt

echo "broadcast_config.json
permissions.json
*.pyc
__pycache__/
.env" > .gitignore

# Copy the bot code
# (Copy discord_broadcast_bot.py into this folder)
mv discord_broadcast_bot.py discord_bot.py

# Push to GitHub
git add .
git commit -m "Add bot code"
git push
```

---

## Step 5: Update Your Bot Code for Railway

In your bot file, change the last few lines from:

```python
if __name__ == "__main__":
    TOKEN = input("Enter your Discord bot token: ")
    bot.run(TOKEN)
```

To:

```python
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN not set in environment variables!")
    bot.run(TOKEN)
```

Then commit this change:
```bash
git add discord_bot.py
git commit -m "Update for Railway environment variables"
git push
```

---

## Step 6: Deploy on Railway

1. Go to [railway.app](https://railway.app) and log in
2. Click **New Project** (top right)
3. Click **Deploy from GitHub**
4. Select your `discord-broadcast-bot` repository
5. Click **Deploy**

Railway will:
- Detect it's a Python project
- Install dependencies from `requirements.txt`
- Start your bot automatically

---

## Step 7: Add Your Discord Bot Token

1. In Railway, your project should be deploying
2. Click on the project name
3. Click the **Variables** tab
4. Click **New Variable**
5. Name: `DISCORD_BOT_TOKEN`
6. Value: Paste your bot token (the one you copied earlier)
7. Press Enter

**Your bot will automatically restart and connect!**

---

## Step 8: Verify It's Running

1. Go to your Discord server
2. Type `/broadcast test message`
3. Check if it appears in all configured channels
4. Look at Railway's **Build Logs** to confirm no errors

---

## Managing Your Bot on Railway

### View Logs:
1. Open your Railway project
2. Click **Deployment** tab
3. Scroll down to see real-time logs
4. This helps debug any issues

### Stop/Start Bot:
1. Click the **vertical three dots** on your project
2. Click **Pause** to stop it
3. Click **Deploy** to restart it

### Update Your Code:
1. Make changes to your GitHub repository
2. Railway automatically deploys the latest version
3. No need to manually update!

### Add Bot Token Again After Railway Restart:
If your project crashes, the environment variable stays saved, so your token won't reset.

---

## Your Bot's New Workflow

### Setup (One-Time):

1. **Get your Discord ID:**
   - Enable Developer Mode (User Settings → Advanced)
   - Right-click your username → Copy User ID

2. **Set up permissions:**
   - When you first use `/broadcast`, Railway creates `broadcast_config.json` and `permissions.json`
   - Use `/authorize [user]` to add your friend's access

3. **Add channels:**
   - Use `/add_channel [channel]` in each Discord server
   - Only you and authorized users can do this

### Daily Use:

- Type `/broadcast your message` in **any** Discord server where the bot is
- Message instantly appears in all configured channels
- Bot stays online 24/7 even if your computer is off!

---

## Free Tier Details

**Railway Free Tier Includes:**
- Free monthly credits (~$5 worth)
- Enough to run a simple Discord bot 24/7
- No credit card required to start

**If you run out:**
- Service pauses until next month
- Use their paid plans ($5-20/month) for unlimited usage

For a simple broadcast bot, free tier is more than enough!

---

## Troubleshooting

**"Bot not responding?"**
1. Check Railway deployment logs for errors
2. Verify `DISCORD_BOT_TOKEN` is set correctly
3. Make sure bot has permissions in Discord servers

**"'requirements.txt not found' error?"**
- Make sure `requirements.txt` is in your GitHub repo root folder
- Try pushing it again if you just added it

**"Bot token not recognized?"**
1. Go to Railway → Variables
2. Check `DISCORD_BOT_TOKEN` is spelled exactly right
3. Verify the token value (no extra spaces)
4. Restart deployment

**"Changes not deploying?"**
1. Push your code to GitHub
2. Railway automatically redeploys within 1-2 minutes
3. Check **Build Logs** to see if it's deploying

**"Module not found (discord, dotenv)?"**
- Make sure `requirements.txt` has:
  ```
  discord.py==2.3.2
  python-dotenv==1.0.0
  ```
- Push it to GitHub and Railway will reinstall

---

## Next Steps

1. Create GitHub repo
2. Add bot code + requirements.txt + .gitignore
3. Update bot code for environment variables
4. Deploy to Railway
5. Add `DISCORD_BOT_TOKEN` variable
6. Add channels with `/add_channel`
7. Start broadcasting!

Your bot is now running in the cloud 24/7! 🚀
