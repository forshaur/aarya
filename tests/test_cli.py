import pytest
import asyncio
from aarya.cli import is_valid, run_scan

@pytest.mark.asyncio
async def test_is_valid():
    assert is_valid("whiteroseeee@proton.me") is True
    assert is_valid("invalid-email") is False

@pytest.mark.asyncio
async def test_run_scan(mocker):
    mock_email = "whiteroseeee@proton.me"
    mock_response = [{"name": "Service1", "exists": True}, {"name": "Service2", "exists": False}]
    
    # Mock the check function to return a predefined response
    mock_check = mocker.patch('aarya.cli.check', return_value=mock_response)
    
    results = await run_scan(mock_email)
    
    assert len(results) == 2
    assert results[0]['name'] == "Service1"
    assert results[0]['exists'] is True
    assert results[1]['name'] == "Service2"
    assert results[1]['exists'] is False