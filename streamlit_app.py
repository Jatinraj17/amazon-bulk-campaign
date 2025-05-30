import streamlit as st

# Set page config FIRST before any other Streamlit commands
st.set_page_config(
    page_title="Amazon Ads Bulk Campaign Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from amazon_bulk_generator.web.app import BulkCampaignApp

if __name__ == "__main__":
    app = BulkCampaignApp()
    app.run()
