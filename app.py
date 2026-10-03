import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global Pulse",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS INJECTION ---
# --- CUSTOM CSS INJECTION ---
st.markdown("""
<style>
    /* Warm gradient text for the main title */
    .title-gradient {
        background: -webkit-linear-gradient(45deg, #a65d37, #d98a5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 800;
        margin-bottom: 0px;
    }
    
    /* Make metric cards pop cleanly on a light background */
    div[data-testid="metric-container"] {
        background-color: #faf6f0;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #c28b5e;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = "https://yuycxaomxztqcklbghac.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl1eWN4YW9teHp0cWNrbGJnaGFjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA0MTc4ODIsImV4cCI6MjEwNTk5Mzg4Mn0.c9aeTmkH6M6UbBuoW4r18W9zdh96fjNwnxkmMYxvn2Y"


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# --- DATA FETCHING ---
def fetch_news():
    try:
        response = supabase.table('global_pulse') \
            .select('*') \
            .order('created_at', desc=True) \
            .limit(50) \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return []

# --- HTML BADGE HELPER ---
def get_html_badges(category, sentiment):
    s = (sentiment or "").lower()
    
    # Assign colors based on sentiment
    if s == "positive":
        color = "#10b981" # Emerald Green
        label = "Bullish / Growth"
    elif s == "negative":
        color = "#ef4444" # Red
        label = "Crisis / Severe"
    else:
        color = "#8b5cf6" # Purple
        label = "Neutral / Factual"
        
    return f"""
    <div style="display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap;">
        <span style="background-color: rgba(255, 255, 255, 0.1); color: #e2e8f0; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">
            📁 {category.title()}
        </span>
        <span style="background-color: {color}22; color: {color}; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; border: 1px solid {color}44;">
            ● {label}
        </span>
    </div>
    """

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌐 Global Pulse</h2>", unsafe_allow_html=True)
    
    st.divider()

    st.subheader("Filters & Search")
    search_query = st.text_input("🔍 Search headlines...", placeholder="e.g. AI, quantum, treaty")
    
    sentiment_filter = st.multiselect(
        "Filter by Sentiment:",
        options=["positive", "negative", "neutral"],
        default=["positive", "negative", "neutral"],
        format_func=lambda x: x.capitalize()
    )

    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.caption("🤖 **Models in Pipeline:**")
    st.caption("• `BART-large-MNLI` (Relevance Filter)")
    st.caption("• `FinBERT` (Domain Impact)")

# --- MAIN CONTENT ---
news_data = fetch_news()

if not news_data:
    st.info("No articles found in the database. Run `python main.py` to ingest today's intelligence.")
    st.stop()

# Apply Sidebar Filters
filtered_data = [
    item for item in news_data
    if (item.get('sentiment', 'neutral').lower() in sentiment_filter)
    and (search_query.lower() in item.get('title', '').lower() or search_query.lower() in (item.get('summary') or '').lower())
]

# --- TOP KPI METRICS BAR ---
st.markdown('<p class="title-gradient">Global Pulse</p>', unsafe_allow_html=True)
st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y')} | Live Intelligence Feed")

total_articles = len(news_data)
pos_count = sum(1 for i in news_data if i.get('sentiment', '').lower() == 'positive')
neg_count = sum(1 for i in news_data if i.get('sentiment', '').lower() == 'negative')
neu_count = sum(1 for i in news_data if i.get('sentiment', '').lower() == 'neutral')

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total Tracked", total_articles)
with col_m2:
    st.metric("Growth / Bullish", f"{pos_count}", delta=f"{(pos_count/total_articles*100):.0f}%" if total_articles else "0%")
with col_m3:
    st.metric("Risk / Downside", f"{neg_count}", delta=f"-{(neg_count/total_articles*100):.0f}%" if total_articles else "0%", delta_color="inverse")
with col_m4:
    st.metric("Neutral / Factual", f"{neu_count}")

st.write("\n")

# --- CATEGORY TABS ---
tab_all, tab_science, tab_econ, tab_conflict = st.tabs([
    "All Intelligence", 
    "🔬 Science & Tech", 
    "📈 Macroeconomics", 
    "🌍 Geopolitics & Crisis"
])

def render_feed(articles):
    if not articles:
        st.warning("No stories match your current filter settings.")
        return

    for item in articles:
        with st.container(border=True):
            col_img, col_content = st.columns([1, 4], gap="large")
            
            with col_img:
                img_url = item.get('image_url')
                if img_url:
                    st.image(img_url, use_container_width=True)
                else:
                    st.markdown("<div style='height: 100px; display: flex; align-items: center; justify-content: center; background-color: rgba(255,255,255,0.05); border-radius: 8px;'><span style='color: #64748b;'>No Image</span></div>", unsafe_allow_html=True)
            
            with col_content:
                st.subheader(item.get('title'))
                st.markdown(get_html_badges(item.get('category', 'General'), item.get('sentiment', 'neutral')), unsafe_allow_html=True)
                st.write(item.get('summary') or "Summary not available.")
                
                if item.get('url'):
                    st.link_button("Read Source ↗", item.get('url'))

with tab_all:
    render_feed(filtered_data)

with tab_science:
    science_items = [i for i in filtered_data if "science" in i.get('category', '').lower()]
    render_feed(science_items)

with tab_econ:
    econ_items = [i for i in filtered_data if "macroeconomics" in i.get('category', '').lower()]
    render_feed(econ_items)

with tab_conflict:
    conflict_items = [i for i in filtered_data if "conflict" in i.get('category', '').lower()]
    render_feed(conflict_items)
