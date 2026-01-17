# 📧 Gmail Watcher Setup & Commands

This script monitors your Gmail inbox for important or starred emails and automatically creates tasks in your Obsidian Vault.

## 🚀 Quick Start Commands

If you have already set up your credentials, use this command to start the script:

```powershell
# Run the Gmail Watcher
.\.venv\Scripts\python.exe gmail_watcher.py
```

---

## 🛠️ Setup Instructions

### 1. Install Dependencies
If you are running this for the first time or on a new machine, install the required libraries:

```powershell
# Install all required Google API libraries and Watchdog
.\.venv\Scripts\python.exe -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 watchdog
```

### 2. Google Cloud Setup (One-time)
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable the **Gmail API**.
3.  Create **OAuth 2.0 Credentials** (Web application).
4.  Add `http://localhost:8080/` to the **Authorized redirect URIs**.
5.  Download the JSON and save it as `gmail_credentials.json` in this folder.

### 3. First-Time Authentication
The first time you run the script, it will provide a link in the terminal.
1.  Copy the link and paste it into your browser.
2.  Log in with your Gmail account.
3.  Click **Allow**.
4.  A `gmail_token.json` file will be created automatically, so you won't need to log in again.

---

## 📂 Troubleshooting

### Error: `redirect_uri_mismatch`
- Ensure you added `http://localhost:8080/` (including the trailing slash) to your Google Cloud Console redirect URIs.

### Error: `MismatchingStateError`
- This usually happens if you use an old link. Close the script (Ctrl+C) and run it again to get a fresh link.

### Unicode/Emoji Errors
If you see weird characters or errors in the terminal, run the script with this environment variable:
```powershell
$env:PYTHONUTF8=1; .\.venv\Scripts\python.exe gmail_watcher.py
```

---

## 🎯 Output Locations
- **Tasks**: `e:\obsidian\AI_Employee_Vault\Needs_Action\`
- **Logs**: `e:\obsidian\AI_Employee_Vault\Logs\`
