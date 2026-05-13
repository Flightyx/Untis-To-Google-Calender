# Untis-To-Google-Calendar

A simple Python script that transfers your Untis agenda to Google Calendar. Because I'm lazy, I am only going to provide a guide for Arch Linux (I use Arch btw.). If you have any questions, ask Claude.

# Features
- **Personalized Sync:** Fetches your individual schedule, including specific student-only events.
- **Google OAuth2 Integration:** Securely authenticates via the official Google login prompt.
- **Smart Data Extraction:** Maps subject names, rooms, and times directly to calendar fields.
- **Export as .ics possible:** Instead of exporting your WebUntis agenda to Google Calendar, you can export it as an .ics file. This is useful if you use a calendar provider other than Google.

# Setup

1. **Setup environment**
     - Create a directory in which the script is going to run:
       - `mkdir Untis-To-Calendar`
     - Install all necessary packages:
       - `sudo pacman -S python3 python-pip`
     - Install venv and all pip packages:
       - `python -m venv venv`
       - `source venv/bin/activate`
       - `pip install webuntis python-dotenv google-auth-oauthlib google-api-python-client`

2. **Get Code**
     - Download and unpack the .zip found in the newest release and move all the included files to your working directory (`Untis-To-Calendar`).
     - Open the `.env` file. You will see `SERVER`, `USERNAME`, `PASSWORD`, `SCHOOL`, `TIMEZONE`, and `EXPORTAS`. Fill in your credentials as follows:
       - **SERVER=''** (When you visit the WebUntis webpage and select your school, the URL in the address bar will change. Copy that URL without any subdirectories or `https://`. Example: `gym-neue-os.webuntis.com`)
       - **USERNAME=''** (Your WebUntis username. Example: `Freimann.Udo`)
       - **PASSWORD=''** (Your WebUntis password)
       - **SCHOOL=''** (Usually the same as SERVER but without `.webuntis.com`. Example: `gym-neue-os`)
       - **TIMEZONE=''** (Your timezone, e.g., `Europe/Berlin`)
       - **EXPORTAS='Google-Calendar'** (Set to either `'Google-Calendar'` or `'.ics'`)

3. **Get Google API Key** (The hardest part; you may want to ask an AI for help here)
     - Go to the [Google API Console](https://console.cloud.google.com/apis/).
     - At the top, click **My First Project**, then click **New Project**.
     - Type in your project name (e.g., `Untis-To-Calendar`), then hit **Create**.
     - Next, click on **Enabled APIs & services** on the left, then click **Enable APIs and services** at the top.
     - In the search bar, type **"Google Calendar API"** and click **Enable**.
     - Go to the **"OAuth consent screen"** tab:
       - Click **Get started**.
       - Enter your **App name** (e.g., `Untis-to-Calendar`) and the **User support email** (this can be the same as your Google account).
       - Choose **Audience: External**.
       - Click through to the end.
       - Go back to the **Audience** (or "Test users") tab, scroll down to **Test users**, and click **Add users**.
       - Enter the email address of the Google account you want to sync with.
     - Go to the **Credentials** tab:
       - Click **Create Credentials** -> **OAuth client ID**.
       - Select **Application type: Desktop App**.
       - Click **Create** and then **Download JSON**.
     - Rename the downloaded file to `credentials.json` and move it into your project folder.

# Usage

You can transfer your current week to Google Calendar by navigating to the working directory and typing `python3 main.py`. You will need to authenticate with your Google account once, and you're done. From then on, you can execute the script without re-authenticating. If you want to change your Google account, simply delete the `token.json` file from the working directory and rerun the script.
