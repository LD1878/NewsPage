import feedparser
import json
import time
from datetime import datetime
from dateutil import parser as date_parser

# CONFIG: The World's Best Wire Services
FEEDS = [
    {"source": "Reuters", "url": "https://p.feedblitz.com/t3/Reuters/worldNews.xml"},
    {"source": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"source": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"source": "AP News", "url": "https://apnews.com/hub/ap-top-news.rss"},
    {"source": "Deutsche Welle", "url": "https://rss.dw.com/rdf/rss-en-all"},
    {"source": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
]

articles = []

def parse_feed(source_name, url):
    print(f"📡 Scanning {source_name}...")
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]: # Limit to top 15 per source to keep it snappy
            
            # Normalize Date
            try:
                published = entry.published
                dt = date_parser.parse(published)
                timestamp = dt.timestamp()
                display_date = dt.strftime("%H:%M · %b %d")
            except:
                timestamp = time.time()
                display_date = "Just now"

            # Clean Summary (Remove HTML tags if any)
            summary = entry.get('summary', '')
            if '<' in summary:
                # Basic strip (or just take the title if summary is messy)
                summary = summary.split('<')[0]

            articles.append({
                "source": source_name,
                "title": entry.title,
                "link": entry.link,
                "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                "timestamp": timestamp,
                "date": display_date
            })
    except Exception as e:
        print(f"⚠️ Failed to parse {source_name}: {e}")

def main():
    for feed in FEEDS:
        parse_feed(feed["source"], feed["url"])
    
    # Sort by Newest first
    articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Save to JSON
    with open('news.json', 'w') as f:
        json.dump(articles, f, indent=2)
    
    print(f"✅ Successfully aggregated {len(articles)} articles.")

if __name__ == "__main__":
    main()
