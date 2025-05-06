import logging
import os
from datetime import datetime


def setup_logger() -> logging.Logger:
    """
    Sets up a logger that writes logs to a file named after the calling script.
    The log file is placed in a 'logs' directory relative to the script.
    The log file name is in the format: <script_name>_<YYYY-MM-DD_HH-MM-SS>.log.
 
    Returns:
        logging.Logger: Configured logger instance.
    """
    # Get the name of the calling script
    caller_script_name = os.path.splitext(os.path.basename(__file__))[0]
    # Create a logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
 
    # Create a timestamped log file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"{caller_script_name}_{timestamp}.log")
 
    # Configure the logger
    logger = logging.getLogger(caller_script_name)
    logger.setLevel(logging.DEBUG)  # Set log level to DEBUG for detailed logging
 
    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
 
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
 
    # Create a log formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
