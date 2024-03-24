import asyncio
import os
import pytest
from aioresponses import aioresponses
from aiohttp import ClientSession, http

from src.downloader import download_files


@pytest.mark.asyncio
async def test_download_files():
    directory_info = [
        {'type': 'file', 'name': 'file1.txt', 'download_url': 'http://example.com/file1.txt'},
        {'type': 'file', 'name': 'file2.txt', 'download_url': 'http://example.com/file2.txt'},
    ]
    temp_folder = '/tmp'

    async with ClientSession() as session:
        semaphore = asyncio.Semaphore(1)

        with aioresponses() as mock_responses:
            for file_info in directory_info:
                mock_responses.get(file_info['download_url'], status=http.HTTPStatus.OK,
                                   body=b'Test data')

            await download_files(session, directory_info, temp_folder, semaphore)

        for file_info in directory_info:
            filename = os.path.join(temp_folder, file_info['name'])
            assert os.path.exists(filename)
