cat > README.md << 'ENDOFFILE'
# ATLAS - Automated Financial Intelligence System

An AI-powered daily financial analyst that aggregates news from verified sources, applies geopolitical risk scoring, cross-currency FX analysis, and sector rotation tracking to generate actionable market recommendations delivered by email every weekday at 7:45am.

## What It Does

- Scrapes headlines daily from Reuters, AP, BBC, FT, and Al Jazeera
- Sends headlines to Claude AI with a sophisticated analyst prompt
- Generates 3-5 buy/sell/hold recommendations every weekday morning
- Each recommendation includes:
  - Geopolitical Risk Score (1-10)
  - Expense Ratio
  - Risk Rating (1-10)
  - Vanguard ETF equivalent
  - Cross-Currency FX Impact analysis
  - Contrarian challenge
  - Sector rotation flag
- Tracks past recommendations in a memory log to improve accuracy over time
- Delivers formatted HTML report to email at 7:45am Mon-Fri
- Sunday weekly accuracy review email

## Tech Stack

- Python 3.11
- Anthropic Claude API (claude-opus-4-5)
- feedparser (RSS aggregation)
- smtplib (email delivery)
- schedule (task automation)
- macOS launchd (always-on background service)

## Source Whitelist

Reuters, Associated Press, Financial Times, The Economist, BBC News, El Pais, Al Jazeera. All other sources are discarded to maintain journalistic integrity.

## Setup

1. Clone this repository
2. Install dependencies: pip install anthropic feedparser schedule beautifulsoup4
3. Create config.py with your API keys (see config.example.py)
4. Run: python atlas.py

## Author

Built as a personal finance and AI engineering project to learn Python, API integration, and automated systems.
ENDOFFILE
