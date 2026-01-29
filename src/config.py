"""Configuration module for the weather bot."""
import os
import sys
import re
import urllib.request
import logging

logger = logging.getLogger(__name__)


def get_env_or_exit(key: str) -> str:
    """Get environment variable or exit if not found."""
    value = os.environ.get(key)
    if not value:
        sys.exit(f'{key} not exist or null')
    return value.strip()


def get_webhook_host() -> str:
    """Detect public IP address from external services."""
    ip_services = ['https://ident.me', 'http://ipinfo.io/ip']
    for service in ip_services:
        try:
            response = urllib.request.urlopen(service, timeout=1).read().decode('utf8')
            return re.sub(r"^\s+|\n|\r|\s+$", '', response)
        except Exception:
            logger.warning(f"Service {service} unavailable")
    sys.exit("WEBHOOK_HOST could not be determined")


def find_ssl_files() -> tuple[str, str]:
    """Find SSL certificate and key files in current directory."""
    cert_file = None
    key_file = None
    
    for file in os.listdir('.'):
        if re.search(r"\D+\.pem$", file):
            cert_file = os.path.abspath(file)
        elif re.search(r"\D+\.key$", file):
            key_file = os.path.abspath(file)
    
    if not cert_file:
        sys.exit("SSL certificate not found")
    if not key_file:
        sys.exit("SSL key not found")
    
    return cert_file, key_file


# API Keys
OWM_KEY = get_env_or_exit('OWM_KEY')
TELEBOT_KEY = get_env_or_exit('TELEBOT_KEY')

# Webhook configuration
WEBHOOK_HOST = get_webhook_host()
WEBHOOK_PORT = get_env_or_exit('WEBHOOK_PORT')
WEBHOOK_LISTEN = get_env_or_exit('WEBHOOK_LISTEN')
WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV = find_ssl_files()

WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
WEBHOOK_URL_PATH = f"/{TELEBOT_KEY}/"

# Content types
CONTENT_TO_HANDLE = ['text', 'location']
CONTENT_TO_REJECT = [
    'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice',
    'location', 'contact', 'new_chat_members', 'left_chat_member',
    'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
    'group_chat_created', 'supergroup_chat_created', 'channel_chat_created',
    'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'
]

# Sticker collections
ERROR_STICKERS = [
    'CAADAgAD3gEAAvnkbAAB9tAurz2ipZUWBA',
    'CAADAgADpQEAAvnkbAAB3LCoSz9i3NQWBA',
    'CAADAgAD3AIAAvnkbAABZ4r6GvjutU4WBA',
    'CAADAgAD4AIAAvnkbAABano-tB5DgtYWBA',
    'CAADAgADYssAAmOLRgywPTPuHYqUWhYE',
    'CAADAgADLgADNIWFDDKv5aCIOvtVFgQ',
    'CAADAgADKAADNIWFDJH1ZYPnRgPgFgQ'
]

WRONG_CONTENT_STICKERS = [
    'CAADAgAD4QIAAvnkbAAB4uG83jqZC7oWBA',
    'CAADAgADdgIAAvnkbAABwOWRNMVkWAwWBA',
    'CAADAgADAQIAAvnkbAABgYkUR2jzKikWBA',
    'CAADAgAD2wEAAvnkbAABCX-hVktjtVAWBA',
    'CAADAgADwAEAAvnkbAABoDH6R5pwO0cWBA',
    'CAADAgADvwEAAvnkbAABHngR9XeKmpsWBA',
    'CAADAgADtAEAAvnkbAABLH9k4WvwzJgWBA',
    'CAADAgADOgIAAvnkbAABRlHfrrHgNBcWBA',
    'CAADAgADagEAAvnkbAABiDcDQFCEuXgWBA',
    'CAADAgADJAEAAvnkbAAB2fxXBcKZT08WBA',
    'CAADAgADNAEAAvnkbAABdiR2Dg6Dxc8WBA'
]

# Unicode symbols
DEGREE_SIGN = '\N{DEGREE SIGN}'
