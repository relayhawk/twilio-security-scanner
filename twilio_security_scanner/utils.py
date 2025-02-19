import csv
import logging
from typing import List, TextIO
from dataclasses import dataclass, fields

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Suppress noisy loggers
logging.getLogger('twilio.http_client').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


@dataclass
class PublicEntity:
    type: str          # Either 'Function' or 'Asset'
    url: str           # The URL at which the public entity is accessible
    path: str          # Path to the function/asset
    SID: str           # Unique identifier for the Function or Asset
    service_name: str  # Name of the service containing this entity
    service_sid: str   # SID of the service containing this entity


def write_items_to_csv(items: List[PublicEntity], file_pointer: TextIO) -> None:
    """
    Writes public entities to a CSV file.

    Args:
        items: List of public entities to write
        file_pointer: File-like object to write to

    Raises:
        ValueError: If items list is empty
    """
    if not items:
        raise ValueError("PublicEntities list is empty. Nothing to write.")

    headers = [field.name for field in fields(PublicEntity)]
    writer = csv.writer(file_pointer)
    writer.writerow(headers)

    for item in items:
        writer.writerow([getattr(item, header) for header in headers])
