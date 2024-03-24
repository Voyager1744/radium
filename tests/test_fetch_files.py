"""Test the fetch_files."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.downloader import fetch_files

SUCCESS_URL = 'http://example.com/files'
FAILURE_URL = 'http://example.com/invalid'
FAILURE_RESPONSE_TEXT = 'Not Found'
success_response_data = {'file1': 'content1', 'file2': 'content2'}


@pytest.fixture()
def successful_response() -> AsyncMock:
    """Create a successful response."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = success_response_data
    return mock_response


@pytest.fixture()
def failed_response() -> AsyncMock:
    """Create a failed response."""
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.text.return_value = FAILURE_RESPONSE_TEXT
    return mock_response


@pytest.mark.asyncio()
async def test_fetch_files_successful(successful_response: AsyncMock) -> None:
    """Test successful response."""
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = (  # noqa: WPS609
        successful_response
    )
    files = await fetch_files(mock_session, SUCCESS_URL)
    assert files == success_response_data


@pytest.mark.asyncio()
async def test_fetch_files_failed(failed_response: AsyncMock) -> None:
    """Test failed response."""
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = (  # noqa: WPS609
        failed_response
    )
    files = await fetch_files(mock_session, FAILURE_URL)
    assert files is None
