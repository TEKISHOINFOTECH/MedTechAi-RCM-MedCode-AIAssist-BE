# 🛑 How to Stop Running Processes

## Stop Backend Server in Terminal

### **Option 1: Stop with Ctrl+C** (Simplest)

If the terminal is active and showing logs:

```bash
# Press in the terminal window:
Ctrl + C

# This sends SIGINT to stop the process gracefully
```

---

### **Option 2: Find and Kill the Process**

If Ctrl+C doesn't work or terminal is unresponsive:

```bash
# Find what's running on port 8001 (backend)
lsof -i :8001

# You'll see output like:
# COMMAND   PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# python3  12345 apple  3u  IPv4 0x...      0t0  TCP *:8001 (LISTEN)

# Kill the process (replace 12345 with actual PID)
kill 12345

# Or force kill if needed
kill -9 12345
```

**Quick one-liner:**
```bash
# Kill any process on port 8001
lsof -ti :8001 | xargs kill -9
```

---

### **Option 3: Use pkill** (Kill by name)

```bash
# Kill uvicorn processes
pkill -f uvicorn

# Or kill any Python process running your app
pkill -f "medtechai"
```

---

### **Option 4: Find All Background Jobs**

If you started with `&` (background):

```bash
# List all background jobs
jobs

# Kill specific job (replace %1 with job number)
kill %1

# Or bring to foreground and Ctrl+C
fg %1
# Then press Ctrl+C
```

---

## Stop Streamlit (Port 8501)

```bash
# Find Streamlit process
lsof -i :8501

# Kill it
lsof -ti :8501 | xargs kill -9

# Or by name
pkill -f streamlit
```

---

## Stop All Project Processes

```bash
# Kill all uvicorn (backend)
pkill -f uvicorn

# Kill all streamlit (frontend)
pkill -f streamlit

# Or both at once
pkill -f "uvicorn|streamlit"
```

---

## Verify Processes Stopped

```bash
# Check port 8001 (backend)
lsof -i :8001
# Should return nothing if stopped

# Check port 8501 (streamlit)
lsof -i :8501
# Should return nothing if stopped

# Check all Python processes
ps aux | grep python
```

---

## Common Scenarios

### **Scenario 1: Server Won't Stop**

```bash
# Force kill on port 8001
lsof -ti :8001 | xargs kill -9

# Verify
lsof -i :8001
```

### **Scenario 2: Multiple Terminals Open**

```bash
# Stop all uvicorn instances
pkill -9 -f uvicorn

# Check what's still running
ps aux | grep uvicorn
```

### **Scenario 3: Process Running in Background**

```bash
# List background jobs
jobs -l

# Kill job 1
kill %1

# Or kill all jobs
kill $(jobs -p)
```

---

## Clean Restart

```bash
# Stop everything
pkill -f uvicorn
pkill -f streamlit

# Wait a moment
sleep 2

# Verify ports are free
lsof -i :8001
lsof -i :8501

# Start fresh
make run
```

---

## Terminal Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + C` | Stop current process (SIGINT) |
| `Ctrl + Z` | Suspend process (pause) |
| `Ctrl + D` | End input / Exit shell |
| `fg` | Resume suspended process |
| `bg` | Resume in background |
| `jobs` | List background jobs |

---

## Makefile Helper Commands

I can add these to your Makefile:

```bash
# Stop backend
make stop

# Restart backend
make restart

# Check status
make status
```

Would you like me to add these to your Makefile?

