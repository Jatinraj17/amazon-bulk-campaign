import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import os
from typing import Dict, Any, Tuple, List
import re
import json

from amazon_bulk_generator.core.generator import BulkSheetGenerator, CampaignSettings
from amazon_bulk_generator.core.validators import (
    validate_keywords,
    validate_skus,
    validate_campaign_settings,
    validate_name_template
)
from amazon_bulk_generator.utils.file_handlers import FileHandler
from amazon_bulk_generator.utils.formatters import TextFormatter, DataFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BulkCampaignApp:
    def __init__(self):
        # Cache expensive object initializations
        if 'generator' not in st.session_state:
            st.session_state.generator = BulkSheetGenerator()
        if 'file_handler' not in st.session_state:
            st.session_state.file_handler = FileHandler()
        if 'text_formatter' not in st.session_state:
            st.session_state.text_formatter = TextFormatter()
        if 'data_formatter' not in st.session_state:
            st.session_state.data_formatter = DataFormatter()
        
        # Use session state references
        self.generator = st.session_state.generator
        self.file_handler = st.session_state.file_handler
        self.text_formatter = st.session_state.text_formatter
        self.data_formatter = st.session_state.data_formatter

    def get_keywords_input(self) -> Tuple[list, bool, int]:
        """Get and validate keywords input"""
        input_method = st.radio(
            "Choose input method for keywords:",
            ["Type/Paste", "Upload CSV"],
            help="Select how you want to input your keywords",
            key="keywords_input_method"
        )
        
        keywords = []
        has_error = False
        group_size = None
        
        if input_method == "Type/Paste":
            sample_data = self.file_handler.load_template_data('keywords')
            use_sample = st.checkbox("Load sample keywords", key="use_sample_keywords")
            
            keyword_text = st.text_area(
                "Enter keywords",
                value=sample_data if use_sample else "",
                height=150,
                help="Enter keywords (one per line or comma-separated)",
                key="keyword_text_input"
            )
            
            if keyword_text:
                keywords = self.text_formatter.clean_text_input(keyword_text)
        else:
            keyword_file = st.file_uploader(
                "Upload keywords CSV",
                type=['csv'],
                key="keyword_file_upload"
            )
            if keyword_file:
                try:
                    keywords = self.file_handler.load_csv_data(keyword_file)
                except Exception as e:
                    st.error(f"Error loading keywords: {str(e)}")
                    has_error = True
        
        if keywords and not has_error:
            valid, error = validate_keywords(keywords)
            if not valid:
                st.error(error)
                has_error = True
            else:
                st.success(f"Successfully loaded {len(keywords)} keywords")
                
                enable_grouping = st.checkbox(
                    "Enable keyword grouping",
                    help="Group multiple keywords into a single campaign",
                    key="enable_keyword_grouping"
                )
                
                if enable_grouping:
                    group_size = st.number_input(
                        "Keywords per group",
                        min_value=1,
                        max_value=len(keywords),
                        value=min(3, len(keywords)),
                        key="keyword_group_size"
                    )
                    
                    if group_size:
                        st.write("Preview of keyword groups:")
                        groups = [keywords[i:i + group_size] for i in range(0, len(keywords), group_size)]
                        for i, group in enumerate(groups, 1):
                            with st.expander(f"Group {i}", expanded=i==1):
                                st.write("\n".join(group))
        
        return keywords, has_error, group_size

    def get_skus_input(self) -> Tuple[list, bool, int]:
        """Get and validate SKUs input"""
        input_method = st.radio(
            "Choose input method for SKUs:",
            ["Type/Paste", "Upload CSV"],
            help="Select how you want to input your SKUs",
            key="skus_input_method"
        )
        
        skus = []
        has_error = False
        group_size = None
        
        if input_method == "Type/Paste":
            sample_data = self.file_handler.load_template_data('skus')
            use_sample = st.checkbox("Load sample SKUs", key="use_sample_skus")
            
            sku_text = st.text_area(
                "Enter SKUs",
                value=sample_data if use_sample else "",
                height=150,
                help="Enter SKUs (one per line or comma-separated)",
                key="sku_text_input"
            )
            
            if sku_text:
                skus = self.text_formatter.clean_text_input(sku_text)
        else:
            sku_file = st.file_uploader(
                "Upload SKUs CSV",
                type=['csv'],
                key="sku_file_upload"
            )
            if sku_file:
                try:
                    skus = self.file_handler.load_csv_data(sku_file)
                except Exception as e:
                    st.error(f"Error loading SKUs: {str(e)}")
                    has_error = True
        
        if skus and not has_error:
            valid, error = validate_skus(skus)
            if not valid:
                st.error(error)
                has_error = True
            else:
                st.success(f"Successfully loaded {len(skus)} SKUs")
                
                enable_grouping = st.checkbox(
                    "Enable SKU grouping",
                    help="Group multiple SKUs into a single campaign",
                    key="enable_sku_grouping"
                )
                
                if enable_grouping:
                    group_size = st.number_input(
                        "SKUs per group",
                        min_value=1,
                        max_value=len(skus),
                        value=min(3, len(skus)),
                        key="sku_group_size"
                    )
                    
                    if group_size:
                        st.write("Preview of SKU groups:")
                        groups = [skus[i:i + group_size] for i in range(0, len(skus), group_size)]
                        for i, group in enumerate(groups, 1):
                            with st.expander(f"Group {i}", expanded=i==1):
                                st.write("\n".join(group))
        
        return skus, has_error, group_size

    def get_campaign_settings(self) -> Tuple[Dict[str, Any], bool]:
        """Get and validate campaign settings"""
        has_error = False
        
        # Create columns for settings
        col1, col2 = st.columns(2)
        
        with col1:
            daily_budget = st.number_input(
                "Daily Budget ($)",
                min_value=1.0,
                value=10.0,
                help="Minimum daily budget is $1.00",
                key="daily_budget"
            )
            
            start_date = st.date_input(
                "Campaign Start Date",
                min_value=datetime.today(),
                help="Choose when your campaign should start",
                key="start_date"
            )
        
        with col2:
            match_types = st.multiselect(
                "Select Match Types",
                ["exact", "phrase", "broad"],
                default=["exact"],
                key="match_types"
            )
            
            bids = {}
            for match_type in match_types:
                bids[match_type] = st.number_input(
                    f"Default bid for {match_type} match ($)",
                    min_value=0.02,
                    value=0.75,
                    key=f"bid_{match_type}"
                )
        
        # Create settings dictionary
        settings = {
            'campaign_name_template': "SP_[SKU]_match_type",
            'ad_group_name_template': "AG_[SKU]_match_type",
            'daily_budget': daily_budget,
            'start_date': start_date,
            'match_types': match_types,
            'bids': bids
        }
        
        # Validate settings
        valid, error = validate_campaign_settings(settings)
        if not valid:
            st.error(error)
            has_error = True
        
        return settings, has_error

    def _display_bulk_sheet_results(self, df: pd.DataFrame):
        """Display bulk sheet results including download buttons and preview"""
        try:
            preview_df = self.data_formatter.prepare_preview_data(df)
            excel_path = self.file_handler.save_bulk_sheet(df, 'xlsx')
            csv_path = self.file_handler.save_bulk_sheet(df, 'csv')
            
            st.success("Bulk sheet generated successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                with open(excel_path, 'rb') as f:
                    st.download_button(
                        "Download Excel File",
                        f.read(),
                        file_name=os.path.basename(excel_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel"
                    )
            
            with col2:
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        "Download CSV File",
                        f.read(),
                        file_name=os.path.basename(csv_path),
                        mime="text/csv",
                        key="download_csv"
                    )
            
            st.markdown("### 🔍 Preview")
            st.dataframe(preview_df, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Error displaying bulk sheet results: {str(e)}")
            st.error(f"Error displaying bulk sheet results: {str(e)}")

    def generate_bulk_sheet(self, keywords: list, skus: list, settings: Dict[str, Any], group_size: int = None):
        """Generate bulk sheet"""
        try:
            campaign_settings = CampaignSettings(
                daily_budget=settings['daily_budget'],
                start_date=settings['start_date'],
                match_types=settings['match_types'],
                bids=settings['bids'],
                campaign_name_template=settings['campaign_name_template'],
                ad_group_name_template=settings['ad_group_name_template'],
                keyword_group_size=group_size
            )
            
            if st.session_state.get('sku_group_size'):
                # Generate bulk sheets for each SKU group
                sku_groups = [skus[i:i + st.session_state.sku_group_size] 
                            for i in range(0, len(skus), st.session_state.sku_group_size)]
                all_dfs = []
                for sku_group in sku_groups:
                    df = self.generator.generate_bulk_sheet(keywords, sku_group, campaign_settings)
                    all_dfs.append(df)
                
                # Combine all dataframes
                final_df = pd.concat(all_dfs, ignore_index=True)
            else:
                # Original behavior without SKU grouping
                final_df = self.generator.generate_bulk_sheet(keywords, skus, campaign_settings)
            
            # Display results
            self._display_bulk_sheet_results(final_df)
            
        except Exception as e:
            logger.error(f"Error generating bulk sheet: {str(e)}")
            st.error(f"Error generating bulk sheet: {str(e)}")

    def run(self):
        """Run the Streamlit application"""
        logger.info("Starting application")
        logger.info(f"Current session state: {st.session_state}")
        
        # Main app content
        st.title("Amazon Ads Bulk Campaign Generator 🎯")
        st.markdown("Create properly formatted bulk sheets for Amazon Sponsored Products campaigns")
        
        # Initialize all required session state keys
        for key in ['step', 'keywords', 'skus', 'keyword_group_size', 'sku_group_size']:
            if key not in st.session_state:
                st.session_state[key] = {
                    'step': 1,
                    'keywords': [],
                    'skus': [],
                    'keyword_group_size': None,
                    'sku_group_size': None
                }.get(key)
        
        # Create two columns for Step 1
        if st.session_state['step'] == 1:
            st.header("Step 1: Enter Keywords and SKUs")
            
            col1, col2 = st.columns(2)
            with col1:
                keywords, keywords_error, keyword_group_size = self.get_keywords_input()
            with col2:
                skus, skus_error, sku_group_size = self.get_skus_input()
            
            # Navigation section with fixed position at bottom
            st.markdown("<br>", unsafe_allow_html=True)  # Add some space
            nav_container = st.container()
            
            with nav_container:
                # Success message if both inputs are valid
                if keywords and skus and not keywords_error and not skus_error:
                    st.success(f"✅ Successfully loaded {len(keywords)} keywords and {len(skus)} SKUs")
                    
                    # Center the button using columns
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("Continue to Campaign Settings ➡️", type="primary", use_container_width=True):
                            # Store values in session state using dictionary syntax
                            st.session_state['keywords'] = keywords
                            st.session_state['skus'] = skus
                            st.session_state['keyword_group_size'] = keyword_group_size
                            if sku_group_size is not None:
                                st.session_state['sku_group_size'] = sku_group_size
                            st.session_state['step'] = 2
                            st.rerun()
        
        # Step 2: Campaign Settings
        elif st.session_state['step'] == 2:
            st.header("Step 2: Configure Campaign Settings")
            settings, settings_error = self.get_campaign_settings()
            
            # Add container for better organization
            with st.container():
                st.markdown("---")  # Add a visual separator
                
                # Navigation buttons
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("⬅️ Back to Step 1", use_container_width=True):
                        st.session_state['step'] = 1
                        st.rerun()
                with col2:
                    if settings and not settings_error:
                        if st.button("🎯 Generate Bulk Sheet", type="primary", use_container_width=True):
                            # Retrieve values from session state
                            if 'keywords' not in st.session_state or 'skus' not in st.session_state:
                                st.error("Keywords or SKUs not found. Please go back to Step 1.")
                                return
                            # Generate bulk sheet with both keyword and SKU grouping
                            self.generate_bulk_sheet(
                                st.session_state['keywords'],
                                st.session_state['skus'],
                                settings,
                                st.session_state.get('keyword_group_size')
                            )

if __name__ == "__main__":
    app = BulkCampaignApp()
    app.run()
