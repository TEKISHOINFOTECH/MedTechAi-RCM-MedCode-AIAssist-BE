# 🔑 How to Configure OpenAI API Key

## 📍 Three Ways to Set Your API Key

### ✅ **Option 1: Environment Variable (Recommended for Testing)**

**For Current Terminal Session:**

```bash
# Set the API key
export OPENAI_API_KEY="sk-proj-your-actual-key-here"

# Verify it's set
echo $OPENAI_API_KEY

# Run tests
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC
make test-integration
```

**Pros:** Quick, temporary, secure  
**Cons:** Lost when you close terminal

---

### ✅ **Option 2: .env File (Recommended for Development)**

**Step 1: Create .env file**

```bash
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC

# Create .env file
cat > .env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Optional: Other providers
GOOGLE_API_KEY=your-google-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# LLM Settings
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large

# App Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
EOF
```

**Step 2: Update config/settings.py to load .env**

The `config/settings.py` file already uses `python-dotenv`, so it will automatically load `.env` file!

**Step 3: Verify**

```bash
# Run app (it will auto-load .env)
make run

# Or run tests
make test-integration
```

**Pros:** Persistent, easy to manage, not in git  
**Cons:** Need to create file  
**Security:** ✅ Already in `.gitignore`

---

### ✅ **Option 3: Shell Profile (Permanent)**

**For zsh (macOS default):**

```bash
# Add to ~/.zshrc
echo 'export OPENAI_API_KEY="sk-proj-your-actual-key-here"' >> ~/.zshrc

# Reload
source ~/.zshrc

# Verify
echo $OPENAI_API_KEY
```

**For bash:**

```bash
# Add to ~/.bashrc
echo 'export OPENAI_API_KEY="sk-proj-your-actual-key-here"' >> ~/.bashrc

# Reload
source ~/.bashrc

# Verify
echo $OPENAI_API_KEY
```

**Pros:** Always available  
**Cons:** Stored in plain text in shell config  

---

## 🎯 Quick Start (Recommended Method)

### Using .env File

```bash
# 1. Navigate to project
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC

# 2. Copy example file
cp env.example .env

# 3. Edit .env file (use nano, vim, or any editor)
nano .env

# 4. Replace with your actual key:
#    OPENAI_API_KEY=sk-proj-your-real-key-here

# 5. Save and exit (Ctrl+X, then Y, then Enter for nano)

# 6. Verify it works
make test-integration
```

---

## 🔍 How to Get Your OpenAI API Key

### Step 1: Go to OpenAI Platform

Visit: https://platform.openai.com/api-keys

### Step 2: Sign In

Log in with your OpenAI account

### Step 3: Create API Key

1. Click "Create new secret key"
2. Give it a name (e.g., "MedTechAI RCM Dev")
3. Copy the key (starts with `sk-proj-...`)
4. **Important:** Save it immediately - you won't see it again!

### Step 4: Add Credits (if needed)

- Go to: https://platform.openai.com/account/billing
- Add payment method and credits

---

## ✅ Verify Configuration

### Test 1: Check Environment Variable

```bash
# In terminal
echo $OPENAI_API_KEY

# Should show: sk-proj-...
# If empty, it's not set
```

### Test 2: Run Simple Connectivity Test

```bash
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC

# Test OpenAI connection
uv run pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection -v
```

**Expected Output:**
```
tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection 
✓ OpenAI connection successful: success
PASSED [100%]
```

### Test 3: Check Config Loading

```bash
# Start Python and check
uv run python -c "from config import settings; print('API Key configured:', bool(settings.openai_api_key))"

# Should print: API Key configured: True
```

---

## 📂 Where Files Are Located

### Project Directory

```
/Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC/
├── .env                    ← Create this file (from env.example)
├── env.example             ← Template file
├── config/
│   └── settings.py         ← Reads .env automatically
├── .gitignore              ← Already includes .env
└── tests/
    └── integration/        ← Tests that need API key
```

### Configuration File

The `config/settings.py` already has code to read environment variables:

```python
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str = ""  # Reads from OPENAI_API_KEY env var
    # ... other settings
```

