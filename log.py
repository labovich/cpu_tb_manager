import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    """Singleton logger configuration"""
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._setup_logging()
        return cls._instance

    @classmethod
    def _get_logs_directory(cls) -> Path:
        """Get the standard Windows logs directory for the application"""
        if os.name == 'nt':  # Windows
            # Use %LOCALAPPDATA%\TurboBoostManager\logs\
            local_appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
            logs_dir = Path(local_appdata) / 'TurboBoostManager' / 'logs'
        else:
            # Fallback for non-Windows systems
            logs_dir = Path.cwd() / 'logs'

        # Create directory if it doesn't exist
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    @classmethod
    def _setup_logging(cls):
        # Get logs directory and create log file path
        logs_dir = cls._get_logs_directory()
        log_file_path = logs_dir / 'turbo_boost_manager.log'

        # Create rotating file handler with 5MB limit and 3 backup files
        file_handler = RotatingFileHandler(
            str(log_file_path),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )

        # Create console handler
        console_handler = logging.StreamHandler()

        # Set formatter for both handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler]
        )
        cls._logger = logging.getLogger(__name__)

        # Log the actual log file location
        cls._logger.info(f"Log file location: {log_file_path}")

    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            cls()
        return cls._logger

