"""
Main entry point for the Amazon Ads Bulk Campaign Generator.
Run this file to start the application.
"""

import streamlit as st
from src.amazon_bulk_generator.web.app import BulkCampaignApp

def main():
    """Main entry point for the application"""
    app = BulkCampaignApp()
    app.run()

if __name__ == "__main__":
    main()
