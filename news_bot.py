import feedparser
import json
import time
from datetime import datetime
from time import mktime

# ROBUST CONFIG
FEEDS = [
    {"source": "Reuters", "url": "https://p.feedblitz.com/t3/Reuters/worldNews.xml"},
    {"source": "BBC", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"source": "AP", "url": "https://apnews.com/hub/ap-top-news.rss"},
]

articles = []

def parse_feed(source_name, url):
    print(f"--- Scanning {source_name} ---")
    try:
        d = feedparser.parse(url)
        # Check if feed actually worked
        if not d.entries:
            print(f"⚠️ No entries found for {source_name}")
            return

        for entry in d.entries[:10]:
            try:
                # robust date handling
                if hasattr(entry, 'published_parsed'):
                    timestamp = mktime(entry.published_parsed)
                    dt = datetime.fromtimestamp(timestamp)
                    display_date = dt.strftime("%b %d, %H:%M")
                else:
                    timestamp = time.time()
                    display_date = "Just now"

                # cleanup summary
                summary = getattr(entry, 'summary', '')
                if '<' in summary: summary = summary.split('<')[0]
                
                # cleanup title
                title = getattr(entry, 'title', 'No Title')

                articles.append({
                    "source": source_name,
                    "title": title,
                    "link": entry.link,
                    "summary": summary[:150] + "..." if summary else "",
                    "timestamp": timestamp,
                    "date": display_date
                })
            except Exception as e:
                print(f"Skipping article: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Failed source {source_name}: {e}")

def main():
    for feed in FEEDS:
        parse_feed(feed["source"], feed["url"])
    
    # Sort by newest
    articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # ALWAYS save, even if empty (prevents 404 errors)
    with open('news.json', 'w') as f:
        json.dump(articles, f, indent=2)
    
    print(f"💾 Saved {len(articles)} articles to news.json")

if __name__ == "__main__":
    main()
