import os
import pytest
from pydantic import ValidationError

def test_settings_validation_error():
    # If we remove the env variables, Pydantic should raise ValidationError
    # We need to test the Settings class directly.
    from app.core.config import Settings
    
    # Store old env
    old_key = os.environ.get("GEMINI_API_KEY")
    old_url = os.environ.get("GEMINI_API_BASE_URL")
    
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    if "GEMINI_API_BASE_URL" in os.environ:
        del os.environ["GEMINI_API_BASE_URL"]
        
    with pytest.raises(ValidationError):
        # We try to create Settings without the required env vars
        Settings(
            _env_file=None, # prevent reading .env
        )
        
    # Restore env
    if old_key:
        os.environ["GEMINI_API_KEY"] = old_key
    if old_url:
        os.environ["GEMINI_API_BASE_URL"] = old_url
