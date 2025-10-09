"""Streamlit frontend for Daily Briefing."""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page configuration
st.set_page_config(
    page_title="Daily Briefing",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_available_categories() -> List[str]:
    """Fetch available categories from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/categories", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("categories", [])
    except requests.RequestException as e:
        st.error(f"Error fetching categories: {e}")
        return []

def generate_briefing(categories: List[str]) -> Dict[str, Any]:
    """Generate briefing for selected categories."""
    try:
        payload = {"categories": categories}
        response = requests.post(
            f"{API_BASE_URL}/briefing",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error generating briefing: {e}")
        return {}

def check_briefing_status(categories: List[str]) -> Dict[str, Any]:
    """Check the status of briefing generation."""
    try:
        categories_str = ",".join(categories)
        response = requests.get(
            f"{API_BASE_URL}/briefing/status/{categories_str}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error checking status: {e}")
        return {}

def trigger_refresh():
    """Trigger manual refresh of all categories."""
    try:
        response = requests.get(f"{API_BASE_URL}/briefing/refresh", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error triggering refresh: {e}")
        return {}

def display_article(article: Dict[str, Any]):
    """Display a single article."""
    with st.container():
        st.markdown(f"### {article['title']}")
        
        # Article metadata
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Category:** {article['category'].title()}")
        with col2:
            created_at = datetime.fromisoformat(article['created_at'].replace('Z', '+00:00'))
            st.markdown(f"**Published:** {created_at.strftime('%H:%M')}")
        
        # Article summary
        if article.get('summary'):
            st.markdown(f"**Summary:** {article['summary']}")
        elif article.get('description'):
            st.markdown(f"**Description:** {article['description']}")
        
        # Article link
        st.markdown(f"[Read full article]({article['url']})")
        
        st.divider()

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("📰 Daily Briefing")
    st.markdown("*Personalized news summaries powered by AI*")
    
    # Sidebar for category selection
    with st.sidebar:
        st.header("📋 Select Categories")
        
        # Get available categories
        available_categories = get_available_categories()
        
        if not available_categories:
            st.error("Unable to load categories. Please check if the API is running.")
            st.stop()
        
        # Category selection
        selected_categories = st.multiselect(
            "Choose up to 10 categories:",
            options=available_categories,
            default=["technology", "business"],
            max_selections=10,
            help="Select the news categories you're interested in"
        )
        
        # Generate briefing button
        generate_button = st.button(
            "📰 Generate Briefing",
            type="primary",
            disabled=len(selected_categories) == 0,
            use_container_width=True
        )
        
        # Manual refresh button
        if st.button("🔄 Refresh All News", use_container_width=True):
            with st.spinner("Triggering news refresh..."):
                result = trigger_refresh()
                if result:
                    st.success("News refresh started! Check back in a few minutes.")
        
        # Status section
        st.divider()
        st.subheader("📊 Status")
        
        if selected_categories:
            status = check_briefing_status(selected_categories)
            if status:
                st.metric("Articles Available", status.get("articles_available", 0))
                if status.get("last_updated"):
                    last_updated = datetime.fromisoformat(status["last_updated"].replace('Z', '+00:00'))
                    st.write(f"Last updated: {last_updated.strftime('%Y-%m-%d %H:%M')}")
                
                status_color = "🟢" if status.get("status") == "ready" else "🟡"
                st.write(f"Status: {status_color} {status.get('status', 'unknown').title()}")
    
    # Main content area
    if not selected_categories:
        st.info("👈 Please select at least one category from the sidebar to get started.")
        
        # Show sample categories
        st.subheader("Available Categories")
        cols = st.columns(3)
        for i, category in enumerate(available_categories):
            with cols[i % 3]:
                st.markdown(f"• **{category.title()}**")
        
        return
    
    # Generate briefing
    if generate_button:
        with st.spinner("Generating your personalized briefing..."):
            briefing_data = generate_briefing(selected_categories)
            
            if not briefing_data:
                st.error("Failed to generate briefing. Please try again.")
                return
            
            # Store briefing data in session state
            st.session_state.briefing_data = briefing_data
            st.session_state.last_generated = datetime.now()
    
    # Display briefing if available
    if hasattr(st.session_state, 'briefing_data') and st.session_state.briefing_data:
        briefing = st.session_state.briefing_data
        articles = briefing.get('articles', [])
        
        # Briefing header
        st.header(f"📰 Your Daily Briefing")
        
        # Briefing metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Categories", len(briefing.get('categories', [])))
        with col2:
            st.metric("Articles", briefing.get('total_articles', 0))
        with col3:
            if hasattr(st.session_state, 'last_generated'):
                st.write(f"Generated: {st.session_state.last_generated.strftime('%H:%M')}")
        
        if not articles:
            st.warning(
                "No articles available yet. Articles are being processed in the background. "
                "Please try again in a few minutes or click 'Generate Briefing' again."
            )
            return
        
        # Group articles by category
        articles_by_category = {}
        for article in articles:
            category = article['category']
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)
        
        # Display articles by category
        for category, category_articles in articles_by_category.items():
            st.subheader(f"📂 {category.title()}")
            
            for article in category_articles:
                display_article(article)
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            Daily Briefing • Powered by ChatGPT-4o-mini • Built with FastAPI & Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
