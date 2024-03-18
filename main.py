import asyncio
import os
from scr import downloader
from scr import hash_calculator

URL = (
    'https://gitea.radium.group/api/v1/repos/radium/' +
    'project-configuration/contents/'
)
TEMP_FOLDER = 'temp'


async def main():
    """Run the main script."""
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)

    await downloader.setup_session(URL, TEMP_FOLDER)

    hash_values = hash_calculator.calculate_hash_values()

    hash_calculator.write_hash_values(hash_values)


if __name__ == '__main__':
    asyncio.run(main())
