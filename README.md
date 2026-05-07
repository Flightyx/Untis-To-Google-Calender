# Untis-To-Google-Calender

A simple python script that transfers Untis agenda to Google Calender. Because im lazy i am only going to provide a guide for arch Linux ( I use Arch btw. ). If you have any questions ask claude.

# Features
- **Personalized Sync:** Fetches your individual schedule, including specific student-only events.
- **Google OAuth2 Integration:** Securely authenticates via the official Google login prompt.
- **Smart Data Extraction:** Maps subject names, rooms, and times directly to calendar fields.

# Setup

  1. Setup enviorement
     - Make a Directory in which the script is going to run:
       mkdir Untis-To-Calender
     - Install all necesary packages:
       sudo pacman -S python3 python-pip
     - Install venv and all pip packages
       python -m venv venv
       source venv/bin/activate
       pip install webuntis python-dotenv google-auth-oauthlib google-api-python-client

  2. Get Code
     - Download the main.py from this repository and move it to your working directory ( Untis-To-Calender )
    
  3. Get Google API Key ( hardest part, you may want to ask AI for this one )
     - Go to the [Google Cloud Console](https://console.cloud.google.com/).
     - **Create a New Project** (e.g., "Untis-Sync").
     - In the search bar, type **"Google Calendar API"** and click **Enable**.
     - Go to the **"OAuth consent screen"** tab:
       Choose **User Type: External**.
       Fill in the App name (e.g., "My Untis App") and your email.
       Click through to the end and **add your own email** as a "Test User" (Required!).
     - Go to the **"Credentials"** tab:
       Click **Create Credentials** -> **OAuth client ID**.
       Select **Application type: Desktop App**.
       Click **Create** and then **Download JSON**.
     - Rename the downloaded file to `credentials.json` and move it into your project folder.

# Usage

You can transfer your current Week to Google Calender by going in the working directory and typing in 'python3 main.py'. Then you need to authenticate with your Google Account once and your done. If you want to change your Google Account just delete the token.json form the working directory and rerun the script.

(https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
pip install -r requirements.txt
