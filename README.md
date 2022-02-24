# Discord-Music-Bot
Fully original code that uses the APIs from Google, Youtube and Discord to put togheter an in-call audio player bot in Discord

The process for a single video playing in this bot would be somewhat like this:

**Discord:** gets play command message → **main.py** → **youtube API:** does youtube search of message terms and fetches video url → **youtube_dl:** gets audio from url → **FFMPEG:** processes audio → **Discord Bot:** plays audio on call...

## Setting up:
For setting this up you'll require the following...

**Python Packages:**
- Python itself
- Youtube_dl
- Discord API
- Google Client Library for Python
- PyNaCl

**Also:**
- FFMPEG 

**Accounts:**
- Youtube developer key
- Discord Bot token

With that installed you set up your *youtube_developer_key* and *discord_token* on the defined sections of **config.json**

After all that you can just run main.py.

A personal recomendation would be to instead of going through all those *"pip install --..."* is to just run it on [Replit](https://replit.com/) for free, it's very hands off.
