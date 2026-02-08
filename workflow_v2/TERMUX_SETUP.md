# 📱 Termux Setup Guide for Job Automation (Hybrid Cloud Setup)

## 🎯 Overview
This guide helps you run **n8n locally** on your Android tablet while using a **cloud-hosted Flask server** on Railway.

**Architecture:**
```
┌─────────────────────┐      ┌──────────────────┐
│  Flask Server       │◄─────│  n8n (Local)     │
│  Railway (Cloud)    │      │  Your Termux     │
│  Always Available   │      │  Privacy + Free  │
└─────────────────────┘      └──────────────────┘
```

**What you'll run locally:**
- ✅ n8n workflow automation (Node.js)
- ✅ Lightweight & Battery-friendly

**What runs in the cloud:**
- ✅ Flask server (Railway free tier)
- ✅ Always accessible, no ngrok needed

---

## ⚡ Quick Start (Copy-Paste Commands)

### Step 1: Initial Termux Setup

```bash
# Update packages
pkg update && pkg upgrade -y

# Install Node.js for n8n
pkg install nodejs git -y

# Optional: Install termux-services for better process management
pkg install termux-services -y
```

### Step 2: Install n8n

```bash
# Install n8n globally
npm install -g n8n

# Create n8n data directory
mkdir -p ~/.n8n
```

### Step 3: Get Your Flask Server URL

Your Flask server is already deployed on Railway. You should have received a URL like:
```
https://your-app.up.railway.app
```

If you haven't deployed yet, see the [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) guide (it takes 5 minutes).

---

## 🚀 Running n8n

### Method 1: Using tmux (Recommended)

tmux keeps n8n running even when you close Termux.

```bash
# Install tmux
pkg install tmux -y

# Create a tmux session
tmux new-session -s automation

# Start n8n:
n8n start

# Detach from tmux session: Ctrl+b then d
# Reattach later: tmux attach -t automation
# Kill session: tmux kill-session -t automation
```

### Method 2: Using Background Process

```bash
# Start n8n in background
nohup n8n start > ~/n8n.log 2>&1 &

# View logs
tail -f ~/n8n.log

# Stop n8n later
pkill -f n8n
```

### Method 3: Using PM2 (Production-Ready)

```bash
# Install PM2 (Process Manager)
npm install -g pm2

# Start n8n
pm2 start n8n

# Check status
pm2 list

# Monitor logs
pm2 logs n8n

# Stop n8n
pm2 stop n8n

# Auto-restart on reboot (optional)
pm2 startup
pm2 save
```

### Quick Start Script

Create a convenient startup script:

```bash
cat > ~/start-n8n.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Starting n8n Workflow Automation..."
nohup n8n start > ~/n8n.log 2>&1 &

sleep 3
echo ""
echo "✅ n8n started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 n8n Dashboard: http://localhost:5678"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs: tail -f ~/n8n.log"
echo "Stop: pkill -f n8n"
EOF

chmod +x ~/start-n8n.sh
```

Now just run:
```bash
bash ~/start-n8n.sh
```

---

## 🔧 Setting Up n8n Workflow

1. **Start n8n** (if not already running):
   ```bash
   bash ~/start-n8n.sh
   # Or: n8n start
   ```

2. **Access n8n**:
   - Open browser on your tablet: `http://localhost:5678`
   - Create an account (all data stored locally)

3. **Create the workflow**:
   - Add an **HTTP Request** node
   - Method: **POST**
   - URL: `https://your-app.up.railway.app/job-search` ⬅️ **Use your Railway URL**
   - Body Content Type: JSON
   - Body Parameters:
     ```json
     {
       "SEARCH_TERM": "python developer",
       "LOCATION": "India",
       "HOURS_OLD": 72,
       "JOB_TYPE": "internship"
     }
     ```

4. **Test it**: Click "Test Workflow" to ensure it connects to your Railway server

5. **Activate the workflow** by toggling the switch in the top-right corner

---

## 🤖 Making it Fully Automated (Production Mode)

You currently have to click "Execute" manually. To make it run automatically on its own:

### Understanding Triggers in n8n

**Your workflow has 2 triggers** - here's how they work:

1. **Manual Trigger** - For testing (click "Execute Workflow")
2. **Automatic Trigger** - For production (runs on its own)

### Step 1: Choose Your Trigger Type

**Option A: Schedule Trigger** (Most Common)
For automatic scraping at specific times/intervals:

