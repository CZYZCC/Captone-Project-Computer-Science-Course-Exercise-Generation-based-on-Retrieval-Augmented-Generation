# 🔐 Security Guide: Protecting API Keys with GitGuardian

## ⚠️ CRITICAL: API Key Exposure Fixed

Your DeepSeek API key was previously hardcoded in `graphrag_mvp.py`. This has been remediated.

---

## 📋 GitGuardian Setup Steps

### 1. **Install GitGuardian (Already Done ✓)**
You mentioned you've already installed GitGuardian.

### 2. **Connect Your GitHub Repository to GitGuardian**

#### Option A: Via GitGuardian Dashboard (Recommended)
1. Go to https://dashboard.gitguardian.com/
2. Sign in with your GitHub account
3. Click **"Add Repositories"**
4. Select your repository:
   ```
   CZYZCC/Captone-Project-Computer-Science-Course-Exercise-Generation-based-on-Retrieval-Augmented-Generation
   ```
5. Enable **"Public Monitoring"** (free for public repos)

#### Option B: Via GitHub Marketplace
1. Visit: https://github.com/marketplace/gitguardian
2. Click **"Set up a plan"**
3. Choose **Free Plan** for public repositories
4. Grant GitGuardian access to your repository

### 3. **GitGuardian Will Now Monitor:**
- ✅ All new commits for secrets
- ✅ Pull requests before merging
- ✅ Historical scans (one-time)

---

## 🛡️ What GitGuardian Does

### Real-Time Scanning
- Detects 350+ types of secrets (API keys, tokens, passwords)
- Alerts you immediately via email if secrets are found
- Blocks commits in CI/CD pipelines (optional)

### Incident Management
When a secret is detected:
1. You receive an **email alert**
2. See the incident in GitGuardian Dashboard
3. Recommended actions:
   - **Revoke** the exposed credential immediately
   - **Rotate** with a new key
   - **Fix** the code to use environment variables

---

## 🔄 Remediation Checklist (For This Incident)

### ✅ Completed Steps:
- [x] Removed hardcoded API key from code
- [x] Added `.env.example` template
- [x] Updated `.gitignore` to exclude `.env` files
- [x] Force-pushed to overwrite GitHub history
- [x] Added security documentation

### ⚠️ URGENT: Must Do Immediately:
- [ ] **Revoke the exposed API key** at https://platform.deepseek.com/api_keys
      - Key to revoke: `sk-579409f87c4f44d0b3cd5b2d7e527618`
- [ ] **Generate a new API key** from DeepSeek
- [ ] **Add new key to .env file** (never commit this!)

### 🔧 Setup for Future Use:
```bash
# Create your .env file
cp .env.example .env

# Edit it with your NEW API key
nano .env

# Verify .env is ignored by git
git status  # Should NOT show .env

# Run the program (will now load from environment)
python graphrag_mvp.py
```

---

## 🚀 GitGuardian CLI (Optional Advanced Setup)

### Install ggshield (GitGuardian CLI):
```bash
pip install ggshield
```

### Authenticate:
```bash
ggshield auth login
```

### Scan Before Committing:
```bash
# Scan specific files
ggshield secret scan path graphrag_mvp.py

# Scan entire repo
ggshield secret scan repo .

# Pre-commit hook (prevents commits with secrets)
ggshield install -m local
```

### Add Pre-Commit Hook:
```bash
# Install pre-commit framework
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/gitguardian/ggshield
    rev: v1.14.5
    hooks:
      - id: ggshield
        language_version: python3
        stages: [commit]
EOF

# Install the hook
pre-commit install
```

Now every commit will be automatically scanned!

---

## 📊 GitGuardian Dashboard Features

Access at: https://dashboard.gitguardian.com/

### Key Features:
1. **Incidents Tab**: View all detected secrets
2. **Repositories Tab**: Manage monitored repos
3. **Integrations**: Connect Slack, Jira, etc. for alerts
4. **Policies**: Customize what gets detected

---

## 🔍 Verify Your Protection

### Check if .env is properly ignored:
```bash
echo "DEEPSEEK_API_KEY=test-key-12345" > .env
git status
# Should show: nothing to commit (working tree clean)
```

### Test GitGuardian detection (DO NOT commit this!):
```bash
# This will trigger GitGuardian if you try to commit
echo "password = 'sk-123456789abcdef'" > test_secret.py
git add test_secret.py
ggshield secret scan path test_secret.py
# Should detect the fake API key pattern
rm test_secret.py
```

---

## 📚 Best Practices Going Forward

### ✅ DO:
- Use environment variables for ALL secrets
- Add `.env` to `.gitignore` before first commit
- Use `.env.example` templates (with placeholder values)
- Enable GitGuardian monitoring on all repos
- Rotate keys immediately if exposed

### ❌ DON'T:
- Hardcode API keys, passwords, tokens in source code
- Commit `.env` files
- Share secrets via chat, email, screenshots
- Ignore GitGuardian alerts

---

## 🆘 Emergency Response Plan

If you accidentally commit a secret:

1. **IMMEDIATELY**:
   ```bash
   # Don't push if you haven't yet!
   git reset HEAD~1
   ```

2. **If already pushed**:
   - Revoke the credential ASAP (https://platform.deepseek.com/api_keys)
   - Use `git filter-branch` or BFG Repo-Cleaner to remove from history
   - Force push: `git push --force origin main`
   - Notify your team if applicable

3. **Contact GitGuardian Support**:
   - Email: support@gitguardian.com
   - They can help with incident response

---

## 🔗 Useful Links

- GitGuardian Dashboard: https://dashboard.gitguardian.com/
- Documentation: https://docs.gitguardian.com/
- GitHub Integration: https://github.com/marketplace/gitguardian
- DeepSeek API Keys: https://platform.deepseek.com/api_keys

---

*Last Updated: January 2, 2026*
*Status: Repository secured ✅*