---

## 🔐 Security Best Practices

### ✅ DO:

- ✅ Use `.env` file for local development
- ✅ Keep `.env` in `.gitignore` (already done)
- ✅ Use environment variables in production
- ✅ Rotate keys regularly
- ✅ Use different keys for dev/staging/prod

### ❌ DON'T:

- ❌ Commit API keys to git
- ❌ Share API keys in public channels
- ❌ Hardcode keys in source code
- ❌ Use production keys in development
- ❌ Store keys in plain text files (except .env which is gitignored)

---

## 🚀 Complete Setup Example

### Terminal Commands

```bash
# 1. Navigate to project
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC

# 2. Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-paste-your-real-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
ENVIRONMENT=development
DEBUG=true
EOF

# 3. Verify file was created
cat .env

# 4. Test connectivity
uv run pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection -v

# 5. Run all tests
make test-integration

# 6. Start backend (will auto-load .env)
make run
```

---

## 🐛 Troubleshooting

### Issue: "API key not configured" error

**Check 1: Is the key set?**
```bash
echo $OPENAI_API_KEY
# If empty, it's not set
```

**Check 2: Is .env file present?**
```bash
ls -la .env
cat .env | grep OPENAI_API_KEY
```

**Check 3: Is key format correct?**
```bash
# Should start with sk-proj- or sk-
echo $OPENAI_API_KEY | grep -E "^sk-"
```

**Fix:** Re-create .env file with correct key

---

### Issue: Tests still skipped

**Check:** Run with verbose skip reasons
```bash
uv run pytest tests/integration/ -v -rs
```

**Look for:** `SKIPPED [1] ... : OpenAI API key not configured`

**Fix:** Ensure key is set and valid

---

### Issue: "Invalid API key" error

**Possible causes:**
1. Key copied incorrectly (missing characters)
2. Key has been revoked
3. Account has no credits

**Fix:** 
1. Check key format (starts with `sk-proj-` or `sk-`)
2. Verify key at https://platform.openai.com/api-keys
3. Check billing at https://platform.openai.com/account/billing

---

### Issue: ".env file not loading"

**Check:** Is python-dotenv installed?
```bash
uv pip list | grep dotenv
```

**Fix:** Install if missing
```bash
uv pip install python-dotenv
```

**Verify:** Check config loads it
```bash
grep -n "load_dotenv" config/settings.py
```

---

## 📋 Checklist

Before running tests with API key:

- [ ] Have OpenAI API key from https://platform.openai.com/api-keys
- [ ] Key starts with `sk-proj-` or `sk-`
- [ ] Created `.env` file in project root
- [ ] Added `OPENAI_API_KEY=sk-...` to `.env`
- [ ] Verified key is set: `echo $OPENAI_API_KEY` or check `.env`
- [ ] Account has credits at https://platform.openai.com/account/billing
- [ ] Ran connectivity test successfully

---

## 🎯 What to Run After Configuration

```bash
# 1. Test connectivity
make test-connectivity

# 2. Test workflows
make test-workflow

# 3. Run all tests
make test-integration

# 4. Start backend
make run

# 5. Start Streamlit UI
cd streamlit_app && streamlit run app.py
```

---

## 📞 Need Help?

### Quick Fixes

```bash
# Reset everything and start fresh
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC

# Remove old .env
rm -f .env

# Create new .env
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-your-actual-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EOF

# Test
make test-connectivity
```

### Documentation

- Main guide: `TESTING_GUIDE.md`
- Quick reference: `QUICK_TEST_REFERENCE.md`
- This file: `HOW_TO_CONFIGURE_API_KEY.md`

---

## ✅ Summary

**Recommended approach:**

1. Create `.env` file in project root
2. Add `OPENAI_API_KEY=sk-proj-...`
3. The app will automatically load it
4. Run tests with `make test-integration`

**One-liner setup:**

```bash
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC && echo "OPENAI_API_KEY=sk-proj-your-key" > .env && make test-connectivity
```

(Replace `sk-proj-your-key` with your actual key)

