"""
Configuration management for Vedic Astrology Chatbot
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any
import logging

class Config:
    def __init__(self):
        """Initialize configuration by loading environment variables"""
        # Load environment variables from .env file
        load_dotenv()

        # Validate required environment variables
        self._validate_required_vars()

        # Setup logging
        self._setup_logging()

    def _validate_required_vars(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'GEMINI_API_KEY',
            'USER_NAME',
            'USER_DOB',
            'USER_TIME',
            'USER_LOCATION',
            'USER_LATITUDE',
            'USER_LONGITUDE'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # API Configuration
    @property
    def gemini_api_key(self) -> str:
        return os.getenv('GEMINI_API_KEY')

    @property
    def gemini_model(self) -> str:
        return os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')

    @property
    def api_temperature(self) -> float:
        return float(os.getenv('API_TEMPERATURE', '0.7'))

    @property
    def api_top_p(self) -> float:
        return float(os.getenv('API_TOP_P', '0.9'))

    @property
    def api_top_k(self) -> int:
        return int(os.getenv('API_TOP_K', '40'))

    @property
    def max_output_tokens(self) -> int:
        return int(os.getenv('MAX_OUTPUT_TOKENS', '200'))

    # User Configuration
    @property
    def user_data(self) -> Dict[str, Any]:
        return {
            'name': os.getenv('USER_NAME'),
            'dob': os.getenv('USER_DOB'),
            'time': os.getenv('USER_TIME'),
            'location': os.getenv('USER_LOCATION'),
            'coordinates': {
                'lat': float(os.getenv('USER_LATITUDE')),
                'lon': float(os.getenv('USER_LONGITUDE'))
            },
            'timezone': os.getenv('USER_TIMEZONE', 'UTC+0:00')
        }

    # Astrologer Configuration
    @property
    def astrologer_data(self) -> Dict[str, Any]:
        return {
            'name': os.getenv('ASTROLOGER_NAME', 'Sarika Pandey'),
            'age': int(os.getenv('ASTROLOGER_AGE', '20')),
            'experience': int(os.getenv('ASTROLOGER_EXPERIENCE', '18')),
            'location': os.getenv('ASTROLOGER_LOCATION', 'Lucknow, UP, India')
        }

    # Application Configuration
    @property
    def max_conversation_history(self) -> int:
        return int(os.getenv('MAX_CONVERSATION_HISTORY', '20'))

    @property
    def debug_mode(self) -> bool:
        return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

    @property
    def session_timeout(self) -> int:
        return int(os.getenv('SESSION_TIMEOUT', '3600'))

    # Astrological Settings
    @property
    def default_ayanamsa(self) -> str:
        return os.getenv('DEFAULT_AYANAMSA', 'Lahiri')

    @property
    def house_system(self) -> str:
        return os.getenv('HOUSE_SYSTEM', 'Equal')

    @property
    def ephemeris_type(self) -> str:
        return os.getenv('EPHEMERIS_TYPE', 'Swiss')

# Global configuration instance
config = Config()
