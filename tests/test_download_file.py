"""Test the download_file."""
import asyncio
import os

import pytest
from aiohttp import ClientSession, http
from aioresponses import aioresponses

from src.downloader import download_file

expected_url_successful = 'http://example.com/successful_download.txt'
expected_filename = 'successful_download.txt'
file_data = b'Test data'

expected_url_not_found = 'http://example.com/not_found.txt'
expected_filename_not_found = 'not_found.txt'


@pytest.mark.asyncio()
async def test_download_file_success():
    async with ClientSession() as session:
        with aioresponses() as mock_responses:
            mock_responses.get(
                expected_url_successful,
                status=http.HTTPStatus.OK,
                body=file_data,
            )

            semaphore = asyncio.Semaphore(1)
            await download_file(
                session,
                expected_url_successful,
                expected_filename,
                semaphore,
            )

        with open(expected_filename, 'rb') as file_handle:
            downloaded_data = file_handle.read()
        assert downloaded_data == file_data


@pytest.mark.asyncio()
async def test_download_file_failure():
    async with ClientSession() as session:

        with aioresponses() as mock_responses:
            mock_responses.get(
                expected_url_not_found,
                status=http.HTTPStatus.NOT_FOUND,
            )

            semaphore = asyncio.Semaphore(1)
            downloaded_files = await download_file(
                session,
                expected_url_not_found,
                expected_filename_not_found,
                semaphore,
            )
            assert downloaded_files is None


@pytest.fixture(autouse=True)
def _cleanup_files() -> None:
    # Clean up created files
    yield
    for entry in os.scandir():
        if entry.name in {'successful_download.txt', 'not_found.txt'}:
            os.remove(entry.name)