1. In n8n, click **"+"** to add a node
2. Search for **"Schedule Trigger"**
3. Configure it:
   - **Interval**: Run every X hours/days
     - Example: Every 3 hours
     - Example: Every day at 9 AM
   - **Cron Expression**: Advanced scheduling
     - Example: `0 9,17 * * *` (9 AM and 5 PM daily)

**Option B: Webhook Trigger**
For triggering from external systems:

1. Add a **"Webhook"** node
2. n8n will give you a URL like: `http://localhost:5678/webhook/job-trigger`
3. Call this URL to trigger the workflow

### Step 2: Connect Your Trigger

1. **Delete or disconnect** the manual trigger node
2. **Connect** your Schedule/Webhook trigger to the HTTP Request node
3. Your flow should look like:
   ```
   [Schedule Trigger] → [HTTP Request to Railway] → [Process Jobs] → [Send Email]
   ```

### Step 3: Activate the Workflow ⚡ **MOST IMPORTANT**

1. Look at the **top-right corner** of your workflow
2. Find the toggle switch (currently says "Inactive")
3. **Click to toggle it to "Active"**
4. Confirm any prompts

**When Active:**
- ✅ Triggers will fire automatically
- ✅ Workflow runs in background
- ✅ No need to click "Execute"
- ⚠️ The workflow must stay active for triggers to work

### Step 4: Handle Multiple Users/Scenarios

If you want to scrape jobs for **multiple users** or **different search terms**:

**Method 1: Multiple Workflows** (Recommended)
- Create one workflow per user/scenario
- Each workflow has its own trigger schedule
- Easy to manage individually

**Method 2: Loop Through Users** (Advanced)
1. Add a **"Set"** node with user data:
   ```json
   [
     {"name": "User1", "search": "python developer", "location": "Mumbai"},
     {"name": "User2", "search": "data analyst", "location": "Delhi"}
   ]
   ```
2. Add a **"Loop Over Items"** node
3. Each iteration calls the Railway API with different parameters

### Step 5: Test Your Setup

1. **Activate** the workflow
2. **Wait** for the trigger to fire (or trigger manually for testing)
3. **Check Executions**:
   - Click "Executions" in the left sidebar
   - See all past runs
   - Debug any errors

### Example: Daily Job Scraper

**Workflow Setup:**
```
┌─────────────────┐
│ Schedule Trigger│  (Every day at 9 AM)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │  (Call Railway API)
│  POST /job-search
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Process Data   │  (Format jobs)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Send Email    │  (SMTP to your email)
└─────────────────┘
```

**Schedule Trigger Settings:**
- Mode: "Interval"
- Interval: 1 day
- Hour: 9
- Minute: 0

### Common Scenarios

**Scenario 1: Different Jobs for Different Times**
```
Workflow 1: Tech Jobs (9 AM daily)
Workflow 2: Finance Jobs (2 PM daily)
Workflow 3: Remote Jobs (6 PM daily)
```

**Scenario 2: Multiple Locations**
```
Single workflow with Set node:
- User1: Python jobs in Mumbai
- User2: Python jobs in Bangalore
- User3: Python jobs in Delhi
Then loop through each
```

### Monitoring Your Automated Workflows

```bash
# Check if n8n is running
pm2 list

# View n8n logs in real-time
pm2 logs n8n

# Check workflow executions in n8n dashboard
# Go to: http://localhost:5678 → Executions
```

---

## 📊 Resource Management (4GB RAM)

Your tablet has 4GB RAM. With Flask on the cloud, you only need to run n8n locally:

| Service | RAM Usage | Notes |
|---------|-----------|-------|
| Android OS | ~1.5 GB | System |
| Termux | ~100 MB | Base |
| n8n (Node.js) | ~300 MB | Workflow engine |
| **Total** | **~1.9 GB** | **You have 2GB+ free** ✅ |

**Much lighter than running both services locally!**

**Tips:**
- Close other apps while running automation
- Use `htop` to monitor: `pkg install htop -y && htop`
- n8n uses very little power when idle

---

## 🧪 Testing Your Setup

### Test 1: Check Your Railway Server
```bash
# Health check
curl https://your-app.up.railway.app/health

# Should return: {"status":"healthy","message":"Job Scraper Server is running"}
```

