"""
Centralized logging configuration using loguru.

Loguru provides better logging with:
- Colorized output
- Better exception handling
- Simpler API
- Automatic rotation
- No configuration files needed
"""

import sys
from pathlib import Path
from loguru import logger


# Project root directory (where pyproject.toml lives)
def get_project_root() -> Path:
    """Get the project root directory."""
    # Start from this file's location and go up to find pyproject.toml
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback to current working directory
    return Path.cwd()


PROJECT_ROOT = get_project_root()
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
    colorize: bool = True,
):
    """
    Configure loguru logging for TinyDSL.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        rotation: When to rotate log file (e.g., "10 MB", "1 day")
        retention: How long to keep old logs
        colorize: Whether to colorize console output

    Returns:
        Configured logger instance
    """
    # Remove default handler
    logger.remove()

    # Add console handler with nice formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=log_format,
        level=level,
        colorize=colorize,
        backtrace=True,
        diagnose=True,
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=log_format,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

    return logger


def get_logger(name: str = None):
    """
    Get a logger instance.

    Args:
        name: Optional name for the logger context

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Default configuration
# Can be overridden by calling setup_logging() with custom parameters
logger = setup_logging(
    level="INFO",
    colorize=True,
)


def configure_for_production():
    """Configure logging for production environment."""
    return setup_logging(
        level="WARNING",
        log_file=str(DEFAULT_LOG_DIR / "tinydsl.log"),
        rotation="50 MB",
        retention="30 days",
        colorize=False,
    )


def configure_for_development():
    """Configure logging for development environment."""
    return setup_logging(
        level="DEBUG",
        log_file=str(DEFAULT_LOG_DIR / "tinydsl-dev.log"),
        rotation="10 MB",
        retention="3 days",
        colorize=True,
    )


def configure_for_testing():
    """Configure logging for testing environment."""
    return setup_logging(
        level="WARNING",
        log_file=None,  # No file logging during tests
        colorize=False,
    )


# Intercept standard logging and redirect to loguru
class InterceptHandler:
    """
    Intercept standard logging messages and redirect to loguru.

    This allows libraries using standard logging to benefit from loguru.
    """

    def write(self, message):
        # Get corresponding Loguru level if it exists
        level = "INFO"

        # Find caller from where the logged message originated
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=False).log(level, message.rstrip())


def setup_standard_logging_interception():
    """
    Setup interception of standard logging to redirect to loguru.

    Call this to make libraries using standard logging work with loguru.
    """
    import logging

    class LoguruHandler(logging.Handler):
        """Handler that redirects standard logging to loguru."""

        def emit(self, record):
            # Get corresponding Loguru level
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated
            frame, depth = sys._getframe(6), 6
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Intercept specific loggers
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [LoguruHandler()]
        logging_logger.propagate = False  # Don't propagate to root logger


# Example usage patterns for developers
"""
Basic usage:
    from tinydsl.core.logging_config import logger

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

In classes:
    from tinydsl.core.logging_config import get_logger

    class MyClass:
        def __init__(self):
            self.logger = get_logger(self.__class__.__name__)

        def do_something(self):
            self.logger.info("Doing something")

Exception logging:
    try:
        dangerous_operation()
    except Exception as e:
        logger.exception("Operation failed")  # Automatically includes traceback

Contextual logging:
    with logger.contextualize(request_id="12345"):
        logger.info("Processing request")  # Will include request_id in output

Performance timing:
    from loguru import logger
    import time

    @logger.catch  # Automatically log exceptions
    def my_function():
        logger.info("Function started")
        time.sleep(1)
        logger.info("Function completed")
"""
