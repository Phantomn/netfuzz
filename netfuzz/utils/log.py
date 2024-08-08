import logging
import os

RESET = "\033[0m"
BOLD = "\033[1m"
WHITE = "\033[1;37m"

# Define color codes
text = {
    "magenta": "\033[35m",
    "bold_green": "\033[1;32m",
    "bold_red": "\033[1;31m",
    "bold_blue": "\033[1;34m",
    "bold_yellow": "\033[1;33m",
    "on_red": "\033[41m",
}

# Message type prefixes with colors
_msgtype_prefixes = {
    'debug': [text['bold_red'], 'DEBUG'],
    'info': [text['bold_green'], '*'],
    'warning': [text['bold_yellow'], '!'],
    'error': [text['on_red'], 'ERROR']
}

class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        # Select color and prefix based on log level
        prefix, symbol = _msgtype_prefixes.get(record.levelname.lower(), ["", ""])
        message = f"{WHITE}[{prefix}{symbol}{WHITE}{RESET}] {WHITE}{record.getMessage()}{RESET}"
        return message
    
class FileFormatter(logging.Formatter):
    DATE_FORMAT = "%Y%m%d %H:%M:%S"

    def format(self, record):
        date = self.formatTime(record, self.DATE_FORMAT)
        message = f"[{date}] {record.getMessage()}"
        return message
    
class Logger:
    _instance = None
    _loggers = {}
    _default_path = "logs"
    _logger_name = "default"
    _logger_level = logging.INFO
    _configured = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'logger'):  # 처음 초기화할 때만 실행
            # skipcq: PTC-W0052
            self.logger = logging.getLogger(Logger._logger_name)
            self.logger.setLevel(Logger._logger_level)

            if not self.logger.handlers:
                # Console handler with colored output
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(ConsoleFormatter())
                self.logger.addHandler(console_handler)

                # File handler with timestamp
                if Logger._default_path:
                    try:
                        # Ensure that the directory for the file exists
                        os.makedirs(Logger._default_path, exist_ok=True)

                        # Construct the full file path
                        filename = os.path.join(Logger._default_path,
                                                f"{Logger._logger_name}.log")

                        # Create the file if it doesn't exist
                        open(filename, 'a').close()

                        file_handler = logging.FileHandler(filename)
                        file_handler.setFormatter(FileFormatter())
                        self.logger.addHandler(file_handler)
                    except Exception as e:
                        self.logger.error(f"Failed to set up file handler: {e}")

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    @classmethod
    def configure(cls, path=None, test="default", level=None):
        if cls._configured:
            return
        cls._default_path = path or cls._default_path
        cls._logger_name = test
        cls._logger_level = level
        cls._configured = True

    @classmethod
    def getLogger(cls):
        if cls._logger_name not in Logger._loggers:
            Logger._loggers[cls._logger_name] = cls()
        logger_instance = Logger._loggers[cls._logger_name]
        logger_instance.logger.setLevel(cls._logger_level)
        return logger_instance