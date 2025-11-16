# 🎯 ProFlow Environment Setup Checklist

**Date Started**: November 15, 2025  
**Target Completion**: Today (Days 1-2)

---

## ✅ Completed Steps

Track your progress as you go through setup:

### Google Cloud Setup
- [ ] Created Google Cloud account / logged in
- [ ] Created project: `proflow-agent-capstone`
- [ ] Noted PROJECT_ID: `_______________________`
- [ ] Enabled Gmail API
- [ ] Enabled Calendar API
- [ ] Enabled Drive API
- [ ] Enabled Vertex AI API
- [ ] Enabled Cloud Trace API
- [ ] Enabled Cloud Logging API
- [ ] Set up billing account
- [ ] Created budget alert at $50

### Python Environment
- [ ] Verified Python 3.10+ installed: `python --version`
- [ ] Navigated to ProFlow-Agent directory
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Activated virtual environment
- [ ] Upgraded pip: `pip install --upgrade pip`
- [ ] Installed requirements: `pip install -r requirements.txt`
- [ ] Verified ADK installation

### Authentication
- [ ] Installed Google Cloud CLI
- [ ] Ran: `gcloud auth login`
- [ ] Set project: `gcloud config set project PROJECT_ID`
- [ ] Ran: `gcloud auth application-default login`
- [ ] Verified config: `gcloud config list`

### Project Structure
- [ ] Created all directories (src/, agents/, tools/, etc.)
- [ ] Created README.md
- [ ] Created requirements.txt
- [ ] Created .env.example
- [ ] Created .gitignore
- [ ] Copied .env.example to .env
- [ ] Updated .env with your PROJECT_ID

### Verification
- [ ] Ran test agent: `python test_setup.py`
- [ ] Test agent responded successfully
- [ ] No authentication errors
- [ ] Ready to build!

---

## 🔧 Your Environment Details

Fill this in as you set up:

```
PROJECT_ID: _______________________
REGION: us-central1
PYTHON_VERSION: _______________________
ADK_VERSION: _______________________
```

---

## 🚀 Next Steps

Once all checkboxes above are complete:

1. ✅ Update PROJECT_TRACKER.md - mark Days 1-2 complete
2. 🎯 Move to Week 1, Days 3-4: Build Email Intelligence Agent
3. 💪 You're ready to code!

---

## 🆘 Troubleshooting

### If test_setup.py fails:

**Authentication Error**:
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

**API Not Enabled**:
```bash
gcloud services enable aiplatform.googleapis.com
```

**Module Not Found**:
```bash
pip install --upgrade google-adk
```

**Permission Denied**:
- Check billing is enabled
- Verify you have Editor/Owner role on project

---

## 📝 Notes

Write any issues or observations here:

```
[Your notes]
```

---

**Status**: ⏳ In Progress  
**When Complete**: Mark this in PROJECT_TRACKER.md!
