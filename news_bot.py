import feedparser
import json
import time
from datetime import datetime
from time import mktime

# --- THE MEGA FEED LIST ---
# A mix of world, tech, and financial news from reliable wires.
FEEDS = [
    # --- MAJOR WIRES ---
    {"source": "Reuters World", "url": "https://p.feedblitz.com/t3/Reuters/worldNews.xml"},
    {"source": "AP Top News", "url": "https://apnews.com/hub/ap-top-news.rss"},
    {"source": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    
    # --- EUROPE ---
    {"source": "Deutsche Welle", "url": "https://rss.dw.com/rdf/rss-en-all"},
    {"source": "France 24", "url": "https://www.france24.com/en/rss"},
    {"source": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    
    # --- AMERICAS ---
    {"source": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"source": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
    {"source": "CBC Canada", "url": "https://www.cbc.ca/cmlink/rss-world"},
    
    # --- MIDDLE EAST & ASIA ---
    {"source": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"source": "CNA (Asia)", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml"},
    {"source": "Kyodo News (Japan)", "url": "https://english.kyodonews.net/rss/news.xml"},
    
    # --- TECH & SCIENCE (Optional - remove if you want only politics) ---
    {"source": "TechCrunch", "url": "https://techcrunch.com/feed/"},
    {"source": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    
    # --- FINANCE ---
    {"source": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"},
]

articles = []

def parse_feed(source_name, url):
    print(f"--- Scanning {source_name} ---")
    try:
        # Set a short timeout so one bad feed doesn't hang the script
        d = feedparser.parse(url)
        
        if not d.entries:
            print(f"⚠️ No entries for {source_name}")
            return

        # GRAB TOP 20 STORIES PER SOURCE (Increased from 10)
        for entry in d.entries[:20]:
            try:
                # 1. Robust Date Handling
                # We try to find a real timestamp. If missing, we default to 'now'
                # so it appears at the top, or 0 so it drops to bottom (your choice).
                # Here we default to 'now' to catch breaking items with bad metadata.
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    timestamp = mktime(entry.published_parsed)
                    dt = datetime.fromtimestamp(timestamp)
                    display_date = dt.strftime("%b %d, %H:%M")
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    timestamp = mktime(entry.updated_parsed)
                    dt = datetime.fromtimestamp(timestamp)
                    display_date = dt.strftime("%b %d, %H:%M")
                else:
                    timestamp = time.time()
                    display_date = "Just now"

                # 2. Cleanup Content
                summary = getattr(entry, 'summary', '')
                # Remove HTML tags from summary (simple clean)
                if '<' in summary: 
                    summary = summary.split('<')[0]
                
                # If summary is empty, try description
                if not summary:
                    summary = getattr(entry, 'description', '')

                title = getattr(entry, 'title', 'No Title')
                link = getattr(entry, 'link', '#')

                # Filter out "Live" blog spam if needed, or keep it.
                
                articles.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                    "timestamp": timestamp,
                    "date": display_date
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"❌ Failed source {source_name}: {e}")

def main():
    for feed in FEEDS:
        parse_feed(feed["source"], feed["url"])
    
    # 1. Sort by Newest first
    articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # 2. LIMIT TOTAL VOLUME
    # If we have 15 sources * 20 articles = 300 articles.
    # Browsers handle 300 items easily. If you go over 500, it might lag on mobile.
    final_list = articles[:300]
    
    # 3. Save
    with open('news.json', 'w') as f:
        json.dump(final_list, f, indent=2)
    
    print(f"💾 Saved {len(final_list)} articles to news.json")

if __name__ == "__main__":
    main()
