# logging_config.py
import logging

# Create a custom logger
logger = logging.getLogger('hetznercloud')
logger.setLevel(logging.DEBUG)  # Set the desired logging level

# Create handlers for file and console output
file_handler = logging.FileHandler('log/application.log')
console_handler = logging.StreamHandler()

# Set logging levels for handlers if needed
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for both handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

file_handler.encoding = 'utf-8'
console_handler.encoding = 'utf-8'

# Add handlers to the logger if they haven't been added yet
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)