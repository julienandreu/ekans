"""HTTP Stats middleware for tracking request statistics."""

from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime
from logging import getLogger
from typing import Awaitable, Deque, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

_start_time: datetime = datetime.now()
_request_count: int = 0
_status_counts: Dict[int, int] = defaultdict(int)
_recent_status_codes: Deque[int] = deque(maxlen=100)

logger = getLogger(__name__)


class HttpStatsMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request statistics.

    Args:
        app: ASGI app
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Dispatch the request.

        Args:
            request: Request
            call_next: Callable[[Request], Awaitable[Response]]
        """
        # pylint: disable=global-statement
        global _request_count
        response = await call_next(request)

        _request_count += 1
        _status_counts[response.status_code] += 1
        _recent_status_codes.append(response.status_code)

        return response


def get_stats() -> tuple[int, Dict[int, int], list[int]]:
    """Get current HTTP statistics.

    Returns:
        tuple containing:
            - Total request count
            - Dictionary of status code counts
            - List of recent status codes
    """

    logger.info("get_stats()")
    return (
        _request_count,
        dict(_status_counts),
        list(reversed(_recent_status_codes)),
    )


def get_start_time() -> datetime:
    """Get the application start time.

    Returns:
        datetime: Application start timestamp
    """
    return _start_time
