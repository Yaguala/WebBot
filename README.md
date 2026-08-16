# Travian Automation Bot

## Overview
This project is a Python-based automation bot designed to optimize repetitive actions in the Travian browser game.

The bot automates key gameplay tasks such as logging in, identifying inactive players, and managing attacks, improving efficiency and reducing manual work.

---

## Features

- Automated Login  
  Performs a simple login to access the user account and maintain an active session.

- Inactive Players Scraping  
  Uses BeautifulSoup to scrape external sources and identify inactive players and villages.

- Target Management  
  Processes scraped data to select relevant targets.

- Farm List Integration  
  Adds villages directly to the in-game farm list by filling coordinates automatically.

- Attack Automation  
  Fills attack forms (coordinates, attack type, troop quantity) using Selenium.

---

## Tech Stack

- Python  
- Selenium  
- BeautifulSoup  
- Chrome WebDriver  

---

## How It Works

1. The bot logs into the Travian account.  
2. It scrapes data to identify inactive players.  
3. Extracted villages are processed as potential targets.  
4. The bot can:
   - Add them to the farm list  
   - Or launch attacks automatically  

---

## Disclaimer

This project is for educational purposes only.  
Automation tools may violate the terms of service of online games like Travian. Use at your own risk.

---

## Installation/Uninstall
WebBot keeps everything isolated inside the project folder:
  Python & Libraries are stored in WebBot/.uv_cache/
  Chrome Drivers are stored in WebBot/.wdm/
  Deleting the WebBot folder wipes everything clean with zero system clutter.

Windows (PowerShell)
```bash
# Install uv and load PATH
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex";
$env:Path = "$env:USERPROFILE\.local\bin;" + $env:Path

git clone https://github.com/Yaguala/WebBot.git
cd WebBot

# Force uv and ChromeDriverManager to use the local WebBot folder
$env:UV_CACHE_DIR="$PWD\.uv_cache"
$env:WDM_LOCAL="1"

uv run --with-requirements requirements.txt webbot.py
```
macOS / Linux
```bash
# Install uv and load PATH
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

git clone https://github.com/Yaguala/WebBot.git
cd WebBot

# Force uv and ChromeDriverManager to use the local WebBot folder
export UV_CACHE_DIR="$(pwd)/.uv_cache"
export WDM_LOCAL=1

uv run --with-requirements requirements.txt webbot.py
```