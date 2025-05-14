# Amazon Bulk Campaign Generator

A Streamlit web application for generating properly formatted bulk sheets for Amazon Sponsored Products campaigns.

## Features

- Generate bulk campaign sheets for Amazon Sponsored Products
- Support for multiple SKUs and keywords
- Customizable campaign settings
- Supports special characters in SKUs
- Export to both Excel and CSV formats

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd amazon-bulk-campaign
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will be available at http://localhost:8501

## Input Format

### SKUs
- One SKU per line
- Supports alphanumeric characters and special characters (-, _, ., ,, >, <, /, ", :, ;, +, =)
- Maximum length: 40 characters

### Keywords
- One keyword per line
- Supports alphanumeric characters, spaces, hyphens, and apostrophes
- Maximum length: 80 characters

## Campaign Settings

- Daily budget (minimum $1.00)
- Match types (exact, phrase, broad)
- Default bids per match type (minimum $0.02)
- Campaign start date
- Customizable campaign and ad group name templates

## Output

The tool generates:
- Excel file (.xlsx)
- CSV file (.csv)

Both files are properly formatted for Amazon Sponsored Products bulk uploads.

## License

MIT License
