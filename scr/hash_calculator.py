"""Calculate hash values for files in TEMP_FOLDER."""

import hashlib
import os

TEMP_FOLDER = 'temp'


def calculate_hash_values():
    """Calculate hash values for files in TEMP_FOLDER."""
    hash_dict = {}
    for filepath, file_data in read_files():
        hash_value = hashlib.sha256(file_data).hexdigest()
        hash_dict[filepath] = hash_value
    return hash_dict


def read_files():
    """Read files in TEMP_FOLDER and yield filepath and file data."""
    for root, _, filenames in os.walk(TEMP_FOLDER):
        for filename in filenames:
            with open(os.path.join(root, filename), 'rb') as file_handle:
                file_data = file_handle.read()
                yield os.path.join(root, filename), file_data


def write_hash_values(hash_values):
    """Write hash values to a file."""
    with open('hashes.csv', 'w') as hash_file:
        for filepath, hash_value in hash_values.items():
            hash_file.write('{filepath}, {hash_value}\n'.format(
                filepath=filepath, hash_value=hash_value,
            ))


if __name__ == '__main__':
    hash_values = calculate_hash_values()
    write_hash_values(hash_values)
