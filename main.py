import os
import thecampy
import feedparser
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()

# 환경 변수에서 값 읽기
soldiers = os.getenv('SOLDIERS').split(',')
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

thecampy_soldiers = [thecampy.Soldier(soldier) for soldier in soldiers]
tc = thecampy.Client(email, password)


def send_to_all(title, content):
    for soldier in thecampy_soldiers:
        msg = thecampy.Message(title, content)
        tc.get_soldier(soldier)
        tc.send_message(soldier, msg)

        # Get News from Rss

def get_articles(url):
    articles = []
    feeds = feedparser.parse(url)
    for feed in feeds['entries']:
        title = feed['title']
        summary = BeautifulSoup(feed['summary'], 'html.parser').get_text()
        if summary[0] == '\n':
            summary = summary[1:]
        summary = summary.replace('\n', '<br>')
        news = {
            'title': title,
            'summary': summary
        }
        articles.append(news)
    return articles

def articlePaginate(news, max_length):
    news_texts = []
    newsContent = ""
    for item in news:
        next_content = '# ' + item['title'] + '<br>' + item['summary'] + '<br><br>'
        if len(newsContent + next_content) > max_length:
            news_texts.append(newsContent)
            newsContent = next_content
        else:
            newsContent += next_content
    news_texts.append(newsContent)  # 마지막에 남은 뉴스 텍스트 추가
    return news_texts


def sendNews(news_provider, articles):
    pages = articlePaginate(articles, 1400)
    
    for i, page in enumerate(pages):
        title = f"{news_provider} ({i+1}/{len(pages)})"
        print(title)
        print(page)
        
        send_to_all(title, page)

# get_news('https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko')
sendNews('SBS', get_articles('http://news.sbs.co.kr/news/ReplayRssFeed.do'))
sendNews('GeekNews', get_articles('https://news.hada.io/rss/news'))