import anthropic
import feedparser
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import ANTHROPIC_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, SEND_TO_EMAIL, SEND_AT_TIME

RSS_FEEDS = {
    "Reuters":        "https://feeds.reuters.com/reuters/businessNews",
    "Reuters Top":    "https://feeds.reuters.com/reuters/topNews",
    "BBC News":       "http://feeds.bbci.co.uk/news/business/rss.xml",
    "BBC World":      "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera":     "https://www.aljazeera.com/xml/rss/all.xml",
    "FT":             "https://www.ft.com/?format=rss",
}

SYSTEM_PROMPT = """You are ATLAS - an elite financial analyst combining deep expertise in global macroeconomics, geopolitical risk, market history, and emerging technology. You think like a geo-strategist, historian, and quant trader rolled into one.

SOURCES: You ONLY accept and cite from Reuters, Associated Press (AP), Financial Times (FT), The Economist, BBC News, El Pais, Al Jazeera. Discard anything else.

FOR EACH RECOMMENDATION use this exact format:
---
TICKER: [symbol]
ACTION: BUY / SELL / HOLD
CONVICTION: High / Medium / Low
GEOPOLITICAL RISK SCORE: [1-10]
GEO RISK FACTORS: [brief explanation]
EXPENSE RATIO: [ETF expense ratio as a percentage e.g. 0.10% for VDE. For individual stocks type N/A.]
RISK RATING: [rate overall risk 1-10, where 1=very low risk e.g. treasury bond, 10=very high risk e.g. leveraged ETF. Factor in volatility, liquidity, sector concentration, and geopolitical exposure. Explain in one sentence.]
VANGUARD PLAY: [most relevant Vanguard ETF equivalent e.g. VDE for energy, VPU for utilities, VXUS for international, BND for bonds. If no Vanguard equivalent exists, say so clearly.]
THESIS: [2-3 sentences]
CONTRARIAN CHALLENGE: [1 sentence against this call]
SECTOR ROTATION FLAG: [Yes/No - if yes, explain]
TIME HORIZON: Short / Medium / Long
---

MEMORY: Review the memory log provided. Acknowledge what past calls were right or wrong. Adjust confidence accordingly.

TONE: Direct, sharp, no filler. Bloomberg meets Foreign Affairs."""


def fetch_headlines():
    headlines = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                headlines.append(f"[{source}] {entry.title}")
        except Exception as e:
            headlines.append(f"[{source}] Feed unavailable today")
    return "\n".join(headlines)


def load_memory():
    try:
        with open("memory_log.txt", "r") as f:
            return f.read()
    except:
        return "No prior memory found. This is session one."


def save_memory(new_entry):
    with open("memory_log.txt", "a") as f:
        f.write(f"\n\n--- {datetime.now().strftime('%Y-%m-%d')} ---\n")
        f.write(new_entry)


def run_atlas():
    print(f"[{datetime.now()}] ATLAS running...")
    headlines = fetch_headlines()
    memory = load_memory()
    today = datetime.now().strftime("%A, %B %d, %Y")

    user_prompt = f"""Today is {today}.

Here are today's headlines from approved sources:
{headlines}

Memory log from past sessions:
{memory}

Run your full analysis. Give me today's top 3-5 buy/sell/hold recommendations with full scoring.
Then add a brief MARKET PULSE section: what is the dominant macro theme today, and is there any sector rotation signal?

PORTFOLIO TASK: I am adding $100 this month to a Vanguard account. Based on today's analysis and the current portfolio in the memory log, tell me exactly how to allocate this $100 across your recommended positions. Be specific - e.g. $60 into VDE, $40 into BND. Factor in what I already hold."""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )

    analysis = message.content[0].text
    save_memory(analysis[:800])
    send_email(analysis, today)
    print(f"[{datetime.now()}] ATLAS complete. Email sent.")


def run_weekly_review():
    memory = load_memory()
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"""Review this week's ATLAS recommendations from the memory log below.

For each call made this week:
1. Was the thesis directionally correct based on how events developed?
2. What did you miss?
3. What would you do differently?
4. Update your confidence calibration for next week.

Be brutally honest. This is how you improve.

Memory log:
{memory}"""}]
    )
    send_email(message.content[0].text, "Weekly Accuracy Review - " + datetime.now().strftime("%B %d, %Y"))


def send_email(analysis, date_str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"ATLAS Daily Brief - {date_str}"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = SEND_TO_EMAIL

    text_body = f"ATLAS DAILY BRIEF\n{date_str}\n\n{analysis}"
    html_analysis = analysis.replace("\n", "<br>").replace("---", "<hr>")
    html_body = f"""
    <html><body style="font-family: Georgia, serif; max-width: 700px; margin: auto; padding: 20px;">
    <h1 style="color: #1a1a2e; border-bottom: 2px solid #e74c3c; padding-bottom: 10px;">
    ATLAS Daily Brief</h1>
    <p style="color: #666; font-size: 14px;">{date_str}</p>
    <div style="line-height: 1.8; font-size: 15px;">{html_analysis}</div>
    <hr><p style="color: #999; font-size: 12px;">ATLAS Financial Intelligence System -
    Sources: Reuters, AP, FT, The Economist, BBC, El Pais, Al Jazeera only.
    Not financial advice. Do your own research.</p>
    </body></html>"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, SEND_TO_EMAIL, msg.as_string())


if __name__ == "__main__":
    print(f"ATLAS scheduler started. Will run daily at {SEND_AT_TIME}.")
    print("Press Ctrl+C to stop.\n")

    run_atlas()

    schedule.every().day.at(SEND_AT_TIME).do(run_atlas)
    schedule.every().sunday.at("08:00").do(run_weekly_review)

    while True:
        schedule.run_pending()
        time.sleep(60)
