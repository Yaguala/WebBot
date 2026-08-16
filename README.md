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

## Installation
Windows (PowerShell)
```bash
git clone https://github.com/Yaguala/WebBot.git
cd WebBot

# Force uv and ChromeDriverManager to use the local WebBot folder
$env:UV_CACHE_DIR="$PWD\.uv_cache"
$env:WDM_LOCAL="1"

uv run --with-requirements requirements.txt webbot.py
```
macOS / Linux
```bash
git clone https://github.com/Yaguala/WebBot.git
cd WebBot

# Force uv and ChromeDriverManager to use the local WebBot folder
export UV_CACHE_DIR="$(pwd)/.uv_cache"
export WDM_LOCAL=1

uv run --with-requirements requirements.txt webbot.py
```