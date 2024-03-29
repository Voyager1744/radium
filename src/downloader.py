"""Download files from the repository."""

import asyncio
import logging
import os
import ssl
from typing import Dict, List

import aiohttp
from aiohttp import ClientSession

logging.basicConfig(level=logging.ERROR)


async def fetch_files(session: aiohttp.ClientSession, url: str) -> dict:
    """Fetch files from the repository."""
    try:
        async with session.get(url) as response:
            if response.status == aiohttp.http.HTTPStatus.OK:
                return await response.json()
            logging.error(
                f'Failed to fetch files: {response.status} - {await response.text()}'
            )
            return None
    except aiohttp.ClientError as e:
        logging.error(f'Failed to fetch files: {e}')
        return None


async def download_file(session, file_url, filename, semaphore):
    """Download a file asynchronously.

    Args:
        session: aiohttp.ClientSession: A session object for making HTTP requests.
        file_url (str): URL of the file to download.
        filename (str): Name of the file to save.
        semaphore: asyncio.Semaphore: A semaphore to control concurrency.

    Returns:
        None
    """
    async with semaphore:
        try:
            async with session.get(file_url) as response:
                if response.status == aiohttp.http.HTTPStatus.OK:
                    file_data = await response.read()
                    with open(filename, 'wb') as file_handle:
                        file_handle.write(file_data)
                else:
                    logging.error(f'Failed to download file: {file_url}. Status: {response.status}')
        except aiohttp.ClientError as e:
            logging.error(f'Error downloading file: {file_url}. {e}')


async def download_files(session: ClientSession,
                         directory_info: List[Dict],
                         temp_folder: str,
                         semaphore: asyncio.Semaphore) -> None:
    """Download files from the repository."""
    async def download_file_task(file_info):
        filename = os.path.join(temp_folder, file_info['name'])
        await download_file(session, file_info['download_url'], filename, semaphore)

    tasks = []
    for file_or_directory in directory_info:
        if file_or_directory['type'] == 'file':
            tasks.append(download_file_task(file_or_directory))
        elif file_or_directory['type'] == 'dir':
            await download_directory(
                session, file_or_directory, temp_folder, semaphore,
            )

    await asyncio.gather(*tasks)


async def download_directory(session: ClientSession,
                             directory_info: Dict,
                             temp_folder: str,
                             semaphore: asyncio.Semaphore) -> None:
    """Download a directory."""
    subdir_url = directory_info.get('url')
    if not subdir_url:
        return

    subdir_files = await fetch_files(session, subdir_url)
    if subdir_files:
        subdir_name = os.path.join(temp_folder, directory_info['name'])
        os.makedirs(subdir_name, exist_ok=True)
        await download_files(session, subdir_files, subdir_name, semaphore)


async def setup_session(repository_url, temp_folder):
    """Set up the aiohttp session and SSL context."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    semaphore = asyncio.Semaphore(3)

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context),
    ) as session:
        files = await fetch_files(session, repository_url)
        if files:
            await download_files(session, files, temp_folder, semaphore)
