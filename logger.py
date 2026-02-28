import logging
import sys

def get_logger(name, log_file='trading_log.txt'):
    """
    Initializes and returns a logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create handlers
        file_handler = logging.FileHandler(log_file)
        stdout_handler = logging.StreamHandler(sys.stdout)

        # Create formatters and add it to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)

    return logger
