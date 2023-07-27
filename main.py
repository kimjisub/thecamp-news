import os
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import feedparser
import pytz
import thecampy

# Load environment variables
load_dotenv()

# Initialize TheCamp client and soldiers
soldier_names = os.getenv('SOLDIERS').split(',')
thecampy_client = thecampy.Client(os.getenv('EMAIL'), os.getenv('PASSWORD'))
thecampy_soldiers = [thecampy.Soldier(name) for name in soldier_names]


def send_message_to_all(title, content):
    """Send a message to all soldiers."""
    for soldier in thecampy_soldiers:
        print(f"Sending to {soldier.name}... ", end='', flush=True)
        message = thecampy.Message(title, content)
        thecampy_client.get_soldier(soldier)
        thecampy_client.send_message(soldier, message)
        print("Sent.")
        time.sleep(1)


def fetch_articles(rss_feed_url):
    """Fetch and parse articles from an RSS feed."""
    articles = []
    feeds = feedparser.parse(rss_feed_url)
    for feed in feeds['entries']:
        title = feed['title']
        summary = BeautifulSoup(feed['summary'], 'html.parser').get_text().strip().replace('\n', '<br>')
        articles.append({
            'title': title,
            'summary': summary
        })
    return articles


def paginate_articles(articles, max_length):
    """Split articles into pages."""
    pages = []
    page_content = ""
    for article in articles:
        next_article = f"# {article['title']}<br>{article['summary']}<br><br>"
        if len(page_content + next_article) > max_length:
            pages.append(page_content)
            page_content = next_article
        else:
            page_content += next_article
    pages.append(page_content)  # Add remaining page content
    return pages


def dispatch_news(provider_name, rss_feed_url):
    """Fetch articles from an RSS feed, paginate them, and send them to all soldiers."""
    # Fetch and paginate articles
    articles = fetch_articles(rss_feed_url)
    pages = paginate_articles(articles, 1400)

    # Generate date string for current time in KST
    kst_date = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d')

    # Send all pages to all soldiers
    for i, page in enumerate(pages):
        title = f"{kst_date} {provider_name} ({i + 1}/{len(pages)})"
        print(f"Dispatching {title}")
        print(page)
        send_message_to_all(title, page)


# Dispatch news
dispatch_news('SBS', 'http://news.sbs.co.kr/news/ReplayRssFeed.do')
dispatch_news('GeekNews', 'https://news.hada.io/rss/news')