### Test 2: Test Job Search from Termux
```bash
curl -X POST https://your-app.up.railway.app/job-search \
  -H "Content-Type: application/json" \
  -d '{
    "SEARCH_TERM": "python developer",
    "LOCATION": "India",
    "HOURS_OLD": 72,
    "JOB_TYPE": "internship"
  }'
```

### Test 3: Check n8n
- Open browser: `http://localhost:5678`
- Should see n8n dashboard
- Create a workflow pointing to your Railway URL

---

## 🔄 Auto-Start on Boot (Optional)

Make n8n start automatically when you open Termux:

```bash
# Edit bash profile
nano ~/.bashrc

# Add these lines at the end:
echo ""
echo "Job Automation System"
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo "Start n8n: bash ~/start-n8n.sh"
echo "Stop n8n:  pkill -f n8n"
echo "Status:    pm2 list"
echo ""
```

---

## 🐛 Troubleshooting

### Problem: Can't connect to Railway server
```bash
# Check if your Railway app is running
curl https://your-app.up.railway.app/health

# If it fails, redeploy on Railway or check Railway dashboard
```

### Problem: n8n won't start
```bash
# Check if port 5678 is in use
netstat -tuln | grep 5678

# Kill any existing n8n process
pkill -f n8n

# Try starting again
n8n start
```

### Problem: Workflow not triggering
- Make sure the workflow is **Active** (toggle in top-right)
- Check if the Railway URL is correct in your HTTP Request node
- Test the URL manually with curl first

### Problem: n8n stops when closing Termux
- Use **tmux** or **PM2** (see Methods 1 & 3 above)
- Don't use simple `n8n start` in foreground

---

## 📱 Accessing Your System

**On your tablet:**
- n8n Dashboard: `http://localhost:5678`
- Flask Server: `https://your-app.up.railway.app` ⬅️ Works from anywhere!

**From other devices (same WiFi):**
- Find tablet IP: `ifconfig` (look for wlan0)
- n8n: `http://TABLET_IP:5678`
- Flask: `https://your-app.up.railway.app` (no IP needed - it's on the cloud!)

---

## 💡 Pro Tips

1. **Save battery**: n8n uses minimal power when idle. Stop it when not needed:
   ```bash
   pkill -f n8n
   # Or: pm2 stop n8n
   ```

2. **Monitor resources**:
   ```bash
   pkg install htop -y
   htop
   ```

3. **View n8n logs**:
   ```bash
   tail -f ~/n8n.log
   # Or: pm2 logs n8n
   ```

4. **Update n8n**:
   ```bash
   npm update -g n8n
   ```

5. **Backup your n8n workflows**:
   ```bash
   cd ~/.n8n
   tar -czf n8n-backup-$(date +%Y%m%d).tar.gz .
   ```

---

## 🌟 Why This Setup is Better

✅ **Lighter on Termux**: Only runs n8n (300MB) instead of Flask + n8n (500MB+)  
✅ **No Python dependencies**: Skip installing pandas, numpy, etc. on Termux  
✅ **Always accessible**: Flask server on Railway never goes down  
✅ **Better battery**: Less CPU usage = longer battery life  
✅ **Easier updates**: Update Flask on Railway without touching your tablet  
✅ **Still free**: Railway free tier + local n8n = $0/month  

---

## 📞 Need Help?

Check n8n logs:
```bash
tail -100 ~/n8n.log
# Or: pm2 logs n8n
```

Check running processes:
```bash
ps aux | grep n8n
# Or: pm2 list
```

Test Railway server:
```bash
curl https://your-app.up.railway.app/health
```

---

## 🎉 You're All Set!

Your job automation system is now running in **hybrid mode**:
- ✅ Flask server on Railway (cloud)
- ✅ n8n on Termux (local)
- ✅ Best of both worlds!
- ✅ Completely free

**Start n8n:**
```bash
bash ~/start-n8n.sh
# Or: pm2 start n8n
```

**Stop n8n:**
```bash
pkill -f n8n
# Or: pm2 stop n8n
```

**Your Flask API URL:**
```
https://your-app.up.railway.app/job-search
```

Happy job hunting! 🚀

---

## 📚 Next Steps

1. **Deploy Flask to Railway**: See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
2. **Create n8n Workflows**: Point them to your Railway URL
3. **Set up Schedule Triggers**: For automatic job scraping
4. **Configure Email Notifications**: Using SMTP in n8n

Need the Railway deployment guide? Let me know!
