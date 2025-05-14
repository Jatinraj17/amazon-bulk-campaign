import pytest
from datetime import datetime
from src.amazon_bulk_generator.core.generator import BulkSheetGenerator, CampaignSettings
from src.amazon_bulk_generator.core.validators import (
    validate_keywords,
    validate_asins,
    validate_campaign_settings,
    validate_campaign_prefix
)

@pytest.fixture
def sample_settings():
    """Fixture for sample campaign settings"""
    return CampaignSettings(
        daily_budget=10.0,
        start_date=datetime.today(),
        match_types=['EXACT'],
        bids={'EXACT': 0.75},
        campaign_prefix='KW'
    )

@pytest.fixture
def sample_keywords():
    """Fixture for sample keywords"""
    return [
        'gaming keyboard',
        'wireless mouse',
        'laptop stand'
    ]

@pytest.fixture
def sample_asins():
    """Fixture for sample ASINs"""
    return [
        'B07XYZ1234',
        'B07ABC4567'
    ]

def test_bulk_sheet_generator_initialization():
    """Test BulkSheetGenerator initialization"""
    generator = BulkSheetGenerator()
    assert generator is not None
    assert len(generator.headers) > 0

def test_bulk_sheet_generation(sample_settings, sample_keywords, sample_asins):
    """Test bulk sheet generation with sample data"""
    generator = BulkSheetGenerator()
    df = generator.generate_bulk_sheet(sample_keywords, sample_asins, sample_settings)
    
    # Check basic DataFrame properties
    assert df is not None
    assert not df.empty
    assert len(df.columns) == len(generator.headers)
    
    # Check if all required columns are present
    required_columns = [
        'Campaign', 'Ad Group', 'Keyword', 'Match Type',
        'Campaign Daily Budget', 'Max Bid'
    ]
    for col in required_columns:
        assert col in df.columns

def test_keyword_validation():
    """Test keyword validation"""
    # Valid keywords
    valid_keywords = ['gaming keyboard', 'wireless mouse']
    is_valid, error = validate_keywords(valid_keywords)
    assert is_valid
    assert error is None
    
    # Empty keywords
    empty_keywords = []
    is_valid, error = validate_keywords(empty_keywords)
    assert not is_valid
    assert "required" in error.lower()
    
    # Invalid characters
    invalid_keywords = ['gaming@keyboard']
    is_valid, error = validate_keywords(invalid_keywords)
    assert not is_valid
    assert "invalid characters" in error.lower()

def test_asin_validation():
    """Test ASIN validation"""
    # Valid ASINs
    valid_asins = ['B07XYZ1234', 'B07ABC4567']
    is_valid, error = validate_asins(valid_asins)
    assert is_valid
    assert error is None
    
    # Invalid format
    invalid_asins = ['INVALID123']
    is_valid, error = validate_asins(invalid_asins)
    assert not is_valid
    assert "format" in error.lower()
    
    # Empty ASINs
    empty_asins = []
    is_valid, error = validate_asins(empty_asins)
    assert not is_valid
    assert "required" in error.lower()

def test_campaign_settings_validation(sample_settings):
    """Test campaign settings validation"""
    # Valid settings
    settings_dict = {
        'daily_budget': sample_settings.daily_budget,
        'start_date': sample_settings.start_date,
        'match_types': sample_settings.match_types,
        'bids': sample_settings.bids
    }
    is_valid, error = validate_campaign_settings(settings_dict)
    assert is_valid
    assert error is None
    
    # Invalid budget
    invalid_settings = settings_dict.copy()
    invalid_settings['daily_budget'] = 0
    is_valid, error = validate_campaign_settings(invalid_settings)
    assert not is_valid
    assert "budget" in error.lower()

def test_campaign_prefix_validation():
    """Test campaign prefix validation"""
    # Valid prefix
    is_valid, error = validate_campaign_prefix('KW')
    assert is_valid
    assert error is None
    
    # Invalid characters
    is_valid, error = validate_campaign_prefix('KW@')
    assert not is_valid
    assert "can only contain" in error.lower()
    
    # Too long
    is_valid, error = validate_campaign_prefix('A' * 11)
    assert not is_valid
    assert "cannot exceed" in error.lower()
    
    # Empty
    is_valid, error = validate_campaign_prefix('')
    assert not is_valid
    assert "cannot be empty" in error.lower()

def test_campaign_name_format(sample_settings, sample_keywords, sample_asins):
    """Test campaign name formatting"""
    generator = BulkSheetGenerator()
    df = generator.generate_bulk_sheet(sample_keywords, sample_asins, sample_settings)
    
    # Check campaign name format
    campaign_names = df[df['Entity'] == 'Campaign']['Campaign']
    for name in campaign_names:
        # Check prefix
        assert name.startswith(sample_settings.campaign_prefix)
        
        # Check format (PREFIX-ASIN-MATCHTYPE-DATE)
        parts = name.split('-')
        assert len(parts) == 4
        
        # Check ASIN part
        assert parts[1] in sample_asins
        
        # Check match type part
        assert parts[2] in sample_settings.match_types
        
        # Check date part (YYYYMMDD)
        assert len(parts[3]) == 8
        assert parts[3].isdigit()
