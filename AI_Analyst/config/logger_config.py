# logger_config.py
import logging
import os

# log_dir = "logs"
log_dir = os.path.join(os.path.dirname(__file__), "..", "log")
os.makedirs(log_dir, exist_ok=True)

LOG_FILE = os.path.join(log_dir, "aia_logger.log")

# Set the log level based on environment variable or default to INFO
ENVIRONMENT = os.getenv("APP_ENV", "production").lower()  # e.g., "development", "production"
LOG_LEVEL = logging.DEBUG if ENVIRONMENT == "development" else logging.INFO

def setup_logger():
    logger = logging.getLogger()  # Root logger

    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(funcName)s | %(levelname)s | %(lineno)d | %(message)s"
        )

       # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File Handler
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        logger.info(f"Logger initialized with level: {logging.getLevelName(LOG_LEVEL)} (env: {ENVIRONMENT})")
