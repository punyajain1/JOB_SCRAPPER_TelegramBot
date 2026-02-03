# 📱 Termux Setup Guide for Job Automation

## 🎯 Overview
This guide will help you run the Job Automation system + n8n **locally** on your Android tablet using Termux (4GB RAM).

**What you'll run:**
- ✅ Python Flask server (Job scraper API)
- ✅ n8n workflow automation (Node.js)
- ✅ Both running simultaneously in background

---

## ⚡ Quick Start (Copy-Paste Commands)

### Step 1: Initial Termux Setup

```bash
# Update packages
pkg update && pkg upgrade -y

# Install required packages
pkg install python nodejs git openssh termux-services -y

# Install proot for better compatibility
pkg install proot-distro -y

# Create project directory
mkdir -p ~/job-automation
cd ~/job-automation
```

### Step 2: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
# Note: Some packages might fail on Termux, we'll handle that
pip install flask python-dotenv requests pandas beautifulsoup4 lxml pydantic

# Install remaining deps (some might need compilation)
pip install markdownify tls-client urllib3 certifi regex

# If numpy fails, use this special command:
pkg install python-numpy -y  # Use Termux's prebuilt numpy
```

### Step 3: Get the Code

**Option A: Git Clone (Recommended)**
```bash
cd ~/job-automation
# Replace with your actual repo URL
git clone https://github.com/yourusername/job-automation.git .
```

**Option B: Manual Download & Copy**
If you downloaded the code manually (e.g., zip file):

1. **Extract** the zip file in your phone's Downloads folder.
2. **Setup storage access** in Termux:
   ```bash
   termux-setup-storage
   # Click 'Allow' on the permission popup
   ```
3. **Copy files** (assuming folder is in Downloads):
   ```bash
   # Adjust folder name if needed
   cp -r /sdcard/Download/job_automation/* ~/job-automation/
   ```

### Step 4: Install n8n

```bash
# Install n8n globally
npm install -g n8n

# Create n8n data directory
mkdir -p ~/.n8n
```

### Step 5: Configure Environment Variables

1. **No `.env` file needed anymore!** We now send configuration directly via the API.

2. However, if you want to set custom API parameters, you'll do that inside n8n or your curl request.

---

## 🚀 Running the Services

### Method 1: Using tmux (Recommended)

tmux allows you to run multiple sessions that persist when you close Termux.

```bash
# Install tmux
pkg install tmux -y

# Create a tmux session
tmux new-session -s automation

# Split into 2 panes (Ctrl+b then ")
# Top pane: n8n
# Bottom pane: Flask server

# In top pane, start n8n:
n8n start --tunnel

# Switch to bottom pane (Ctrl+b then arrow down)
# Start Flask server:
cd ~/job-automation
python server.py

# Detach from tmux session: Ctrl+b then d
# Reattach later: tmux attach -t automation
# Kill session: tmux kill-session -t automation
```

### Method 2: Using Background Processes

```bash
# Start n8n in background
nohup n8n start > ~/n8n.log 2>&1 &

# Start Flask server in background
cd ~/job-automation
nohup python server.py > ~/server.log 2>&1 &

# View logs
tail -f ~/n8n.log      # n8n logs
tail -f ~/server.log   # Flask logs

# Stop processes later
pkill -f n8n
pkill -f server.py
```

### Method 3: Create Startup Scripts

Create a convenient startup script:

```bash
cat > ~/start-automation.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Starting Job Automation System..."

# Start n8n
echo "📊 Starting n8n..."
nohup n8n start > ~/n8n.log 2>&1 &
N8N_PID=$!
echo "n8n started with PID: $N8N_PID"

# Wait for n8n to start
sleep 5

# Start Flask server
echo "🔍 Starting Job Scraper Server..."
cd ~/job-automation
nohup python server.py > ~/server.log 2>&1 &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

echo ""
echo "✅ All services started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 n8n:         http://localhost:5678"
echo "🔍 Job Server:  http://localhost:5000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs:"
echo "  n8n:     tail -f ~/n8n.log"
echo "  server:  tail -f ~/server.log"
echo ""
echo "To stop:"
echo "  bash ~/stop-automation.sh"
EOF

# Make executable
chmod +x ~/start-automation.sh
```

Create a stop script:

```bash
cat > ~/stop-automation.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

echo "🛑 Stopping Job Automation System..."

# Stop n8n
pkill -f n8n
echo "✅ n8n stopped"

# Stop Flask server
pkill -f server.py
echo "✅ Server stopped"

echo "🏁 All services stopped!"
EOF

# Make executable
chmod +x ~/stop-automation.sh
```

---

## 🔧 Setting Up n8n Workflow

1. **Start n8n** (if not already running):
   ```bash
   n8n start
   ```

2. **Access n8n**:
   - Open browser on your tablet: `http://localhost:5678`
   - Create an account (all data stored locally)

3. **Create the workflow**:
   - Addan HTTP Request node
   - Method: POST
   - URL: `http://localhost:5000/job-search`
   - Body Parameters:
     ```json
     {
       "SEARCH_TERM": "python developer",
       "LOCATION": "India",
       "HOURS_OLD": 72,
       "JOB_TYPE": "internship"
     }
     ```

4. **Activate the workflow** in n8n

---

## 🤖 Making it Fully Automated (Production Mode)

You currently have to click "Execute" manually. To make it run automatically on its own:

### 1. Add a Schedule Trigger
 If you want it to scrape automatically (e.g., every day):
1. Add a **Schedule Trigger** node in n8n.
2. Configure it (e.g., "Interval" -> 3 hours).
3. Connect it to your **HTTP Request** node.

### 2. Activate the Workflow
**This is the most important step!**
1. Look at the top-right corner of your n8n canvas.
2. Toggle the switch from **Inactive** to **Active**.
3. Confirm the dialog.
   - *Note: In "Active" mode, the generic "Execute Workflow" button changes behavior. You usually rely on the triggers now.*

### 3. Use PM2 for Process Management (Better than nohup)
For a true "production" feel where apps restart if they crash:

```bash
# Install PM2 (Process Manager)
npm install -g pm2

# Start n8n
pm2 start n8n

# Start Flask Server
pm2 start server.py --interpreter python3

# Check status
pm2 list

# Monitor logs
pm2 monit

# Stop everything
pm2 stop all
```

---

## 📊 Resource Management (4GB RAM)

Your tablet has 4GB RAM. Here's the typical usage:

| Service | RAM Usage | Notes |
|---------|-----------|-------|
| Android OS | ~1.5 GB | System |
| Termux | ~200 MB | Base |
| Python/Flask | ~150 MB | Job scraper |
| n8n (Node.js) | ~300 MB | Workflow engine |
| **Total** | **~2.15 GB** | **You have 1.8GB free** ✅ |

**Tips to save RAM:**
- Close other apps while running automation
- Use `top` command to monitor: `pkg install htop && htop`
- If RAM is tight, run one service at a time

---

## 🧪 Testing Your Setup

### Test 1: Check Flask Server
```bash
# Health check
curl http://localhost:5000/health

# Should return: {"status":"healthy","message":"Job Scraper Server is running"}
```

### Test 2: Test Job Search
```bash
curl -X POST http://localhost:5000/job-search \
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

---

## 🔄 Auto-Start on Boot (Optional)

Make services start automatically when you open Termux:

```bash
# Edit bash profile
nano ~/.bashrc

# Add these lines at the end:
echo "Job Automation System available"
echo "Start: bash ~/start-automation.sh"
echo "Stop:  bash ~/stop-automation.sh"
```

---

## 🐛 Troubleshooting

### Problem: numpy installation fails
```bash
# Use Termux's prebuilt version
pkg install python-numpy -y
```

### Problem: lxml installation fails
```bash
pkg install libxml2 libxslt -y
pip install lxml
```

### Problem: Can't access from other devices
```bash
# Find your tablet's IP
ifconfig

# Run Flask with external access:
# Edit server.py, change the last line to:
# app.run(host='0.0.0.0', port=5000, debug=True)
```

### Problem: Port already in use
```bash
# Kill process on port 5000
pkill -f server.py

# Kill process on port 5678
pkill -f n8n
```

### Problem: Services stop when closing Termux
- Use **tmux** (Method 1) or **background processes** (Method 2)
- Install: `pkg install termux-services`

---

## 📱 Using from Browser

Once everything is running:

1. **On your tablet**:
   - n8n: `http://localhost:5678`
   - API: `http://localhost:5000`

2. **From other devices on same WiFi**:
   - Find tablet IP: `ifconfig` (look for wlan0)
   - n8n: `http://TABLET_IP:5678`
   - API: `http://TABLET_IP:5000`

---

## 💡 Pro Tips

1. **Save battery**: Services consume battery. Stop when not needed.
   ```bash
   bash ~/stop-automation.sh
   ```

2. **Monitor resources**:
   ```bash
   pkg install htop -y
   htop
   ```

3. **View logs in real-time**:
   ```bash
   tail -f ~/n8n.log ~/server.log
   ```

4. **Backup your work**:
   ```bash
   cd ~/job-automation
   tar -czf backup-$(date +%Y%m%d).tar.gz .
   ```

5. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   npm update -g n8n
   ```

---

## 🚫 Why NOT Docker on Termux?

- ❌ Docker requires root access (Termux is non-root)
- ❌ Heavy resource usage (your 4GB RAM would struggle)
- ❌ Unreliable on Android (proot-docker has many issues)
- ✅ Native installation is faster, lighter, and more stable

---

## 📞 Need Help?

Check logs:
```bash
tail -100 ~/n8n.log
tail -100 ~/server.log
```

Check running processes:
```bash
ps aux | grep -E 'n8n|python'
```

Check ports:
```bash
netstat -tuln | grep -E '5000|5678'
```

---

## 🎉 You're All Set!

Your job automation system is now running locally on your Android tablet:
- ✅ No cloud needed
- ✅ Complete privacy
- ✅ Free to use
- ✅ Runs in background

**Start automation:**
```bash
bash ~/start-automation.sh
```

**Stop automation:**
```bash
bash ~/stop-automation.sh
```

Happy job hunting! 🚀
