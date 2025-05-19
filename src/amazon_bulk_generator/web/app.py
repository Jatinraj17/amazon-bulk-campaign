import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import os
from typing import Dict, Any, Tuple, List
import re
import json

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from amazon_bulk_generator.core.generator import BulkSheetGenerator, CampaignSettings
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import os
from typing import Dict, Any, Tuple, List
import re
from streamlit_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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
        # Set page config first to avoid Streamlit warnings
        st.set_page_config(
            page_title="Amazon Ads Bulk Campaign Generator",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="collapsed"  # Collapse sidebar for faster loading
        )
        
        # Default credentials configuration
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@ecommercean.com',
                        'name': 'Admin User',
                        'password': '$2b$12$7YxQmLSXJxjBHwYeGNWQO.KF3zXcPjnQB8YQstAI8Tp/Hr8ldnZeO'  # hashed 'admin123'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'amazon_bulk_campaign_key',
                'name': 'amazon_bulk_campaign_cookie'
            },
            'preauthorized': {
                'emails': ['admin@ecommercean.com']
            }
        }

        # Load credentials from Streamlit secrets
        try:
            credentials_json = st.secrets["authentication"]["credentials"]
            credentials = json.loads(credentials_json)
            cookie_name = st.secrets["authentication"]["cookie_name"]
            cookie_key = st.secrets["authentication"]["cookie_key"]
            cookie_expiry_days = st.secrets["authentication"]["cookie_expiry_days"]
            preauthorized = {"emails": st.secrets["authentication"]["preauthorized_emails"]}
            self.credentials = {
                "credentials": credentials,
                "cookie": {
                    "name": cookie_name,
                    "key": cookie_key,
                    "expiry_days": cookie_expiry_days
                },
                "preauthorized": preauthorized
            }
            logger.info("Loaded credentials from Streamlit secrets")
        except Exception as e:
            logger.error(f"Error loading credentials from secrets: {str(e)}")
            self.credentials = default_config

        # Initialize authenticator
        self.authenticator = stauth.Authenticate(
            self.credentials['credentials'],
            self.credentials['cookie']['name'],
            self.credentials['cookie']['key'],
            self.credentials['cookie']['expiry_days'],
            self.credentials['preauthorized']
        )
        
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
            help="Select how you want to input your keywords"
        )
        
        keywords = []
        has_error = False
        group_size = None
        
        if input_method == "Type/Paste":
            sample_data = self.file_handler.load_template_data('keywords')
            use_sample = st.checkbox("Load sample keywords")
            
            keyword_text = st.text_area(
                "Enter keywords",
                value=sample_data if use_sample else "",
                height=150,
                help="Enter keywords (one per line or comma-separated)"
            )
            
            if keyword_text:
                keywords = self.text_formatter.clean_text_input(keyword_text)
        else:
            keyword_file = st.file_uploader(
                "Upload keywords CSV",
                type=['csv']
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
                    help="Group multiple keywords into a single campaign"
                )
                
                if enable_grouping:
                    group_size = st.number_input(
                        "Keywords per group",
                        min_value=1,
                        max_value=len(keywords),
                        value=min(3, len(keywords))
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
            help="Select how you want to input your SKUs"
        )
        
        skus = []
        has_error = False
        group_size = None
        
        if input_method == "Type/Paste":
            sample_data = self.file_handler.load_template_data('skus')
            use_sample = st.checkbox("Load sample SKUs")
            
            sku_text = st.text_area(
                "Enter SKUs",
                value=sample_data if use_sample else "",
                height=150,
                help="Enter SKUs (one per line or comma-separated)"
            )
            
            if sku_text:
                skus = self.text_formatter.clean_text_input(sku_text)
        else:
            sku_file = st.file_uploader(
                "Upload SKUs CSV",
                type=['csv']
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
                    help="Group multiple SKUs into a single campaign"
                )
                
                if enable_grouping:
                    group_size = st.number_input(
                        "SKUs per group",
                        min_value=1,
                        max_value=len(skus),
                        value=min(3, len(skus))
                    )
                    
                    if group_size:
                        st.write("Preview of SKU groups:")
                        groups = [skus[i:i + group_size] for i in range(0, len(skus), group_size)]
                        for i, group in enumerate(groups, 1):
                            with st.expander(f"Group {i}", expanded=i==1):
                                st.write("\n".join(group))
        
        return skus, has_error, group_size

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
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        "Download CSV File",
                        f.read(),
                        file_name=os.path.basename(csv_path),
                        mime="text/csv"
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
        
        # Show login page if not authenticated
        if not st.session_state.get('authentication_status'):
            logger.info("User not authenticated, showing login page")
            st.markdown("""
            ### Welcome to Amazon Ads Bulk Campaign Generator! 👋
            
            Choose one of the options below:
            - **Existing Users**: Use the "Login" tab to access your account
            - **New Users**: Use the "Register" tab to request access
            - **Admin Access**: Use username `admin` to manage users and approve registrations
            """)
            
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
            
            with tab1:
                st.markdown("""
                #### Login
                If you already have an account or are an admin, please log in below.
                
                **Admin Login:**
                - Username: `admin`
                - Password: Contact system administrator
                """)
                
                name, authentication_status, username = self.authenticator.login("Enter your credentials", "main")
                logger.info(f"Login attempt - Status: {authentication_status}, Username: {username}")
                
                if authentication_status is False:
                    logger.warning("Login failed - incorrect credentials")
                    st.error('Username/password is incorrect')
                elif authentication_status is None:
                    logger.info("No login attempt yet")
                    st.info('Please enter your credentials to access the app')
                else:
                    logger.info(f"Successful login for user: {username}")
                    st.session_state['authentication_status'] = authentication_status
                    st.session_state['name'] = name
                    st.session_state['username'] = username
                    st.rerun()
            
            with tab2:
                self.show_registration_page()
            
            return
        
        # If authenticated, show logout in sidebar and welcome message
        st.sidebar.success(f'Welcome *{st.session_state["name"]}*')
        if self.authenticator.logout('Logout', 'sidebar'):
            logger.info("User logged out")
            st.rerun()
        
        # Admin features
        if st.session_state['username'] == 'admin':
            st.sidebar.markdown("---")
            if st.sidebar.button("User Management"):
                st.session_state['show_user_management'] = True
                st.rerun()
            if st.sidebar.button("Pending Approvals"):
                st.session_state['show_approvals'] = True
                st.rerun()
        
        # Show appropriate page based on state
        if st.session_state.get('show_user_management', False) and st.session_state['username'] == 'admin':
            self.show_user_management()
            if st.sidebar.button("Back to Main App"):
                st.session_state['show_user_management'] = False
                st.rerun()
        elif st.session_state.get('show_approvals', False) and st.session_state['username'] == 'admin':
            self.show_pending_approvals()
            if st.sidebar.button("Back to Main App"):
                st.session_state['show_approvals'] = False
                st.rerun()
        else:
            # Main app content
            col1, col2 = st.columns([3, 1])
            with col1:
                st.title("Amazon Ads Bulk Campaign Generator 🎯")
                st.markdown("Create properly formatted bulk sheets for Amazon Sponsored Products campaigns")
        
        # Initialize session state
        if 'step' not in st.session_state:
            st.session_state.step = 1
            st.session_state.keywords = []
            st.session_state.skus = []
            st.session_state.keyword_group_size = None
            st.session_state.sku_group_size = None
        
        # Create two columns for Step 1
        if st.session_state.step == 1:
            st.header("Step 1: Enter Keywords and SKUs")
            
            col1, col2 = st.columns(2)
            with col1:
                keywords, keywords_error, group_size = self.get_keywords_input()
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
                            # Store values in session state
                            st.session_state.keywords = keywords
                            st.session_state.skus = skus
                            st.session_state.keyword_group_size = group_size
                            st.session_state.sku_group_size = sku_group_size
                            st.session_state.step = 2
                            st.rerun()
        
        # Step 2: Campaign Settings
        elif st.session_state.step == 2:
            st.header("Step 2: Configure Campaign Settings")
            settings, settings_error = self.get_campaign_settings()
            
            # Add container for better organization
            with st.container():
                st.markdown("---")  # Add a visual separator
                
                # Navigation buttons
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("⬅️ Back to Step 1", use_container_width=True):
                        st.session_state.step = 1
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
                                st.session_state.keywords,
                                st.session_state.skus,
                                settings,
                                st.session_state.get('keyword_group_size')
                            )

if __name__ == "__main__":
    app = BulkCampaignApp()
    app.run()
