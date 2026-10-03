import requests
import time
from transformers import pipeline
from supabase import create_client, Client

# --- CREDENTIALS ---
GNEWS_API_KEY = "19a1abe3af1dcbb1477c9585d4a70c27"
SUPABASE_URL = "https://yuycxaomxztqcklbghac.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl1eWN4YW9teHp0cWNrbGJnaGFjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA0MTc4ODIsImV4cCI6MjEwNTk5Mzg4Mn0.c9aeTmkH6M6UbBuoW4r18W9zdh96fjNwnxkmMYxvn2Y"

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_news_pipeline():
    print("1. Fetching news across multiple categories...")
    
    # We will query these 4 specific categories to get 40 articles total
    gnews_categories = ['world', 'business', 'technology', 'science']
    all_raw_articles = []
    
    for cat in gnews_categories:
        print(f"   Fetching '{cat}' news...")
        url = f"https://gnews.io/api/v4/top-headlines?category={cat}&lang=en&max=10&apikey={GNEWS_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            all_raw_articles.extend(articles)
        else:
            print(f"   Failed to fetch '{cat}'.")
            
        # Pause for 1 second between requests to avoid overwhelming the free API
        time.sleep(1) 
        
    print(f"\nTotal raw articles fetched: {len(all_raw_articles)}")
    
    print("\n2. Loading Deep Learning Models...")
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    
    categories = [
        "scientific breakthrough or technology", 
        "global macroeconomics", 
        "major geopolitical conflict",
        "petty local politics", 
        "entertainment and gossip"
    ]
    
    print("\n3. Processing and Saving to Database...\n")
    saved_count = 0
    
    for article in all_raw_articles:
        headline = article.get('title', '')
        summary = article.get('description', '') or headline
        
        # Filter Noise
        filter_res = classifier(headline, categories)
        top_cat = filter_res['labels'][0]
        
        if top_cat in ["petty local politics", "entertainment and gossip"]:
            continue
            
        # Sentiment Analysis
        sentiment_res = sentiment_analyzer(summary[:512])[0]
        
        # Save to Supabase (using upsert to prevent duplicates)
        try:
            supabase.table('global_pulse').upsert({
                "title": headline,
                "summary": summary,
                "url": article.get('url'),
                "image_url": article.get('image'),
                "category": top_cat,
                "sentiment": sentiment_res['label']
            }, on_conflict="url").execute()
            
            print(f"✅ Saved to DB: {headline}")
            saved_count += 1
        except Exception as e:
            # It will silently skip duplicate URLs if you set up the constraint!
            pass
            
    print(f"\nPipeline finished. {saved_count} new high-value stories saved.")

if __name__ == "__main__":
    run_news_pipeline()