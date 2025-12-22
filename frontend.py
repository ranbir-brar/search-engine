import streamlit as st
import requests
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "http://search-api:8000"

st.set_page_config(
    page_title="Neural Search",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS: DARK GLASSMORPHISM THEME ---
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    /* Global Styles */
    .stApp {
        background-color: #0E1117;
        background-image: radial-gradient(circle at 50% 0%, #1c2331 0%, #0E1117 70%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        margin-bottom: 3rem;
        box-shadow: 0 0 80px rgba(100, 100, 255, 0.05);
    }
    
    .hero-title {
        font-size: 4rem;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #8b9bb4;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Search Input */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4facfe;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.2);
        background-color: rgba(255, 255, 255, 0.08);
    }
    
    /* Result Cards */
    .result-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        border-color: rgba(79, 172, 254, 0.4);
        background: rgba(255, 255, 255, 0.05);
    }
    
    .card-header {
        display: flex;
        justify_content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .score-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 100px;
        background: rgba(79, 172, 254, 0.1);
        color: #4facfe;
        border: 1px solid rgba(79, 172, 254, 0.2);
    }
    
    .category-tag {
        font-size: 0.8rem;
        color: #8b9bb4;
        background: rgba(255, 255, 255, 0.05);
        padding: 4px 12px;
        border-radius: 100px;
    }
    
    .result-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-decoration: none;
    }
    
    .result-content {
        color: #a0aec0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Sidebar Stats */
    .stat-box {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stat-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        color: #ffffff;
        font-weight: 700;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #8b9bb4;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border: none;
        color: #000;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        transition: opacity 0.3s;
    }
    .stButton > button:hover {
        opacity: 0.9;
        color: #000;
        border: none;
    }
    
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'total_searches' not in st.session_state:
    st.session_state.total_searches = 0

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📡 System Telemetry")
    
    # Live Stats
    try:
        response = requests.get(f"{API_URL}/stats", timeout=2)
        if response.status_code == 200:
            data = response.json()
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-num">{data.get("points_count", 0):,}</div>
                <div class="stat-label">Vector Index Size</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-num">{st.session_state.total_searches}</div>
                <div class="stat-label">Session Queries</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Backend Offline")
    except:
        st.error("Connection Failed")
    
    st.markdown("---")
    st.markdown("### ⚡ Filters")
    
    # Dynamic Categories
    categories = ["All Sources"]
    try:
        cat_resp = requests.get(f"{API_URL}/categories", timeout=2)
        if cat_resp.status_code == 200:
            categories += cat_resp.json().get("categories", [])
    except:
        pass
        
    selected_category = st.selectbox("Source Category", categories)
    limit = st.slider("Result Limit", 5, 50, 10)

# --- MAIN CONTENT ---

# Hero
st.markdown("""
<div class="hero-container">
    <div class="hero-title">NEURAL SEARCH</div>
    <div class="hero-subtitle">Real-time semantic vector retrieval powered by Spark, Kafka & Qdrant</div>
</div>
""", unsafe_allow_html=True)

# Search Bar
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    query = st.text_input("Search Query", placeholder="Describe what you are looking for...", label_visibility="collapsed")
    
    # Quick Search Chips
    suggestions = ["Artificial Intelligence", "Crypto Market", "Space Exploration", "Electric Vehicles"]
    cols = st.columns(len(suggestions))
    for i, sugg in enumerate(suggestions):
        with cols[i]:
            if st.button(sugg, key=f"btn_{i}", use_container_width=True):
                query = sugg 

# Search Logic
if query:
    if query not in st.session_state.search_history:
        st.session_state.search_history.append(query)
        st.session_state.total_searches += 1
    
    start_ts = time.time()
    
    # Prepare API payload
    payload = {"query": query, "limit": limit}
    if selected_category != "All Sources":
        payload["category"] = selected_category
        
    try:
        with st.spinner("Computing vector embeddings..."):
            response = requests.post(f"{API_URL}/search", json=payload)
            results = response.json()
            duration = time.time() - start_ts
            
        # Results Header
        st.markdown(f"##### Found {len(results)} results in {duration:.3f}s")
        st.markdown("---")
        
        if not results:
            st.warning("No relevant articles found.")
        
        # Results Grid
        for item in results:
            score = item['score'] * 100
            
            # Dynamic color based on score
            score_color = "#4facfe" if score > 70 else "#f093fb"
            
            st.markdown(f"""
            <div class="result-card">
                <div class="card-header">
                    <span class="category-tag">{item['category']}</span>
                    <span class="score-badge" style="color: {score_color}; border-color: {score_color}30; background: {score_color}10">
                        {score:.1f}% MATCH
                    </span>
                </div>
                <div class="result-title">{item['title']}</div>
                <div class="result-content">{item['content'][:280]}...</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Visualization Section
        if len(results) > 0:
            st.markdown("### 📊 Search Analytics")
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Relevance Bar Chart
                fig_bar = px.bar(
                    x=[r['title'][:20] + "..." for r in results],
                    y=[r['score'] for r in results],
                    labels={'x': 'Article', 'y': 'Relevance'},
                    title="Relevance Distribution",
                    template="plotly_dark",
                    color=[r['score'] for r in results],
                    color_continuous_scale="Bluered"
                )
                fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col_chart2:
                 # Category Pie Chart (if multiple categories)
                cats = [r['category'] for r in results]
                if len(set(cats)) > 1:
                    fig_pie = px.pie(
                        names=cats, 
                        title="Source Distribution",
                        template="plotly_dark",
                        hole=0.4
                    )
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_pie, use_container_width=True)

    except Exception as e:
        st.error(f"Search failed: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #8b9bb4; font-size: 0.8rem;">
    Running on Docker Container Network | Neural Search Engine v2.0
</div>
""", unsafe_allow_html=True)