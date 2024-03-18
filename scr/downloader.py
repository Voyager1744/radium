"""Download files from the repository."""

import asyncio
import logging
import os
import ssl

import aiohttp

logging.basicConfig(level=logging.ERROR)


async def fetch_files(session, url):
    """Fetch files from the repository."""
    async with session.get(url) as response:
        if response.status == aiohttp.http.HTTPStatus.OK:
            return await response.json()
        logging.error(
            'Failed to fetch files: {status}'.format(status=response.status),
        )
        return None


async def download_file(session, file_url, filename, semaphore):
    """Download a file."""
    async with semaphore:
        async with session.get(file_url) as response:
            if response.status == aiohttp.http.HTTPStatus.OK:
                file_data = await response.read()
                with open(filename, 'wb') as file_handle:
                    file_handle.write(file_data)
            else:
                logging.error(
                    'Failed to download file: {file_url}'.format(
                        file_url=file_url,
                    ),
                )


async def download_files(session, directory_info, temp_folder, semaphore):
    """Download files from the repository."""
    tasks = []
    for file_or_directory in directory_info:
        if file_or_directory['type'] == 'file':
            filename = os.path.join(temp_folder, file_or_directory['name'])
            tasks.append(
                download_file(
                    session,
                    file_or_directory['download_url'],
                    filename,
                    semaphore,
                ),
            )
        elif file_or_directory['type'] == 'dir':
            await download_directory(
                session, file_or_directory, temp_folder, semaphore,
            )
    await asyncio.gather(*tasks)


async def download_directory(
    session,
    directory_info,
    temp_folder,
    semaphore,
):
    """Download a directory."""
    subdir_url = directory_info['url']
    subdir_files = await fetch_files(session, subdir_url)
    if subdir_files:
        subdir_name = os.path.join(temp_folder, directory_info['name'])
        if not os.path.exists(subdir_name):
            os.makedirs(subdir_name)
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
