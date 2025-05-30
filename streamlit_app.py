import sys
import os
import streamlit as st

# Debug information
st.write("Current Working Directory:", os.getcwd())
st.write("Python Path:", sys.path)
st.write("Contents of src directory:", os.listdir("src") if os.path.exists("src") else "src directory not found")

try:
    from amazon_bulk_generator.web.app import BulkCampaignApp
    st.write("Successfully imported BulkCampaignApp")
except ImportError as e:
    st.error(f"Import Error: {str(e)}")
    st.write("Detailed error information:", sys.exc_info())

if __name__ == "__main__":
    app = BulkCampaignApp()
    app.run()
