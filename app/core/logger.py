"""Logging configuration and setup."""

import io
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from opentelemetry.trace import get_current_span
from rich.console import Console
from rich.syntax import Syntax

from app.middlewares.tracing import get_correlation_id, get_request_id


def colorize_json(data: Dict[str, Any]) -> str:
    """Return JSON as a colorized string (instead of printing to console)."""
    json_string = json.dumps(data, indent=2)

    # Create a temporary StringIO buffer
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=True)  # Redirect output

    # Render JSON with syntax highlighting
    syntax = Syntax(json_string, "json", theme="ansi_dark")
    console.print(syntax)

    # Get the colorized string
    return buffer.getvalue()


class JsonFormatter(logging.Formatter):
    """JSON log formatter with trace context integration."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON with trace context.

        Args:
            record: Log record to format

        Returns:
            str: JSON formatted log entry
        """
        # Basic log entry structure
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request ID if available
        request_id = get_request_id()
        if request_id:
            log_entry["request_id"] = request_id

        # Add correlation ID if available
        correlation_id = get_correlation_id()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        # Add trace context if available
        span = get_current_span()
        if span and span.is_recording():
            span_context = span.get_span_context()
            log_entry["trace_id"] = format(span_context.trace_id, "032x")
            log_entry["span_id"] = format(span_context.span_id, "016x")

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]),
            }

        # Add any extra attributes
        if hasattr(record, "extras"):
            log_entry.update(getattr(record, "extras"))

        if os.environ.get("ENV") != "development":
            return colorize_json(log_entry)

        return json.dumps(log_entry)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure JSON logging with trace context.

    Args:
        level: Logging level (default: INFO)
    """
    # Create JSON handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Remove default handlers
    for h in root_logger.handlers[:]:
        if not isinstance(h, logging.StreamHandler):
            root_logger.removeHandler(h)
