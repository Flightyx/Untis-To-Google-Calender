# Untis-To-Google-Calender

A simple python script that transfers Untis agenda to Google Calender. Because im lazy I am only going to provide a guide for Arch Linux ( I use Arch btw. ). If you have any questions ask Claude.

# Features
- **Personalized Sync:** Fetches your individual schedule, including specific student-only events.
- **Google OAuth2 Integration:** Securely authenticates via the official Google login prompt.
- **Smart Data Extraction:** Maps subject names, rooms, and times directly to calendar fields.
- **Export as .ics possible** You can, instead of exporting your WebUntis agenda to Google Calendar, export it as a .ics. This can be useful if you use another Calender than Google Calendar.

# Setup

 1. **Setup enviorement**
     - Make a directory in which the script is going to run:
       - mkdir Untis-To-Calender
     - Install all necesary packages:
       - sudo pacman -S python3 python-pip
     - Install venv and all pip packages
       - python -m venv venv
       - source venv/bin/activate
       - pip install webuntis python-dotenv google-auth-oauthlib google-api-python-client

2. **Get Code**
     - Download the main.py and the .env from this repository and move them to your working directory ( Untis-To-Calender )
     - Open the .env file. There you will see 'SERVER','USERNAME','PASSWORD', 'SCHOOL', 'TIMEZONE' and 'EXPORTAS'. You will need to fill in your credentials as following:
       - SERVER='' (when you go on the WebUntis Webpage, after you selected your school, the URL in the top bar will change. you just copy that URL without any subdirectories or https:// (this could look like this: gym-neue-os.webuntis.com))
       - USERNAME='' (Your WebUntis login Username (For Examle: Freimann.Udo))
       - PASSWORD='' (Your WebUntis login Password)
       - SCHOOL='' (Usualy this is the same as SERVER but without .webuntis.com (For example: gym-neue-os))
       - TIMEZONE='' (Your Timezone, for example Europe/Berlin)
       - EXPORTAS='Google-Calendar' (Set to either 'Google-Calendar' if you want to export to google calendar or alternatively set it to '.ics' to export it as a .ics file.
    
3. **Get Google API Key** ( hardest part, you may want to ask AI for this one )
     - Go to the [Google API Console](https://console.cloud.google.com/apis/).
     - On the Top click the Button **My First Project**, then click on **New Project**
     - Type in your Project name ( e.g. Untis-To-Calender ), then hit **create**
     - Next, click on **Enabled APIs & services** on the right, then click **Enable APIs and services** on the top
     - In the search bar, type **"Google Calendar API"** and click **Enable**.
     - Go to the **"OAuth consent screen"** tab:
       - Click **Get started**
       - Type in your **App name** ( e.g. Untis-to-Calender ) and the **User support email** ( Thiscan be the same as the Google Account you are currently using )
       - Choose **Audiance: External**.
       - Click through to the end
       - Go back to the **Audiance** tab, scroll down to Test users and click **Add users**
         - Now type in the E-Mail Adress of the Google Account you are going to be synchronising with
     - Go to the **Clients** tab:
       - Click **Create Client**
       - Select **Application type: Desktop App**.
       - Click **Create** and then **Download JSON**.
     - Rename the downloaded file to `credentials.json` and move it into your project folder.

# Usage

You can transfer your current Week to Google Calender by going in the working directory and typing in 'python3 main.py'. Then you need to authenticate with your Google Account once and your done. From there on you can you can execute the script without reauthenticating every time. If you want to change your Google Account just delete the 'token.json' form the working directory and rerun the script.
